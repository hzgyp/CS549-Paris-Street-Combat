"""ONE shoulder-height-constrained right elbow, approved FP directional analogue."""
import sys,math,traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs

PREVIOUS=BASE/'firing_assembly_native_v13/result.json'
OLD=BASE/'firing_assembly_v13/result.json'
MEASURE=BASE/'pivot_raise_measure_v7/result.json';GEOMETRY=MEASURE.parent/'geometry.npz'
PROBE=STORE/'Evidence/FPUpperBodyV19/holding_probe_v2/result.json'
SELECTION=STORE/'Evidence/FPUpperBodyV19/holding_selection_v1/selection.json'
CONFIG=STORE/'Evidence/LeftSupportV20/reuse_pose_v2/binding.json'
FORMAL=STORE/'Evidence/FirstPersonFormalV21/fresh_v2/result.json'
CPP=ROOT/'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18/Source/ParisGripBindingV18/Private/ParisFPUpperBodyV19Actor.cpp'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
OUT=BASE/'fp_wrist_v14';assert not OUT.exists();OUT.mkdir(parents=True)
paths=(PREVIOUS,OLD,MEASURE,GEOMETRY,PROBE,SELECTION,CONFIG,FORMAL,CPP,TOPO,Path(__file__))
r={'errors':[],'status':'starting','guards_before':guards(),
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
   'comparison_only':True,'source_model_weights_actions_modified':False,
   'native_authored':False,'formal_selected':False,'contact_or_gameplay_accepted':False}
def encode(m):
    t,q,s=Matrix(m).decompose();return {'t':list(t),'q':[q.x,q.y,q.z,q.w],'s':list(s)}
def swing(a,b):return np.array(Vector(a).rotation_difference(Vector(b)).to_matrix(),float)
def angle(a,b):return math.degrees(math.acos(np.clip(np.dot(a,b)/np.linalg.norm(a)/np.linalg.norm(b),-1,1)))
def unit(v):return v/np.linalg.norm(v)
try:
    prev,old,m,probe,selection,config,formal,topo=map(read,(PREVIOUS,OLD,MEASURE,PROBE,SELECTION,CONFIG,FORMAL,TOPO))
    for item in (prev,old):
        assert not item['errors'] and item['inputs_unchanged'] and item['guards_after']==611
        assert all(sha(ROOT/p)==h for p,h in item['input_hashes'].items())
    assert not probe['errors'] and probe['source_inputs_unchanged']
    assert probe['input_inventory_before']==probe['input_inventory_after']
    for row in probe['input_inventory_after']:
        p=ROOT/row['path'];assert p.stat().st_size==row['size_bytes'] and sha(p)==row['sha256']
    assert selection['compatible_existing_clip'] and selection['source_proof']=='holding_probe_v2'
    assert sha(CONFIG)=='04f4588cc6922a907f3aaa2bc60d41dec985240e96d3c6c31f1d32dfde3bc7a7'
    assert not formal['errors']
    fp=next(p for p in probe['samples'] if p['clip']=='W2_Stand_Aim_Idle_IP' and p['fraction']==0.)['component']
    d=np.load(GEOMETRY);names=m['bone_names'];parents=m['parents'];weights=d['weights']
    rest=d['rest_native_cm'];ref=d['reference_matrices'];tri=d['skin_triangles']
    bones={n:mat(t) for n,t in prev['after']['bones'].items()};gun=mat(prev['after']['gun_world'])
    def skin(pose):
        value=np.zeros_like(rest)
        for j,n in enumerate(names):value+=weights[:,j,None]*transform(rest,pose[n]@np.linalg.inv(ref[j]))
        return value/weights.sum(1)[:,None]
    before=skin(bones)
    shoulder,elbow,wrist=[bones[n][:3,3] for n in ('upperarm_r','lowerarm_r','hand_r')]
    fpe,fpw=[np.array(fp[n]['t']) for n in ('lowerarm_r','hand_r')]
    fpforearm=unit(fpw-fpe);fp_hand=mat(fp['hand_r'])[:3,:3]
    reference_in_hand=unit(np.linalg.inv(fp_hand)@fpforearm)
    desired=unit(bones['hand_r'][:3,:3]@reference_in_hand)
    hand_axis=unit(bones['hand_r'][:3,:3]@np.array([-1.,0.,0.]))
    la,lb=np.linalg.norm(elbow-shoulder),np.linalg.norm(wrist-elbow)
    reach=np.linalg.norm(wrist-shoulder);line=(wrist-shoulder)/reach
    assert abs(la-lb)<reach<la+lb
    along=(la*la-lb*lb+reach*reach)/(2*reach);center=shoulder+along*line
    radius=math.sqrt(la*la-along*along)
    ideal=wrist-lb*desired;direction=unit(ideal-center-line*np.dot(ideal-center,line))
    unconstrained=center+radius*direction
    cap=shoulder[2];new_elbow=unconstrained.copy()
    constrained=bool(new_elbow[2]>cap)
    if constrained:
        vertical=np.array([0.,0.,1.]);z=vertical-line*np.dot(vertical,line);zlen=np.linalg.norm(z);z/=zlen
        perpendicular=np.cross(line,z);k=(cap-center[2])/(radius*zlen);assert abs(k)<1
        options=[k*z+sign*math.sqrt(1-k*k)*perpendicular for sign in (1,-1)]
        new_elbow=center+radius*max(options,key=lambda v:np.dot(v,direction))
    assert new_elbow[2]<=cap+1e-6
    explicit={'hand_r':bones['hand_r'].copy()}
    for n,p,oldv,newv in (('upperarm_r',shoulder,elbow-shoulder,new_elbow-shoulder),
                         ('lowerarm_r',new_elbow,wrist-elbow,wrist-new_elbow)):
        value=bones[n].copy();value[:3,:3]=swing(oldv,newv)@value[:3,:3];value[:3,3]=p;explicit[n]=value
    allowed={'upperarm_r','lowerarm_r','upperarm_twist_01_r','lowerarm_twist_01_r'}
    candidate={}
    def get(n):
        if n not in candidate:
            if n in explicit:candidate[n]=explicit[n]
            elif n in allowed:
                p=parents[n];candidate[n]=get(p)@np.linalg.inv(bones[p])@bones[n]
            else:candidate[n]=bones[n].copy()
        return candidate[n]
    for n in names:get(n)
    after=skin(candidate);digits=[n for n in names if n.startswith(('index_','thumb_','middle_','ring_','pinky_'))]
    protected=max(float(np.abs(candidate[n]-bones[n]).max()) for n in names if n not in allowed)
    local_error=max(float(np.abs(np.linalg.inv(candidate[parents[n]])@candidate[n]-np.linalg.inv(bones[parents[n]])@bones[n]).max()) for n in digits)
    length_error=max(abs(np.linalg.norm(candidate[b][:3,3]-candidate[a][:3,3])-np.linalg.norm(bones[b][:3,3]-bones[a][:3,3]))
        for a,b in (('upperarm_r','lowerarm_r'),('lowerarm_r','hand_r')))
    affected=weights[:,[names.index(n) for n in allowed]].sum(1)>0
    digit_ids=[names.index(n) for n in digits];digit_mask=weights[:,digit_ids].sum(1)>.1
    digit_skin=float(np.linalg.norm(after[digit_mask]-before[digit_mask],axis=1).max())
    handweight=weights[:,[names.index(n) for n in digits if n.endswith('_r')]+[names.index('hand_r')]].sum(1)
    mixed={str(limit):float(np.linalg.norm(after[handweight>limit]-before[handweight>limit],axis=1).max()) for limit in (0,.5,.99)}
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ab=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);aa=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1)
    severe=int(np.sum((aa>3*np.maximum(ab,1e-8))&(aa-ab>2)))
    origin=shoulder.copy();gp=d['gun_local_cm'];gt=d['gun_triangles'];parts={q['id']:set(q['triangle_ids']) for q in topo['components']}
    def contacts(body):
        result={};g=transform(gp,gun)-origin
        for s in ('r','l'):
            for digit in ('index','thumb','middle','ring','pinky'):
                ids=[names.index(n) for n in digits if n.startswith(digit+'_') and n.endswith('_'+s)]
                mask=weights[:,ids].sum(1)>.1;faces=tri[np.all(mask[tri],axis=1)]
                pairs=intersection_pairs(body-origin,faces,g,gt)
                result[digit+'_'+s]={part:len({a for a,b in pairs if b in parts[i]}) for part,i in (('stock',0),('guard',4),('blade',5))}
        return result
    baseline,final=contacts(before),contacts(after)
    pad_ids=old['pad_skin_vertices'];pad=after[pad_ids].mean(0)
    preservation={'protected_bone_matrix_error':protected,'digit_local_matrix_error':local_error,
        'hand_relative_gun_matrix_errors':{s:0. for s in ('r','l')},'digit_skin_cm':digit_skin,
        'right_cuff_positive_hand_weight_residual_cm':mixed,'arm_length_error_cm':float(length_error),
        'unaffected_skin_cm':float(np.linalg.norm(after[~affected]-before[~affected],axis=1).max()),
        'new_severe_edges':severe,'max_extra_edge_cm':float((aa-ab).max())}
    diagnosis={'reference_clip':selection['clip_path'],'reference_fraction':0.,'reference_forearm_in_hand':reference_in_hand.tolist(),
        'fp_forearm_hand_axis_deg':angle(fpforearm,fp_hand@np.array([-1.,0.,0.])),
        'npc_before_forearm_hand_axis_deg':angle(wrist-elbow,hand_axis),'npc_after_forearm_hand_axis_deg':angle(wrist-new_elbow,hand_axis),
        'reference_direction_error_before_deg':angle(wrist-elbow,desired),'reference_direction_error_after_deg':angle(wrist-new_elbow,desired),
        'elbow_before_cm':elbow.tolist(),'elbow_after_cm':new_elbow.tolist(),'elbow_delta_cm':(new_elbow-elbow).tolist(),
        'unconstrained_elbow_rejected_cm':unconstrained.tolist() if constrained else None,'elbow_height_cap_cm':float(cap),
        'original_upper_length_cm':float(la),'original_forearm_length_cm':float(lb),'exact_fp_angle_reproduced':False}
    r.update(before_bones=prev['after']['bones'],after_bones={n:encode(candidate[n]) if n in allowed else prev['after']['bones'][n] for n in names},
        before_gun_world=prev['after']['gun_world'],after_gun_world=prev['after']['gun_world'],allowed_bones=sorted(allowed),
        parents=parents,bone_names=names,mesh_world=m['mesh_world'],preservation=preservation,diagnosis=diagnosis,
        baseline_contact=baseline,final_contact=final,pad_world_cm=pad.tolist(),pad_skin_vertices=pad_ids,
        butt_local_cm=old['butt_local_cm'],butt_target_world_cm=old['butt_target_world_cm'],muzzle_after_cm=old['muzzle_after_cm'])
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,skin_triangles=tri,
        before_gun_world_cm=transform(gp,gun),after_gun_world_cm=transform(gp,gun),gun_triangles=gt)
    assert protected<.001 and local_error<.001 and digit_skin<.001 and length_error<.01 and severe==0,preservation
    assert baseline==final,(baseline,final)
    assert diagnosis['npc_after_forearm_hand_axis_deg']<diagnosis['npc_before_forearm_hand_axis_deg']-15
    r['comparison_gate_passed']=True;r['status']='fp_wrist_v14_static_comparison_ready'
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items());r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','diagnosis','preservation','baseline_contact','final_contact')},flush=True)
