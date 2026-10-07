"""Read-only hashes of existing game and action drafts, with isolated evidence."""
import argparse
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
dest=Path(a.output).resolve()
if dest.exists():raise RuntimeError('Preserve existing verification identity')
dest.parent.mkdir(parents=True,exist_ok=True)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
checks=[]
for name in ('Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json',
             'Assets/Integration/PLAYER_ACTIONS_DRAFT_INVENTORY_20261003.json'):
    data=json.loads((root/name).read_text(encoding='utf-8-sig'))
    bad=[]
    for entry in data['files']:
        path=root/entry['path']
        if not path.is_file() or path.stat().st_size!=entry['size_bytes'] or sha(path)!=entry['sha256']:bad.append(entry['path'])
    checks.append({'manifest':name,'files':len(data['files']),'mismatches':bad})
result={'all_pass':all(not c['mismatches'] for c in checks),'checks':checks}
dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
raise SystemExit(0 if result['all_pass'] else 1)
