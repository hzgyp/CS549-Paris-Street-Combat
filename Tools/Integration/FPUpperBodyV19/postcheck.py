"""Audit the ENTIRE return fade, not just the action-state boundary."""
import hashlib,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'GripBindingV18'))
from common import STORE,guard,config
base=STORE/'Evidence/FPUpperBodyV19';city=base/'city_v1'
r=json.loads((city/'result.json').read_text());frames=r['motion_frames']
pairs=[(a,b) for a,b in zip(frames,frames[1:]) if b['action']=='Ready' and b['holding_alpha']<1]
checks=[]
for a,b in pairs:
    checks.append({'seconds':b['seconds'],'interval_s':b['seconds']-a['seconds'],
        'alpha_before':a['holding_alpha'],'alpha_after':b['holding_alpha'],
        'gun_step_cm':math.dist(a['gun_camera']['t'],b['gun_camera']['t']),
        'wrist_step_cm':math.dist(a['wrist_camera']['t'],b['wrist_camera']['t'])})
out={'whole_return_fade_checks':checks,'threshold_cm':3,
     'whole_return_fade_pass':bool(checks) and max(max(x['gun_step_cm'],x['wrist_step_cm']) for x in checks)<3,
     'earlier_observer_gap':'enforced only first Reloading->Ready adjacent pair, not the remaining Ready fade',
     'motion_source_results_preserved':True,'guards':guard(),
     'city_result_sha256':hashlib.sha256((city/'result.json').read_bytes()).hexdigest(),
     'overall_fp_acceptance':False,'formal_selection':False}
assert not out['guards']['mismatches'];config()
folder=base/'postcheck_v1';assert not folder.exists();folder.mkdir()
(folder/'source.py').write_bytes(Path(__file__).read_bytes())
(folder/'result.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
