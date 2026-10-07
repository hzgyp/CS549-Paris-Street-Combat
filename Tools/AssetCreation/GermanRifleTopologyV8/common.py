import hashlib,json
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8'
INPUT=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7/normals_v1/Kar98k_Normals_V7.blend'
VIEWS=[('right_detail',(-.08,-2,.07),(-.08,0,.07),.58),('top_detail',(-.08,0,2),(-.08,0,.07),.58),
       ('left_detail',(-.08,2,.07),(-.08,0,.07),.58),('bottom_detail',(-.08,0,-2),(-.08,0,.07),.58),
       ('quarter',(.1,-1,.7),(-.1,0,.075),.46),('reverse',(-.6,1,.7),(-.05,0,.06),.65),
       ('whole_right',(0,-3,0),(0,0,0),1.3),('whole_left',(0,3,0),(0,0,0),1.3),
       ('whole_top',(0,0,3),(0,0,0),1.3),('whole_bottom',(0,0,-3),(0,0,0),1.3),
       ('muzzle',(.72,-1,.6),(.465,0,.02),.27)]
def load():
    inv=json.loads((ROOT/'Assets/Integration/GERMAN_RIFLE_FINISH_INVENTORY_20261003.json').read_text())
    expected=next(r['sha256'] for r in inv['files'] if r['path']==INPUT.relative_to(ROOT).as_posix())
    assert hashlib.sha256(INPUT.read_bytes()).hexdigest()==expected
    bpy.ops.wm.open_mainfile(filepath=str(INPUT),load_ui=False,use_scripts=False)
    meshes=sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.polygons),reverse=True)
    return meshes[0],meshes
def camera(n,e,t,scale):
    d=bpy.data.cameras.new(n);c=bpy.data.objects.new(n,d);bpy.context.scene.collection.objects.link(c)
    c.location=e;c.rotation_euler=(Vector(t)-c.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=100
    return c
def setup():
    s=bpy.context.scene;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.engine='BLENDER_WORKBENCH';s.view_settings.view_transform='AgX'
    sh=s.display.shading;sh.color_type='SINGLE';sh.single_color=(.62,.65,.69);sh.light='STUDIO';sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD'
    s.world=bpy.data.worlds.new('V8FixedWorld');return s,{n:camera(n,e,t,sc) for n,e,t,sc in VIEWS}
def pbr():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.14,.17,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    for n,pos,energy,size in [('Key',(0,-1.2,2),100,2),('Fill',(0,1,1),55,1.5),('Rim',(-.3,.5,1.6),65,1)]:
        d=bpy.data.lights.new(n,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
def save_export(meshes,out,name):
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_vertex_color='MATERIAL')
