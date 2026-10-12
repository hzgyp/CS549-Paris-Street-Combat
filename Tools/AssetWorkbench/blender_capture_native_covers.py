"""Open each UE-exported mesh with its own action and capture honest neutral-material views."""
import bpy,json,hashlib,traceback,sys,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'Assets/LocalWorking/AssetWorkbench/native-covers-v1'
for receipt in sorted(BASE.glob('anim-*/export-v3/result.json')):
 if '--only' in sys.argv and sys.argv[sys.argv.index('--only')+1] not in str(receipt):continue
 source=json.loads(receipt.read_text());out=receipt.parent.parent/'capture-v4';out.mkdir(exist_ok=True);result=out/'result.json'
 if result.exists():continue
 if source['status']!='exported':continue
 report={**source,'status':'running','captures':[],'errors':[],'renderer':'Blender '+bpy.app.version_string+' Workbench','neutral_material':True}
 def save():result.write_text(json.dumps(report,indent=2))
 save()
 try:
  file=receipt.parent/'source-action.fbx';assert hashlib.sha256(file.read_bytes()).hexdigest()==source['fbx_sha256']
  bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=30
  model=receipt.parent/'source-mesh.fbx';assert hashlib.sha256(model.read_bytes()).hexdigest()==source['mesh_fbx_sha256']
  bpy.ops.import_scene.fbx(filepath=str(model),automatic_bone_orientation=False,use_anim=False)
  meshes=[o for o in scene.objects if o.type=='MESH'];rigs=[o for o in scene.objects if o.type=='ARMATURE'];assert meshes and len(rigs)==1,'FBX lacks mesh or one rig'
  target=rigs[0];before=set(scene.objects)
  bpy.ops.import_scene.fbx(filepath=str(file),automatic_bone_orientation=False,use_anim=True)
  added=set(scene.objects)-before;src=next(o for o in added if o.type=='ARMATURE');assert src.animation_data and src.animation_data.action
  bpy.context.view_layer.update();shared=set(target.data.bones.keys())&set(src.data.bones.keys());assert len(shared)>=min(10,len(target.data.bones))
  error=max(((target.matrix_world@target.data.bones[n].matrix_local).translation-(src.matrix_world@src.data.bones[n].matrix_local).translation).length for n in shared)
  assert error<.03,('FBX bind mismatch',error)
  target.animation_data_create();target.animation_data.action=src.animation_data.action
  if target.animation_data.action.slots:target.animation_data.action_slot=target.animation_data.action.slots[0]
  for o in added:bpy.data.objects.remove(o,do_unlink=True)
  report['bind_error_m']=error
  assert any(r.animation_data and r.animation_data.action for r in rigs),'FBX lacks active bone action'
  action=next(r.animation_data.action for r in rigs if r.animation_data and r.animation_data.action);first,last=action.frame_range
  fps=scene.render.fps
  assert last>first and abs((last-first)/fps-source['duration'])<max(.08,2/fps),('duration mismatch',first,last,source['duration'],fps)
  report['import_fps']=fps
  scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=800;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
  sh=scene.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.5;sh.color_type='SINGLE';sh.single_color=(.55,.6,.53);sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD'
  scene.world=bpy.data.worlds.new('Preview background');scene.world.color=(.12,.135,.12)
  camera=bpy.data.objects.new('CoverCamera',bpy.data.cameras.new('CoverCamera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.lens=50
  report.update(mesh_count=len(meshes),bone_count=sum(len(r.data.bones) for r in rigs),action_frames=[first,last])
  for index,fraction in enumerate([.22,.65]):
   frame=first+source['duration']*fps*fraction;scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();points=[]
   for o in meshes:
    ev=o.evaluated_get(deps);points.extend(ev.matrix_world@v.co for v in ev.data.vertices)
   low=Vector([min(p[i] for p in points) for i in range(3)]);high=Vector([max(p[i] for p in points) for i in range(3)]);center=(low+high)*.5;size=high-low;radius=max(size.length*.5,.001)
   assert all(math.isfinite(x) for x in size) and max(size)>0
   camera.location=center+Vector((1,-1.8,.55)).normalized()*radius*4;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=radius*2.65;camera.data.clip_start=max(radius/1000,.00001);camera.data.clip_end=radius*100
   image=out/f'frame-{index}.png';scene.render.filepath=str(image);bpy.ops.render.render(write_still=True)
   assert image.is_file()
   bones={}
   for r in rigs:
    for name in ['root','pelvis','head','hand_l','hand_r']:
     if name in r.pose.bones:bones[name]=list((r.matrix_world@r.pose.bones[name].matrix).translation)
   report['captures'].append(dict(file=image.name,time=source['duration']*fraction,fraction=fraction,sha256=hashlib.sha256(image.read_bytes()).hexdigest(),center=list(center),extent=list(size*.5),bones=bones));save()
  assert hashlib.sha256(file.read_bytes()).hexdigest()==source['fbx_sha256'];report['status']='captured_pending_visual_review'
 except Exception:report['status']='failed';report['errors'].append(traceback.format_exc())
 save();print('BLENDER_COVER',source['id'],report['status'],flush=True)
