"""One closest actual-pad/blade pair; same complete mature index rotations."""
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
from arm_fit import encode,arm_targets
BASE=STORE/'Evidence/GermanNPCIndexGripV12';OUT=BASE/'paired_surface_v3'
assert not OUT.exists();OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCLowerGripV11/source_frame_v4/result.json'
OLD=BASE/'complete_existing_grasp_v2/result.json';VIEW=BASE/'root_limit_views_v1/result.json'
DATA=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz';CACHE=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
paths=(PREV,OLD,VIEW,DATA,CACHE,GLB,Path(__file__),ROOT/'Tools/Integration/GermanNPCOrderedGripV4/arm_fit.py',ROOT/'Tools/Integration/WeaponTriggerAlignmentV2/blender_contact_common.py')
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in paths],
   'lower_three_human_accepted_visual_only':True,'formal_selected':False,'source_modified':False,
   'native_tested':False,'contact_accepted':False,'new_motion':False}
write(OUT/'result.json',r)
try:
    old=read(PREV);v2=read(OLD);view=read(VIEW);assert view['status']=='over_limit_existing_grasp_failure_reconstructed_not_selected'
    for receipt in (old,v2,view):
        for e in receipt['inputs']:assert sha(ROOT/e['path'])==e['sha256']
    d=np.load(DATA);names=old['bone_names'];parents=old['parents'];w=d['weights'];rest=d['rest_native_cm'];refs=d['reference_matrices'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles']
    def skin(b):
        out=np.zeros_like(rest)
        for j,n in enumerate(names):out+=w[:,j,None]*transform(rest,b[n]@np.linalg.inv(refs[j]))
        return out/w.sum(1)[:,None]
    bones={n:mat(v) for n,v in old['after_bones'].items()};new={n:m.copy() for n,m in bones.items()};p0=skin(bones)
    cache=read(CACHE);sample=next(s for t,s in cache['clips']['owner_reload']['samples'].items() if float(t)==2.2);src={n:mat(v) for n,v in sample['bones_component'].items()}
    index=tuple('index_'+i+'_r' for i in ('01','02','03'));localchecks={};turns={}
    for n in index:
        p=parents[n];local=np.linalg.inv(bones[p])@bones[n];original=local.copy();donor=np.linalg.inv(src[p])@src[n]
        local[:3,:3]=donor[:3,:3]/np.linalg.norm(donor[:3,:3],axis=0)*np.linalg.norm(local[:3,:3],axis=0);new[n]=new[p]@local
        localchecks[n]={'translation_error_cm':float(np.max(abs(local[:3,3]-original[:3,3]))),'scale_error':float(np.max(abs(np.linalg.norm(local[:3,:3],axis=0)-np.linalg.norm(original[:3,:3],axis=0))))}
        turns[n]=tm.angle(encode(local)['q'],encode(original)['q'])
    curved=skin(new);g0=old['after_gun_world'];gm=mat(g0);wg0=transform(gp,gm)
    blob=GLB.read_bytes();gltf=json.loads(blob[20:20+struct.unpack_from('<I',blob,12)[0]]);at=0;groups={'stock':set(),'guard':set(),'blade':set(),'whole':set(range(len(gt)))}
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            count=gltf['accessors'][prim['indices']]['count']//3;ids=set(range(at,at+count))
            if node['name'].startswith('Wood_'):groups['stock']|=ids
            if node['name'].startswith('Guard_'):groups['guard']|=ids
            if node['name']=='Trigger_Donor':groups['blade']|=ids
            at+=count
    assert at==len(gt)==24466
    pull=gm[:3,1]/np.linalg.norm(gm[:3,1]);gn=np.cross(wg0[gt[:,1]]-wg0[gt[:,0]],wg0[gt[:,2]]-wg0[gt[:,0]]);gn/=np.maximum(np.linalg.norm(gn,axis=1)[:,None],1e-12)
    front=np.array([f for f in sorted(groups['blade']) if gn[f]@pull>.7]);assert len(front)>=2
    fronttree=BVHTree.FromPolygons([Vector(v) for v in wg0],gt[front].tolist(),all_triangles=True)
    distal=w[:,names.index('index_03_r')]>.6;df=np.flatnonzero(np.all(distal[tri],axis=1))
    sn=-np.cross(curved[tri[:,1]]-curved[tri[:,0]],curved[tri[:,2]]-curved[tri[:,0]]);sn/=np.maximum(np.linalg.norm(sn,axis=1)[:,None],1e-12)
    pf=df[(sn[df]@pull)<-.25];assert len(pf)>=4
    # Correspondence over actual surfaces, not parameter/pose/offset fitting.
    nearest=[]
    for f in pf:
        center=curved[tri[f]].mean(0);pt,n,fi,dist=fronttree.find_nearest(Vector(center))
        if sn[f]@np.array(n)<-.25:nearest.append((dist,int(f),center,np.array(pt,float),np.array(n,float),int(front[fi])))
    dist,f,center,blade,normal,bf=min(nearest,key=lambda v:v[0])
    local_patch=pf[np.linalg.norm(curved[tri[pf]].mean(1)-center,axis=1)<=.5]
    vertices=np.unique(tri[local_patch]);patch=curved[vertices]
    support=center+normal*float(np.min((patch-center)@normal));delta=support-normal*.1-blade
    r.update(actual_pad_face_ids=local_patch.tolist(),actual_pad_vertex_ids=vertices.tolist(),contact_skin_face_id=f,contact_trigger_face_id=bf,
      contact_skin_center_cm=center.tolist(),contact_trigger_before_cm=blade.tolist(),contact_trigger_outward=normal.tolist(),
      actual_paired_surface_distance_cm=float(dist),gun_translation_world_cm=delta.tolist(),gun_translation_cm=float(np.linalg.norm(delta)),
      source_clip=cache['clips']['owner_reload']['asset'],source_phase_s=2.2,index_local_rotation_deltas_deg=turns,
      index_local_translation_scale_checks=localchecks,index_chain_turn_after_deg=v2['index_chain_turn_after_deg'],gun_angle_scale_unchanged=True)
    write(OUT/'result.json',r);assert np.linalg.norm(delta)<=4
    g1=dict(g0);g1['t']=(np.array(g0['t'])+delta).tolist();wg1=transform(gp,mat(g1));change=mat(g1)@np.linalg.inv(gm)
    new,armchecks=arm_targets(new,{'l':change@new['hand_l']},parents);p1=skin(new)
    faces={digit:np.flatnonzero(np.any((w[:,[names.index(digit+'_'+i+'_r') for i in ('01','02','03')]].sum(1)>0)[tri],axis=1)) for digit in ('thumb','index','middle','ring','pinky')}
    def contact(p,g):
        wood=BVHTree.FromPolygons([Vector(v) for v in g],gt[sorted(groups['stock'])].tolist(),all_triangles=True);out={}
        for digit,fs in faces.items():
            pairs=intersection_pairs(p,tri[fs],g,gt);out[digit]={group:sorted({int(fs[a]) for a,b in pairs if b in ids}) for group,ids in groups.items()}
            if digit in old['fixed_pad_face_ids']:out[digit]['pad_mean_stock_gap_cm']=float(np.mean([wood.find_nearest(Vector(v))[3] for v in p[tri[old['fixed_pad_face_ids'][digit]]].mean(1)]))
        return out
    def selfpairs(p):
        pairs=set()
        for digit in ('thumb','middle','ring','pinky'):
            for a,b in intersection_pairs(p,tri[faces['index']],p,tri[faces[digit]]):
                x,y=int(faces['index'][a]),int(faces[digit][b])
                if not set(tri[x]).intersection(tri[y]):pairs.add((min(x,y),max(x,y)))
        return pairs
    bc,ac=contact(p0,wg0),contact(p1,wg1);bs,ss=selfpairs(p0),selfpairs(p1)
    left=[n for n in names if n.endswith('_l') and n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))];affected=[*index,*left];protected=[n for n in names if n not in affected]
    output=dict(old['after_bones'])
    for n in affected:output[n]=encode(new[n])
    edge=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);e0=np.linalg.norm(p0[edge[:,0]]-p0[edge[:,1]],axis=1);e1=np.linalg.norm(p1[edge[:,0]]-p1[edge[:,1]],axis=1)
    eligible=w[:,[names.index(n) for n in affected]].sum(1)>0;move=np.linalg.norm(p1-p0,axis=1)
    im=w[:,[names.index('index_02_r'),names.index('index_03_r')]].sum(1)>0;dfs=np.flatnonzero(np.any(im[tri],axis=1));pairs=intersection_pairs(p1,tri[dfs],wg1,gt)
    dc={group:sorted({int(dfs[a]) for a,b in pairs if b in groups[group]}) for group in ('stock','guard','blade')}
    blade=BVHTree.FromPolygons([Vector(v) for v in wg1],gt[sorted(groups['blade'])].tolist(),all_triangles=True);gaps=[blade.find_nearest(Vector(v))[3] for v in p1[tri[local_patch]].mean(1)]
    r.update(before_contact=bc,after_contact=ac,actual_distal_index_crossing_faces=dc,actual_pad_mean_blade_gap_cm=float(np.mean(gaps)),actual_pad_min_blade_gap_cm=float(min(gaps)),
      new_index_neighbor_self_pairs=len(ss-bs),before_index_neighbor_self_pairs=len(bs),after_index_neighbor_self_pairs=len(ss),new_severe_edges=int(np.sum((e1>e0*3)&(e1-e0>2))),
      max_extra_skin_edge_cm=float(np.max(e1-e0)),protected_bone_matrix_error=float(max(np.max(abs(new[n]-bones[n])) for n in protected)),true_zero_changed_influence_skin_cm=float(move[~eligible].max()),
      original_length_arm_checks=armchecks,bone_names=names,parents=parents,before_bones=old['after_bones'],after_bones=output,before_gun_world=g0,after_gun_world=g1,mesh_world=old['mesh_world'],
      protected_bones=protected,authorized_bones=affected,source_model_weights_actions_modified=False,
      all_other_right_digit_local_error=float(max(np.max(abs(np.linalg.inv(new[parents[n]])@new[n]-np.linalg.inv(bones[parents[n]])@bones[n])) for n in names if n.endswith('_r') and n.startswith(('thumb_','middle_','ring_','pinky_')))),
      left_digit_local_error=float(max(np.max(abs(np.linalg.inv(new[parents[n]])@new[n]-np.linalg.inv(bones[parents[n]])@bones[n])) for n in left if n.startswith(('thumb_','index_','middle_','ring_','pinky_')))))
    np.savez_compressed(OUT/'diagnostic_geometry.npz',skin=p1,before_skin=p0,skin_triangles=tri,gun_before_cm=wg0,gun_after_cm=wg1,gun_triangles=gt);write(OUT/'result.json',r)
    assert not r['new_severe_edges'] and not r['new_index_neighbor_self_pairs']
    assert not dc['stock'] and not dc['guard'] and not dc['blade'],'Distal finger still crosses actual gun'
    assert r['actual_pad_mean_blade_gap_cm']<=.3
    r['status']='paired_surface_index_gun_requires_actual_views'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(json.dumps({k:r.get(k) for k in ('status','errors','gun_translation_cm','actual_pad_mean_blade_gap_cm','actual_distal_index_crossing_faces','new_index_neighbor_self_pairs','new_severe_edges')},indent=2))
