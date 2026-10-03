"""Read-only saved-map dependency audit for the private team playtest release."""
import hashlib
import json
import os
from collections import deque
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = os.environ.get('CS549_PLAYTEST_AUDIT_IDENTITY', 'dependency-audit')
assert IDENTITY.replace('-', '').replace('_', '').isalnum()
OUT = ROOT / ('tmp/paris-native-playtest-20261003-v1/' + IDENTITY + '.json')
INVENTORY = ROOT / 'Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    if OUT.exists():
        raise RuntimeError('Preserve occupied audit identity; inspect before another run')
    inventory = json.loads(INVENTORY.read_text(encoding='utf-8-sig'))
    def guards():
        return all((ROOT / f['path']).stat().st_size == f['size_bytes']
                   and digest(ROOT / f['path']) == f['sha256'] for f in inventory['files'])
    assert guards(), 'Current native inventory differs'
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    options = unreal.AssetRegistryDependencyOptions(
        include_hard_package_references=True, include_soft_package_references=True)
    queue, seen, edges, external = deque([ENTRY]), {ENTRY}, {}, set()
    while queue:
        package = queue.popleft()
        dependencies = sorted(str(x) for x in registry.get_dependencies(package, options))
        edges[package] = dependencies
        for dep in dependencies:
            if dep.startswith('/Game/'):
                if dep not in seen:
                    seen.add(dep)
                    queue.append(dep)
            else:
                external.add(dep)
    assert '/Game/ParisCombat/Blueprints/ContinuousArmsNativeV1/BP_PC_ContinuousArmsNativeV1' in seen
    content = ROOT / 'Unreal/ParisStreetCombat/Content'
    files, missing = [], []
    for package in sorted(seen):
        base = content / package.removeprefix('/Game/')
        candidates = [Path(str(base) + suffix) for suffix in ('.uasset', '.umap')]
        existing = [p for p in candidates if p.is_file()]
        if len(existing) != 1:
            missing.append(package)
            continue
        path = existing[0]
        files.append({'package': package, 'path': path.relative_to(ROOT).as_posix(),
                      'size_bytes': path.stat().st_size, 'sha256': digest(path)})
    hard_options = unreal.AssetRegistryDependencyOptions(
        include_hard_package_references=True, include_soft_package_references=False)
    hard_queue, hard_seen = deque([ENTRY]), {ENTRY}
    while hard_queue:
        for dep in registry.get_dependencies(hard_queue.popleft(), hard_options):
            dep = str(dep)
            if dep.startswith('/Game/') and dep not in hard_seen:
                hard_seen.add(dep)
                hard_queue.append(dep)
    hard_missing = sorted(set(missing) & hard_seen)
    city_manifest = json.loads((ROOT / 'Assets/Sync/manifests/france-liberation-content.json').read_text(encoding='utf-8-sig'))
    original_city_paths = {f['path'] for f in city_manifest['files']}
    # These supplier soft references are not silently accepted. The v2 report
    # separates hard startup closure from optional vendor dangling references.
    missing_referencers = {p: sorted(k for k, deps in edges.items() if p in deps) for p in missing}
    assert guards(), 'Read-only audit changed guarded bytes'
    report = {'status': 'pass_required_closure_with_vendor_soft_gaps' if missing and not hard_missing else ('pass' if not missing else 'failed'), 'entry': ENTRY,
              'engine': unreal.SystemLibrary.get_engine_version(),
              'files': files, 'edges': edges, 'external_dependencies': sorted(external),
              'missing_packages': missing, 'hard_missing_packages': hard_missing,
              'missing_referencers': missing_referencers,
              'noncity_files': [f for f in files if f['path'] not in original_city_paths],
              'guarded_files': len(inventory['files']),
              'guarded_bytes_unchanged': True, 'scope': 'Read-only registry closure; no native save or second-machine pass'}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    assert not hard_missing, 'Missing hard dependency packages; preserve report and do not publish'
    unreal.log('CS549_PLAYTEST_RELEASE_AUDIT pass')

main()
