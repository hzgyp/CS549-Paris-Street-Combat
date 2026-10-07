"""Existing mature thumb02/03 grasp only; V9 gun/root/index/arms stay exact."""
import sys,json,struct,traceback
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,GLB,read,write,row,sha,guards,tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs
sys.path.insert(0,str(ROOT/'Tools/Integration/GermanNPCOrderedGripV4'))
from arm_fit import encode

BASE=STORE/'Evidence/GermanNPCThumbCurlV10';OUT=BASE/'distal_reuse_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCScreenRotateV9/extra_two_v1/result.json'
REVIEW=PREV.parent.parent/'review_v1/result.json'
DATA=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
CACHE=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
GERMAN=STORE/'Evidence/WeaponAnimationReuseV1/audit_v1/result.json'
DONOR=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
MARK=Path('C:/Users/hzgyp/AppData/Local/Temp/codex-clipboard-04eb33a3-7413-4975-82ac-c8cf75887de4.png')
paths=(PREV,REVIEW,DATA,CACHE,GERMAN,DONOR,GLB,MARK,Path(__file__),ROOT/'Tools/Integration/WeaponTriggerAlignmentV2/blender_contact_common.py',ROOT/'Tools/Integration/GermanNPCOrderedGripV4/arm_fit.py')
r={'status':'starting','errors':[],'guards_before':guards(),
   'inputs':[row(p) if p.is_relative_to(ROOT) else {'path':str(p),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in paths],
   'formal_selected':False,'source_modified':False,'native_tested':False,'contact_accepted':False,
   'v9_minor_overlap_human_accepted':True,'new_motion':False,'gun_moved':False}
write(OUT/'result.json',r)
CHANGED=('thumb_02_r','thumb_03_r')

def skin(b):
    p=np.zeros_like(rest)
    for j,n in enumerate(names):p+=w[:,j,None]*transform(rest,b[n]@np.linalg.inv(refs[j]))
    return p/w.sum(1)[:,None]

def contact(p):
    pairs=intersection_pairs(p,tri[thumbfaces],wg,gt)
    whole={int(thumbfaces[a]) for a,b in pairs};wood={int(thumbfaces[a]) for a,b in pairs if b in stockids}
    distalwood={int(thumbfaces[a]) for a,b in pairs if b in stockids and int(thumbfaces[a]) in distalfaces}
    pads=p[tri[padfaces]].mean(1);nearest=[top_tree.find_nearest(Vector(v)) for v in pads]
    return {'whole_thumb_crossing_faces':len(whole),'thumb_stock_crossing_faces':len(wood),
            'distal_stock_crossing_face_ids':sorted(distalwood),
            'mean_distal_pad_gap_cm':float(np.mean([n[3] for n in nearest])),
            'min_distal_pad_gap_cm':float(min(n[3] for n in nearest)),
            'mean_pad_height_over_stock_cm':float(np.mean([(v-np.array(n[0]))@up for v,n in zip(pads,nearest)]))}

def selfpairs(p):
    result=set()
    for a,b in intersection_pairs(p,tri[thumbfaces],p,tri[otherfaces]):
        x,y=int(thumbfaces[a]),int(otherfaces[b])
        if not set(tri[x]).intersection(tri[y]):result.add((min(x,y),max(x,y)))
    return result

try:
    old=read(PREV);checked=read(REVIEW);cache=read(CACHE)
    assert not old['errors'] and not checked['errors'] and not cache['errors']
    assert old['cumulative_rotation_deg']==6
    for receipt in (old,checked):
        for e in receipt['inputs']:assert sha(ROOT/e['path'])==e['sha256']
    d=np.load(DATA);names=old['bone_names'];parents=old['parents'];w=d['weights'];rest=d['rest_native_cm'];refs=d['reference_matrices'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles']
    bones={n:mat(v) for n,v in old['after_bones'].items()};p0=skin(bones);gun=old['after_gun_world'];wg=transform(gp,mat(gun))
    shown=np.load(REVIEW.parent/'diagnostic_geometry.npz')
    r['v9_reproduction_skin_cm']=float(np.linalg.norm(p0-shown['skin'],axis=1).max())
    r['v9_reproduction_gun_cm']=float(np.linalg.norm(wg-shown['gun_after_cm'],axis=1).max())
    assert max(r['v9_reproduction_skin_cm'],r['v9_reproduction_gun_cm'])<.0001
    gd=read(GERMAN)['models']['german']['ref_local'];od=read(DONOR)['models']['owner']['ref_local']
    basis={n:tm.angle(od[n]['rotation'],gd[n]['rotation']) for n in ('thumb_01_r',*CHANGED)}
    assert max(basis.values())<.001;r['source_reference_basis_errors_deg']=basis
    blob=GLB.read_bytes();size=struct.unpack_from('<I',blob,12)[0];gltf=json.loads(blob[20:20+size]);at=0;stockids=set()
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            count=gltf['accessors'][prim['indices']]['count']//3
            if node['name'] in ('Wood_ContinuousStock','Wood_UpperHandguard'):stockids.update(range(at,at+count))
            at+=count
    assert at==len(gt)==24466
    gn=np.cross(gp[gt[:,1]]-gp[gt[:,0]],gp[gt[:,2]]-gp[gt[:,0]]);gn/=np.maximum(np.linalg.norm(gn,axis=1)[:,None],1e-12)
    centers=gp[gt].mean(1);stock=np.array(sorted(stockids),int);apex=stock[centers[stock,2]>np.quantile(centers[stock,2],.8)]
    sign=1 if np.mean(gn[apex,2])>0 else -1;gn*=sign;upper=stock[gn[stock,2]>.5]
    up=np.array(tm.rotate(gun['q'],[0,0,1]));top_tree=BVHTree.FromPolygons([Vector(v) for v in wg],gt[upper].tolist(),all_triangles=True)
    ids=[names.index(n) for n in CHANGED];positive=w[:,ids].sum(1)>0
    allthumb=w[:,[names.index(n) for n in ('thumb_01_r',*CHANGED)]].sum(1)>0
    thumbfaces=np.flatnonzero(np.any(allthumb[tri],axis=1))
    other=w[:,[j for j,n in enumerate(names) if n.startswith(('index_','middle_','ring_','pinky_')) and n.endswith('_r')]].sum(1)>0
    otherfaces=np.flatnonzero(np.any(other[tri],axis=1));shared=positive&other
    distal=w[:,names.index('thumb_03_r')]>.6
    sn=-np.cross(p0[tri[:,1]]-p0[tri[:,0]],p0[tri[:,2]]-p0[tri[:,0]]);sn/=np.maximum(np.linalg.norm(sn,axis=1)[:,None],1e-12)
    distalfaces=set(np.flatnonzero(np.all(distal[tri],axis=1)).tolist())
    padfaces=np.flatnonzero(np.all(distal[tri],axis=1)&((sn@up)<-.2));assert len(padfaces)>3
    sample=cache['clips']['owner_reload']['samples']['2.2'];src={n:mat(v) for n,v in sample['bones_component'].items()}
    new={n:b.copy() for n,b in bones.items()};after_bones=dict(old['after_bones']);qlocals={};angles={};ts={}
    for n in CHANGED:
        parent=parents[n];local=np.linalg.inv(bones[parent])@bones[n];mature=np.linalg.inv(src[parent])@src[n]
        oldlocal=local.copy();local[:3,:3]=mature[:3,:3]/np.linalg.norm(mature[:3,:3],axis=0)*np.linalg.norm(local[:3,:3],axis=0)
        new[n]=new[parent]@local;after_bones[n]=encode(new[n]);qlocals[n]=encode(local)['q']
        angles[n]=tm.angle(encode(oldlocal)['q'],qlocals[n]);ts[n]={'translation_error_cm':float(np.max(abs(local[:3,3]-oldlocal[:3,3]))),'scale_error':float(np.max(abs(np.linalg.norm(local[:3,:3],axis=0)-np.linalg.norm(oldlocal[:3,:3],axis=0))))}
    assert max(angles.values())<30
    p1=skin(new);baseline=contact(p0);final=contact(p1);bs=selfpairs(p0);fs=selfpairs(p1)
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    e0=np.linalg.norm(p0[edges[:,0]]-p0[edges[:,1]],axis=1);e1=np.linalg.norm(p1[edges[:,0]]-p1[edges[:,1]],axis=1);move=np.linalg.norm(p1-p0,axis=1)
    index=w[:,[names.index(n) for n in ('index_02_r','index_03_r')]].sum(1)>0
    protected=[n for n in names if n not in CHANGED]
    r.update(baseline=baseline,after_contact=final,changed_local_rotation_deg=angles,local_rotations=qlocals,
      source_clip=cache['clips']['owner_reload']['asset'],source_phase_s=2.2,local_translation_scale_checks=ts,
      true_zero_changed_influence_skin_cm=float(move[~positive].max()),actual_distal_index_skin_cm=float(move[index].max()),
      shared_other_digit_vertices=int(shared.sum()),shared_other_digit_skin_cm=float(move[shared].max()) if shared.any() else 0,
      new_thumb_other_self_pairs=len(fs-bs),before_self_pairs=len(bs),after_self_pairs=len(fs),
      new_distal_stock_crossing_faces=sorted(set(final['distal_stock_crossing_face_ids'])-set(baseline['distal_stock_crossing_face_ids'])),
      new_severe_edges=int(np.sum((e1>e0*3)&(e1-e0>2))),max_extra_skin_edge_cm=float((e1-e0).max()),
      protected_bone_matrix_error=float(max(np.max(abs(new[n]-bones[n])) for n in protected)),
      bone_names=names,parents=parents,before_bones=old['after_bones'],after_bones=after_bones,
      before_gun_world=gun,after_gun_world=gun,mesh_world=old['mesh_world'],protected_bones=protected,
      fixed_distal_pad_face_ids=padfaces.tolist(),source_model_weights_actions_modified=False)
    assert all(after_bones[n]==old['after_bones'][n] for n in protected)
    np.savez_compressed(OUT/'diagnostic_geometry.npz',skin=p1,before_skin=p0,skin_triangles=tri,gun_before_cm=wg,gun_after_cm=wg,gun_triangles=gt)
    write(OUT/'result.json',r)
    assert r['protected_bone_matrix_error']==0 and max(r['true_zero_changed_influence_skin_cm'],r['actual_distal_index_skin_cm'])<.0001
    assert not r['new_severe_edges'] and not r['new_thumb_other_self_pairs'] and not r['new_distal_stock_crossing_faces']
    assert final['mean_distal_pad_gap_cm']<baseline['mean_distal_pad_gap_cm']
    r['status']='distal_existing_grasp_candidate_requires_actual_views'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(json.dumps({k:r.get(k) for k in ('status','errors','baseline','after_contact','changed_local_rotation_deg','new_distal_stock_crossing_faces','new_thumb_other_self_pairs','new_severe_edges')},indent=2))
