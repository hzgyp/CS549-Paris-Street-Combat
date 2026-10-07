"""Fixed German hands: modest trigger yaw, then measured stock-pivot muzzle lowering."""
import sys, math, json, struct, traceback
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT, STORE, GLB, read, write, row, sha, guards, tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat, transform, intersection_pairs

BASE=STORE/'Evidence/GermanNPCOrderedGripV4'
OUT=BASE/'offline_v1'; assert not OUT.exists(); OUT.mkdir(parents=True)
V3=STORE/'Evidence/GermanNPCSmallPivotV3/small_rotation_v1/result.json'
F3=V3.parent.parent/'marked_rotation_v1/result.json'
AUDIT=STORE/'Evidence/WeaponAnimationReuseV1/audit_v1/result.json'
FBX=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Exchange/SK_WWII_GermanSoldier_varA.fbx'
ALLIED=STORE/'Evidence/AlliedNPCGripV2/fp_wrist_native_v14/result.json'
paths=(V3,F3,AUDIT,FBX,GLB,ALLIED,Path(__file__))
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in paths],
   'source_modified':False,'all_bones_fixed':True,'formal_selected':False,'contact_accepted':False}
write(OUT/'result.json',r)

def near(points, faces, target):
    tree=BVHTree.FromPolygons([Vector(p) for p in points],faces.tolist(),all_triangles=True)
    loc,normal,index,gap=tree.find_nearest(Vector(target)); assert loc is not None
    return np.array(loc,float),int(index),float(gap)

def rigid(gun, pivot, axis, angle):
    axis=np.asarray(axis,float); axis/=np.linalg.norm(axis)
    q=[*(axis*math.sin(angle/2)),math.cos(angle/2)]
    return {'t':(pivot+np.array(tm.rotate(q,np.array(gun['t'])-pivot))).tolist(),
            'q':tm.qmul(q,gun['q']),'s':gun['s']}

def contacts(gun, gp, gt, groups, skin, tri, masks):
    world=transform(gp,mat(gun)); result={}
    for name,mask in masks.items():
        ids=np.flatnonzero(np.any(mask[tri],axis=1))
        pairs=intersection_pairs(skin,tri[ids],world,gt)
        result[name]={part:len({int(ids[a]) for a,b in pairs if b in group}) for part,group in groups.items()}
    return result

try:
    prev,fit,audit,ally=map(read,(V3,F3,AUDIT,ALLIED))
    assert not prev['errors'] and prev['all_bones_exact'] and not audit['errors']
    for e in (fit['v1_result'],fit['v1_landmarks'],fit['model']): assert sha(ROOT/e['path'])==e['sha256']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX),automatic_bone_orientation=False,use_anim=False)
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    meshes=[o for o in bpy.data.objects if o.type=='MESH']; assert len(meshes)==1
    source=meshes[0]; refs=audit['models']['german']['ref_local']; names=list(refs)
    assert all(n in rig.data.bones for n in names)
    parents={n:rig.data.bones[n].parent.name if rig.data.bones[n].parent else None for n in names}
    ref={}
    def reference(n):
        if n not in ref:
            p=parents[n]; ref[n]=(reference(p) if p in refs else np.eye(4))@mat(refs[n])
        return ref[n]
    for n in names:reference(n)
    a=np.array([list(rig.matrix_world@rig.data.bones[n].head_local)+[1] for n in names])
    b=np.array([ref[n][:3,3] for n in names]); align=np.linalg.lstsq(a,b,rcond=None)[0]
    error=float(np.linalg.norm(a@align-b,axis=1).max()); assert error<.01,('Reference mismatch',error)
    assert np.linalg.det(align[:3,:])<0
    rest=np.array([list(source.matrix_world@v.co)+[1] for v in source.data.vertices])@align
    weights=np.zeros((len(rest),len(names)))
    for i,v in enumerate(source.data.vertices):
        for g in v.groups:
            if g.weight>0:
                n=source.vertex_groups[g.group].name; assert n in names; weights[i,names.index(n)]=g.weight
    assert np.max(np.abs(weights.sum(1)-1))<.001
    bones={n:mat(t) for n,t in prev['after']['bones'].items()}; posed=np.zeros_like(rest)
    for j,n in enumerate(names):posed+=weights[:,j,None]*transform(rest,bones[n]@np.linalg.inv(ref[n]))
    posed/=weights.sum(1)[:,None]
    source.data.calc_loop_triangles(); tri=np.array([list(t.vertices) for t in source.data.loop_triangles],int)
    masks={}
    for side in ('r','l'):
        for digit in ('thumb','index','middle','ring','pinky'):
            idx=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_'+side)]
            masks[digit+'_'+side]=weights[:,idx].sum(1)>0
    palm_mask=weights[:,names.index('hand_l')]>.8
    palm_tri=tri[np.all(palm_mask[tri],axis=1)]; assert len(palm_tri)>10
    blob=GLB.read_bytes(); count=struct.unpack_from('<I',blob,12)[0]
    gltf=json.loads(blob[20:20+count]); binary=blob[28+count:]
    offset=np.array(read(ROOT/'tmp/german-rifle-ue-v1/preflight_v1.json')['native_import_offset_cm'])
    def acc(index):
        a=gltf['accessors'][index]; v=gltf['bufferViews'][a['bufferView']]
        assert 'sparse' not in a and 'byteStride' not in v
        dims={'SCALAR':1,'VEC3':3}[a['type']]; dtype={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]
        return np.frombuffer(binary,dtype=dtype,count=a['count']*dims,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],dims)
    points=[]; faces=[]; groups={'stock':set(),'guard':set(),'blade':set(),'whole':set()}
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        assert all(k not in node for k in ('matrix','rotation','scale'))
        for p in gltf['meshes'][node['mesh']]['primitives']:
            v=acc(p['attributes']['POSITION']).astype(float)+np.array(node.get('translation',[0,0,0]))
            v=np.stack([v[:,2],v[:,0],v[:,1]],axis=1)*100+offset
            t=acc(p['indices']).ravel().reshape(-1,3).astype(int)+len(points)
            part={'Wood_ContinuousStock':'stock','Trigger_Donor':'blade','TriggerGuard_Donor':'guard'}.get(node['name'])
            if 'TriggerGuard' in node['name']:part='guard'
            if part:groups[part].update(range(len(faces),len(faces)+len(t)))
            points.extend(v);faces.extend(t)
    gp=np.asarray(points);gt=np.asarray(faces,int);groups['whole']=set(range(len(gt)))
    assert len(gt)==24466 and all(groups[k] for k in ('stock','guard','blade'))
    native=read(STORE/'Evidence/GermanRifleUEV1/import_v3/result.json')
    bounderr=float(max(np.max(abs(gp.min(0)-native['bounds_min_cm'])),np.max(abs(gp.max(0)-native['bounds_max_cm']))))
    assert bounderr<.01
    g0=prev['after']['gun_world']; H=prev['after']['bones']['hand_r']
    pivot=np.array(tm.point(g0,fit['pivot_gun_cm']))
    g1=rigid(g0,pivot,fit['axis_world'],math.radians(-5))
    stock_pivot=np.array(tm.point(g1,fit['stock_gun_cm']))
    # The actual original fore-end nearest the fixed support palm identifies its
    # contact station. It is not a mean finger-bone coordinate or invented depth.
    v1=read(ROOT/fit['v1_result']['path']); old=v1['before']['gun_world']; oldH=v1['before']['bones']['hand_r']
    oldrel={'t':tm.inverse_point(oldH,old['t']),'q':tm.qmul(tm.qinv(oldH['q']),old['q']),'s':old['s']}
    original={'t':tm.point(H,oldrel['t']),'q':tm.qmul(H['q'],oldrel['q']),'s':oldrel['s']}
    stock_faces=gt[sorted(groups['stock'])]
    originalwood=transform(gp,mat(original)); leftw=bones['hand_l'][:3,3]
    wood,wi,_=near(originalwood,stock_faces,leftw)
    palm,pi,_=near(posed,palm_tri,wood)
    wood,wi,source_gap=near(originalwood,stock_faces,palm)
    support_local=tm.inverse_point(original,wood.tolist())
    before_support=np.array(tm.point(g1,support_local))
    forward=np.array(tm.rotate(g1['q'],[0,1,0])); horizontal=forward.copy();horizontal[2]=0;horizontal/=np.linalg.norm(horizontal)
    axis=np.cross(horizontal,[0,0,1]);axis/=np.linalg.norm(axis)
    # In this plane a positive rotation raises the muzzle; solve a signed
    # DOWNWARD angle toward the actual palm point, bounded before evaluating.
    a=before_support-stock_pivot;b=palm-stock_pivot
    af=a-axis*np.dot(a,axis);bf=b-axis*np.dot(b,axis)
    pitch=math.atan2(np.dot(axis,np.cross(af,bf)),np.dot(af,bf))
    r['measured_pitch_deg']=math.degrees(pitch)
    # axis cross(horizontal,+Z) produces positive elevation. Verify sign from
    # actual transformed rifle rather than assuming Blender/UE parity.
    trial=rigid(g1,stock_pivot,axis,pitch)
    elevation_before=math.degrees(math.asin(forward[2]))
    elevation_after=math.degrees(math.asin(tm.rotate(trial['q'],[0,1,0])[2]))
    r.update(reference_alignment_cm=error,reference_determinant=float(np.linalg.det(align[:3,:])),
        skin_vertices=len(posed),skin_triangles=len(tri),gun_bounds_error_cm=bounderr,
        source_gun_world=g0,first_gun_world=g1,new_gun_world=trial,
        trigger_pivot_gun_cm=fit['pivot_gun_cm'],trigger_pivot_world_cm=pivot.tolist(),
        stock_pivot_gun_cm=fit['stock_gun_cm'],stock_pivot_world_cm=stock_pivot.tolist(),
        yaw_extra_deg=-5,yaw_total_from_v1_deg=-10,pitch_axis_world=axis.tolist(),
        support_gun_cm=support_local,support_palm_world_cm=palm.tolist(),
        original_support_gap_cm=source_gap,support_gap_after_yaw_cm=float(np.linalg.norm(before_support-palm)),
        support_gap_final_cm=math.dist(tm.point(trial,support_local),palm),
        elevation_before_deg=elevation_before,elevation_after_deg=elevation_after,
        trigger_motion_after_pitch_cm=math.dist(tm.point(trial,fit['pivot_gun_cm']),pivot),
        stock_pivot_residual_cm=math.dist(tm.point(trial,fit['stock_gun_cm']),stock_pivot),
        max_gun_motion_from_v3_cm=float(np.linalg.norm(transform(gp,mat(trial))-transform(gp,mat(g0)),axis=1).max()),
        bone_world=prev['after']['bones'],mesh_world=prev['before']['mesh_world'],
        v3_gun_hand_relative={'t':tm.inverse_point(H,g0['t']),'q':tm.qmul(tm.qinv(H['q']),g0['q']),'s':g0['s']},
        final_gun_hand_relative={'t':tm.inverse_point(H,trial['t']),'q':tm.qmul(tm.qinv(H['q']),trial['q']),'s':trial['s']})
    write(OUT/'result.json',r)
    assert abs(r['measured_pitch_deg'])<=12 and elevation_after<elevation_before,('Not bounded downward pitch',r['measured_pitch_deg'])
    assert r['support_gap_final_cm']<r['support_gap_after_yaw_cm']
    before=contacts(g0,gp,gt,groups,posed,tri,masks);after=contacts(trial,gp,gt,groups,posed,tri,masks)
    r.update(before_crossing_faces=before,after_crossing_faces=after,guards_after=guards(),
        status='ordered_gun_fit_requires_native_visual_review')
    np.savez_compressed(OUT/'geometry.npz',skin=posed,skin_triangles=tri,gun_local_cm=gp,gun_triangles=gt)
    write(OUT/'result.json',r)
    print(json.dumps({k:r[k] for k in ('status','measured_pitch_deg','support_gap_after_yaw_cm','support_gap_final_cm','trigger_motion_after_pitch_cm','max_gun_motion_from_v3_cm','before_crossing_faces','after_crossing_faces')}))
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved';write(OUT/'result.json',r);print(r['errors'][-1])
