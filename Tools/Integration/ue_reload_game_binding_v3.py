"""Disposable city binding observations. No authoring, skin read, save or pose updater."""
import hashlib
import json
import os
import sys
import time
import traceback
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
SCOPE = os.environ['CS549_BINDING_SCOPE']
assert SCOPE in ('saved', 'actions')
OUT = STORE / 'Evidence/ReloadContactBindingV3' / os.environ['CS549_BINDING_IDENTITY']
assert not OUT.exists(), 'Preserve occupied evidence'
OUT.mkdir(parents=True)
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
records = json.loads((ROOT / 'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
records += json.loads((ROOT / 'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']


def guard():
    differences = []
    for item in records:
        path = ROOT / item['path']
        if not path.is_file() or path.stat().st_size != item['size_bytes']:
            differences.append(item['path'])
        elif hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            differences.append(item['path'])
    return {'checked': len(records), 'different': differences}


def path_of(obj):
    return obj.get_path_name() if obj else None


def vec(v):
    return [v.x, v.y, v.z]


def transform(t):
    q = t.rotation
    return {'t': vec(t.translation), 'q': [q.x, q.y, q.z, q.w], 's': vec(t.scale3d)}


BONES = ('spine_03', 'upperarm_l', 'lowerarm_l', 'hand_l',
         'upperarm_r', 'lowerarm_r', 'hand_r', 'thumb_02_r', 'thumb_03_r',
         'middle_02_r', 'middle_03_r', 'ring_02_r', 'ring_03_r', 'pinky_02_r', 'pinky_03_r')


def mesh_info(mesh):
    if not mesh:
        return None
    asset = mesh.get_skeletal_mesh_asset()
    single = mesh.get_anim_instance()
    return {
        'component': path_of(mesh), 'asset': path_of(asset),
        'skeleton': path_of(asset.get_editor_property('skeleton')) if asset else None,
        'leader': path_of(mesh.get_editor_property('leader_pose_component')),
        'num_bones': mesh.get_num_bones(), 'predicted_lod': mesh.get_predicted_lod_level(),
        'forced_lod_api_value': mesh.get_forced_lod(),
        'visibility_tick': str(mesh.get_editor_property('visibility_based_anim_tick_option')),
        'animation_mode': str(mesh.get_editor_property('animation_mode')),
        'anim_instance': path_of(single),
        'single_asset': path_of(single.get_animation_asset()) if isinstance(single, unreal.AnimSingleNodeInstance) else None,
        'single_position': mesh.get_position() if isinstance(single, unreal.AnimSingleNodeInstance) else None,
        'world_t': transform(mesh.get_socket_transform('None', unreal.RelativeTransformSpace.RTS_WORLD)),
        'bones_component': {name: transform(mesh.get_socket_transform(name, unreal.RelativeTransformSpace.RTS_COMPONENT))
                            for name in BONES if mesh.does_socket_exist(name)},
    }


def grip_point(mesh):
    names = [digit + '_' + segment + '_r' for digit in ('middle', 'ring', 'pinky', 'thumb') for segment in ('02', '03')]
    return sum((mesh.get_socket_location(n) for n in names), unreal.Vector()) / len(names)


def gun_info(gun, mesh):
    if not gun:
        return None
    t = gun.get_actor_transform()
    anchor = unreal.MathLibrary.transform_location(t, unreal.Vector(-.5, -8, 0))
    return {'actor': path_of(gun), 'class': path_of(gun.get_class()), 'world_t': transform(t),
            'anchor_cm': vec(anchor), 'right_grip_proxy_cm': vec(grip_point(mesh)),
            'right_grip_proxy_error_cm': (anchor - grip_point(mesh)).length(),
            'note': 'Existing proxy anchor, not fingertip/trigger or sleeve geometry acceptance'}


r = {'status': 'starting', 'scope': SCOPE, 'errors': [], 'samples': [], 'commands': [],
     'native_assets_saved': False, 'map_saved': False, 'runtime_animation_and_attachment': 'existing UE Blueprints only',
     'failed_D059_clip_applied': False, 'bulk_skin_or_geometry_script_read': False}
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
callback = None
start = time.monotonic()
ready = None
ending = None
phase = 'warmup'
phase_start = None
last_sample = -1
busy = False


def write():
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n')


def snapshot():
    display = owner.get_component_by_class(unreal.SkeletalMeshComponent)
    pose = owner.get_editor_property('PoseMesh') if SCOPE == 'actions' else None
    source = owner.get_editor_property('SourceMesh')
    world_gun = owner.get_editor_property('WorldGun')
    display_gun = owner.get_editor_property('DisplayGun')
    camera = player.get_editor_property('ParisPlayerCamera')
    return {
        'phase': phase, 'world_seconds': unreal.GameplayStatics.get_time_seconds(world),
        'action': str(player.get_editor_property('ActionState')),
        'ammo': [int(player.get_editor_property('LoadedAmmo')), int(player.get_editor_property('ReserveAmmo'))],
        'commits': int(player.get_editor_property('ReloadCommitCount')),
        'pose_mode': str(owner.get_editor_property('PoseMode')) if pose else None,
        'body': mesh_info(player.mesh), 'pose': mesh_info(pose), 'display': mesh_info(display),
        'source_reference': path_of(source), 'world_gun': gun_info(world_gun, source),
        'display_gun': gun_info(display_gun, display),
        'player_appearance': path_of(player.get_editor_property('WeaponAppearance')),
        'camera_relative': vec(camera.get_editor_property('relative_location')),
        'camera_relative_rotation': str(camera.get_editor_property('relative_rotation')),
        'camera_fov': camera.get_editor_property('field_of_view'),
    }


def finish(error=None):
    global ending
    if ending is not None:
        return
    if error:
        r['errors'].append(error)
    r['guard_after'] = guard()
    r['status'] = 'observations_complete_no_game_change' if not r['errors'] else 'diagnostic_failed_preserve_evidence'
    write()
    levels.editor_request_end_play()
    ending = time.monotonic()


def enter(name):
    global phase, phase_start, last_sample
    phase = name
    phase_start = unreal.GameplayStatics.get_time_seconds(world)
    last_sample = -1
    if name == 'reload':
        command = 'PC_ActionReload' if SCOPE == 'actions' else 'PC_RequestReload'
        before = str(player.get_editor_property('ActionState'))
        player.call_method(command)
        r['commands'].append({'command': command, 'before': before, 'after': str(player.get_editor_property('ActionState'))})
        assert str(player.get_editor_property('ActionState')) == 'Reloading', 'Native request was not admitted'
    elif name == 'reset':
        player.call_method('PC_ResetLifecycle')
        r['commands'].append({'command': 'PC_ResetLifecycle'})


def tick(delta):
    global busy, world, player, owner, ready, last_sample
    if busy:
        return
    busy = True
    try:
        if ending is not None:
            if time.monotonic() - ending > 2:
                unreal.unregister_slate_post_tick_callback(callback)
                unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic() - start < 180, 'Bounded diagnostic deadline'
        world = editor.get_game_world()
        player = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
        if not player:
            return
        owner_label = 'PC_ActionOwnerViewTrial' if SCOPE == 'actions' else 'PC_Player_ContinuousArmsNativeV1'
        owner = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SkeletalMeshActor)
                      if a.get_actor_label() == owner_label), None)
        if not owner or not owner.get_editor_property('Initialized'):
            return
        if ready is None:
            ready = time.monotonic()
            r['runtime_world'] = path_of(world)
            r['player_class'] = path_of(player.get_class())
            r['owner_class'] = path_of(owner.get_class())
            return
        if time.monotonic() - ready < 20:
            return
        if phase == 'warmup':
            enter('before_reload')
        now = unreal.GameplayStatics.get_time_seconds(world)
        if now - last_sample > .2:
            r['samples'].append(snapshot())
            last_sample = now
            write()
        elapsed = now - phase_start
        if phase == 'before_reload' and elapsed > .8:
            enter('reload')
        elif phase == 'reload':
            assert elapsed < 12, 'Native reload did not return to Ready'
            if str(player.get_editor_property('ActionState')) == 'Ready':
                enter('after_reload')
        elif phase == 'after_reload' and elapsed > 1.0:
            enter('reset')
        elif phase == 'reset' and elapsed > 1.0:
            finish()
    except Exception:
        finish(traceback.format_exc())
    finally:
        busy = False


try:
    assert not hasattr(unreal, 'ParisBlueprintAuthoring'), 'Bridge must remain disabled'
    r['guard_before'] = guard()
    assert not r['guard_before']['different']
    saved_player = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == 'PC_City_Player')
    saved_owner = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == 'PC_Player_ContinuousArmsNativeV1')
    r['saved_map_bindings'] = {'player_class': path_of(saved_player.get_class()),
        'owner_class': path_of(saved_owner.get_class()), 'player_mesh': path_of(saved_player.mesh.get_skeletal_mesh_asset()),
        'gun_class': path_of(saved_player.get_editor_property('WeaponAppearance').get_class()),
        'owner_combatant': path_of(saved_owner.get_editor_property('Combatant'))}
    if SCOPE == 'actions':
        sys.path.insert(0, str(Path(__file__).parent))
        # Accepted existing unsaved action staging, NOT the stopped AN001 stage/author.
        from ue_player_actions_stage import stage_actions_actor
        r['unsaved_staging'], _, _ = stage_actions_actor()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
    write()
    levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status'] = 'startup_failed_preserve_evidence'
    r['guard_after'] = guard()
    write()
    unreal.SystemLibrary.quit_editor()
