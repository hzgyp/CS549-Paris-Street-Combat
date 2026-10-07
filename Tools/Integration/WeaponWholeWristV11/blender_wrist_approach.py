"""One0.75cm whole right wrist approach, all digit local poses intact, gun fixed."""
import hashlib
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wrist_common import *

PROBE = STORE / 'Evidence/WeaponWholeWristV11/palm_landmarks_v2b/result.json'
PIVOT = STORE / 'Evidence/WeaponTriggerAlignmentV2/pivot_fit_v2/result.json'
OUT = STORE / 'Evidence/WeaponWholeWristV11/small_approach_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
inputs = [FBX, POSES, AUDIT, CALIB, TOPOLOGY, INDEX, PROBE, PIVOT, Path(__file__),
          Path(__file__).with_name('wrist_common.py'),
          Path(__file__).resolve().parents[1] / 'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-3:]:
    (OUT / p.name).write_bytes(p.read_bytes())
r = {'scope': __doc__, 'errors': [], 'native_authored': False, 'source_clip_modified': False,
     'views': [], 'phases': [], 'candidate_count': 1, 'finger_local_pose_modified': False}


def write():
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')


def contact(d, points, pad_id):
    tri, gp, gt = d['tri'], d['gp'], d['gt']
    parts = {c['id']: set(c['triangle_ids']) for c in d['topo']['components']}
    result = {'digits': {}, 'digit_self_pairs': {}}
    for name in ('thumb', 'middle', 'ring', 'pinky', 'index'):
        faces = tri[np.all(d['digits'][name][tri], axis=1)]
        pairs = intersection_pairs(points, faces, gp, gt)
        result['digits'][name] = {'all_gun_crossing_triangles': len({a for a, b in pairs}),
                                 'stock': len({a for a, b in pairs if b in parts[0]}),
                                 'guard': len({a for a, b in pairs if b in parts[4]}),
                                 'blade': len({a for a, b in pairs if b in parts[5]})}
    for a, b in (('middle', 'ring'), ('ring', 'pinky'), ('thumb', 'index'), ('index', 'middle')):
        ta = tri[np.all(d['digits'][a][tri], axis=1)]
        tb = tri[np.all(d['digits'][b][tri], axis=1)]
        result['digit_self_pairs'][a + '_' + b] = len(nonadjacent_pairs(points, ta, tb))
    pad = points[tri[pad_id]].mean(0)
    blade = np.array(sorted(parts[5]))
    q, _, _, gap = project(gp, gt[blade], blade, pad)
    result['index_pad_cm'] = pad.tolist()
    result['index_pad_to_blade_cm'] = gap
    result['blade_nearest_cm'] = q.tolist()
    return result


try:
    d = load()
    accepted = json.loads(INDEX.read_text())
    probe = json.loads(PROBE.read_text())
    pivot = json.loads(PIVOT.read_text())
    assert not probe['errors'] and probe['inputs_unchanged']
    direction = np.array(probe['derived_translation_gun_cm'])
    delta = direction / np.linalg.norm(direction) * .75
    assert np.linalg.norm(delta) <= 1.5
    b = baseline(d, '0.0', accepted)
    gun = b['hand_r'] @ np.array(accepted['gun_hand_relative_matrix'])
    world_delta = gun[:3, :3] @ delta
    after_bones = move_wrist(d, b, world_delta)
    before = evaluate(d, b, gun)
    after = evaluate(d, after_bones, gun)
    r['translation_gun_cm'] = delta.tolist()
    r['translation_native_component_cm'] = world_delta.tolist()
    r['fixed_gun_native_component_matrix'] = gun.tolist()
    r['baseline_component_bones'] = {n: v.tolist() for n, v in b.items()}
    r['candidate_component_bones'] = {n: v.tolist() for n, v in after_bones.items()}
    parents = d['model']['parents']
    fingers = [n for n in b if n.endswith('_r') and n.startswith(('index_', 'thumb_', 'middle_', 'ring_', 'pinky_'))]
    finger_delta = max(float(np.max(abs(np.linalg.inv(b[parents[n]]) @ b[n] -
                                        np.linalg.inv(after_bones[parents[n]]) @ after_bones[n]))) for n in fingers)
    assert finger_delta < 1e-10, 'Finger local pose changed'
    r['max_finger_local_matrix_delta'] = finger_delta
    r['right_hand_orientation_matrix_delta'] = float(np.max(abs(b['hand_r'][:3, :3] - after_bones['hand_r'][:3, :3])))
    r['wrist_translation_error_cm'] = float(np.linalg.norm(after_bones['hand_r'][:3, 3] - b['hand_r'][:3, 3] - world_delta))
    r['left_support_skin_delta_cm'] = float(np.max(np.linalg.norm(after[d['masks']['l']] - before[d['masks']['l']], axis=1)))
    r['arm_length_errors_cm'] = []
    for a, c in (('upperarm_r', 'lowerarm_r'), ('lowerarm_r', 'hand_r')):
        old = np.linalg.norm(b[c][:3, 3] - b[a][:3, 3])
        new = np.linalg.norm(after_bones[c][:3, 3] - after_bones[a][:3, 3])
        r['arm_length_errors_cm'].append(float(abs(new - old)))
    pad_id = int(pivot['landmarks']['pad_source_triangle_id'])
    row = {'phase_s': 0., 'before': contact(d, before, pad_id), 'after': contact(d, after, pad_id)}
    edges = np.unique(np.sort(np.concatenate([d['tri'][:, [0, 1]], d['tri'][:, [1, 2]], d['tri'][:, [2, 0]]]), axis=1), axis=0)
    old_lengths = np.linalg.norm(before[edges[:, 1]] - before[edges[:, 0]], axis=1)
    new_lengths = np.linalg.norm(after[edges[:, 1]] - after[edges[:, 0]], axis=1)
    row['new_severe_edges'] = int(np.sum((new_lengths > 3 * np.maximum(old_lengths, 1e-8)) & (new_lengths - old_lengths > 2)))
    row['max_extra_edge_length_cm'] = float(np.max(new_lengths - old_lengths))
    palm_faces = np.array(probe['landmarks']['selected_palm_triangles'])
    r['palm_patch_mean_x_approach_cm'] = float((after[d['tri'][palm_faces]].mean((0, 1)) - before[d['tri'][palm_faces]].mean((0, 1)))[0])
    idx = row['after']['digits']['index']
    increased_digits = [n for n in ('thumb', 'middle', 'ring', 'pinky', 'index')
                        if row['after']['digits'][n]['all_gun_crossing_triangles'] > row['before']['digits'][n]['all_gun_crossing_triangles']]
    row['increased_gun_crossing_digits'] = increased_digits
    r['phases'].append(row)
    r['early_gate_passed'] = bool(row['after']['index_pad_to_blade_cm'] <= .2 and idx['stock'] == 0
                                 and idx['guard'] == 0 and not increased_digits and row['new_severe_edges'] == 0
                                 and max(r['arm_length_errors_cm']) < .001 and r['left_support_skin_delta_cm'] < 1e-7)
    write()
    scene = setup_scene()
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    wood = material('Wood neutral diagnostic', (.21, .14, .09))
    metal = material('Metal', (.18, .21, .22))
    handmat = material('Intact skin', (.61, .42, .29))
    indexmat = material('Unchanged local index pose', (1., .26, .07))
    blue = material('Unchanged left support', (.19, .43, .61))
    garment = material('Existing sleeve', (.23, .27, .16))
    rifle = mesh('Fixed M1 reference', d['gp'], d['gt'], [wood, metal])
    parts = {c['id']: set(c['triangle_ids']) for c in d['topo']['components']}
    for poly in rifle.data.polygons:
        poly.material_index = 0 if poly.index in parts[0] else 1
    rt = d['tri'][np.all(d['masks']['r'][d['tri']], axis=1)]
    lt = d['tri'][np.all(d['masks']['l'][d['tri']], axis=1)]
    visible = []
    for condition, points in (('before', before), ('whole_wrist_7p5mm', after)):
        for o in visible:
            bpy.data.objects.remove(o, do_unlink=True)
        right = mesh('Right intact grip ' + condition, points, rt, [handmat, indexmat])
        left = mesh('Left support unchanged ' + condition, points, lt, [blue])
        for poly, face in zip(right.data.polygons, rt):
            poly.material_index = int(np.all(d['digits']['index'][face]))
        visible = [right, left]
        for view, offset in (('right', (.28, -.05, .10)), ('opposite', (-.28, -.05, -.08)),
                             ('top', (.02, -.04, .30)), ('bottom', (.02, -.04, -.30)),
                             ('oblique', (-.20, -.25, .20))):
            camera([-.035, -.02, -.025], offset, .26)
            file = condition + '_' + view + '.png'
            scene.render.filepath = str(OUT / file)
            bpy.ops.render.render(write_still=True)
            r['views'].append({'file': file, 'condition': condition, 'view': view})
            write()
        right.hide_render = True
        left.hide_render = True
        full = mesh('Whole arms continuity ' + condition, points, d['tri'], [garment, handmat])
        visible.append(full)
        for poly, face in zip(full.data.polygons, d['tri']):
            poly.material_index = int(np.all((d['masks']['r'] | d['masks']['l'])[face]))
        for view, offset in (('whole_oblique', (-1.2, -.1, .45)), ('whole_reverse', (1.2, -.1, .45))):
            camera([0, .12, -.10], offset, 1.2)
            file = condition + '_' + view + '.png'
            scene.render.filepath = str(OUT / file)
            bpy.ops.render.render(write_still=True)
            r['views'].append({'file': file, 'condition': condition, 'view': view})
            write()
        full.hide_render = True
        right.hide_render = False
        left.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'WholeWristApproach_7p5mm.blend'))
    r['saved_comparison'] = 'WholeWristApproach_7p5mm.blend'
    r['status'] = 'comparison_pending_visual_review' if r['early_gate_passed'] else 'stopped_at_actual_contact_gate_comparison_retained'
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == v for k, v in hashes.items())
    write()
    print(json.dumps({k: r.get(k) for k in ('status', 'errors', 'inputs_unchanged', 'early_gate_passed', 'translation_gun_cm')}))
