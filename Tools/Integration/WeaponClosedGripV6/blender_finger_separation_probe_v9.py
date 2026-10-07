"""Read-only existing-family interior-finger separating-plane feasibility."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2'))
from blender_contact_common import *
POSE=STORE/'Evidence/WeaponClosedGripV6/chain_seat_v8b/result.json';OUT=STORE/'Evidence/WeaponClosedGripV6/finger_interference_probe_v9';assert not OUT.exists();OUT.mkdir(parents=True)
d=load();v=json.loads(POSE.read_text());gun=np.array(v['gun_hand_relative_matrix']);_,b=posed(d,'0.0');parents=d['model']['parents']
def apply(b,rotations):
    new=dict(b)
    for n,r in rotations.items():
        local=np.linalg.inv(b[parents[n]])@b[n];local[:3,:3]=np.array(r)*np.linalg.norm(local[:3,:3],axis=0);new[n]=new[parents[n]]@local
    return new
def evaluated(b):return transform(skin(d['p'],d['weights'],{n:b[n]@d['invref'][n] for n in d['invref']}),np.linalg.inv(b['hand_r']@gun))
baseline=evaluated(apply(b,v['protected_index_local_rotations']));current=evaluated(apply(b,{**v['protected_index_local_rotations'],**v['adapted_local_rotations']}));r={'pairs':[],'native_authored':False}
for a,c in [('middle','ring'),('ring','pinky')]:
    ia=np.array([i for i,w in enumerate(d['weights']) if w.get(a+'_02_r',0)+w.get(a+'_03_r',0)>.6]);ic=np.array([i for i,w in enumerate(d['weights']) if w.get(c+'_02_r',0)+w.get(c+'_03_r',0)>.6]);direction=baseline[ia].mean(0)-baseline[ic].mean(0);direction/=np.linalg.norm(direction);lower=float(np.min(baseline[ia]@direction));upper=float(np.max(baseline[ic]@direction));r['pairs'].append({'a':a,'b':c,'normal_from_b_to_a':direction.tolist(),'a_vertices':ia.tolist(),'b_vertices':ic.tolist(),'baseline_projection_gap_cm':lower-upper,'baseline_plane_offset_cm':(lower+upper)*.5,'current_projection_gap_cm':float(np.min(current[ia]@direction)-np.max(current[ic]@direction))})
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'pairs':[{k:x[k] for k in ('a','b','normal_from_b_to_a','baseline_projection_gap_cm','baseline_plane_offset_cm','current_projection_gap_cm')} for x in r['pairs']]}))
