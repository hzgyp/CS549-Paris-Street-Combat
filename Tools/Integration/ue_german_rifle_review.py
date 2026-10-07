"""Fresh real-city native gun motion measurements and separate matched-phase views."""
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).parent))
from german_rifle_ue_common import ROOT, STORE, GUARDS, guard, read, new_output
from ue_german_rifle_stage import integration_records, stage_german_rifles
from ue_player_actions_stage import stage_actions_actor

OUT = new_output(os.environ['CS549_GERMAN_UE_IDENTITY'])
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
imported, authored, native_files = integration_records()
config = read(GUARDS)
r = {'status': 'starting', 'errors': [], 'samples': [], 'captures': [], 'checks': {},
     'map_saved': False, 'runtime': 'UE native Blueprint attachment; Python observation/input only',
     'frozen_views_are_motion_acceptance': False}
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
start = time.monotonic()
ready = ending = None
phase = -1
since = 0.0
shot_issued = None
callback = None
world = player = soldier = camera = controller = None
busy = False
phases = [('idle_front', 'front', None), ('idle_contact', 'contact', None),
          ('walk_live', None, None), ('walk_side', 'side', None),
          ('reload_early', 'contact', .30), ('reload_mid', 'contact', 1.0),
          ('reload_late', 'side', 1.8), ('ready_after_reload', 'front', None)]


def xyz(v):
    return [v.x, v.y, v.z]


def write():
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')


def hollow(mesh, side):
    fingers = ('middle', 'ring', 'pinky') if side == 'r' else ('index', 'middle', 'ring', 'pinky')
    names = [f + '_0' + str(n) + '_' + side for f in fingers for n in (2, 3)] + ['thumb_02_' + side, 'thumb_03_' + side]
    total = unreal.Vector()
    for name in names:
        total += mesh.get_socket_location(name)
    return total / len(names)


def snapshot():
    rows = []
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
        if actor.get_class().get_name().startswith('BP_PCParis') and actor.get_editor_property('TeamId') == 1:
            gun = actor.get_editor_property('WeaponAppearance')
            assert gun and gun.get_class().get_name() == authored['package'].rsplit('/', 1)[1] + '_C'
            t = gun.get_actor_transform()
            right = hollow(actor.mesh, 'r')
            anchor = unreal.MathLibrary.transform_location(t, unreal.Vector(*config['grip_anchor_cm']))
            left_local = unreal.MathLibrary.inverse_transform_location(t, hollow(actor.mesh, 'l'))
            muzzle = unreal.MathLibrary.transform_location(t, unreal.Vector(0, 83.23, 0))
            forward = unreal.MathLibrary.transform_direction(t, unreal.Vector(0, 1, 0))
            rows.append({'actor': actor.get_actor_label(), 'state': str(actor.get_editor_property('ActionState')),
                'speed_cm_s': actor.get_velocity().length(), 'grip_error_cm': (anchor - right).length(),
                'left_palm_rifle_local_cm': xyz(left_local), 'muzzle_world_cm': xyz(muzzle),
                'barrel_direction': xyz(forward), 'location_cm': xyz(actor.get_actor_location()),
                'anim_class': actor.mesh.get_anim_instance().get_class().get_path_name(),
                'gun_scale': xyz(gun.get_actor_scale3d()),
                'collision': str(gun.static_mesh_component.get_collision_enabled())})
    assert len(rows) == 3
    return {'phase': phases[phase][0], 'game_seconds': unreal.GameplayStatics.get_time_seconds(world), 'germans': rows}


def freeze(value):
    unreal.GameplayStatics.set_global_time_dilation(world, .0001 if value else 1)
    soldier.mesh.set_editor_property('pause_anims', value)
    soldier.character_movement.stop_movement_immediately()


def enter(i):
    global phase, since, shot_issued
    phase = i
    name, view, reload_time = phases[i]
    shot_issued = None
    if world:
        freeze(False)
    if reload_time is not None:
        soldier.call_method('PC_ResetLifecycle')
        if soldier.get_editor_property('LoadedAmmo') == soldier.get_editor_property('Capacity'):
            before = soldier.get_editor_property('LoadedAmmo')
            soldier.call_method('PC_DoShot', args=(soldier.mesh.get_socket_location('head'), unreal.Vector(0, 0, 1)))
            assert soldier.get_editor_property('LoadedAmmo') == before - 1, 'Use an actual shot, never edit protected ammo'
        soldier.call_method('PC_RequestReload')
        assert str(soldier.get_editor_property('ActionState')) == 'Reloading'
    since = unreal.GameplayStatics.get_time_seconds(world)


def frame_camera(view):
    p = soldier.get_actor_location()
    forward = soldier.get_actor_forward_vector()
    right = soldier.get_actor_right_vector()
    if view == 'contact':
        target = (hollow(soldier.mesh, 'r') + hollow(soldier.mesh, 'l')) / 2
        eye = target + right * 100 + forward * 40 + unreal.Vector(0, 0, 20)
    else:
        target = p + unreal.Vector(0, 0, -10)
        eye = p + (forward * 230 + right * 130 if view == 'front' else right * 270) + unreal.Vector(0, 0, 20)
    camera.set_actor_location(eye, False, False)
    camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(eye, target), False)
    controller.set_view_target_with_blend(camera, 0)


def finish(error=None):
    global ending
    if ending is not None:
        return
    if error:
        r['errors'].append(error)
    if world:
        freeze(False)
    moving = [x for x in r['samples'] if x['phase'] == 'walk_live']
    r['checks'] = {'three_equipped_native_germans': bool(r['samples']),
        'grip_anchor_max_below_1cm': bool(r['samples']) and max(a['grip_error_cm'] for s in r['samples'] for a in s['germans']) < 1,
        'all_guns_unit_scale_no_collision': all(all(math.isfinite(v) and abs(v - 1) <= 1e-6 for v in a['gun_scale']) and 'NO_COLLISION' in a['collision'] for s in r['samples'] for a in s['germans']),
        'continuous_walk_observed': len(moving) > 10 and any(a['speed_cm_s'] > 100 for s in moving for a in s['germans']),
        'protected_inputs_unchanged': bool(guard())}
    r['status'] = 'failed' if r['errors'] or not all(r['checks'].values()) else 'fresh_motion_and_views_recorded_requires_actual_image_and_human_review'
    write()
    ending = time.monotonic()
    levels.editor_request_end_play()


def tick(delta):
    global world, player, soldier, camera, controller, ready, callback, busy, shot_issued
    if busy:
        return
    busy = True
    try:
        if ending is not None:
            if time.monotonic() - ending > 3:
                unreal.unregister_slate_post_tick_callback(callback)
                unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic() - start < 300, 'Review deadline'
        world = editor.get_game_world()
        player = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
        if not player:
            return
        if ready is None:
            controller = unreal.GameplayStatics.get_player_controller(world, 0)
            soldier = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character) if a.get_class().get_name().startswith('BP_PCParis') and a.get_editor_property('TeamId') == 1)
            camera = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.CameraActor) if a.get_actor_label() == 'PC_GermanIntegrationReviewCamera')
            controller.set_editor_property('should_perform_full_tick_when_paused', True)
            ready = time.monotonic()
            return
        if phase < 0:
            if time.monotonic() - ready > 20:
                enter(0)
            return
        name, view, reload_time = phases[phase]
        elapsed = unreal.GameplayStatics.get_time_seconds(world) - since
        if name == 'walk_live':
            soldier.add_movement_input(soldier.get_actor_forward_vector(), 1, False)
            r['samples'].append(snapshot())
            if elapsed > .8:
                enter(phase + 1)
            return
        if shot_issued is None:
            if elapsed < (reload_time if reload_time is not None else .8):
                return
            sample = snapshot()
            r['samples'].append(sample)
            freeze(True)
            frame_camera(view)
            shot_issued = {'time': time.monotonic(), 'requested': False}
            r['captures'].append({'file': name + '.png', 'frozen_sample': sample, 'view': view})
            write()
            return
        if not shot_issued['requested'] and time.monotonic() - shot_issued['time'] > 1.2:
            path = OUT / (name + '.png')
            unreal.SystemLibrary.execute_console_command(world, 'HighResShot 1280x720 filename="' + path.as_posix() + '"', controller)
            shot_issued['requested'] = True
            shot_issued['time'] = time.monotonic()
            return
        if shot_issued['requested'] and time.monotonic() - shot_issued['time'] > 1.5:
            assert (OUT / (name + '.png')).exists(), 'Missing actual viewport capture'
            if phase + 1 == len(phases):
                finish()
            else:
                enter(phase + 1)
    except Exception:
        finish(traceback.format_exc())
    finally:
        busy = False


try:
    assert not hasattr(unreal, 'ParisBlueprintAuthoring')
    r['fresh_import_triangles'] = unreal.load_asset(imported['mesh']).get_num_triangles(0)
    assert r['fresh_import_triangles'] == 24466
    r['player_staging'], _, _ = stage_actions_actor()
    r['german_staging'] = stage_german_rifles()
    review_camera = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(), unreal.Rotator())
    review_camera.set_actor_label('PC_GermanIntegrationReviewCamera')
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
    write()
    levels.editor_request_begin_play()
except Exception:
    r['status'] = 'failed_startup'
    r['errors'].append(traceback.format_exc())
    r['protected_files_unchanged'] = bool(guard())
    write()
    unreal.SystemLibrary.quit_editor()
