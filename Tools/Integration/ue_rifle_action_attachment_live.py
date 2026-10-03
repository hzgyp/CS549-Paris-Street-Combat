"""Fresh unselected gun-only actor on actual player/motions; no native saves."""
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/RifleActionAttachmentV3' / os.environ['CS549_RIFLE_ACTION_LIVE_IDENTITY']
assert OUT.name.replace('_', '').isalnum() and not OUT.exists()
OUT.mkdir(parents=True)
inventory = json.loads((ROOT / 'Assets/Integration/CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json').read_text())
deps = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text())
author_name = os.environ['CS549_RIFLE_ACTION_SOURCE_AUTHOR']
assert author_name.replace('_', '').isalnum()
author = json.loads((OUT.parent / author_name / 'result.json').read_text())
assert author['status'] == 'saved_unselected_rifle_actor_requires_fresh_runtime_review' and not author['errors']
records = inventory['files'] + deps['files'] + inventory['retained_unselected_rejected_trial'] + [author['saved_trial']]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert all(digest(ROOT / e['path']) == e['sha256'] for e in records)
report = {'scope': __doc__, 'status': 'initializing', 'errors': [], 'captures': [], 'frames': [], 'samples': []}
moving_reload = os.environ.get('CS549_RIFLE_MOVING_RELOAD', '0') == '1'
report['moving_reload_requested'] = moving_reload
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
callback = None
phase = 'waiting'
phase_start = 0
started = time.monotonic()
in_tick = False
ending_at = 0

def write():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2))

def xyz(v):
    return [v.x, v.y, v.z]

def center(side):
    fs = ('middle', 'ring', 'pinky') if side == 'r' else ('index', 'middle', 'ring', 'pinky')
    ns = [f+'_0'+str(s)+'_'+side for f in fs for s in (2, 3)] + ['thumb_02_'+side, 'thumb_03_'+side]
    return sum((mesh.get_socket_location(n) for n in ns), unreal.Vector()) / len(ns)

def views(stem):
    mid = (mesh.get_socket_location('hand_l') + mesh.get_socket_location('hand_r')) / 2
    for label, offset, fov in (('side', unreal.Vector(150, -110, 70), 50),
                               ('front', unreal.Vector(160, 120, 50), 50), ('fp', None, 90)):
        if offset is not None:
            point = mid + offset
            rotation = unreal.MathLibrary.find_look_at_rotation(point, mid)
        else:
            eye = pawn.get_component_by_class(unreal.CameraComponent)
            point, rotation = eye.get_world_location(), eye.get_world_rotation()
        camera.set_actor_location(point, False, False)
        camera.set_actor_rotation(rotation, False)
        capture.set_editor_property('fov_angle', fov)
        capture.capture_scene()
        name = stem + '_' + label + '.png'
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), name)
        report['captures'].append(name)

def finish(error=None):
    global phase, ending_at
    if error:
        report['errors'].append(error)
    report['status'] = 'failed' if report['errors'] else 'fresh_rifle_actor_requires_contact_review'
    levels.editor_request_end_play()
    phase, ending_at = 'ending', time.monotonic()
    write()

def tick(delta):
    global in_tick, phase, phase_start, pawn, mesh, gun, world, camera, capture, target
    if in_tick:
        return
    in_tick = True
    try:
        if phase == 'ending':
            if not levels.is_in_play_in_editor() and time.monotonic()-ending_at > 3:
                report['protected_37_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in records)
                write()
                unreal.unregister_slate_post_tick_callback(callback)
                unreal.SystemLibrary.quit_editor()
            return
        if time.monotonic()-started > 180:
            finish('Bounded live timeout')
            return
        world = editor.get_game_world()
        if not world:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if phase == 'waiting':
            pawn = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character) if a.get_actor_label() == 'RifleActionPlayer')
            mesh = pawn.get_component_by_class(unreal.SkeletalMeshComponent)
            gun = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor) if a.get_actor_label() == 'RifleActionGun')
            controller = unreal.GameplayStatics.get_player_controller(world, 0)
            controller.possess(pawn)
            assert gun.get_editor_property('GripMesh') == mesh
            assert gun.get_editor_property('Combatant') == pawn
            assert 'ABP_PC_Allied_Stride_v1_C' in mesh.get_anim_instance().get_class().get_path_name()
            spawn = unreal.get_default_object(unreal.GameplayStatics.static_class())
            camera = spawn.call_method('BeginDeferredActorSpawnFromClass', args=(world, unreal.SceneCapture2D.static_class(), unreal.Transform(),
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, pawn, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            camera = spawn.call_method('FinishSpawningActor', args=(camera, unreal.Transform(), unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
            capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('capture_every_frame', False)
            capture.set_editor_property('override_custom_near_clipping_plane', True)
            capture.set_editor_property('custom_near_clipping_plane', 1)
            target = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0, 0, 0, 1), False)
            capture.set_editor_property('texture_target', target)
            phase, phase_start = 'idle', now
            return
        right, left = center('r'), center('l')
        anchor = unreal.MathLibrary.transform_location(gun.get_actor_transform(), unreal.Vector(-.5, -8, 0))
        error = (anchor-right).length()
        action = str(pawn.get_editor_property('ActionState'))
        record = {'phase': phase, 'time': now, 'action': action, 'rear_anchor_error_cm': error,
                  'velocity': xyz(pawn.get_velocity()), 'grasp_span_cm': (left-right).length()}
        report['frames'].append(record)
        # Post-Slate observers may precede one mesh refresh; bound rather than hide it.
        if phase == 'walk':
            pawn.add_movement_input(unreal.Vector(1, 0, 0), 1, True)
            for index, threshold in enumerate((.7, 1.4, 2.1)):
                tag = 'walk_' + str(index)
                if now-phase_start >= threshold and tag not in report['samples']:
                    assert pawn.get_velocity().length() > 100
                    views(tag)
                    report['samples'].append(tag)
            if now-phase_start > 2.5:
                pawn.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
                phase, phase_start = 'settle', now
        elif phase == 'idle' and now-phase_start > 1.5:
            assert error < .1, 'Runtime gun fitting not active'
            views('idle')
            phase, phase_start = 'walk', now
        elif phase == 'settle' and now-phase_start > .5:
            report['before_reload'] = {n: str(pawn.get_editor_property(n)) for n in ('LoadedAmmo', 'ReserveAmmo', 'ActionState')}
            pawn.call_method('PC_RequestReload')
            phase, phase_start = 'reload', now
        elif phase == 'reload':
            if moving_reload:
                pawn.add_movement_input(unreal.Vector(1, 0, 0), 1, True)
            for index, threshold in enumerate((.55, 1.1, 1.8)):
                tag = 'reload_' + str(index)
                if now-phase_start >= threshold and tag not in report['samples']:
                    views(tag)
                    report['samples'].append(tag)
            if now-phase_start > 3.5:
                report['after_reload'] = {n: str(pawn.get_editor_property(n)) for n in ('LoadedAmmo', 'ReserveAmmo', 'ActionState')}
                assert action == 'Ready'
                assert int(pawn.get_editor_property('LoadedAmmo')) + int(pawn.get_editor_property('ReserveAmmo')) == 18
                if moving_reload:
                    report['moving_reload_frames'] = sum(f['phase'] == 'reload' and f['action'] == 'Reloading' and unreal.Vector(*f['velocity']).length() > 100 for f in report['frames'])
                    assert report['moving_reload_frames'] > 10
                pawn.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
                pawn.call_method('PC_ResetLifecycle')
                phase, phase_start = 'reset', now
        elif phase == 'reset' and now-phase_start > .7:
            report['after_reset_class'] = mesh.get_anim_instance().get_class().get_path_name()
            assert 'ABP_PC_Allied_Stride_v1_C' in report['after_reset_class']
            report['max_anchor_error_cm'] = max(f['rear_anchor_error_cm'] for f in report['frames'])
            report['max_walk_speed_cm_s'] = max(unreal.Vector(*f['velocity']).length() for f in report['frames'])
            assert report['max_anchor_error_cm'] < 2, 'Reject stale/lagged fit'
            views('reset')
            finish()
        write()
    except Exception:
        finish(traceback.format_exc())
    finally:
        in_tick = False

try:
    assert levels.load_level('/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001')
    for a in actors.get_all_level_actors():
        if isinstance(a, unreal.Character):
            actors.destroy_actor(a)
    pawn = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'), unreal.Vector(0, 0, 100))
    pawn.set_actor_label('RifleActionPlayer')
    mesh = pawn.get_component_by_class(unreal.SkeletalMeshComponent)
    gun = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(author['package']), unreal.Vector())
    gun.set_actor_label('RifleActionGun')
    gun.set_editor_property('GripMesh', mesh)
    gun.set_editor_property('Combatant', pawn)
    gun.set_owner(pawn)
    pawn.set_editor_property('WeaponAppearance', gun)
    assert gun.attach_to_component(mesh, 'hand_r', unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
    r = inventory['rifle_attachment']['rotation']
    gun.static_mesh_component.set_editor_property('relative_location', unreal.Vector(*inventory['rifle_attachment']['location']))
    gun.static_mesh_component.set_editor_property('relative_rotation', unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
    light = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(80, -80, 220))
    component = light.get_component_by_class(unreal.PointLightComponent)
    component.set_editor_property('intensity', 20)
    component.set_editor_property('attenuation_radius', 700)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
    write()
    levels.editor_request_begin_play()
except Exception:
    report['status'] = 'failed_startup'
    report['errors'].append(traceback.format_exc())
    report['protected_37_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in records)
    write()
    unreal.SystemLibrary.quit_editor()
