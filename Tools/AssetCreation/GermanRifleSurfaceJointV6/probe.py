"""Original-surface ray landmark probe, not a semantic coordinate classifier."""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/incoming/kar98k-parts-v3-0-recovery.glb'
EXPECTED = '78d3398820afc92314ce553afc4f1aa2528267281b644432177338bc052f4bf4'

def load():
    assert hashlib.sha256(INPUT.read_bytes()).hexdigest() == EXPECTED
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(INPUT))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    norm = Matrix(json.loads((ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/incoming_v2/inspection.json').read_text())['normalizationMatrix'])
    for o in meshes:
        o.matrix_world = norm @ o.matrix_world
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return max(meshes, key=lambda o:len(o.data.polygons)), meshes

def camera(name, eye, target, scale):
    d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d)
    bpy.context.scene.collection.objects.link(o); o.location=eye
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=100
    return o

def setup():
    s=bpy.context.scene;s.render.resolution_x=1440;s.render.resolution_y=810
    s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    s.render.engine='BLENDER_WORKBENCH';s.world=bpy.data.worlds.new('JointWorld')
    sh=s.display.shading;sh.color_type='MATERIAL';sh.light='STUDIO'
    sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD'
    return s

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    rifle,meshes=load();m=rifle.data;tree=BVHTree.FromPolygons([v.co for v in m.vertices],[p.vertices for p in m.polygons],all_triangles=True)
    c=camera('Reference_receiver_quarter',(.1,-1,.7),(-.1,0,.075),.46)
    rot=c.rotation_euler.to_matrix(); rows=[]
    # Points picked on the inspected V5 fixed quarter-view image, in image pixels.
    for name,px,py in [('ball_front',511,487),('ball_top',515,451),('neck_center',520,392),('neck_base',535,352),('receiver',615,261)]:
        origin=c.location+rot@Vector(((px/1440-.5)*.46,(.5-py/810)*.46*810/1440,0))
        hit,n,face,dist=tree.ray_cast(origin,rot@Vector((0,0,-1)))
        rows.append({'name':name,'pixel':[px,py],'face':face,'point':list(hit) if hit else None,'normal':list(n) if n else None})
    (out/'landmarks.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    s=setup();s.camera=c;s.render.filepath=str(out/'clay_original_quarter.png');bpy.ops.render.render(write_still=True)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'OriginalSurfaceProbe.blend'))
    print(json.dumps(rows),flush=True)
