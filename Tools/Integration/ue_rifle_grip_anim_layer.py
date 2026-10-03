"""One new terminal finger-layer AnimBP trial; never selects it in the city."""
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ['CS549_GRIP_LAYER_IDENTITY']
assert IDENTITY.replace('_', '').isalnum(), 'Safe evidence identity required'
OUT = STORE / 'Evidence/CityGameplay20261002/WeaponGrip' / IDENTITY
assert not OUT.exists()
OUT.mkdir(parents=True)
DEST = '/Game/ParisCombat/Animation/WeaponPresentationV1/ABP_PC_AlliedGripV1'
SOURCE = '/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_Allied_Stride_v1'
guarded = {}
for name in ('CITY_NAVIGATION_DRAFT_INVENTORY_20261002', 'RELOAD_DRAFT_SNAPSHOT_20261002'):
    for e in json.loads((ROOT / ('Assets/Integration/' + name + '.json')).read_text(encoding='utf-8-sig'))['files']:
        guarded[ROOT / e['path']] = e['sha256']
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(digest(p) == h for p, h in guarded.items())
report = {'scope': 'Unselected existing-AnimBP finger-layer trial; no city/default/source-clip changes',
          'errors': [], 'captures': [], 'joints': [], 'nodes': [], 'status': 'initializing'}
def checkpoint():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2))
lib, pins = unreal.BlueprintEditorLibrary, unreal.BlueprintGraphPinLibrary
callback = None
ending = False
phase = 0
phase_start = 0
in_tick = False
started = time.monotonic()
ending_at = 0
def xyz(v):
    return [v.x, v.y, v.z]
def finish(error=None):
    global ending, ending_at
    if ending:
        return
    ending = True
    ending_at = time.monotonic()
    if error:
        report['errors'].append(error)
    report['status'] = 'failed' if report['errors'] else 'runtime_trial_pending_contact_review'
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    checkpoint()
def tick(delta):
    global phase, phase_start, in_tick, runtime_player, runtime_mesh
    if in_tick:
        return
    in_tick = True
    try:
        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        if time.monotonic() - started > 180 and not ending:
            finish('Runtime watchdog exceeded 180 seconds')
        if ending:
            if not levels.is_in_play_in_editor() and time.monotonic() - ending_at > 3:
                report['protected_35_unchanged'] = all(digest(p) == h for p, h in guarded.items())
                checkpoint()
                unreal.unregister_slate_post_tick_callback(callback)
                unreal.SystemLibrary.quit_editor()
            return
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if not world:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if phase == 0:
            report['runtime_actors'] = [a.get_actor_label() for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)]
            runtime_player = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character) if a.get_actor_label() == 'GripLayer_Player')
            runtime_mesh = runtime_player.get_component_by_class(unreal.SkeletalMeshComponent)
            report['runtime_mesh'] = runtime_mesh.get_skeletal_mesh_asset().get_path_name()
            globals()['runtime_player'] = runtime_player
            globals()['runtime_mesh'] = runtime_mesh
            controller = unreal.GameplayStatics.get_player_controller(world, 0)
            assert controller, 'Ordinary player controller required for walking trial'
            controller.possess(runtime_player)
            report['player_controller'] = controller.get_name()
            globals()['runtime_weapon'] = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor) if a.get_actor_label() == 'GripLayer_Rifle')
            spawn = unreal.get_default_object(unreal.GameplayStatics.static_class())
            camera = spawn.call_method('BeginDeferredActorSpawnFromClass', args=(world,
                unreal.SceneCapture2D.static_class(), unreal.Transform(),
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, runtime_player,
                unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            globals()['runtime_camera'] = spawn.call_method('FinishSpawningActor', args=(
                camera, unreal.Transform(), unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            globals()['capture'] = runtime_camera.get_component_by_class(unreal.SceneCaptureComponent2D)
            capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('capture_every_frame', True)
            capture.set_editor_property('override_custom_near_clipping_plane', True)
            capture.set_editor_property('custom_near_clipping_plane', 1)
            globals()['target'] = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720,
                unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0, 0, 0, 1), False)
            capture.set_editor_property('texture_target', target)
            runtime_mesh.set_anim_instance_class(source_class)
            phase, phase_start = 1, now
            return
        if now - phase_start < 1:
            return
        name = ('original_contact', 'corrected_contact', 'corrected_fp', 'corrected_walk_fp',
                'corrected_walk_contact', 'source_walk_fp')[phase - 1]
        if phase >= 4:
            runtime_player.add_movement_input(unreal.Vector(1, 0, 0), 1, True)
        if phase <= 2 or phase == 5:
            if phase == 5 and not report.get('walk_contact_attached_to_capsule'):
                assert runtime_camera.attach_to_component(runtime_player.capsule_component, 'None',
                    unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET,
                    unreal.AttachmentRule.KEEP_WORLD, False)
                report['walk_contact_attached_to_capsule'] = True
            middle = (runtime_mesh.get_socket_location('hand_l') + runtime_mesh.get_socket_location('hand_r')) / 2
            location = middle + unreal.Vector(90, -70, 35)
            rotation = unreal.MathLibrary.find_look_at_rotation(location, middle)
            fov = 40
        else:
            eye = runtime_player.get_component_by_class(unreal.CameraComponent)
            if (phase == 3 and not report.get('capture_attached_to_player_camera')) or (phase == 6 and not report.get('source_walk_camera_attached')):
                assert runtime_camera.attach_to_component(eye, 'None',
                    unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET,
                    unreal.AttachmentRule.KEEP_WORLD, False)
                report['capture_attached_to_player_camera'] = True
                if phase == 6:
                    report['source_walk_camera_attached'] = True
            location, rotation, fov = eye.get_world_location(), eye.get_world_rotation(), 90
        if now - phase_start < 1.7:
            runtime_camera.set_actor_location(location, False, False)
            runtime_camera.set_actor_rotation(rotation, False)
            capture.set_editor_property('fov_angle', fov)
            return
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), name + '.png')
        joints = {n: xyz(runtime_mesh.get_socket_location(n)) for n in ('hand_l', 'index_01_l', 'index_02_l', 'index_03_l', 'middle_02_l', 'middle_03_l')}
        report['captures'].append(name + '.png')
        report['joints'].append({'name': name, 'bones': joints, 'velocity': xyz(runtime_player.get_velocity())})
        if phase == 1:
            runtime_mesh.set_anim_instance_class(dest_class)
            r = selected['experimental_relative_rotation']
            root = runtime_weapon.static_mesh_component
            root.set_editor_property('relative_location', unreal.Vector(*selected['experimental_relative_location']))
            root.set_editor_property('relative_rotation', unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
        if phase == 5:
            runtime_mesh.set_anim_instance_class(source_class)
        if phase == 6:
            finish()
            return
        phase += 1
        phase_start = now
        checkpoint()
    except Exception:
        finish(traceback.format_exc())
    finally:
        in_tick = False

try:
    file = STORE / ('Content/' + DEST.removeprefix('/Game/') + '.uasset')
    if os.environ.get('CS549_GRIP_LAYER_FRESH') == '1':
        prior = json.loads((OUT.parent / 'layer_v3/result.json').read_text())['saved_trial']
        assert file.stat().st_size == prior['size_bytes'] and digest(file) == prior['sha256']
        report['fresh_trial_verified'] = prior
        bp = unreal.load_asset(DEST)
        assert bp
    else:
        assert not unreal.EditorAssetLibrary.does_asset_exist(DEST), 'Preserve occupied trial package'
        bp = unreal.EditorAssetLibrary.duplicate_asset(SOURCE, DEST)
        assert bp
        graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'AnimGraph')
        assert graph
        report['author_helper'] = json.loads(unreal.ParisBlueprintAuthoring.add_allied_grip_layer(bp))
        checkpoint()
        assert report['author_helper']['success'], 'Narrow editor-only graph authoring failed'
        report['graph_errors'] = [str(n) for n in graph.list_nodes_with_errors()]
        assert not report['graph_errors']
        assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report['saved_trial'] = {'path': file.relative_to(ROOT).as_posix(), 'sha256': digest(file), 'size_bytes': file.stat().st_size}
    report['protected_35_unchanged'] = all(digest(p) == h for p, h in guarded.items())
    assert report['protected_35_unchanged']
    source_class = unreal.EditorAssetLibrary.load_blueprint_class(SOURCE)
    dest_class = unreal.EditorAssetLibrary.load_blueprint_class(DEST)
    assert source_class and dest_class
    # Keep the fore-end under the support hand; the curl_v1 rear anchor misplaced the stock.
    selected = json.loads((OUT.parent / 'probe_v2/result.json').read_text())
    report['attachment_trial_source'] = 'probe_v2; unselected until contact review'
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level('/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in actors.get_all_level_actors():
        if isinstance(a, unreal.Character):
            actors.destroy_actor(a)
    player = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'), unreal.Vector(0, 0, 100))
    player.set_actor_label('GripLayer_Player')
    weapon = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector())
    weapon.set_actor_label('GripLayer_Rifle')
    weapon.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    weapon.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'))
    weapon.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    weapon.set_owner(player)
    assert weapon.attach_to_component(player.get_component_by_class(unreal.SkeletalMeshComponent), 'hand_r', unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
    original = json.loads((OUT.parent / 'probe_v2/result.json').read_text())
    r = original['relative_rotation']
    weapon.static_mesh_component.set_editor_property('relative_location', unreal.Vector(*original['relative_location']))
    weapon.static_mesh_component.set_editor_property('relative_rotation', unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
    light = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(80, -80, 220))
    component = light.get_component_by_class(unreal.PointLightComponent)
    component.set_editor_property('intensity', 20)
    component.set_editor_property('attenuation_radius', 700)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
    checkpoint()
    levels.editor_request_begin_play()
except Exception:
    report['status'] = 'failed_author_or_startup'
    report['errors'].append(traceback.format_exc())
    report['protected_35_unchanged'] = all(digest(p) == h for p, h in guarded.items())
    checkpoint()
    unreal.SystemLibrary.quit_editor()
