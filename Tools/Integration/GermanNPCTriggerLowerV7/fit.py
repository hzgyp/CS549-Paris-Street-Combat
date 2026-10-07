"""One user-marked stock-down trigger rotation; retained thumb and source-length left follow."""
import sys, math, traceback, json, struct
from pathlib import Path
import numpy as np
from mathutils import Matrix, Quaternion, Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT, STORE, GLB, read, write, row, sha, guards, tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat, transform, intersection_pairs
sys.path.insert(0,str(ROOT/'Tools/Integration/GermanNPCOrderedGripV4'))
from arm_fit import arm_targets, encode
BASE=STORE/'Evidence/GermanNPCTriggerLowerV7'; OUT=BASE/'stock_down_v1'
assert not OUT.exists(); OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/result.json'; DATA=PREV.parent/'geometry.npz'
THUMB=STORE/'Evidence/GermanNPCRightThumbV6/vertical_lift_v2/result.json'
MARK=Path('C:/Users/hzgyp/AppData/Local/Temp/codex-clipboard-30bd8c0b-0866-43e3-a0b5-c6e7dccb5cfe.png')
paths=(PREV,DATA,THUMB,GLB,MARK,Path(__file__),ROOT/'Tools/Integration/GermanNPCOrderedGripV4/arm_fit.py',ROOT/'Tools/Integration/WeaponTriggerAlignmentV2/blender_contact_common.py')
r={'status':'starting','errors':[],'guards_before':guards(),'inputs':[row(p) for p in paths],
   'formal_selected':False,'source_modified':False,'native_tested':False,'contact_accepted':False}
write(OUT/'result.json',r)

def posed(bones):
    p=np.zeros_like(rest)
    for j,n in enumerate(names):p+=weights[:,j,None]*transform(rest,bones[n]@np.linalg.inv(ref[j]))
    return p/weights.sum(1)[:,None]

def contacts(points,worldgun):
    result={}
    for side in ('r','l'):
        for digit in ('thumb','index','middle','ring','pinky'):
            ids=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_'+side)]
            mask=weights[:,ids].sum(1)>0; faces=np.flatnonzero(np.any(mask[tri],axis=1))
            pairs=intersection_pairs(points,tri[faces],worldgun,gt)
            result[digit+'_'+side]={part:len({int(faces[a]) for a,b in pairs if b in group}) for part,group in groups.items()}
    return result

try:
    old=read(PREV); t=read(THUMB); assert not old['errors'] and t['status']=='failed_preserved'
    for e in old['inputs']:assert sha(ROOT/e['path'])==e['sha256']
    names=old['bone_names'];parents=old['parents'];d=np.load(DATA)
    rest=d['rest_native_cm'];weights=d['weights'];ref=d['reference_matrices'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles']
    bones={n:mat(v) for n,v in old['after_bones'].items()}; base={n:m.copy() for n,m in bones.items()}
    thumbnames=('thumb_01_r','thumb_02_r','thumb_03_r')
    for n in thumbnames:
        p=parents[n];local=np.linalg.inv(bones[p])@bones[n];x,y,z,q=t['chosen']['local_rotations'][n]
        local[:3,:3]=np.array(Quaternion((q,x,y,z)).to_matrix())*np.linalg.norm(local[:3,:3],axis=0)
        base[n]=base[p]@local
    before=posed(base);g0=mat(old['after_gun_world']);pivot=transform(np.array([old['trigger_pivot_gun_cm']]),g0)[0]
    # Same actual horizontal pitch axis as V4. Positive rotates the muzzle up
    # and the rear stock down, matching the arrow rather than its opposite.
    forward=g0[:3,:3]@np.array([0.,1.,0.]);horizontal=forward.copy();horizontal[2]=0;horizontal/=np.linalg.norm(horizontal)
    axis=np.cross(horizontal,[0.,0.,1.]);axis/=np.linalg.norm(axis);angle=math.radians(8)
    rotation=np.array(Quaternion(Vector(axis),angle).to_matrix(),float)
    change=np.eye(4);change[:3,:3]=rotation;change[:3,3]=pivot-rotation@pivot
    g1=change@g0;left_target=change@base['hand_l'];afterbones,armcheck=arm_targets(base,{'l':left_target},parents)
    after=posed(afterbones);w0,w1=transform(gp,g0),transform(gp,g1)
    stocklocal=np.array([old['stock_pivot_gun_cm']]);stock0=transform(stocklocal,g0)[0];stock1=transform(stocklocal,g1)[0]
    pivot1=transform(np.array([old['trigger_pivot_gun_cm']]),g1)[0]
    protected=[n for n in names if not (n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_l'))]
    protected_error=float(max(np.max(abs(afterbones[n]-base[n])) for n in protected))
    digit_error=float(max(np.max(abs(np.linalg.inv(afterbones[parents[n]])@afterbones[n]-np.linalg.inv(base[parents[n]])@base[n])) for n in names if n.startswith(('thumb_','index_','middle_','ring_','pinky_'))))
    leftrelative=float(np.max(abs(np.linalg.inv(afterbones['hand_l'])@g1-np.linalg.inv(base['hand_l'])@g0)))
    rightidx=weights[:,[j for j,n in enumerate(names) if n.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_r')]].sum(1)>0
    rightskin=float(np.linalg.norm(after[rightidx]-before[rightidx],axis=1).max())
    leftdigits=weights[:,[j for j,n in enumerate(names) if n.startswith(('thumb_','index_','middle_','ring_','pinky_')) and n.endswith('_l')]].sum(1)>0
    track=float(np.linalg.norm(after[leftdigits]-transform(before[leftdigits],change),axis=1).max())
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    edge0=np.linalg.norm(before[edges[:,0]]-before[edges[:,1]],axis=1);edge1=np.linalg.norm(after[edges[:,0]]-after[edges[:,1]],axis=1)
    severe=int(np.sum((edge1>edge0*3)&(edge1-edge0>2)))
    # Semantic GLB groups retain exact original triangle order.
    blob=GLB.read_bytes();count=struct.unpack_from('<I',blob,12)[0];gltf=json.loads(blob[20:20+count]);at=0
    groups={'stock':set(),'guard':set(),'blade':set(),'whole':set(range(len(gt)))}
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            count=gltf['accessors'][prim['indices']]['count']//3
            part='stock' if node['name'] in ('Wood_ContinuousStock','Wood_UpperHandguard') else 'blade' if node['name']=='Trigger_Donor' else 'guard' if 'TriggerGuard' in node['name'] else None
            if part:groups[part].update(range(at,at+count))
            at+=count
    assert at==len(gt)==24466
    r.update(rotation_deg=8,axis_world=axis.tolist(),direction='Rear stock down; muzzle up',
       trigger_pivot_gun_cm=old['trigger_pivot_gun_cm'],trigger_pivot_world_cm=pivot.tolist(),
       trigger_pivot_error_cm=float(np.linalg.norm(pivot1-pivot)),stock_contact_motion_cm=(stock1-stock0).tolist(),
       stock_contact_world_before_cm=stock0.tolist(),stock_contact_world_after_cm=stock1.tolist(),
       original_length_left_arm_checks=armcheck,protected_bone_matrix_error=protected_error,
       digit_local_matrix_error=digit_error,left_gun_hand_relative_matrix_error=leftrelative,
       right_skin_error_cm=rightskin,left_digit_mixed_skin_tracking_cm=track,new_severe_edges=severe,
       max_extra_skin_edge_cm=float((edge1-edge0).max()),
       before_crossing_faces=contacts(before,w0),after_crossing_faces=contacts(after,w1),
       max_gun_vertex_motion_cm=float(np.linalg.norm(w1-w0,axis=1).max()),
       bone_names=names,parents=parents,before_bones={n:encode(b) for n,b in base.items()},
       after_bones={n:encode(b) for n,b in afterbones.items()},before_gun_world=encode(g0),after_gun_world=encode(g1),
       retained_thumb_local_rotations=t['chosen']['local_rotations'],mesh_world=old['mesh_world'],
       source_model_weights_actions_modified=False,protected_bones=protected)
    write(OUT/'result.json',r)
    assert r['trigger_pivot_error_cm']<.0001 and stock1[2]<stock0[2]
    assert protected_error<1e-8 and digit_error<1e-8 and rightskin<.0001 and leftrelative<1e-8
    assert max(armcheck['l']['upper_length_error_cm'],armcheck['l']['forearm_length_error_cm'])<.0001
    assert severe==0,('New severe edges',severe)
    r['status']='marked_stock_down_comparison_requires_visual_review'
    np.savez_compressed(OUT/'geometry.npz',skin=after,before_skin=before,skin_triangles=tri,gun_local_cm=gp,gun_triangles=gt,rest_native_cm=rest,weights=weights,reference_matrices=ref)
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print(json.dumps({k:r.get(k) for k in ('status','errors','rotation_deg','trigger_pivot_error_cm','stock_contact_motion_cm','original_length_left_arm_checks','new_severe_edges','before_crossing_faces','after_crossing_faces')},indent=2))
