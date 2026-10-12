"""Convert a jointly exported native FBX to a self-contained neutral GLB; validate fresh import."""
import bpy,json,hashlib,sys,traceback,math
from pathlib import Path
from mathutils import Vector
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
jobs=json.loads(Path(sys.argv[sys.argv.index('--jobs')+1]).read_text(encoding='utf8'))
for job in jobs:
 out=Path(job['output']);out.mkdir(parents=True,exist_ok=True);receipt=out/'fresh-validation-v3.json'
 if receipt.exists():continue
 report={'status':'running','id':job['id'],'errors':[]}
 try:
  src=Path(job['fbx']);assert sha(src)==job['fbx_sha256'],'FBX_CHANGED'
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(src),automatic_bone_orientation=False,use_anim=True)
  scene=bpy.context.scene;rigs=[o for o in scene.objects if o.type=='ARMATURE'];meshes=[o for o in scene.objects if o.type=='MESH']
  assert len(rigs)==1 and meshes,'MESH_OR_RIG_MISSING'
  rig=rigs[0];assert rig.animation_data and rig.animation_data.action,'ANIMATION_MISSING'
  action=rig.animation_data.action;action.name=job['name'];first,last=action.frame_range;assert last>first
  # FBX importer keys use integer fps; remove custom fps_base so seconds match those keys.
  scene.render.fps_base=1;fps=scene.render.fps;scene.frame_start=math.floor(first);scene.frame_end=math.ceil(last)
  mat=bpy.data.materials.new('Neutral preview');mat.diffuse_color=(.52,.58,.49,1);mat.use_nodes=True
  shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.52,.58,.49,1);shader.inputs['Roughness'].default_value=.68
  for obj in meshes:obj.data.materials.clear();obj.data.materials.append(mat)
  for obj in list(scene.objects):
   if obj.type not in ('MESH','ARMATURE','EMPTY'):bpy.data.objects.remove(obj,do_unlink=True)
  samples=[];sample_times=[]
  for fraction in (0,.22,.65,1):
   f=math.ceil(first)+round((math.floor(last)-math.ceil(first))*fraction);sample_times.append(f/fps);scene.frame_set(f);bpy.context.view_layer.update()
   samples.append({n:list((rig.matrix_world@b.matrix).translation) for n,b in rig.pose.bones.items()})
  scene.frame_set(scene.frame_start);path=out/'model.glb'
  assert path.is_file(),'GLB_MISSING'
  size=path.stat().st_size;assert size<=128*1024**2,'MODEL_TOO_LARGE'
  names=set(rig.data.bones.keys());mesh_count=len(meshes)
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));fresh=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];assert len(fresh)<=1
  new=fresh[0] if fresh else None
  assert names<=(set(new.data.bones.keys()) if new else set(bpy.data.objects.keys())),'BONES_LOST'
  assert any(o.animation_data and o.animation_data.action for o in bpy.context.scene.objects),'EXPORTED_ACTION_MISSING'
  errors=[]
  for seconds,expected in zip(sample_times,samples):
   f=seconds*bpy.context.scene.render.fps/bpy.context.scene.render.fps_base;bpy.context.scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
   errors.append(max((((new.matrix_world@new.pose.bones[n].matrix).translation if new else bpy.data.objects[n].matrix_world.translation)-Vector(x)).length for n,x in expected.items()))
  assert max(errors)<.005,('FRESH_POSE_MISMATCH',max(errors))
  assert sha(src)==job['fbx_sha256'],'FBX_CHANGED'
  report.update(status='ready',path=str(path),sha256=sha(path),size_bytes=size,mesh_count=mesh_count,bones=len(names),name=job['name'],duration=(last-first)/fps,fresh_pose_errors_m=errors,source_fbx_sha256=job['fbx_sha256'])
 except Exception:report.update(status='failed',errors=[traceback.format_exc()])
 receipt.write_text(json.dumps(report,indent=2));print('GLB',job['id'],report['status'],flush=True)
