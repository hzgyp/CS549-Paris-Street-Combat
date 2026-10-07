"""One fixed existing distal curl; analytic small rearward gun seating."""
import ast,sys,math,traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs

PREVIOUS=BASE/'trigger_fit_native_v10/result.json';MEASURE=BASE/'pivot_raise_measure_v7/result.json'
GEOMETRY=MEASURE.parent/'geometry.npz'
POSES=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
AUDIT=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
HELPER=Path(__file__).with_name('blender_pivot_raise_v7.py')
OUT=BASE/'index_curl_v11d';assert not OUT.exists();OUT.mkdir(parents=True)
paths=(PREVIOUS,MEASURE,GEOMETRY,POSES,AUDIT,TOPO,HELPER,Path(__file__))
r={'errors':[],'status':'starting','guards_before':guards(),'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
   'source_model_weights_actions_modified':False,'native_authored':False,'formal_selected':False,'contact_or_gameplay_accepted':False}
pure=[n for n in ast.parse(HELPER.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name in ('swing','encode','left_chain')]
exec(compile(ast.Module(body=pure,type_ignores=[]),str(HELPER)+':pure','exec'),globals())

def intervals(a,b,direction):
    """Continuous SAT for fixed triangle A versus translating triangle B."""
    ae=np.roll(a,-1,axis=1)-a;be=np.roll(b,-1,axis=1)-b
    an=np.cross(ae[:,0],ae[:,1]);bn=np.cross(be[:,0],be[:,1])
    axes=np.concatenate([an[:,None],bn[:,None],
        np.cross(ae[:,:,None,:],be[:,None,:,:]).reshape(-1,9,3),
        np.cross(an[:,None,:],ae),np.cross(bn[:,None,:],be)],axis=1)
    norm=np.linalg.norm(axes,axis=2);axes/=np.maximum(norm[:,:,None],1e-14)
    ap=np.einsum('nvi,nki->nkv',a,axes);bp=np.einsum('nvi,nki->nkv',b,axes)
    amin,amax=ap.min(2),ap.max(2);bmin,bmax=bp.min(2),bp.max(2)
    speed=axes@direction;moving=np.abs(speed)>1e-12
    lo=(amin-bmax)/np.where(moving,speed,1);hi=(amax-bmin)/np.where(moving,speed,1)
    low=np.where(moving,np.minimum(lo,hi),-np.inf);high=np.where(moving,np.maximum(lo,hi),np.inf)
    separated=(~moving)&(norm>1e-12)&((amax<bmin-1e-9)|(bmax<amin-1e-9))
    low=np.maximum(low.max(1),0);high=np.minimum(high.min(1),1)
    good=(low<=high+1e-10)&~separated.any(1)
    return [(float(x),float(y)) for x,y in zip(low[good],high[good])]

try:
    prev,m,poses,audit,topo=map(read,(PREVIOUS,MEASURE,POSES,AUDIT,TOPO))
    assert not prev['errors'] and prev['inputs_unchanged'] and prev['guards_after']==611
    assert all(sha(ROOT/p)==h for p,h in prev['input_hashes'].items())
    d=np.load(GEOMETRY);names=m['bone_names'];parents=m['parents'];weights=d['weights'];tri=d['skin_triangles']
    rest=d['rest_native_cm'];ref=d['reference_matrices'];bones={n:mat(t) for n,t in prev['after']['bones'].items()}
    gb=mat(prev['after']['gun_world']);origin=bones['hand_r'][:3,3].copy();idx=('index_01_r','index_02_r','index_03_r')
    frame={}
    for n in ('hand_r',)+idx:
        actual=np.linalg.inv(ref[names.index(parents[n])])@ref[names.index(n)]
        source=np.linalg.inv(mat(audit['models']['owner']['ref_component'][parents[n]]))@mat(audit['models']['owner']['ref_component'][n])
        frame[n]=float(np.abs(actual-source).max())
    assert max(frame.values())<.001
    source={n:mat(t) for n,t in poses['clips']['owner_reload']['samples']['2.2']['bones_component'].items()}
    local=np.linalg.inv(bones['index_02_r'])@bones['index_03_r'];sl=np.linalg.inv(source['index_02_r'])@source['index_03_r']
    qb=Matrix(local).to_quaternion();qs=Matrix(sl).to_quaternion();q=qb.slerp(qs,1/3)
    adapted=local.copy();adapted[:3,:3]=np.array(q.to_matrix(),float)*np.linalg.norm(local[:3,:3],axis=0)
    fixed=dict(bones);fixed['index_03_r']=bones['index_02_r']@adapted
    curl_deg=math.degrees(qb.rotation_difference(q).angle)
    def skin(pose):
        out=np.zeros_like(rest)
        for j,n in enumerate(names):out+=weights[:,j,None]*transform(rest,pose[n]@np.linalg.inv(ref[j]))
        return out/weights.sum(1)[:,None]
    before=skin(bones);curled=skin(fixed);gp=d['gun_local_cm'];gt=d['gun_triangles']
    direction=-(gb[:3,:3]@np.array([0.,1.,0.]));direction/=np.linalg.norm(direction)
    parts={c['id']:set(c['triangle_ids']) for c in topo['components']}
    digitfaces={}
    for digit in ('index','thumb','middle','ring','pinky'):
        mask=weights[:,[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_r')]].sum(1)>.1
        digitfaces[digit]=tri[np.all(mask[tri],axis=1)]
    ip=(curled-origin)[digitfaces['index']];gunbase=transform(gp,gb)-origin;bt=gunbase[gt]
    bmin=np.minimum(bt.min(1),bt.min(1)+direction);bmax=np.maximum(bt.max(1),bt.max(1)+direction)
    collision=[];paircount=0
    for a in ip:
        mask=np.all(bmax>=a.min(0)-1e-8,axis=1)&np.all(bmin<=a.max(0)+1e-8,axis=1)
        bs=bt[mask];paircount+=len(bs)
        if len(bs):collision.extend(intervals(np.repeat(a[None],len(bs),axis=0),bs,direction))
    merged=[]
    for lo,hi in sorted(collision):
        if merged and lo<=merged[-1][1]+1e-7:merged[-1][1]=max(merged[-1][1],hi)
        else:merged.append([lo,hi])
    clear=[];cursor=0.
    for lo,hi in merged:
        if lo>cursor:clear.append((cursor,lo))
        cursor=max(cursor,hi)
    if cursor<1:clear.append((cursor,1.))
    choices=[]
    for lo,hi in clear:
        # Guard against float32 BVH surface touch; fixed margin not relaxed collision.
        lo+=.015;hi-=.015
        if lo<=hi:choices.append(float(np.clip(.4,lo,hi)))
    assert choices,'No small rearward axial clearance interval'
    distance=min(choices,key=lambda x:abs(x-.4))
    ga=gb.copy();ga[:3,3]+=direction*distance;c=np.eye(4);c[:3,3]=direction*distance
    candidate,reach=left_chain(fixed,c@fixed['hand_l'],parents);after=skin(candidate);gun=transform(gp,ga)-origin
    def contact(body):
        bladeids=sorted(parts[5]);tree=BVHTree.FromPolygons([Vector(p) for p in gun],gt[bladeids].tolist(),all_triangles=True)
        pad=(body-origin)[[21415,21418,21422]].mean(0);hit,normal,face,gap=tree.find_nearest(Vector(pad))
        ct={}
        for digit,faces in digitfaces.items():
            pairs=intersection_pairs(body-origin,faces,gun,gt)
            ct[digit]={part:len({a for a,b in pairs if b in parts[i]}) for part,i in (('stock',0),('guard',4),('blade',5))}
        return {'actual_pad_to_blade_cm':float(gap),'pad_world_cm':(pad+origin).tolist(),'digits':ct}
    ct=contact(after)
    neighbors=np.concatenate([digitfaces[n] for n in ('thumb','middle','ring','pinky')])
    def selfpairs(body):
        return {(a,b) for a,b in intersection_pairs(body-origin,digitfaces['index'],body-origin,neighbors)
                if not set(digitfaces['index'][a])&set(neighbors[b])}
    left=set()
    for n in names:
        p=n
        while p in parents:
            if p=='upperarm_l':left.add(n);break
            p=parents[p]
    allowed=left|{'index_03_r'}
    unaffected=np.all(weights[:,[names.index(n) for n in allowed]]==0,axis=1)
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ab=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);aa=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1)
    localerrors=[]
    for n in names:
        if n.startswith(('thumb_','middle_','ring_','pinky_','index_')) and n!='index_03_r':
            localerrors.append(float(np.abs(np.linalg.inv(candidate[parents[n]])@candidate[n]-np.linalg.inv(bones[parents[n]])@bones[n]).max()))
    preserve={'protected_bone_matrix_error':max(float(np.abs(candidate[n]-bones[n]).max()) for n in names if n not in allowed),
        'other_digit_local_matrix_error':max(localerrors),'unaffected_skin_cm':float(np.linalg.norm(after[unaffected]-before[unaffected],axis=1).max()),
        'right_wrist_matrix_error':float(np.abs(candidate['hand_r']-bones['hand_r']).max()),
        'arm_length_error_cm':float(max(abs(np.linalg.norm(candidate[b][:3,3]-candidate[a][:3,3])-np.linalg.norm(bones[b][:3,3]-bones[a][:3,3])) for a,b in (('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l')))),
        'new_severe_edges':int(np.sum((aa>3*np.maximum(ab,1e-8))&(aa-ab>2))),
        'max_extra_edge_cm':float((aa-ab).max()),'baseline_index_neighbor_self_pairs':len(selfpairs(before)),
        'new_index_neighbor_self_pairs':len(selfpairs(after)-selfpairs(before))}
    indexweights=weights[:,names.index('index_03_r')]>0
    otherweights=np.any(weights[:,[j for j,n in enumerate(names) if n.endswith('_r') and n.startswith(('thumb_','middle_','ring_','pinky_'))]]>0,axis=1)
    mixed=indexweights&otherweights
    preserve['mixed_other_digit_vertex_count']=int(mixed.sum())
    preserve['mixed_other_digit_skin_delta_cm']=float(np.linalg.norm(after[mixed]-before[mixed],axis=1).max()) if mixed.any() else 0
    r.update(reference_local_matrix_errors=frame,curl_degrees=curl_deg,rearward_distance_cm=distance,rearward_world_cm=(direction*distance).tolist(),
        nominal_retreat_cm=.4,swept_pair_count=paircount,collision_intervals_cm=merged,clear_intervals_cm=clear,
        before_bones=prev['after']['bones'],after_bones={n:encode(candidate[n]) if n in allowed else prev['after']['bones'][n] for n in names},
        before_gun_world=prev['after']['gun_world'],after_gun_world=encode(ga),preservation=preserve,reach=reach,
        mesh_world=m['mesh_world'],parents=parents,bone_names=names,allowed_bones=sorted(allowed),index_bones=['index_03_r'],
        pad_world_cm=ct['pad_world_cm'],pad_skin_vertices=[21415,21418,21422],final_contact=ct,
        selected_existing_pose={'clip':poses['clips']['owner_reload']['asset'],'sample_s':2.2,'strength':1/3,'distal_mode':'tip_only'},
        source_index_local_transform=encode(sl),gun_to_right_hand=encode(np.linalg.inv(bones['hand_r'])@ga),gun_rotation_scale_unchanged=True)
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,skin_triangles=tri,
        before_gun_world_cm=transform(gp,gb),after_gun_world_cm=transform(gp,ga),gun_triangles=gt)
    gate=sum(ct['digits']['index'].values())==0 and ct['actual_pad_to_blade_cm']<=.2
    r['contact_gate_passed']=gate
    assert preserve['protected_bone_matrix_error']<1e-8 and preserve['other_digit_local_matrix_error']<1e-8 and preserve['unaffected_skin_cm']<.001 and preserve['new_severe_edges']==0 and preserve['new_index_neighbor_self_pairs']==0
    assert gate,'Analytic axial placement retained but exact local contact failed'
    r['status']='index_curl_v11d_local_geometry_pass'
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items());r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','curl_degrees','rearward_distance_cm','collision_intervals_cm','final_contact','preservation')},flush=True)
