"""Unsaved Blueprint-mesh reload pose views; not live input/FP contact acceptance."""
import hashlib
import json
import math
import os
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY=os.environ.get('CS549_RELOAD_VIEW_IDENTITY','Views_v2')
assert IDENTITY in ('Views_v1','Views_v2')
OUT=STORE/'Evidence/P4/SimplifiedReload20261002'/IDENTITY
OUT.mkdir(parents=True,exist_ok=True)
DEST=OUT/'pose_views.json'
assert not DEST.exists(), 'Preserve existing pose evidence'
MAP='/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001'
map_file=STORE/'Content/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001.umap'
before=hashlib.sha256(map_file.read_bytes()).hexdigest()
assert unreal.EditorLevelLibrary.load_level(MAP)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for actor in actors.get_all_level_actors():
    if isinstance(actor,unreal.Character):actors.destroy_actor(actor)
camera=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(380,0,140))
capture=camera.get_component_by_class(unreal.SceneCaptureComponent2D)
capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
capture.set_editor_property('capture_every_frame',False)
capture.set_editor_property('capture_on_movement',False)
capture.set_editor_property('fov_angle',35)
target=unreal.RenderingLibrary.create_render_target2d(world,800,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(0,0,0,1),False)
capture.set_editor_property('texture_target',target)
clip=unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Reload_2')
duration=clip.get_play_length()
report={'engine':unreal.SystemLibrary.get_engine_version(),'scope':'Static sampled poses on actual saved player/NPC Blueprint meshes. Separate native-world probes exercise action logic. Empty hands, no M1/FP/contact acceptance. No map/mesh/animation saved.', 'captures':[],'joints':[]}
prefix='/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/'
for name in ('BP_PCPlayerReloadV1','BP_PCNPCReloadV1'):
    cls=unreal.EditorAssetLibrary.load_blueprint_class(prefix+name)
    actor=actors.spawn_actor_from_class(cls,unreal.Vector(0,0,95))
    mesh=actor.get_component_by_class(unreal.SkeletalMeshComponent)
    mesh.set_update_animation_in_editor(True)
    for index,fraction in enumerate((0,.25,.5,.75,.999)):
        time_s=duration*fraction
        # UE only initializes saved AnimationData when switching to single-node
        # mode. Repeating OverrideAnimationData in that same mode left v1 at
        # its first pose. Force a new transient instance before each sample.
        mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
        mesh.override_animation_data(clip,False,False,time_s,1)
        assert abs(mesh.get_position()-time_s)<.001
        unreal.AutomationLibrary.finish_loading_before_screenshot()
        for bone in ('root','pelvis','head','upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r','thigh_l','calf_l','foot_l','thigh_r','calf_r','foot_r'):
            t=mesh.get_bone_transform(bone,unreal.RelativeTransformSpace.RTS_WORLD)
            v=[t.translation.x,t.translation.y,t.translation.z]
            assert all(math.isfinite(x) for x in v)
            report['joints'].append({'class':name,'time_s':time_s,'bone':bone,'world_cm':v})
        for view,loc in (('front',unreal.Vector(380,0,140)),('side',unreal.Vector(0,380,140))):
            camera.set_actor_location(loc,False,False)
            camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(0,0,95)),False)
            unreal.AutomationLibrary.finish_loading_before_screenshot()
            capture.capture_scene()
            filename=f'{name}_{index}_{view}.png'
            assert not (OUT/filename).exists()
            unreal.RenderingLibrary.export_render_target(world,target,str(OUT),filename)
            report['captures'].append({'file':filename,'class':name,'time_s':time_s,'view':view})
    for bone in ('hand_l','hand_r'):
        values=[e['world_cm'] for e in report['joints'] if e['class']==name and e['bone']==bone]
        assert max(math.dist(values[0],v) for v in values)>1, 'Reject stale pose sampling'
    actors.destroy_actor(actor)
assert before==hashlib.sha256(map_file.read_bytes()).hexdigest()
report['saved_map_unchanged']=True
report['status']='complete_static_pose_views_pending_visual_review'
DEST.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
unreal.log('CS549_RELOAD_POSE_VIEWS_COMPLETE')
