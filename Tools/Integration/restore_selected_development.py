"""Restore selected private development dependencies without compiling or launching UE.

Standard-library Python and OpenSSH only. Network credentials remain local. Plans
are pinned to the checkout's Catalog. Apply never replaces a different file and
never writes personal saves, the working Unreal project, or old Editor binaries.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PROFILES = {
    'npc': ['paris-npc-survey-rasters'],
    'workbench': ['paris-workbench-restore-context', 'paris-npc-survey-rasters'],
    'tutorial-source': ['paris-tutorial-runtime-resources', 'paris-tutorial-native-overlay'],
    'tutorial-game': ['paris-tutorial-packaged-release'],
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def relative(value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or '\\' in value or ':' in value or any(c in value for c in '\r\n"\0'):
        raise ValueError(f'Unsafe relative restore path: {value!r}')
    return p


def inside(root, value):
    p = root.joinpath(*relative(value).parts)
    if not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('Restore path escapes checkout')
    # Do not enter an existing junction, including one that resolves inside root.
    for q in (p, *p.parents):
        if q == root:
            break
        if q.exists() or q.is_symlink():
            s = q.lstat()
            if q.is_symlink() or getattr(s, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024):
                raise ValueError(f'Restore path traverses a link: {q}')
    return p


def same(path, item):
    return path.is_file() and path.stat().st_size == item['size_bytes'] and sha(path) == item['sha256']


def selected(root, profile):
    catalog = {x['asset_id']: x for x in read(root/'Assets/Sync/CATALOG.json')['active_manifests']}
    result = {}

    def add(aid):
        if aid in result:
            return
        entry = catalog[aid]
        path = inside(root, entry['path'])
        if sha(path) != entry['sha256']:
            raise ValueError('Catalog manifest hash differs: '+aid)
        m = read(path)
        if (m['asset_id'], m['asset_version']) != (aid, entry['asset_version']):
            raise ValueError('Catalog/manifest identity differs')
        result[aid] = m
        for dep in m.get('dependencies', []):
            did = dep if isinstance(dep, str) else dep['asset_id']
            if isinstance(dep, dict):
                for key in ('asset_version', 'sha256'):
                    if key in dep and catalog[did][key] != dep[key]:
                        raise ValueError('Pinned dependency differs: '+did)
            add(did)

    for aid in PROFILES[profile]:
        add(aid)
    return result


def objects(manifests):
    found = {}
    for m in manifests.values():
        for item in m['files']:
            h = item['sha256']
            if len(h) != 64 or any(c not in '0123456789abcdef' for c in h) or not isinstance(item['size_bytes'], int) or item['size_bytes'] < 0:
                raise ValueError('Invalid object identity')
            remote = item['remote_path']
            if not remote.startswith(('/objects/sha256/', '/baselines/')) or any(c in remote for c in '"\r\n\\\0') or '..' in PurePosixPath(remote).parts:
                raise ValueError('Not an immutable SFTP location')
            if h in found and found[h]['size_bytes'] != item['size_bytes']:
                raise ValueError('Conflicting object sizes')
            found[h] = item
    return found


def mapping(manifests, profile):
    """Final file placement, with the named tutorial overlay applied last."""
    out = {}
    if profile in ('npc', 'workbench'):
        for item in manifests['paris-npc-survey-rasters']['files']:
            out[item['path']] = item
    elif profile == 'tutorial-source':
        prefix = 'Unreal/ParisStreetCombat/'
        target = 'tmp/Restored-Development-20261020/Tutorial/Project/'
        # Use the selected UE5.8.2 integration, never the original UE4 intake.
        for aid in ('character-ue582-integration-baseline', 'rifle-pro-mocap-ue582-selected'):
            for item in manifests[aid]['files']:
                if '/Content/' in item['path']:
                    out[target+'Content/'+item['path'].split('/Content/', 1)[1]] = item
        for aid in ('france-liberation-content', 'paris-gameplay-native-playtest'):
            for item in manifests[aid]['files']:
                p = item['path']
                # Parent Editor DLLs do not match source145. Restore Content only.
                if p.startswith(prefix+'Content/'):
                    out[target+p[len(prefix):]] = item
        for aid in ('paris-tutorial-native-overlay', 'paris-tutorial-runtime-resources'):
            for item in manifests[aid]['files']:
                rel = item.get('restore_path', '')
                if rel and rel != 'Matching-Source-145.zip':
                    relative(rel)
                    out[target+rel] = item
    folded = {}
    for p, item in out.items():
        if p.casefold() in folded and folded[p.casefold()] != p:
            raise ValueError('Case-insensitive restore ownership conflict: '+p)
        folded[p.casefold()] = p
    return out


def download(args, cache, rows):
    needed = [x for h, x in rows.items() if not same(cache/h, x)]
    if not needed:
        return
    if not all((args.host, args.user, args.identity, args.known_hosts)):
        raise ValueError('Download needs --host, --user, --identity and --known-hosts; obtain access privately')
    for value in (args.host, args.user):
        if value.startswith('-') or any(c in value for c in '\r\n\0'):
            raise ValueError('Unsafe connection argument')
    commands = []
    for item in needed:
        dest = cache/item['sha256']
        if dest.exists() or dest.is_symlink():
            raise ValueError('Preserve different/partial cache file before retry: '+str(dest))
        if any(c in dest.as_posix() for c in '"\r\n\0'):
            raise ValueError('Unsafe cache path')
        commands.append(f'get "{item["remote_path"]}" "{dest.as_posix()}"')
    command = ['sftp', '-b', '-', '-P', str(args.port), '-i', str(Path(args.identity).resolve()),
               '-o', 'UserKnownHostsFile='+str(Path(args.known_hosts).resolve()),
               '-o', 'StrictHostKeyChecking=yes', '-o', 'IdentitiesOnly=yes', args.user+'@'+args.host]
    with (cache/'transfer.log').open('w', encoding='utf-8') as log:
        p = subprocess.run(command, input='\n'.join(commands)+'\n', text=True, stdout=log, stderr=subprocess.STDOUT)
    if p.returncode:
        raise RuntimeError('Transfer failed; retain private transfer.log; no files applied')
    if not all(same(cache/x['sha256'], x) for x in needed):
        raise RuntimeError('Downloaded object identity differs; no files applied')


def zipped_files(root, cache, manifests, profile):
    """Return hash-verified archive members; never extractall untrusted paths."""
    if profile == 'npc':
        return []
    aid = {'tutorial-source': 'paris-tutorial-runtime-resources', 'tutorial-game': 'paris-tutorial-packaged-release',
           'workbench': 'paris-workbench-restore-context'}[profile]
    m = manifests[aid]
    item = next(x for x in m['files'] if x.get('restore_path') == 'Matching-Source-145.zip') if profile == 'tutorial-source' else m['files'][0]
    path = cache/item['sha256']
    if not same(path, item):
        raise RuntimeError('Matching archive is missing or changed')
    with zipfile.ZipFile(path) as z:
        if profile == 'tutorial-source':
            raw = z.read('SOURCE_MANIFEST.json')
            contract = read(root/'Assets/Sync/TUTORIAL_SOURCE_CONTRACT_20261017.json')
            if hashlib.sha256(raw).hexdigest() != contract['source_manifest_sha256']:
                raise ValueError('Source145 manifest identity differs')
            specs = [{'path': 'Project/'+x['path'], **{k: x[k] for k in ('sha256', 'size_bytes')}} for x in json.loads(raw)['files']]
            specs.append(dict(path='SOURCE_MANIFEST.json', sha256=hashlib.sha256(raw).hexdigest(), size_bytes=len(raw)))
            prefix = 'tmp/Restored-Development-20261020/Tutorial/'
        else:
            specs = m['archive_members']
            prefix = '' if profile == 'workbench' else 'tmp/Restored-Development-20261020/Game/'
        if {i.filename for i in z.infolist()} != {s['path'] for s in specs}:
            raise ValueError('Archive members differ from selected inventory')
        result = []
        for item in specs:
            relative(item['path'])
            info = z.getinfo(item['path'])
            if info.file_size != item['size_bytes']:
                raise ValueError('Archive member size differs')
            with z.open(info) as f:
                if hashlib.file_digest(f, 'sha256').hexdigest() != item['sha256']:
                    raise ValueError('Archive member hash differs')
            result.append((prefix+item['path'], item, path, item['path']))
        return result


def apply_or_verify(root, cache, manifests, profile, verify=False):
    placements = [(p, x, cache/x['sha256'], None) for p, x in mapping(manifests, profile).items()]
    placements += zipped_files(root, cache, manifests, profile)
    # Check all conflicts and source identities before the first write.
    for rel, item, source, member in placements:
        dest = inside(root, rel)
        if dest.exists() and not same(dest, item):
            raise RuntimeError('Different existing file; preserve it and use a fresh checkout: '+rel)
        if verify and not same(dest, item):
            raise RuntimeError('Restored file missing: '+rel)
        if member is None and not same(source, item):
            raise RuntimeError('Cache object missing or changed')
    if not verify:
        for rel, item, source, member in placements:
            dest = inside(root, rel)
            if same(dest, item):
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            part = dest.with_name(dest.name+'.restore-part')
            if part.exists():
                raise RuntimeError('Preserve previous partial restoration: '+str(part))
            if member is None:
                with source.open('rb') as src, part.open('xb') as dst:
                    shutil.copyfileobj(src, dst, 1024*1024)
            else:
                with zipfile.ZipFile(source) as z, z.open(member) as src, part.open('xb') as dst:
                    shutil.copyfileobj(src, dst, 1024*1024)
            if not same(part, item):
                raise RuntimeError('Placement verification failed; retain partial')
            # Refuse any concurrent creator instead of replacing its file.
            os.link(part, dest)  # Atomic exclusive creation; never replaces a concurrent file.
            part.unlink()
    return len(placements)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', choices=PROFILES)
    parser.add_argument('operation', choices=('plan', 'download', 'apply', 'verify'))
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--host')
    parser.add_argument('--user')
    parser.add_argument('--port', type=int, default=22222)
    parser.add_argument('--identity')
    parser.add_argument('--known-hosts')
    args = parser.parse_args()
    root = args.root.resolve()
    manifests = selected(root, args.profile)
    rows = objects(manifests)
    cache = inside(root, 'tmp/Selected-Development-Restore/'+args.profile+'/objects')
    plan = dict(profile=args.profile, assets=[dict(id=k, version=v['asset_version']) for k, v in manifests.items()],
                unique_objects=len(rows), total_bytes=sum(x['size_bytes'] for x in rows.values()),
                missing_objects=sum(not same(cache/h, x) for h, x in rows.items()),
                game_build_or_launch=False, personal_saves_modified=False)
    if args.operation != 'plan':
        cache.mkdir(parents=True, exist_ok=True)
        if args.operation == 'download':
            download(args, cache, rows)
        else:
            plan['verified_placements'] = apply_or_verify(root, cache, manifests, args.profile, args.operation == 'verify')
        (cache.parent/(args.operation+'-receipt.json')).write_text(json.dumps(plan, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
