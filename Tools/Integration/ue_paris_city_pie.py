"""Read-only actual-city PIE smoke test in a full editor, never a blank fixture."""
import hashlib
import json
import os
import time
import traceback
from datetime import datetime
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
EVIDENCE = STORE / 'Evidence/CityGameplay20261002'
IDENTITY = os.environ.get('CS549_CITY_PIE_IDENTITY', 'pie_v1')
assert IDENTITY.replace('_', '').isalnum()
OUT = EVIDENCE / 'Runtime' / IDENTITY
assert not OUT.exists(), 'Preserve occupied PIE evidence'
OUT.mkdir(parents=True)
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
authored = json.loads((EVIDENCE / 'Setup/author_v4.json').read_text(encoding='utf-8'))
controls = json.loads((EVIDENCE / 'Setup/input_v1.json').read_text(encoding='utf-8'))
assert authored['status'] == 'saved_asset_backed_city_setup_not_gameplay_acceptance'
assert controls['status'] == 'saved_city_input_bindings_not_device_test'
guarded = {f['path']: f['sha256'] for f in authored['saved_files']}
guarded[controls['saved_file']['path']] = controls['saved_file']['sha256']
old = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
guarded.update({f['path']: f['sha256'] for f in old['files']})
for file in (STORE / 'Content/WW2City/Maps').glob('*.umap'):
    guarded[file.relative_to(ROOT).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in guarded.items())
report = {'started_at': datetime.now().astimezone().isoformat(),
          'engine': unreal.SystemLibrary.get_engine_version(),
          'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'scope': 'Actual-city PIE scripted Blueprint requests, not keyboard/mouse, FPS, combat or mission acceptance',
          'status': 'initializing', 'samples': [], 'captures': [], 'errors': []}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
started = time.monotonic()
phase = 'waiting'
phase_start = started
phase_game_start = 0.0
player = controller = world = capture_actor = target = None
callback = None
finishing = False
pending_capture = None
in_tick = False


def xyz(v):
    return [v.x, v.y, v.z]


def checkpoint():
    (OUT / 'pie.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


def advance(name):
    global phase, phase_start, phase_game_start
    phase = name
    phase_start = time.monotonic()
    phase_game_start = unreal.GameplayStatics.get_time_seconds(world)


def sample(label):
    location, rotation = controller.get_player_view_point()
    data = {'label': label, 'game_time_seconds': unreal.GameplayStatics.get_time_seconds(world),
            'position_cm': xyz(player.get_actor_location()),
            'velocity_cm_s': xyz(player.get_velocity()),
            'view_location_cm': xyz(location), 'view_rotation': [rotation.pitch, rotation.yaw, rotation.roll]}
    for key in ('LoadedAmmo', 'ReserveAmmo', 'Capacity', 'ReloadCommitCount', 'ActionState', 'Health'):
        data[key] = str(player.get_editor_property(key))
    report['samples'].append(data)
    checkpoint()


def queue_capture(name):
    global pending_capture
    location, rotation = controller.get_player_view_point()
    capture_actor.set_actor_location(location, False, False)
    capture_actor.set_actor_rotation(rotation, False)
    if name == 'idle_player_view':
        # Capture the active PIE viewport as well as a matched SceneCapture view.
        report['viewport_request'] = str(OUT / 'idle_game_viewport.png')
        # FunctionalTesting screenshot helper flushes editor work and pumps Slate;
        # use the ordinary viewport screenshot console command instead.
        unreal.SystemLibrary.execute_console_command(world,
            'HighResShot 1280x720 filename="' + (OUT / 'idle_game_viewport.png').as_posix() + '"', controller)
    pending_capture = (name, unreal.GameplayStatics.get_time_seconds(world))


def finish(status, error=None):
    global finishing, phase, phase_start
    if finishing:
        return
    finishing = True
    report['status'] = status
    if error:
        report['errors'].append(error)
    if capture_actor:
        capture_actor.destroy_actor()
    level_editor.editor_request_end_play()
    phase = 'ending'
    phase_start = time.monotonic()
    checkpoint()


def tick(delta):
    global world, player, controller, phase, phase_start, capture_actor, target, pending_capture, in_tick
    if in_tick:
        return
    in_tick = True
    now = time.monotonic()
    try:
        if phase == 'ending':
            if not level_editor.is_in_play_in_editor() or now - phase_start > 10:
                unreal.unregister_slate_post_tick_callback(callback)
                report['native_bytes_unchanged'] = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in guarded.items())
                if not report['native_bytes_unchanged']:
                    report['status'] = 'failed'
                    report['errors'].append('Unexpected native bytes changed')
                report['finished_at'] = datetime.now().astimezone().isoformat()
                viewport_file = OUT / 'idle_game_viewport.png'
                if viewport_file.exists():
                    report['viewport_capture'] = {'file': viewport_file.relative_to(ROOT).as_posix(),
                        'size_bytes': viewport_file.stat().st_size,
                        'sha256': hashlib.sha256(viewport_file.read_bytes()).hexdigest()}
                checkpoint()
                unreal.SystemLibrary.quit_editor()
            return
        if now - started > 240:
            finish('failed', 'Bounded PIE timeout')
            return
        game_age = unreal.GameplayStatics.get_time_seconds(world) - phase_game_start if world else 0
        if phase == 'waiting':
            world = editor.get_game_world()
            if not world:
                return
            controller = unreal.GameplayStatics.get_player_controller(world, 0)
            player = unreal.GameplayStatics.get_player_pawn(world, 0) if controller else None
            if not player:
                return
            assert player.get_class().get_name() == 'BP_PCParisPlayerV1_C', 'Wrong player possessed'
            roster = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                      if a.get_class().get_name().startswith('BP_PCParis')]
            assert len(roster) == 6, 'Wrong runtime roster'
            weapons = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor)
                       if a.get_owner() in roster]
            assert len(weapons) == 3, 'Wrong runtime weapon count'
            report['world'] = world.get_path_name()
            report['runtime_roster'] = [a.get_class().get_name() for a in roster]
            report['runtime_weapon_count'] = len(weapons)
            report['controller'] = controller.get_class().get_path_name()
            # These installed UFUNCTIONs are BlueprintInternalUseOnly and lack Python glue.
            spawn_library = unreal.get_default_object(unreal.GameplayStatics.static_class())
            capture_actor = spawn_library.call_method('BeginDeferredActorSpawnFromClass', args=(
                world, unreal.SceneCapture2D.static_class(), unreal.Transform(),
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, player,
                unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            capture_actor = spawn_library.call_method('FinishSpawningActor', args=(
                capture_actor, unreal.Transform(), unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            capture = capture_actor.get_component_by_class(unreal.SceneCaptureComponent2D)
            target = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720,
                unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0, 0, 0, 1), False)
            capture.set_editor_property('texture_target', target)
            capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('capture_every_frame', True)
            capture.set_editor_property('always_persist_rendering_state', True)
            capture.set_editor_property('fov_angle', 90)
            report['status'] = 'running'
            advance('warm')
            sample('possessed')
        elif phase == 'warm' and game_age > 4:
            sample('idle_settled')
            queue_capture('idle_player_view')
            advance('idle_capture')
        elif phase == 'idle_capture' and game_age > 2:
            sample('before_forward')
            advance('forward')
        elif phase == 'forward':
            player.call_method('PC_RequestMoveForward', args=(1.0,))
            if game_age > 1.5:
                sample('after_forward')
                advance('brake')
        elif phase == 'brake' and game_age > 1:
            sample('after_brake')
            player.call_method('PC_RequestLookYaw', args=(10.0,))
            advance('look')
        elif phase == 'look' and game_age > 1:
            sample('after_look')
            player.call_method('PC_RequestReload')
            sample('reload_requested')
            queue_capture('reload_player_view')
            advance('reload')
        elif phase == 'reload' and game_age > 8:
            sample('reload_finished')
            queue_capture('post_reload_player_view')
            advance('final_capture')
        elif phase == 'final_capture' and game_age > 2:
            camera = player.get_component_by_class(unreal.CameraComponent)
            report['unsaved_camera_variant_cm'] = [45, 0, 60]
            camera.set_relative_location(unreal.Vector(45, 0, 60), False, False)
            advance('camera_variant_settle')
        elif phase == 'camera_variant_settle' and game_age > 1:
            sample('unsaved_forward_camera_variant')
            queue_capture('unsaved_forward_camera_variant')
            advance('camera_variant_capture')
        elif phase == 'camera_variant_capture' and game_age > 2:
            finish('completed_actual_city_pie_smoke_requires_result_review')
        if pending_capture and unreal.GameplayStatics.get_time_seconds(world) - pending_capture[1] > .7:
            name = pending_capture[0]
            unreal.RenderingLibrary.export_render_target(world, target, str(OUT), name + '.png')
            file = OUT / (name + '.png')
            assert file.exists() and file.stat().st_size > 1000
            report['captures'].append({'file': file.relative_to(ROOT).as_posix(), 'size_bytes': file.stat().st_size,
                                       'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
            pending_capture = None
            checkpoint()
    except Exception:
        finish('failed', traceback.format_exc())
    finally:
        in_tick = False


try:
    # ExecutePythonScript otherwise schedules editor exit after the script returns.
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    current = editor.get_editor_world()
    if not current or current.get_path_name() != ENTRY + '.' + ENTRY.rsplit('/', 1)[1]:
        assert unreal.EditorLevelLibrary.load_level(ENTRY)
    callback = unreal.register_slate_post_tick_callback(tick)
    checkpoint()
    level_editor.editor_request_begin_play()
except Exception:
    report['status'] = 'failed_startup'
    report['errors'].append(traceback.format_exc())
    checkpoint()
    if callback:
        unreal.unregister_slate_post_tick_callback(callback)
    unreal.SystemLibrary.quit_editor()
