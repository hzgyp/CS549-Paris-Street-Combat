"""Pure intact-grip baseline, fixed-gun evaluation and source-length wrist IK."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'WeaponTriggerAlignmentV2'))
from blender_contact_common import *

INDEX = STORE / 'Evidence/WeaponTriggerAlignmentV2/index_pose_v1/result.json'


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


def evaluate(d, bones, fixed_gun_world):
    p = skin(d['p'], d['weights'], {n: bones[n] @ d['invref'][n] for n in d['invref'] if n in bones})
    return transform(p, np.linalg.inv(fixed_gun_world))


def swing(a, b):
    q = Vector(a).rotation_difference(Vector(b))
    return np.array(q.to_matrix())


def move_wrist(d, bones, delta_world):
    shoulder = bones['upperarm_r'][:3, 3]
    elbow = bones['lowerarm_r'][:3, 3]
    wrist = bones['hand_r'][:3, 3]
    target = wrist + delta_world
    length_a = float(np.linalg.norm(elbow - shoulder))
    length_b = float(np.linalg.norm(wrist - elbow))
    reach = float(np.linalg.norm(target - shoulder))
    assert abs(length_a - length_b) + 1e-5 < reach < length_a + length_b - 1e-5, 'Wrist unreachable without changing bone lengths'
    line = (target - shoulder) / reach
    bend = elbow - shoulder - line * ((elbow - shoulder) @ line)
    assert np.linalg.norm(bend) > 1e-6, 'Original elbow bend plane degenerate'
    bend /= np.linalg.norm(bend)
    along = (length_a ** 2 - length_b ** 2 + reach ** 2) / (2 * reach)
    height = np.sqrt(max(0, length_a ** 2 - along ** 2))
    new_elbow = shoulder + line * along + bend * height
    rotations = {'upperarm_r': swing(elbow - shoulder, new_elbow - shoulder),
                 'lowerarm_r': swing(wrist - elbow, target - new_elbow)}
    explicit = {}
    for n, origin in (('upperarm_r', shoulder), ('lowerarm_r', new_elbow)):
        result = bones[n].copy()
        result[:3, :3] = rotations[n] @ result[:3, :3]
        result[:3, 3] = origin
        explicit[n] = result
    explicit['hand_r'] = bones['hand_r'].copy()
    explicit['hand_r'][:3, 3] = target
    parents = d['model']['parents']
    result = {}

    def get(n):
        if n in result:
            return result[n]
        parent = parents.get(n)
        if n in explicit:
            result[n] = explicit[n]
        elif parent in bones:
            result[n] = get(parent) @ (np.linalg.inv(bones[parent]) @ bones[n])
        else:
            result[n] = bones[n].copy()
        return result[n]

    for n in bones:
        get(n)
    return result


def nonadjacent_pairs(p, ta, tb):
    pairs = intersection_pairs(p, ta, p, tb)
    return [(int(a), int(b)) for a, b in pairs
            if np.min(np.linalg.norm(p[ta[a]][:, None, :] - p[tb[b]][None, :, :], axis=2)) >= 1e-5]


def palm_landmark(d, p):
    tri, gp, gt = d['tri'], d['gp'], d['gt']
    parts = {c['id']: c['triangle_ids'] for c in d['topo']['components']}
    gn, _ = normals(gp, gt)
    gc = gp[gt].mean(1)
    stock = np.array(parts[0], int)
    side = stock[(gn[stock, 0] < -.35) & (gc[stock, 1] > -18) & (gc[stock, 1] < 4)]
    assert len(side) > 3, 'No same-side actual wood surface'
    hn, area = normals(p, tri)
    hc = p[tri].mean(1)
    palm_vertex = np.array([w.get('hand_r', 0) > .5 for w in d['weights']])
    faces = np.flatnonzero(np.all(palm_vertex[tri], axis=1) & (hn[:, 0] > .35)
                          & (hc[:, 1] > -18) & (hc[:, 1] < 4))
    samples = []
    for face in faces:
        q, n, wood_face, gap = project(gp, gt[side], side, hc[face])
        separation = float((hc[face] - q) @ n)
        if hc[face, 0] < q[0] and separation >= 0 and abs(hc[face, 1] - q[1]) < .5:
            samples.append({'palm_triangle': int(face), 'stock_triangle': wood_face,
                            'palm_point_cm': hc[face].tolist(), 'stock_point_cm': q.tolist(),
                            'normal': n.tolist(), 'gap_cm': gap, 'signed_gap_cm': separation,
                            'area_cm2': float(area[face])})
    assert len(samples) >= 4, 'Actual opposing inward palm patch not proved'
    samples.sort(key=lambda x: x['gap_cm'])
    # One contiguous close-contact patch, not one isolated vertex or joint hollow.
    selected = samples[:max(4, len(samples) // 3)]
    center = np.average(np.array([s['palm_point_cm'] for s in selected]), axis=0,
                        weights=np.array([s['area_cm2'] for s in selected]))
    q, normal, wood_face, gap = project(gp, gt[side], side, center)
    # Seat toward the wood side; keep longitudinal/vertical placement intact.
    delta_x = float(q[0] - center[0] - .08)
    assert delta_x > 0, 'Palm already seated; no positive approach shift'
    return {'eligible_surface_samples': samples, 'selected_palm_triangles': [s['palm_triangle'] for s in selected],
            'palm_center_cm': center.tolist(), 'stock_point_cm': q.tolist(), 'stock_triangle': wood_face,
            'stock_normal': normal.tolist(), 'surface_gap_cm': gap,
            'translation_gun_cm': [delta_x, 0., 0.]}
