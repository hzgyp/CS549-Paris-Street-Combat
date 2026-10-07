"""One small stock-side turn toward actual marked reverse camera; V7 right pose fixed."""
import sys,math,traceback,json,struct
from pathlib import Path
import numpy as np
from mathutils import Quaternion,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,GLB,read,write,row,sha,guards
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs
sys.path.insert(0,str(ROOT/'Tools/Integration/GermanNPCOrderedGripV4'))
from arm_fit import arm_targets,encode
BASE=STORE/'Evidence/GermanNPCScreenRotateV8';OUT=BASE/'screen_turn_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCTriggerLowerV7/stock_down_v2/result.json'
REVIEW=PREV.parent.parent/'review_v1/result.json'
V4=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/result.json';DATA=V4.parent/'geometry.npz'
MARK=Path('C:/Users/hzgyp/AppData/Local/Temp/codex-clipboard-9a68a9b9-03ab-4b64-b9c2-807eddb52c3d.png')
paths=(PREV,REVIEW,V4,DATA,GLB,MARK,Path(__file__),ROOT/'Tools/Integration/GermanNPCOrderedGripV4/arm_fit.py',ROOT/'Tools/Integration/WeaponTriggerAlignmentV2/blender_contact_common.py')
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) if p.is_relative_to(ROOT) else {'path':str(p),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in paths],
 'formal_selected':False,'source_modified':False,'native_tested':False,'contact_accepted':False}
write(OUT/'result.json',r)
def skin(bones):
    points=np.zeros_like(rest)
    for j,n in enumerate(names):points+=w[:,j,None]*transform(rest,bones[n]@np.linalg.inv(ref[j]))
    return points/w.sum(1)[:,None]
def contacts(points,gunpoints):
    out={}
    for side in ('r','l'):
        for digit in ('thumb','index','middle','ring','pinky'):
            ids=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_'+side)]
            faces=np.flatnonzero(np.any((w[:,ids].sum(1)>0)[tri],axis=1))
            pairs=intersection_pairs(points,tri[faces],gunpoints,gt)
            out[digit+'_'+side]={part:len({int(faces[a]) for a,b in pairs if b in group}) for part,group in groups.items()}
    return out
try:
    old=read(PREV);checked=read(REVIEW);assert old['rotation_deg']==8 and not checked['errors']
    assert checked['status']=='retained_directional_comparison_views_not_full_contact_acceptance'
    for receipt in (old,checked):
        for e in receipt['inputs']:assert sha(ROOT/e['path'])==e['sha256']
    d=np.load(DATA);names=old['bone_names'];parents=old['parents'];w=d['weights'];rest=d['rest_native_cm'];ref=d['reference_matrices'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles']
    beforebones={n:mat(v) for n,v in old['after_bones'].items()};p0=skin(beforebones);g0=mat(old['after_gun_world']);wg0=transform(gp,g0)
    recorded=np.load(REVIEW.parent/'diagnostic_geometry.npz');r['v7_reproduction_skin_cm']=float(np.linalg.norm(p0-recorded['skin'],axis=1).max());r['v7_reproduction_gun_cm']=float(np.linalg.norm(wg0-recorded['gun_after_cm'],axis=1).max())
    assert max(r['v7_reproduction_skin_cm'],r['v7_reproduction_gun_cm'])<.0001
    blob=GLB.read_bytes();count=struct.unpack_from('<I',blob,12)[0];gltf=json.loads(blob[20:20+count]);at=0
    groups={'stock':set(),'blade':set(),'guard':set(),'whole':set(range(len(gt)))}
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            count=gltf['accessors'][prim['indices']]['count']//3
            part='stock' if node['name'] in ('Wood_ContinuousStock','Wood_UpperHandguard') else 'blade' if node['name']=='Trigger_Donor' else 'guard' if 'TriggerGuard' in node['name'] else None
            if part:groups[part].update(range(at,at+count))
            at+=count
    assert at==len(gt)==24466
    # The reverse camera stayed centered on pre-V7 thumb. Reproduce that exact
    # center, not a post-V7 shared-skin average or player/NPC camera guess.
    sourcecenter={n:mat(old['before_bones'][n]) for n in ('thumb_01_r','thumb_03_r')}
    center=(sourcecenter['thumb_01_r'][:3,3]+sourcecenter['thumb_03_r'][:3,3])/2
    toward=np.array([0.,40.,12.]);toward/=np.linalg.norm(toward)
    screenright=np.array([-1.,0.,0.]);screenup=np.cross(toward,screenright)
    # image Y grows down, projected height =25cm*(850/1200).
    u,v=394/645,(310-39)/476
    projected=center+screenright*((u-.5)*25)+screenup*((.5-v)*25*850/1200)
    rayorigin=projected+toward*80
    tree=BVHTree.FromPolygons([Vector(q) for q in wg0],gt.tolist(),all_triangles=True)
    hit,normal,face,distance=tree.ray_cast(Vector(rayorigin),Vector(-toward),160)
    assert hit is not None and int(face) in groups['stock'],('Marked ray must hit actual wood',face)
    marked=np.array(hit,float);pivot=transform(np.array([old['trigger_pivot_gun_cm']]),g0)[0]
    lever=marked-pivot;axis=np.cross(lever,toward);assert np.linalg.norm(axis)>1
    axis/=np.linalg.norm(axis);angle=math.radians(4)
    rot=np.array(Quaternion(Vector(axis),angle).to_matrix(),float);change=np.eye(4);change[:3,:3]=rot;change[:3,3]=pivot-rot@pivot
    g1=change@g0;marked1=transform(marked[None],change)[0]
    afterbones,armcheck=arm_targets(beforebones,{'l':change@beforebones['hand_l']},parents)
    p1=skin(afterbones);wg1=transform(gp,g1);move=np.linalg.norm(p1-p0,axis=1)
    allowed=[j for j,n in enumerate(names) if n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_l')]
    protected=[n for n in names if names.index(n) not in allowed]
    protected_error=float(max(np.max(abs(afterbones[n]-beforebones[n])) for n in protected))
    digit_error=float(max(np.max(abs(np.linalg.inv(afterbones[parents[n]])@afterbones[n]-np.linalg.inv(beforebones[parents[n]])@beforebones[n])) for n in names if n.startswith(('thumb_','index_','middle_','ring_','pinky_'))))
    lm=w[:,allowed].sum(1)>0;ri=[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_r')];shared=lm&(w[:,ri].sum(1)>0)
    index=w[:,[names.index(n) for n in ('index_02_r','index_03_r')]].sum(1)>0
    ld=w[:,[j for j,n in enumerate(names) if n.startswith(('thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_l')]].sum(1)>0
    lefttrack=float(np.linalg.norm(p1[ld]-transform(p0[ld],change),axis=1).max())
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    e0=np.linalg.norm(p0[edges[:,0]]-p0[edges[:,1]],axis=1);e1=np.linalg.norm(p1[edges[:,0]]-p1[edges[:,1]],axis=1)
    severe=int(np.sum((e1>e0*3)&(e1-e0>2)))
    r.update(rotation_deg=4,axis_world=axis.tolist(),direction='Marked rear stock toward reverse-view camera',
      screenshot_normalized_uv=[u,v],inferred_marked_stock_face=int(face),marked_stock_world_before_cm=marked.tolist(),marked_stock_world_after_cm=marked1.tolist(),
      marked_point_toward_camera_cm=float((marked1-marked)@toward),marked_point_motion_cm=(marked1-marked).tolist(),
      trigger_pivot_gun_cm=old['trigger_pivot_gun_cm'],trigger_pivot_error_cm=float(np.linalg.norm(transform(np.array([old['trigger_pivot_gun_cm']]),g1)[0]-pivot)),
      protected_bone_matrix_error=protected_error,digit_local_matrix_error=digit_error,true_zero_left_influence_skin_cm=float(move[~lm].max()),actual_distal_index_skin_cm=float(move[index].max()),
      original_length_left_arm_checks=armcheck,left_gun_hand_relative_matrix_error=float(np.max(abs(np.linalg.inv(afterbones['hand_l'])@g1-np.linalg.inv(beforebones['hand_l'])@g0))),
      shared_hand_vertices=[{'vertex_id':int(i),'motion_cm':float(move[i]),'right_hand_weight':float(w[i,ri].sum()),'left_arm_weight':float(w[i,allowed].sum())} for i in np.flatnonzero(shared)],
      left_digit_mixed_skin_tracking_cm=lefttrack,new_severe_edges=severe,max_extra_skin_edge_cm=float((e1-e0).max()),
      before_crossing_faces=contacts(p0,wg0),after_crossing_faces=contacts(p1,wg1),
      max_gun_vertex_motion_cm=float(np.linalg.norm(wg1-wg0,axis=1).max()),bone_names=names,parents=parents,
      before_bones={n:encode(b) for n,b in beforebones.items()},after_bones={n:encode(b) for n,b in afterbones.items()},
      before_gun_world=encode(g0),after_gun_world=encode(g1),mesh_world=old['mesh_world'],protected_bones=protected,
      retained_thumb_local_rotations=old['retained_thumb_local_rotations'],source_model_weights_actions_modified=False)
    write(OUT/'result.json',r)
    assert r['trigger_pivot_error_cm']<.0001 and r['marked_point_toward_camera_cm']>.2
    assert protected_error<1e-8 and digit_error<1e-8 and max(r['true_zero_left_influence_skin_cm'],r['actual_distal_index_skin_cm'])<.0001
    assert max(armcheck['l']['upper_length_error_cm'],armcheck['l']['forearm_length_error_cm'])<.0001 and severe==0
    r['status']='toward_camera_directional_comparison_requires_human_review'
    np.savez_compressed(OUT/'diagnostic_geometry.npz',skin=p1,before_skin=p0,skin_triangles=tri,gun_after_cm=wg1,gun_before_cm=wg0,gun_triangles=gt)
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(json.dumps({k:r.get(k) for k in ('status','errors','rotation_deg','marked_point_motion_cm','marked_point_toward_camera_cm','trigger_pivot_error_cm','new_severe_edges','before_crossing_faces','after_crossing_faces')},indent=2))
