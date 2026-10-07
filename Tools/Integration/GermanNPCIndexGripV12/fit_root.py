"""One complete existing-grasp index pose and actual-surface gun translation."""
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
BASE=STORE/'Evidence/GermanNPCIndexGripV12';OUT=BASE/'complete_existing_grasp_v2'
assert not OUT.exists();OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCLowerGripV11/source_frame_v4/result.json'
PROBE=BASE/'source_probe_v1/result.json';DATA=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
CACHE=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
paths=(PREV,PROBE,DATA,CACHE,GLB,Path(__file__),ROOT/'Tools/Integration/GermanNPCOrderedGripV4/arm_fit.py',ROOT/'Tools/Integration/WeaponTriggerAlignmentV2/blender_contact_common.py')
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in paths],
   'lower_three_human_accepted_visual_only':True,'formal_selected':False,'source_modified':False,
   'native_tested':False,'contact_accepted':False,'new_motion':False}
write(OUT/'result.json',r)
DIGITS=('thumb','index','middle','ring','pinky');INDEX=tuple('index_'+i+'_r' for i in ('01','02','03'))
def skin(b):
    out=np.zeros_like(rest)
    for j,n in enumerate(names):out+=w[:,j,None]*transform(rest,b[n]@np.linalg.inv(refs[j]))
    return out/w.sum(1)[:,None]
def contacts(p,g):
    out={};woodtree=BVHTree.FromPolygons([Vector(v) for v in g],gt[sorted(groups['stock'])].tolist(),all_triangles=True)
    for digit,fs in faces.items():
        cross=intersection_pairs(p,tri[fs],g,gt);out[digit]={}
        for group,gids in groups.items():out[digit][group]=sorted({int(fs[a]) for a,b in cross if b in gids})
        if digit in old['fixed_pad_face_ids']:
            pads=p[tri[old['fixed_pad_face_ids'][digit]]].mean(1)
            out[digit]['pad_mean_stock_gap_cm']=float(np.mean([woodtree.find_nearest(Vector(v))[3] for v in pads]))
    return out
def finger_self(p):
    pairs=set()
    for digit in ('thumb','middle','ring','pinky'):
        for a,b in intersection_pairs(p,tri[faces['index']],p,tri[faces[digit]]):
            x,y=int(faces['index'][a]),int(faces[digit][b])
            if not set(tri[x]).intersection(tri[y]):pairs.add((min(x,y),max(x,y)))
    return pairs
try:
    old=read(PREV);probe=read(PROBE);assert not probe['errors']
    for receipt in (old,probe):
        for e in receipt['inputs']:assert sha(ROOT/e['path'])==e['sha256']
    d=np.load(DATA);names=old['bone_names'];parents=old['parents'];w=d['weights'];rest=d['rest_native_cm'];refs=d['reference_matrices'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles']
    bones={n:mat(v) for n,v in old['after_bones'].items()};p0=skin(bones);g0=old['after_gun_world'];gm=mat(g0);wg0=transform(gp,gm)
    cache=read(CACHE);sample=next(s for phase,s in cache['clips']['owner_reload']['samples'].items() if float(phase)==2.2)
    source={n:mat(v) for n,v in sample['bones_component'].items()}
    new={n:m.copy() for n,m in bones.items()};localchecks={};localturn={}
    for n in INDEX:
        parent=parents[n];local=np.linalg.inv(bones[parent])@bones[n];local0=local.copy();donor=np.linalg.inv(source[parent])@source[n]
        local[:3,:3]=donor[:3,:3]/np.linalg.norm(donor[:3,:3],axis=0)*np.linalg.norm(local0[:3,:3],axis=0)
        new[n]=new[parent]@local
        localchecks[n]={'translation_error_cm':float(np.max(abs(local[:3,3]-local0[:3,3]))),
          'scale_error':float(np.max(abs(np.linalg.norm(local[:3,:3],axis=0)-np.linalg.norm(local0[:3,:3],axis=0))))}
        localturn[n]=tm.angle(encode(local0)['q'],encode(local)['q'])
    curlskin=skin(new)
    blob=GLB.read_bytes();gltf=json.loads(blob[20:20+struct.unpack_from('<I',blob,12)[0]]);at=0;groups={'stock':set(),'guard':set(),'blade':set(),'whole':set(range(len(gt)))}
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            count=gltf['accessors'][prim['indices']]['count']//3;ids=set(range(at,at+count))
            if node['name'].startswith('Wood_'):groups['stock']|=ids
            if node['name'].startswith('Guard_'):groups['guard']|=ids
            if node['name']=='Trigger_Donor':groups['blade']|=ids
            at+=count
    assert at==len(gt)==24466 and len(groups['blade'])==188
    faces={}
    for digit in DIGITS:
        mask=w[:,[names.index(digit+'_'+i+'_r') for i in ('01','02','03')]].sum(1)>0
        faces[digit]=np.flatnonzero(np.any(mask[tri],axis=1))
    pull=gm[:3,1]/np.linalg.norm(gm[:3,1]);gn=np.cross(wg0[gt[:,1]]-wg0[gt[:,0]],wg0[gt[:,2]]-wg0[gt[:,0]])
    gn/=np.maximum(np.linalg.norm(gn,axis=1)[:,None],1e-12)
    firing=np.array([f for f in sorted(groups['blade']) if gn[f]@pull>.7],int);assert len(firing)>=2
    distal=w[:,names.index('index_03_r')]>.6;df=np.flatnonzero(np.all(distal[tri],axis=1))
    sn=-np.cross(curlskin[tri[:,1]]-curlskin[tri[:,0]],curlskin[tri[:,2]]-curlskin[tri[:,0]]);sn/=np.maximum(np.linalg.norm(sn,axis=1)[:,None],1e-12)
    padfaces=df[(sn[df]@pull)<-.25];assert len(padfaces)>=4,('No inward actual pad patch',len(padfaces))
    padvertices=np.unique(tri[padfaces]);patch=curlskin[padvertices];pad=patch.mean(0)
    ftree=BVHTree.FromPolygons([Vector(v) for v in wg0],gt[firing].tolist(),all_triangles=True)
    blade,nor,face,dist=ftree.find_nearest(Vector(pad));blade=np.array(blade,float);normal=np.array(nor,float)
    assert normal@pull>.7
    support=pad+normal*float(np.min((patch-pad)@normal));delta=support-normal*.1-blade
    a=new[INDEX[1]][:3,3]-new[INDEX[0]][:3,3];c=new[INDEX[2]][:3,3]-new[INDEX[1]][:3,3]
    turn=float(np.degrees(np.arccos(np.clip(a@c/(np.linalg.norm(a)*np.linalg.norm(c)),-1,1))))
    r.update(actual_pad_face_ids=padfaces.tolist(),actual_pad_vertex_ids=padvertices.tolist(),
      trigger_front_face_id=int(firing[face]),trigger_front_face_ids=firing.tolist(),
      trigger_front_before_world_cm=blade.tolist(),trigger_outward_world=normal.tolist(),
      curled_pad_center_world_cm=pad.tolist(),curled_pad_tangent_world_cm=support.tolist(),
      gun_translation_world_cm=delta.tolist(),gun_translation_cm=float(np.linalg.norm(delta)),
      source_clip=cache['clips']['owner_reload']['asset'],source_phase_s=2.2,
      index_chain_turn_before_deg=probe['baseline_chain_turn_deg'],index_chain_turn_after_deg=turn,
      index_local_rotation_deltas_deg=localturn,index_local_translation_scale_checks=localchecks,gun_angle_scale_unchanged=True)
    write(OUT/'result.json',r)
    assert np.linalg.norm(delta)<=4,('Whole gun shift exceeds4cm',np.linalg.norm(delta))
    g1=dict(g0);g1['t']=(np.array(g0['t'])+delta).tolist();gm1=mat(g1);wg1=transform(gp,gm1)
    change=gm1@np.linalg.inv(gm);leftgoal=change@new['hand_l'];new,armchecks=arm_targets(new,{'l':leftgoal},parents)
    p1=skin(new);before=contacts(p0,wg0);after=contacts(p1,wg1);bs=finger_self(p0);fs=finger_self(p1)
    left=[n for n in names if n.endswith('_l') and n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))]
    affected=[*INDEX,*left];protected=[n for n in names if n not in affected]
    after_bones=dict(old['after_bones'])
    for n in affected:after_bones[n]=encode(new[n])
    eligible=w[:,[names.index(n) for n in affected]].sum(1)>0;move=np.linalg.norm(p1-p0,axis=1)
    im=w[:,[names.index(n) for n in INDEX]].sum(1)>0
    rightother=w[:,[names.index(n) for n in names if n.endswith('_r') and n.startswith(('hand_','thumb_','middle_','ring_','pinky_'))]].sum(1)>0
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);e0=np.linalg.norm(p0[edges[:,0]]-p0[edges[:,1]],axis=1);e1=np.linalg.norm(p1[edges[:,0]]-p1[edges[:,1]],axis=1)
    distal_mask=w[:,[names.index('index_02_r'),names.index('index_03_r')]].sum(1)>0
    distalfs=np.flatnonzero(np.any(distal_mask[tri],axis=1));distalcross=intersection_pairs(p1,tri[distalfs],wg1,gt)
    dc={group:sorted({int(distalfs[a]) for a,b in distalcross if b in groups[group]}) for group in ('stock','guard','blade')}
    bladetree=BVHTree.FromPolygons([Vector(v) for v in wg1],gt[sorted(groups['blade'])].tolist(),all_triangles=True)
    gaps=[bladetree.find_nearest(Vector(v))[3] for v in p1[tri[padfaces]].mean(1)]
    r.update(before_contact=before,after_contact=after,actual_distal_index_crossing_faces=dc,
      actual_pad_mean_blade_gap_cm=float(np.mean(gaps)),actual_pad_min_blade_gap_cm=float(min(gaps)),
      new_index_neighbor_self_pairs=len(fs-bs),before_index_neighbor_self_pairs=len(bs),after_index_neighbor_self_pairs=len(fs),
      new_severe_edges=int(np.sum((e1>e0*3)&(e1-e0>2))),max_extra_skin_edge_cm=float(np.max(e1-e0)),
      protected_bone_matrix_error=float(max(np.max(abs(new[n]-bones[n])) for n in protected)),
      true_zero_changed_influence_skin_cm=float(move[~eligible].max()),
      index_shared_other_right_skin=[{'vertex_id':int(i),'motion_cm':float(move[i])} for i in np.flatnonzero(im&rightother)],
      original_length_arm_checks=armchecks,
      all_other_right_digit_local_error=float(max(np.max(abs(np.linalg.inv(new[parents[n]])@new[n]-np.linalg.inv(bones[parents[n]])@bones[n])) for n in names if n.endswith('_r') and n.startswith(('thumb_','middle_','ring_','pinky_')))),
      left_digit_local_error=float(max(np.max(abs(np.linalg.inv(new[parents[n]])@new[n]-np.linalg.inv(bones[parents[n]])@bones[n])) for n in left if n.startswith(('thumb_','index_','middle_','ring_','pinky_')))),
      bone_names=names,parents=parents,before_bones=old['after_bones'],after_bones=after_bones,
      before_gun_world=g0,after_gun_world=g1,mesh_world=old['mesh_world'],protected_bones=protected,
      authorized_bones=affected,changed_local_rotation_deg={n:tm.angle(encode(np.linalg.inv(bones[parents[n]])@bones[n])['q'],encode(np.linalg.inv(new[parents[n]])@new[n])['q']) for n in affected},
      source_model_weights_actions_modified=False)
    np.savez_compressed(OUT/'diagnostic_geometry.npz',skin=p1,before_skin=p0,skin_triangles=tri,gun_before_cm=wg0,gun_after_cm=wg1,gun_triangles=gt)
    write(OUT/'result.json',r)
    assert r['protected_bone_matrix_error']<1e-8 and r['true_zero_changed_influence_skin_cm']<.0001
    assert not r['new_severe_edges'] and not r['new_index_neighbor_self_pairs']
    assert not dc['stock'] and not dc['guard'] and not dc['blade'],'Actual distal index still crosses gun'
    assert r['actual_pad_mean_blade_gap_cm']<=.3,'Actual curved pad not seated'
    r['status']='curled_index_translated_gun_requires_actual_views'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(json.dumps({k:r.get(k) for k in ('status','errors','gun_translation_world_cm','gun_translation_cm','index_chain_turn_after_deg','actual_pad_mean_blade_gap_cm','actual_distal_index_crossing_faces','new_index_neighbor_self_pairs','new_severe_edges')},indent=2))
