"""Independent read of frozen V12 static geometry; not playable-rig acceptance."""
import hashlib
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pivot_common import *

SOURCE = BASE / 'pivot_10deg_v1'
OUT = BASE / 'fresh_check_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
blend = SOURCE / 'FixedRightTriggerPivot10deg.blend'
inputs = [blend, SOURCE / 'result.json', FBX, POSES, AUDIT, INDEX, Path(__file__),
          Path(__file__).with_name('pivot_common.py')]
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r = {'errors': [], 'native_authored': False}
try:
    proof = json.loads((SOURCE / 'result.json').read_text())
    d = load()
    bones = {n: np.array(v) for n, v in proof['candidate_component_bones'].items()}
    expected = evaluate(d, bones, np.array(proof['baseline_gun_component_matrix']))
    expected_gun = transform(d['gp'], np.array(proof['rigid_pivot_change_gun_local']))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    errors = {}
    for name, target in [('Right fixed pivot_10deg', expected), ('Left chain pivot_10deg', expected),
                         ('Continuous arms pivot_10deg', expected), ('M1 pivot_10deg', expected_gun)]:
        o = bpy.data.objects[name]
        actual = np.array([list(o.matrix_world @ v.co) for v in o.data.vertices]) * 100
        errors[name] = float(np.max(np.linalg.norm(actual - target, axis=1)))
        assert errors[name] < .0001, 'Fresh geometry differs: ' + name
    r['saved_geometry_max_errors_cm'] = errors
    r['source_armature_bones'] = len(next(o for o in bpy.data.objects if o.type == 'ARMATURE').data.bones)
    r['status'] = 'fresh_static_geometry_read_passed'
    r['limitations'] = ['Baked evaluated geometry is not a new playable rig/action.',
                        'Fresh read does not override any contact or visual failure.']
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == v for k, v in hashes.items())
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(r))
