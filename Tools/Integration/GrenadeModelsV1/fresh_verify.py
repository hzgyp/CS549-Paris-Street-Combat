import bpy,json,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3];kind=sys.argv[sys.argv.index('--')+1]
base=root/'Assets/LocalWorking/Experiments/GrenadeModels/20261011'
src=base/'frag_finish_v1/MkIIExisting.glb' if kind=='frag' else base/'smoke/finish_v1/ANM8Smoke.glb'
out=base/(kind+'_fresh_v1');out.mkdir(exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src));scene=bpy.context.scene
meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==1;o=meshes[0];o.data.calc_loop_triangles()
assert len(o.data.loop_triangles)>2000 and len(o.data.uv_layers)>0
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('FreshWorld');scene.world.color=(.18,.18,.18);scene.view_settings.exposure=-1.3
for name,loc,power in [('key',(.5,-.6,.65),40),('fill',(-.5,-.2,.4),30),('rim',(.2,.5,.5),40)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=.5;b=bpy.data.objects.new(name,d);scene.collection.objects.link(b);b.location=loc;b.rotation_euler=(-b.location).to_track_quat('-Z','Y').to_euler()
for name,loc in [('front',(.23,-.4,.20)),('side',(.4,.03,.06)),('rear',(-.25,.35,.16)),('bottom',(.15,-.2,-.4))]:
    d=bpy.data.cameras.new(name);c=bpy.data.objects.new(name,d);scene.collection.objects.link(c);c.location=loc;c.rotation_euler=(-c.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=.19 if kind=='frag' else .22;scene.camera=c;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
(out/'REPORT.json').write_text(json.dumps(dict(kind=kind,triangles=len(o.data.loop_triangles),vertices=len(o.data.vertices),dimensions_m=list(o.dimensions),uv_layers=len(o.data.uv_layers),materials=[m.name for m in o.data.materials],source=str(src),new_process=True),indent=2),encoding='utf-8')
