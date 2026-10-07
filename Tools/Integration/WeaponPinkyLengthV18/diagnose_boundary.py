"""Read-only localization of the stopped whole-pinky scale boundary."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12'))
from pivot_common import *

OUT=STORE/'Evidence/WeaponPinkyLengthV18/boundary_diagnosis_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
d=load()
current=json.loads((STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/result.json').read_text())
b={n:np.array(v) for n,v in current['candidate_component_bones'].items()}
names=['pinky_01_r','pinky_02_r','pinky_03_r']
c={n:v.copy() for n,v in b.items()}
root=b[names[0]][:3,3]
for n in names:
    c[n][:3,:3]*=.9
    c[n][:3,3]=root+.9*(b[n][:3,3]-root)
gun=np.array(current['baseline_gun_component_matrix'])
old,new=evaluate(d,b,gun),evaluate(d,c,gun)
affected=np.array([sum(w.get(n,0) for n in names)>1e-8 for w in d['weights']])
boundary=np.flatnonzero(affected & d['digits']['ring'])
r={'scope':__doc__,'candidate_authored':False,
   'boundary':[{'vertex':int(i),'source_weights':d['weights'][int(i)],
                'delta_cm':float(np.linalg.norm(new[i]-old[i])),
                'distance_to_pinky_root_native_cm':float(np.linalg.norm(d['p'][i]-mat(d['model']['ref_component'][names[0]])[:3,3]))}
               for i in boundary],
   'unaffected_delta_cm':float(np.max(np.linalg.norm(new[~affected]-old[~affected],axis=1))),
   'guards':guarded_files()}
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r),flush=True)
