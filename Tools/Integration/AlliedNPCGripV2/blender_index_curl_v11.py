"""Small rigid retreat plus compatible EXISTING right-index locals, no new action."""
import ast, sys, math, traceback
from pathlib import Path
import numpy as np
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat, transform, intersection_pairs

PREVIOUS=BASE/'trigger_fit_native_v10/result.json'
MEASURE=BASE/'pivot_raise_measure_v7/result.json'
GEOMETRY=MEASURE.parent/'geometry.npz'
POSES=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
AUDIT=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
HELPER=Path(__file__).with_name('blender_pivot_raise_v7.py')
OUT=BASE/'index_curl_v11';assert not OUT.exists();OUT.mkdir(parents=True)
paths=(PREVIOUS,MEASURE,GEOMETRY,POSES,AUDIT,TOPO,HELPER,Path(__file__),Path(__file__).with_name('common.py'))
r={'errors':[],'status':'starting','guards_before':guards(),
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
   'source_model_weights_actions_modified':False,'native_authored':False,
   'formal_selected':False,'contact_or_gameplay_accepted':False,'evaluations':[]}
pure=[n for n in ast.parse(HELPER.read_text(encoding='utf-8')).body
      if isinstance(n,ast.FunctionDef) and n.name in ('swing','encode','left_chain')]
exec(compile(ast.Module(body=pure,type_ignores=[]),str(HELPER)+':pure','exec'),globals())
try:
    prev,m,poses,audit,topo=map(read,(PREVIOUS,MEASURE,POSES,AUDIT,TOPO))
    assert not prev['errors'] and prev['inputs_unchanged'] and prev['guards_after']==611
    assert all(sha(ROOT/p)==h for p,h in prev['input_hashes'].items())
    d=np.load(GEOMETRY);names=m['bone_names'];parents=m['parents']
    rest=d['rest_native_cm'];weights=d['weights'];tri=d['skin_triangles'];ref=d['reference_matrices']
    bones={n:mat(t) for n,t in prev['after']['bones'].items()}
    gb=mat(prev['after']['gun_world']);origin=bones['hand_r'][:3,3].copy()
    idx=('index_01_r','index_02_r','index_03_r')
    # SAME native reference-local frame, not inherited player pose offsets.
    frame_errors={}
    for n in ('hand_r',)+idx:
        j=names.index(n);pj=names.index(parents[n])
        actual=np.linalg.inv(ref[pj])@ref[j]
        source=mat(audit['models']['owner']['ref_component'][parents[n]])
        source=np.linalg.inv(source)@mat(audit['models']['owner']['ref_component'][n])
        frame_errors[n]=float(np.abs(actual-source).max())
    assert max(frame_errors.values())<.001,frame_errors
    r['reference_local_matrix_errors']=frame_errors
    axis=gb[:3,:3]@np.array([0.,1.,0.]);axis/=np.linalg.norm(axis)
    rearward=-axis*.4
    ga=gb.copy();ga[:3,3]+=rearward
    r.update(rearward_distance_cm=.4,rearward_world_cm=rearward.tolist(),gun_rotation_scale_unchanged=True)
    c=np.eye(4);c[:3,3]=rearward
    follow,reach=left_chain(bones,c@bones['hand_l'],parents)
    left=set()
    for n in names:
        p=n
        while p in parents:
            if p=='upperarm_l':left.add(n);break
            p=parents[p]
    allowed=left|set(idx)
    def skin(pose):
        out=np.zeros_like(rest)
        for j,n in enumerate(names):out+=weights[:,j,None]*transform(rest,pose[n]@np.linalg.inv(ref[j]))
        return out/weights.sum(1)[:,None]
    before=skin(bones)
    gp=d['gun_local_cm'];gt=d['gun_triangles'];gun=transform(gp,ga)-origin
    parts={q['id']:set(q['triangle_ids']) for q in topo['components']}
    digitfaces={}
    for digit in ('index','thumb','middle','ring','pinky'):
        ids=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_r')]
        mask=weights[:,ids].sum(1)>.1;digitfaces[digit]=tri[np.all(mask[tri],axis=1)]
    bladeids=np.array(sorted(parts[5]),int)
    blade=BVHTree.FromPolygons([Vector(p) for p in gun],gt[bladeids].tolist(),all_triangles=True)
    padverts=np.array([21415,21418,21422])
    def contact(body,all_digits=False):
        local=body-origin;pad=local[padverts].mean(0)
        hit,normal,face,gap=blade.find_nearest(Vector(pad))
        result={}
        for digit in (digitfaces if all_digits else ('index',)):
            pairs=intersection_pairs(local,digitfaces[digit],gun,gt)
            result[digit]={part:len({a for a,b in pairs if b in parts[i]})
                for part,i in (('stock',0),('guard',4),('blade',5))}
        return {'actual_pad_to_blade_cm':float(gap),'pad_world_cm':(pad+origin).tolist(),'digits':result}
    # Exclude shared-vertex adjacent triangles from self-contact, retain baseline.
    neighbor=np.concatenate([digitfaces[n] for n in ('thumb','middle','ring','pinky')])
    def self_pairs(body):
        pairs=intersection_pairs(body-origin,digitfaces['index'],body-origin,neighbor)
        return {(a,b) for a,b in pairs if not set(digitfaces['index'][a])&set(neighbor[b])}
    baseline_self=self_pairs(before)
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ab=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1)
    local_base={n:np.linalg.inv(bones[parents[n]])@bones[n] for n in idx}
    r['after_retreat_before_curl']=contact(before,True)
    best=None
    # Inspect all retained mature pose samples, three declared interpolation strengths.
    for clip in ('owner_idle','owner_reload'):
        for phase,sample in poses['clips'][clip]['samples'].items():
            src={n:mat(t) for n,t in sample['bones_component'].items()}
            local_src={n:np.linalg.inv(src[parents[n]])@src[n] for n in idx}
            for strength in (1/3,2/3,1.):
                candidate=dict(follow);deltas={}
                for n in idx:
                    local=local_base[n].copy();scale=np.linalg.norm(local[:3,:3],axis=0)
                    qb=Quaternion(tuple(encode(local)['q'][j] for j in (3,0,1,2)))
                    qs=Quaternion(tuple(encode(local_src[n])['q'][j] for j in (3,0,1,2)))
                    q=qb.slerp(qs,strength);local[:3,:3]=np.array(q.to_matrix(),float)*scale
                    candidate[n]=candidate[parents[n]]@local
                    deltas[n]=math.degrees(qb.rotation_difference(q).angle)
                body=skin(candidate);ct=contact(body);aa=np.linalg.norm(body[edges[:,1]]-body[edges[:,0]],axis=1)
                severe=int(np.sum((aa>3*np.maximum(ab,1e-8))&(aa-ab>2)))
                # Curl is a bend between local segments, not displacement alone.
                direction0=bones['index_02_r'][:3,3]-bones['index_01_r'][:3,3]
                direction1=candidate['index_03_r'][:3,3]-candidate['index_02_r'][:3,3]
                bend=math.degrees(math.acos(np.clip(np.dot(direction0,direction1)/(np.linalg.norm(direction0)*np.linalg.norm(direction1)),-1,1)))
                row={'clip':poses['clips'][clip]['asset'],'sample_s':float(phase),'strength':strength,
                     'joint_rotation_change_deg':deltas,'bend_from_original_proximal_deg':bend,
                     'contact':ct,'new_severe_edges':severe}
                if sum(ct['digits']['index'].values())==0 and ct['actual_pad_to_blade_cm']<=.2 and severe==0 and bend>=10:
                    newself=self_pairs(body)-baseline_self;row['new_index_neighbor_self_pairs']=len(newself)
                    if not newself:
                        row['local_gate_passed']=True
                        if best is None or ct['actual_pad_to_blade_cm']<best[2]['contact']['actual_pad_to_blade_cm']:
                            best=(candidate,body,row,local_src)
                r['evaluations'].append(row);write(OUT/'result.json',r)
                print(clip,phase,round(strength,3),'bend',round(bend,2),'gap',round(ct['actual_pad_to_blade_cm'],3),'cross',ct['digits']['index'],flush=True)
    assert best is not None,'No existing pose within finite local curl/contact gate'
    candidate,after,selected,source_locals=best
    unaffected=np.all(weights[:,[names.index(n) for n in allowed]]==0,axis=1)
    indexmask=np.any(weights[:,[names.index(n) for n in idx]]>0,axis=1)
    otherdigitmask=np.any(weights[:,[j for j,n in enumerate(names) if n.endswith('_r') and n.startswith(('thumb_','middle_','ring_','pinky_'))]]>0,axis=1)
    mixed=indexmask&otherdigitmask
    protected=max(float(np.abs(candidate[n]-bones[n]).max()) for n in names if n not in allowed)
    local_errors={}
    for n in names:
        if n in idx or n not in parents or parents[n] not in names:continue
        local_errors[n]=float(np.abs(np.linalg.inv(candidate[parents[n]])@candidate[n]-np.linalg.inv(bones[parents[n]])@bones[n]).max())
    aa=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1)
    preserve={'protected_bone_matrix_error':protected,'other_digit_local_matrix_error':max(v for n,v in local_errors.items() if n.startswith(('thumb_','middle_','ring_','pinky_','index_'))),
              'unaffected_skin_cm':float(np.linalg.norm(after[unaffected]-before[unaffected],axis=1).max()),
              'mixed_other_digit_vertex_count':int(mixed.sum()),'mixed_other_digit_skin_delta_cm':float(np.linalg.norm(after[mixed]-before[mixed],axis=1).max()) if mixed.any() else 0,
              'arm_length_error_cm':float(max(abs(np.linalg.norm(candidate[b][:3,3]-candidate[a][:3,3])-np.linalg.norm(bones[b][:3,3]-bones[a][:3,3])) for a,b in (('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l')))),
              'new_severe_edges':int(np.sum((aa>3*np.maximum(ab,1e-8))&(aa-ab>2))),
              'max_extra_edge_cm':float((aa-ab).max()),'right_wrist_matrix_error':float(np.abs(candidate['hand_r']-bones['hand_r']).max()),
              'baseline_index_neighbor_self_pairs':len(baseline_self),'new_index_neighbor_self_pairs':len(self_pairs(after)-baseline_self)}
    assert protected<1e-8 and preserve['other_digit_local_matrix_error']<1e-8 and preserve['unaffected_skin_cm']<.001 and preserve['arm_length_error_cm']<.01 and preserve['new_severe_edges']==0 and preserve['new_index_neighbor_self_pairs']==0
    r.update(status='index_curl_v11_local_geometry_pass',contact_gate_passed=True,
        before_bones=prev['after']['bones'],after_bones={n:encode(candidate[n]) if n in allowed else prev['after']['bones'][n] for n in names},
        before_gun_world=prev['after']['gun_world'],after_gun_world=encode(ga),preservation=preserve,reach=reach,
        mesh_world=m['mesh_world'],parents=parents,bone_names=names,allowed_bones=sorted(allowed),index_bones=list(idx),
        selected_existing_pose=selected,source_index_local_transforms={n:encode(source_locals[n]) for n in idx},
        pad_world_cm=selected['contact']['pad_world_cm'],pad_skin_vertices=padverts.tolist(),final_contact=contact(after,True),
        gun_to_right_hand=encode(np.linalg.inv(bones['hand_r'])@ga))
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,skin_triangles=tri,
        before_gun_world_cm=transform(gp,gb),after_gun_world_cm=transform(gp,ga),gun_triangles=gt)
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items());r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','rearward_world_cm','selected_existing_pose','final_contact','preservation')},flush=True)
