"""Human PIE review of a transient player variant; current editor map stays unchanged."""
import json,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from ue_player_aim_runtime_preview import EVIDENCE,trial_records,stage
identity=os.environ.get('CS549_PLAYER_AIM_HUMAN_IDENTITY','human_preview_v1')
assert identity.replace('_','').isalnum()
OUT=EVIDENCE/(identity+'.json');assert not OUT.exists()
combat=json.loads((EVIDENCE.parent/'Runtime/combat_aim_preview_v2/combat.json').read_text())
assert combat['all_assertions_passed'] and combat['native_bytes_unchanged'] and not combat['errors']
files=trial_records()
r={'status':'launching_transient_human_review','scope':__doc__,'files':files,'errors':[],
   'main_city_saved_or_selected':False,'human_contact_and_framing_acceptance':False}
def write():OUT.write_text(json.dumps(r,indent=2))
started=time.monotonic(); callback=None
def tick(delta):
    try:
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:
            assert time.monotonic()-started<180,'Human preview startup timed out'
            return
        r['variant']=stage(world,player)
        r['status']='open_human_runtime_only_review_not_contact_approval'
        write();unreal.unregister_slate_post_tick_callback(callback)
        unreal.log('Aim preview ready. Click PIE viewport: WASD / mouse / left click / R. Esc ends PIE. Editor city was not saved.')
    except Exception:
        r['status']='failed';r['errors'].append(traceback.format_exc());write()
        unreal.unregister_slate_post_tick_callback(callback)
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        unreal.SystemLibrary.quit_editor()
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback=unreal.register_slate_post_tick_callback(tick)
write();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
