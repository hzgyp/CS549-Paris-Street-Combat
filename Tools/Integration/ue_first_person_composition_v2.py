"""V3-based frozen ordinary-holding composition probe; no assets saved or gameplay acceptance."""
import hashlib, json, math, os, time, traceback
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
CASE=ROOT/'Failures/FP001-20261003-first-person-view'
archive=json.loads((CASE/'VERIFICATION.json').read_text(encoding='utf-8'))
assert archive['passed'], 'Complete failure archive before restarting'
manifest=json.loads((CASE/'MANIFEST.json').read_text(encoding='utf-8-sig'))
records=manifest['protected_files']
identity=os.environ['CS549_FP_V2_IDENTITY']
assert identity.replace('_','').isalnum()
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FirstPersonRebuildV2'/identity
assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'probe_source.py').write_bytes(Path(__file__).read_bytes())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(digest(ROOT/f['path'])==f['sha256'] for f in records)
report={'scope':__doc__,'read_cases':['FP001','V4 aiming'],'status':'initializing','errors':[],
        'samples':[],'native_saved':False,'visual_acceptance':False,'gameplay_with_display_muzzle_tested':False}
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
start=time.monotonic(); ending=None; busy=False; callback=None;ready_at=None;phase=-1;at=0;capture_requested=False;phase_frames=0
specs=[('source_v3',None),('A_near_right',[22,22,-16]),('B_near_right',[26,25,-18]),('C_near_right',[30,28,-20])]
def write():(OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def xyz(v):return [v.x,v.y,v.z]
def pose(component):
    result={}
    for side in ('l','r'):
        for finger in ('thumb','index','middle','ring','pinky'):
            for segment in (1,2,3):
                name=f'{finger}_0{segment}_{side}'
                parent=f'hand_{side}' if segment==1 else f'{finger}_0{segment-1}_{side}'
                t=component.get_socket_transform(name);p=component.get_socket_transform(parent)
                result[name]={'translation':xyz(unreal.MathLibrary.inverse_transform_location(p,t.translation)),
                    'axes':[xyz(unreal.MathLibrary.inverse_transform_direction(p,unreal.MathLibrary.transform_direction(t,v))) for v in (unreal.Vector(1,0,0),unreal.Vector(0,1,0),unreal.Vector(0,0,1))]}
    return result
def delta(a,b):
    return max(abs(x-y) for n in a for key in ('translation','axes') for x,y in zip(flat(a[n][key]),flat(b[n][key])))
def flat(values):
    return [y for x in values for y in x] if isinstance(values[0],list) else values
def grasp(component,side):
    fingers=('middle','ring','pinky') if side=='r' else ('index','middle','ring','pinky')
    names=[f'{f}_0{s}_{side}' for f in fingers for s in (2,3)]+[f'thumb_02_{side}',f'thumb_03_{side}']
    return sum((component.get_socket_location(n) for n in names),unreal.Vector())/len(names)
def finish(error=None):
    global ending
    if ending:return
    if error:report['errors'].append(error)
    report['status']='failed' if report['errors'] else 'static_composition_captured_requires_visual_review'
    levels.editor_request_end_play();ending=time.monotonic();write()
def spawn(cls,t):
    api=unreal.get_default_object(unreal.GameplayStatics.static_class())
    actor=api.call_method('BeginDeferredActorSpawnFromClass',args=(world,cls,t,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,player,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    return api.call_method('FinishSpawningActor',args=(actor,t,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
def setup():
    global source,world_gun,eye,controller,view,viewmesh,displaygun,source_pose,source_transform,gun_transform,relative_mesh
    source=player.get_component_by_class(unreal.SkeletalMeshComponent)
    world_gun=player.get_editor_property('WeaponAppearance')
    assert world_gun.get_class().get_name()=='BP_PC_RifleAttachmentV3_C'
    assert source.get_anim_instance().get_class().get_name()=='ABP_PC_Allied_Stride_v1_C'
    eye=player.get_component_by_class(unreal.CameraComponent)
    assert (eye.get_editor_property('relative_location')-unreal.Vector(25,0,60)).length()<1e-6
    assert eye.get_editor_property('field_of_view')==90
    controller=unreal.GameplayStatics.get_player_controller(world,0)
    player.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
    source.set_editor_property('pause_anims',True,unreal.PropertyAccessChangeNotifyMode.NEVER)
    source.set_component_tick_enabled(False)
    source_pose=pose(source);source_transform=source.get_world_transform();gun_transform=world_gun.get_actor_transform()
    relative_mesh=unreal.MathLibrary.make_relative_transform(source_transform,gun_transform)
    view=spawn(unreal.SkeletalMeshActor.static_class(),source_transform)
    viewmesh=view.get_component_by_class(unreal.SkeletalMeshComponent)
    viewmesh.set_skeletal_mesh_asset(source.get_skeletal_mesh_asset())
    for slot in range(source.get_num_materials()):viewmesh.set_material(slot,source.get_material(slot))
    viewmesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    viewmesh.set_only_owner_see(True);viewmesh.set_cast_shadow(False)
    viewmesh.set_leader_pose_component(source,True,False)
    viewmesh.add_tick_prerequisite_component(source)
    viewmesh.set_visibility(False)
    displaygun=spawn(unreal.StaticMeshActor.static_class(),gun_transform)
    sm=displaygun.static_mesh_component
    sm.set_mobility(unreal.ComponentMobility.MOVABLE)
    sm.set_static_mesh(world_gun.static_mesh_component.get_editor_property('static_mesh'))
    for slot in range(world_gun.static_mesh_component.get_num_materials()):sm.set_material(slot,world_gun.static_mesh_component.get_material(slot))
    sm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);sm.set_only_owner_see(True);sm.set_cast_shadow(False);sm.set_visibility(False)
    report['source_class']=source.get_anim_instance().get_class().get_path_name()
    report['source_camera']={'relative_cm':xyz(eye.get_editor_property('relative_location')),'fov':eye.get_editor_property('field_of_view')}
    report['world_weapon_class']=world_gun.get_class().get_path_name()
    report['materials_and_mesh']='Original same mesh/material slots; no masks or hidden bones; scale 1'
def begin(index):
    global phase,at,capture_requested,phase_frames
    phase=index;at=time.monotonic();capture_requested=False;phase_frames=0
    name,anchor=specs[index]
    if anchor is None:return
    source.set_owner_no_see(True);world_gun.static_mesh_component.set_owner_no_see(True)
    viewmesh.set_visibility(True);displaygun.static_mesh_component.set_visibility(True)
    camera=eye.get_world_transform();desired=unreal.MathLibrary.transform_location(camera,unreal.Vector(*anchor))
    goal=eye.get_world_location()+eye.get_forward_vector()*20000
    t=unreal.Transform(location=desired)
    for _ in range(8):
        look=unreal.MathLibrary.find_look_at_rotation(t.translation,goal)
        rotation=unreal.Rotator(pitch=0,yaw=look.yaw-90,roll=-look.pitch)
        t=unreal.Transform(location=unreal.Vector(),rotation=rotation,scale=unreal.Vector(1,1,1))
        t.translation=desired-unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,-8,0))
    view.set_actor_transform(unreal.MathLibrary.compose_transforms(relative_mesh,t),False,True)
    displaygun.set_actor_transform(t,False,True)
def measure():
    name,anchor=specs[phase];component=source if anchor is None else viewmesh;gun=world_gun if anchor is None else displaygun
    t=gun.get_actor_transform();camera=eye.get_world_transform()
    data={'name':name,'grasp_camera_cm':anchor,'source_pose_delta':delta(source_pose,pose(source)),
        'finger_local_delta':delta(source_pose,pose(component)),
        'rear_grasp_cm':(unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,-8,0))-grasp(component,'r')).length(),
        'support_grasp_cm':(unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,22.2,0))-grasp(component,'l')).length(),
        'bones_camera_cm':{n:xyz(unreal.MathLibrary.inverse_transform_location(camera,component.get_socket_location(n))) for n in ('pelvis','spine_03','head','upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r')},
        'original_weapon_binding':player.get_editor_property('WeaponAppearance')==world_gun,
        'camera_relative_cm':xyz(eye.get_editor_property('relative_location')),'fov':eye.get_editor_property('field_of_view'),
        'camera_world_cm':xyz(eye.get_world_location()),'camera_world_rotation':str(eye.get_world_rotation()),
        'settled_frames':phase_frames,'world_time_seconds':unreal.GameplayStatics.get_time_seconds(world)}
    assert data['source_pose_delta']<1e-6 and data['finger_local_delta']<1e-6,data
    assert data['original_weapon_binding'] and data['fov']==90
    return data
def tick(dt):
    global busy,world,player,ready_at
    if busy:return
    busy=True
    try:
        if ending:
            if not levels.is_in_play_in_editor() and time.monotonic()-ending>3:
                report['protected_40_unchanged']=all(digest(ROOT/f['path'])==f['sha256'] for f in records)
                report['protected_count']=len(records);write()
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        if time.monotonic()-start>240:finish('Composition probe timeout');return
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        if ready_at is None:
            unreal.GameplayStatics.get_player_controller(world,0).set_control_rotation(unreal.Rotator())
            player.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
            ready_at=time.monotonic();return
        if phase<0:
            if time.monotonic()-ready_at<20:return
            setup();begin(0);return
        run_phase()
    except Exception:finish(traceback.format_exc())
    finally:busy=False
def run_phase():
    global capture_requested,phase_frames
    phase_frames+=1
    name,_=specs[phase];path=OUT/(name+'.png')
    if time.monotonic()-at<5 or phase_frames<60:return
    if not capture_requested:
        report['samples'].append(measure());write()
        unreal.SystemLibrary.execute_console_command(world,'Shot -nosuffix filename="'+path.as_posix()+'"',controller)
        capture_requested=True;return
    if path.exists() and path.stat().st_size>1000 and time.monotonic()-at>3:
        if phase+1==len(specs):finish()
        else:begin(phase+1)

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback=unreal.register_slate_post_tick_callback(tick)
write();levels.editor_request_begin_play()
