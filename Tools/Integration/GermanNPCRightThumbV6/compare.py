"""Only recorded mature right-thumb local rotations; immutable German gun/grasp."""
import sys, json, struct, traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix, Vector, Quaternion
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,GLB,read,write,row,sha,guards,tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs

BASE=STORE/'Evidence/GermanNPCRightThumbV6'
OUT=BASE/'compare_v1';assert not OUT.exists();OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/result.json'
DATA=PREV.parent/'geometry.npz'
CACHE=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
GERMAN=STORE/'Evidence/WeaponAnimationReuseV1/audit_v1/result.json'
DONOR=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
NAMES=('thumb_01_r','thumb_02_r','thumb_03_r')
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in (PREV,DATA,CACHE,GERMAN,DONOR,GLB,Path(__file__),ROOT/'Tools/Integration/WeaponTriggerAlignmentV2/blender_contact_common.py')],
   'comparisons':[],'formal_selected':False,'source_modified':False,'gun_moved':False,'new_motion':False}
write(OUT/'result.json',r)

def encode(m):
    t,q,s=Matrix(m).decompose();return {'t':list(t),'q':[q.x,q.y,q.z,q.w],'s':list(s)}
def unitrot(m):return m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)
def selfpairs(p):
    pairs=intersection_pairs(p,tri[thumbfaces],p,tri[otherfaces]); result=set()
    for a,b in pairs:
        x,y=int(thumbfaces[a]),int(otherfaces[b])
        if not set(tri[x]).intersection(tri[y]): result.add((min(x,y),max(x,y)))
    return result
def contact(p):
    pairs=intersection_pairs(p,tri[thumbfaces],worldgun,gt)
    whole={int(thumbfaces[a]) for a,b in pairs}; stock={int(thumbfaces[a]) for a,b in pairs if b in stockids}
    pads=p[tri[padfaces]].mean(1); nearest=[top_tree.find_nearest(Vector(v)) for v in pads]
    gap=float(np.mean([v[3] for v in nearest]))
    height=float(np.mean([(p0-np.array(n[0]))@up for p0,n in zip(pads,nearest)]))
    return {'whole_faces':len(whole),'stock_faces':len(stock),'pad_gap_cm':gap,'pad_height_over_upper_stock_cm':height}, whole

try:
    old=read(PREV);cache=read(CACHE);assert not old['errors'] and not cache['errors']
    for e in old['inputs']:assert sha(ROOT/e['path'])==e['sha256']
    gd=read(GERMAN)['models']['german']['ref_local'];od=read(DONOR)['models']['owner']['ref_local']
    basis={n:tm.angle(od[n]['rotation'],gd[n]['rotation']) for n in ('hand_r',*NAMES)}
    assert max(basis.values())<.001; r['source_reference_basis_errors_deg']=basis
    d=np.load(DATA);names=old['bone_names'];parents=old['parents'];rest=d['rest_native_cm'];weights=d['weights'];refs=d['reference_matrices']
    before=d['skin'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles'];gun=old['after_gun_world']
    bones={n:mat(t) for n,t in old['after_bones'].items()}
    # Identify existing GLB stock triangle membership, not a guessed coordinate box.
    blob=GLB.read_bytes();size=struct.unpack_from('<I',blob,12)[0];gltf=json.loads(blob[20:20+size])
    at=0;stockids=set()
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            count=gltf['accessors'][prim['indices']]['count']//3
            if node['name'] in ('Wood_ContinuousStock','Wood_UpperHandguard'):stockids.update(range(at,at+count))
            at+=count
    assert at==len(gt)==24466
    cross=np.cross(gp[gt[:,1]]-gp[gt[:,0]],gp[gt[:,2]]-gp[gt[:,0]])
    gn=cross/np.maximum(np.linalg.norm(cross,axis=1)[:,None],1e-12)
    centers=gp[gt].mean(1);stock=np.array(sorted(stockids),int)
    apex=stock[centers[stock,2]>np.quantile(centers[stock,2],.8)]
    sign=1 if np.mean(gn[apex,2])>0 else -1;gn*=sign
    upper=stock[gn[stock,2]>.5];assert len(upper)>10
    worldgun=transform(gp,mat(gun));up=np.array(tm.rotate(gun['q'],[0,0,1]))
    top_tree=BVHTree.FromPolygons([Vector(v) for v in worldgun],gt[upper].tolist(),all_triangles=True)
    ids=[names.index(n) for n in NAMES];positive=weights[:,ids].sum(1)>0
    thumbfaces=np.flatnonzero(np.any(positive[tri],axis=1))
    other=weights[:,[j for j,n in enumerate(names) if n.startswith(('index_','middle_','ring_','pinky_')) and n.endswith('_r')]].sum(1)>0
    otherfaces=np.flatnonzero(np.any(other[tri],axis=1))
    distal=weights[:,names.index('thumb_03_r')]>.6
    skin_n=-np.cross(before[tri[:,1]]-before[tri[:,0]],before[tri[:,2]]-before[tri[:,0]])
    skin_n/=np.maximum(np.linalg.norm(skin_n,axis=1)[:,None],1e-12)
    padfaces=np.flatnonzero(np.all(distal[tri],axis=1)&((skin_n@up)<-.2));assert len(padfaces)>3
    shared=positive&other; edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    edge0=np.linalg.norm(before[edges[:,0]]-before[edges[:,1]],axis=1)
    baseline,basecross=contact(before); baseself=selfpairs(before)
    r.update(baseline=baseline,baseline_thumb_other_self_pairs=len(baseself),thumb_any_vertices=int(positive.sum()),
        thumb_touching_faces=len(thumbfaces),shared_other_digit_vertices=int(shared.sum()),
        fixed_distal_pad_face_ids=padfaces.tolist(),upper_stock_face_count=len(upper),gun_winding_sign=sign)
    options={}
    for clip in ('owner_idle','owner_reload'):
        for phase,sample in cache['clips'][clip]['samples'].items():
            src={n:mat(v) for n,v in sample['bones_component'].items()};new={n:b.copy() for n,b in bones.items()};locals_q={}
            for n in NAMES:
                p=parents[n];local=np.linalg.inv(bones[p])@bones[n]
                mature=np.linalg.inv(src[p])@src[n]
                local[:3,:3]=unitrot(mature)*np.linalg.norm(local[:3,:3],axis=0)
                new[n]=new[p]@local;locals_q[n]=encode(local)['q']
            after=np.zeros_like(rest)
            for j,n in enumerate(names):after+=weights[:,j,None]*transform(rest,new[n]@np.linalg.inv(refs[j]))
            after/=weights.sum(1)[:,None]
            c,crossings=contact(after);selfset=selfpairs(after)
            edge1=np.linalg.norm(after[edges[:,0]]-after[edges[:,1]],axis=1)
            c.update(identity=clip+'_'+phase,clip=cache['clips'][clip]['asset'],phase_s=float(phase),local_rotations=locals_q,
                true_unaffected_skin_cm=float(np.linalg.norm(after[~positive]-before[~positive],axis=1).max()),
                other_digit_shared_skin_cm=float(np.linalg.norm(after[shared]-before[shared],axis=1).max()) if shared.any() else 0,
                new_thumb_other_self_pairs=len(selfset-baseself),thumb_other_self_pairs=len(selfset),
                new_severe_edges=int(np.sum((edge1>edge0*3)&(edge1-edge0>2))),
                max_extra_edge_cm=float((edge1-edge0).max()))
            c['early_pass']=bool(c['stock_faces']<baseline['stock_faces'] and c['pad_height_over_upper_stock_cm']>baseline['pad_height_over_upper_stock_cm']
                and c['pad_gap_cm']<baseline['pad_gap_cm'] and not c['new_thumb_other_self_pairs'] and not c['new_severe_edges'] and c['true_unaffected_skin_cm']<.0001)
            r['comparisons'].append(c);options[c['identity']]=(new,after);write(OUT/'result.json',r)
    passed=[v for v in r['comparisons'] if v['early_pass']]
    if passed:
        chosen=min(passed,key=lambda x:(x['stock_faces'],x['pad_gap_cm']))
        new,skin=options[chosen['identity']]
        after_bones=dict(old['after_bones'])
        for n in NAMES:after_bones[n]=encode(new[n])
        assert all(after_bones[n]==old['after_bones'][n] for n in names if n not in NAMES)
        r.update(status='existing_thumb_candidate_requires_actual_views',chosen=chosen,
            bone_names=names,parents=parents,before_bones=old['after_bones'],after_bones=after_bones,
            before_gun_world=gun,after_gun_world=gun,mesh_world=old['mesh_world'],
            trigger_pivot_gun_cm=old['trigger_pivot_gun_cm'],stock_pivot_gun_cm=old['stock_pivot_gun_cm'],
            left_palm_target_world_cm=old['left_palm_target_world_cm'],new_severe_edges=chosen['new_severe_edges'])
        np.savez_compressed(OUT/'geometry.npz',skin=skin,before_skin=before,skin_triangles=tri,gun_local_cm=gp,gun_triangles=gt,
            rest_native_cm=rest,weights=weights,reference_matrices=refs)
        write(OUT/'binding.json',{'authorized_bones':list(NAMES),'local_rotations':chosen['local_rotations'],
            'source_asset':chosen['clip'],'phase_s':chosen['phase_s'],'source_cache':row(CACHE),
            'gun_and_other_bones_unchanged':True,'formal_selected':False})
    else:r['status']='no_retained_existing_thumb_sample_passes'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(json.dumps({k:r.get(k) for k in ('status','errors','baseline','chosen','comparisons','guards_after')},indent=2))
