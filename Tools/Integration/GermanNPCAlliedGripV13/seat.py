"""One opposed-surface rigid seating, no per-digit or parameter-grid solve."""
import sys,traceback
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards,tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs
sys.path.insert(0,str(ROOT/'Tools/Integration/GermanNPCOrderedGripV4'))
from arm_fit import encode,arm_targets
BASE=STORE/'Evidence/GermanNPCAlliedGripV13';OUT=BASE/'seating_v3'
PREV=BASE/'transfer_fit_v2/result.json';PROBE=BASE/'probe_v2/result.json'
GD=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz';AD=STORE/'Evidence/AlliedNPCGripV2/pivot_raise_measure_v7/geometry.npz'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
assert not OUT.exists();OUT.mkdir(parents=True)
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in (PREV,PROBE,GD,AD,TOPO,Path(__file__))],
   'source_modified':False,'formal_selected':False,'native_tested':False,'contact_accepted':False,'new_motion':False}
try:
    old=read(PREV);probe=read(PROBE);assert not old['errors']
    for entry in old['inputs']:assert sha(ROOT/entry['path'])==entry['sha256']
    d=np.load(GD);ad=np.load(AD);saved=np.load(PREV.parent/'geometry.npz')
    names=old['bone_names'];parents=old['parents'];w=d['weights'];rest=d['rest_native_cm'];refs=d['reference_matrices'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles']
    b={n:mat(v) for n,v in old['after_bones'].items()};p=saved['skin'];gm=mat(old['after_gun_world']);world=transform(gp,gm)
    blade_ids=np.arange(9026,9214);stock_ids=np.arange(9214,24466);guard_ids=np.arange(3508,4868)
    assert len(gt)==24466
    am=b['hand_r']@mat(probe['allied_gun_world']);ap=transform(ad['gun_local_cm'],am);at=ad['gun_triangles']
    topo=read(TOPO);a_stock=np.array(next(c['triangle_ids'] for c in topo['components'] if c['id']==0),int)
    a_tree=BVHTree.FromPolygons([Vector(v) for v in ap],at[a_stock].tolist(),all_triangles=True)
    g_trees={k:BVHTree.FromPolygons([Vector(v) for v in world],gt[ids].tolist(),all_triangles=True) for k,ids in [('wood',stock_ids),('blade',blade_ids)]}
    body_norm=-np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]])
    body_norm/=np.maximum(np.linalg.norm(body_norm,axis=1)[:,None],1e-12)
    stations=[];sources=[];targets=[];weights=[]
    for digit,weight in [('index',12),('thumb',4),('middle',3),('ring',3),('pinky',2)]:
        joints=[names.index(f'{digit}_{i:02}_r') for i in (2,3)]
        ids=np.flatnonzero(np.all((w[:,joints].sum(1)>.75)[tri],axis=1));assert len(ids)>4
        candidates=[]
        for f in ids:
            center=p[tri[f]].mean(0);n=body_norm[f]
            tree=g_trees['blade'] if digit=='index' else a_tree
            point,gn,fi,dist=tree.find_nearest(Vector(center))
            if n@np.array(gn)<-.25:candidates.append((float(dist),int(f),center,n,np.array(point,float)))
        assert candidates,('No opposed pad surface',digit)
        distance,f,center,n,reference=min(candidates,key=lambda x:x[0])
        if digit=='index':actual=reference
        else:
            local=transform(reference[None],np.linalg.inv(am))[0]
            local+=np.array(old['actual_german_blade_local_cm'])-old['actual_allied_blade_local_cm']
            guess=transform(local[None],gm)[0];point,gn,fi,dist=g_trees['wood'].find_nearest(Vector(guess));actual=np.array(point,float)
        target=center+n*.04
        sources.append(actual);targets.append(target);weights.append(weight)
        stations.append({'digit':digit,'skin_face_id':f,'skin_point_cm':center.tolist(),'skin_outward':n.tolist(),
          'actual_gun_surface_before_cm':actual.tolist(),'target_gun_surface_cm':target.tolist(),'initial_skin_reference_gap_cm':distance})
    x=np.array(sources);y=np.array(targets);weights=np.array(weights,float);weights/=weights.sum()
    xc=(x*weights[:,None]).sum(0);yc=(y*weights[:,None]).sum(0)
    u,s,v=np.linalg.svd((x-xc).T@((y-yc)*weights[:,None]));rot=v.T@u.T
    if np.linalg.det(rot)<0:v[-1]*=-1;rot=v.T@u.T
    change=np.eye(4);change[:3,:3]=rot;change[:3,3]=yc-rot@xc
    angle=float(np.degrees(np.arccos(np.clip((np.trace(rot)-1)/2,-1,1))))
    r.update(contact_stations=stations,one_surface_registration_rotation_deg=angle,
      seating_translation_cm=float(np.linalg.norm(change[:3,3])),rigid_change=change.tolist(),
      station_residual_cm=np.linalg.norm(transform(x,change)-y,axis=1).tolist(),no_parameter_grid=True)
    write(OUT/'result.json',r)
    assert angle<20,'Contact registration changes orientation too far; do not continue this fit'
    newgm=change@gm;new,armchecks=arm_targets(b,{'l':change@b['hand_l']},parents)
    skin=np.zeros_like(rest)
    for j,n in enumerate(names):skin+=w[:,j,None]*transform(rest,new[n]@np.linalg.inv(refs[j]))
    skin/=w.sum(1)[:,None];gun=transform(gp,newgm)
    faces={f'{digit}_{side}':np.flatnonzero(np.any((w[:,[names.index(f'{digit}_{i:02}_{side}') for i in (1,2,3)]].sum(1)>0)[tri],axis=1)) for side in ('r','l') for digit in ('thumb','index','middle','ring','pinky')}
    groups={'stock':set(stock_ids),'guard':set(guard_ids),'blade':set(blade_ids)}
    contacts={}
    for digit,fs in faces.items():
        pairs=intersection_pairs(skin,tri[fs],gun,gt);contacts[digit]={group:sorted({int(fs[a]) for a,z in pairs if z in ids}) for group,ids in groups.items()}
    edge=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    e0=np.linalg.norm(p[edge[:,0]]-p[edge[:,1]],axis=1);e1=np.linalg.norm(skin[edge[:,0]]-skin[edge[:,1]],axis=1)
    locals_error={n:tm.angle(encode(np.linalg.inv(new[parents[n]])@new[n])['q'],q) for n,q in old['transferred_digit_local_rotations'].items()}
    assert max(locals_error.values())<.001
    protected_error=float(max(np.max(abs(new[n]-b[n])) for n in old['protected_bones']));assert protected_error<1e-8
    r.update({k:old[k] for k in ('bone_names','parents','mesh_world','before_bones','before_gun_world','protected_bones','transferred_digit_local_rotations','before_contact','local_checks')})
    r.update(after_bones={n:encode(m) for n,m in new.items()},after_gun_world=encode(newgm),
      after_contact=contacts,prior_transfer_contact=old['after_contact'],source_transfer_result_sha256=sha(PREV),
      final_donor_rotation_errors_deg=locals_error,protected_bone_matrix_error=protected_error,
      original_length_support_arm_checks=armchecks,new_severe_edges=int(np.sum((e1>e0*3)&(e1-e0>2))),
      new_index_neighbor_self_pairs_from_transfer=old['new_index_neighbor_self_pairs'],
      actual_gun_origin_motion_cm=float(np.linalg.norm(newgm[:3,3]-gm[:3,3])),
      mechanism='Single weighted opposed actual-pad/wood/blade surface registration, reused digit locals fixed')
    np.savez_compressed(OUT/'geometry.npz',skin=skin,before_skin=saved['before_skin'],skin_triangles=tri,gun_before_cm=saved['gun_before_cm'],gun_after_cm=gun,gun_triangles=gt)
    assert r['new_severe_edges']==0
    r['status']='whole_grasp_reuse_single_surface_seating_requires_visual_review'
except Exception:r['status']='failed_preserved';r['errors'].append(traceback.format_exc())
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','one_surface_registration_rotation_deg','actual_gun_origin_motion_cm','station_residual_cm','new_severe_edges')})
    print('Contact faces',{d:{g:len(v) for g,v in x.items()} for d,x in r.get('after_contact',{}).items()})
