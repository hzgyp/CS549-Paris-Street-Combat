"""Human review startup only; unregister Python before ordinary native play."""
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).parent))
from german_rifle_ue_common import guard, new_output
from ue_german_rifle_stage import integration_records, stage_german_rifles
from ue_player_actions_stage import stage_actions_actor

OUT = new_output(os.environ['CS549_GERMAN_UE_IDENTITY'])
r = {'status': 'starting', 'errors': [], 'user_owned': True, 'map_saved': False,
     'human_acceptance': 'pending', 'runtime': 'UE native Blueprint; startup Python unregisters at ready'}
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
start = time.monotonic()
callback = None


def write():
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')


def tick(delta):
    global callback
    try:
        assert time.monotonic() - start < 240, 'Human review initialization deadline'
        world = editor.get_game_world()
        player = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
        if not player:
            return
        view = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SkeletalMeshActor)
                     if a.get_actor_label() == 'PC_ActionOwnerViewTrial'), None)
        if view and view.get_editor_property('Initialized') and time.monotonic() - start > 10:
            enemies = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                       if a.get_class().get_name().startswith('BP_PCParis') and a.get_editor_property('TeamId') == 1]
            assert len(enemies) == 3 and all(a.get_editor_property('WeaponAppearance') for a in enemies)
            camera = player.get_component_by_class(unreal.CameraComponent)
            p = camera.get_editor_property('relative_location')
            r['camera_relative_cm'] = [p.x, p.y, p.z]
            r['fov'] = camera.get_editor_property('field_of_view')
            r['german_locations_cm'] = {a.get_actor_label(): [a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z] for a in enemies}
            r['protected_files_unchanged'] = bool(guard())
            r['status'] = 'ready_for_human_review_native_runtime_only'
            write()
            unreal.unregister_slate_post_tick_callback(callback)
            unreal.EditorPythonScripting.set_keep_python_script_alive(False)
            r['startup_callback_unregistered'] = True
            write()
    except Exception:
        r['status'] = 'failed_startup'
        r['errors'].append(traceback.format_exc())
        write()
        unreal.unregister_slate_post_tick_callback(callback)
        unreal.EditorPythonScripting.set_keep_python_script_alive(False)
        levels.editor_request_end_play()


try:
    assert not hasattr(unreal, 'ParisBlueprintAuthoring')
    integration_records()
    r['player_staging'], _, _ = stage_actions_actor()
    r['german_staging'] = stage_german_rifles()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
    write()
    levels.editor_request_begin_play()
except Exception:
    r['status'] = 'failed_startup'
    r['errors'].append(traceback.format_exc())
    write()
