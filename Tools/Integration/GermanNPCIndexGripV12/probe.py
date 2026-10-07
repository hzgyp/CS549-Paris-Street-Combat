"""Read-only existing index-source and accepted V11 reproduction audit."""
import sys,json,traceback
from pathlib import Path
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,GLB,read,write,row,sha,guards,tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform
sys.path.insert(0,str(ROOT/'Tools/Integration/GermanNPCOrderedGripV4'))
from arm_fit import encode
BASE=STORE/'Evidence/GermanNPCIndexGripV12';OUT=BASE/'source_probe_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCLowerGripV11/source_frame_v4/result.json'
REVIEW=STORE/'Evidence/GermanNPCLowerGripV11/frame_failure_views_v1/result.json'
DATA=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
CACHE=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
GERMAN=STORE/'Evidence/WeaponAnimationReuseV1/audit_v1/result.json';DONOR=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
IMAGE=STORE/'Evidence/WeaponTexturedViewsV17/presentation_v2/three_views.jpg'
paths=(PREV,REVIEW,DATA,CACHE,GERMAN,DONOR,GLB,IMAGE,Path(__file__))
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in paths],
   'human_accepted_v11_lower_three_visual_only':True,'source_modified':False,'formal_selected':False,'native_tested':False}
write(OUT/'result.json',r)
try:
    old=read(PREV);d=np.load(DATA);cache=read(CACHE);names=old['bone_names'];parents=old['parents']
    bones={n:mat(v) for n,v in old['after_bones'].items()};rest=d['rest_native_cm'];w=d['weights'];refs=d['reference_matrices'];skin=np.zeros_like(rest)
    for j,n in enumerate(names):skin+=w[:,j,None]*transform(rest,bones[n]@np.linalg.inv(refs[j]))
    skin/=w.sum(1)[:,None];shown=np.load(REVIEW.parent/'diagnostic_geometry.npz')
    r['baseline_skin_cm']=float(np.linalg.norm(skin-shown['skin'],axis=1).max())
    r['baseline_gun_cm']=float(np.linalg.norm(transform(d['gun_local_cm'],mat(old['after_gun_world']))-shown['gun_after_cm'],axis=1).max())
    assert max(r['baseline_skin_cm'],r['baseline_gun_cm'])<.01
    index=['index_'+i+'_r' for i in ('01','02','03')]
    gd=read(GERMAN)['models']['german']['ref_local'];od=read(DONOR)['models']['owner']['ref_local']
    r['reference_basis_deg']={n:tm.angle(gd[n]['rotation'],od[n]['rotation']) for n in ['hand_r',*index]}
    assert max(r['reference_basis_deg'].values())<.001
    def angle(b):
        a=b[index[1]][:3,3]-b[index[0]][:3,3];c=b[index[2]][:3,3]-b[index[1]][:3,3]
        return float(np.degrees(np.arccos(np.clip(a@c/(np.linalg.norm(a)*np.linalg.norm(c)),-1,1))))
    r['baseline_chain_turn_deg']=angle(bones);r['existing_source_samples']=[]
    for clip in ('owner_idle','owner_reload'):
        for phase,sample in cache['clips'][clip]['samples'].items():
            src={n:mat(v) for n,v in sample['bones_component'].items()};new={n:v.copy() for n,v in bones.items()};delta={};locals={}
            for n in index:
                parent=parents[n];oldlocal=np.linalg.inv(bones[parent])@bones[n];donor=np.linalg.inv(src[parent])@src[n]
                # Keep01 rooted/oriented; real bend from the mature02/03 only.
                local=oldlocal.copy()
                if n!=index[0]:local[:3,:3]=donor[:3,:3]/np.linalg.norm(donor[:3,:3],axis=0)*np.linalg.norm(oldlocal[:3,:3],axis=0)
                new[n]=new[parent]@local;locals[n]=encode(local)['q'];delta[n]=tm.angle(encode(oldlocal)['q'],locals[n])
            r['existing_source_samples'].append({'clip':clip,'phase_s':float(phase),'asset':cache['clips'][clip]['asset'],
              'chain_turn_deg':angle(new),'local_rotation_delta_deg':delta,'candidate_index_local_q':locals})
    r['status']='read_only_index_source_and_baseline_verified'
except Exception:r['errors'].append(traceback.format_exc());r['status']='probe_failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(json.dumps({k:r.get(k) for k in ('status','errors','baseline_chain_turn_deg','reference_basis_deg','existing_source_samples')},indent=2))
