"""Load this isolated source package and capture its own real skeletal animation."""
import unreal,json,traceback,hashlib,time,math,os
from pathlib import Path
project=Path(unreal.Paths.project_dir()).resolve();job_dir=os.environ.get('COVER_JOB_DIR');OUT=(Path(job_dir)/'capture-v2') if job_dir else project.parent/'capture-v1';OUT.mkdir(exist_ok=True)
report={'engine':unreal.SystemLibrary.get_engine_version(),'status':'running','errors':[],'captures':[],'packages_saved':False}
def save():(OUT/'result.json').write_text(json.dumps(report,indent=2),encoding='utf8')
save()
try:
 registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
 records=registry.get_assets_by_path('/Game',recursive=True)
 if job_dir:
  allowed=set(json.loads((Path(job_dir)/'allowed-packages.json').read_text()));records=[a for a in records if str(a.package_name) in allowed]
 meshes=[a for a in records if str(a.asset_class_path.asset_name)=='SkeletalMesh']
 clips=[a for a in records if str(a.asset_class_path.asset_name)=='AnimSequence']
 report['mesh_candidates']=[str(a.package_name) for a in meshes];report['clip_count']=len(clips);save()
 def rank(a):
  n=str(a.asset_name).lower();return (any(x in n for x in ('additive','aimoffset','tpose','reference','ref_pose')),0 if any(x in n for x in ('attack','walk','run','idle')) else 1,n)
 chosen=None
 for a in sorted(clips,key=rank)[:60]:
  anim=a.get_asset()
  if not anim or anim.get_play_length()<=0:continue
  skeleton=anim.get_editor_property('skeleton')
  if not skeleton:continue
  for m in sorted(meshes,key=lambda x:('mannequin' not in str(x.asset_name).lower(),str(x.asset_name))):
   mesh=m.get_asset()
   if mesh and mesh.get_editor_property('skeleton')==skeleton:
    chosen=(mesh,anim,skeleton);break
  if chosen:break
 assert chosen,'No own mesh and matching nonempty clip'
 mesh,anim,skeleton=chosen
 report.update(mesh=mesh.get_path_name(),animation=anim.get_path_name(),skeleton=skeleton.get_path_name(),duration=anim.get_play_length())
 assert unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 for pitch,yaw,intensity in [(-30,-135,8),(-25,45,5),(-15,90,3)]:
  light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,300),unreal.Rotator(pitch=pitch,yaw=yaw));c=light.get_component_by_class(unreal.DirectionalLightComponent);c.set_intensity(intensity);c.set_cast_shadows(False)
 sky=actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,300));c=sky.get_component_by_class(unreal.SkyLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('source_type',unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);c.set_cubemap(unreal.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'));c.set_intensity(1);c.recapture_sky()
 actor=actors.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(0,0,0));comp=actor.get_component_by_class(unreal.SkeletalMeshComponent);comp.set_skeletal_mesh_asset(mesh);comp.set_update_animation_in_editor(True)
 camera=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(350,350,100));cap=camera.get_component_by_class(unreal.SceneCaptureComponent2D)
 cap.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR);cap.set_editor_property('capture_every_frame',False);cap.set_editor_property('capture_on_movement',False);cap.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
 target=unreal.RenderingLibrary.create_render_target2d(world,800,600,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.04,.04,.04,1),False);cap.set_editor_property('texture_target',target)
 for index,fraction in enumerate([.22,.65]):
  moment=anim.get_play_length()*fraction;comp.override_animation_data(anim,False,False,moment,1)
  unreal.AutomationLibrary.finish_loading_before_screenshot()
  center,extent=actor.get_actor_bounds(False);radius=max(extent.x,extent.y,extent.z,30)
  # Square sphere budget accommodates source root motion and non-human rigs.
  cap.set_editor_property('ortho_width',radius*3.8)
  point=center+unreal.Vector(radius*2.7,radius*3.5,radius*.7);camera.set_actor_location(point,False,False);camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(point,center),False)
  for _ in range(3):cap.capture_scene()
  file=OUT/f'frame-{index}.png';unreal.RenderingLibrary.export_render_target(world,target,str(OUT),file.name)
  assert file.is_file() and file.stat().st_size>1000
  bones={}
  for bone in ['root','pelvis','head','hand_l','hand_r']:
   v=comp.get_bone_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT).translation;bones[bone]=[v.x,v.y,v.z]
  report['captures'].append(dict(file=file.name,time=moment,fraction=fraction,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),center=[center.x,center.y,center.z],extent=[extent.x,extent.y,extent.z],bones=bones));save()
 report['status']='captured_pending_visual_review'
except Exception:report['status']='failed';report['errors'].append(traceback.format_exc())
save()
