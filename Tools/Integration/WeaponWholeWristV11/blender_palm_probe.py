"""One read-only actual opposing palm/stock-side correction, no pose edit."""
import hashlib
import json
import sys
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wrist_common import *

OUT = STORE / 'Evidence/WeaponWholeWristV11/palm_landmarks_v2b'
assert not OUT.exists()
OUT.mkdir(parents=True)
inputs = [FBX, POSES, AUDIT, CALIB, TOPOLOGY, INDEX, Path(__file__), Path(__file__).with_name('wrist_common.py'),
          Path(__file__).resolve().parents[1] / 'WeaponTriggerAlignmentV2/blender_contact_common.py']
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
for p in inputs[-3:]:
    (OUT / p.name).write_bytes(p.read_bytes())
r = {'scope': __doc__, 'errors': [], 'native_authored': False, 'pose_modified': False}
try:
    d = load()
    accepted = json.loads(INDEX.read_text())
    bones = baseline(d, '0.0', accepted)
    gun_world = bones['hand_r'] @ np.array(accepted['gun_hand_relative_matrix'])
    p = evaluate(d, bones, gun_world)
    r['landmarks'] = palm_landmark(d, p)
    r['derived_translation_gun_cm'] = r['landmarks']['translation_gun_cm']
    r['derived_translation_length_cm'] = float(np.linalg.norm(r['derived_translation_gun_cm']))
    r['translation_gate_passed'] = bool(r['derived_translation_length_cm'] <= 1.5)
    r['status'] = 'actual_palm_landmarks_collected' if r['translation_gate_passed'] else 'stopped_at_translation_cap'
except Exception:
    r['status'] = 'stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes'] = hashes
    r['inputs_unchanged'] = all(hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == v for k, v in hashes.items())
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: r.get(k) for k in ('status', 'errors', 'inputs_unchanged', 'derived_translation_gun_cm', 'derived_translation_length_cm')}))
