"""Natural-end cause observation only; native Blueprints own playback and transactions."""
import hashlib,json,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ['CS549_RELOAD_V5_IDENTITY']
assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from ue_player_actions_stage import stage_actions_actor
inventory=json.loads((ROOT/'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())
MODE=os.environ.get('CS549_RELOAD_V5_MODE','cause')
assert MODE in ('cause','timing')
rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']+inventory['files']
def guard():return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in rows)
def xyz(v):return [v.x,v.y,v.z]
def tr(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
r={'status':'starting','mode':MODE,'errors':[],'samples':[],'commands':[],'map_saved':False,'native_authored':False,
   'scope':'Natural-end observation of rejected diagnostic target, not reuse as baseline or repair acceptance',
   'runtime_control':'UE Blueprint only; no Python pose/attachment updater, seek, reset or freeze'}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
callback=None;ending=ready=None;wall_start=time.monotonic();busy=False
world=player=owner=pose=None;requested=None;last_sample=-1;returned=None
def snapshot(now):
    display=owner.skeletal_mesh_component;gun=owner.get_editor_property('DisplayGun')
    body=player.mesh;cam=player.get_editor_property('ParisPlayerCamera')
    instance=body.get_anim_instance()
    asset=instance.get_animation_asset() if instance and hasattr(instance,'get_animation_asset') else None
    return {'game_seconds':now,'elapsed_request':now-requested if requested is not None else None,
        'action_state':str(player.get_editor_property('ActionState')),'pose_mode':str(owner.get_editor_property('PoseMode')),
        'body_seconds':body.get_position() if asset else None,'body_asset':asset.get_path_name() if asset else None,
        'pose_seconds':pose.get_position(),'pose_asset':pose.get_anim_instance().get_animation_asset().get_path_name(),
        'reload_elapsed':player.get_editor_property('ReloadElapsed'),'reload_commits':int(player.get_editor_property('ReloadCommitCount')),
        'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
        'display_leader':display.get_editor_property('leader_pose_component').get_path_name(),
        'pose_leader':str(pose.get_editor_property('leader_pose_component')),
        'pose_world':tr(pose.get_socket_transform('',unreal.RelativeTransformSpace.RTS_WORLD)),
        'display_world':tr(owner.get_actor_transform()),'gun_world':tr(gun.get_actor_transform()),
        'framing':tr(owner.get_editor_property('FramingT')),
        'right_wrist':xyz(display.get_socket_location('hand_r')),'index03':xyz(display.get_socket_location('index_03_r')),
        'camera_relative':xyz(cam.get_editor_property('relative_location')),'fov':cam.get_editor_property('field_of_view')}
def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    r['protected_514_unchanged']=guard();r['status']='failed_preserve_evidence' if r['errors'] else 'natural_end_observed_requires_analysis'
    write();levels.editor_request_end_play();ending=time.monotonic()
def tick(delta):
    global busy,world,player,owner,pose,ready,requested,last_sample,returned
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>2:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-wall_start<220,'Bounded initialization/runtime deadline'
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        owner=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_ReloadNaturalEndV5'),None)
        if not owner or not owner.get_editor_property('Initialized'):return
        pose=owner.get_editor_property('PoseMesh')
        if ready is None:ready=time.monotonic();return
        if time.monotonic()-ready<8:return
        now=unreal.GameplayStatics.get_time_seconds(world)
        if requested is None:
            r['before_request']=snapshot(now)
            player.call_method('PC_ActionReload');requested=now
            r['commands'].append({'command':'PC_ActionReload','game_seconds':now,'after':str(player.get_editor_property('ActionState'))})
            assert str(player.get_editor_property('ActionState'))=='Reloading';write()
        if now-last_sample>=.025:
            r['samples'].append(snapshot(now));last_sample=now
        state=str(player.get_editor_property('ActionState'))
        if state=='Ready' and now-requested>.2:
            if returned is None:returned=now;r['native_ready_game_seconds']=now;write()
            elif now-returned>.5:finish()
        assert now-requested<12,'No natural Ready by diagnostic bound'
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    assert guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6')
    cdo=unreal.get_default_object(cls)
    r['original_timing']={'duration':cdo.get_editor_property('ReloadDuration'),'commit':cdo.get_editor_property('ReloadCommitTime'),'rate':cdo.get_editor_property('ReloadPlayRate')}
    if MODE=='cause':
        cdo.set_editor_property('ReloadDuration',4.133333);cdo.set_editor_property('ReloadCommitTime',3.95)
        r['timing_scope']='Process-local unsaved mismatched diagnostic defaults, not formal transaction selection'
    else:
        clip=unreal.load_asset('/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1')
        length=clip.get_play_length();assert length>0
        rate=r['original_timing']['duration']/length;assert .25<rate<2
        cdo.set_editor_property('ReloadPlayRate',rate)
        r['timing_sync']={'owner_clip_length':length,'body_play_rate':rate,'duration_unchanged':True,'commit_unchanged':True}
        r['timing_scope']='Unsaved playback-rate adaptation only; original body phase transaction, no direct ammo/control logic changes'
    r['staging'],staged,old=stage_actions_actor()
    owner=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(inventory['files'][1]['package']),staged.get_actor_location(),unreal.Rotator());assert owner
    owner.set_actor_label('PC_ReloadNaturalEndV5');owner.set_editor_property('Combatant',staged);actors.destroy_actor(old)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_startup';r['protected_514_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
