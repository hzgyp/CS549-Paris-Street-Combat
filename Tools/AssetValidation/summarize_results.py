"""Aggregate completed diagnostics and compare pre/post-resave samples."""
import json
import math
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalWorking/Validation/UE582/2026-09-30-v1/Evidence'


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


before = read('ue_pose_validation_before_resave.json')
after = read('ue_pose_validation.json')
versions = read('version_verification.json')
loaded = read('ue_load_inventory.json')
exports = read('ue_resaved_exports.json')
blender = read('blender_export_audit_resaved.json')
native = read('ue_native_captures.json')
key = lambda s: (s['label'], s['action'], round(s['time'], 6))
previous = {key(s): s for s in before['samples']}
current = {key(s): s for s in after['samples']}
shared = set(previous) & set(current)
maximum = max(math.dist(previous[k]['bone_positions_cm'][bone], current[k]['bone_positions_cm'][bone])
              for k in shared for bone in previous[k]['bone_positions_cm'])
report = {'generated_at': datetime.now().astimezone().isoformat(),
    'scope': 'Local diagnostic baseline, not gameplay/historical/rights acceptance or SFTP publication',
    'original_files_verified': versions['original_files_checked'],
    'changed_originals': versions['changed_originals'],
    'source_packages_with_UE582_header': versions['UE582_header_packages'],
    'fresh_reopen_assets': loaded['loaded_count'], 'reopen_inspection_errors': loaded['errors'],
    'native_captures': len(native['captures']), 'native_capture_errors': native['errors'],
    'pre_resave_samples': len(previous), 'post_resave_samples': len(current),
    'post_resave_pose_errors': after['errors'], 'finite_samples': sum(s['finite'] for s in after['samples']),
    'same_sample_keys': set(previous) == set(current),
    'max_pre_post_bone_displacement_cm': maximum,
    'post_resave_exports': len(exports['exports']),
    'successful_post_resave_exports': sum(e['ok'] and e['size_bytes'] > 0 for e in exports['exports']),
    'export_errors': exports['errors'], 'blender_mesh_imports': len(blender['models']),
    'blender_animation_imports': len(blender['animations']), 'blender_errors': blender['errors'],
    'animations_without_actions': [a['file'] for a in blender['animations'] if not a['actions']],
    'blender_weight_findings': [{'file': model['file'],
        'unweighted': sum(m['unweighted_vertices'] for m in model['meshes']),
        'non_normalized': sum(m['weight_sum_outside_0_001'] for m in model['meshes'])}
        for model in blender['models']]}
sequence_lengths = {a['path'].split('/')[-1]: a['sequence_length'] for a in loaded['assets']
                    if a.get('class') == 'AnimSequence' and '/InPlace/' in a['path']}
report['animation_duration_comparisons'] = []
for animation in blender['animations']:
    if not animation['actions']:
        continue
    start, end = animation['actions'][0]['frame_range']
    duration = (end - start) / animation['fps']
    expected = sequence_lengths[Path(animation['file']).stem]
    report['animation_duration_comparisons'].append({'file': animation['file'],
        'import_fps': animation['fps'], 'UE_seconds': expected, 'Blender_seconds': duration,
        'absolute_difference_seconds': abs(duration - expected)})
if not after.get('finished_at'):
    raise SystemExit('Pose test is incomplete')
(OUT / 'validation_summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'blender_weight_findings'}, indent=2))
