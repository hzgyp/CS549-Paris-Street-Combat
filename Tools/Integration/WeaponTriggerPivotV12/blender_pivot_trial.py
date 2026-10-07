"""ONE10-degree actual-trigger rifle pivot with fixed right hand and left-arm IK."""
import hashlib
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pivot_common import *

PROBE = BASE / 'landmarks_v1/result.json'
OUT = BASE / 'pivot_10deg_v1'
assert not OUT.exists(), 'Never overwrite a prior comparison'
OUT.mkdir(parents=True)
inputs = [FBX, POSES, AUDIT, CALIB, TOPOLOGY, INDEX, PIVOT_PROOF, PROBE,
          Path(__file__), Path(__file__).with_name('pivot_common.py'),
          Path(__file__).resolve().parents[1] / 'WeaponWholeWristV11/wrist_common.py',
          Path(__file__).resolve().parents[1] / 'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for path in inputs[-4:]:
    (OUT / path.name).write_bytes(path.read_bytes())
r = {'scope': __doc__, 'errors': [], 'views': [], 'native_authored': False,
     'candidate_count': 1, 'source_motion_modified': False, 'right_hand_modified': False,
     'all_finger_local_poses_modified': False, 'phase_s': 0., 'rotation_degrees': 10.}


def write():
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')


try:
    r['guards_before'] = guarded_files()
    assert not r['guards_before']['mismatches'], 'Protected current native files changed before trial'
    d = load()
    probe = json.loads(PROBE.read_text())
    assert not probe['errors'] and probe['inputs_unchanged']
    old_bones = {n: np.array(v) for n, v in probe['baseline_component_bones'].items()}
    old_gun = np.array(probe['baseline_gun_component_matrix'])
    right_points = evaluate(d, old_bones, old_gun)
    axis = np.array(probe['gun_local_turn_axis'])
    pivot = np.array(probe['trigger_pivot_gun_cm'])
    rotation = np.array(Quaternion(Vector(axis), np.radians(10.)).to_matrix())
    change = np.eye(4)
    change[:3, :3] = rotation
    change[:3, 3] = pivot - rotation @ pivot
    new_gun = old_gun @ change
    component_change = new_gun @ np.linalg.inv(old_gun)
    new_bones = left_chain(d, old_bones, component_change @ old_bones['hand_l'])
    after = evaluate(d, new_bones, old_gun)
    gun_after = transform(d['gp'], change)
    pad_id = int(probe['actual_index_pad_triangle'])
    parents = d['model']['parents']
    digits = [n for n in old_bones if n.startswith(('index_', 'middle_', 'ring_', 'pinky_', 'thumb_'))]
    finger_error = max(float(np.max(abs(np.linalg.inv(old_bones[parents[n]]) @ old_bones[n]
                                       - np.linalg.inv(new_bones[parents[n]]) @ new_bones[n]))) for n in digits)
    right_names = [n for n in old_bones if n.endswith('_r')]
    right_bone_error = max(float(np.max(abs(old_bones[n] - new_bones[n]))) for n in right_names)
    right_skin_error = float(np.max(np.linalg.norm(after[d['masks']['r']] - right_points[d['masks']['r']], axis=1)))
    assert finger_error < 1e-10 and right_bone_error < 1e-10 and right_skin_error < .0001
    before_contact = contact(d, right_points, d['gp'], pad_id)
    after_contact = contact(d, after, gun_after, pad_id)
    left_rigid_reference = transform(right_points, change)
    palm_mask = np.array([w.get('hand_l', 0) > .98 for w in d['weights']])
    palm_faces = np.flatnonzero(np.all(palm_mask[d['tri']], axis=1))
    assert len(palm_faces), 'No rigid left palm skin patch'
    left_error = float(np.max(np.linalg.norm(after[d['tri'][palm_faces]] - left_rigid_reference[d['tri'][palm_faces]], axis=2)))
    left_finger_mask = np.array([sum(v for n, v in w.items() if n.endswith('_l')
                                   and n.startswith(('index_', 'middle_', 'ring_', 'pinky_', 'thumb_'))) > .98
                                for w in d['weights']])
    left_finger_error = float(np.max(np.linalg.norm(after[left_finger_mask] - left_rigid_reference[left_finger_mask], axis=1)))
    arm_errors = []
    for a, b in (('upperarm_l', 'lowerarm_l'), ('lowerarm_l', 'hand_l')):
        arm_errors.append(float(abs(np.linalg.norm(old_bones[a][:3, 3] - old_bones[b][:3, 3])
                                    - np.linalg.norm(new_bones[a][:3, 3] - new_bones[b][:3, 3]))))
    index = after_contact['digits']['index']
    nonindex = ('thumb', 'middle', 'ring', 'pinky')
    increased_clear = [n for n in nonindex if before_contact['digits'][n]['stock'] == 0
                       and after_contact['digits'][n]['stock'] > 0]
    edges = edge_check(d, right_points, after)
    gate = dict(pivot_error_cm=float(np.linalg.norm(transform(pivot[None], change)[0] - pivot)),
                right_bone_matrix_delta=right_bone_error, right_skin_delta_cm=right_skin_error,
                all_finger_local_matrix_delta=finger_error, left_palm_tracking_error_cm=left_error,
                left_finger_tracking_error_cm=left_finger_error, arm_length_errors_cm=arm_errors,
                formerly_clear_stock_digits_now_crossing=increased_clear, **edges)
    old_sum = sum(before_contact['digits'][n]['stock'] for n in nonindex)
    new_sum = sum(after_contact['digits'][n]['stock'] for n in nonindex)
    r['early_gate_passed'] = bool(gate['pivot_error_cm'] < .001 and left_error < .02
                                 and max(arm_errors) < .001 and not edges['new_severe_edges']
                                 and index['stock'] == 0 and index['guard'] == 0
                                 and index['blade'] <= before_contact['digits']['index']['blade']
                                 and after_contact['index_pad_to_blade_cm'] <= .2
                                 and new_sum <= old_sum and not increased_clear)
    landmark = probe['direction_landmark']
    old_mark = np.array(landmark['stock_point_cm'])
    target_mark = np.array(landmark['palm_point_cm'])
    new_mark = transform(old_mark[None], change)[0]
    r.update(before_contact=before_contact, after_contact=after_contact, checks=gate,
             nonindex_wood_crossing_sum_before=old_sum, nonindex_wood_crossing_sum_after=new_sum,
             turn_axis_gun_local=axis.tolist(), gun_pivot_cm=pivot.tolist(),
             rigid_pivot_change_gun_local=change.tolist(),
             new_gun_hand_relative_matrix=(np.linalg.inv(old_bones['hand_r']) @ new_gun).tolist(),
             baseline_component_bones={n: v.tolist() for n, v in old_bones.items()},
             candidate_component_bones={n: v.tolist() for n, v in new_bones.items()},
             baseline_gun_component_matrix=old_gun.tolist(), candidate_gun_component_matrix=new_gun.tolist(),
             support_actual_palm_faces=palm_faces.tolist(),
             palm_direction_gap_before_cm=float(np.linalg.norm(old_mark - target_mark)),
             palm_direction_gap_after_cm=float(np.linalg.norm(new_mark - target_mark)),
             rear_marker_motion_cm=(new_mark - old_mark).tolist())
    write()
    scene = setup_scene()
    scene.render.resolution_x, scene.render.resolution_y = 1200, 900
    wood = material('Wood contact diagnostic', (.21, .14, .09))
    metal = material('Metal', (.18, .21, .22))
    skinmat = material('Fixed firing hand', (.61, .42, .29))
    orange = material('Protected index', (1., .26, .07))
    blue = material('Following support hand', (.19, .43, .61))
    garment = material('Original sleeve', (.23, .27, .16))
    stock_ids = set(next(c for c in d['topo']['components'] if c['id'] == 0)['triangle_ids'])
    rt = d['tri'][np.all(d['masks']['r'][d['tri']], axis=1)]
    lt = d['tri'][np.all(d['masks']['l'][d['tri']], axis=1)]
    visible = []
    for condition, points, gun_points in [('before', right_points, d['gp']), ('pivot_10deg', after, gun_after)]:
        for o in visible:
            bpy.data.objects.remove(o, do_unlink=True)
        rifle = mesh('M1 ' + condition, gun_points, d['gt'], [wood, metal])
        for poly in rifle.data.polygons:
            poly.material_index = int(poly.index not in stock_ids)
        right = mesh('Right fixed ' + condition, points, rt, [skinmat, orange])
        for poly, face in zip(right.data.polygons, rt):
            poly.material_index = int(np.all(d['digits']['index'][face]))
        left = mesh('Left chain ' + condition, points, lt, [blue])
        visible = [rifle, right, left]
        close_views = [('right', (.28, -.05, .10)), ('opposite', (-.28, -.05, -.08)),
                       ('top', (.02, -.04, .30)), ('bottom', (.02, -.04, -.30)),
                       ('oblique', (-.20, -.25, .20))]
        for view, offset in close_views:
            camera([-.035, -.02, -.025], offset, .26)
            file = condition + '_' + view + '.png'
            scene.render.filepath = str(OUT / file)
            bpy.ops.render.render(write_still=True)
            r['views'].append({'file': file, 'condition': condition, 'view': view})
        camera([0, .16, 0], (-1.2, -.3, .45), 1.35)
        file = condition + '_whole_rifle.png'
        scene.render.filepath = str(OUT / file)
        bpy.ops.render.render(write_still=True)
        r['views'].append({'file': file, 'condition': condition, 'view': 'whole_rifle'})
        camera([0, .225, -.02], (-.25, .02, .20), .36)
        file = condition + '_left_support.png'
        scene.render.filepath = str(OUT / file)
        bpy.ops.render.render(write_still=True)
        r['views'].append({'file': file, 'condition': condition, 'view': 'left_support'})
        right.hide_render = left.hide_render = True
        full = mesh('Continuous arms ' + condition, points, d['tri'], [garment, skinmat, blue])
        for poly, face in zip(full.data.polygons, d['tri']):
            poly.material_index = 1 if np.all(d['masks']['r'][face]) else (2 if np.all(d['masks']['l'][face]) else 0)
        visible.append(full)
        for view, offset in [('whole_oblique', (-1.2, -.1, .45)), ('whole_reverse', (1.2, -.1, .45))]:
            camera([0, .12, -.10], offset, 1.2)
            file = condition + '_' + view + '.png'
            scene.render.filepath = str(OUT / file)
            bpy.ops.render.render(write_still=True)
            r['views'].append({'file': file, 'condition': condition, 'view': view})
        full.hide_render = True
        right.hide_render = left.hide_render = False
        write()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'FixedRightTriggerPivot10deg.blend'))
    r['saved_comparison'] = 'FixedRightTriggerPivot10deg.blend'
    r['status'] = ('static_contact_screen_passed_requires_visual_review' if r['early_gate_passed']
                   else 'stopped_at_contact_or_continuity_gate_comparison_retained')
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == v for k, v in hashes.items())
    r['guards_after'] = guarded_files()
    write()
    print(json.dumps({k: r.get(k) for k in ('status', 'errors', 'early_gate_passed', 'inputs_unchanged',
                                          'checks', 'before_contact', 'after_contact')}))
