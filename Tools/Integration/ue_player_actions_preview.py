"""One-time unsaved editor staging; native Blueprints own all gameplay after startup."""
import hashlib,json,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from ue_player_actions_stage import stage_actions_actor
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/PlayerActionsV1'/os.environ['CS549_ACTION_IDENTITY']
assert not OUT.exists();OUT.mkdir(parents=True)
records=json.loads((ROOT/'Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json').read_text())['files']
def guard():return all(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in records)
assert guard()
r={'status':'staging','errors':[],'native_saved':False,'user_owned':True}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
start=time.monotonic();callback=None
def tick(delta):
    global callback
    try:
        world=editor.get_game_world()
        player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if player and player.get_editor_property('WeaponAppearance'):
            views=[a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor)
                   if a.get_actor_label()=='PC_ActionOwnerViewTrial']
            if views and views[0].get_editor_property('Initialized'):
                assert guard();r['status']='ready_for_human_review_native_tick_only'
                r['protected_43_unchanged']=True
                camera=player.get_component_by_class(unreal.CameraComponent)
                p=camera.get_editor_property('relative_location')
                r['camera_relative_cm']=[p.x,p.y,p.z];r['fov']=camera.get_editor_property('field_of_view')
                write();unreal.unregister_slate_post_tick_callback(callback)
                unreal.EditorPythonScripting.set_keep_python_script_alive(False)
                return
        assert time.monotonic()-start<240,'Preview initialization deadline'
    except Exception:
        r['status']='failed';r['errors'].append(traceback.format_exc());write()
        unreal.unregister_slate_post_tick_callback(callback)
        unreal.EditorPythonScripting.set_keep_python_script_alive(False)
        levels.editor_request_end_play()
try:
    assert not hasattr(unreal,'ParisBlueprintAuthoring')
    r['staging'],_,_=stage_actions_actor();write()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick)
    levels.editor_request_begin_play()
except Exception:
    r['status']='failed_startup';r['errors'].append(traceback.format_exc());write()
