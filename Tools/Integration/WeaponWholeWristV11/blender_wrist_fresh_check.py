"""Fresh-open frozen wrist comparison; read-only, not a rig/runtime acceptance."""
import hashlib
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wrist_common import *

SOURCE = STORE / 'Evidence/WeaponWholeWristV11/small_approach_v1'
OUT = STORE / 'Evidence/WeaponWholeWristV11/fresh_check_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
blend = SOURCE / 'WholeWristApproach_7p5mm.blend'
proof = json.loads((SOURCE / 'result.json').read_text())
inputs = [blend, SOURCE / 'result.json', FBX, POSES, AUDIT, INDEX, Path(__file__), Path(__file__).with_name('wrist_common.py')]
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
r = {'errors': [], 'native_authored': False}
try:
    d = load()
    b = {n: np.array(v) for n, v in proof['candidate_component_bones'].items()}
    expected = evaluate(d, b, np.array(proof['fixed_gun_native_component_matrix']))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    right = bpy.data.objects['Right intact grip whole_wrist_7p5mm']
    actual = np.array([list(v.co) for v in right.data.vertices]) * 100
    delta = float(np.max(np.linalg.norm(actual - expected, axis=1)))
    assert delta < .0001, 'Saved geometry differs from evaluated candidate'
    r['saved_candidate_max_vertex_error_cm'] = delta
    r['right_hand_vertices'] = len(right.data.vertices)
    r['right_hand_faces'] = len(right.data.polygons)
    r['gun_vertices'] = len(bpy.data.objects['Fixed M1 reference'].data.vertices)
    r['source_armature_bones'] = len(next(o for o in bpy.data.objects if o.type == 'ARMATURE').data.bones)
    r['status'] = 'fresh_static_comparison_read_passed'
    r['limitations'] = ['Static evaluated derivative, not an authored playable rig or exported action.',
                        'Contact gate failed; fresh read does not make this an accepted asset.']
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == v for k, v in hashes.items())
    r['input_hashes'] = hashes
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(r))
