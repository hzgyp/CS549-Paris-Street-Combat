"""Read-only V14/source/old10+20 and current native guard audit."""
import ast
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponThumbGunSeatV14'
OUT = BASE/'verification_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
records = json.loads((BASE.parent/'ReloadIndexContactV6/map_recovery_v1/result.json').read_text())['files']
errors = []
for item in records:
    p = ROOT/item['path']
    if not p.is_file() or p.stat().st_size!=item['size_bytes'] or sha(p)!=item['sha256']:
        errors.append({'native_guard':item['path']})
proofs = {}
for label,path in [('probe',BASE/'surface_probe_v1/result.json'),('fit',BASE/'thumb_seat_v1/result.json'),
                   ('fresh',BASE/'fresh_check_v1/result.json'),
                   ('old10',BASE.parent/'WeaponTriggerPivotV12/pivot_10deg_v1/result.json'),
                   ('old10fresh',BASE.parent/'WeaponTriggerPivotV12/fresh_check_v1/result.json'),
                   ('old20',BASE.parent/'WeaponTriggerPivotV13/pivot_20deg_v1b/result.json'),
                   ('old20fresh',BASE.parent/'WeaponTriggerPivotV13/fresh_check_v1/result.json')]:
    proof = json.loads(path.read_text())
    changed = [name for name,value in proof['input_hashes'].items() if sha(ROOT/name)!=value]
    errors.extend({'changed_input':name} for name in changed)
    errors.extend({'task_error':value} for value in proof['errors'])
    proofs[label] = {'status':proof['status'],'input_changes':changed,'errors':proof['errors']}
scripts = list(Path(__file__).parent.glob('*.py'))
for p in scripts:
    ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
fit = json.loads((BASE/'thumb_seat_v1/result.json').read_text())
map_path = ROOT/'Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap'
thumb = fit['after_contact']['digits']['thumb']
r = {'status':'file_protection_passed_local_result_reported' if not errors else 'verification_failed',
     'time_utc':datetime.now(timezone.utc).isoformat(),'errors':errors,'proofs':proofs,
     'native_guard_count':len(records),'includes_previously_recorded_unselected_V6_rate_difference':True,
     'script_ast_count':len(scripts),'thumb_only_surface_screen_passed':thumb['all_gun']==0 and thumb['stock']==0,
     'complete_planned_contact_and_continuity_gate_passed':fit['early_gate_passed'],
     'trigger_gap_cm':fit['after_contact']['index_pad_to_blade_cm'],
     'formal_map_size_bytes':map_path.stat().st_size,'formal_map_sha256':sha(map_path),
     'blend_sha256':sha(BASE/'thumb_seat_v1/FixedHandThumbSeat.blend'),
     'native_authored':False,'selected':False,
     'limitations':['Thumb-local screen is not complete grip/contact acceptance.',
                    'Left skin tracking exceeds the declared 0.02 cm gate; no threshold relaxed.',
                    'Index local pose stays intact but trigger contact is displaced.']}
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r))
raise SystemExit(0 if not errors else 1)
