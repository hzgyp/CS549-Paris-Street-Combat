"""Read-only guarded asset hashes and Markdown evidence links for this review."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog/final_verification.json'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8*1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))

checks = []
for name in ('Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json',
             'Assets/Integration/PLAYER_ACTIONS_DRAFT_INVENTORY_20261003.json',
             'Assets/Sync/manifests/paris-gameplay-native-playtest.json',
             'Assets/Sync/manifests/german-soldier-original.json',
             'Assets/Sync/manifests/us-paratrooper-original.json',
             'Assets/Sync/manifests/rifle-animset-pro-original.json',
             'Assets/Sync/manifests/rifle-pro-mocap-original.json'):
    files = read(name)['files']
    bad = []
    for entry in files:
        path = ROOT/entry['path']
        if not path.is_file() or path.stat().st_size != entry['size_bytes'] or sha(path) != entry['sha256']:
            bad.append(entry['path'])
    checks.append({'manifest': name, 'files': len(files), 'mismatches': bad})
    print(json.dumps(checks[-1]), flush=True)
facts = read('Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog/catalog_facts.json')
blend = ROOT/'Assets/LocalWorking/Intake/2026-10-03/01_MW2_Guns_Asset_Library/MW2_Guns_Asset_Library.blend'
gun_ok = blend.stat().st_size == facts['gun_source']['size_bytes'] and sha(blend) == facts['gun_source']['sha256']
links = []
for rel in ('Assets/XIAN_YU_ASSET_CATALOG_20261003_ZH.md', 'Assets/XIAN_YU_ASSET_CATALOG_20261003.md',
            'Docs/Development/RELOAD_COMPARISON_20261003_ZH.md', 'Docs/Development/RELOAD_COMPARISON_20261003.md'):
    path = ROOT/rel
    if not path.exists():
        links.append({'document': rel, 'target': 'DOCUMENT_MISSING', 'exists': False})
        continue
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8-sig')):
        target = target.strip('<>').split('#')[0]
        if not target or '://' in target:
            continue
        links.append({'document': rel, 'target': target, 'exists': (path.parent/target).exists()})
result = {'checks': checks, 'new_blend_sha_unchanged': gun_ok, 'links': links,
          'all_pass': gun_ok and not any(x['mismatches'] for x in checks) and all(x['exists'] for x in links)}
OUT.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({'all_pass': result['all_pass'], 'links': len(links), 'missing_links': [x for x in links if not x['exists']]}))
