"""Fresh data-only audit: three existing thumb rotations, no other binding edit."""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE = STORE / 'Evidence/LeftSupportV20'
sys.path.insert(0, str(ROOT / 'Tools/Integration/NPCInteractionV1'))
from common import guard_rows, guards_match

OUT = BASE / 'config_verification_v1'
assert not OUT.exists(), 'Preserve occupied identity'
OUT.mkdir()
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
names = ('thumb_01_l', 'thumb_02_l', 'thumb_03_l')
oldpath = STORE / 'Evidence/GripBindingV18/config_v1/binding.json'
newpath = BASE / 'reuse_pose_v2/binding.json'
old = json.loads(oldpath.read_text())
new = json.loads(newpath.read_text())
proof = json.loads((BASE / 'reuse_pose_v2/result.json').read_text())
assert not proof['errors'] and proof['true_influence_audit_passed']
expected = json.loads(oldpath.read_text())
for name in names:
    q = proof['chosen_existing_pose']['existing_local_rotations'][name]
    assert abs(sum(v*v for v in q)-1) < 1e-6
    expected['fingers_local'][name]['q'] = q
assert new == expected, 'Not exclusively three reused thumb rotations'
cache = STORE / 'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
assert hashlib.sha256(cache.read_bytes()).hexdigest() == '194cd91e6e6d743654ec961d6a387ec8ae3a0c318ca3f5303ac89859fec95bf1'
rows = guard_rows()
assert guards_match(rows)
receipt = {
    'status': 'exact_three_rotation_only_private_variant',
    'config_sha256': hashlib.sha256(newpath.read_bytes()).hexdigest(),
    'baseline_config_sha256': hashlib.sha256(oldpath.read_bytes()).hexdigest(),
    'cache_sha256': hashlib.sha256(cache.read_bytes()).hexdigest(),
    'changed_fields': ['fingers_local.'+n+'.q' for n in names],
    'local_translation_scale_preserved': all(new['fingers_local'][n]['t']==old['fingers_local'][n]['t'] and new['fingers_local'][n]['s']==old['fingers_local'][n]['s'] for n in names),
    'source_pose_identity': proof['chosen_existing_pose']['identity'],
    'guard_count': len(rows), 'guards_match': True,
    'shared_other_digit_skin_delta_cm': proof['checks']['shared_other_digit_max_skin_delta_cm'],
    'native_acceptance': False, 'source_rig_export_authored': False,
}
assert receipt['config_sha256'] == proof['config_sha256']
(OUT / 'result.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
