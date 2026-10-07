"""Measured assembly/support follow with original segment lengths; unchanged digit locals."""
import math
import numpy as np
from mathutils import Matrix,Vector

def encode(m):
    t,q,s=Matrix(m).decompose()
    return {'t':list(t),'q':[q.x,q.y,q.z,q.w],'s':list(s)}

def arm_targets(bones,targets,parents):
    explicit={}; checks={}
    for side,target in targets.items():
        u,l,h=['upperarm_'+side,'lowerarm_'+side,'hand_'+side]
        shoulder,elbow,wrist=[bones[n][:3,3] for n in (u,l,h)]
        goal=target[:3,3];a=np.linalg.norm(elbow-shoulder);b=np.linalg.norm(wrist-elbow)
        reach=np.linalg.norm(goal-shoulder)
        assert abs(a-b)+1e-5<reach<a+b-1e-5,('Unreachable original-length arm',side,reach,a,b)
        line=(goal-shoulder)/reach;bend=elbow-shoulder-line*np.dot(elbow-shoulder,line)
        assert np.linalg.norm(bend)>1e-6
        bend/=np.linalg.norm(bend);along=(a*a-b*b+reach*reach)/(2*reach)
        newelbow=shoulder+along*line+math.sqrt(max(0,a*a-along*along))*bend
        explicit[h]=target.copy()
        for n,p,v,w in ((u,shoulder,elbow-shoulder,newelbow-shoulder),(l,newelbow,wrist-elbow,goal-newelbow)):
            rot=np.array(Vector(v).rotation_difference(Vector(w)).to_matrix(),float)
            value=bones[n].copy();value[:3,:3]=rot@value[:3,:3];value[:3,3]=p;explicit[n]=value
        checks[side]={'upper_length_cm':float(a),'forearm_length_cm':float(b),'reach_cm':float(reach),
            'wrist_motion_cm':float(np.linalg.norm(goal-wrist)),
            'upper_length_error_cm':float(abs(np.linalg.norm(newelbow-shoulder)-a)),
            'forearm_length_error_cm':float(abs(np.linalg.norm(goal-newelbow)-b))}
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

def integrate(scope):
    # First yaw remains gun-only. The downward step now moves the fitted right
    # grasp and gun together instead of moving the trigger through a fixed digit.
    bones=scope['bones']; r=scope['r'];mat=scope['mat'];transform=scope['transform']
    g1=scope['g1'];trial=scope['trial'];original=scope['original'];palm=scope['palm']
    change=mat(trial)@np.linalg.inv(mat(g1))
    right=change@bones['hand_r']
    lc=mat(trial)@np.linalg.inv(mat(original))
    left=lc@bones['hand_l']
    actualwood=np.array(scope['tm'].point(trial,scope['support_local']))
    movedpalm=transform(palm[None],lc)[0]
    away=movedpalm-actualwood; assert np.linalg.norm(away)>.01
    desired=actualwood+away/np.linalg.norm(away)*.3
    left[:3,3]+=desired-movedpalm
    after,checks=arm_targets(bones,{'r':right,'l':left},scope['parents'])
    def skin(pose):
        out=np.zeros_like(scope['rest'])
        for j,n in enumerate(scope['names']):out+=scope['weights'][:,j,None]*transform(scope['rest'],pose[n]@np.linalg.inv(scope['ref'][n]))
        return out/scope['weights'].sum(1)[:,None]
    finalskin=skin(after)
    allowed={n for n in bones if n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))}
    protected=[n for n in bones if n not in allowed]
    assert max(np.max(abs(after[n]-bones[n])) for n in protected)<1e-8
    locals_error=max(np.max(abs(np.linalg.inv(after[scope['parents'][n]])@after[n]-np.linalg.inv(bones[scope['parents'][n]])@bones[n]))
                     for n in bones if n.startswith(('thumb_','index_','middle_','ring_','pinky_')))
    assert locals_error<1e-8
    relative_error=float(np.max(abs(np.linalg.inv(right)@mat(trial)-np.linalg.inv(bones['hand_r'])@mat(g1))))
    assert relative_error<1e-8
    edges=np.unique(np.sort(np.concatenate([scope['tri'][:,[0,1]],scope['tri'][:,[1,2]],scope['tri'][:,[2,0]]]),axis=1),axis=0)
    before_len=np.linalg.norm(scope['posed'][edges[:,0]]-scope['posed'][edges[:,1]],axis=1)
    after_len=np.linalg.norm(finalskin[edges[:,0]]-finalskin[edges[:,1]],axis=1)
    newsevere=int(np.sum((after_len>before_len*3)&(after_len-before_len>2)))
    assert newsevere==0,('New severe sleeve edges',newsevere)
    before=scope['contacts'](scope['g0'],scope['gp'],scope['gt'],scope['groups'],scope['posed'],scope['tri'],scope['masks'])
    first=scope['contacts'](g1,scope['gp'],scope['gt'],scope['groups'],scope['posed'],scope['tri'],scope['masks'])
    final=scope['contacts'](trial,scope['gp'],scope['gt'],scope['groups'],finalskin,scope['tri'],scope['masks'])
    right_index=scope['names'].index('hand_r')
    # Distal hand skin should rigidly follow, not detach from a translated wrist.
    digitmask=np.logical_or.reduce([scope['masks'][d+'_r'] for d in ('thumb','index','middle','ring','pinky')])
    track=float(np.linalg.norm(finalskin[digitmask]-transform(scope['posed'][digitmask],change),axis=1).max())
    r.update(status='ordered_assembly_support_requires_native_review',
        all_bones_fixed=False,source_model_weights_actions_modified=False,
        bone_names=scope['names'],parents=scope['parents'],
        before_bones={n:encode(b) for n,b in bones.items()},
        first_bones={n:encode(b) for n,b in bones.items()},
        after_bones={n:encode(b) for n,b in after.items()},
        before_gun_world=scope['g0'],after_gun_world=trial,
        before_crossing_faces=before,first_crossing_faces=first,after_crossing_faces=final,
        original_length_arm_checks=checks,protected_bones=protected,
        digit_local_matrix_error=locals_error,right_gun_hand_matrix_error=relative_error,
        right_digit_rigid_skin_error_cm=track,new_severe_edges=newsevere,
        max_extra_skin_edge_cm=float(np.max(after_len-before_len)),
        left_palm_target_world_cm=desired.tolist(),left_target_standoff_cm=.3,
        right_trigger_relative_preserved_during_pitch=True,
        mechanism='Yaw gun only; lower right-hand/gun assembly; whole left source-length arm follows actual fore-end')
    scope['np'].savez_compressed(scope['OUT']/'geometry.npz',skin=finalskin,before_skin=scope['posed'],skin_triangles=scope['tri'],
        gun_local_cm=scope['gp'],gun_triangles=scope['gt'],rest_native_cm=scope['rest'],weights=scope['weights'],
        reference_matrices=np.array([scope['ref'][n] for n in scope['names']]))
    scope['write'](scope['OUT']/'result.json',r)
    scope['print'](scope['json'].dumps({k:r[k] for k in ('status','measured_pitch_deg','original_length_arm_checks','new_severe_edges','right_digit_rigid_skin_error_cm','first_crossing_faces','after_crossing_faces')}))
