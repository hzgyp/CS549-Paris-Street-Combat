"""Read-only content closeout and metadata for the stopped animation attempt."""
import ast
import json
from pathlib import Path
from weapon_animation_reuse_common import ROOT, STORE, JOURNAL, guard, read, sha

CASE = ROOT / 'Failures/AN001-20261004-existing-weapon-animation'
DEST = ROOT / 'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json'
assert not DEST.exists(), 'Preserve prior closeout'
assert not (CASE / 'MANIFEST.json').exists()
protected = guard()
rows = read(STORE / 'Evidence/WeaponAnimationReuseV1/retarget_v1/result.json')['packages']
rows += read(STORE / 'Evidence/WeaponAnimationReuseV1/author_reload_v1/result.json')['packages']
for row in rows:
    p = ROOT / row['path']
    assert p.stat().st_size == row['size_bytes'] and sha(p) == row['sha256']
    row['selection'] = 'unselected_failed_visual_gate'
assert len(rows) == 5
for version in (1, 2):
    assert not (STORE / f'Content/ParisCombat/Blueprints/WeaponAnimationReuseV1/BP_PCAnimationOwnerViewV{version}.uasset').exists()
    assert not (STORE / f'Evidence/WeaponAnimationReuseV1/author_owner_v{version}/result.json').exists()
    assert read(JOURNAL / f'author_owner_v{version}.log.exit.json')['exit_code'] == 3
views = read(STORE / 'Evidence/WeaponAnimationReuseV1/reload_views_v2/result.json')
assert not views['errors'] and len(views['captures']) == 6
assert views['samples'][0]['state'] == 'Ready'
assert all(x['state'] == 'Reloading' for x in views['samples'][1:])
for tool in (ROOT / 'Tools/Integration').glob('*weapon_animation*.py'):
    ast.parse(tool.read_text(encoding='utf-8'), filename=str(tool))
inventory = {
    'schema_version': 1, 'date': '2026-10-04', 'owner': 'yg745',
    'status': 'stopped_failed_reload_visual_and_recoil_native_authoring',
    'canonical_map_unchanged': True,
    'canonical_map_sha256': '2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519',
    'protected_file_count': protected, 'files': rows,
    'files_remain_in_place': True, 'automatic_restore_authority': False,
    'catalog_selected': False, 'immutable_release_created': False,
    'functional_regression_run': False, 'recoil_native_package_saved': False,
    'old_reload_original_deleted': False,
    'old_reload_binding_withdrawn_in_failed_candidate_only': True,
    'failure_case': 'Failures/AN001-20261004-existing-weapon-animation/FAILURE_ANALYSIS.md',
    'evidence_root': (STORE / 'Evidence/WeaponAnimationReuseV1').relative_to(ROOT).as_posix(),
    'stopped_author_identities': ['author_owner_v1', 'author_owner_v2'],
    'review': 'Six valid frozen reload phases captured; actual visual rejection, not continuous-motion acceptance.',
}
DEST.write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')

files = list((STORE / 'Evidence/WeaponAnimationReuseV1').rglob('*'))
files += list(JOURNAL.glob('*'))
for crash in ('UECC-Windows-D44454C14D6EDAEBB3B69EB1969C06A5_0000',
              'UECC-Windows-BBE8FAAD4D44AB8E62688FB83A3A574E_0000'):
    files += list((ROOT / 'Unreal/ParisStreetCombat/Saved/Crashes' / crash).rglob('*'))
files += [ROOT / x['path'] for x in rows]
files += list((ROOT / 'Tools/Integration').glob('*weapon_animation*.py'))
files += [ROOT / 'Tools/Integration/run_weapon_animation_reuse.ps1',
          ROOT / 'Tools/Integration/weapon_animation_reuse_common.py',
          ROOT / 'Docs/Development/WEAPON_ANIMATION_REUSE_V1.md',
          ROOT / 'Docs/Development/WEAPON_ANIMATION_REUSE_V1_ZH.md']
manifest = []
for p in sorted(set(x for x in files if x.is_file())):
    manifest.append({'path': p.relative_to(ROOT).as_posix(), 'size_bytes': p.stat().st_size,
                     'sha256': sha(p), 'storage': 'retained_in_place_no_duplicate_copy'})
(CASE / 'MANIFEST.json').write_text(json.dumps({
    'schema_version': 1, 'date': '2026-10-04', 'status': 'stopped_evidence_retained_in_place',
    'migration_performed': False, 'automatic_restore_authority': False, 'files': manifest,
}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'protected_unchanged': protected, 'native_drafts': len(rows),
                  'case_entries': len(manifest), 'total_bytes': sum(x['size_bytes'] for x in manifest)}, indent=2))
