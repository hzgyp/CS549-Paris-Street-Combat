"""Read-only actual current pinky identity, pose and proportion audit."""
import sys
import traceback
import hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12'))
from pivot_common import *

BASE = STORE/'Evidence/WeaponPinkyLengthV18'
OUT = BASE/'probe_v1'
CURRENT = STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/result.json'
assert not OUT.exists()
OUT.mkdir(parents=True)
r = {'errors':[],'scope':__doc__}
try:
    d = load()
    current = json.loads(CURRENT.read_text())
    bones = {n:np.array(v) for n,v in current['candidate_component_bones'].items()}
    source = {n:mat(t) for n,t in d['poses']['0.0']['bones_component'].items()}
    parents = d['model']['parents']
    pinky = ['pinky_01_r','pinky_02_r','pinky_03_r']
    local_delta = {n:float(np.max(abs(np.linalg.inv(bones[parents[n]])@bones[n]
                                    -np.linalg.inv(source[parents[n]])@source[n]))) for n in pinky}
    affected = np.array([sum(w.get(n,0) for n in pinky)>1e-8 for w in d['weights']])
    r.update(current_pinky_vs_source_local_matrix_delta=local_delta,
             current_pinky_unmodified_from_D059=bool(max(local_delta.values())<1e-10),
             affected_vertices=int(affected.sum()),
             shared_index_vertices=int(np.sum(affected & d['digits']['index'])),
             shared_ring_vertices=int(np.sum(affected & d['digits']['ring'])),
             skeleton_joint_distances_cm={f:[float(np.linalg.norm(bones[f+'_0'+str(i+1)+'_r'][:3,3]
                                                       -bones[f+'_0'+str(i)+'_r'][:3,3])) for i in (1,2)]
                                          for f in ('index','middle','ring','pinky')},
             rest_bone_lengths_blender_m={n:float(d['rig'].data.bones[n].length) for n in pinky},
             phases=list(d['poses']),source_vertices=len(d['p']),source_triangles=len(d['tri']))
    assert r['shared_index_vertices']==0,'Length exception would affect protected index skin'
    r['status'] = 'source_identity_and_current_pose_audited'
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status']='stopped'
finally:
    r['guards']=guarded_files()
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r),flush=True)
    if r['errors'] or r['guards']['mismatches']:
        raise SystemExit(1)
