"""Continuous, geometry-measured rigid gun fitting; source hand is immutable."""
import ast
import math
import sys
import traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix, Quaternion, Vector
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
OUT=BASE/'trigger_fit_v10'
assert not OUT.exists()
OUT.mkdir(parents=True)
paths=(PREVIOUS,MEASURE,GEOMETRY,TOPO,HELPER,Path(__file__))
r={'errors':[],'status':'starting','guards_before':guards(),
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
   'source_model_weights_actions_modified':False,'native_authored':False,
   'formal_selected':False,'contact_or_gameplay_accepted':False,'v8_translation_consumed':False,
   'trajectory':[]}
write(OUT/'source.json',r)
tree=ast.parse(HELPER.read_text(encoding='utf-8'))
pure=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('swing','encode','left_chain')]
assert len(pure)==3
exec(compile(ast.Module(body=pure,type_ignores=[]),str(HELPER)+':pure_helpers','exec'),globals())

try:
    previous,m,topo=read(PREVIOUS),read(MEASURE),read(TOPO)
    assert not previous['errors'] and previous['inputs_unchanged'] and previous['guards_after']==611
    assert all(sha(ROOT/p)==h for p,h in previous['input_hashes'].items())
    d=np.load(GEOMETRY); names=m['bone_names'];parents=m['parents']
    original=previous['after']['bones'];bones={n:mat(t) for n,t in original.items()}
    gb=mat(previous['after']['gun_world']);pivot=transform(np.array([m['pivot_gun_cm']]),gb)[0]
    origin=pivot.copy();gb[:3,3]-=origin
    gp=d['gun_local_cm'];gt=d['gun_triangles'];tri=d['skin_triangles'];weights=d['weights']
    ref=d['reference_matrices'];rest=d['rest_native_cm']
    def skin(pose):
        out=np.zeros_like(rest)
        for j,n in enumerate(names):out+=weights[:,j,None]*transform(rest,pose[n]@np.linalg.inv(ref[j]))
        return out/weights.sum(1)[:,None]
    before=skin(bones); body=before-origin
    parts={c['id']:np.array(c['triangle_ids'],int) for c in topo['components']}
    trees={i:BVHTree.FromPolygons([Vector(x) for x in gp],gt[parts[i]].tolist(),all_triangles=True) for i in (0,4,5)}
    topology={}
    for part in (0,4,5):
        faces=gt[parts[part]]
        edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1)
        counts=np.unique(edges,axis=0,return_counts=True)[1]
        volume=float(np.einsum('ij,ij->i',gp[faces[:,0]],np.cross(gp[faces[:,1]],gp[faces[:,2]])).sum()/6)
        topology[part]={'boundary_edges':int(np.sum(counts==1)),'nonmanifold_edges':int(np.sum(counts>2)),
                        'signed_volume_cm3':volume,'signed_distance_used':part==0}
    assert topology[0]['boundary_edges']==0 and topology[0]['nonmanifold_edges']==0 and abs(topology[0]['signed_volume_cm3'])>1
    # Stock is closed with consistently inward original winding. Guard/blade
    # are open: use UNSIGNED clearance and final exact triangle intersections.
    stock_normal_sign=1 if topology[0]['signed_volume_cm3']>0 else -1
    masks={}
    for digit in ('index','thumb','middle','ring','pinky'):
        ids=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_r')]
        masks[digit]=weights[:,ids].sum(1)>.1
    faces={n:tri[np.all(mask[tri],axis=1)] for n,mask in masks.items()}
    indexids=np.flatnonzero(masks['index'])
    # Include actual triangle interiors/edge midpoints, not only sparse skin vertices.
    iv=body[indexids]
    it=body[faces['index']]
    samples=np.concatenate([iv,it.mean(1),(it[:,0]+it[:,1])/2,(it[:,1]+it[:,2])/2,(it[:,2]+it[:,0])/2])
    samples=np.unique(np.round(samples,8),axis=0)
    thumb=body[masks['thumb']]
    pad=transform(np.array([m['pad_hand_cm']]),bones['hand_r'])[0]-origin
    def distances(part,points,g):
        q=transform(points,np.linalg.inv(g));out=[]
        for p in q:
            hit,normal,idx,gap=trees[part].find_nearest(Vector(p))
            assert hit is not None
            if part==0:
                sign=1 if np.dot(p-np.array(hit),stock_normal_sign*np.array(normal))>=0 else -1
                gap*=sign
            out.append(gap)
        return np.array(out)
    oldthumb=distances(0,thumb,gb)
    oldstock=distances(0,samples,gb)
    def change(x):
        a=np.linalg.norm(x[:3]);c=np.eye(4)
        if a>1e-12:c[:3,:3]=np.array(Quaternion((math.cos(a/2),*(x[:3]/a*math.sin(a/2)))).to_matrix(),float)
        c[:3,3]=x[3:]
        return c
    def residual(x,seat):
        g=change(x)@gb
        localpad=transform(pad[None,:],np.linalg.inv(g))[0]
        hit,normal,idx,gap=trees[5].find_nearest(Vector(localpad))
        # Point-to-actual-blade surface vector, with a small nonpenetrating gap.
        delta=localpad-np.array(hit);target=.07
        touch=delta*(max(0,gap-target)/max(gap,1e-8))
        stock=distances(0,samples,g)
        guard=distances(4,samples,g)
        blade=distances(5,samples,g)
        th=distances(0,thumb,g)
        return np.concatenate([touch*12,
            np.minimum(stock-.06,0)*3,
            np.minimum(guard-.06,0)*2,
            np.minimum(blade-.04,0)*2,
            np.minimum(th-np.minimum(oldthumb,0)+.02,0)*.4,
            x[:3]*.12,x[3:]*(.20 if seat else 30)])
    def exact(g):
        gun=transform(gp,g)
        localpad=transform(pad[None,:],np.linalg.inv(g))[0]
        hit,normal,idx,gap=trees[5].find_nearest(Vector(localpad))
        out={}
        psets={i:set(ids.tolist()) for i,ids in parts.items()}
        for digit in masks:
            pairs=intersection_pairs(body,faces[digit],gun,gt)
            out[digit]={name:len({a for a,b in pairs if b in psets[i]}) for name,i in (('stock',0),('guard',4),('blade',5))}
        return {'actual_pad_to_blade_cm':float(gap),'digits':out}
    baseline=exact(gb)
    r.update(component_topology=topology,index_samples=len(samples),baseline_contact=baseline)
    write(OUT/'result.json',r)
    x=np.zeros(6);best=x.copy();bestscore=float('inf');bestcontact=None
    for stage,seat in (('fixed_pivot_rotation',False),('measured_seating',True)):
        if stage=='measured_seating' and bestcontact and bestcontact['actual_pad_to_blade_cm']<=.15 and all(bestcontact['digits']['index'][k]==0 for k in ('stock','guard','blade')):break
        damping=.001
        for iteration in range(50):
            e=residual(x,seat);loss=float(e@e)
            delta=np.array([2e-4]*3+[.002]*3)
            cols=[]
            for j in range(6):
                y=x.copy();y[j]+=delta[j];cols.append((residual(y,seat)-e)/delta[j])
            jac=np.column_stack(cols)
            step=-np.linalg.solve(jac.T@jac+damping*np.eye(6),jac.T@e)
            rs=np.linalg.norm(step[:3]);ts=np.linalg.norm(step[3:])
            step*=min(1,math.radians(3)/max(rs,1e-9),.35/max(ts,1e-9))
            if not seat:step[3:]=0
            accepted=False
            for alpha in (1,.5,.25,.125):
                y=x+alpha*step
                if np.linalg.norm(y[:3])>math.radians(30) or np.linalg.norm(y[3:])>3:continue
                ne=residual(y,seat)
                if ne@ne<loss-1e-9:x=y;accepted=True;break
            if not accepted:damping*=10
            else:damping=max(.0001,damping*.6)
            # Exact full triangles every coherent5iterations, and at convergence.
            if iteration%5==0 or not accepted or np.linalg.norm(step)<1e-5:
                c=exact(change(x)@gb)
                ic=c['digits']['index']
                score=sum(ic.values())*10+c['actual_pad_to_blade_cm']
                r['trajectory'].append({'stage':stage,'iteration':iteration,'loss':loss,'x':x.tolist(),'contact':c})
                write(OUT/'result.json',r)
                print('fit',stage,iteration,round(loss,4),'pad',round(c['actual_pad_to_blade_cm'],4),'index',ic,flush=True)
                if score<bestscore:bestscore=score;best=x.copy();bestcontact=c
                if c['actual_pad_to_blade_cm']<=.15 and all(ic[k]==0 for k in ('stock','guard','blade')):
                    best=x.copy();bestcontact=c;break
            if not accepted and damping>1000:break
        x=best.copy()
    c=change(best);ga=c@gb
    # Return from pivot-local diagnostics to native world without accumulating offset.
    cw=c.copy();cw[:3,3]=origin+c[:3,3]-c[:3,:3]@origin
    afterworld=ga.copy();afterworld[:3,3]+=origin
    beforeworld=gb.copy();beforeworld[:3,3]+=origin
    candidate,reach=left_chain(bones,cw@bones['hand_l'],parents)
    allowed=set()
    for n in names:
        p=n
        while p in parents:
            if p=='upperarm_l':allowed.add(n);break
            p=parents[p]
    protected=max(float(np.abs(candidate[n]-bones[n]).max()) for n in names if n not in allowed)
    digit=max(float(np.abs(np.linalg.inv(candidate[parents[n]])@candidate[n]-np.linalg.inv(bones[parents[n]])@bones[n]).max()) for n in names if n.endswith('_l') and n.startswith(('thumb_','index_','middle_','ring_','pinky_')))
    after=skin(candidate)
    rightids=[j for j,n in enumerate(names) if n=='hand_r' or (n.endswith('_r') and n.startswith(('thumb_','index_','middle_','ring_','pinky_')))]
    rightmask=np.any(weights[:,rightids]>0,axis=1)
    unaffected=np.all(weights[:,[names.index(n) for n in allowed]]==0,axis=1)
    palm=weights[:,names.index('hand_l')]>.99999
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ab=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);aa=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1)
    preservation={'protected_bone_matrix_error':protected,'digit_local_matrix_error':digit,
        'right_skin_cm':float(np.linalg.norm(after[rightmask]-before[rightmask],axis=1).max()),
        'unaffected_skin_cm':float(np.linalg.norm(after[unaffected]-before[unaffected],axis=1).max()),
        'palm_tracking_cm':float(np.linalg.norm(after[palm]-transform(before[palm],cw),axis=1).max()),
        'arm_length_error_cm':float(max(abs(np.linalg.norm(candidate[b][:3,3]-candidate[a][:3,3])-np.linalg.norm(bones[b][:3,3]-bones[a][:3,3])) for a,b in (('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l')))),
        'new_severe_edges':int(np.sum((aa>3*np.maximum(ab,1e-8)) & (aa-ab>2))),
        'max_extra_edge_cm':float((aa-ab).max())}
    assert protected<1e-8 and digit<1e-8 and preservation['right_skin_cm']<.001 and preservation['unaffected_skin_cm']<.001 and preservation['palm_tracking_cm']<.05 and preservation['arm_length_error_cm']<.01 and preservation['new_severe_edges']==0
    gate=bestcontact['actual_pad_to_blade_cm']<=.15 and all(bestcontact['digits']['index'][k]==0 for k in ('stock','guard','blade'))
    r.update(status='trigger_fit_v10_local_geometry_pass' if gate else 'trigger_fit_v10_bounded_residual_retained',contact_gate_passed=gate,
        before_bones=original,after_bones={n:encode(candidate[n]) if n in allowed else original[n] for n in names},
        before_gun_world=encode(beforeworld),after_gun_world=encode(afterworld),preservation=preservation,reach=reach,
        mesh_world=m['mesh_world'],parents=parents,bone_names=names,allowed_bones=sorted(allowed),
        pivot_world_cm=origin.tolist(),pivot_gun_cm=m['pivot_gun_cm'],pad_world_cm=(pad+origin).tolist(),
        blade_gun_cm=m['blade_gun_cm'],additional_rotation_vector_deg=np.degrees(best[:3]).tolist(),
        additional_angle_deg=float(np.degrees(np.linalg.norm(best[:3]))),pivot_displacement_world_cm=best[3:].tolist(),
        final_contact=bestcontact,gun_to_right_hand=encode(np.linalg.inv(bones['hand_r'])@afterworld))
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,skin_triangles=tri,
        before_gun_world_cm=transform(gp,beforeworld),after_gun_world_cm=transform(gp,afterworld),gun_triangles=gt)
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
    r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','final_contact','additional_angle_deg','pivot_displacement_world_cm','preservation')},flush=True)
