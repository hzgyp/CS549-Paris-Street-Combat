"""One unsaved gun translation to a verified fixed index pad; native textures."""
import math
import os
import sys
import time
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).parent))
from common import *
import transform_math as tm

IDENTITY = os.environ['CS549_ALLIED_TRANSLATION_ID']
assert IDENTITY.replace('_', '').isalnum()
OUT = BASE / IDENTITY
assert not OUT.exists(), 'Preserve occupied identity'
OUT.mkdir(parents=True)
FIT = BASE / 'stock_pivot_v1/result.json'
fit = read(FIT)
assert fit['status'] == 'stopped_contact_gate' and fit['inputs_unchanged']
assert fit['reference_alignment']['max_cm'] < .01
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
r = {'scope': __doc__, 'errors': [], 'pid': os.getpid(), 'status': 'starting',
     'guards_before': guards(), 'captures': [], 'map_saved': False,
     'formal_selected': False, 'rotation_changed': False, 'hand_pose_changed': False,
     'support_fitted': False, 'contact_or_gameplay_accepted': False,
     'landmark_proof_sha256': sha(FIT)}
write(OUT / 'source.json', {'identity': IDENTITY, 'sha256': sha(Path(__file__))})
start = time.monotonic()
ready = ending = callback = world = soldier = gun = capture = target = None
index = 0
requested = None
busy = moved = False
views = [('before_right','right',78), ('after_right','right',78),
         ('after_front','front',78), ('after_top','top',78),
         ('after_context','right',155), ('after_trigger','right',30)]

def xyz(v): return [v.x, v.y, v.z]
def encoded(t):
    return {'t':xyz(t.translation), 'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],
            's':xyz(t.scale3d)}
def save(): write(OUT / 'result.json', r)
def bones():
    m = soldier.mesh
    return {str(m.get_bone_name(i)): encoded(m.get_socket_transform(m.get_bone_name(i),
        unreal.RelativeTransformSpace.RTS_WORLD)) for i in range(m.get_num_bones())}

def finish(error=None):
    global ending
    if ending is not None: return
    if error: r['errors'].append(error)
    try: r['guards_after'] = guards()
    except Exception: r['errors'].append(traceback.format_exc())
    r['status'] = 'failed_preserved' if r['errors'] else 'translated_native_views_require_user_review'
    save()
    if world:
        unreal.GameplayStatics.set_game_paused(world, False)
        levels.editor_request_end_play()
    ending = time.monotonic()

def tick(delta):
    global ready, ending, callback, world, soldier, gun, capture, target, index, requested, busy, moved
    if busy: return
    busy = True
    try:
        if ending is not None:
            if time.monotonic()-ending > 3:
                unreal.unregister_slate_post_tick_callback(callback)
                unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start < 240, 'Capture deadline'
        world = editor.get_game_world()
        player = unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player: return
        if ready is None:
            soldier = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character)
                if a.get_actor_label() == 'PC_City_Ally1')
            gun = soldier.get_editor_property('WeaponAppearance')
            assert gun and gun.get_editor_property('GripMesh') == soldier.mesh
            assert gun.get_editor_property('Combatant') == soldier
            assert 'RifleAttachmentV3' in gun.get_class().get_name()
            assert 'SK_WWII_US_Paratrooper_simple_UE582_v1' in soldier.mesh.get_skeletal_mesh_asset().get_path_name()
            capture = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SceneCapture2D)
                if a.get_actor_label() == 'PC_AlliedTranslationCapture').get_component_by_class(unreal.SceneCaptureComponent2D)
            target = unreal.RenderingLibrary.create_render_target2d(world,1600,1000,
                unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
            capture.set_editor_property('texture_target',target)
            capture.set_editor_property('primitive_render_mode',unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
            capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
            capture.set_editor_property('capture_every_frame',False)
            capture.set_editor_property('capture_on_movement',False)
            capture.set_editor_property('show_flag_settings',[unreal.EngineShowFlagsSetting(show_flag_name=n,enabled=False)
                for n in ('Fog','Atmosphere','Bloom','DepthOfField','MotionBlur')])
            ready = time.monotonic()
            return
        if time.monotonic()-ready < 15: return
        if 'before' not in r:
            assert str(soldier.get_editor_property('ActionState')) == 'Ready'
            assert soldier.get_velocity().length() < .1
            assert unreal.GameplayStatics.set_game_paused(world,True)
            component = gun.get_component_by_class(unreal.StaticMeshComponent)
            assert 'SM_M1_Garand' in component.get_editor_property('static_mesh').get_path_name()
            collision = str(component.get_collision_enabled())
            r['unchanged_collision_mode'] = collision
            assert collision == fit['pose_source']['collision'], 'Preserve the actual baseline collision policy'
            r['before'] = {'bones':bones(), 'gun_world':encoded(component.get_world_transform()),
                'mesh_world':encoded(soldier.mesh.get_world_transform()),
                'gun_class':gun.get_class().get_path_name(), 'mesh':soldier.mesh.get_skeletal_mesh_asset().get_path_name(),
                'materials':[soldier.mesh.get_material(i).get_path_name() for i in range(soldier.mesh.get_num_materials())]}
            old = fit['pose_source']
            errors = tm.index_errors(old['bone_world'],r['before']['bones'])
            r['unchanged_index_local_rotation_error_deg'] = errors
            save()
            assert max(errors.values()) < .05, 'Reconstruct a changed source index before fitting'
            r['landmarks'] = tm.landmarks(fit,r['before'])
            save()
        if index >= len(views): finish(); return
        name,axis,width = views[index]
        if index == 1 and not (OUT/'early_acceptance.json').is_file(): return
        if name.startswith('after') and not moved:
            # ONE preparation change. Native world stays paused; no per-frame
            # Python fitting and no change to the saved V3 attachment graph.
            gun.set_actor_location(gun.get_actor_location()+unreal.Vector(*r['landmarks']['delta_world_cm']),False,False)
            moved = True
            component = gun.get_component_by_class(unreal.StaticMeshComponent)
            after = encoded(component.get_world_transform())
            r['after'] = {'gun_world':after,'bones':bones()}
            assert after['q'] == r['before']['gun_world']['q'] and after['s'] == r['before']['gun_world']['s']
            assert r['after']['bones'] == r['before']['bones'], 'Character pose moved'
            blade_now = unreal.Vector(*tm.point(after,r['landmarks']['blade_gun_cm']))
            residual = (blade_now-unreal.Vector(*r['landmarks']['pad_world_cm'])).length()
            r['landmark_residual_cm'] = residual
            save()
            assert residual < .01
        if requested is None:
            rh,lh = soldier.mesh.get_socket_location('hand_r'),soldier.mesh.get_socket_location('hand_l')
            center = (rh+lh)/2
            if name == 'after_context': center = (center+soldier.mesh.get_socket_location('spine_03'))/2
            if name == 'after_trigger': center = unreal.Vector(*r['landmarks']['pad_world_cm'])
            direction = {'front':soldier.get_actor_forward_vector(),'right':soldier.get_actor_right_vector(),
                'top':unreal.Vector(0,0,1)}[axis]
            eye = center+direction*250
            rotation = unreal.MathLibrary.find_look_at_rotation(eye,center)
            if axis == 'top': rotation = unreal.Rotator(pitch=-90,yaw=soldier.get_actor_rotation().yaw,roll=0)
            capture.set_world_location(eye,False,False)
            capture.set_world_rotation(rotation,False,False)
            capture.set_editor_property('ortho_width',width)
            capture.clear_show_only_components()
            capture.set_editor_property('show_only_actors',[soldier,gun])
            capture.capture_scene()
            requested = time.monotonic()
            r['captures'].append({'file':name+'.png','view':axis,'width_cm':width,
                'eye_cm':xyz(eye),'target_cm':xyz(center)})
            save()
            return
        if time.monotonic()-requested < 1.5: return
        unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),name+'.png')
        assert (OUT/(name+'.png')).stat().st_size > 15000
        assert bones() == r['before']['bones'], 'Stale or drifting character capture'
        expected = r['after']['gun_world'] if moved else r['before']['gun_world']
        current = encoded(gun.get_component_by_class(unreal.StaticMeshComponent).get_world_transform())
        drift = (unreal.Vector(*current['t'])-unreal.Vector(*expected['t'])).length()
        assert drift < .01 and current['q'] == expected['q'] and current['s'] == expected['s']
        r['captures'][-1]['gun_drift_cm'] = drift
        save()
        index += 1
        requested = None
    except Exception: finish(traceback.format_exc())
    finally: busy = False

try:
    cap = actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(),unreal.Rotator())
    cap.set_actor_label('PC_AlliedTranslationCapture')
    for pitch,yaw in ((-25,45),(-25,-135),(-20,135),(-20,-45)):
        light = actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,300),unreal.Rotator(pitch=pitch,yaw=yaw))
        light.set_actor_label('PC_AlliedTranslationFill')
        component = light.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_intensity(6)
        component.set_cast_shadows(False)
    save()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
    levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status'] = 'failed_startup'
    save()
    unreal.SystemLibrary.quit_editor()
