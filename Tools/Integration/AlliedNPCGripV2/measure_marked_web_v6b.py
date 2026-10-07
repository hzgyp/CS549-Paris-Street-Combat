"""Read-only marked regions with explicitly native UE screen-right parity."""
import argparse
import sys
import traceback
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, STORE, BASE, read, write, sha, guards
sys.path.insert(0, str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat, transform, skin

parser = argparse.ArgumentParser()
parser.add_argument('--identity', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
assert args.identity.replace('_','').isalnum()
OUT = BASE/args.identity
assert not OUT.exists()
OUT.mkdir(parents=True)
FBX = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Exchange/SK_WWII_US_Paratrooper_simple.fbx'
AUDIT = STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
TOPO = STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
PREVIOUS = BASE/'fit_v5/result.json'
paths = (FBX,AUDIT,TOPO,PREVIOUS,Path(__file__))
r = {'errors':[], 'status':'measuring', 'guards_before':guards(),
     'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
     'pose_or_source_modified':False, 'native_authored':False}
write(OUT/'source.json',r)

try:
    previous = read(PREVIOUS)
    assert not previous['errors'] and previous['guards_after'] == 611
    pose = previous['after']['bones']
    mw = mat(previous['before']['mesh_world'])
    origin = mw[:3,3]
    model = read(AUDIT)['models']['owner']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX),automatic_bone_orientation=False,use_anim=False)
    rig = next(o for o in bpy.data.objects if o.type=='ARMATURE')
    source = next(o for o in bpy.data.objects if o.type=='MESH')
    names = [n for n in model['ref_component'] if n in rig.data.bones]
    a = np.array([list(rig.matrix_world@rig.data.bones[n].head_local)+[1] for n in names])
    b = np.array([model['ref_component'][n]['translation'] for n in names])
    fit = np.linalg.lstsq(a,b,rcond=None)[0]
    error = float(np.linalg.norm(a@fit-b,axis=1).max())
    determinant = float(np.linalg.det(fit[:3,:]))
    assert len(names)>=60 and error<.01 and determinant<0
    ref = {n:mat(t) for n,t in model['ref_component'].items()}
    bones = {n:np.linalg.inv(mw)@mat(t) for n,t in pose.items()}
    assert set(ref)<=set(bones)
    rest = np.array([list(source.matrix_world@v.co)+[1] for v in source.data.vertices])@fit
    weights = [{source.vertex_groups[g.group].name:float(g.weight) for g in v.groups if g.weight>0}
               for v in source.data.vertices]
    assert all(w and abs(sum(w.values())-1)<.001 and set(w)<=set(ref) for w in weights)
    p = transform(skin(rest,weights,{n:bones[n]@np.linalg.inv(ref[n]) for n in ref}),mw)-origin
    source.data.calc_loop_triangles()
    tri = np.array([list(t.vertices) for t in source.data.loop_triangles],int)
    topology = read(TOPO)
    gp = np.array(topology['gun_points_cm'])
    gt = np.array(topology['gun_triangles'],int)
    gun = transform(gp,mat(previous['after']['gun_world']))-origin
    stock_ids = next(c['triangle_ids'] for c in topology['components'] if c['id']==0)
    trees = {'stock':BVHTree.FromPolygons([Vector(x) for x in gun],gt[stock_ids].tolist(),all_triangles=True)}
    face_ids = {'stock':stock_ids}
    for side in ('r','l'):
        mask = np.array([any(n=='hand_'+side or (n.endswith('_'+side) and
            n.startswith(('index_','middle_','ring_','pinky_','thumb_'))) for n in w) for w in weights])
        ids = np.flatnonzero(np.any(mask[tri],axis=1))
        trees[side] = BVHTree.FromPolygons([Vector(x) for x in p],tri[ids].tolist(),all_triangles=True)
        face_ids[side] = ids.tolist()
    cam = next(c for c in previous['captures'] if c['file']=='after_right.png')
    eye = np.array(cam['eye_cm'])-origin
    center = np.array(cam['target_cm'])-origin
    forward = (center-eye)/np.linalg.norm(center-eye)
    up = np.array([0.,0.,1.])
    right = np.cross(up,forward)  # UE camera screen-right, verified from native side view.
    assert np.linalg.norm(right-np.array([1,0,0]))<1e-6
    def hit(kind,uv):
        ray = eye+right*((uv[0]-800)*78/1600)+up*((500-uv[1])*78/1600)
        loc,normal,idx,distance = trees[kind].ray_cast(Vector(ray),Vector(forward),500)
        assert loc is not None, (kind,uv,'No actual source surface')
        loc = np.array(loc)+origin
        face = face_ids[kind][idx]
        result = {'native_pixel':uv,'world_cm':loc.tolist(),'triangle':int(face),'distance_cm':float(distance)}
        if kind in ('r','l'):
            result['vertex_weights'] = [weights[v] for v in tri[face]]
            result['hand_local_cm'] = transform(np.array([loc]),np.linalg.inv(mat(pose['hand_'+kind])))[0].tolist()
        else:
            result['gun_local_cm'] = transform(np.array([loc]),np.linalg.inv(mat(previous['after']['gun_world'])))[0].tolist()
        return result
    # Approximate native-camera clicks, interpreted from the marked regions;
    # neither arrow shaft length nor its endpoint is a calibrated 3D distance.
    landmarks = {
        'right_web_region':hit('r',[692,435]),
        'stock_neck_region':hit('stock',[715,398]),
        'left_palm_region':hit('l',[1160,447]),
        'foreend_lower_region':hit('stock',[1160,332]),
    }
    r.update(reference_alignment={'bones':len(names),'max_cm':error,'determinant':determinant},
        camera=cam,landmarks=landmarks,vertices=len(p),triangles=len(tri),
        status='source_regions_measured_requires_inspection')
    # Retain immutable geometry only for final fixed-pose contact diagnosis.
    np.savez_compressed(OUT/'source_geometry.npz',skin_world_cm=p+origin,skin_triangles=tri,
        gun_local_cm=gp,gun_triangles=gt,
        right_mask=np.array([any(n=='hand_r' or (n.endswith('_r') and n.startswith(
            ('index_','middle_','ring_','pinky_','thumb_'))) for n in w) for w in weights]),
        left_mask=np.array([any(n=='hand_l' or (n.endswith('_l') and n.startswith(
            ('index_','middle_','ring_','pinky_','thumb_'))) for n in w) for w in weights]))
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status']='failed_measurement_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
    r['guards_after']=guards()
    write(OUT/'result.json',r)
    print(r['status'],r['errors'],r.get('landmarks'))
