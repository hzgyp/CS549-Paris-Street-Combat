"""Actual-city complete-arm motion diagnostic; transient only, no native saves."""
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3'
IDENTITY = os.environ['CS549_ARMS_DYNAMIC_IDENTITY']
MODE = os.environ.get('CS549_ARMS_DYNAMIC_MODE', 'early')
assert IDENTITY.replace('_', '').isalnum() and MODE in ('early', 'full','tail')
OUT = BASE/IDENTITY
assert not OUT.exists(), 'Preserve occupied identity'
OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
protected = json.loads((ROOT/'Failures/FP001-20261003-first-person-view/MANIFEST.json').read_text(encoding='utf-8-sig'))['protected_files']
native = json.loads((BASE/'native_material_v1/result.json').read_text())
records = protected + native['native_files']
def guard():
    return all((ROOT/f['path']).stat().st_size == f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest() == f['sha256'] for f in records)
assert guard()
report = {'scope': __doc__, 'mode': MODE, 'errors': [], 'frames': [], 'captures': [], 'checks': {},
          'native_saved': False, 'visual_acceptance': False, 'display_muzzle_gameplay_tested': False,
          'accepted_grasp_camera_cm': [22,22,-16]}
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
started = time.monotonic()
ready = ending = None
busy = False
step = -1
step_start = 0
capture_pending = None
framing = None
last_action = None
seen_world = False

def write():
    (OUT/'result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
def xyz(v):
    return [v.x,v.y,v.z]
def prop(n):
    return player.get_editor_property(n)
def state():
    return {n: str(prop(n)) for n in ('ActionState','LoadedAmmo','ReserveAmmo','ReloadCommitCount','ShotSequence','ShotOutcome','IsDead')}
def fingers(c):
    result = {}
    for side in ('l','r'):
        for f in ('thumb','index','middle','ring','pinky'):
            for i in (1,2,3):
                n = f'{f}_0{i}_{side}'
                parent = c.get_socket_transform(f'hand_{side}' if i == 1 else f'{f}_0{i-1}_{side}')
                t = c.get_socket_transform(n)
                result[n] = xyz(unreal.MathLibrary.inverse_transform_location(parent,t.translation))
                for axis in (unreal.Vector(1,0,0),unreal.Vector(0,1,0),unreal.Vector(0,0,1)):
                    result[n] += xyz(unreal.MathLibrary.inverse_transform_direction(parent,unreal.MathLibrary.transform_direction(t,axis)))
    return result
def pose_delta():
    a,b = fingers(source),fingers(vm)
    return max(abs(x-y) for n in a for x,y in zip(a[n],b[n]))
def grasp(c,side):
    fs = ('middle','ring','pinky') if side == 'r' else ('index','middle','ring','pinky')
    ns = [f'{f}_0{i}_{side}' for f in fs for i in (2,3)] + [f'thumb_02_{side}',f'thumb_03_{side}']
    return sum((c.get_socket_location(n) for n in ns),unreal.Vector())/len(ns)
def spawn(cls,t):
    api = unreal.get_default_object(unreal.GameplayStatics.static_class())
    a = api.call_method('BeginDeferredActorSpawnFromClass', args=(world,cls,t,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,player,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    return api.call_method('FinishSpawningActor',args=(a,t,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
def setup():
    global source,eye,gun,view,vm,display,origin,controller
    controller = unreal.GameplayStatics.get_player_controller(world,0)
    source = player.get_component_by_class(unreal.SkeletalMeshComponent)
    eye = player.get_component_by_class(unreal.CameraComponent)
    gun = prop('WeaponAppearance')
    assert source.get_anim_instance().get_class().get_name() == 'ABP_PC_Allied_Stride_v1_C'
    assert gun.get_class().get_name() == 'BP_PC_RifleAttachmentV3_C'
    origin = player.get_actor_location()
    source.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
    source.set_owner_no_see(True)
    gun.static_mesh_component.set_owner_no_see(True)
    view = spawn(unreal.SkeletalMeshActor.static_class(),source.get_world_transform())
    vm = view.skeletal_mesh_component
    vm.set_skeletal_mesh_asset(unreal.load_asset('/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3'))
    assert [vm.get_material(i).get_path_name() for i in range(vm.get_num_materials())] == native['after_materials']
    vm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    vm.set_only_owner_see(True)
    vm.set_cast_shadow(False)
    vm.set_leader_pose_component(source,True,False)
    vm.add_tick_prerequisite_component(source)
    display = spawn(unreal.StaticMeshActor.static_class(),gun.get_actor_transform())
    sm = display.static_mesh_component
    sm.set_mobility(unreal.ComponentMobility.MOVABLE)
    sm.set_static_mesh(gun.static_mesh_component.get_editor_property('static_mesh'))
    for i in range(gun.static_mesh_component.get_num_materials()):
        sm.set_material(i,gun.static_mesh_component.get_material(i))
    sm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    sm.set_only_owner_see(True)
    sm.set_cast_shadow(False)
    report['initial_state'] = state()

def update_display():
    global framing,last_action
    action = str(prop('ActionState'))
    visible = not bool(prop('IsDead'))
    vm.set_visibility(visible)
    display.static_mesh_component.set_visibility(visible)
    if not visible:
        last_action = action
        return
    # Refresh only the existing pure spatial attachment function after source evaluation.
    gun.call_method('PC_UpdateRifleAttachment')
    camera = eye.get_world_transform()
    if action == 'Ready' or framing is None:
        relative = unreal.MathLibrary.make_relative_transform(source.get_world_transform(),gun.get_actor_transform())
        desired = unreal.MathLibrary.transform_location(camera,unreal.Vector(22,22,-16))
        goal = eye.get_world_location()+eye.get_forward_vector()*20000
        t = unreal.Transform(location=desired)
        for _ in range(8):
            look = unreal.MathLibrary.find_look_at_rotation(t.translation,goal)
            t = unreal.Transform(location=unreal.Vector(),rotation=unreal.Rotator(pitch=0,yaw=look.yaw-90,roll=-look.pitch),scale=unreal.Vector(1,1,1))
            t.translation = desired-unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,-8,0))
        v = unreal.MathLibrary.compose_transforms(relative,t)
        framing = unreal.MathLibrary.make_relative_transform(v,camera)
    else:
        v = unreal.MathLibrary.compose_transforms(framing,camera)
        gun_local = unreal.MathLibrary.make_relative_transform(gun.get_actor_transform(),source.get_world_transform())
        t = unreal.MathLibrary.compose_transforms(gun_local,v)
    view.set_actor_transform(v,False,True)
    display.set_actor_transform(t,False,True)
    last_action = action

def measure(label):
    camera = eye.get_world_transform()
    t = display.get_actor_transform()
    d = {'phase': label, 'game_seconds': unreal.GameplayStatics.get_time_seconds(world),
         'state': state(), 'velocity_cm_s': xyz(player.get_velocity()), 'finger_local_delta': pose_delta(),
         'right_anchor_cm': (unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,-8,0))-grasp(vm,'r')).length(),
         'support_proxy_cm': (unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,22.2,0))-grasp(vm,'l')).length(),
         'camera_relative_cm': xyz(eye.get_editor_property('relative_location')), 'fov': eye.get_editor_property('field_of_view'),
         'original_weapon_binding': prop('WeaponAppearance') == gun, 'view_visible': vm.is_visible(),
         'bones_camera_cm': {n: xyz(unreal.MathLibrary.inverse_transform_location(camera,vm.get_socket_location(n))) for n in ('upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r')}}
    assert d['finger_local_delta'] < 1e-6, d
    assert (unreal.Vector(*d['camera_relative_cm'])-unreal.Vector(25,0,60)).length() < 1e-6 and abs(d['fov']-90) < 1e-6 and d['original_weapon_binding'],d
    if not bool(prop('IsDead')):
        assert d['right_anchor_cm'] < .05,d
    return d

def finish(error=None):
    global ending
    if ending is not None:
        return
    if error:
        report['errors'].append(error)
    if world:
        unreal.GameplayStatics.set_global_time_dilation(world,1)
    report['status'] = 'failed' if report['errors'] else 'motion_captured_requires_image_review'
    levels.editor_request_end_play()
    ending = time.monotonic()
    write()

def enter(i):
    global step,step_start
    step = i
    step_start = unreal.GameplayStatics.get_time_seconds(world)
    name,duration,move,rotation,invoke = phases[i]
    if i == 0 or phases[i][2] != phases[i-1][2] or phases[i][2] is None:
        player.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
    if rotation is not None:
        controller.set_control_rotation(unreal.Rotator(pitch=rotation[0],yaw=rotation[1],roll=0))
    if invoke:
        before = state()
        player.call_method(invoke,args=(1000.0,) if invoke == 'PC_ApplyDamage' else ())
        report.setdefault('events',[]).append({'phase':name,'function':invoke,'before':before,'after':state()})

phases = [('idle',1.5,None,(0,0),None),('forward_start',.2,(1,0,0),None,None),
          ('forward',1.0,(1,0,0),None,None),('stopped',.5,None,None,None),
          ('reload_early',.35,None,None,'PC_RequestReload')]
if MODE in ('full','tail'):
    if MODE == 'full':
        phases[3:3] = [(f'walk_cycle_{i:02d}',.1,(1,0,0),None,None) for i in range(12)]
    phases += [('reload_middle',.6,None,None,None),('reload_late',.8,None,None,None),('reload_finished',2.8,None,None,None),
               ('backward',.9,(-1,0,0),None,None),('left',.9,(0,-1,0),None,None),('right',.9,(0,1,0),None,None),
               ('pitch_up30',.5,None,(30,0),None),('pitch_down30',.5,None,(-30,0),None),
               ('pitch_up60',.5,None,(60,0),None),('pitch_down60',.5,None,(-60,0),None),
               ('yaw45',.5,None,(0,45),None),('fire',.5,None,(0,0),'PC_PlayerFire'),
               ('moving_reload_early',.35,(1,0,0),None,'PC_RequestReload'),
               ('moving_reload_middle',.6,(1,0,0),None,None),('moving_reload_late',.8,(1,0,0),None,None),
               ('moving_reload_finished',2.8,None,None,None),('dead',.5,None,None,'PC_ApplyDamage'),
               ('reset',1,None,None,'PC_ResetLifecycle')]
if MODE == 'tail':
    # Real reload establishes the same 8/10 state as the inspected partial run, no direct ammo fixture.
    remaining = {'yaw45','fire','moving_reload_early','moving_reload_middle','moving_reload_late','moving_reload_finished','dead','reset'}
    phases = [('tail_preload',4,None,(0,0),'PC_RequestReload')]+[p for p in phases if p[0] in remaining]

def tick(dt):
    global busy,world,player,ready,capture_pending,seen_world
    if busy:
        return
    busy = True
    try:
        if ending is not None:
            if not levels.is_in_play_in_editor() and time.monotonic()-ending > 3:
                report['protected_42_unchanged'] = guard()
                write()
                unreal.unregister_slate_post_tick_callback(callback)
                unreal.SystemLibrary.quit_editor()
            return
        if time.monotonic()-started > 300:
            finish('Bounded dynamic timeout')
            return
        world = editor.get_game_world()
        if world:
            seen_world = True
        if seen_world and not levels.is_in_play_in_editor():
            finish('PIE ended unexpectedly before diagnostic completion')
            return
        player = unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:
            return
        if ready is None:
            unreal.GameplayStatics.get_player_controller(world,0).set_control_rotation(unreal.Rotator())
            ready = time.monotonic()
            return
        if step < 0:
            if time.monotonic()-ready < 20:
                return
            setup()
            update_display()
            enter(0)
        if capture_pending:
            p = capture_pending
            p['settle_frames'] += 1
            if p['issued'] is None:
                if time.monotonic()-p['paused_at'] >= .8 and p['settle_frames'] >= 12:
                    assert abs(unreal.GameplayStatics.get_time_seconds(world)-p['game_seconds']) < .01
                    assert str(prop('ActionState')) == p['action']
                    actual = fingers(source)
                    assert max(abs(x-y) for n in actual for x,y in zip(actual[n],p['source_fingers'][n])) < 1e-6
                    report['captures'][-1]['settled_render_frames'] = p['settle_frames']
                    unreal.SystemLibrary.execute_console_command(world,'Shot -nosuffix filename="'+p['path'].as_posix()+'"',controller)
                    p['issued'] = time.monotonic()
                    write()
                return
            if p['path'].exists() and p['path'].stat().st_size > 1000 and time.monotonic()-p['issued'] > .3:
                source.set_editor_property('pause_anims',False,unreal.PropertyAccessChangeNotifyMode.NEVER)
                source.set_component_tick_enabled(True)
                player.set_editor_property('custom_time_dilation',1.0)
                unreal.GameplayStatics.set_global_time_dilation(world,1)
                capture_pending = None
                if step+1 == len(phases):
                    if MODE in ('full','tail'):
                        report['checks']['original_anim_after_reset'] = source.get_anim_instance().get_class().get_name() == 'ABP_PC_Allied_Stride_v1_C'
                        report['checks']['alive_after_reset'] = not bool(prop('IsDead')) and str(prop('ActionState')) == 'Ready'
                        report['checks']['ammo_conserved'] = int(prop('LoadedAmmo'))+int(prop('ReserveAmmo'))+int(prop('ShotSequence')) == 18
                        report['checks']['two_actual_reload_commits'] = int(prop('ReloadCommitCount')) == 2
                        for name in (('forward','backward','left','right','moving_reload_middle') if MODE == 'full' else ('moving_reload_middle',)):
                            report['checks'][name+'_movement_exercised'] = any(f['phase'] == name and unreal.Vector(*f['velocity_cm_s']).length() > 100 for f in report['frames'])
                        report['checks']['dead_display_hidden'] = all(not f['view_visible'] for f in report['frames'] if f['phase'] == 'dead')
                    finish()
                else:
                    enter(step+1)
            return
        name,duration,move,rotation,invoke = phases[step]
        if move:
            player.add_movement_input(unreal.Vector(*move),1,True)
        update_display()
        d = measure(name)
        report['frames'].append(d)
        now = unreal.GameplayStatics.get_time_seconds(world)
        if now-step_start >= duration:
            path = OUT/(name+'.png')
            unreal.GameplayStatics.set_global_time_dilation(world,.0001)
            player.set_editor_property('custom_time_dilation',0.0)
            source.set_editor_property('pause_anims',True,unreal.PropertyAccessChangeNotifyMode.NEVER)
            source.set_component_tick_enabled(False)
            report['captures'].append(dict(d,file=path.name,source_frozen_world_dilation=.0001))
            capture_pending = {'name':name,'path':path,'paused_at':time.monotonic(),'issued':None,'settle_frames':0,
                               'game_seconds':now,'source_fingers':fingers(source),'action':str(prop('ActionState'))}
            write()
    except Exception:
        finish(traceback.format_exc())
    finally:
        busy = False

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback = unreal.register_slate_post_tick_callback(tick)
write()
levels.editor_request_begin_play()
