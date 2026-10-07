"""Read-only actual trigger and rear-neck/inward-palm rotation-direction proof."""
import hashlib
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pivot_common import *

OUT = BASE / 'landmarks_v1'
assert not OUT.exists(), 'Never overwrite a prior evidence identity'
OUT.mkdir(parents=True)
inputs = [FBX, POSES, AUDIT, CALIB, TOPOLOGY, INDEX, PIVOT_PROOF, Path(__file__),
          Path(__file__).with_name('pivot_common.py'),
          Path(__file__).resolve().parents[1] / 'WeaponWholeWristV11/wrist_common.py',
          Path(__file__).resolve().parents[1] / 'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r = {'errors': [], 'native_authored': False, 'pose_modified': False, 'views': []}


def write():
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')


try:
    d = load()
    approved = json.loads(INDEX.read_text())
    proof = json.loads(PIVOT_PROOF.read_text())
    bones = baseline(d, '0.0', approved)
    gun = bones['hand_r'] @ np.array(approved['gun_hand_relative_matrix'])
    points = evaluate(d, bones, gun)
    pad_id = int(proof['landmarks']['pad_source_triangle_id'])
    pad = points[d['tri'][pad_id]].mean(0)
    parts = {c['id']: np.array(c['triangle_ids'], int) for c in d['topo']['components']}
    pivot, _, pivot_id, pad_gap = project(d['gp'], d['gt'][parts[5]], parts[5], pad)
    gn, _ = normals(d['gp'], d['gt'])
    gc = d['gp'][d['gt']].mean(1)
    # Actual rear neck surface: not fore-end, butt center or a finger-bone mean.
    wood = parts[0][(gn[parts[0], 0] < -.35) & (gc[parts[0], 1] > -18)
                    & (gc[parts[0], 1] < -4)]
    hn, ha = normals(points, d['tri'])
    hc = points[d['tri']].mean(1)
    palm_mask = np.array([w.get('hand_r', 0) > .7 for w in d['weights']])
    faces = np.flatnonzero(np.all(palm_mask[d['tri']], axis=1) & (hn[:, 0] > .35)
                           & (hc[:, 1] > -18) & (hc[:, 1] < -4))
    samples = []
    for face in faces:
        q, normal, wood_id, gap = project(d['gp'], d['gt'][wood], wood, hc[face])
        signed = float((hc[face] - q) @ normal)
        if signed > .03 and hc[face, 0] < q[0]:
            samples.append({'palm_triangle': int(face), 'palm_point_cm': hc[face].tolist(),
                            'palm_normal': hn[face].tolist(), 'stock_triangle': wood_id,
                            'stock_point_cm': q.tolist(), 'gap_cm': gap,
                            'signed_gap_cm': signed})
    assert samples, 'No actual inward rear-neck/palm facing pair identified'
    # Only a turn-direction landmark, NOT an empty grasp center or full closure.
    selected = min(samples, key=lambda s: s['gap_cm'])
    a = np.array(selected['stock_point_cm']) - pivot
    b = np.array(selected['palm_point_cm']) - pivot
    axis = np.cross(a, b)
    assert np.linalg.norm(axis) > 1e-6
    axis /= np.linalg.norm(axis)
    angle = float(np.arctan2(np.linalg.norm(np.cross(a, b)), a @ b))
    r.update(baseline_component_bones={n: m.tolist() for n, m in bones.items()},
             baseline_gun_component_matrix=gun.tolist(), actual_index_pad_triangle=pad_id,
             actual_index_pad_cm=pad.tolist(), trigger_pivot_triangle=pivot_id,
             trigger_pivot_gun_cm=pivot.tolist(), actual_index_pad_gap_cm=pad_gap,
             direction_landmark=selected, eligible_palm_pair_count=len(samples),
             gun_local_turn_axis=axis.tolist(), landmark_full_alignment_angle_deg=float(np.degrees(angle)),
             proposed_partial_turn_deg=10.,
             limitations=['Nearest actual inward-palm pair indicates direction only, not complete C-grasp seating.',
                          '10 degrees is a single user-informed hypothesis, not measured final acceptance.'])
    scene = setup_scene()
    scene.render.resolution_x, scene.render.resolution_y = 1200, 900
    gun_obj = mesh('Unchanged M1 baseline', d['gp'], d['gt'],
                   [material('Wood', (.21, .14, .09)), material('Metal', (.18, .21, .22))])
    for poly in gun_obj.data.polygons:
        poly.material_index = int(poly.index not in set(parts[0]))
    hand = mesh('Fixed right hand baseline', points,
                d['tri'][np.all(d['masks']['r'][d['tri']], axis=1)], [material('Skin', (.61, .42, .29))])
    for name, p, color in [('Trigger actual pivot', pivot, (1., .08, .03)),
                           ('Rear neck marker', np.array(selected['stock_point_cm']), (.03, .7, .15)),
                           ('Inward palm marker', np.array(selected['palm_point_cm']), (.05, .35, 1.))]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=.0018, location=p * .01)
        o = bpy.context.object
        o.name = name
        o.data.materials.append(material(name, color))
    for view, offset in [('top', (.02, -.04, .30)), ('bottom', (.02, -.04, -.30)),
                         ('oblique', (-.20, -.25, .20))]:
        camera([-.035, -.02, -.025], offset, .26)
        scene.render.filepath = str(OUT / (view + '.png'))
        bpy.ops.render.render(write_still=True)
        r['views'].append(view + '.png')
    r['status'] = 'read_only_direction_landmarks_collected'
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == v for k, v in hashes.items())
    write()
    print(json.dumps({k: r.get(k) for k in ('status', 'errors', 'inputs_unchanged', 'gun_local_turn_axis',
                                          'landmark_full_alignment_angle_deg')}))
