"""Native C++ early city proof. Python prepares once, then observes; no pose loop."""
import json,math,os,sys,time,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import ROOT,BASE,CONFIG,guard,config
OUT=BASE/os.environ['CS549_GRIP_BINDING_ID'];assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
c=config()
r={'status':'starting','errors':[],'samples':[],'captures':[],'packages':[],
   'selected':False,'map_saved':False,'functional_acceptance':False,
   'runtime_control':'UE source animation and native C++ actor; Python one-time binding/read-only pose observations',
   'grip_source':'accepted V18 private configuration; unchanged data', 'guards_before':guard()}
assert not r['guards_before']['mismatches']
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
start=time.monotonic();ready=bound=ending=None;callback=None;busy=False
world=player=owner=new=controller=None;phase=-1;phase_time=0;capture_time=None
MOTION=os.environ.get('CS549_GRIP_BINDING_SCOPE')=='motion'
phases=[('idle',0,2,None,None),('look_up',20,2,None,None),('look_down',-20,2,None,None)]
if MOTION:phases += [('walk_forward',0,2,(1,0,0),None),('walk_left',0,2,(0,-1,0),None),('stop',0,1,None,None),('reload',0,3,None,'PC_RequestReload'),('post_reload',0,1,None,None)]
r['scope']='native_idle_movement_reload' if MOTION else 'native_idle_only'
r['motion_frames']=[]

def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def xyz(v):return [v.x,v.y,v.z]
def tr(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
def angular_degrees(actual,expected):
    # AngularDistance requires unit inputs. Normalize only temporary read values,
    # never the immutable config file or the native pose. Preserve .01degree gate.
    a=[actual.x,actual.y,actual.z,actual.w]
    na=math.sqrt(sum(x*x for x in a));nb=math.sqrt(sum(x*x for x in expected))
    dot=abs(sum(x*y for x,y in zip(a,expected))/(na*nb))
    return math.degrees(2*math.acos(max(-1.,min(1.,dot))))

def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    r['guards_after']=guard()
    r['status']='stopped_native_binding_gate' if r['errors'] else 'actual_native_idle_views_recorded_requires_image_review'
    write();levels.editor_request_end_play();ending=time.monotonic()

def snapshot():
    camera=player.get_editor_property('ParisPlayerCamera')
    pose=new.get_editor_property('Pose');gun=new.get_editor_property('Gun')
    rel=unreal.MathLibrary.make_relative_transform(gun.get_world_transform(),pose.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD))
    expected=unreal.Transform()
    expected.translation=unreal.Vector(*c['gun_hand_relative']['t'])
    expected.rotation=unreal.Quat(*c['gun_hand_relative']['q'])
    expected.scale3d=unreal.Vector(*c['gun_hand_relative']['s'])
    angle=angular_degrees(rel.rotation,c['gun_hand_relative']['q'])
    actual_fingers={}
    for bone,row in c['fingers_local'].items():
        parent=pose.get_parent_bone(bone)
        local=unreal.MathLibrary.make_relative_transform(pose.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT),pose.get_socket_transform(parent,unreal.RelativeTransformSpace.RTS_COMPONENT))
        actual_fingers[bone]={'rotation_degrees':angular_degrees(local.rotation,row['q']),'scale':xyz(local.scale3d),'q':[local.rotation.x,local.rotation.y,local.rotation.z,local.rotation.w]}
    support=unreal.MathLibrary.make_relative_transform(pose.get_socket_transform('hand_l',unreal.RelativeTransformSpace.RTS_COMPONENT),pose.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_COMPONENT))
    actual_support_cm=(support.translation-unreal.Vector(*c['support_hand_relative_to_right']['t'])).length()
    s={'phase':phases[phase][0],'native_updates':int(new.get_editor_property('NativePoseUpdates')),
       'error':str(new.get_editor_property('BindingError')),'action':str(new.get_editor_property('ObservedAction')),
       'support_cm':new.get_editor_property('SupportErrorCm'),'limb_length_cm':new.get_editor_property('LimbLengthErrorCm'),
       'finger_rotation_degrees':new.get_editor_property('FingerRotationErrorDegrees'),
       'gun_hand_cm':(rel.translation-expected.translation).length(),'gun_hand_degrees':angle,
       'actual_finger_locals':actual_fingers,'actual_support_relative_cm':actual_support_cm,
       'gun_relative':tr(rel),'frame':tr(new.get_editor_property('CachedAssemblyFrame')),
       'camera_relative_cm':xyz(camera.get_editor_property('relative_location')),'fov':camera.get_editor_property('field_of_view'),
       'mesh':pose.get_skinned_asset().get_path_name(),'materials':[pose.get_material(i).get_path_name() for i in range(pose.get_num_materials())],
       'source_mesh':player.mesh.get_skeletal_mesh_asset().get_path_name(),
       'source_anim':player.mesh.get_anim_instance().get_class().get_path_name(),
       'gun_parent':gun.get_attach_parent().get_path_name(),'gun_socket':str(gun.get_attach_socket_name()),
       'authoritative_weapon_unchanged':player.get_editor_property('WeaponAppearance')==owner.get_editor_property('DisplayGun'),
       'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
       'visible':pose.is_visible(),'gun_collision':str(gun.get_collision_enabled()),
       'game_seconds':unreal.GameplayStatics.get_time_seconds(world)}
    assert s['error']=='',s
    if s['action']=='Ready':
        assert s['support_cm']<.2 and s['limb_length_cm']<.01 and s['finger_rotation_degrees']<.01,s
        assert actual_support_cm<.2 and max(x['rotation_degrees'] for x in actual_fingers.values())<.01,s
    else:assert MOTION and s['action']=='Reloading',s
    assert max(abs(x-.9) for x in actual_fingers['pinky_02_r']['scale'])<1e-4,s
    assert s['gun_hand_cm']<.01 and s['gun_hand_degrees']<.01,s
    assert max(abs(a-b) for a,b in zip(s['camera_relative_cm'],(25,0,60)))<1e-6 and abs(s['fov']-90)<1e-6,s
    assert s['authoritative_weapon_unchanged'] and s['gun_socket']=='hand_r' and s['visible'],s
    return s

def observe_motion():
    camera=player.get_editor_property('ParisPlayerCamera');gun=new.get_editor_property('Gun');pose=new.get_editor_property('Pose')
    action=str(new.get_editor_property('ObservedAction'))
    gt=unreal.MathLibrary.make_relative_transform(gun.get_world_transform(),camera.get_world_transform())
    wt=unreal.MathLibrary.make_relative_transform(pose.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD),camera.get_world_transform())
    f={'phase':phases[phase][0],'seconds':unreal.GameplayStatics.get_time_seconds(world),'action':action,
       'native_updates':int(new.get_editor_property('NativePoseUpdates')),'speed':player.get_velocity().length(),
       'gun_camera':tr(gt),'wrist_camera':tr(wt),'support_cm':new.get_editor_property('SupportErrorCm'),
       'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
       'commits':int(player.get_editor_property('ReloadCommitCount'))}
    previous=r['motion_frames'][-1] if r['motion_frames'] else None
    r['motion_frames'].append(f)
    if action=='Ready':assert f['support_cm']<.2,f
    if previous and previous['action']=='Reloading' and action=='Ready':
        f['natural_end_gun_step_cm']=sum((a-b)**2 for a,b in zip(f['gun_camera']['t'],previous['gun_camera']['t']))**.5
        f['natural_end_wrist_step_cm']=sum((a-b)**2 for a,b in zip(f['wrist_camera']['t'],previous['wrist_camera']['t']))**.5
        f['sample_interval_seconds']=f['seconds']-previous['seconds']
        write()
        assert max(f['natural_end_gun_step_cm'],f['natural_end_wrist_step_cm'])<3,f

def enter(index):
    global phase,phase_time,capture_time
    phase=index;phase_time=unreal.GameplayStatics.get_time_seconds(world);capture_time=None
    controller.set_control_rotation(unreal.Rotator(pitch=phases[index][1],yaw=0,roll=0))
    invoke=phases[index][4]
    if invoke:
        r['reload_before']={'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],'commits':int(player.get_editor_property('ReloadCommitCount'))}
        player.call_method(invoke)
        assert str(player.get_editor_property('ActionState'))=='Reloading','Reload request not admitted'

def tick(delta):
    global busy,world,player,owner,new,controller,ready,bound,capture_time
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>2:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<240,'Isolated native proof deadline'
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        owner=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_Player_ContinuousArmsNativeV1'),None)
        if not owner or not owner.get_editor_property('Initialized'):return
        if ready is None:ready=time.monotonic();return
        if time.monotonic()-ready<20:return
        controller=unreal.GameplayStatics.get_player_controller(world,0)
        if bound is None:
            new=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisGripV18Actor) if a.get_actor_label()=='PC_GripBindingV18Proof')
            cfg=unreal.new_object(unreal.ParisGripV18Config,outer=new)
            cfg.set_editor_property('BindingJson',CONFIG.read_text())
            camera=player.get_editor_property('ParisPlayerCamera')
            oldgun=owner.get_editor_property('DisplayGun')
            r['source_weapon_before_binding']=oldgun.get_path_name()
            ok=new.bind_existing_pose(player,player.mesh,camera,oldgun,unreal.load_asset(c['source_mesh']),unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'),cfg)
            r['bind_return']=ok;r['bind_error']=str(new.get_editor_property('BindingError'));write()
            assert ok,r['bind_error']
            # Visual-only hides, once. Source animation and authoritative weapon remain untouched.
            owner.set_actor_hidden_in_game(True);oldgun.set_actor_hidden_in_game(True)
            bound=time.monotonic();enter(0);return
        move=phases[phase][3]
        if move:player.add_movement_input(unreal.Vector(*move),1.,True) # Test stimulus only, not pose control.
        if MOTION:observe_motion()
        if unreal.GameplayStatics.get_time_seconds(world)-phase_time<phases[phase][2]:return
        if capture_time is None:
            s=snapshot();r['samples'].append(s)
            file=phases[phase][0]+'.png'
            unreal.SystemLibrary.execute_console_command(world,'HighResShot 1280x720 filename="'+(OUT/file).as_posix()+'"',controller)
            r['captures'].append({'file':file,'request_sample':s,'frozen':False});write();capture_time=time.monotonic();return
        if time.monotonic()-capture_time<2:return
        assert (OUT/(phases[phase][0]+'.png')).is_file(),'Missing actual rendered viewport'
        r['captures'][-1]['after_render_sample']=snapshot();write()
        if phase+1==len(phases):
            if MOTION:
                before=r['reload_before'];after=r['samples'][-1]['ammo']
                r['motion_checks']={'walk_forward':any(f['phase']=='walk_forward' and f['speed']>100 for f in r['motion_frames']),
                    'walk_left':any(f['phase']=='walk_left' and f['speed']>100 for f in r['motion_frames']),
                    'one_conserved_reload':int(player.get_editor_property('ReloadCommitCount'))==before['commits']+1 and sum(after)==sum(before['ammo']) and after[0]>before['ammo'][0],
                    'native_ready_return':str(player.get_editor_property('ActionState'))=='Ready'}
                assert all(r['motion_checks'].values()),r['motion_checks']
            finish()
        else:enter(phase+1)
    except Exception:finish(traceback.format_exc())
    finally:busy=False

try:
    assert hasattr(unreal,'ParisGripV18Actor') and not hasattr(unreal,'ParisBlueprintAuthoring')
    actor=actors.spawn_actor_from_class(unreal.ParisGripV18Actor,unreal.Vector(),unreal.Rotator());assert actor
    actor.set_actor_label('PC_GripBindingV18Proof')
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='stopped_startup';r['guards_after']=guard();write();unreal.SystemLibrary.quit_editor()
