"""Fresh import and fixed material-boundary/detail views; unedited GLB evidence."""
import argparse,json,hashlib,sys,math
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--final',action='store_true');p.add_argument('--detail',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);src=Path(a.input).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src))
mesh=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in mesh:o.data.calc_loop_triangles()
parts=[{'name':o.name,'parent':o.parent.name if o.parent else None,'triangles':len(o.data.loop_triangles),
        'uv':[u.name for u in o.data.uv_layers],'colors':[c.name for c in o.data.color_attributes],
        'materials':[m.name for m in o.data.materials],'finite':all(math.isfinite(x) for v in o.data.vertices for x in v.co)} for o in mesh]
s=bpy.context.scene;s.render.resolution_x=1440;s.render.resolution_y=810;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.world=bpy.data.worlds.new('FixedWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.14,.17,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
s.view_settings.view_transform='AgX'
def cam(n,e,t,scale):
    d=bpy.data.cameras.new(n);c=bpy.data.objects.new(n,d);s.collection.objects.link(c);c.location=e;c.rotation_euler=(Vector(t)-c.location).to_track_quat('-Z','Y').to_euler()
    d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=100;return c
views=[('receiver_side',(-.1,-2,.08),(-.1,0,.08),.46),('receiver_top',(-.1,0,2),(-.1,0,.08),.46),('receiver_quarter',(.1,-1,.7),(-.1,0,.075),.46),
       ('right_side',(0,-3,0),(0,0,0),1.3),('reverse_quarter',(-.75,2,1.2),(0,0,0),1.3),('three_quarter',(.75,-2,1.2),(0,0,0),1.3)]
if a.final:views += [('left_side',(0,3,0),(0,0,0),1.3),('top',(0,0,3),(0,0,0),1.3),('bottom',(0,0,-3),(0,0,0),1.3),('muzzle_quarter',(.72,-1,.6),(.465,0,.02),.27)]
if a.detail:views=views[:3]
cams={n:cam(n,e,t,scale) for n,e,t,scale in views}
s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.color_type='SINGLE';sh.single_color=(.62,.65,.69);sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';sh.show_object_outline=False
for n,c in cams.items():s.camera=c;s.render.filepath=str(out/('clay_'+n+'.png'));bpy.ops.render.render(write_still=True)
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
for n,pos,energy,size in [('Key',(0,-1.2,2),100,2),('Fill',(0,1,1),55,1.5),('Rim',(-.3,.5,1.6),65,1)]:
    d=bpy.data.lights.new(n,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
for n,c in cams.items():s.camera=c;s.render.filepath=str(out/('pbr_'+n+'.png'));bpy.ops.render.render(write_still=True)
s.camera=cams.get('three_quarter',cams['receiver_quarter']);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'Kar98k_SurfaceReview_V4.blend'))
r={'inputSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'parts':parts,'triangles':sum(p['triangles'] for p in parts),
   'images':[{'name':i.name,'packed':bool(i.packed_file),'size':list(i.size),'sha256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None} for i in bpy.data.images],
   'views':list(cams),'dataValid':all(p['finite'] and p['uv'] and p['materials'] for p in parts),'visualPass':'Not inferred; inspect actual PNGs'}
(out/'review.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
