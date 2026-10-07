"""Read-only final preservation/pose/source-unit audit; no model rerun."""
import ast,sys,json,traceback
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards,tm
BASE=STORE/'Evidence/GermanNPCIndexGripV12';OUT=BASE/'final_check_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
r={'status':'starting','errors':[],'formal_selected':False,'native_tested':False,'contact_accepted':False}
write(OUT/'result.json',r)
try:
    entries={};receipts=list(BASE.glob('*/result.json'))
    receipts=[p for p in receipts if p.parent!=OUT]
    for p in receipts:
        x=read(p);entries[p.relative_to(ROOT).as_posix()]=row(p)
        for e in x.get('inputs',[])+x.get('images',[]):
            assert sha(ROOT/e['path'])==e['sha256'],e['path'];entries[e['path']]=e
    fit=read(BASE/'distal_existing_grasp_v4b/result.json');assert fit['status']=='failed_preserved'
    before,after=fit['before_bones'],fit['after_bones'];names=fit['bone_names'];parents=fit['parents']
    protected=fit['protected_bones'];assert all(before[n]==after[n] for n in protected)
    assert before['index_01_r']==after['index_01_r'] and before['index_02_r']==after['index_02_r']
    assert fit['before_gun_world']['q']==fit['after_gun_world']['q'] and fit['before_gun_world']['s']==fit['after_gun_world']['s']
    q0=tm.local_q(before['index_02_r'],before['index_03_r']);q1=tm.local_q(after['index_02_r'],after['index_03_r'])
    turn=tm.angle(q0,q1);assert abs(turn-10.500156)<.01
    def chain(b):
        a=np.array(b['index_02_r']['t'])-b['index_01_r']['t'];c=np.array(b['index_03_r']['t'])-b['index_02_r']['t']
        return float(np.degrees(np.arccos(np.clip(a@c/np.linalg.norm(a)/np.linalg.norm(c),-1,1))))
    d=np.load(STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz');g=np.load(BASE/'distal_existing_grasp_v4b/diagnostic_geometry.npz');w=d['weights']
    move=np.linalg.norm(g['skin']-g['before_skin'],axis=1)
    rm=w[:,[j for j,n in enumerate(names) if n.endswith('_r') and n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_'))]].sum(1)>0
    im=w[:,names.index('index_03_r')]>0;lm=w[:,[j for j,n in enumerate(names) if n.endswith('_l') and n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))]].sum(1)>0
    r.update(actual_index03_local_rotation_deg=turn,actual_index01_02_03_joint_head_turn_before_deg=chain(before),actual_index01_02_03_joint_head_turn_after_deg=chain(after),
      inherited_raw_chain_turn_field_not_current_pose=fit['index_chain_turn_after_deg'],
      metadata_warning='Raw v4b chain-turn field inherited from full-source v2; not a current-pose measurement. Distal orientation above is verified.',
      protected_bone_count=len(protected),protected_bone_serialized_exact=True,
      thumb_lower_three_local_bones_exact=True,gun_rotation_scale_exact=True,
      index03_other_right_skin_shared_vertex_count=int(np.sum(im&rm&(w[:,names.index('index_03_r')]<.999))),
      right_skin_mixed_left_influence=[{'vertex_id':int(i),'motion_cm':float(move[i])} for i in np.flatnonzero(lm&rm)],
      true_zero_authorized_influence_motion_cm=float(move[~(im|lm)].max()),
      index_local_translation_scale_checks=fit['index_local_translation_scale_checks'],
      guards_exact=guards(),inputs=list(entries.values()),script_parses=[])
    for p in Path(__file__).parent.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'));r['script_parses'].append(row(p))
    assert r['true_zero_authorized_influence_motion_cm']<.0001 and r['guards_exact']==618
    assert len(read(BASE/'final_views_v1/result.json')['images'])==12
    r['status']='preservation_and_actual_distal_pose_verified_contact_still_failed'
except Exception:r['errors'].append(traceback.format_exc());r['status']='verification_failed_preserved'
finally:
    write(OUT/'result.json',r);print(json.dumps({k:r.get(k) for k in ('status','errors','actual_index03_local_rotation_deg','actual_index01_02_03_joint_head_turn_after_deg','protected_bone_count','guards_exact','right_skin_mixed_left_influence')},indent=2))
