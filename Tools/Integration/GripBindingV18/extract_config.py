"""Read immutable V18 matrices; emit private native binding parameters only."""
import hashlib,json,sys,traceback
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12'))
from pivot_common import ROOT,STORE,AUDIT,guarded_files
BASE=STORE/'Evidence/GripBindingV18'
OUT=BASE/'config_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
V18=STORE/'Evidence/WeaponPinkyLengthV18/distal_v1'
V16=STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/result.json'
inputs=[V18/'result.json',V18/'RightPinkyDistalShorter.blend',V16,AUDIT,Path(__file__)]
hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r={'errors':[],'scope':__doc__,'native_authored':False,'source_actions_modified':False}
def row(m):
    sc=np.linalg.norm(m[:3,:3],axis=0)
    rotation=m[:3,:3]/sc
    assert np.linalg.det(rotation)>.9999 and np.max(abs(rotation.T@rotation-np.eye(3)))<1e-5
    q=Matrix(rotation.tolist()).to_quaternion()
    return {'t':m[:3,3].tolist(),'q':[q.x,q.y,q.z,q.w],'s':sc.tolist()}
try:
    r['guards_before']=guarded_files();assert not r['guards_before']['mismatches']
    data=json.loads((V18/'result.json').read_text());assert not data['errors']
    assert hashes[(V18/'RightPinkyDistalShorter.blend').relative_to(ROOT).as_posix()]==data['blend_sha256']
    b={n:np.array(v) for n,v in data['candidate_component_bones'].items()}
    parent=json.loads(AUDIT.read_text())['models']['owner']['parents']
    fingers={}
    for side in ('r','l'):
        for digit in ('thumb','index','middle','ring','pinky'):
            for index in (1,2,3):
                name=f'{digit}_{index:02}_{side}'
                assert parent[name] in b
                fingers[name]=row(np.linalg.inv(b[parent[name]])@b[name])
    assert max(abs(v-.9) for v in fingers['pinky_02_r']['s'])<1e-5
    assert max(abs(v-1) for v in fingers['pinky_03_r']['s'])<1e-5
    config={'source_blend_sha256':data['blend_sha256'],
            'fingers_local':fingers,
            'gun_hand_relative':row(np.array(json.loads(V16.read_text())['new_gun_hand_relative_matrix'])),
            'support_hand_relative_to_right':row(np.linalg.inv(b['hand_r'])@b['hand_l']),
            'elbow_pole_relative_to_right_cm':(np.linalg.inv(b['hand_r'])@np.append(b['lowerarm_l'][:3,3],1))[:3].tolist(),
            'source_mesh':'/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3',
            'native_model_and_action_bytes_unchanged':True}
    (OUT/'binding.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    r.update(status='private_parameters_extracted_unchanged_accepted_pose',finger_count=len(fingers),
             config_sha256=hashlib.sha256((OUT/'binding.json').read_bytes()).hexdigest())
except Exception:r['status']='stopped';r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes']=hashes
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    r['guards_after']=guarded_files()
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r),flush=True)
    if r['errors'] or not r['inputs_unchanged'] or r['guards_after']['mismatches']:raise SystemExit(1)
