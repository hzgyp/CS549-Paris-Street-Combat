"""ONE horizontal shoulder-seated assembly, both source-length arms; no digit fitting."""
import sys,math,traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs

PREVIOUS=BASE/'tip_curl_native_v12/result.json'
OFFLINE=BASE/'tip_curl_v12/result.json'
MEASURE=BASE/'pivot_raise_measure_v7/result.json';GEOMETRY=MEASURE.parent/'geometry.npz'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
OUT=BASE/'firing_assembly_v13';assert not OUT.exists();OUT.mkdir(parents=True)
paths=(PREVIOUS,OFFLINE,MEASURE,GEOMETRY,TOPO,Path(__file__))
r={'errors':[],'status':'starting','guards_before':guards(),
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
   'comparison_only':True,'source_model_weights_actions_modified':False,
   'native_authored':False,'formal_selected':False,'contact_or_gameplay_accepted':False}

def encode(m):
    t,q,s=Matrix(m).decompose()
    return {'t':list(t),'q':[q.x,q.y,q.z,q.w],'s':list(s)}

def swing(a,b):return np.array(Vector(a).rotation_difference(Vector(b)).to_matrix(),float)

def arm_targets(bones,targets,parents):
    explicit={};checks={}
    for side,target in targets.items():
        u,l,h=['upperarm_'+side,'lowerarm_'+side,'hand_'+side]
        shoulder,elbow,wrist=[bones[n][:3,3] for n in (u,l,h)]
        goal=target[:3,3];la=np.linalg.norm(elbow-shoulder);lb=np.linalg.norm(wrist-elbow)
        reach=np.linalg.norm(goal-shoulder)
        assert abs(la-lb)+1e-5<reach<la+lb-1e-5,(side,'source-length target unreachable',reach,la,lb)
        line=(goal-shoulder)/reach;bend=elbow-shoulder-line*np.dot(elbow-shoulder,line)
        assert np.linalg.norm(bend)>1e-6
        bend/=np.linalg.norm(bend);along=(la*la-lb*lb+reach*reach)/(2*reach)
        new_elbow=shoulder+along*line+math.sqrt(max(0,la*la-along*along))*bend
        explicit[h]=target.copy()
        for n,p,old,new in ((u,shoulder,elbow-shoulder,new_elbow-shoulder),(l,new_elbow,wrist-elbow,goal-new_elbow)):
            value=bones[n].copy();value[:3,:3]=swing(old,new)@value[:3,:3];value[:3,3]=p;explicit[n]=value
        checks[side]={'upper_cm':float(la),'forearm_cm':float(lb),'target_reach_cm':float(reach),
            'max_reach_cm':float(la+lb),'wrist_motion_cm':float(np.linalg.norm(goal-wrist)),
            'source_elbow_cm':elbow.tolist(),'target_elbow_cm':new_elbow.tolist()}
    result={}
    def get(n):
        if n not in result:
            p=parents.get(n)
            if n in explicit:result[n]=explicit[n]
            elif p in bones:result[n]=get(p)@np.linalg.inv(bones[p])@bones[n]
            else:result[n]=bones[n].copy()
        return result[n]
    for n in bones:get(n)
    return result,checks

try:
    prev,old,m,topo=map(read,(PREVIOUS,OFFLINE,MEASURE,TOPO))
    for source in (prev,old):
        assert not source['errors'] and source['inputs_unchanged'] and source['guards_after']==611
        assert all(sha(ROOT/p)==h for p,h in source['input_hashes'].items())
    d=np.load(GEOMETRY);names=m['bone_names'];parents=m['parents'];weights=d['weights']
    rest=d['rest_native_cm'];ref=d['reference_matrices'];tri=d['skin_triangles']
    bones={n:mat(t) for n,t in prev['after']['bones'].items()};gb=mat(prev['after']['gun_world'])
    def skin(pose):
        result=np.zeros_like(rest)
        for j,n in enumerate(names):result+=weights[:,j,None]*transform(rest,pose[n]@np.linalg.inv(ref[j]))
        return result/weights.sum(1)[:,None]
    before=skin(bones);origin=bones['upperarm_r'][:3,3].copy()
    gp=d['gun_local_cm'];gt=d['gun_triangles'];parts={q['id']:set(q['triangle_ids']) for q in topo['components']}
    forward=gb[:3,:3]@np.array([0.,1.,0.]);forward/=np.linalg.norm(forward)
    heading=forward.copy();heading[2]=0;heading/=np.linalg.norm(heading)
    rotation=swing(forward,heading)
    angle=math.degrees(math.acos(np.clip((np.trace(rotation)-1)/2,-1,1)));assert angle<40
    elevation=math.degrees(math.asin(forward[2]));assert elevation>20
    stock_ids=np.unique(gt[sorted(parts[0])]);rear_min=gp[stock_ids,1].min()
    butt_ids=stock_ids[gp[stock_ids,1]<=rear_min+.30];assert len(butt_ids)>3
    butt_local=gp[butt_ids].mean(0);butt_world=transform(butt_local[None],gb)[0]
    shoulder_ids=[names.index('upperarm_r'),names.index('clavicle_r'),names.index('upperarm_twist_01_r')]
    shoulder_weight=weights[:,shoulder_ids].sum(1)
    shoulder_faces=tri[(np.max(shoulder_weight[tri],axis=1)>.3)&(np.linalg.norm(before[tri].mean(1)-origin,axis=1)<12)]
    assert len(shoulder_faces)>20
    tree=BVHTree.FromPolygons([Vector(p) for p in before-origin],shoulder_faces.tolist(),all_triangles=True)
    hit,normal,face,distance=tree.ray_cast(Vector(heading*25),Vector(-heading),50)
    assert hit is not None,'No actual shoulder clothing hit; do not invent contact'
    shoulder_surface=np.array(hit,float)+origin
    butt_target=shoulder_surface+heading*.15
    change=np.eye(4);change[:3,:3]=rotation;change[:3,3]=butt_target-rotation@butt_world
    ga=change@gb;candidate,reach=arm_targets(bones,{s:change@bones['hand_'+s] for s in ('r','l')},parents)
    after=skin(candidate);expected=transform(before,change)
    allowed=set()
    for n in names:
        p=n
        while p in parents:
            if p in ('upperarm_l','upperarm_r'):allowed.add(n);break
            p=parents[p]
    digits=[n for n in names if n.startswith(('index_','thumb_','middle_','ring_','pinky_')) and n.endswith(('_l','_r'))]
    protected=max(float(np.abs(candidate[n]-bones[n]).max()) for n in names if n not in allowed)
    digit_error=max(float(np.abs(np.linalg.inv(candidate[parents[n]])@candidate[n]-np.linalg.inv(bones[parents[n]])@bones[n]).max()) for n in digits)
    relation={s:float(np.abs(np.linalg.inv(candidate['hand_'+s])@ga-np.linalg.inv(bones['hand_'+s])@gb).max()) for s in ('r','l')}
    length_error=max(abs(np.linalg.norm(candidate[b][:3,3]-candidate[a][:3,3])-np.linalg.norm(bones[b][:3,3]-bones[a][:3,3]))
        for a,b in (('upperarm_r','lowerarm_r'),('lowerarm_r','hand_r'),('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l')))
    affected=weights[:,[names.index(n) for n in allowed]].sum(1)>0
    tracking={};mixed={}
    for s in ('r','l'):
        did=[names.index(n) for n in digits if n.endswith('_'+s)]
        hand_ids=did+[names.index('hand_'+s)]
        digit_mask=weights[:,did].sum(1)>.1
        hand_mask=weights[:,hand_ids].sum(1)>0
        tracking[s]=float(np.linalg.norm(after[digit_mask]-expected[digit_mask],axis=1).max())
        mixed[s]=float(np.linalg.norm(after[hand_mask]-expected[hand_mask],axis=1).max())
    pad_ids=old['pad_skin_vertices'];pad=after[pad_ids].mean(0)
    pad_tracking=float(np.linalg.norm(pad-transform(before[pad_ids].mean(0)[None],change)[0]))
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ab=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);aa=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1)
    severe=int(np.sum((aa>3*np.maximum(ab,1e-8))&(aa-ab>2)))
    def contacts(body,gunmat):
        gun=transform(gp,gunmat)-origin;result={}
        for s in ('r','l'):
            for digit in ('index','thumb','middle','ring','pinky'):
                ids=[names.index(n) for n in digits if n.startswith(digit+'_') and n.endswith('_'+s)]
                mask=weights[:,ids].sum(1)>.1;faces=tri[np.all(mask[tri],axis=1)]
                pairs=intersection_pairs(body-origin,faces,gun,gt)
                result[digit+'_'+s]={part:len({a for a,b in pairs if b in parts[i]}) for part,i in (('stock',0),('guard',4),('blade',5))}
        blade=BVHTree.FromPolygons([Vector(p) for p in gun],gt[sorted(parts[5])].tolist(),all_triangles=True)
        result['pad_blade_cm']=float(blade.find_nearest(Vector(body[pad_ids].mean(0)-origin))[3]);return result
    baseline=contacts(before,gb);final=contacts(after,ga)
    new_contacts={n:{p:final[n][p]-baseline[n][p] for p in baseline[n]} for n in baseline if isinstance(baseline[n],dict)}
    assert all(delta<=0 for row in new_contacts.values() for delta in row.values()),new_contacts
    muzzle_local=gp[np.argmax(gp[:,1])];muzzle_before=transform(muzzle_local[None],gb)[0];muzzle_after=transform(muzzle_local[None],ga)[0]
    preservation={'protected_bone_matrix_error':protected,'digit_local_matrix_error':digit_error,
        'hand_relative_gun_matrix_errors':relation,'digit_skin_rigid_tracking_cm':tracking,
        'all_hand_influenced_skin_rigid_residual_cm':mixed,'actual_index_pad_rigid_tracking_cm':pad_tracking,
        'arm_length_error_cm':float(length_error),'unaffected_skin_cm':float(np.linalg.norm(after[~affected]-before[~affected],axis=1).max()),
        'new_severe_edges':severe,'max_extra_edge_cm':float((aa-ab).max())}
    r.update(before_bones=prev['after']['bones'],after_bones={n:encode(candidate[n]) if n in allowed else prev['after']['bones'][n] for n in names},
        before_gun_world=prev['after']['gun_world'],after_gun_world=encode(ga),allowed_bones=sorted(allowed),parents=parents,bone_names=names,
        mesh_world=m['mesh_world'],assembly_transform=change.tolist(),angle_down_deg=angle,barrel_elevation_before_deg=elevation,
        barrel_elevation_after_deg=math.degrees(math.asin((ga[:3,:3]@np.array([0.,1.,0.]))[2]/np.linalg.norm(ga[:3,:3]@np.array([0.,1.,0.])))),
        shoulder_surface_world_cm=shoulder_surface.tolist(),butt_target_world_cm=butt_target.tolist(),butt_source_vertices=butt_ids.tolist(),
        butt_local_cm=butt_local.tolist(),shoulder_surface_face=shoulder_faces[face].tolist(),shoulder_outward_clearance_cm=.15,
        muzzle_before_cm=muzzle_before.tolist(),muzzle_after_cm=muzzle_after.tolist(),muzzle_drop_cm=float(muzzle_before[2]-muzzle_after[2]),
        preservation=preservation,reach=reach,baseline_contact=baseline,final_contact=final,new_contact_face_deltas=new_contacts,
        pad_world_cm=pad.tolist(),pad_skin_vertices=pad_ids,contact_gate_passed=False)
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,skin_triangles=tri,
        before_gun_world_cm=transform(gp,gb),after_gun_world_cm=transform(gp,ga),gun_triangles=gt)
    assert protected<1e-5 and digit_error<1e-5 and max(relation.values())<.001 and length_error<.01
    assert max(tracking.values())<.05 and pad_tracking<.02 and preservation['unaffected_skin_cm']<.001 and severe==0,preservation
    r['comparison_gate_passed']=True;r['status']='firing_assembly_v13_static_comparison_ready'
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items());r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','angle_down_deg','barrel_elevation_before_deg','barrel_elevation_after_deg','muzzle_drop_cm','reach','preservation','baseline_contact','final_contact')},flush=True)
