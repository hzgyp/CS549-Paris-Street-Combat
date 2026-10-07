"""Fresh read-only check including all faces touching any thumb-weighted vertex."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Quaternion

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerPivotV12'))
from pivot_common import load, evaluate, transform, intersection_pairs, edge_check, STORE
BASE=STORE/'Evidence/LeftSupportV20'
OUT=BASE/'skin_boundary_verification_v1'
assert not OUT.exists(), 'Preserve occupied fresh skin identity'
OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
d=load()
source=json.loads((STORE/'Evidence/WeaponPinkyLengthV18/distal_v1/result.json').read_text())
b={n:np.array(m) for n,m in source['candidate_component_bones'].items()}
gun0=np.array(source['baseline_gun_component_matrix'])
cfg=json.loads((BASE/'reuse_pose_v2/binding.json').read_text())
c={n:m.copy() for n,m in b.items()}
names=('thumb_01_l','thumb_02_l','thumb_03_l')
parents=d['model']['parents']
for n in names:
    local=np.linalg.inv(b[parents[n]])@b[n]
    x,y,z,w=cfg['fingers_local'][n]['q']
    local[:3,:3]=np.array(Quaternion((w,x,y,z)).to_matrix())*np.linalg.norm(local[:3,:3],axis=0)
    c[n]=c[parents[n]]@local
before=evaluate(d,b,gun0);after=evaluate(d,c,gun0)
affected=np.array([any(w.get(n,0)>0 for n in names) for w in d['weights']])
indices=np.flatnonzero(np.any(affected[d['tri']],axis=1))
faces=d['tri'][indices]
change=np.array(json.loads((STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/result.json').read_text())['rigid_change_gun_local'])
gp=transform(d['gp'],change)
old={int(indices[a]) for a,_ in intersection_pairs(before,faces,gp,d['gt'])}
new={int(indices[a]) for a,_ in intersection_pairs(after,faces,gp,d['gt'])}
proof=json.loads((BASE/'reuse_pose_v2/result.json').read_text())
bone_error=max(float(np.max(abs(c[n]-np.array(proof['candidate_component_bones'][n])))) for n in c)
r={'status':'fresh_all_influence_boundary_audit',
   'affected_vertices':int(affected.sum()),'all_touching_faces':len(indices),
   'baseline_crossing_faces':sorted(old),'candidate_crossing_faces':sorted(new),
   'new_crossing_faces':sorted(new-old),'removed_crossing_faces':sorted(old-new),
   'fresh_component_matrix_delta':bone_error,
   'true_unaffected_skin_delta_cm':float(np.linalg.norm(after[~affected]-before[~affected],axis=1).max()),
   'right_skin_delta_cm':float(np.linalg.norm(after[d['masks']['r']]-before[d['masks']['r']],axis=1).max()),
   **edge_check(d,before,after),
   'source_mesh_rig_weights_actions_saved':False,'full_grasp_accepted':False}
r['local_boundary_pass']=not r['new_crossing_faces'] and bone_error<1e-6 and r['true_unaffected_skin_delta_cm']<.0001 and r['right_skin_delta_cm']<.0001 and not r['new_severe_edges']
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
if not r['local_boundary_pass']:raise SystemExit(1)
