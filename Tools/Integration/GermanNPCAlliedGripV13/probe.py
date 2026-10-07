"""Read-only accepted Allied grasp / German frame compatibility audit."""
import sys, traceback
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT, STORE, GLB, read, write, row, sha, guards, tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat
sys.path.insert(0,str(ROOT/'Tools/Integration/GermanNPCOrderedGripV4'))
from arm_fit import encode

BASE=STORE/'Evidence/GermanNPCAlliedGripV13'; OUT=BASE/'probe_v1'
ALLIED=STORE/'Evidence/AlliedNPCGripV2/fp_wrist_native_v14/result.json'
CFG=STORE/'Evidence/AlliedNPCUEV15/preflight_v16/binding.json'
PREV=STORE/'Evidence/GermanNPCLowerGripV11/source_frame_v4/result.json'
AUDIT=STORE/'Evidence/WeaponAnimationReuseV1/audit_v1/result.json'
AD=STORE/'Evidence/AlliedNPCGripV2/pivot_raise_measure_v7/geometry.npz'
AP=AD.parent/'result.json'
GD=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
assert not OUT.exists(); OUT.mkdir(parents=True)
r={'status':'starting','errors':[],'guards_before':guards(),
   'inputs':[row(p) for p in (ALLIED,CFG,PREV,AUDIT,AD,AP,GD,TOPO,GLB,Path(__file__))],
   'formal_selected':False,'source_modified':False,'native_tested':False}
try:
    a=read(ALLIED); cfg=read(CFG); g=read(PREV); audit=read(AUDIT)
    assert not a['errors'] and cfg['accepted_holding']
    assert cfg['source_record_sha256']==sha(ALLIED)
    parents=g['parents']; ap=read(AP)['parents']
    ab={n:mat(v) for n,v in a['after']['bones'].items()}
    gb={n:mat(v) for n,v in g['after_bones'].items()}
    digits=[f'{d}_{i:02}_{s}' for s in ('r','l') for d in ('thumb','index','middle','ring','pinky') for i in (1,2,3)]
    locals={}; checks={}
    for n in ['hand_r','hand_l',*digits]:
        assert ap[n]==parents[n],n
        ar=audit['models']['allied']['ref_local'][n]; gr=audit['models']['german']['ref_local'][n]
        checks[n]={'translation_cm':float(np.linalg.norm(np.array(ar['translation'])-gr['translation'])),
          'rotation_deg':tm.angle(ar['rotation'],gr['rotation']),
          'scale':float(np.max(abs(np.array(ar['scale'])-gr['scale'])))}
        assert checks[n]['translation_cm']<.001 and checks[n]['rotation_deg']<.001
        if n in digits: locals[n]=encode(np.linalg.inv(ab[ap[n]])@ab[n])['q']
    config_errors={x['bone']:tm.angle(x['accepted_q'],encode(np.linalg.inv(ab[ap[x['bone']]])@ab[x['bone']])['q']) for x in cfg['rules']}
    assert max(config_errors.values())<.001
    def stats(p,key):
        d=np.load(p); pts=d[key];return {'min':pts.min(0).tolist(),'max':pts.max(0).tolist(),'extent':np.ptp(pts,axis=0).tolist()}
    r.update(status='approved_allied_digit_locals_and_reference_frames_verified',bone_names=g['bone_names'],parents=parents,
      approved_digit_local_rotations=locals,reference_checks=checks,accepted_config_errors_deg=config_errors,
      baseline_bones=g['after_bones'],baseline_gun_world=g['after_gun_world'],mesh_world=g['mesh_world'],
      allied_bones=a['after']['bones'],allied_gun_world=a['after']['gun_world'],
      allied_gun_geometry=stats(AD,'gun_local_cm'),german_gun_geometry=stats(GD,'gun_local_cm'))
except Exception:r['status']='probe_failed_preserved';r['errors'].append(traceback.format_exc())
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','allied_gun_geometry','german_gun_geometry','accepted_config_errors_deg')})
