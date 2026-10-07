"""One isolated native-owner visual gate. Frozen observations are not gameplay tests."""
import hashlib,json,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadContactBindingV3'/os.environ['CS549_APPROVED_IDENTITY']
assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
sys.path.insert(0,str(Path(__file__).parent))
from ue_player_actions_stage import stage_actions_actor
author=json.loads((OUT.parent/'binding_proof_author_v2/result.json').read_text())
assert not author['errors'] and author['status'].startswith('saved_unselected')
rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
rows+=author['packages']
def guard():return all((ROOT/e['path']).stat().st_size==e['size_bytes'] and hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()==e['sha256'] for e in rows)
def xyz(v):return [v.x,v.y,v.z]
def tr(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
def hollow(mesh,side):
    digits=('middle','ring','pinky','thumb') if side=='r' else ('index','middle','ring','pinky','thumb')
    return sum((mesh.get_socket_location(d+'_0'+str(i)+'_'+side) for d in digits for i in (2,3)),unreal.Vector())/(len(digits)*2)
r={'status':'starting','errors':[],'captures':[],'samples':[],'map_saved':False,
   'runtime_control':'existing UE Blueprint only; Python explicit diagnostic setup/seek/read',
   'diagnostic_target_derivative':author['diagnostic_derivative'],'functional_acceptance':False,
   'scope':'Unselected native independent pose-driver proof; no camera/model/finger/source/transaction logic edit'}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
callback=None;ending=ready=None;start=time.monotonic();busy=False
phase=-1;pending=None;world=player=owner=pose=None
phases=[('holding',None),('reload_start',0.),('reload_take',1.2),('reload_operate',2.2),('reload_return',3.4),('reload_finish',4.1),('reset_ready',None)]
def snapshot():
    display=owner.skeletal_mesh_component;gun=owner.get_editor_property('DisplayGun');camera=player.get_editor_property('ParisPlayerCamera')
    anchor=unreal.MathLibrary.transform_location(gun.get_actor_transform(),unreal.Vector(-.5,-8,0))
    return {'phase':phases[phase][0],'state':str(player.get_editor_property('ActionState')),
        'pose_mode':str(owner.get_editor_property('PoseMode')),'pose_seconds':pose.get_position(),
        'pose_asset':pose.get_anim_instance().get_animation_asset().get_path_name(),
        'pose_leader':str(pose.get_editor_property('leader_pose_component')),
        'display_leader':display.get_editor_property('leader_pose_component').get_path_name(),
        'pose_component':pose.get_path_name(),'body_component':player.mesh.get_path_name(),
        'grip_cm':(anchor-hollow(display,'r')).length(),'camera_relative':xyz(camera.get_editor_property('relative_location')),
        'camera_fov':camera.get_editor_property('field_of_view'),
        'source_right':xyz(hollow(pose,'r')),'display_right':xyz(hollow(display,'r')),
        'pose_lod':pose.get_predicted_lod_level(),'display_lod':display.get_predicted_lod_level(),
        'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
        'source_mesh':pose.get_skeletal_mesh_asset().get_path_name(),'display_mesh':display.get_skeletal_mesh_asset().get_path_name()}
def unfreeze():
    if world:
        unreal.GameplayStatics.set_global_time_dilation(world,1.)
        player.mesh.set_play_rate(1.)
        if pose:pose.set_play_rate(1.)
def finish(error=None):
    global ending
    if ending:return
    if error:r['errors'].append(error)
    unfreeze();r['protected_514_unchanged']=guard()
    r['status']='failed_preserve_evidence' if r['errors'] else 'frozen_target_views_recorded_requires_inspection'
    write();levels.editor_request_end_play();ending=time.monotonic()
def enter(index):
    global phase,pending
    unfreeze();phase=index;pending={'stage':'wait_native','wall':time.monotonic(),'issued':False}
    name,seconds=phases[phase]
    if name=='reload_start':
        assert abs(player.get_editor_property('ReloadDuration')-4.133333)<1e-5
        assert abs(player.get_editor_property('ReloadCommitTime')-3.95)<1e-5
        player.call_method('PC_ActionReload')
        assert str(player.get_editor_property('ActionState'))=='Reloading','Existing request not admitted'
    elif name=='reset_ready':
        player.call_method('PC_ResetLifecycle')
        r['reset_note']='Reset explicitly cancels diagnostic reload; not natural completion/ammo acceptance'
    write()
def tick(delta):
    global busy,world,player,owner,pose,ready,pending
    if busy:return
    busy=True
    try:
        if ending:
            if time.monotonic()-ending>2:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<260,'Isolated visual deadline'
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        owner=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_ReloadBindingProofV4'),None)
        if not owner or not owner.get_editor_property('Initialized'):return
        pose=owner.get_editor_property('PoseMesh')
        if ready is None:ready=time.monotonic();return
        if phase<0:
            if time.monotonic()-ready>20:enter(0)
            return
        name,seconds=phases[phase];now=time.monotonic()
        if pending['stage']=='wait_native':
            if now-pending['wall']<.5:return
            if seconds is not None:
                assert str(owner.get_editor_property('PoseMode'))=='Reloading'
                player.mesh.set_play_rate(0.);pose.set_play_rate(0.);pose.set_position(seconds,False)
            unreal.GameplayStatics.set_global_time_dilation(world,.0001)
            pending={'stage':'frozen_refresh','wall':now,'issued':False};return
        if pending['stage']=='frozen_refresh':
            if now-pending['wall']<1.:return
            if name=='reload_start':
                # One native fixture parameter calibration, not a pose/attachment frame loop.
                right,left=hollow(pose,'r'),hollow(pose,'l');look=unreal.MathLibrary.find_look_at_rotation(right,left)
                ori=unreal.Transform(rotation=unreal.Rotator(pitch=0,yaw=look.yaw-90,roll=-look.pitch))
                candidate=unreal.Transform();candidate.translation=right-unreal.MathLibrary.transform_location(ori,unreal.Vector(-.5,-8,0));candidate.rotation=ori.rotation;candidate.scale3d=unreal.Vector(1,1,1)
                relative=unreal.MathLibrary.make_relative_transform(candidate,pose.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD))
                pg=owner.get_editor_property('PoseGun');r['actual_phase0_hand_relative']=tr(relative)
                r['before_actual_calibration']=tr(pg.get_editor_property('ReloadHandRelativeT'))
                r['calibration_application']='Read/verify authored target calibration; no write to defaults-only instance'
                pending={'stage':'capture','wall':now,'issued':False};return
            pending={'stage':'capture','wall':now,'issued':False};return
        if pending['stage']=='capture':
            if now-pending['wall']<.7:return
            sample=snapshot();r['samples'].append(sample)
            assert sample['camera_relative']==[25.,0.,60.] and abs(sample['camera_fov']-90.)<1e-6
            assert sample['display_leader']==sample['pose_component'] and sample['pose_leader']=='None'
            if seconds is not None:assert abs(sample['pose_seconds']-seconds)<1e-5
            file=name+'.png';controller=unreal.GameplayStatics.get_player_controller(world,0)
            unreal.SystemLibrary.execute_console_command(world,'HighResShot 1280x720 filename="'+(OUT/file).as_posix()+'"',controller)
            r['captures'].append({'file':file,'frozen_sample':sample});write()
            pending={'stage':'file','wall':now,'issued':True};return
        if pending['stage']=='file':
            if now-pending['wall']<1.2:return
            assert (OUT/(name+'.png')).is_file(),'No actual viewport image'
            r['captures'][-1]['after_render_sample']=snapshot();write()
            if phase+1==len(phases):finish()
            else:enter(phase+1)
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    assert guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    # Defaults-only timing: transient loaded CDO before spawning test actors.
    # Never saved; process discard restores disk defaults. No live-user editor.
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6'))
    r['original_timing']={'duration':cdo.get_editor_property('ReloadDuration'),'commit':cdo.get_editor_property('ReloadCommitTime')}
    cdo.set_editor_property('ReloadDuration',4.133333);cdo.set_editor_property('ReloadCommitTime',3.95)
    r['diagnostic_timing_setup']='Unsaved loaded CDO defaults before test spawn, no game package save'
    r['staging'],staged,old=stage_actions_actor()
    replacement=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(author['packages'][1]['package']),staged.get_actor_location(),unreal.Rotator());assert replacement
    replacement.set_actor_label('PC_ReloadBindingProofV4');replacement.set_editor_property('Combatant',staged);actors.destroy_actor(old)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_startup';r['protected_514_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
