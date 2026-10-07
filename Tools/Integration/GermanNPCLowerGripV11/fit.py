"""ONE existing mature three-finger grasp; gun/accepted thumb/index bones protected."""
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
BASE=STORE/'Evidence/GermanNPCLowerGripV11';OUT=BASE/'mature_reuse_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCThumbCurlV10/surface_limit_v2/result.json';REVIEW=PREV.parent.parent/'review_v1/result.json'
DATA=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
CACHE=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
GERMAN=STORE/'Evidence/WeaponAnimationReuseV1/audit_v1/result.json';DONOR=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
MARK=Path('C:/Users/hzgyp/AppData/Local/Temp/codex-clipboard-bb268e54-4897-42a1-8a24-6d3c3e28a628.png')
paths=(PREV,REVIEW,DATA,CACHE,GERMAN,DONOR,GLB,MARK,Path(__file__),ROOT/'Tools/Integration/WeaponTriggerAlignmentV2/blender_contact_common.py',ROOT/'Tools/Integration/GermanNPCOrderedGripV4/arm_fit.py')
r={'status':'starting','errors':[],'guards_before':guards(),
   'inputs':[row(p) if p.is_relative_to(ROOT) else {'path':str(p),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in paths],
   'formal_selected':False,'source_modified':False,'native_tested':False,'contact_accepted':False,
   'v10_thumb_human_accepted':True,'new_motion':False,'gun_moved':False}
write(OUT/'result.json',r)
DIGITS=('middle','ring','pinky');CHANGED=tuple(d+'_'+i+'_r' for d in DIGITS for i in ('01','02','03'))

def skin(b):
    p=np.zeros_like(rest)
    for j,n in enumerate(names):p+=w[:,j,None]*transform(rest,b[n]@np.linalg.inv(refs[j]))
    return p/w.sum(1)[:,None]

def contacts(p):
    out={}
    for digit,faces in digitfaces.items():
        pairs=intersection_pairs(p,tri[faces],wg,gt)
        crossing=sorted({int(faces[a]) for a,b in pairs});wood=sorted({int(faces[a]) for a,b in pairs if b in stockids})
        pads=p[tri[padfaces[digit]]].mean(1);near=[stocktree.find_nearest(Vector(v)) for v in pads]
        out[digit]={'whole_crossing_face_ids':crossing,'stock_crossing_face_ids':wood,
            'pad_mean_gap_cm':float(np.mean([n[3] for n in near])),'pad_min_gap_cm':float(min(n[3] for n in near)),
            'pad_faces_under_0p3_cm':int(sum(n[3]<=.3 for n in near)),'pad_face_count':len(near)}
    return out

def selfpairs(p):
    result=set()
    for digit,faces in digitfaces.items():
        for other,ofaces in allrightfaces.items():
            if digit==other:continue
            for a,b in intersection_pairs(p,tri[faces],p,tri[ofaces]):
                x,y=int(faces[a]),int(ofaces[b])
                if not set(tri[x]).intersection(tri[y]):result.add((min(x,y),max(x,y)))
    return result

try:
    old=read(PREV);checked=read(REVIEW);cache=read(CACHE)
    assert not old['errors'] and not checked['errors'] and not cache['errors']
    for receipt in (old,checked):
        for e in receipt['inputs']:assert sha(ROOT/e['path'])==e['sha256']
    d=np.load(DATA);names=old['bone_names'];parents=old['parents'];w=d['weights'];rest=d['rest_native_cm'];refs=d['reference_matrices'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles']
    bones={n:mat(v) for n,v in old['after_bones'].items()};p0=skin(bones);gun=old['after_gun_world'];wg=transform(gp,mat(gun))
    shown=np.load(REVIEW.parent/'diagnostic_geometry.npz')
    r['v10_reproduction_skin_cm']=float(np.linalg.norm(p0-shown['skin'],axis=1).max());r['v10_reproduction_gun_cm']=float(np.linalg.norm(wg-shown['gun_after_cm'],axis=1).max())
    assert max(r['v10_reproduction_skin_cm'],r['v10_reproduction_gun_cm'])<.0001
    gd=read(GERMAN)['models']['german']['ref_local'];od=read(DONOR)['models']['owner']['ref_local'];basis={n:tm.angle(od[n]['rotation'],gd[n]['rotation']) for n in CHANGED}
    assert max(basis.values())<.001;r['source_reference_basis_errors_deg']=basis
    blob=GLB.read_bytes();size=struct.unpack_from('<I',blob,12)[0];gltf=json.loads(blob[20:20+size]);at=0;stockids=set()
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            count=gltf['accessors'][prim['indices']]['count']//3
            if node['name'] in ('Wood_ContinuousStock','Wood_UpperHandguard'):stockids.update(range(at,at+count))
            at+=count
    assert at==len(gt)==24466
    stock=np.array(sorted(stockids),int);stocktree=BVHTree.FromPolygons([Vector(v) for v in wg],gt[stock].tolist(),all_triangles=True)
    ids=[names.index(n) for n in CHANGED];positive=w[:,ids].sum(1)>0
    sn=-np.cross(p0[tri[:,1]]-p0[tri[:,0]],p0[tri[:,2]]-p0[tri[:,0]]);sn/=np.maximum(np.linalg.norm(sn,axis=1)[:,None],1e-12)
    allrightfaces={};digitfaces={};padfaces={}
    for digit in ('thumb','index',*DIGITS):
        mask=w[:,[names.index(digit+'_'+i+'_r') for i in ('01','02','03')]].sum(1)>0
        faces=np.flatnonzero(np.any(mask[tri],axis=1));allrightfaces[digit]=faces
        if digit not in DIGITS:continue
        digitfaces[digit]=faces
        distal=w[:,names.index(digit+'_03_r')]>.6;df=np.flatnonzero(np.all(distal[tri],axis=1))
        centers=p0[tri[df]].mean(1);loc=np.array([stocktree.find_nearest(Vector(v))[0] for v in centers]);toward=loc-centers;toward/=np.maximum(np.linalg.norm(toward,axis=1)[:,None],1e-12)
        padfaces[digit]=df[np.einsum('ij,ij->i',sn[df],toward)>.2];assert len(padfaces[digit])>=4,(digit,len(padfaces[digit]))
    sample=cache['clips']['owner_reload']['samples']['2.2'];src={n:mat(v) for n,v in sample['bones_component'].items()}
    new={n:b.copy() for n,b in bones.items()};after_bones=dict(old['after_bones']);qlocals={};angles={};ts={}
    for n in CHANGED:
        parent=parents[n];local=np.linalg.inv(bones[parent])@bones[n];oldlocal=local.copy();mature=np.linalg.inv(src[parent])@src[n]
        local[:3,:3]=mature[:3,:3]/np.linalg.norm(mature[:3,:3],axis=0)*np.linalg.norm(local[:3,:3],axis=0)
        new[n]=new[parent]@local;after_bones[n]=encode(new[n]);qlocals[n]=encode(local)['q'];angles[n]=tm.angle(encode(oldlocal)['q'],qlocals[n])
        ts[n]={'translation_error_cm':float(np.max(abs(local[:3,3]-oldlocal[:3,3]))),'scale_error':float(np.max(abs(np.linalg.norm(local[:3,:3],axis=0)-np.linalg.norm(oldlocal[:3,:3],axis=0))))}
    p1=skin(new);before=contacts(p0);after=contacts(p1);bs=selfpairs(p0);fs=selfpairs(p1)
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);e0=np.linalg.norm(p0[edges[:,0]]-p0[edges[:,1]],axis=1);e1=np.linalg.norm(p1[edges[:,0]]-p1[edges[:,1]],axis=1);move=np.linalg.norm(p1-p0,axis=1)
    im=w[:,[names.index('index_'+i+'_r') for i in ('01','02','03')]].sum(1)>0;ix=w[:,[names.index('index_'+i+'_r') for i in ('02','03')]].sum(1)>0;th=w[:,[names.index('thumb_'+i+'_r') for i in ('01','02','03')]].sum(1)>0
    protected=[n for n in names if n not in CHANGED];newcross={di:sorted(set(after[di]['whole_crossing_face_ids'])-set(before[di]['whole_crossing_face_ids'])) for di in DIGITS}
    r.update(before_contact=before,after_contact=after,changed_local_rotation_deg=angles,local_rotations=qlocals,local_translation_scale_checks=ts,
      source_clip=cache['clips']['owner_reload']['asset'],source_phase_s=2.2,
      true_zero_changed_influence_skin_cm=float(move[~positive].max()),actual_distal_index_skin_cm=float(move[ix].max()),accepted_thumb_skin_cm=float(move[th].max()),
      shared_index_boundary=[{'vertex_id':int(i),'motion_cm':float(move[i])} for i in np.flatnonzero(im&positive)],
      new_lower_digit_gun_crossing_face_ids=newcross,new_finger_self_pairs=len(fs-bs),before_finger_self_pairs=len(bs),after_finger_self_pairs=len(fs),
      new_severe_edges=int(np.sum((e1>e0*3)&(e1-e0>2))),max_extra_skin_edge_cm=float((e1-e0).max()),
      protected_bone_matrix_error=float(max(np.max(abs(new[n]-bones[n])) for n in protected)),
      bone_names=names,parents=parents,before_bones=old['after_bones'],after_bones=after_bones,before_gun_world=gun,after_gun_world=gun,
      mesh_world=old['mesh_world'],protected_bones=protected,authorized_bones=list(CHANGED),fixed_pad_face_ids={di:f.tolist() for di,f in padfaces.items()},source_model_weights_actions_modified=False)
    assert all(after_bones[n]==old['after_bones'][n] for n in protected)
    np.savez_compressed(OUT/'diagnostic_geometry.npz',skin=p1,before_skin=p0,skin_triangles=tri,gun_before_cm=wg,gun_after_cm=wg,gun_triangles=gt)
    write(OUT/'result.json',r)
    assert r['protected_bone_matrix_error']==0 and max(r['true_zero_changed_influence_skin_cm'],r['actual_distal_index_skin_cm'],r['accepted_thumb_skin_cm'])<.0001
    assert not r['new_severe_edges'] and not r['new_finger_self_pairs'] and not any(newcross.values())
    assert all(after[di]['pad_mean_gap_cm']<=.3 for di in DIGITS),'Source grasp does not seat all three actual pads'
    r['status']='mature_lower_grasp_candidate_requires_actual_views'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(json.dumps({k:r.get(k) for k in ('status','errors','before_contact','after_contact','new_finger_self_pairs','new_severe_edges','shared_index_boundary')},indent=2))
