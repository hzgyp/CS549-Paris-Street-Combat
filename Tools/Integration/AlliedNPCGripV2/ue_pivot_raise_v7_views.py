"""Unsaved whole-source frozen V6/V7 comparison; no FP binding or live NPC changes."""
import os
import sys
import math
import time
import traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import *
import transform_math as tm

IDENTITY=os.environ['CS549_ALLIED_PIVOT_RAISE_V7_ID']
assert IDENTITY.replace('_','').isalnum()
OUT=BASE/IDENTITY
assert not OUT.exists()
OUT.mkdir(parents=True)
TRIAL=BASE/'pivot_raise_trial_v7/result.json'
V6=BASE/'marked_web_v6/result.json'
trial,previous=read(TRIAL),read(V6)
assert not trial['errors'] and trial['inputs_unchanged'] and trial['guards_after']==611
assert trial['preservation']['new_severe_edges']==0
assert trial['preservation']['right_skin_cm']<.001
assert all(sha(ROOT/p)==h for p,h in trial['input_hashes'].items())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
r={'scope':__doc__,'identity':IDENTITY,'pid':os.getpid(),'errors':[], 'status':'starting',
   'guards_before':guards(),'captures':[],'map_saved':False,'formal_selected':False,
   'frozen_diagnostic_only':True,'fp_binding_called':False,'original_npc_driver_changed':False,
   'contact_or_gameplay_accepted':False,
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in (TRIAL,V6,Path(__file__))}}
write(OUT/'source.json',r)
world=soldier=gun=pose=container=capture=target=ready=ending=callback=requested=None
start=time.monotonic();index=0;stage='before';busy=False
views=[('before_right','right',78),('before_trigger','right',30),
       ('after_right','right',78),('after_front','front',78),('after_top','top',78),
       ('after_trigger','right',30),('after_support','front',40),
       ('after_support_right','right',40),('after_reverse','reverse',78),
       ('after_context','right',155),('before_context','right',155)]

def xyz(v):return [v.x,v.y,v.z]
def encoded(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
def native(t):
    value=unreal.Transform(location=unreal.Vector(*t['t']),rotation=unreal.Quat(*t['q']).rotator(),scale=unreal.Vector(*t['s']))
    assert math.dist(encoded(value)['t'],t['t'])<.001 and tm.angle(encoded(value)['q'],t['q'])<.01
    return value
def original_bones():
    m=soldier.mesh
    return {str(m.get_bone_name(i)):encoded(m.get_socket_transform(m.get_bone_name(i),unreal.RelativeTransformSpace.RTS_WORLD)) for i in range(m.get_num_bones())}
def pose_bones():
    return {n:encoded(pose.get_bone_transform_by_name(n,unreal.BoneSpaces.WORLD_SPACE)) for n in trial['bone_names']}
def current_gun():return encoded(gun.get_component_by_class(unreal.StaticMeshComponent).get_world_transform())
def save():write(OUT/'result.json',r)
def parity(expected):
    actual=pose_bones()
    point=max(math.dist(actual[n]['t'],expected[n]['t']) for n in expected)
    angle=max(tm.angle(actual[n]['q'],expected[n]['q']) for n in expected)
    scale=max(max(abs(a-b) for a,b in zip(actual[n]['s'],expected[n]['s'])) for n in expected)
    assert point<.01 and angle<.01 and scale<.001,(point,angle,scale)
    assert original_bones()==r['original']['bones'],'Original NPC pose changed while paused'
    return {'max_bone_position_cm':point,'max_bone_rotation_deg':angle,'max_bone_scale_error':scale}
def apply(stage_name):
    expected=trial[stage_name+'_bones']
    # Engine implementation derives parent component transform from current local
    # hierarchy. Apply verified parent-first names, never query native skinned vertices.
    done=set()
    for n in trial['bone_names']:
        p=trial['parents'].get(n)
        assert p not in expected or p in done,'Pose order must be parent-first'
        pose.set_bone_transform_by_name(n,native(expected[n]),unreal.BoneSpaces.WORLD_SPACE)
        done.add(n)
    goal=trial[stage_name+'_gun_world']
    gun.set_actor_transform(native(goal),False,False)
    r[stage_name]={'pose_parity':parity(expected),'bones':pose_bones(),'gun_world':current_gun()}
    assert math.dist(current_gun()['t'],goal['t'])<.01
    assert tm.angle(current_gun()['q'],goal['q'])<.01
    save()
def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    try:r['guards_after']=guards()
    except Exception:r['errors'].append(traceback.format_exc())
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
    r['status']='failed_preserved' if r['errors'] else 'pivot_raise_v7_native_views_require_user_review'
    save()
    if world:
        unreal.GameplayStatics.set_game_paused(world,False)
        levels.editor_request_end_play()
    ending=time.monotonic()
def camera_for(name,axis,width):
    base=next(c for c in previous['captures'] if c['file']=='after_right.png')
    center=unreal.Vector(*base['target_cm'])
    if name.endswith('_trigger'):center=unreal.Vector(*trial['pad_world_cm'])
    if 'support' in name:
        center=unreal.Vector(*trial['after_bones']['hand_l']['t'])
    if 'context' in name:
        center=(center+unreal.Vector(*trial['before_bones']['spine_03']['t']))/2
    direction={'front':unreal.Vector(1,0,0),'right':unreal.Vector(0,1,0),
               'reverse':unreal.Vector(0,-1,0),'top':unreal.Vector(0,0,1)}[axis]
    eye=center+direction*250
    rot=unreal.MathLibrary.find_look_at_rotation(eye,center)
    if axis=='top':rot=unreal.Rotator(pitch=-90,yaw=0,roll=0)
    capture.set_world_location(eye,False,False);capture.set_world_rotation(rot,False,False)
    capture.set_editor_property('ortho_width',width)
    capture.clear_show_only_components();capture.set_editor_property('show_only_actors',[container,gun])
    capture.capture_scene()
    return {'file':name+'.png','stage':stage,'view':axis,'width_cm':width,'eye_cm':xyz(eye),'target_cm':xyz(center)}
def tick(delta):
    global ready,ending,callback,world,soldier,gun,pose,container,capture,target,index,requested,busy,stage
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>3:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<300,'Frozen comparison deadline'
        world=editor.get_game_world()
        player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        if ready is None:
            soldier=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character) if a.get_actor_label()=='PC_City_Ally1')
            gun=soldier.get_editor_property('WeaponAppearance')
            assert gun and gun.get_editor_property('GripMesh')==soldier.mesh and gun.get_editor_property('Combatant')==soldier
            assert 'RifleAttachmentV3' in gun.get_class().get_name()
            assert 'SK_WWII_US_Paratrooper_simple_UE582_v1' in soldier.mesh.get_skeletal_mesh_asset().get_path_name()
            container=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisGripV18Actor) if a.get_actor_label()=='PC_AlliedPivotRaiseV7Frozen')
            container.set_actor_tick_enabled(False)
            pose=container.get_editor_property('Pose')
            pose.set_skinned_asset_and_update(soldier.mesh.get_skeletal_mesh_asset(),True)
            pose.set_only_owner_see(False)
            pose.set_world_transform(native(trial['mesh_world']),False,False)
            for i in range(soldier.mesh.get_num_materials()):pose.set_material(i,soldier.mesh.get_material(i))
            assert pose.get_num_bones()==len(trial['bone_names'])
            capture=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SceneCapture2D) if a.get_actor_label()=='PC_AlliedPivotRaiseV7Capture').get_component_by_class(unreal.SceneCaptureComponent2D)
            target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
            capture.set_editor_property('texture_target',target)
            capture.set_editor_property('primitive_render_mode',unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
            capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
            capture.set_editor_property('capture_every_frame',False);capture.set_editor_property('capture_on_movement',False)
            capture.set_editor_property('show_flag_settings',[unreal.EngineShowFlagsSetting(show_flag_name=n,enabled=False) for n in ('Fog','Atmosphere','Bloom','DepthOfField','MotionBlur')])
            ready=time.monotonic();return
        if time.monotonic()-ready<15:return
        if 'original' not in r:
            assert str(soldier.get_editor_property('ActionState'))=='Ready' and soldier.get_velocity().length()<.1
            assert unreal.GameplayStatics.set_game_paused(world,True)
            c=gun.get_component_by_class(unreal.StaticMeshComponent)
            assert 'SM_M1_Garand' in c.get_editor_property('static_mesh').get_path_name()
            r['original']={'bones':original_bones(),'gun_world':current_gun(),
                'mesh':soldier.mesh.get_skeletal_mesh_asset().get_path_name(),
                'materials':[pose.get_material(i).get_path_name() for i in range(pose.get_num_materials())],
                'gun_materials':[c.get_material(i).get_path_name() for i in range(c.get_num_materials())]}
            apply('before')
        if index>=len(views):finish();return
        if index==2 and not (OUT/'early_acceptance.json').is_file():return
        name,axis,width=views[index]
        expected_stage='before' if name.startswith('before') else 'after'
        if expected_stage!=stage:apply(expected_stage);stage=expected_stage
        if requested is None:
            r['captures'].append(camera_for(name,axis,width));save();requested=time.monotonic();return
        if time.monotonic()-requested<1.5:return
        unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),name+'.png')
        assert (OUT/(name+'.png')).stat().st_size>15000
        r['captures'][-1]['pose_parity']=parity(trial[stage+'_bones'])
        expected=trial[stage+'_gun_world'];actual=current_gun()
        r['captures'][-1]['gun_drift_cm']=math.dist(actual['t'],expected['t'])
        assert r['captures'][-1]['gun_drift_cm']<.01
        save();index+=1;requested=None
    except Exception:finish(traceback.format_exc())
    finally:busy=False

try:
    container=actors.spawn_actor_from_class(unreal.ParisGripV18Actor,unreal.Vector(),unreal.Rotator())
    container.set_actor_label('PC_AlliedPivotRaiseV7Frozen');container.set_actor_tick_enabled(False)
    cap=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(),unreal.Rotator())
    cap.set_actor_label('PC_AlliedPivotRaiseV7Capture')
    for pitch,yaw in ((-25,45),(-25,-135),(-20,135),(-20,-45)):
        light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,300),unreal.Rotator(pitch=pitch,yaw=yaw))
        light.set_actor_label('PC_AlliedPivotRaiseV7Fill')
        c=light.get_component_by_class(unreal.DirectionalLightComponent);c.set_intensity(6);c.set_cast_shadows(False)
    save();unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_startup';save();unreal.SystemLibrary.quit_editor()
