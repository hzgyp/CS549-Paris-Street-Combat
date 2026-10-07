"""ONE actual-palm pivot goal for the intact support grasp; early scope screen."""
import hashlib,json,sys,traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerPivotV12'))
from pivot_common import *
SOURCE=STORE/'Evidence/WeaponPinkyLengthV18/distal_v1'
OUT=STORE/'Evidence/LeftSupportV20/pivot_goal_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
r={'errors':[],'native_authored':False,'candidate_authored':False,'scope':__doc__}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
try:
    r['guards_before']=guarded_files();assert not r['guards_before']['mismatches']
    proof=json.loads((SOURCE/'result.json').read_text())
    bones={n:np.array(v) for n,v in proof['candidate_component_bones'].items()}
    gun0=np.array(proof['baseline_gun_component_matrix'])
    change=np.array(json.loads((STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/result.json').read_text())['rigid_change_gun_local'])
    d=load();points=evaluate(d,bones,gun0);gp=transform(d['gp'],change)
    stockids=np.array(next(c['triangle_ids'] for c in d['topo']['components'] if c['id']==0),int)
    tree=BVHTree.FromPolygons([Vector(v) for v in gp],d['gt'][stockids][:,::-1].tolist(),all_triangles=True)
    # Contiguous pure-palm patch already near the wood; exclude digits.
    audit=json.loads((STORE/'Evidence/LeftSupportV20/audit_v1/result.json').read_text())
    patches=[x for x in audit['pure_palm_surface_samples'] if 0<=x['signed_gap_cm'] and x['gap_cm']<.15 and x['opposition']<-.5]
    assert len(patches)>=3,'No existing support-palm contact patch'
    pivot=np.mean([x['palm_point_cm'] for x in patches],axis=0)
    thumb=np.array([sum(w.get(n,0) for n in ('thumb_02_l','thumb_03_l'))>.7 for w in d['weights']])
    ids=np.flatnonzero(np.all(thumb[d['tri']],axis=1))
    hn,areas=normals(points,d['tri']);candidates=[]
    for fid in ids:
        center=points[d['tri'][fid]].mean(0)
        q,n,j,gap=tree.find_nearest(Vector(center));q,n=np.array(q),np.array(n)
        opposition=float(hn[fid]@n);signed=float((center-q)@n)
        if opposition<-.3 and signed>0:
            candidates.append({'face':int(fid),'point':center,'q':q,'normal':n,'gap':float(gap),'area':float(areas[fid])})
    assert len(candidates)>=3,'Thumb opposing wood-side pad not proved'
    candidates.sort(key=lambda x:x['gap'])
    selected=candidates[:max(3,len(candidates)//3)]
    pad=np.average([x['point'] for x in selected],axis=0,weights=[x['area'] for x in selected])
    q,n,j,gap=tree.find_nearest(Vector(pad));q,n=np.array(q),np.array(n)
    # Closest compatible angular target preserves pivot-to-pad radius: rotate,
    # not rescale the hand. Residual radial difference is explicitly reported.
    goal=q+n*.08
    a,b=pad-pivot,goal-pivot
    angle=float(np.degrees(np.arccos(np.clip(a@b/(np.linalg.norm(a)*np.linalg.norm(b)),-1,1))))
    rotation=swing(a,b);rigid=np.eye(4);rigid[:3,:3]=rotation;rigid[:3,3]=pivot-rotation@pivot
    hand=np.linalg.inv(gun0)@bones['hand_l'];target=gun0@rigid@hand
    shift=float(np.linalg.norm(target[:3,3]-bones['hand_l'][:3,3]))
    r.update(pivot_cm=pivot.tolist(),palm_patch_triangles=[x['palm_triangle'] for x in patches],
             thumb_pad_cm=pad.tolist(),thumb_pad_triangles=[x['face'] for x in selected],
             wood_point_cm=q.tolist(),wood_normal=n.tolist(),original_gap_cm=float(gap),
             derived_angle_degrees=angle,wrist_shift_cm=shift,
             radial_residual_cm=float(abs(np.linalg.norm(a)-np.linalg.norm(b))),
             rigid_left_in_baseline_gun_frame=rigid.tolist(),target_hand_component_matrix=target.tolist())
    assert angle<15 and shift<2,'Derived intact-hand target outside declared scope; no clipping/capping/scan'
    candidate=left_chain(d,bones,target);after=evaluate(d,candidate,gun0)
    mask=d['masks']['l'];faces=d['tri'][np.all(mask[d['tri']],axis=1)]
    beforepairs=intersection_pairs(points,faces,gp,d['gt'])
    afterpairs=intersection_pairs(after,faces,gp,d['gt'])
    beforefaces={a for a,b in beforepairs};afterfaces={a for a,b in afterpairs}
    pad_after=after[d['tri'][[x['face'] for x in selected]]].mean(1)
    nearest=[float(tree.find_nearest(Vector(v))[3]) for v in pad_after]
    r['checks']={'left_gun_faces_before':len(beforefaces),'left_gun_faces_after':len(afterfaces),
                 'new_crossing_faces':len(afterfaces-beforefaces),
                 'thumb_mean_gap_after_cm':float(np.mean(nearest)),
                 'right_skin_delta_cm':float(np.max(np.linalg.norm(after[d['masks']['r']]-points[d['masks']['r']],axis=1))),
                 'finger_local_delta':max(float(np.max(abs(np.linalg.inv(candidate[d['model']['parents'][n]])@candidate[n]-np.linalg.inv(bones[d['model']['parents'][n]])@bones[n]))) for n in bones if n.startswith(('thumb_','index_','middle_','ring_','pinky_'))),
                 'arm_length_delta_cm':max(abs(float(np.linalg.norm(candidate[a][:3,3]-candidate[b][:3,3])-np.linalg.norm(bones[a][:3,3]-bones[b][:3,3]))) for a,b in [('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l')]),
                 **edge_check(d,points,after)}
    ck=r['checks']
    r['early_gate_passed']=bool(ck['new_crossing_faces']==0 and ck['right_skin_delta_cm']<.0001 and ck['finger_local_delta']<1e-10 and ck['arm_length_delta_cm']<.01 and not ck['new_severe_edges'] and ck['thumb_mean_gap_after_cm']<gap)
    r['candidate_component_bones']={n:v.tolist() for n,v in candidate.items()}
    r['status']='intact_target_screen_passed_requires_views' if r['early_gate_passed'] else 'stopped_intact_target_contact_gate'
except Exception:r['errors'].append(traceback.format_exc());r['status']='stopped'
finally:
    r['guards_after']=guarded_files();write()
    print(json.dumps({k:r.get(k) for k in ['status','errors','derived_angle_degrees','wrist_shift_cm','original_gap_cm','radial_residual_cm','checks','early_gate_passed','guards_after']}),flush=True)
    if r['errors'] or r['guards_after']['mismatches']:raise SystemExit(1)
