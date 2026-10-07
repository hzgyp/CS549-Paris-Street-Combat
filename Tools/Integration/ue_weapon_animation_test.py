"""Bridge-disabled unfrozen native transaction/recoil test on actual Paris city."""
import json,math,os,sys,time,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from weapon_animation_reuse_common import PLAYER,OWNER,RELOAD,output,guard
from ue_weapon_animation_stage import stage_candidate,candidate_records
OUT=output(os.environ['CS549_ANIMATION_IDENTITY'])
r={'status':'starting','errors':[],'checks':{},'samples':[],'map_saved':False,
   'runtime':'Native Blueprint; Python issues test requests and observes only'}
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world=player=view=None;callback=None;ready=ending=None;busy=False;start=time.monotonic()
steps=pending=None;wait_start=0;last_sample=0;walk=False;barrier=None


def write():
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')


def prop(k):return player.get_editor_property(k)
def state():return {k:str(prop(k)) for k in ('ActionState','LoadedAmmo','ReserveAmmo','ActionID','RestoreGeneration','ReloadCommitCount','ReloadTimeoutCount','ShotSequence','ShotOutcome')}
def ammo():return prop('LoadedAmmo')+prop('ReserveAmmo')
def check(name,ok):
    r['checks'][name]=bool(ok);write();assert ok,name
def wait(seconds=0,until=None,timeout=8):return {'seconds':seconds,'until':until,'timeout':timeout}
def fire():
    cam=player.get_component_by_class(unreal.CameraComponent)
    player.call_method('PC_RequestFire',args=(cam.get_world_location(),cam.get_forward_vector()))
def token():return prop('ActionID'),prop('RestoreGeneration')
def cancel(t):player.call_method('PC_EndReload',args=t)
def commit(t):player.call_method('PC_CommitReload',args=t)


def scenario():
    global walk,barrier
    yield wait(2)
    check('candidate_player_fresh',player.get_class().get_path_name().split('.')[0]==PLAYER)
    check('candidate_owner_fresh',view.get_class().get_path_name().split('.')[0]==OWNER)
    check('new_duration_and_late_commit',abs(prop('ReloadDuration')-4.133333206)<.001 and abs(prop('ReloadCommitTime')-3.95)<.001)
    baseline=state();total=ammo();initial_position=player.get_actor_location()
    player.call_method('PC_RequestReload');t=token()
    check('new_reload_started',str(prop('ActionState'))=='Reloading')
    commit(t);check('early_commit_rejected',ammo()==total and prop('LoadedAmmo')==int(baseline['LoadedAmmo']))
    old_id=prop('ActionID');player.call_method('PC_RequestReload')
    check('duplicate_request_rejected',prop('ActionID')==old_id)
    walk=True;r['test_phase']='walking_reload'
    yield wait(.6)
    walk=False;player.character_movement.stop_movement_immediately()
    check('walk_reload_moves_character',(player.get_actor_location()-initial_position).length()>20 and str(prop('ActionState'))=='Reloading')
    check('no_old_midpoint_commit',prop('LoadedAmmo')==int(baseline['LoadedAmmo']))
    yield wait(until=lambda:bool(prop('ReloadCommitted')))
    check('one_late_commit',prop('ReloadCommitCount')==int(baseline['ReloadCommitCount'])+1 and prop('LoadedAmmo')==8 and ammo()==total)
    seq=prop('ShotSequence');fire();check('fire_busy_after_commit_rejected',prop('ShotSequence')==seq)
    commit(t);check('duplicate_commit_conserved',ammo()==total and prop('ReloadCommitCount')==int(baseline['ReloadCommitCount'])+1)
    yield wait(until=lambda:str(prop('ActionState'))=='Ready')
    check('returns_original_locomotion','ABP_PC_Allied_Stride_v1' in player.mesh.get_anim_instance().get_class().get_name())
    old_id=prop('ActionID');player.call_method('PC_RequestReload');check('full_magazine_rejected',prop('ActionID')==old_id)
    r['test_phase']='native_recoil';gun=view.get_editor_property('DisplayGun');hold=gun.get_actor_location()
    before=state();fire();check('accepted_fire_one_round',prop('LoadedAmmo')==int(before['LoadedAmmo'])-1 and prop('ShotSequence')==int(before['ShotSequence'])+1)
    seq=prop('ShotSequence');fire();check('cooldown_rejects_without_new_sequence',prop('ShotSequence')==seq)
    yield wait(until=lambda:bool(view.get_editor_property('RecoilActive')),timeout=2)
    check('existing_shoot_clip_active',str(view.get_editor_property('PoseMode'))=='Recoil')
    yield wait(.12)
    check('gun_recoil_visible_in_native_transform',(gun.get_actor_location()-hold).length()>.05)
    r['recoil_peak_displacement_cm']=(gun.get_actor_location()-hold).length()
    yield wait(until=lambda:not view.get_editor_property('RecoilActive'),timeout=2)
    check('recoil_returns_holding',str(view.get_editor_property('PoseMode'))=='Holding')
    fire();yield wait(.3);seq=prop('ShotSequence');fire()
    check('repeat_accepted_fire_restarts_source_motion',prop('ShotSequence')==seq+1)
    yield wait(.12)
    check('repeated_fire_keeps_native_recoil',bool(view.get_editor_property('RecoilActive')))
    yield wait(until=lambda:not view.get_editor_property('RecoilActive'),timeout=2)
    before=state();total=ammo();player.call_method('PC_RequestReload');t=token()
    yield wait(.4)
    player.call_method('PC_ActionRunOn');player.call_method('PC_ActionRunOff')
    check('run_cancels_before_commit',str(prop('ActionState'))=='Ready' and state()['LoadedAmmo']==before['LoadedAmmo'] and ammo()==total)
    commit(t);check('stale_cancelled_token_rejected',state()['LoadedAmmo']==before['LoadedAmmo'] and ammo()==total)
    player.call_method('PC_RequestReload');t=token();yield wait(.4)
    player.call_method('PC_Die');commit(t)
    check('death_before_commit_no_ammo',str(prop('ActionState'))=='Dead' and ammo()==total and state()['LoadedAmmo']==before['LoadedAmmo'])
    player.call_method('PC_ResetLifecycle');commit(t)
    yield wait(.1)
    check('reset_generation_rejects_old_event',str(prop('ActionState'))=='Ready' and ammo()==total and state()['LoadedAmmo']==before['LoadedAmmo'])
    check('reset_clears_recoil',not view.get_editor_property('RecoilActive'))
    timeout_count=prop('ReloadTimeoutCount');player.call_method('PC_RequestReload')
    player.mesh.set_editor_property('pause_anims',True)
    r['test_phase']='missing_phase_timeout'
    yield wait(until=lambda:str(prop('ActionState'))=='Ready',timeout=7)
    player.mesh.set_editor_property('pause_anims',False)
    check('missing_animation_timeout_only_cancels',ammo()==total and state()['LoadedAmmo']==before['LoadedAmmo'] and prop('ReloadTimeoutCount')==timeout_count+1)
    player.call_method('PC_RequestReload');t=token()
    r['test_phase']='death_after_commit'
    yield wait(until=lambda:bool(prop('ReloadCommitted')))
    loaded=prop('LoadedAmmo');reserve=prop('ReserveAmmo');count=prop('ReloadCommitCount')
    player.call_method('PC_Die');commit(t);player.call_method('PC_ResetLifecycle');commit(t)
    yield wait(.3)
    check('death_reset_after_commit_keeps_one_transfer',prop('LoadedAmmo')==loaded and prop('ReserveAmmo')==reserve and prop('ReloadCommitCount')==count)
    # One disposable near-wall collision fixture; no map/save or ammo field edits.
    cam=player.get_component_by_class(unreal.CameraComponent);transform=cam.get_world_transform()
    transform.translation=cam.get_world_location()+cam.get_forward_vector()*80
    transform.scale3d=unreal.Vector(.02,3,3)
    api=unreal.get_default_object(unreal.GameplayStatics.static_class())
    barrier=api.call_method('BeginDeferredActorSpawnFromClass',args=(world,unreal.StaticMeshActor.static_class(),transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    c=barrier.static_mesh_component;c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));c.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
    c.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_IGNORE)
    c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY,unreal.CollisionResponseType.ECR_BLOCK)
    barrier=api.call_method('FinishSpawningActor',args=(barrier,transform,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    yield wait(.3);fire()
    check('near_wall_retains_gun_obstruction',str(prop('ShotOutcome')) in ('Barrel blocked','Muzzle blocked','World blocked'))
    barrier.destroy_actor();barrier=None
    yield wait(1)
    cam=player.get_component_by_class(unreal.CameraComponent)
    check('protected_camera',(cam.get_editor_property('relative_location')-unreal.Vector(25,0,60)).length()<1e-6 and abs(cam.get_editor_property('field_of_view')-90)<1e-6)
    check('display_no_collision','NO_COLLISION' in str(gun.static_mesh_component.get_collision_enabled()))
    check('display_binding_kept',prop('WeaponAppearance')==gun)
    r['final_state']=state();check('global_ammo_conservation',ammo()+prop('ShotSequence')==18)
    r['status']='native_player_reload_recoil_functional_checks_pass_pending_visual_review'


def finish(error=None):
    global ending
    if ending:return
    if error:r['errors'].append(error);r['status']='failed'
    if player:player.mesh.set_editor_property('pause_anims',False)
    if barrier:barrier.destroy_actor()
    r['protected_files_unchanged']=guard();r['candidate_files']=candidate_records(True)
    write();ending=time.monotonic();levels.editor_request_end_play()


def tick(delta):
    global world,player,view,ready,ending,busy,callback,steps,pending,wait_start,last_sample
    if busy:return
    busy=True
    try:
        if ending:
            if time.monotonic()-ending>3:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<300
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        if ready is None:
            view=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_AnimationOwnerViewTrial')
            ready=time.monotonic();return
        if time.monotonic()-ready<18 or not view.get_editor_property('Initialized'):return
        now=unreal.GameplayStatics.get_time_seconds(world)
        if walk:player.add_movement_input(player.get_actor_forward_vector(),1,False)
        if now-last_sample>.05:
            r['samples'].append({'phase':r.get('test_phase'),'time':now,'state':state(),
                'body_position':player.mesh.get_position(),'recoil':bool(view.get_editor_property('RecoilActive')),
                'pose_mode':str(view.get_editor_property('PoseMode')),
                'right_hand':str(view.skeletal_mesh_component.get_socket_location('hand_r')),
                'gun_location':str(view.get_editor_property('DisplayGun').get_actor_location())})
            last_sample=now
        if steps is None:steps=scenario()
        if pending:
            assert now-wait_start<pending['timeout'],'Scenario wait timed out '+str(r.get('test_phase'))
            if now-wait_start<pending['seconds'] or (pending['until'] and not pending['until']()):return
            pending=None
        try:pending=next(steps);wait_start=now
        except StopIteration:finish()
    except Exception:finish(traceback.format_exc())
    finally:busy=False


try:
    assert not hasattr(unreal,'ParisBlueprintAuthoring')
    r['staging'],_,_=stage_candidate(True)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_startup';write();unreal.SystemLibrary.quit_editor()
