"""Generate an unselected local diagnostic inventory, not Catalog restore authority."""
import json
from german_rifle_ue_common import ROOT, STORE, GUARDS, read, sha, guard

OUT = ROOT / 'Assets/Integration/GERMAN_RIFLE_UE_DRAFT_INVENTORY_20261004.json'
assert not OUT.exists(), 'Preserve occupied metadata identity'
EVIDENCE = STORE / 'Evidence/GermanRifleUEV1'
imported, authored, rejected, review = [read(EVIDENCE / n / 'result.json') for n in ('import_v3', 'author_v2', 'author_v1', 'review_v3')]
assert not imported['errors'] and not authored['errors'] and not review['errors']
validation = read(EVIDENCE / 'review_validation_v1/result.json')
assert all(validation['checks'].values())
assert validation['source']['sha256'] == sha(EVIDENCE / 'review_v3/result.json')
rows = imported['native_files'] + authored['native_files']
for row in rows + rejected['native_files']:
    p = ROOT / row['path']
    assert p.stat().st_size == row['size_bytes'] and sha(p) == row['sha256']
proofs = []
for name in ('import_v3', 'author_v2', 'review_v3', 'review_validation_v1'):
    p = EVIDENCE / name / 'result.json'
    proofs.append({'path': p.relative_to(ROOT).as_posix(), 'size_bytes': p.stat().st_size, 'sha256': sha(p)})
combat = STORE / 'Evidence/CityGameplay20261002/Runtime/german_combat_v2/combat.json'
c = read(combat)
assert not c['errors'] and c.get('all_assertions_passed') and c.get('ammo_conserved') and c.get('reload_conserved')
proofs.append({'path': combat.relative_to(ROOT).as_posix(), 'size_bytes': combat.stat().st_size, 'sha256': sha(combat)})
d = {'schema_version': 1, 'date': '2026-10-04', 'owner': 'yg745',
     'status': 'local_unselected_native_rifle_and_action_review_not_catalog_or_restore_authority',
     'source_asset': 'german-rifle-model-20261004-v1', 'human_review': 'pending',
     'canonical_map_unchanged': True, 'canonical_map_sha256': '2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519',
     'review_package': authored['package'], 'mesh': imported['mesh'],
     'files': rows, 'native_file_count': len(rows), 'native_bytes': sum(f['size_bytes'] for f in rows),
     'rejected_unselected_v1': rejected['native_files'], 'validation': proofs,
     'protected_count': guard(), 'muzzle_frame_cm': [0, 83.23, 0],
     'grip_anchor_cm': read(GUARDS)['grip_anchor_cm'], 'runtime': 'UE native Blueprint; no runtime bridge/Python',
     'remaining': ['human player movement/body/eye-height review', 'human German gun contact/appearance review',
        'generic reload contact', 'historical variant/loadout', 'selection/publication', 'mission/AI/FPS/package/second machine']}
OUT.write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8')
print('Unselected inventory:', len(rows), 'native files; protected inputs:', d['protected_count'])
