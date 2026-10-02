"""Verify known junctions and task-owned SFTP CRUD without touching releases."""
import hashlib
import json
import subprocess
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/P0'
OUT.mkdir(parents=True, exist_ok=True)
state = json.loads((ROOT / 'tmp/paris-integration-20261001/storage.json').read_text(encoding='utf-8-sig'))
if state['status'] != 'complete':
    raise RuntimeError('Relocation must complete before runtime storage verification')
report = {'checked_at': datetime.now().astimezone().isoformat(), 'aliases': [], 'errors': [],
          'scope': 'Local junction destinations and authenticated local SFTP CRUD; no external reachability/teammate or release publication claim'}
lab = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Content'
aliases = [(ROOT / 'Unreal/ParisStreetCombat/Content', STORE / 'Content')]
aliases += [(lab / p, STORE / 'Content' / p) for p in
            ('GermanSoldier', 'USParatrooper', 'RifleAnimsetPro', 'ParisCombat/Characters/Adaptation')]
for source, expected in aliases:
    resolved = source.resolve(strict=True)
    passed = source.is_junction() and resolved == expected.resolve(strict=True)
    report['aliases'].append({'source': str(source), 'target': str(resolved), 'pass': passed})
    if not passed:
        report['errors'].append('Unexpected alias: ' + str(source))
report['runtime_file_count_before_diagnostic_map'] = sum(p.is_file() for p in (STORE / 'Content').rglob('*'))
if report['runtime_file_count_before_diagnostic_map'] != 16390:
    report['errors'].append('Unexpected runtime inventory before P2')
identity = Path('C:/Users/hzgyp/.ssh/cs549_sftp_ed25519')
known_hosts = Path('C:/Users/hzgyp/.ssh/known_hosts_cs549')
client = ['sftp.exe', '-b', '-', '-P', '22222', '-i', str(identity), '-o', 'BatchMode=yes',
          '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile=' + str(known_hosts),
          'cs549sftp@127.0.0.1']
remote = '/workspaces/yg745/paris-gameplay-v1/P0_CRUD_' + uuid.uuid4().hex
report['probe_directory'] = remote


def batch(commands):
    result = subprocess.run(client, input='\n'.join(commands) + '\n', text=True,
                            capture_output=True, timeout=45)
    if result.returncode:
        raise RuntimeError('SFTP diagnostic failed: ' + result.stderr[-2000:])


try:
    with tempfile.TemporaryDirectory(prefix='p0-crud-', dir=ROOT / 'tmp/paris-integration-20261001') as task_dir:
        local = Path(task_dir)
        first, second, download = local / 'first.txt', local / 'second.txt', local / 'download.txt'
        first.write_bytes(b'CS549 runtime CRUD initial\n')
        second.write_bytes(b'CS549 runtime CRUD changed\n')
        batch(['mkdir "' + remote + '"', 'put "' + first.as_posix() + '" "' + remote + '/probe.txt"',
               'put "' + second.as_posix() + '" "' + remote + '/probe.txt"',
               'rename "' + remote + '/probe.txt" "' + remote + '/renamed.txt"',
               'get "' + remote + '/renamed.txt" "' + download.as_posix() + '"'])
        if hashlib.sha256(download.read_bytes()).digest() != hashlib.sha256(second.read_bytes()).digest():
            raise RuntimeError('SFTP downloaded bytes differ')
        # Exact UUID task-owned targets only; never a recursive/mirror cleanup.
        batch(['rm "' + remote + '/renamed.txt"', 'rmdir "' + remote + '"'])
        report['sftp_crud'] = {'create': True, 'overwrite': True, 'rename': True,
                               'read_sha256_match': True, 'delete': True, 'probe_removed': True}
except Exception as exc:
    report['errors'].append(str(exc))
report['result'] = 'pass' if not report['errors'] else 'fail'
(OUT / 'storage_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
if report['errors']:
    raise SystemExit(1)
