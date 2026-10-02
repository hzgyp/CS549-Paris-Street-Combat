"""Prove the exact redundant discovery tree recoverable before native cleanup."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LAB=ROOT/'Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1'
TARGET=LAB/'Content/Rifle_01'
ORIGINAL=ROOT/'Assets/LocalShared/SFTP/baselines/rifle-pro-mocap-original/rifle-motion-20261002-v1/Rifle Pro - MoCap Pack'
WORK=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/rifle-motion-ue582-v1'
OUT=ROOT/'tmp/rifle-motion-20261002-v1/cleanup-eligibility.json'

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

status=json.loads((ROOT/'Assets/Sync/RIFLE_MOTION_PUBLICATION_STATUS.json').read_text())
assert status['status']=='verified_private_sftp_publication'
staged=json.loads((LAB/'Evidence/staging.json').read_text())
expected={e['path']:e for e in staged['files'] if e['path'].startswith('Content/Rifle_01/')}
selected=json.loads((WORK/'Evidence/selected_native.json').read_text())['files']
for e in selected:
    p=WORK/e['path']
    assert p.stat().st_size==e['size_bytes'] and digest(p)==e['sha256']
assert not TARGET.is_symlink() and not TARGET.is_junction()
actual=[]
for p in TARGET.rglob('*'):
    assert not p.is_symlink() and not p.is_junction()
    if not p.is_file():continue
    rel=p.relative_to(LAB).as_posix();e=expected[rel];original=ORIGINAL/rel
    assert p.stat().st_size==original.stat().st_size==e['size_bytes']
    assert digest(p)==digest(original)==e['original_sha256']
    actual.append({'path':rel,'size_bytes':e['size_bytes'],'sha256':e['original_sha256']})
assert len(actual)==753 and len(selected)==33
result={'status':'verified_redundant_discovery_only','target':TARGET.relative_to(ROOT).as_posix(),
        'retained_original':ORIGINAL.relative_to(ROOT).as_posix(),'retained_selected':WORK.relative_to(ROOT).as_posix(),
        'files':actual,'file_count':len(actual),'size_bytes':sum(e['size_bytes'] for e in actual),
        'scope':'No originals, diagnostics, unique edits, release objects or other candidate trees selected for removal'}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='files'}))
