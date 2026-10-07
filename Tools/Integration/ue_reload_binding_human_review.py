"""User-requested AN003 viewing only. One-time unsaved staging, no repair/save."""
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
OUT = STORE / 'Evidence/ReloadContactBindingV3' / os.environ['CS549_RELOAD_REVIEW_IDENTITY']
assert not OUT.exists(), 'Preserve existing review identity'
OUT.mkdir(parents=True)
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
sys.path.insert(0, str(Path(__file__).parent))
from ue_player_actions_stage import stage_actions_actor

inventory = json.loads((ROOT / 'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())
records = json.loads((ROOT / 'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
records += json.loads((ROOT / 'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
records += inventory['files']
assert len(records) == 514

def guard():
    return all((ROOT / f['path']).stat().st_size == f['size_bytes'] and
               hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256']
               for f in records)

report = {'status': 'starting', 'errors': [], 'user_owned': True, 'map_saved': False,
          'scope': 'Explicit human viewing only; AN003 author/visual jobs remain stopped',
          'runtime': 'Existing native Blueprint; preparation callback unregisters at ready',
          'functional_acceptance': False, 'visual_acceptance': False}

def write():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2) + '\n')

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
started = time.monotonic()
callback = None
settling = None
done = False

def tick(delta):
    global settling, done
    if done:
        return
    try:
        assert time.monotonic() - started < 240, 'Human review initialization deadline'
        world = editor.get_game_world()
        player = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
        if not player:
            return
        views = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SkeletalMeshActor)
                 if a.get_actor_label() == 'PC_ReloadBindingHumanReviewV4']
        if len(views) != 1 or not views[0].get_editor_property('Initialized'):
            return
        if settling is None:
            settling = time.monotonic()
            return
        if time.monotonic() - settling < 3:
            return
        view = views[0]
        pose = view.get_editor_property('PoseMesh')
        display = view.skeletal_mesh_component
        assert display.get_editor_property('leader_pose_component') == pose
        assert pose.get_editor_property('leader_pose_component') is None
        camera = player.get_editor_property('ParisPlayerCamera')
        p = camera.get_editor_property('relative_location')
        assert max(abs(a-b) for a,b in zip((p.x,p.y,p.z),(25.,0.,60.))) < 1e-6
        assert abs(camera.get_editor_property('field_of_view') - 90.) < 1e-6
        assert guard(), 'Native bytes changed'
        report.update(status='ready_for_human_review_native_tick_only', protected_514_unchanged=True,
                      player_class=player.get_class().get_path_name(), owner_class=view.get_class().get_path_name(),
                      pose_asset=pose.get_anim_instance().get_animation_asset().get_path_name(),
                      display_leader=pose.get_path_name(), pose_leader=None,
                      camera_relative_cm=[p.x,p.y,p.z], fov=camera.get_editor_property('field_of_view'),
                      loaded_ammo=int(player.get_editor_property('LoadedAmmo')),
                      reserve_ammo=int(player.get_editor_property('ReserveAmmo')))
        write()
        done = True
        unreal.unregister_slate_post_tick_callback(callback)
        unreal.EditorPythonScripting.set_keep_python_script_alive(False)
        unreal.log('HUMAN_RELOAD_BINDING_READY: click viewport, fire once then R; do not save staged map')
    except Exception:
        done = True
        report['status'] = 'failed_initialization'
        report['errors'].append(traceback.format_exc())
        write()
        unreal.unregister_slate_post_tick_callback(callback)
        unreal.EditorPythonScripting.set_keep_python_script_alive(False)
        levels.editor_request_end_play()

try:
    assert not hasattr(unreal, 'ParisBlueprintAuthoring')
    assert guard()
    cdo = unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(
        '/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6'))
    report['original_timing'] = {'duration': cdo.get_editor_property('ReloadDuration'),
                                 'commit': cdo.get_editor_property('ReloadCommitTime')}
    cdo.set_editor_property('ReloadDuration', 4.133333)
    cdo.set_editor_property('ReloadCommitTime', 3.95)
    report['timing_note'] = 'Unsaved process-local diagnostic defaults, not transaction acceptance'
    report['staging'], staged, old = stage_actions_actor()
    replacement = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(
        inventory['files'][1]['package']), staged.get_actor_location(), unreal.Rotator())
    assert replacement
    replacement.set_actor_label('PC_ReloadBindingHumanReviewV4')
    replacement.set_editor_property('Combatant', staged)
    actors.destroy_actor(old)
    write()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
    levels.editor_request_begin_play()
except Exception:
    report['status'] = 'failed_startup'
    report['errors'].append(traceback.format_exc())
    write()
