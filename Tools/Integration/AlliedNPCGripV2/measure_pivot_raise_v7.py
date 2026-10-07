"""Reconstruct immutable V6 full US skin; identify new marked grip pivot."""
import sys
import traceback
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
import transform_math as tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform

OUT=BASE/'pivot_raise_measure_v7'
assert not OUT.exists()
OUT.mkdir(parents=True)
FBX=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Exchange/SK_WWII_US_Paratrooper_simple.fbx'
AUDIT=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
PREVIOUS=BASE/'marked_web_v6/result.json'
LANDMARKS=BASE/'stock_pivot_v1/result.json'
paths=(FBX,AUDIT,TOPO,PREVIOUS,LANDMARKS,Path(__file__))
r={'errors':[],'status':'starting','guards_before':guards(),
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
   'native_authored':False,'source_model_weights_actions_modified':False}
write(OUT/'source.json',r)
try:
    previous=read(PREVIOUS)
    assert not previous['errors'] and previous['guards_after']==611
    pose=previous['after']['bones']
    model=read(AUDIT)['models']['owner']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX),automatic_bone_orientation=False,use_anim=False)
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    source=next(o for o in bpy.data.objects if o.type=='MESH')
    names=[n for n in model['ref_component'] if n in rig.data.bones]
    a=np.array([list(rig.matrix_world@rig.data.bones[n].head_local)+[1] for n in names])
    b=np.array([model['ref_component'][n]['translation'] for n in names])
    fit=np.linalg.lstsq(a,b,rcond=None)[0]
    error=float(np.linalg.norm(a@fit-b,axis=1).max())
    determinant=float(np.linalg.det(fit[:3,:]))
    assert len(names)>=60 and error<.01 and determinant<0
    names=list(model['ref_component'])
    assert set(names)<=set(pose)
    rest=np.array([list(source.matrix_world@v.co)+[1] for v in source.data.vertices])@fit
    weights=np.zeros((len(rest),len(names)))
    indices={n:i for i,n in enumerate(names)}
    for i,v in enumerate(source.data.vertices):
        for g in v.groups:
            if g.weight>0:
                n=source.vertex_groups[g.group].name
                assert n in indices
                weights[i,indices[n]]=g.weight
    assert np.max(abs(weights.sum(1)-1))<.001
    ref=np.array([mat(model['ref_component'][n]) for n in names])
    p=np.zeros_like(rest)
    for j,n in enumerate(names):
        p+=weights[:,j,None]*transform(rest,mat(pose[n])@np.linalg.inv(ref[j]))
    p/=weights.sum(1)[:,None]
    source.data.calc_loop_triangles()
    tri=np.array([list(t.vertices) for t in source.data.loop_triangles],int)
    slots=np.array([t.material_index for t in source.data.loop_triangles])
    topo=read(TOPO)
    gp=np.array(topo['gun_points_cm']);gt=np.array(topo['gun_triangles'],int)
    gun=transform(gp,mat(previous['after']['gun_world']))
    stockids=next(c['triangle_ids'] for c in topo['components'] if c['id']==0)
    origin=np.array(previous['before']['mesh_world']['t'])
    right_ids=[i for i,n in enumerate(names) if n=='hand_r' or (n.endswith('_r') and n.startswith(('index_','middle_','ring_','pinky_','thumb_')))]
    mask=np.any(weights[:,right_ids]>0,axis=1)
    handfaces=np.flatnonzero(np.any(mask[tri],axis=1))
    bodytree=BVHTree.FromPolygons([Vector(x) for x in p-origin],tri[handfaces].tolist(),all_triangles=True)
    stocktree=BVHTree.FromPolygons([Vector(x) for x in gun-origin],gt[stockids].tolist(),all_triangles=True)
    cam=next(c for c in previous['captures'] if c['file']=='after_right.png')
    eye=np.array(cam['eye_cm'])-origin
    target=np.array(cam['target_cm'])-origin
    forward=(target-eye)/np.linalg.norm(target-eye)
    up=np.array([0.,0.,1.]);right=np.cross(up,forward)
    uv=[726,456]
    ray=eye+right*((uv[0]-800)*78/1600)+up*((500-uv[1])*78/1600)
    hand,normal,index,distance=bodytree.ray_cast(Vector(ray),Vector(forward),500)
    assert hand is not None,'Marked region does not identify right-hand skin'
    hand=np.array(hand)+origin
    wood,normal,woodindex,distance=stocktree.ray_cast(Vector(ray),Vector(forward),500)
    mode='actual stock ray at marked region'
    if wood is None:
        wood,normal,woodindex,distance=stocktree.find_nearest(Vector(hand-origin))
        mode='mark falls on hand/occluded underside; nearest actual stock to marked skin'
    assert wood is not None
    pivot=np.array(wood)+origin
    projected=[800+np.dot(pivot-(target+origin),right)*1600/78,
               500-(pivot[2]-(target+origin)[2])*1600/78]
    assert abs(projected[0]-uv[0])<30 and abs(projected[1]-uv[1])<30,'Pivot outside marked region'
    padlocal=previous['landmarks']['pad_hand_cm']
    pad=np.array(tm.point(pose['hand_r'],padlocal))
    blade_local=previous['landmarks']['blade_gun_cm']
    r.update(status='marked_grip_surface_measured',reference_alignment={'bones':len(names),'max_cm':error,'determinant':determinant},
        marker={'native_pixel':uv,'camera':cam,'selection':mode,'actual_stock_projected_pixel':projected},
        pivot_world_cm=pivot.tolist(),pivot_gun_cm=tm.inverse_point(previous['after']['gun_world'],pivot.tolist()),
        pivot_stock_triangle=int(stockids[woodindex]),marked_hand_world_cm=hand.tolist(),
        marked_hand_triangle=int(handfaces[index]),index_pad_world_cm=pad.tolist(),
        pad_hand_cm=padlocal,blade_gun_cm=blade_local,
        before_bones=pose,before_gun_world=previous['after']['gun_world'],
        mesh_world=previous['before']['mesh_world'],parents=model['parents'],bone_names=names,
        vertices=len(p),triangles=len(tri),original_native_result_sha256=sha(PREVIOUS))
    np.savez_compressed(OUT/'geometry.npz',rest_native_cm=rest,weights=weights,reference_matrices=ref,
        skin_triangles=tri,skin_slots=slots,skin_world_cm=p,gun_local_cm=gp,gun_triangles=gt)
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
    r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','marker','pivot_world_cm','reference_alignment')})
