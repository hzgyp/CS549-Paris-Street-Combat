"""Transient source/target reload views, no package saving or compatibility edits."""
import hashlib
import json
import math
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = os.environ.get('CS549_RELOAD_CATALOG_IDENTITY', 'compare_v2')
assert IDENTITY.replace('_', '').isalnum()
OUT = ROOT / 'Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload' / IDENTITY
OUT.mkdir(parents=True, exist_ok=True)
assert not (OUT / 'result.json').exists(), 'Preserve occupied comparison identity'
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'status': 'running',
          'scope': 'Current clip on current Allied mesh; D059 on its own source mannequin. Fixed diagnostic views, not matched FP contact or runtime replacement acceptance.',
          'clips': [], 'samples': [], 'images': [], 'errors': [], 'packages_saved': False}
def save():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

try:
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    # new_level creates a map package on disk. Use an untitled transient world
    # instead; keep the earlier diagnostic-only empty map as failure evidence.
    assert unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for pitch, yaw in [(-30,-135),(-25,45),(-15,90),(-15,-90)]:
        light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,300), unreal.Rotator(pitch=pitch,yaw=yaw))
        c = light.get_component_by_class(unreal.DirectionalLightComponent)
        c.set_intensity(12); c.set_cast_shadows(False)
    sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,300))
    c = sky.get_component_by_class(unreal.SkyLightComponent)
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_property('source_type',unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
    c.set_cubemap(unreal.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'))
    c.set_intensity(1); c.recapture_sky()
    camera = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0,350,105))
    cap = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    cap.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cap.set_editor_property('capture_every_frame',False)
    cap.set_editor_property('capture_on_movement',False)
    cap.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
    cap.set_editor_property('ortho_width',220)
    target = unreal.RenderingLibrary.create_render_target2d(world,720,800,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.06,.06,.06,1),False)
    cap.set_editor_property('texture_target',target)
    tests = [
        ('current_allied','/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Reload_2',
         '/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1'),
        ('d059_aim','/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP',
         '/Game/Rifle_01/Character/Mesh/SK_Mannequin'),
        ('d059_relaxed','/Game/Rifle_01/Animation/In-Place/W2_Stand_Relaxed_Reload_IP',
         '/Game/Rifle_01/Character/Mesh/SK_Mannequin')]
    for label, path, model in tests:
        clip, mesh = unreal.load_asset(path), unreal.load_asset(model)
        assert clip and mesh, (path, model)
        report['clips'].append({'label': label, 'clip':path, 'mesh':model,
            'duration_s':clip.get_play_length(), 'frames':unreal.AnimationLibrary.get_num_frames(clip),
            'root_motion':clip.get_editor_property('enable_root_motion'),
            'clip_skeleton':clip.get_editor_property('skeleton').get_path_name(),
            'mesh_skeleton':mesh.get_editor_property('skeleton').get_path_name()})
        for i, fraction in enumerate((0,.15,.3,.5,.7,.85,.999)):
            obj = actors.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(0,0,0))
            comp = obj.get_component_by_class(unreal.SkeletalMeshComponent)
            comp.set_skeletal_mesh_asset(mesh)
            comp.set_update_animation_in_editor(True)
            t = clip.get_play_length()*fraction
            comp.override_animation_data(clip,False,False,t,1)
            assert abs(comp.get_position()-t)<.001
            unreal.AutomationLibrary.finish_loading_before_screenshot()
            bones = {}
            for bone in ('root','pelvis','hand_l','hand_r','lowerarm_l','lowerarm_r','thumb_03_l','index_03_r'):
                v = comp.get_bone_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT).translation
                bones[bone] = [v.x,v.y,v.z]
                assert all(math.isfinite(x) for x in bones[bone])
            report['samples'].append({'label':label,'fraction':fraction,'time_s':t,'bones_cm':bones})
            for view, location in [('front',(0,-350,100)),('side',(350,0,100))]:
                pos = unreal.Vector(*location)
                camera.set_actor_location(pos,False,False)
                camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(pos,unreal.Vector(0,0,95)),False)
                cap.capture_scene()
                filename=f'{label}_{i:02d}_{view}.png'
                unreal.RenderingLibrary.export_render_target(world,target,str(OUT),filename)
                report['images'].append({'file':filename,'label':label,'view':view,'fraction':fraction,'time_s':t})
            actors.destroy_actor(obj)
            save()
        samples = [s for s in report['samples'] if s['label']==label]
        report['clips'][-1]['left_hand_excursion_cm'] = max(math.dist(samples[0]['bones_cm']['hand_l'],s['bones_cm']['hand_l']) for s in samples)
        assert report['clips'][-1]['left_hand_excursion_cm']>1, 'Reject stale animation poses'
        save()
    report['status']='captured_source_comparison_pending_image_review'
except Exception:
    report['errors'].append(traceback.format_exc()); report['status']='failed'
finally:
    save()
    unreal.log('CS549_RELOAD_CATALOG_REVIEW '+report['status'])
    unreal.SystemLibrary.quit_editor()
