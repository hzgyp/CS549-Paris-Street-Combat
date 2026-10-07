"""Read-only independent check of retained static evidence; never rerun fitting."""
import ast
import math
import sys
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'GermanNPCGripV1'))
from common import ROOT, STORE, read, write, sha, row, guards, tm

BASE = STORE / 'Evidence/GermanNPCOrderedGripV4'
OUT = BASE / 'ordered_native_v2'
assert not (OUT / 'verification.json').exists()
o = read(BASE / 'offline_v6/result.json')
n = read(OUT / 'result.json')
f = read(BASE / 'final_clearance_v7/result.json')
assert not o['errors'] and not n['errors']
assert n['status'] == 'german_ordered_static_views_require_user_review'
assert not n['map_saved'] and not n['formal_selected']
assert not n['original_npc_driver_changed'] and not n['fp_binding_called']
assert not n['contact_or_gameplay_accepted']
assert guards() == n['guards_after'] == o['guards_after'] == 618
for e in o['inputs']:
    assert sha(ROOT / e['path']) == e['sha256'], e['path']
for p, h in n['input_hashes'].items():
    assert sha(ROOT / p) == h, p

def matrix(t):
    q = np.array(t['q'], dtype=float)
    q /= np.linalg.norm(q)
    x, y, z, w = q
    rot = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                    [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                    [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    value = np.eye(4)
    value[:3, :3] = rot @ np.diag(t['s'])
    value[:3, 3] = t['t']
    return value

def distance(a, b):
    return float(np.linalg.norm(np.array(a)-np.array(b)))

assert len(n['captures']) == 15
for c in n['captures']:
    assert Image.open(OUT / c['file']).size == (1600, 1000)
    assert c['gun_drift_cm'] < .01
    assert c['pose_parity']['max_bone_position_cm'] < .01
    assert c['pose_parity']['max_bone_rotation_deg'] < .01

parity = {}
for stage in ('before', 'first', 'after'):
    actual, expected = n[stage]['bones'], o[stage+'_bones']
    assert set(actual) == set(expected)
    pos = max(distance(actual[b]['t'], expected[b]['t']) for b in actual)
    rot = max(tm.angle(actual[b]['q'], expected[b]['q']) for b in actual)
    assert pos < .01 and rot < .01
    parity[stage] = {'position_cm': pos, 'rotation_deg': rot}
before, first, after = [n[s]['bones'] for s in ('before', 'first', 'after')]
g0, g1, g2 = [n[s]['gun_world'] for s in ('before', 'first', 'after')]
first_bone_error = max(float(np.max(abs(matrix(before[b])-matrix(first[b])))) for b in before)
assert first_bone_error < 1e-6
trigger = o['trigger_pivot_gun_cm']
stock = o['stock_pivot_gun_cm']
trigger_pivot_error = distance(tm.point(g0, trigger), tm.point(g1, trigger))
stock_pivot_error = distance(tm.point(g1, stock), tm.point(g2, stock))
yaw = tm.angle(g0['q'], g1['q'])
pitch = tm.angle(g1['q'], g2['q'])
assert trigger_pivot_error < .01 and stock_pivot_error < .01
assert abs(yaw-5) < .01 and abs(pitch-12) < .01
relative_before = np.linalg.inv(matrix(first['hand_r'])) @ matrix(g1)
relative_after = np.linalg.inv(matrix(after['hand_r'])) @ matrix(g2)
relative = float(np.max(abs(relative_before-relative_after)))
relative_pos = distance(relative_before[:3, 3], relative_after[:3, 3])
relative_rot = tm.angle(tm.local_q(first['hand_r'], g1), tm.local_q(after['hand_r'], g2))
assert relative_pos < .01 and relative_rot < .01
protected = max(float(np.max(abs(matrix(before[b])-matrix(after[b])))) for b in o['protected_bones'])
assert protected < 1e-6
digit_error = 0.0
digit_pos = 0.0
digit_rot = 0.0
for b in before:
    if b.startswith(('thumb_', 'index_', 'middle_', 'ring_', 'pinky_')):
        p = o['parents'][b]
        old = np.linalg.inv(matrix(before[p])) @ matrix(before[b])
        new = np.linalg.inv(matrix(after[p])) @ matrix(after[b])
        digit_error = max(digit_error, float(np.max(abs(old-new))))
        digit_pos = max(digit_pos, distance(old[:3, 3], new[:3, 3]))
        digit_rot = max(digit_rot, tm.angle(tm.local_q(before[p], before[b]), tm.local_q(after[p], after[b])))
assert digit_pos < .01 and digit_rot < .01
lengths = {}
for side in ('r', 'l'):
    u, l, h = ['upperarm_'+side, 'lowerarm_'+side, 'hand_'+side]
    old = [distance(before[u]['t'], before[l]['t']), distance(before[l]['t'], before[h]['t'])]
    new = [distance(after[u]['t'], after[l]['t']), distance(after[l]['t'], after[h]['t'])]
    assert max(abs(a-b) for a, b in zip(old, new)) < .01
    lengths[side] = {'before_cm': old, 'after_cm': new}
assert f['status'] == 'failed_preserved' and f['errors']
assert not (BASE / 'final_clearance_v7/geometry.npz').exists()
receipts = []
for identity in ('ordered_native_v1', 'ordered_native_v2'):
    p = ROOT / 'tmp/german-npc-ordered-grip-v4' / (identity+'.log.exit.json')
    receipt = read(p)
    assert receipt['exit_code'] == 0
    receipts.append(receipt)
presentation = read(OUT / 'presentation.json')
for e in presentation['images'] + presentation['native_originals']:
    assert sha(ROOT / e['path']) == e['sha256']
for p in Path(__file__).parent.glob('*.py'):
    ast.parse(p.read_text(encoding='utf-8-sig'), filename=str(p))
write(OUT / 'verification.json', {
    'status': 'static_reproduction_verified_not_full_contact_or_motion_acceptance',
    'guards': 618, 'native_originals_opened': 15, 'composed_sheets_opened': 4,
    'source_input_hashes_exact': True, 'bone_parity': parity,
    'extra_yaw_deg': yaw, 'downward_pitch_deg': pitch,
    'trigger_pivot_during_yaw_error_cm': trigger_pivot_error,
    'stock_pivot_during_pitch_error_cm': stock_pivot_error,
    'first_stage_bone_matrix_error': first_bone_error,
    'right_gun_hand_pitch_matrix_error': relative,
    'right_gun_hand_pitch_position_error_cm': relative_pos,
    'right_gun_hand_pitch_rotation_error_deg': relative_rot,
    'protected_bone_world_matrix_error': protected,
    'digit_local_matrix_error': digit_error, 'native_digit_local_position_error_cm': digit_pos,
    'native_digit_local_rotation_error_deg': digit_rot, 'native_arm_lengths': lengths,
    'right_digit_mixed_skin_rigid_error_cm': o['right_digit_rigid_skin_error_cm'],
    'failed_clearance_not_used': True, 'native_exit_receipts': receipts,
    'tool_sources': [row(p) for p in sorted(Path(__file__).parent.glob('*')) if p.is_file()],
    'formal_selected': False, 'full_contact_accepted': False, 'motion_tested': False,
    'visual_residuals': ['Loose firing grasp/straight index and guard/blade overlap',
        'Left thumb/index/little stock crossings', 'Small exposed skin chips at left cuff; no zero-artifact claim'],
})
print('Static evidence verified; 618 guards exact. Contact/motion NOT accepted.')
