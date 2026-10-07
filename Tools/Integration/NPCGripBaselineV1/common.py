"""Read-only native capture helpers; current approved epoch, no exemptions."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE = STORE / 'Evidence/NPCGripBaselineV1'
SNAPSHOT = STORE / 'Evidence/FirstPersonFormalV21/selected_v1/result.json'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def check():
    rows = read(SNAPSHOT)['files']
    assert len(rows) == 555
    bad = [row['path'] for row in rows if not (ROOT / row['path']).is_file()
           or (ROOT / row['path']).stat().st_size != row['size_bytes']
           or sha(ROOT / row['path']) != row['sha256']]
    assert not bad, bad
    return len(rows)

if __name__ == '__main__':
    print('Exact current guards:', check())
