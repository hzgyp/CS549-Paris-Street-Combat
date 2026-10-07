"""Pure V12 fixed-right baseline, rifle-pivot and left-chain helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'WeaponWholeWristV11'))
from wrist_common import *

PIVOT_PROOF = STORE / 'Evidence/WeaponTriggerAlignmentV2/pivot_fit_v2/result.json'
GUARD_PROOF = STORE / 'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json'
BASE = STORE / 'Evidence/WeaponTriggerPivotV12'


def contact(d, points, gun_points, pad_id):
    parts = {c['id']: set(c['triangle_ids']) for c in d['topo']['components']}
    result = {'digits': {}}
    for name in ('thumb', 'middle', 'ring', 'pinky', 'index'):
        faces = d['tri'][np.all(d['digits'][name][d['tri']], axis=1)]
        pairs = intersection_pairs(points, faces, gun_points, d['gt'])
        result['digits'][name] = {
            'all_gun': len({a for a, b in pairs}),
            **{label: len({a for a, b in pairs if b in parts[part]})
               for label, part in (('stock', 0), ('guard', 4), ('blade', 5))}}
    pad = points[d['tri'][pad_id]].mean(0)
    ids = np.array(sorted(parts[5]), int)
    q, _, face, gap = project(gun_points, d['gt'][ids], ids, pad)
    result.update(index_pad_cm=pad.tolist(), blade_nearest_cm=q.tolist(),
                  blade_nearest_face=face, index_pad_to_blade_cm=gap)
    return result


def left_chain(d, bones, hand_target):
    """Source-length two-link solve; hand orientation follows independent gun goal."""
    shoulder = bones['upperarm_l'][:3, 3]
    elbow = bones['lowerarm_l'][:3, 3]
    wrist = bones['hand_l'][:3, 3]
    target = hand_target[:3, 3]
    la = float(np.linalg.norm(elbow - shoulder))
    lb = float(np.linalg.norm(wrist - elbow))
    reach = float(np.linalg.norm(target - shoulder))
    assert abs(la - lb) + 1e-5 < reach < la + lb - 1e-5, 'Left support target unreachable without stretch'
    line = (target - shoulder) / reach
    bend = elbow - shoulder - line * ((elbow - shoulder) @ line)
    assert np.linalg.norm(bend) > 1e-6, 'Left elbow plane is degenerate'
    bend /= np.linalg.norm(bend)
    along = (la * la - lb * lb + reach * reach) / (2 * reach)
    next_elbow = shoulder + line * along + bend * np.sqrt(max(0, la * la - along * along))
    explicit = {}
    for name, origin, old_vector, new_vector in (
        ('upperarm_l', shoulder, elbow - shoulder, next_elbow - shoulder),
        ('lowerarm_l', next_elbow, wrist - elbow, target - next_elbow)):
        m = bones[name].copy()
        m[:3, :3] = swing(old_vector, new_vector) @ m[:3, :3]
        m[:3, 3] = origin
        explicit[name] = m
    explicit['hand_l'] = hand_target.copy()
    parents = d['model']['parents']
    result = {}

    def get(name):
        if name not in result:
            parent = parents.get(name)
            if name in explicit:
                result[name] = explicit[name]
            elif parent in bones:
                result[name] = get(parent) @ (np.linalg.inv(bones[parent]) @ bones[name])
            else:
                result[name] = bones[name].copy()
        return result[name]

    for name in bones:
        get(name)
    return result


def edge_check(d, before, after):
    edges = np.unique(np.sort(np.concatenate([d['tri'][:, [0, 1]], d['tri'][:, [1, 2]],
                                             d['tri'][:, [2, 0]]]), axis=1), axis=0)
    a = np.linalg.norm(before[edges[:, 1]] - before[edges[:, 0]], axis=1)
    b = np.linalg.norm(after[edges[:, 1]] - after[edges[:, 0]], axis=1)
    return {'new_severe_edges': int(np.sum((b > 3 * np.maximum(a, 1e-8)) & (b - a > 2))),
            'max_extra_edge_length_cm': float(np.max(b - a))}


def guarded_files():
    import hashlib
    records = json.loads(GUARD_PROOF.read_text())['files']
    mismatches = []
    for item in records:
        path = ROOT / item['path']
        if not path.is_file() or path.stat().st_size != item['size_bytes']:
            mismatches.append(item['path'])
        elif hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            mismatches.append(item['path'])
    return {'current_recovery_record_count': len(records), 'mismatches': mismatches,
            'includes_previously_recorded_unselected_V6_rate_difference': True}
