"""Read-only final protection audit of requested20degree and retained10degree."""
import ast
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponTriggerPivotV13'
OUT = BASE / 'verification_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
guard = BASE.parent / 'ReloadIndexContactV6/map_recovery_v1/result.json'
records = json.loads(guard.read_text())['files']
errors = []
for item in records:
    p = ROOT / item['path']
    if not p.is_file() or p.stat().st_size != item['size_bytes'] or hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
        errors.append({'native_guard': item['path']})
proofs = {}
for label, p in [('new20', BASE / 'pivot_20deg_v1b/result.json'),
                 ('fresh20', BASE / 'fresh_check_v1/result.json'),
                 ('retained10', BASE.parent / 'WeaponTriggerPivotV12/pivot_10deg_v1/result.json'),
                 ('retained_fresh10', BASE.parent / 'WeaponTriggerPivotV12/fresh_check_v1/result.json')]:
    proof = json.loads(p.read_text())
    changed = [name for name, sha in proof['input_hashes'].items()
               if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha]
    errors.extend({'input_changed': name} for name in changed)
    errors.extend({'task_error': e} for e in proof['errors'])
    proofs[label] = {'status': proof['status'], 'input_changes': changed,
                     'errors': proof['errors'], 'contact_gate_passed': proof.get('early_gate_passed')}
scripts = list(Path(__file__).parent.glob('*.py'))
for p in scripts:
    ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
now = datetime.now(timezone.utc)
map_path = ROOT / 'Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap'
r = {'status': 'file_protection_passed_contact_reported' if not errors else 'verification_failed',
     'errors': errors, 'time_utc': now.isoformat(),
     'time_edt_oct4': now.astimezone(timezone(timedelta(hours=-4))).isoformat(),
     'native_guard_count': len(records), 'known_unselected_V6_rate_difference_in_current_snapshot': True,
     'proofs': proofs, 'new_ast_script_count': len(scripts),
     'formal_map_size': map_path.stat().st_size,
     'formal_map_sha256': hashlib.sha256(map_path.read_bytes()).hexdigest(),
     'native_authored': False, 'selected': False,
     'contact_gate_passed': proofs['new20']['contact_gate_passed'],
     'limitation': 'Static comparison and file protection are not playable rig/motion/runtime acceptance.'}
(OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print(json.dumps(r))
raise SystemExit(0 if not errors else 1)
