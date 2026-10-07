"""Fit the actual curved working blade, not its nearest upper attachment."""
import ast,sys,math,traceback
from pathlib import Path
import numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs
PREVIOUS=BASE/'pivot_rotate_native_v9/result.json'
MEASURE=BASE/'pivot_raise_measure_v7/result.json'
GEOMETRY=MEASURE.parent/'geometry.npz'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
HELPER=Path(__file__).with_name('blender_pivot_raise_v7.py')
OUT=BASE/'trigger_surface_v10b';assert not OUT.exists();OUT.mkdir(parents=True)
paths=(PREVIOUS,MEASURE,GEOMETRY,TOPO,HELPER,Path(__file__))
r={'errors':[],'status':'starting','guards_before':guards(),'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
   'source_model_weights_actions_modified':False,'native_authored':False,'formal_selected':False,
   'contact_or_gameplay_accepted':False,'v8_translation_consumed':False,'evaluations':[]}
pure=[n for n in ast.parse(HELPER.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name in ('swing','encode','left_chain')]
exec(compile(ast.Module(body=pure,type_ignores=[]),str(HELPER)+':pure','exec'),globals())
try:
    prev,m,topo=read(PREVIOUS),read(MEASURE),read(TOPO)
    assert prev['inputs_unchanged'] and not prev['errors'] and prev['guards_after']==611
    assert all(sha(ROOT/p)==h for p,h in prev['input_hashes'].items())
    d=np.load(GEOMETRY);names=m['bone_names'];parents=m['parents'];weights=d['weights'];tri=d['skin_triangles']
    bones={n:mat(t) for n,t in prev['after']['bones'].items()};gb=mat(prev['after']['gun_world'])
    pivot=transform(np.array([m['pivot_gun_cm']]),gb)[0];origin=pivot.copy();g=gb.copy();g[:3,3]-=origin
    rest=d['rest_native_cm'];ref=d['reference_matrices']
    def skin(pose):
        out=np.zeros_like(rest)
        for j,n in enumerate(names):out+=weights[:,j,None]*transform(rest,pose[n]@np.linalg.inv(ref[j]))
        return out/weights.sum(1)[:,None]
    before=skin(bones);body=before-origin;gp=d['gun_local_cm'];gt=d['gun_triangles']
    parts={c['id']:set(c['triangle_ids']) for c in topo['components']}
    digitfaces={}
    for digit in ('index','thumb','middle','ring','pinky'):
        inds=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_r')]
        mask=weights[:,inds].sum(1)>.1;digitfaces[digit]=tri[np.all(mask[tri],axis=1)]
    pad=transform(np.array([m['pad_hand_cm']]),bones['hand_r'])[0]-origin
    index_tree=BVHTree.FromPolygons([Vector(p) for p in body],digitfaces['index'].tolist(),all_triangles=True)
    hit,n,face,gap=index_tree.find_nearest(Vector(pad));assert gap<.001
    # The source skin was reflected into UE; correct its measured winding.
    pn=-np.array(n);pn/=np.linalg.norm(pn)
    bladeids=np.array(sorted(parts[5]),int);bt=gp[gt[bladeids]];centers=bt.mean(1)
    normals=-np.cross(bt[:,1]-bt[:,0],bt[:,2]-bt[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
    # Actual separate blade component; lower curved pressure surfaces, not
    # coordinate-based replacement mesh labels or gun material reconstruction.
    functional=(centers[:,2]<-.9)&(centers[:,2]>-2.7)&(np.abs(normals[:,0])<.8)&(np.abs(normals[:,1])>.15)
    selected=np.flatnonzero(functional);assert len(selected)>=4
    r.update(pad_skin_triangle=int(face),pad_normal_native=pn.tolist(),functional_triangles=bladeids[selected].tolist(),
             inherited_upper_stem_point_cm=m['blade_gun_cm'])
    def contact(gunmat,all_digits=False):
        gun=transform(gp,gunmat)
        tree=BVHTree.FromPolygons([Vector(p) for p in gun],gt[bladeids].tolist(),all_triangles=True)
        hit,n,face,gap=tree.find_nearest(Vector(pad));result={}
        for digit in (digitfaces if all_digits else ('index',)):
            pairs=intersection_pairs(body,digitfaces[digit],gun,gt)
            result[digit]={part:len({a for a,b in pairs if b in parts[i]}) for part,i in (('stock',0),('guard',4),('blade',5))}
        return {'actual_pad_to_blade_cm':float(gap),'digits':result}
    r['baseline_contact']=contact(g,True)
    # One transform per actual curved face, derived from geometry; no guessed
    # angles. Maximum44 geometric possibilities, all residuals retained.
    best=None;bestscore=float('inf')
    for j in selected:
        surface=centers[j];old=transform(surface[None,:],g)[0]
        target=pad+pn*.10
        rot=swing(old,target);angle=math.degrees(math.acos(np.clip((np.trace(rot)-1)/2,-1,1)))
        seat=target-rot@old
        if angle>30 or np.linalg.norm(seat)>3:continue
        c=np.eye(4);c[:3,:3]=rot;c[:3,3]=seat
        aftergun=c@g;ct=contact(aftergun)
        count=sum(ct['digits']['index'].values())
        score=count*10+ct['actual_pad_to_blade_cm']
        record={'actual_blade_triangle':int(bladeids[j]),'surface_local_cm':surface.tolist(),
                'normal_local':normals[j].tolist(),'angle_deg':angle,'seat_cm':seat.tolist(),'contact':ct}
        r['evaluations'].append(record);write(OUT/'result.json',r)
        print('surface',record['actual_blade_triangle'],'angle',round(angle,2),'pad',round(ct['actual_pad_to_blade_cm'],4),'index',ct['digits']['index'],flush=True)
        if score<bestscore:bestscore=score;best=(c,aftergun,record)
        if count==0 and ct['actual_pad_to_blade_cm']<=.15:break
    assert best is not None,'No contact transform within finite bounds'
    c,ga,record=best;cw=c.copy();cw[:3,3]=origin+c[:3,3]-c[:3,:3]@origin
    afterworld=ga.copy();afterworld[:3,3]+=origin
    candidate,reach=left_chain(bones,cw@bones['hand_l'],parents)
    allowed=set()
    for n in names:
        p=n
        while p in parents:
            if p=='upperarm_l':allowed.add(n);break
            p=parents[p]
    after=skin(candidate)
    rightids=[j for j,n in enumerate(names) if n=='hand_r' or (n.endswith('_r') and n.startswith(('thumb_','index_','middle_','ring_','pinky_')))]
    rightmask=np.any(weights[:,rightids]>0,axis=1);unaffected=np.all(weights[:,[names.index(n) for n in allowed]]==0,axis=1)
    palm=weights[:,names.index('hand_l')]>.99999
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ab=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);aa=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1)
    protected=max(float(np.abs(candidate[n]-bones[n]).max()) for n in names if n not in allowed)
    digiterror=max(float(np.abs(np.linalg.inv(candidate[parents[n]])@candidate[n]-np.linalg.inv(bones[parents[n]])@bones[n]).max()) for n in names if n.endswith('_l') and n.startswith(('thumb_','index_','middle_','ring_','pinky_')))
    preservation={'protected_bone_matrix_error':protected,'digit_local_matrix_error':digiterror,
        'right_skin_cm':float(np.linalg.norm(after[rightmask]-before[rightmask],axis=1).max()),
        'unaffected_skin_cm':float(np.linalg.norm(after[unaffected]-before[unaffected],axis=1).max()),
        'palm_tracking_cm':float(np.linalg.norm(after[palm]-transform(before[palm],cw),axis=1).max()),
        'arm_length_error_cm':float(max(abs(np.linalg.norm(candidate[b][:3,3]-candidate[a][:3,3])-np.linalg.norm(bones[b][:3,3]-bones[a][:3,3])) for a,b in (('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l')))),
        'new_severe_edges':int(np.sum((aa>3*np.maximum(ab,1e-8)) & (aa-ab>2))),
        'max_extra_edge_cm':float((aa-ab).max())}
    assert protected<1e-8 and digiterror<1e-8 and preservation['right_skin_cm']<.001 and preservation['unaffected_skin_cm']<.001 and preservation['palm_tracking_cm']<.05 and preservation['arm_length_error_cm']<.01 and preservation['new_severe_edges']==0
    final=contact(ga,True);gate=final['actual_pad_to_blade_cm']<=.15 and sum(final['digits']['index'].values())==0
    r.update(status='trigger_surface_v10b_local_geometry_pass' if gate else 'trigger_surface_v10b_residual_retained',contact_gate_passed=gate,
        before_bones=prev['after']['bones'],after_bones={n:encode(candidate[n]) if n in allowed else prev['after']['bones'][n] for n in names},
        before_gun_world=prev['after']['gun_world'],after_gun_world=encode(afterworld),preservation=preservation,reach=reach,
        mesh_world=m['mesh_world'],parents=parents,bone_names=names,allowed_bones=sorted(allowed),
        pivot_world_cm=origin.tolist(),pivot_gun_cm=m['pivot_gun_cm'],pivot_displacement_world_cm=c[:3,3].tolist(),
        pad_world_cm=(pad+origin).tolist(),blade_gun_cm=record['surface_local_cm'],additional_angle_deg=record['angle_deg'],
        final_contact=final,selected_surface_record=record,gun_to_right_hand=encode(np.linalg.inv(bones['hand_r'])@afterworld))
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,skin_triangles=tri,
        before_gun_world_cm=transform(gp,gb),after_gun_world_cm=transform(gp,afterworld),gun_triangles=gt)
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items());r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','additional_angle_deg','pivot_displacement_world_cm','final_contact','preservation')},flush=True)
