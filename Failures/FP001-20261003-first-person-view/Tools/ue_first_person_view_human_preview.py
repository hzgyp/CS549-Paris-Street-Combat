"""Human review of the validated, unselected same-model owner-view candidate."""
import json,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from ue_first_person_view_runtime import EVIDENCE,trial_records,stage
inventory=json.loads((ROOT/'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json').read_text())
validation=inventory['validation']
combat=json.loads((ROOT/validation['combat_report']).read_text())
assert combat['all_assertions_passed'] and combat['native_bytes_unchanged'] and not combat['errors']
trial_records()
identity=os.environ['CS549_FP_HUMAN_IDENTITY'];assert identity.replace('_','').isalnum()
OUT=EVIDENCE/(identity+'.json');assert not OUT.exists()
r={'status':'launching','errors':[],'map_saved':False,'human_visual_acceptance':False}
started=time.monotonic();callback=None
def write():OUT.write_text(json.dumps(r,indent=2))
def tick(dt):
    try:
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:
            assert time.monotonic()-started<180,'Human preview startup timeout';return
        if not r.get('variant'):
            r['variant']=stage(world,player);write();return
        view=player.get_editor_property('WeaponAppearance').get_editor_property('GripMesh').get_owner()
        if not view.get_editor_property('ViewInitialized'):return
        r['status']='ready_runtime_only_human_review';write()
        unreal.unregister_slate_post_tick_callback(callback)
        unreal.log('First-person repair preview ready. WASD, mouse, left click, R; Esc ends PIE. Saved city remains V3.')
    except Exception:
        r['status']='failed';r['errors'].append(traceback.format_exc());write()
        unreal.unregister_slate_post_tick_callback(callback)
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();unreal.SystemLibrary.quit_editor()
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback=unreal.register_slate_post_tick_callback(tick);write()
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
