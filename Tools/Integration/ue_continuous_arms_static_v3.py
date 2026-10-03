"""One complete-arm ordinary holding comparison in real Paris PIE; static, no gameplay claim."""
import hashlib,json,os,time,traceback
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3'
IDENTITY=os.environ.get('CS549_CONTINUOUS_ARMS_IDENTITY','static_v1')
assert IDENTITY.replace('_','').isalnum()
OUT=E/IDENTITY;assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
protected=json.loads((ROOT/'Failures/FP001-20261003-first-person-view/MANIFEST.json').read_text(encoding='utf-8-sig'))['protected_files']
native=json.loads((E/'native_material_v1/result.json').read_text())
assert not native['errors']
records=protected+native['native_files']
def guard():return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in records)
assert guard()
report={'scope':__doc__,'errors':[],'samples':[],'native_saved':False,'visual_acceptance':False,
        'gameplay_with_display_muzzle_tested':False,'read_cases':['FP001','V2 static offsets','V4 aiming','rejected finger layer']}
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
start=time.monotonic();ready=None;ending=None;busy=False;phase=-1;since=0;frames=0;captured=False

def write():(OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def xyz(v):return [v.x,v.y,v.z]
def pose(component):
    result={}
    for side in ('l','r'):
        for finger in ('thumb','index','middle','ring','pinky'):
            for segment in (1,2,3):
                n=f'{finger}_0{segment}_{side}';p=f'hand_{side}' if segment==1 else f'{finger}_0{segment-1}_{side}'
                t=component.get_socket_transform(n);parent=component.get_socket_transform(p)
                result[n]=xyz(unreal.MathLibrary.inverse_transform_location(parent,t.translation))
                for axis in (unreal.Vector(1,0,0),unreal.Vector(0,1,0),unreal.Vector(0,0,1)):
                    result[n]+=xyz(unreal.MathLibrary.inverse_transform_direction(parent,unreal.MathLibrary.transform_direction(t,axis)))
    return result
def delta(a,b):return max(abs(x-y) for n in a for x,y in zip(a[n],b[n]))
def grasp(c,side):
    fs=('middle','ring','pinky') if side=='r' else ('index','middle','ring','pinky')
    ns=[f'{f}_0{s}_{side}' for f in fs for s in (2,3)]+[f'thumb_02_{side}',f'thumb_03_{side}']
    return sum((c.get_socket_location(n) for n in ns),unreal.Vector())/len(ns)
def spawn(cls,t):
    api=unreal.get_default_object(unreal.GameplayStatics.static_class())
    a=api.call_method('BeginDeferredActorSpawnFromClass',args=(world,cls,t,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,player,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    return api.call_method('FinishSpawningActor',args=(a,t,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
def finish(error=None):
    global ending
    if ending:return
    if error:report['errors'].append(error)
    report['status']='failed' if report['errors'] else 'static_captured_requires_image_and_human_review'
    levels.editor_request_end_play();ending=time.monotonic();write()
def setup():
    global source,eye,controller,gun,view,vm,display,original_pose,relative
    source=player.get_component_by_class(unreal.SkeletalMeshComponent)
    eye=player.get_component_by_class(unreal.CameraComponent)
    gun=player.get_editor_property('WeaponAppearance')
    assert source.get_anim_instance().get_class().get_name()=='ABP_PC_Allied_Stride_v1_C'
    assert gun.get_class().get_name()=='BP_PC_RifleAttachmentV3_C'
    assert (eye.get_editor_property('relative_location')-unreal.Vector(25,0,60)).length()<1e-6
    assert eye.get_editor_property('field_of_view')==90
    source.set_editor_property('pause_anims',True,unreal.PropertyAccessChangeNotifyMode.NEVER)
    source.set_component_tick_enabled(False)
    original_pose=pose(source)
    relative=unreal.MathLibrary.make_relative_transform(source.get_world_transform(),gun.get_actor_transform())
    view=spawn(unreal.SkeletalMeshActor.static_class(),source.get_world_transform())
    vm=view.skeletal_mesh_component
    vm.set_skeletal_mesh_asset(unreal.load_asset('/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3'))
    assert [vm.get_material(i).get_path_name() for i in range(vm.get_num_materials())]==native['after_materials'], 'Fresh-load material binding mismatch'
    vm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);vm.set_only_owner_see(True);vm.set_cast_shadow(False)
    vm.set_leader_pose_component(source,True,False);vm.add_tick_prerequisite_component(source);vm.set_visibility(False)
    display=spawn(unreal.StaticMeshActor.static_class(),gun.get_actor_transform())
    sm=display.static_mesh_component;sm.set_mobility(unreal.ComponentMobility.MOVABLE)
    sm.set_static_mesh(gun.static_mesh_component.get_editor_property('static_mesh'))
    for i in range(gun.static_mesh_component.get_num_materials()):sm.set_material(i,gun.static_mesh_component.get_material(i))
    sm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);sm.set_only_owner_see(True);sm.set_cast_shadow(False);sm.set_visibility(False)
    report['source_class']=source.get_anim_instance().get_class().get_path_name()
    report['materials']=[vm.get_material(i).get_path_name() for i in range(vm.get_num_materials())]
    report['geometry']='Complete existing upper limbs; no opacity masks, head, torso or equipment faces'
def begin(index):
    global phase,since,frames,captured
    phase=index;since=time.monotonic();frames=0;captured=False
    if index==0:return
    source.set_owner_no_see(True);gun.static_mesh_component.set_owner_no_see(True)
    camera=eye.get_world_transform();desired=unreal.MathLibrary.transform_location(camera,unreal.Vector(22,22,-16))
    goal=eye.get_world_location()+eye.get_forward_vector()*20000
    t=unreal.Transform(location=desired)
    for _ in range(8):
        look=unreal.MathLibrary.find_look_at_rotation(t.translation,goal)
        t=unreal.Transform(location=unreal.Vector(),rotation=unreal.Rotator(pitch=0,yaw=look.yaw-90,roll=-look.pitch),scale=unreal.Vector(1,1,1))
        t.translation=desired-unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,-8,0))
    view.set_actor_transform(unreal.MathLibrary.compose_transforms(relative,t),False,True)
    display.set_actor_transform(t,False,True)
    vm.set_visibility(True);display.static_mesh_component.set_visibility(True)
def measure():
    c=source if phase==0 else vm;g=gun if phase==0 else display;t=g.get_actor_transform();camera=eye.get_world_transform()
    d={'name':'source_v3' if phase==0 else 'continuous_arms','source_finger_delta':delta(original_pose,pose(source)),
       'follower_finger_delta':delta(original_pose,pose(c)),
       'right_grasp_cm':(unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,-8,0))-grasp(c,'r')).length(),
       'support_grasp_cm':(unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,22.2,0))-grasp(c,'l')).length(),
       'camera_relative_cm':xyz(eye.get_editor_property('relative_location')),'camera_world_cm':xyz(eye.get_world_location()),
       'fov':eye.get_editor_property('field_of_view'),'original_weapon_binding':player.get_editor_property('WeaponAppearance')==gun,
       'bones_camera_cm':{n:xyz(unreal.MathLibrary.inverse_transform_location(camera,c.get_socket_location(n))) for n in ('upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r')},
       'settled_frames':frames}
    assert d['source_finger_delta']<1e-6 and d['follower_finger_delta']<1e-6,d
    assert d['original_weapon_binding'] and d['fov']==90,d
    return d
def tick(dt):
    global busy,world,player,ready,controller,frames,captured
    if busy:return
    busy=True
    try:
        if ending:
            if not levels.is_in_play_in_editor() and time.monotonic()-ending>3:
                report['protected_42_unchanged']=guard();write()
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        if time.monotonic()-start>240:finish('Static probe timeout');return
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        if ready is None:
            controller=unreal.GameplayStatics.get_player_controller(world,0)
            controller.set_control_rotation(unreal.Rotator())
            player.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
            ready=time.monotonic();return
        if phase<0:
            if time.monotonic()-ready<20:return
            setup();begin(0);return
        frames+=1
        if time.monotonic()-since<5 or frames<60:return
        name='source_v3' if phase==0 else 'continuous_arms';p=OUT/(name+'.png')
        if not captured:
            report['samples'].append(measure());write()
            unreal.SystemLibrary.execute_console_command(world,'Shot -nosuffix filename="'+p.as_posix()+'"',controller)
            captured=True;return
        if p.exists() and p.stat().st_size>1000:
            if phase==1:finish()
            else:begin(1)
    except Exception:finish(traceback.format_exc())
    finally:busy=False

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback=unreal.register_slate_post_tick_callback(tick)
write();levels.editor_request_begin_play()
