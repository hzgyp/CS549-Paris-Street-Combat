"""Raycast the user's arrow onto actual V14 wood using its saved diagnostic camera."""
import hashlib
import sys
import traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12'))
from pivot_common import *

PREVIOUS = STORE/'Evidence/WeaponThumbGunSeatV14/thumb_seat_v1/result.json'
BLEND = PREVIOUS.parent/'FixedHandThumbSeat.blend'
OUT = STORE/'Evidence/WeaponMarkedGripV16/marked_pivot_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
inputs = [FBX,POSES,AUDIT,TOPOLOGY,INDEX,PREVIOUS,BLEND,Path(__file__)]
hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r = {'errors':[],'native_authored':False,'pose_or_gun_authored':False}
try:
    d = load()
    old = json.loads(PREVIOUS.read_text())
    change = np.array(old['rigid_change_gun_local'])
    gun = transform(d['gp'],change)
    bones = {n:np.array(v) for n,v in old['baseline_component_bones'].items()}
    points = evaluate(d,bones,np.array(old['baseline_gun_component_matrix']))
    scene = setup_scene()
    scene.render.resolution_x,scene.render.resolution_y = 1200,900
    camera([-.035,-.02,-.025],(-.20,-.25,.20),.26)
    cam = scene.camera
    bpy.context.view_layer.update()
    projection = cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=1200,y=900,scale_x=1,scale_y=1)
    inverse = (projection@cam.matrix_world.inverted()).inverted()
    px,py = 591.,545.
    ray_points = []
    for z in (-1.,1.):
        p = inverse@Vector((2*px/1200-1,1-2*py/900,z,1))
        ray_points.append(np.array(p[:3])/p[3]*100)
    direction = ray_points[1]-ray_points[0]
    direction /= np.linalg.norm(direction)
    stock = np.array(next(c for c in d['topo']['components'] if c['id']==0)['triangle_ids'],int)
    tree = BVHTree.FromPolygons([Vector(p) for p in gun],d['gt'][stock].tolist(),all_triangles=True)
    loc,normal,face,distance = tree.ray_cast(Vector(ray_points[0]),Vector(direction),10000.)
    assert loc is not None,'User arrow ray does not hit wood; do not silently substitute a new marker'
    pivot = np.array(loc)
    r.update(status='user_marked_wood_pivot_measured',source_pixel=[px,py],
             screenshot_pixel_approx=[319,324],screenshot_header_pixels_approx=31,
             grip_pivot_baseline_frame_cm=pivot.tolist(),wood_triangle=int(stock[face]),
             grip_pivot_gun_local_cm=transform(pivot[None],np.linalg.inv(change))[0].tolist(),
             ray_start_cm=ray_points[0].tolist(),ray_direction=direction.tolist())
    wood = material('Wood',(.21,.14,.09))
    metal = material('Metal',(.18,.21,.22))
    skinmat = material('Hand',(.61,.42,.29))
    orange = material('Fixed index',(1.,.26,.07))
    gold = material('Fixed thumb',(.8,.53,.22))
    blue = material('Left support',(.19,.43,.61))
    marker = material('User pivot',(.95,.01,.01))
    rifle = mesh('V14 gun',gun,d['gt'],[wood,metal])
    stockset = set(stock)
    for poly in rifle.data.polygons:
        poly.material_index = int(poly.index not in stockset)
    for side in ('r','l'):
        faces = d['tri'][np.all(d['masks'][side][d['tri']],axis=1)]
        obj = mesh('Fixed '+side,points,faces,[skinmat,orange,gold] if side=='r' else [blue])
        if side=='r':
            for poly,face in zip(obj.data.polygons,faces):
                poly.material_index = 1 if np.all(d['digits']['index'][face]) else (2 if np.all(d['digits']['thumb'][face]) else 0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.0025,location=tuple(pivot*.01))
    bpy.context.object.data.materials.append(marker)
    scene.render.filepath = str(OUT/'marked_pivot_oblique.png')
    bpy.ops.render.render(write_still=True)
except Exception:
    r['status']='stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes']=hashes
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r.get(k) for k in ('status','errors','grip_pivot_baseline_frame_cm','grip_pivot_gun_local_cm','inputs_unchanged')}))
