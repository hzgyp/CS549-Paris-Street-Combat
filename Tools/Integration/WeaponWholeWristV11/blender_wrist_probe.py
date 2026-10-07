"""Read-only intact grasp/true stock-section landmarks; no pose fitting."""
import hashlib
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'WeaponTriggerAlignmentV2'))
from blender_contact_common import *

OUT = STORE / 'Evidence/WeaponWholeWristV11/landmarks_v1'
INDEX = STORE / 'Evidence/WeaponTriggerAlignmentV2/index_pose_v1/result.json'
assert not OUT.exists()
OUT.mkdir(parents=True)
inputs = [FBX, POSES, AUDIT, CALIB, TOPOLOGY, INDEX, Path(__file__),
          Path(__file__).resolve().parents[1] / 'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-2:]:
    (OUT / p.name).write_bytes(p.read_bytes())
r = {'scope': __doc__, 'errors': [], 'native_authored': False, 'pose_modified': False}


def baseline(d, phase, accepted):
    _, bones = posed(d, phase)
    result = dict(bones)
    parents = d['model']['parents']
    for name in ('index_01_r', 'index_02_r', 'index_03_r'):
        local = np.linalg.inv(bones[parents[name]]) @ bones[name]
        target = np.array(accepted['reused_pose']['local_transforms'][name])
        local[:3, :3] = target[:3, :3] / np.linalg.norm(target[:3, :3], axis=0) * np.linalg.norm(local[:3, :3], axis=0)
        result[name] = result[parents[name]] @ local
    return result


def stock_section(gp, stock_triangles, y):
    segments = []
    for face in stock_triangles:
        points = gp[face]
        hits = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            da, db = points[a, 1] - y, points[b, 1] - y
            if da * db < 0:
                point = points[a] + (points[b] - points[a]) * (-da / (db - da))
                hits.append(point[[0, 2]])
            elif abs(da) < 1e-9:
                hits.append(points[a, [0, 2]])
        unique = {tuple(np.round(p, 6)): p for p in hits}
        if len(unique) == 2:
            segments.append(tuple(unique))
        elif len(unique) > 2:
            raise AssertionError('Coplanar/ambiguous stock section; no fit')
    graph = {}
    for a, b in set(tuple(sorted(s)) for s in segments):
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)
    assert graph and all(len(v) == 2 for v in graph.values()), 'Actual section is not closed degree2 contour'
    remaining = set(graph)
    loops = []
    while remaining:
        start = min(remaining)
        previous = None
        current = start
        loop = []
        while True:
            loop.append(current)
            remaining.discard(current)
            choices = sorted(graph[current] - ({previous} if previous is not None else set()))
            nxt = choices[0]
            previous, current = current, nxt
            if current == start:
                break
            assert current not in loop and len(loop) <= len(graph), 'Invalid section loop'
        p = np.array(loop)
        q = np.roll(p, -1, axis=0)
        cross = p[:, 0] * q[:, 1] - q[:, 0] * p[:, 1]
        area = float(cross.sum() / 2)
        assert abs(area) > 1e-6
        center = ((p + q) * cross[:, None]).sum(0) / (6 * area)
        loops.append({'points_xz_cm': p.tolist(), 'area_cm2': abs(area), 'center_xz_cm': center.tolist()})
    return loops


try:
    d = load()
    accepted = json.loads(INDEX.read_text())
    bones = baseline(d, '0.0', accepted)
    gun = np.array(accepted['gun_hand_relative_matrix'])
    invgun = np.linalg.inv(bones['hand_r'] @ gun)
    hand_names = [f'{finger}_0{joint}_r' for finger in ('middle', 'ring', 'pinky', 'thumb') for joint in (2, 3)]
    joint_points = transform(np.array([bones[n][:3, 3] for n in hand_names]), invgun)
    hollow = joint_points.mean(0)
    parts = {c['id']: c['triangle_ids'] for c in d['topo']['components']}
    loops = stock_section(d['gp'], d['gt'][parts[0]], float(hollow[1]))
    closest = min(loops, key=lambda x: np.linalg.norm(np.array(x['center_xz_cm']) - hollow[[0, 2]]))
    target = np.array([closest['center_xz_cm'][0], hollow[1], closest['center_xz_cm'][1]])
    delta = target - hollow
    r['method'] = 'ONE source grasp-hollow mean to true closed wood section area-center; transverse translation only'
    r['baseline'] = {'clip': json.loads(POSES.read_text())['clips']['owner_reload']['asset'], 'phase_s': 0.0,
                     'approved_index_reuse': str(INDEX.relative_to(ROOT)), 'gun_hand_relative_matrix': gun.tolist()}
    r['right_chain'] = {n: {'parent': d['model']['parents'][n], 'component_matrix': bones[n].tolist()}
                        for n in bones if n in ('upperarm_r', 'lowerarm_r', 'hand_r') or ('twist' in n and n.endswith('_r'))}
    r['landmarks'] = {'grasp_joint_names': hand_names, 'grasp_joint_points_gun_cm': joint_points.tolist(),
                      'grasp_hollow_gun_cm': hollow.tolist(), 'stock_sections': loops,
                      'selected_stock_center_gun_cm': target.tolist()}
    r['derived_translation_gun_cm'] = delta.tolist()
    r['derived_translation_length_cm'] = float(np.linalg.norm(delta))
    r['translation_gate_passed'] = bool(np.linalg.norm(delta) <= 1.5)
    r['limitations'] = ['Joint hollow is a proposed whole-grip landmark, not actual skin contact acceptance.',
                        'Cross-section center is real wood, but one translation cannot guarantee all digits/trigger fit.']
    r['status'] = 'landmarks_collected' if r['translation_gate_passed'] else 'stopped_at_translation_cap'
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == v for k, v in hashes.items())
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: r.get(k) for k in ('status', 'errors', 'inputs_unchanged', 'derived_translation_gun_cm', 'derived_translation_length_cm')}))
