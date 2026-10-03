"""Fresh native motion/pose observation; no Python display/pose transform updates."""
import hashlib,json,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from ue_continuous_arms_native_runtime import NativeTrial,native_record
from ue_continuous_arms_runtime_trial import trial_records
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ContinuousArmsNativeV1'/os.environ['CS549_ARMS_NATIVE_IDENTITY']
assert not OUT.exists();OUT.mkdir(parents=True)
records=trial_records()+[native_record()]
def guard():return all(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in records)
assert guard()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
r={'status':'starting','errors':[],'frames':[],'checks':{},'captures':[],'native_saved':False,'display_updates':'UE Blueprint only'}
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
start=time.monotonic();trial=None;ready=None;phase=-1;phase_start=0;callback=None;ending=None;shot_count=0
phases=[('idle',2,None,(0,0),None),('forward',1.5,(1,0,0),None,None),('backward',1.5,(-1,0,0),None,None),('left',1.5,(0,-1,0),None,None),('right',1.5,(0,1,0),None,None),('stop',1,None,None,None),
        ('up',1,None,(60,0),None),('down',1,None,(-60,0),None),('yaw',1,None,(0,45),None),('reload',3,None,(0,0),'PC_RequestReload'),('fire',1,None,None,'PC_PlayerFire'),
        ('moving_reload',3,(0,-1,0),None,'PC_RequestReload'),('dead',1,None,None,'PC_ApplyDamage'),('reset',1,None,None,'PC_ResetLifecycle')]
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def end(error=None):
    global ending
    if error:r['errors'].append(error)
    r['native_bytes_unchanged']=guard();r['status']='failed' if r['errors'] else 'native_motion_numeric_pass_requires_image_review'
    if not r['errors']:
        r['checks']['movement']={n:any(f['phase']==n and f['speed']>100 for f in r['frames']) for n in ('forward','backward','left','right','moving_reload')}
        r['checks']['stationary_reload']=int(player.get_editor_property('ReloadCommitCount'))==2
        r['checks']['alive_ready_after_reset']=not player.get_editor_property('IsDead') and str(player.get_editor_property('ActionState'))=='Ready'
        r['checks']['dead_hidden']=all(not f['snapshot']['arms_visible'] for f in r['frames'] if f['phase']=='dead')
    write();levels.editor_request_end_play();ending=time.monotonic()
def enter(i):
    global phase,phase_start
    phase=i;phase_start=unreal.GameplayStatics.get_time_seconds(world)
    name,dur,move,rot,invoke=phases[i]
    if rot:controller.set_control_rotation(unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=0))
    if invoke:player.call_method(invoke,args=(1000.,) if invoke=='PC_ApplyDamage' else ())
def tick(delta):
    global trial,ready,world,player,controller,ending
    try:
        if ending is not None:
            if time.monotonic()-ending>2:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<240,'Native motion deadline'
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        if ready is None:ready=time.monotonic();return
        if time.monotonic()-ready<20:return
        controller=unreal.GameplayStatics.get_player_controller(world,0)
        if trial is None:trial=NativeTrial(world,player);return
        if not trial.initialized():return
        if phase<0:enter(0)
        n,dur,move,rot,invoke=phases[phase]
        if move:player.add_movement_input(unreal.Vector(*move),1,True)
        snap=trial.snapshot()
        assert snap['finger_local_delta']<1e-6 and snap['display_bound']
        assert max(abs(a-b) for a,b in zip(snap['camera_relative_cm'],(25,0,60)))<1e-6 and abs(snap['fov']-90)<1e-6
        action=str(player.get_editor_property('ActionState'));alive=not player.get_editor_property('IsDead')
        if action=='Ready':assert snap['original_anim_class']=='ABP_PC_Allied_Stride_v1_C'
        anchor=unreal.MathLibrary.transform_location(trial.weapon.get_actor_transform(),unreal.Vector(-.5,-8,0))
        error=(anchor-trial.n['grasp'](trial.n['vm'],'r')).length() if alive else 0
        assert error<.05,(n,error)
        r['frames'].append({'phase':n,'speed':player.get_velocity().length(),'action':action,'snapshot':snap,'anchor_cm':error,'game_seconds':unreal.GameplayStatics.get_time_seconds(world),
          'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],'reload_commits':int(player.get_editor_property('ReloadCommitCount'))})
        if unreal.GameplayStatics.get_time_seconds(world)-phase_start>dur:
            if n in ('idle','up','down','reload','moving_reload','reset'):
                p=OUT/(n+'.png');unreal.SystemLibrary.execute_console_command(world,'Shot -nosuffix filename="'+p.as_posix()+'"',controller)
                r['captures'].append({'phase_requested':n,'file':p.name,'note':'Unfrozen request; not exact-phase frozen proof'})
            if phase+1==len(phases):end()
            else:enter(phase+1)
    except Exception:end(traceback.format_exc())
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
