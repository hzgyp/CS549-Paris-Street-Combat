"""Restore only the selected city/native-playtest manifests, never mutable workspaces.

Python 3.10+ and Windows OpenSSH are sufficient. Passwords are entered in the
OpenSSH console, never command arguments or files. All transfers stage first;
apply refuses existing different files unless --backup-conflicts is explicit.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ('france-liberation-content', 'paris-gameplay-native-playtest')
STAGE = ROOT / 'tmp/native-playtest-restore'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    value = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()

def safe_path(relative):
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or ':' in relative or '\\' in relative:
        raise RuntimeError('Unsafe restore path')
    p = ROOT / relative
    if not p.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError('Restore alias escapes checkout; do not copy another PC junction')
    return p

def idle():
    if os.name == 'nt':
        ps = shutil.which('pwsh') or shutil.which('powershell')
        result = subprocess.check_output([ps, '-NoProfile', '-Command',
            '@(Get-Process UnrealEditor,UnrealEditor-Cmd,blender -ErrorAction SilentlyContinue).Count'], text=True)
        if int(result.strip()):
            raise RuntimeError('Close Unreal/Blender before asset restoration or verification')

def entries():
    catalog = read(ROOT / 'Assets/Sync/CATALOG.json')
    selected, records, seen = [], [], set()
    for aid in ASSETS:
        release = next((x for x in catalog['active_manifests'] if x['asset_id'] == aid), None)
        if release is None:
            raise RuntimeError('Checkout lacks selected playtest release')
        p = safe_path(release['path'])
        if sha(p) != release['sha256']:
            raise RuntimeError('Catalog manifest hash differs')
        manifest = read(p)
        if manifest['asset_version'] != release['asset_version'] or manifest['asset_id'] != aid:
            raise RuntimeError('Manifest identity differs')
        selected.append({k: release[k] for k in ('asset_id', 'asset_version', 'sha256')})
        for e in manifest['files']:
            if e['path'] in seen:
                raise RuntimeError('Conflicting restore ownership')
            seen.add(e['path'])
            safe_path(e['path'])
            remote = PurePosixPath(e['remote_path'])
            if not e['remote_path'].startswith(('/objects/sha256/', '/baselines/')) or '..' in remote.parts:
                raise RuntimeError('Not an immutable remote source')
            records.append(e)
    return selected, records

def same(p, e):
    return p.is_file() and p.stat().st_size == e['size_bytes'] and sha(p) == e['sha256']

def missing(records):
    return [e for e in records if not same(safe_path(e['path']), e)]

def make_plan(selected, records):
    STAGE.mkdir(parents=True, exist_ok=True)
    needed = missing(records)
    unique = {e['sha256']: e for e in needed}
    commands = []
    for h, e in unique.items():
        staged = STAGE / h
        if not same(staged, e):
            if '"' in e['remote_path'] or '\n' in e['remote_path']:
                raise RuntimeError('Unsafe SFTP command path')
            commands.append(f'get "{e["remote_path"]}" "{staged.as_posix()}"')
    plan = {'selected': selected, 'required_files': len(records), 'needed_files': len(needed),
            'download_objects': len(commands), 'download_bytes': sum(e['size_bytes'] for h, e in unique.items() if not same(STAGE / h, e)),
            'conflicts': [e['path'] for e in needed if safe_path(e['path']).exists()]}
    (STAGE / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    (STAGE / 'download.sftp').write_text('\n'.join(commands) + '\n', encoding='utf-8')
    print(json.dumps(plan, ensure_ascii=False))
    return commands, needed

def download(args, selected, records):
    commands, needed = make_plan(selected, records)
    if commands:
        if not args.host or not args.user:
            raise RuntimeError('Supply private --host and --user; no endpoint is stored in Git')
        if any(c in args.host + args.user for c in '\r\n "') or args.host.startswith('-') or args.user.startswith('-'):
            raise RuntimeError('Invalid endpoint')
        known = Path(args.known_hosts).expanduser() if args.known_hosts else Path.home() / '.ssh/known_hosts'
        if not known.is_file():
            raise RuntimeError('First verify server fingerprint privately in interactive SFTP; then use its known_hosts')
        cmd = ['sftp', '-P', str(args.port), '-o', 'StrictHostKeyChecking=yes',
               '-o', 'UserKnownHostsFile=' + str(known)]
        if args.identity:
            cmd += ['-i', str(Path(args.identity).expanduser()), '-o', 'IdentitiesOnly=yes', '-b', '-']
        elif not sys.stdin.isatty():
            raise RuntimeError('Password mode must run in your local interactive terminal, or supply your private --identity')
        cmd.append(args.user + '@' + args.host)
        # Without -b, OpenSSH can prompt at the console for a password. It can
        # continue after a failed get; the all-file hash check below is mandatory.
        with (STAGE / 'sftp.log').open('w', encoding='utf-8') as log:
            result = subprocess.run(cmd, input='\n'.join(commands + ['bye']) + '\n', text=True, stdout=log)
        if result.returncode:
            raise RuntimeError('SFTP failed; active assets unchanged; inspect ignored sftp.log')
    for e in needed:
        if not same(STAGE / e['sha256'], e):
            raise RuntimeError('Missing/mismatched staged transfer; active assets unchanged')
    print('All needed staged bytes verified; run apply next. No active assets changed.')

def apply(args, selected, records):
    needed = missing(records)
    conflicts = [e for e in needed if safe_path(e['path']).exists()]
    if conflicts and not args.backup_conflicts:
        raise RuntimeError('Existing different files: preserve/review your work first; --backup-conflicts is explicit opt-in')
    for e in needed:
        if not same(STAGE / e['sha256'], e):
            raise RuntimeError('Download and verify all needed files before apply')
    backup = STAGE / ('backups-' + uuid.uuid4().hex)
    for e in needed:
        target = safe_path(e['path'])
        if target.exists():
            dest = backup / e['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, dest)
            if sha(dest) != sha(target):
                raise RuntimeError('Conflict backup verification failed')
        target.parent.mkdir(parents=True, exist_ok=True)
        # No deletion or replacement of junctions. Only exact selected files.
        staged = STAGE / e['sha256']
        scratch = target.with_name(target.name + '.restore-' + uuid.uuid4().hex + '.tmp')
        shutil.copyfile(staged, scratch)
        if not same(scratch, e):
            raise RuntimeError('Placement verification failed')
        os.replace(scratch, target)
    verify_all(selected, records)
    # Remove only verified disposable transfer objects; never conflict backups.
    for h in {e['sha256'] for e in needed}:
        p = STAGE / h
        exemplar = next(e for e in needed if e['sha256'] == h)
        if same(p, exemplar):
            p.unlink()
    print('Restored ' + str(len(needed)) + ' files; conflict backups: ' + (str(backup) if conflicts else 'none'))

def verify_all(selected, records):
    absent = missing(records)
    if absent:
        raise RuntimeError('Unsynchronized files: ' + str(len(absent)) + '; first: ' + absent[0]['path'])
    STAGE.mkdir(parents=True, exist_ok=True)
    (STAGE / 'verified.json').write_text(json.dumps({'selected': selected, 'verified_files': len(records)}, indent=2) + '\n', encoding='utf-8')
    print('Verified all ' + str(len(records)) + ' selected city/playtest files. This is not second-machine runtime acceptance.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('plan', 'download', 'apply', 'verify'))
    parser.add_argument('--host')
    parser.add_argument('--port', type=int, default=22222)
    parser.add_argument('--user')
    parser.add_argument('--identity')
    parser.add_argument('--known-hosts')
    parser.add_argument('--backup-conflicts', action='store_true')
    args = parser.parse_args()
    idle()
    selected, records = entries()
    if args.mode == 'plan':
        make_plan(selected, records)
    elif args.mode == 'download':
        download(args, selected, records)
    elif args.mode == 'apply':
        apply(args, selected, records)
    else:
        verify_all(selected, records)

if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        raise SystemExit(str(exc))
