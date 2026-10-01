"""Freeze a local repair handoff. This never publishes assets or updates CATALOG."""
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1'
OUT = LAB / 'Evidence/Repair20261001'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(part)
    return result.hexdigest()


versions = read(OUT / 'repair_versions.json')
inventory = read(OUT / 'FinalInventory/ue_load_inventory.json')
poses = read(OUT / 'NativeRegression/ue_pose_validation.json')
baseline_poses = read(LAB / 'Evidence/ue_pose_validation.json')
exchange = read(OUT / 'exchange_fresh_verification.json')
native = read(OUT / 'FinalNativeCaptures/ue_native_captures.json')
adaptation = read(OUT / 'native_adaptation.json')
textures = read(OUT / 'texture_exports.json')
assert versions['UE582_header_packages'] == 540 and not versions['changed_originals']
assert inventory['loaded_count'] == 540 and not inventory['errors']
assert len(poses['samples']) == 300 and poses.get('finished_at') and not poses['errors']
assert all(p['finite'] for p in poses['samples'])
assert len(native['captures']) == 24 and not native['errors']
assert len(exchange['meshes']) == 12 and len(exchange['animations']) == 7 and len(exchange['sources']) == 12
assert not exchange['errors'] and not any(s['missing_images'] for s in exchange['sources'])
assert all(m['same_triangles'] and m['same_hierarchy'] and not m['bad_weight_sums'] and not m['unweighted'] for m in exchange['meshes'])
assert max(a['error_seconds'] for a in exchange['animations']) < 1e-6
assets = {a['path']: a for a in inventory['assets']}
for model in adaptation['models']:
    original, adapted = assets[model['source']], assets[model['adapted']]
    assert original['bones'] == adapted['bones']
    assert original['skeleton'] == adapted['skeleton'] and original['physics_asset'] == adapted['physics_asset']
    for slot in model['eye_slots']:
        assert adapted['materials'][slot]['material'].startswith('/Game/ParisCombat/Characters/Adaptation/Materials/M_EyePBR_')
for item in textures['textures']:
    assert digest(OUT / item['file']) == item['sha256']
key = lambda row: (row['label'], row['action'], round(row['time'], 6))
previous = {key(p): p for p in baseline_poses['samples']}
maximum = max(math.dist(p['bone_positions_cm'][bone], previous[key(p)]['bone_positions_cm'][bone])
              for p in poses['samples'] for bone in p['bone_positions_cm'])
files = []
for folder, kind in [(LAB / 'Content', 'native_UE582'), (OUT / 'Textures', 'exchange_texture'), (OUT / 'Exchange', 'exchange_source')]:
    for path in sorted(folder.rglob('*')):
        if not path.is_file() or ('ParisCombat/Tests/' in path.relative_to(LAB).as_posix()):
            continue
        if kind == 'native_UE582' and path.suffix not in ('.uasset', '.umap'):
            continue
        files.append({'path': path.relative_to(ROOT).as_posix(), 'kind': kind,
            'size_bytes': path.stat().st_size, 'sha256': digest(path)})
report = {'updated_at': datetime.now().astimezone().isoformat(),
    'status': 'local_repair_baseline_not_shared_release', 'owner': 'Yupu Guo',
    'engine': 'UE 5.8.2-56702186', 'blender': '5.2.2 LTS',
    'physical_workspace': LAB.relative_to(ROOT).as_posix(),
    'original_files_verified': 590, 'changed_originals': [],
    'native_closure_packages': 540, 'fresh_load_errors': [], 'persisted_eye_bindings': 4,
    'native_samples': 300, 'native_captured_pose_views': sum(len(p['captures']) for p in poses['samples']),
    'native_body_and_head_captures': 24, 'max_bone_checkpoint_change_cm': maximum,
    'fresh_exchange_meshes': 12, 'fresh_exchange_actions': 7, 'reopened_blender_sources': 12,
    'missing_blender_images': 0, 'max_exchange_duration_error_seconds': max(a['error_seconds'] for a in exchange['animations']),
    'publication': {'rights': 'pending_three_bundle_team_sharing_confirmation', 'immutable_sftp_release': 'not published',
        'active_catalog_changed': False, 'git_commit_push': 'not performed'},
    'limitations': ['Simple eye PBR loses legacy refraction; final Paris daylight/shadow acceptance remains.',
        'Blender PBR sources are editing previews, not lossless native UE shading.',
        'Normalized exchange models were not reimported over native vendor meshes.',
        'Gameplay gun contact, events, physics, history, LOD/performance and packaging remain deferred.',
        'Existing city/original/backups outside this character batch were not relocated or deleted.'],
    'file_count': len(files), 'size_bytes': sum(f['size_bytes'] for f in files), 'files': files}
(OUT / 'repair_handoff.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))
