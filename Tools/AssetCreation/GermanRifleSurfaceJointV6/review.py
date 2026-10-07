"""Fixed diagnostic cameras for original/candidate and fresh GLB checks."""
import argparse,json,sys,math
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe import load,camera,setup
p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--proof-blend');p.add_argument('--output',required=True);p.add_argument('--clay-only',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
if a.proof_blend:
    bpy.ops.wm.open_mainfile(filepath=str(Path(a.proof_blend).resolve()),load_ui=False,use_scripts=False)
elif a.input:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))
else:load()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];s=setup();s.view_settings.view_transform='AgX'
s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.62,.65,.69)
views=[('ball_side',(-.15,-2,.075),(-.15,-.035,.075),.16),('ball_top',(-.15,-.035,2),(-.15,-.035,.075),.16),
       ('ball_underside',(-.3,-.4,-.1),(-.15,-.035,.075),.18),
       ('receiver_quarter',(.1,-1,.7),(-.1,0,.075),.46),('whole_side',(0,-3,0),(0,0,0),1.3)]
cams={n:camera(n,e,t,scale) for n,e,t,scale in views}
if a.proof_blend:
    cams={'ball_underside':cams['ball_underside']};s.display.shading.color_type='MATERIAL'
for n,c in cams.items():s.camera=c;s.render.filepath=str(out/('clay_'+n+'.png'));bpy.ops.render.render(write_still=True)
if not a.clay_only:
    s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.14,.17,1)
    s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    for n,pos,energy,size in [('Key',(0,-1.2,2),100,2),('Fill',(0,1,1),55,1.5),('Rim',(-.3,.5,1.6),65,1)]:
        d=bpy.data.lights.new(n,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=pos
        o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    for n in ('ball_side','receiver_quarter','whole_side'):
        s.camera=cams[n];s.render.filepath=str(out/('pbr_'+n+'.png'));bpy.ops.render.render(write_still=True)
rows=[{'name':o.name,'triangles':len(o.data.polygons),'uv':[u.name for u in o.data.uv_layers],
       'materials':[m.name for m in o.data.materials],'finite':all(math.isfinite(x) for v in o.data.vertices for x in v.co)} for o in meshes]
(out/'review.json').write_text(json.dumps({'freshGlbImport':bool(a.input),'meshes':rows,'views':list(cams),'pbr':not a.clay_only},indent=2),encoding='utf-8')
