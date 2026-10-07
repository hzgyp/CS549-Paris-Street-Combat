"""Fresh scoped serialization audit; preserve protected dictionaries exactly."""
import sys,json
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards,tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform
BASE=STORE/'Evidence/GermanNPCAlliedGripV13';OUT=BASE/'final_check_v1'
DATA=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
assert not OUT.exists();OUT.mkdir(parents=True)
d=np.load(DATA);r={'status':'starting','guards_before':guards(),'variants':{},'formal_selected':False,'native_tested':False,'contact_accepted':False,'inputs':[row(DATA),row(Path(__file__))]}
for name,folder in [('transfer','transfer_fit_v2'),('seating','seating_v3')]:
    path=BASE/folder/'result.json';old=read(path);assert not old['errors'];r['inputs'].append(row(path))
    # Original protected dictionaries avoid float32 round trips in the final
    # PRIVATE pose payload. This does not rerun or change the contact fit.
    normalized=json.loads(json.dumps(old));changed=[]
    for n in old['protected_bones']:
        if normalized['after_bones'][n]!=old['before_bones'][n]:changed.append(n)
        normalized['after_bones'][n]=old['before_bones'][n]
    normalized['status']='private_parameter_transfer_comparison_not_selected'
    normalized['serialization_normalization_only']=True
    before={n:mat(v) for n,v in old['after_bones'].items()};after={n:mat(v) for n,v in normalized['after_bones'].items()}
    def skin(b):
        p=np.zeros_like(d['rest_native_cm'])
        for j,n in enumerate(old['bone_names']):p+=d['weights'][:,j,None]*transform(d['rest_native_cm'],b[n]@np.linalg.inv(d['reference_matrices'][j]))
        return p/d['weights'].sum(1)[:,None]
    delta=float(np.linalg.norm(skin(after)-skin(before),axis=1).max());assert delta<.001
    assert all(normalized['after_bones'][n]==old['before_bones'][n] for n in old['protected_bones'])
    q_errors={n:tm.angle(tm.local_q(normalized['after_bones'][old['parents'][n]],normalized['after_bones'][n]),q) for n,q in old['transferred_digit_local_rotations'].items()}
    assert max(q_errors.values())<.001
    file=OUT/(name+'_private_pose.json');write(file,normalized)
    r['variants'][name]={'pose':row(file),'protected_dicts_exact':True,'float_serialization_normalized_bones':changed,
      'max_rendered_skin_change_from_serialization_cm':delta,'reused_local_rotation_max_error_deg':max(q_errors.values()),
      'new_fit_performed':False,'contact_status_unchanged':True}
r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs'])
r['status']='private_reused_params_verified_contact_incomplete_not_selected';write(OUT/'result.json',r)
print(r['status']);print(r['variants'])
