"""Resolve the user's linked Allied FP grasp, without copying lengths/offsets."""
import sys,traceback
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,GLB,read,write,row,sha,guards,tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat
sys.path.insert(0,str(ROOT/'Tools/Integration/GermanNPCOrderedGripV4'))
from arm_fit import encode
BASE=STORE/'Evidence/GermanNPCAlliedGripV13';OUT=BASE/'probe_v2'
FIRST=BASE/'probe_v1/result.json'
CFG=STORE/'Evidence/LeftSupportV20/reuse_pose_v2/binding.json'
AUDIT=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
GA=STORE/'Evidence/WeaponAnimationReuseV1/audit_v1/result.json'
IMAGE=STORE/'Evidence/WeaponTexturedViewsV17/presentation_v2/three_views.jpg'
assert not OUT.exists();OUT.mkdir(parents=True)
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in (FIRST,CFG,AUDIT,GA,IMAGE,Path(__file__))],
   'formal_selected':False,'source_modified':False,'native_tested':False,'donor_reference':'User-linked Allied first-person accepted grasp'}
try:
    old=read(FIRST);cfg=read(CFG);audit=read(AUDIT)['models']['owner'];g=read(GA)['models']['german']
    assert sha(CFG)=='04f4588cc6922a907f3aaa2bc60d41dec985240e96d3c6c31f1d32dfde3bc7a7'
    locals={n:v['q'] for n,v in cfg['fingers_local'].items()};assert len(locals)==30
    checks={}
    for n in ['hand_r','hand_l',*locals]:
        assert audit['parents'][n]==old['parents'][n]
        a=audit['ref_local'][n];b=g['ref_local'][n]
        checks[n]={'translation_cm':float(np.linalg.norm(np.array(a['translation'])-b['translation'])),
          'rotation_deg':tm.angle(a['rotation'],b['rotation']),'scale':float(np.max(abs(np.array(a['scale'])-b['scale'])))}
        assert checks[n]['translation_cm']<.001 and checks[n]['rotation_deg']<.001
    r.update({k:old[k] for k in ('bone_names','parents','baseline_bones','baseline_gun_world','mesh_world')})
    r.update(status='approved_allied_digit_locals_and_reference_frames_verified',approved_digit_local_rotations=locals,
      reference_checks=checks,allied_bones={'hand_r':{'t':[0,0,0],'q':[0,0,0,1],'s':[1,1,1]},'hand_l':cfg['support_hand_relative_to_right']},
      allied_gun_world=cfg['gun_hand_relative'],not_transferred_fp_pinky_scale=cfg['fingers_local']['pinky_02_r']['s'],
      source_selection_correction='Conventional NPC V16 differs from explicitly linked FP hand; preserve first comparison unselected')
except Exception:r['status']='probe_failed_preserved';r['errors'].append(traceback.format_exc())
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(r['status'],r['errors'])
