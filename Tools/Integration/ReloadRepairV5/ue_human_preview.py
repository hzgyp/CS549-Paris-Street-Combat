"""User-requested viewing of existing V5 trials only. One-time unsaved setup, no repair/save."""
import hashlib,json,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ['CS549_RELOAD_HUMAN_ID'];assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
sys.path.insert(0,str(Path(__file__).parent))
from common import records,check
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from ue_player_actions_stage import stage_actions_actor
rows=records(True)+json.loads((ROOT/'Docs/Development/NPCInteractionV1/NPC_INTERACTION_V1_DRAFT_INVENTORY_20261004.json').read_text())['files']
assert len(rows)==528 and len({x['path'] for x in rows})==528
PLAYER='/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6'
OWNER='/Game/ParisCombat/Blueprints/ReloadRepairV5/BP_PCReloadOwnerReframeV5'
MESH='/Game/ParisCombat/Characters/ReloadRepairV5/SK_PC_SleeveWeightsV5'
ANIM='/Game/ParisCombat/Animation/ReloadRepairV5/ABP_PCReloadOwnerBlendV5'
GUN='/Game/ParisCombat/Blueprints/ReloadRepairV5/BP_PCReloadBlendGunV5'
r={'scope':__doc__,'status':'starting','errors':[],'user_owned':True,'map_saved':False,
   'native_authored':False,'visual_acceptance':False,'functional_acceptance':False,
   'open_defects':['RLD-01','RLD-02','RLD-03'],
   'runtime':'Existing native Blueprint drivers; callback removed at ready',
   'limitations':['Combined existing unselected owner and sleeve trials for user viewing only; not full integration acceptance.']}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
started=time.monotonic();callback=None;settled=None;done=False;mesh_applied=False
def stop_callback():
    if callback is not None:unreal.unregister_slate_post_tick_callback(callback)
    unreal.EditorPythonScripting.set_keep_python_script_alive(False)
def tick(delta):
    global done,settled,mesh_applied
    if done:return
    try:
        assert time.monotonic()-started<240,'Human preview initialization deadline'
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        view=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_ReloadV5HumanView'),None)
        if not view or not view.get_editor_property('Initialized'):return
        pose=view.get_editor_property('PoseMesh');display=view.skeletal_mesh_component
        if not mesh_applied:
            display.set_skeletal_mesh_asset(unreal.load_asset(MESH));display.set_leader_pose_component(pose,True,False)
            mesh_applied=True;settled=time.monotonic();r['display_assignment']='One initialization assignment of existing new-copy mesh; native leader refresh';write();return
        if time.monotonic()-settled<3:return
        assert display.get_skeletal_mesh_asset().get_path_name()==MESH+'.'+MESH.rsplit('/',1)[-1]
        assert display.get_editor_property('leader_pose_component')==pose and pose.get_editor_property('leader_pose_component') is None
        assert pose.get_anim_instance().get_class().get_path_name()==ANIM+'.'+ANIM.rsplit('/',1)[-1]+'_C'
        gun=view.get_editor_property('PoseGun');assert gun and gun.get_class().get_path_name()==GUN+'.'+GUN.rsplit('/',1)[-1]+'_C'
        displaygun=view.get_editor_property('DisplayGun');assert displaygun and displaygun.get_class()==unreal.StaticMeshActor.static_class()
        camera=player.get_editor_property('ParisPlayerCamera');p=camera.get_editor_property('relative_location')
        assert max(abs(a-b) for a,b in zip((p.x,p.y,p.z),(25.,0.,60.)))<1e-6 and abs(camera.get_editor_property('field_of_view')-90)<1e-6
        assert check(rows),'Native guard changed'
        r.update(status='ready_for_human_review_native_tick_only',protected_count=len(rows),protected_records_unchanged=True,
          player_class=player.get_class().get_path_name(),owner_class=view.get_class().get_path_name(),
          display_mesh=display.get_skeletal_mesh_asset().get_path_name(),display_leader=pose.get_path_name(),
          pose_leader=None,anim_class=pose.get_anim_instance().get_class().get_path_name(),
          gun_class=gun.get_class().get_path_name(),display_gun_class=displaygun.get_class().get_path_name(),camera_relative_cm=[p.x,p.y,p.z],fov=camera.get_editor_property('field_of_view'),
          ammo=[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
          preparation_callback_removed=True)
        write();done=True;stop_callback();unreal.log('CS549_RELOAD_V5_HUMAN_READY: click viewport, R reload; do not save staged map/defaults')
    except Exception:
        r['status']='failed_initialization';r['errors'].append(traceback.format_exc());r['protected_count']=len(rows);r['protected_records_unchanged']=check(rows)
        write();done=True;stop_callback();levels.editor_request_end_play()
try:
    assert check(rows) and not hasattr(unreal,'ParisBlueprintAuthoring')
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(PLAYER))
    if os.environ.get('CS549_RELOAD_HUMAN_RESUME')=='1':
        assert editor.get_game_world() is None,'Resume expects PIE ended'
        stagedrows=[a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_City_Player_ActionTrial']
        viewrows=[a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_ReloadV5HumanView']
        assert len(stagedrows)==len(viewrows)==1
        staged=stagedrows[0];newview=viewrows[0]
        assert staged.get_class().get_path_name()==PLAYER+'.'+PLAYER.rsplit('/',1)[-1]+'_C'
        assert newview.get_class().get_path_name()==OWNER+'.'+OWNER.rsplit('/',1)[-1]+'_C'
        assert newview.get_editor_property('Combatant')==staged
        previous=json.loads((STORE/'Evidence/ReloadRepairV5/human_v5_20261004_211334_842/result.json').read_text())
        assert previous['status']=='failed_initialization' and previous['protected_records_unchanged']
        r['original_timing']=previous['original_timing']
        assert abs(cdo.get_editor_property('ReloadDuration')-r['original_timing']['duration'])<1e-6
        assert abs(cdo.get_editor_property('ReloadCommitTime')-r['original_timing']['commit'])<1e-6
        assert abs(cdo.get_editor_property('ReloadPlayRate')-previous['temporary_rate'])<1e-6
        r['staging']={'reused_same_editor_staging':True,'previous_failed_identity':'human_v5_20261004_211334_842','map_saved':False}
    else:
        r['original_timing']={k:cdo.get_editor_property(v) for k,v in [('duration','ReloadDuration'),('commit','ReloadCommitTime'),('rate','ReloadPlayRate')]}
        cdo.set_editor_property('ReloadPlayRate',r['original_timing']['duration']/4.133333206176758)
        r['staging'],staged,old=stage_actions_actor()
        newview=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(OWNER),staged.get_actor_location(),unreal.Rotator());assert newview
        newview.set_actor_label('PC_ReloadV5HumanView');newview.set_editor_property('Combatant',staged);actors.destroy_actor(old)
    r['temporary_rate']=cdo.get_editor_property('ReloadPlayRate')
    unreal.EditorPythonScripting.set_keep_python_script_alive(True);callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:r['status']='failed_startup';r['errors'].append(traceback.format_exc());r['protected_count']=len(rows);r['protected_records_unchanged']=check(rows);write()
