"""Unsaved full-body eye-level camera feasibility; no weapon-contact claim."""
import hashlib
import json
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/P3/FullBodyView_v2'
OUT.mkdir(parents=True,exist_ok=True)
DEST=OUT/'fullbody_view_v2.json'
if DEST.exists():
    raise RuntimeError('Refusing existing view evidence')
MAP='/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001'
map_file=STORE/'Content/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001.umap'
before=hashlib.sha256(map_file.read_bytes()).hexdigest()
assert unreal.EditorLevelLibrary.load_level(MAP)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
player=None
for a in actors.get_all_level_actors():
    if isinstance(a,unreal.Character):
        if a.get_actor_label()=='P2_Lifecycle_1_Allied_A':
            player=a
        else:
            actors.destroy_actor(a)
assert player
mesh=player.get_component_by_class(unreal.SkeletalMeshComponent)
mesh.set_update_animation_in_editor(True)
camera=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(0,0,200))
capture=camera.get_component_by_class(unreal.SceneCaptureComponent2D)
capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
capture.set_editor_property('capture_every_frame',False)
capture.set_editor_property('capture_on_movement',False)
capture.set_editor_property('fov_angle',90)
capture.set_editor_property('override_custom_near_clipping_plane',True)
capture.set_editor_property('custom_near_clipping_plane',1)
target=unreal.RenderingLibrary.create_render_target2d(world,1280,720,unreal.TextureRenderTargetFormat.RTF_RGBA8,
    unreal.LinearColor(0,0,0,1),False)
capture.set_editor_property('texture_target',target)
report={'engine':unreal.SystemLibrary.get_engine_version(),'scope':'Fixed eye-level full-body camera, empty-hand generic rifle clips; no saved asset changes, accepted FP view, weapon attachment or grip/reload mechanics',
        'fov_horizontal_deg':90,'near_clip_cm':1,'captures':[],
        'prior_attempt':'FullBodyView v1 used positional Rotator arguments: its -25 value was roll, not pitch. Preserve v1 but do not claim down-look acceptance.'}
for action,time in (('Rifle_Idle',0),('Rifle_ShootOnce',.3),('Rifle_Reload_2',.3),('Rifle_Reload_2',1),('Rifle_Reload_2',1.8)):
    mesh.override_animation_data(unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/'+action),False,False,time,1)
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    # Camera remains at idle eye height; do not make it follow reload head bob.
    if not report['captures']:
        head=mesh.get_bone_transform('head',unreal.RelativeTransformSpace.RTS_WORLD).translation
        report['camera_world_cm']=[head.x+8,head.y,head.z+10]
    loc=unreal.Vector(*report['camera_world_cm'])
    for hidden in (False,True):
        if hidden:
            mesh.hide_bone_by_name('head',unreal.PhysBodyOp.PBO_NONE)
        else:
            mesh.un_hide_bone_by_name('head')
        # Pose update occurs before capturing; no model deletion or save.
        unreal.AutomationLibrary.finish_loading_before_screenshot()
        for pitch in (0,-25):
            camera.set_actor_location(loc,False,False)
            camera.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=0,roll=0),False)
            capture.capture_scene()
            name='%s_%03d_head%s_pitch%d.png'%(action,round(time*100),'hidden' if hidden else 'visible',pitch)
            assert not (OUT/name).exists()
            unreal.RenderingLibrary.export_render_target(world,target,str(OUT),name)
            report['captures'].append({'file':name,'head_hidden':hidden,'pitch':pitch,'action':action,'time_s':time})
mesh.un_hide_bone_by_name('head')
report['saved_map_hash_unchanged']=before==hashlib.sha256(map_file.read_bytes()).hexdigest()
assert report['saved_map_hash_unchanged']
DEST.write_text(json.dumps(report,indent=2),encoding='utf-8')
unreal.log('CS549_FULLBODY_VIEW_PROBE_DONE')
