"""Fresh actual-city native action tests; test input injection, not runtime animation control."""
import hashlib,json,os,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/PlayerActionsV1'/os.environ['CS549_ACTION_IDENTITY']
assert not OUT.exists();OUT.mkdir(parents=True)
author=json.loads((OUT.parent/os.environ.get('CS549_ACTION_SOURCE','author_v7')/'result.json').read_text());assert not author['errors']
owner_author=json.loads((OUT.parent/os.environ.get('CS549_ACTION_OWNER_SOURCE','owner_author_v2')/'result.json').read_text());assert not owner_author['errors']
CAPTURE=os.environ.get('CS549_ACTION_CAPTURE','0')=='1'
package=author['packages'][0]['package']
records=json.loads((ROOT/'Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json').read_text())['files']+author['packages']+author.get('source_guards',[])
records+=owner_author['packages']
records+=json.loads((ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json').read_text())['files']
def guard():return all(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in records)
assert guard()
r={'status':'starting','errors':[],'frames':[],'phase_results':[], 'captures':[], 'native_saved':False,'runtime_pose_control':'UE Blueprint only'}
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
phase=-1;start=time.monotonic();ready_time=None;phase_start=0;ending=None;callback=None;busy=False;capture=None;origin=None;prone_origin=None;fixture=None
phases=[('walk',1.5,[],1),('run',1.5,['PC_ActionRunOn','PC_ActionFire','PC_ActionReload'],1),('slow',1.5,['PC_ActionRunOff','PC_ActionSlowOn'],1),
        ('run_backward',1,['PC_ActionSlowOff','PC_ActionRunOn'],-1),('run_right',1,[],2),('run_left',1,[],3),
        ('slow_backward',1,['PC_ActionRunOff','PC_ActionSlowOn'],-1),('slow_right',1,[],2),('slow_left',1,[],3),
        ('stop',.5,['PC_ActionSlowOff'],0),('jump',.2,['PC_ActionJump','PC_ActionFire','PC_ActionReload'],0),('jump_fall',.35,['PC_ActionJumpOff'],0),('landing',1,[],0),
        ('pending_crouch_reload',.15,['PC_ActionCrouch','PC_ActionReload','PC_ActionFire'],0),('crouch',1,[],0),
        ('crouch_forward',1,[],1),('crouch_backward',1,[],-1),('crouch_right',1,[],2),('crouch_left',1,[],3),('stand',1,['PC_ActionCrouch'],0),
        ('ceiling_crouch',.7,['PC_ActionCrouch'],0),('ceiling_stand_blocked',.7,['PC_ActionCrouch'],0),('ceiling_removed',.7,[],0),
        ('prone_wall_reject',.7,['PC_ActionProne'],0),('prone_wall_removed',.7,[],0),
        ('prone',1,['PC_ActionProne','PC_ActionFire','PC_ActionReload'],0),('crawl_forward',1,[],1),('crawl_backward',1,[],-1),
        ('crawl_wall_stop',1,[],1),('crawl_wall_removed',.2,[],0),('stand_prone',1,['PC_ActionProne'],0),
        ('reload_cancel_early',.1,['PC_ActionReload'],0),('run_cancel',.7,['PC_ActionRunOn'],0),
        ('reload_complete',3.2,['PC_ActionRunOff','PC_ActionReload'],0),('death_crouch_prepare',.7,['PC_ActionCrouch'],0),('die_crouch',1,['PC_ApplyDamage'],0),
        ('reset',1,['PC_ResetLifecycle'],0),('death_prone_prepare',.7,['PC_ActionProne'],0),('die_prone',1,['PC_ApplyDamage'],0),('final_reset',1,['PC_ResetLifecycle'],0)]
def spawn_box(location,scale):
    api=unreal.get_default_object(unreal.GameplayStatics.static_class())
    transform=unreal.Transform(location=location,rotation=player.get_actor_rotation(),scale=unreal.Vector(*scale))
    a=api.call_method('BeginDeferredActorSpawnFromClass',args=(world,unreal.StaticMeshActor.static_class(),transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    c=a.static_mesh_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
    c.set_collision_profile_name('BlockAll');c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    a=api.call_method('FinishSpawningActor',args=(a,transform,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    r.setdefault('fixtures',[]).append({'phase':phases[phase][0],'location':[location.x,location.y,location.z],'scale':scale,'scope':'test-only city collision fixture'})
    return a
def prop(n):return player.get_editor_property(n)
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    if 'world' in globals() and world:
        unreal.GameplayStatics.set_global_time_dilation(world,1)
        player.set_editor_property('custom_time_dilation',1.)
        player.mesh.set_editor_property('pause_anims',False)
        player.mesh.set_component_tick_enabled(True)
    r['protected_bytes_unchanged']=guard()
    def frames(name):return [f for f in r['frames'] if f['phase']==name]
    def any_case(name,predicate):return any(predicate(f) for f in frames(name))
    def wall_stable():
        samples=frames('crawl_wall_stop')
        if len(samples)<4 or 'crawl_wall_start' not in r:return False
        origin=unreal.Vector(*r['crawl_wall_start']);tail=samples[-4:]
        return (all((unreal.Vector(*f['location'])-origin).length()<=35 for f in samples)
            and all(f['blocked'] and f['speed']<.01 for f in tail)
            and (unreal.Vector(*tail[-1]['location'])-unreal.Vector(*tail[0]['location'])).length()<1)
    r['checks']={
        'walk_speed':any_case('walk',lambda f:140<=f['speed']<=155),
        'run_speed':any_case('run',lambda f:290<=f['speed']<=305),
        'slow_speed':any_case('slow',lambda f:60<=f['speed']<=70),
        'jump_up':any_case('jump',lambda f:f['velocity_z']>150),
        'jump_down':any_case('jump_fall',lambda f:f['velocity_z']<-100),
        'crouch_capsule_pose':any_case('crouch',lambda f:f['crouched'] and abs(f['half']-60)<.1 and f['pose']=='Rifle_CrouchLoop'),
        'crouch_forward':any_case('crouch_forward',lambda f:f['speed']>90 and f['pose']=='Rifle_Crouch_WalkFwd'),
        'crouch_backward':any_case('crouch_backward',lambda f:f['speed']>90 and f['pose']=='Rifle_Crouch_WalkBwd'),
        'crouch_side':any_case('crouch_right',lambda f:f['speed']>90 and f['pose']=='Rifle_Crouch_WalkRt'),
        'prone_capsule_pose':any_case('prone',lambda f:f['crouched'] and abs(f['half']-34)<.1 and f['pose']=='Rifle_Prone'),
        'crawl_forward':any_case('crawl_forward',lambda f:f['speed']>30 and f['pose']=='Rifle_Prone_WalkFwd'),
        'crawl_backward':any_case('crawl_backward',lambda f:f['speed']>30 and f['pose']=='Rifle_Prone_WalkBwd'),
        'stand_restored':any_case('stand_prone',lambda f:not f['crouched'] and 'ANIMATION_BLUEPRINT' in f['anim_mode']),
        'early_cancel_no_commit':any_case('run_cancel',lambda f:f['action']=='Ready' and f['commits']==0 and f['ammo']==r['initial_ammo']),
        'reload_one_commit':any_case('reload_complete',lambda f:f['action']=='Ready' and f['commits']==1 and sum(f['ammo'])==sum(r['initial_ammo'])),
        'dead':any_case('die_crouch',lambda f:f['dead'] and f['action']=='Dead' and f['speed']<.01),
        'reset_standing':any_case('reset',lambda f:not f['dead'] and not f['crouched'] and f['desired']==0 and f['action']=='Ready'),
        'blocked_standing_retains_crouch':any_case('ceiling_stand_blocked',lambda f:f['desired']==0 and f['crouched'] and abs(f['half']-60)<.1),
        'clearance_restores_standing':any_case('ceiling_removed',lambda f:not f['crouched'] and f['half']>90),
        'prone_long_body_rejects_wall':any_case('prone_wall_reject',lambda f:f['desired']==0 and not f['crouched']),
        'prone_death_and_reset':any_case('death_prone_prepare',lambda f:f['crouched'] and f['state']=='Prone') and any_case('die_prone',lambda f:f['dead']) and any_case('final_reset',lambda f:not f['dead'] and not f['crouched']),
        'run_fire_reload_rejected':any_case('run',lambda f:f['ammo']==r['initial_ammo'] and f['action']=='Ready'),
        'jump_pending_fire_reload_rejected':any_case('jump',lambda f:f['ammo']==r['initial_ammo'] and f['action']=='Ready'),
        'posture_pending_fire_reload_rejected':any_case('pending_crouch_reload',lambda f:f['ammo']==r['initial_ammo'] and f['action']=='Ready'),
        'prone_fire_reload_rejected':any_case('prone',lambda f:f['ammo']==r['initial_ammo'] and f['action']=='Ready'),
        'run_all_directions':all(any_case(n,lambda f:290<=f['speed']<=305) for n in ('run','run_backward','run_right','run_left')),
        'slow_all_directions':all(any_case(n,lambda f:60<=f['speed']<=70) for n in ('slow','slow_backward','slow_right','slow_left')),
        'crouch_left':any_case('crouch_left',lambda f:f['speed']>90 and f['pose']=='Rifle_Crouch_WalkLt'),
        'prone_crawl_sweep_stops_before_wall':wall_stable(),
    }
    r['status']='failed' if r['errors'] else ('native_action_numeric_pass_requires_visual_review' if all(r['checks'].values()) else 'native_action_checks_failed_preserve_evidence')
    write();levels.editor_request_end_play();ending=time.monotonic()
def enter(i):
    global phase,phase_start,origin,prone_origin,fixture
    phase=i;phase_start=unreal.GameplayStatics.get_time_seconds(world)
    name,dur,commands,move=phases[i]
    if name=='walk':
        r['initial_ammo']=[int(prop('LoadedAmmo')),int(prop('ReserveAmmo'))];origin=player.get_actor_location()
        r['original_location']=[origin.x,origin.y,origin.z]
    if name in ('walk','run','slow','run_backward','run_right','run_left','slow_backward','slow_right','slow_left','crouch_forward','crouch_backward','crouch_right','crouch_left'):
        player.character_movement.stop_movement_immediately()
        point=unreal.Vector(origin.x,origin.y,origin.z-96.2331619263+player.capsule_component.get_unscaled_capsule_half_height())
        player.set_actor_location(point,False,True)
        r.setdefault('test_start_resets',[]).append({'phase':name,'location':[point.x,point.y,point.z],'test_setup_not_navigation_success':True})
    if name=='prone':
        # Search a few nearby real-city locations with the actual clearance function.
        # Failures remain recorded; no teleport is counted as gameplay/path success.
        r['prone_location_checks']=[]
        for dx,dy in [(0,0),(-150,0),(-300,0),(0,-200),(0,200),(-400,-200)]:
            player.set_actor_location(origin+unreal.Vector(dx,dy,0),False,True);player.call_method('PC_CheckProneClearance')
            okay=bool(prop('ProneClear'));r['prone_location_checks'].append({'offset':[dx,dy],'clear':okay})
            if okay:prone_origin=player.get_actor_location();break
        assert prone_origin is not None,'No checked nearby city position admits prone; do not fake a pass'
    if name=='stand_prone' and int(prop('DesiredPosture'))!=2:commands=[]
    if name=='ceiling_stand_blocked':
        feet=player.get_actor_location()-unreal.Vector(0,0,player.capsule_component.get_unscaled_capsule_half_height())
        fixture=spawn_box(feet+unreal.Vector(0,0,135),(1.5,1.5,.1))
    if name in ('ceiling_removed','prone_wall_removed','crawl_wall_removed') and fixture:
        fixture.destroy_actor();fixture=None
    if name=='prone_wall_reject':
        feet=player.get_actor_location()-unreal.Vector(0,0,player.capsule_component.get_unscaled_capsule_half_height())
        fixture=spawn_box(feet+player.get_actor_forward_vector()*100+unreal.Vector(0,0,50),(.1,1.5,1))
    if name=='crawl_wall_stop':
        point=player.get_actor_location();r['crawl_wall_start']=[point.x,point.y,point.z]
        feet=point-unreal.Vector(0,0,player.capsule_component.get_unscaled_capsule_half_height())
        fixture=spawn_box(feet+player.get_actor_forward_vector()*160+unreal.Vector(0,0,50),(.1,1.5,1))
    for command in commands:
        before={'desired':prop('DesiredPosture'),'generation':prop('RestoreGeneration'),'seen':prop('SeenGeneration')}
        player.call_method(command,args=(1000.,) if command=='PC_ApplyDamage' else ())
        r.setdefault('commands',[]).append({'phase':name,'command':command,'before':before,
            'after':{'desired':prop('DesiredPosture'),'generation':prop('RestoreGeneration'),'seen':prop('SeenGeneration')}})
def snapshot():
    m=player.character_movement;s=player.mesh;c=player.capsule_component
    single=s.get_anim_instance()
    location=player.get_actor_location();forward=player.get_actor_forward_vector();side=player.get_actor_right_vector()
    body={}
    if str(prop('LocomotionState'))=='Prone':
        for name in ('head','hand_l','hand_r','foot_l','foot_r','pelvis'):
            delta=s.get_socket_location(name)-location;body[name]=[delta.dot(forward),delta.dot(side),delta.z+c.get_unscaled_capsule_half_height()]
    return {'phase':phases[phase][0],'seconds':unreal.GameplayStatics.get_time_seconds(world),'speed':player.get_velocity().length(),
        'location':[location.x,location.y,location.z],'body_bones_from_feet_cm':body,
        'velocity_z':player.get_velocity().z,'z':player.get_actor_location().z,'state':str(prop('LocomotionState')),'pose':str(prop('ActivePose')),
        'crouched':bool(player.get_editor_property('is_crouched')),'half':c.get_unscaled_capsule_half_height(),
        'desired':prop('DesiredPosture'),'generation':prop('RestoreGeneration'),'seen_generation':prop('SeenGeneration'),
        'clear':prop('ProneClear'),'blocked':prop('ProneBlocked'),
        'action':str(prop('ActionState')),'dead':bool(prop('IsDead')),'ammo':[int(prop('LoadedAmmo')),int(prop('ReserveAmmo'))],
        'commits':int(prop('ReloadCommitCount')),'single_time':s.get_position() if isinstance(single,unreal.AnimSingleNodeInstance) else None,
        'anim_mode':str(s.get_editor_property('animation_mode'))}
def tick(delta):
    global ready_time,world,player,callback,busy,ending,capture,camera
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>2:unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<300,'Action test deadline'
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        if capture:
            now=time.monotonic()
            if now-capture['wall_start']<.6:return
            controller=unreal.GameplayStatics.get_player_controller(world,0)
            if capture['stage']==0:
                pose=player.get_actor_location();forward=player.get_actor_forward_vector();side=player.get_actor_right_vector()
                target=pose+unreal.Vector(0,0,-30)
                camera.set_actor_location(pose+side*260+forward*120+unreal.Vector(0,0,30),False,False)
                camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),target),False)
                controller.set_view_target_with_blend(camera,0)
                path=OUT/(capture['name']+'_body.png');unreal.SystemLibrary.execute_console_command(world,'Shot -nosuffix filename="'+path.as_posix()+'"',controller)
                r['captures'].append({'file':path.name,'phase':capture['name'],'phase_frozen':True,'sample':capture['sample']})
                capture.update(stage=1,wall_start=now);return
            controller.set_view_target_with_blend(player,0)
            player.mesh.set_editor_property('pause_anims',False);player.mesh.set_component_tick_enabled(True)
            player.set_editor_property('custom_time_dilation',1.)
            unreal.GameplayStatics.set_global_time_dilation(world,1)
            capture=None
            if phase+1==len(phases):finish()
            else:enter(phase+1)
            write();return
        if ready_time is None:
            ready_time=time.monotonic()
            camera=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.CameraActor) if a.get_actor_label()=='ActionReviewCamera')
            controller=unreal.GameplayStatics.get_player_controller(world,0)
            controller.set_tickable_when_paused(True)
            controller.set_editor_property('should_perform_full_tick_when_paused',True)
            return
        if time.monotonic()-ready_time<20:return
        if phase<0:enter(0)
        name,dur,commands,movement=phases[phase]
        if movement:
            player.call_method('PC_ActionMoveRight' if movement in (2,3) else 'PC_ActionMoveForward',args=(-1. if movement==3 else (1. if movement==2 else float(movement)),))
        r['frames'].append(snapshot())
        if unreal.GameplayStatics.get_time_seconds(world)-phase_start>dur:
            r['phase_results'].append(snapshot())
            if CAPTURE and name in ('run','jump','jump_fall','landing','crouch','crouch_forward','crouch_right','prone','crawl_forward','reload_complete','reset'):
                unreal.GameplayStatics.set_global_time_dilation(world,.0001)
                player.set_editor_property('custom_time_dilation',0.)
                player.mesh.set_editor_property('pause_anims',True);player.mesh.set_component_tick_enabled(False)
                path=OUT/(name+'_fp.png');unreal.SystemLibrary.execute_console_command(world,'Shot -nosuffix filename="'+path.as_posix()+'"')
                capture={'name':name,'stage':0,'wall_start':time.monotonic(),'sample':snapshot()}
                r['captures'].append({'file':path.name,'phase':name,'phase_frozen':True,'sample':capture['sample']})
            elif phase+1==len(phases):finish()
            else:enter(phase+1)
            write()
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    assert not hasattr(unreal,'ParisBlueprintAuthoring')
    old=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_City_Player')
    gun=old.get_editor_property('WeaponAppearance')
    player=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(package),old.get_actor_location(),old.get_actor_rotation());assert player
    player.set_actor_label('PC_City_Player_ActionTrial');player.set_editor_property('WeaponAppearance',gun)
    gun.set_editor_property('Combatant',player);gun.set_editor_property('GripMesh',player.mesh);gun.set_owner(player)
    assert gun.attach_to_component(player.mesh,'hand_r',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
    display=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_Player_ContinuousArmsNativeV1')
    actors.destroy_actor(display)
    display=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(owner_author['packages'][0]['package']),player.get_actor_location(),unreal.Rotator())
    display.set_actor_label('PC_ActionOwnerViewTrial');display.set_editor_property('Combatant',player);actors.destroy_actor(old)
    camera=actors.spawn_actor_from_class(unreal.CameraActor,player.get_actor_location(),unreal.Rotator());camera.set_actor_label('ActionReviewCamera')
    r['substitution']='Unsaved team map player only; NPCs, gun/display classes and all on-disk map bytes retained'
    r['capture_method']='Disabled for functional acceptance; separate frozen-view diagnostics are not acceptance evidence' if not CAPTURE else 'Diagnostic only: tiny world dilation, paused source animation; do not use this run for action acceptance'
    unreal.EditorPythonScripting.set_keep_python_script_alive(True);callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_startup';r['protected_bytes_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
