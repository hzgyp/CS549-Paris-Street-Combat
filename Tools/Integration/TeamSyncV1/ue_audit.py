"""Read-only registry closure for the unified 8 October native release."""
import hashlib
import json
from collections import deque
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tmp/team-sync-20261008-v1/dependency-audit.json'
CONTENT = ROOT / 'Unreal/ParisStreetCombat/Content'


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    assert not OUT.exists(), 'Preserve occupied audit identity'
    frozen = read(OUT.parent / 'frozen.json')
    def exact():
        return all((ROOT / f['path']).stat().st_size == f['size_bytes'] and
                   sha(ROOT / f['path']) == f['sha256'] for f in frozen['guards'])
    assert exact(), 'Current protected epoch changed'
    old = read(ROOT / 'Assets/Sync/manifests/paris-gameplay-native-playtest.json')
    roots = {f['package'] for f in old['files'] if f.get('package')}
    roots.update(['/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1',
                  '/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1',
                  '/Game/ParisCombat/Mission/G1V1/BP_PCG1ControllerV1',
                  '/Game/ParisCombat/VFX/MuzzleFlashV1/DA_PC_MuzzleFlashV1'])
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    options = unreal.AssetRegistryDependencyOptions(
        include_hard_package_references=True, include_soft_package_references=True)
    queue, seen, edges, external = deque(sorted(roots)), set(roots), {}, set()
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
    hard = unreal.AssetRegistryDependencyOptions(
        include_hard_package_references=True, include_soft_package_references=False)
    queue, hard_seen = deque(sorted(roots)), set(roots)
    while queue:
        for dep in registry.get_dependencies(queue.popleft(), hard):
            dep = str(dep)
            if dep.startswith('/Game/') and dep not in hard_seen:
                hard_seen.add(dep)
                queue.append(dep)
    files, missing = [], []
    for package in sorted(seen):
        base = CONTENT / package.removeprefix('/Game/')
        candidates = [Path(str(base) + suffix) for suffix in ('.uasset', '.umap')]
        existing = [p for p in candidates if p.is_file()]
        if len(existing) != 1:
            missing.append(package)
            continue
        p = existing[0]
        files.append({'package': package, 'path': p.relative_to(ROOT).as_posix(),
                      'size_bytes': p.stat().st_size, 'sha256': sha(p)})
    gaps = {p: sorted(k for k, deps in edges.items() if p in deps) for p in missing}
    hard_missing = sorted(set(missing) & hard_seen)
    unchanged = exact()
    known = set(old['known_vendor_soft_reference_gaps'])
    errors = []
    if hard_missing:
        errors.append('missing hard packages')
    if set(missing) != known:
        errors.append('new or changed soft gaps')
    if not unchanged:
        errors.append('guard drift')
    result = {'status': 'pass_readonly_dependency_closure' if not errors else 'failed',
              'errors': errors, 'engine': unreal.SystemLibrary.get_engine_version(),
              'roots': sorted(roots), 'files': files, 'edges': edges,
              'external_dependencies': sorted(external), 'missing_referencers': gaps,
              'hard_missing_packages': hard_missing, 'guards_unchanged': unchanged,
              'scope': 'Registry/files only; no saves, gameplay or second-machine test'}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    assert not errors, str(errors)
    unreal.log('TEAM_SYNC_READONLY_AUDIT_PASS')


main()
