"""One user-directed left/down seating plus actual left-palm stock-web rotation."""
import math
import os
import sys
import time
import traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import *
import transform_math as tm
import marked_web_math as fitting

IDENTITY=os.environ['CS549_ALLIED_MARKED_WEB_V6_ID']
assert IDENTITY.replace('_','').isalnum()
OUT=BASE/IDENTITY
assert not OUT.exists()
OUT.mkdir(parents=True)
FIT=BASE/'stock_pivot_v1/result.json'
PREVIOUS=BASE/'fit_v5/result.json'
MEASURE=BASE/'marked_web_surface_v6c/result.json'
fit,previous,measure=read(FIT),read(PREVIOUS),read(MEASURE)
assert fit['status']=='stopped_contact_gate' and fit['inputs_unchanged']
assert fit['reference_alignment']['max_cm']<.01
assert not previous['errors'] and previous['guards_after']==611
assert previous['cumulative_raise_above_v2_cm']==1.3
assert not measure['errors'] and measure['guards_after']==611 and measure['inputs_unchanged']
assert all(sha(ROOT/p)==h for p,h in measure['input_hashes'].items())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
r={'scope':__doc__,'errors':[],'pid':os.getpid(),'status':'starting',
   'guards_before':guards(),'captures':[],'map_saved':False,'formal_selected':False,
   'hand_pose_changed':False,'support_arm_changed':False,'contact_or_gameplay_accepted':False,
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in (FIT,PREVIOUS,MEASURE,Path(__file__),Path(fitting.__file__))}}
write(OUT/'source.json',{'identity':IDENTITY,'input_hashes':r['input_hashes']})
start=time.monotonic()
ready=ending=callback=world=soldier=gun=capture=target=None
index=0
requested=None
busy=False
stage='before'
views=[('before_right','right',78),('before_trigger','right',30),
       ('seated_right','right',78),('after_right','right',78),
       ('after_front','front',78),('after_top','top',78),
       ('after_context','right',155),('after_trigger','right',30),
       ('after_support','front',40),('after_support_right','right',40)]

def xyz(v):return [v.x,v.y,v.z]
def encoded(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
def save():write(OUT/'result.json',r)
def bones():
    m=soldier.mesh
    return {str(m.get_bone_name(i)):encoded(m.get_socket_transform(m.get_bone_name(i),unreal.RelativeTransformSpace.RTS_WORLD)) for i in range(m.get_num_bones())}
def current():return encoded(gun.get_component_by_class(unreal.StaticMeshComponent).get_world_transform())
def assert_pose_and_transform(expected):
    assert bones()==r['before']['bones'],'Character pose changed'
    c=current()
    assert math.dist(c['t'],expected['t'])<.01
    assert tm.angle(c['q'],expected['q'])<.01
    assert c['s']==expected['s']
    return c
def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    try:r['guards_after']=guards()
    except Exception:r['errors'].append(traceback.format_exc())
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
    r['status']='failed_preserved' if r['errors'] else 'marked_web_v6_native_views_require_user_review'
    save()
    if world:
        unreal.GameplayStatics.set_game_paused(world,False)
        levels.editor_request_end_play()
    ending=time.monotonic()

def tick(delta):
    global ready,ending,callback,world,soldier,gun,capture,target,index,requested,busy,stage
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>3:
                unreal.unregister_slate_post_tick_callback(callback)
                unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<240,'Capture deadline'
        world=editor.get_game_world()
        player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        if ready is None:
            soldier=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character) if a.get_actor_label()=='PC_City_Ally1')
            gun=soldier.get_editor_property('WeaponAppearance')
            assert gun and gun.get_editor_property('GripMesh')==soldier.mesh
            assert gun.get_editor_property('Combatant')==soldier
            assert 'RifleAttachmentV3' in gun.get_class().get_name()
            assert 'SK_WWII_US_Paratrooper_simple_UE582_v1' in soldier.mesh.get_skeletal_mesh_asset().get_path_name()
            capture=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SceneCapture2D) if a.get_actor_label()=='PC_AlliedMarkedWebV6Capture').get_component_by_class(unreal.SceneCaptureComponent2D)
            target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
            capture.set_editor_property('texture_target',target)
            capture.set_editor_property('primitive_render_mode',unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
            capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
            capture.set_editor_property('capture_every_frame',False)
            capture.set_editor_property('capture_on_movement',False)
            capture.set_editor_property('show_flag_settings',[unreal.EngineShowFlagsSetting(show_flag_name=n,enabled=False) for n in ('Fog','Atmosphere','Bloom','DepthOfField','MotionBlur')])
            ready=time.monotonic()
            return
        if time.monotonic()-ready<15:return
        if 'before' not in r:
            assert str(soldier.get_editor_property('ActionState'))=='Ready'
            assert soldier.get_velocity().length()<.1
            assert unreal.GameplayStatics.set_game_paused(world,True)
            component=gun.get_component_by_class(unreal.StaticMeshComponent)
            assert 'SM_M1_Garand' in component.get_editor_property('static_mesh').get_path_name()
            collision=str(component.get_collision_enabled())
            assert collision==fit['pose_source']['collision']
            r['unchanged_collision_mode']=collision
            r['original']={'bones':bones(),'gun_world':current(),'mesh_world':encoded(soldier.mesh.get_world_transform()),
                'gun_class':gun.get_class().get_path_name(),'mesh':soldier.mesh.get_skeletal_mesh_asset().get_path_name(),
                'materials':[soldier.mesh.get_material(i).get_path_name() for i in range(soldier.mesh.get_num_materials())],
                'gun_materials':[component.get_material(i).get_path_name() for i in range(component.get_num_materials())]}
            errors=tm.index_errors(fit['pose_source']['bone_world'],r['original']['bones'])
            r['unchanged_index_local_rotation_error_deg']=errors
            assert max(errors.values())<.05
            r['landmarks']=tm.landmarks(fit,r['original'])
            gun.set_actor_location(gun.get_actor_location()+unreal.Vector(*r['landmarks']['delta_world_cm']),False,False)
            residual=math.dist(tm.point(current(),r['landmarks']['blade_gun_cm']),r['landmarks']['pad_world_cm'])
            assert residual<.01
            r['recreated_v2_anchor_residual_cm']=residual
            forward=xyz(soldier.get_actor_forward_vector())
            right=xyz(soldier.get_actor_right_vector())
            assert abs(forward[2])<1e-6 and abs(right[2])<1e-6
            gun.set_actor_location(gun.get_actor_location()+unreal.Vector(*[-.2*forward[0],-.2*forward[1],1.3]),False,False)
            baseline=current()
            assert baseline['q']==r['original']['gun_world']['q'] and baseline['s']==r['original']['gun_world']['s']
            assert bones()==r['original']['bones']
            r['before']={**r['original'],'gun_world':baseline}
            r['fit']=fitting.derive(measure,r['before'],forward,right)
            # Verified Engine header ScriptMethod=Rotator and prior native usage.
            rotation=unreal.Quat(*r['fit']['final_gun_world']['q']).rotator()
            assert tm.angle(encoded(unreal.Transform(rotation=rotation))['q'],r['fit']['final_gun_world']['q'])<.01
            r['rotation_api_roundtrip_verified']=True
            save()
        if index>=len(views):finish();return
        name,axis,width=views[index]
        if index==2 and not (OUT/'early_acceptance.json').is_file():return
        if name.startswith('seated') and stage=='before':
            expected=r['fit']['seated_gun_world']
            gun.set_actor_location(unreal.Vector(*expected['t']),False,False)
            stage='seated'
            r['seated']={'gun_world':assert_pose_and_transform(expected),'bones':bones()}
            save()
        if name.startswith('after') and stage=='seated':
            expected=r['fit']['final_gun_world']
            gun.set_actor_rotation(unreal.Quat(*expected['q']).rotator(),False)
            gun.set_actor_location(unreal.Vector(*expected['t']),False,False)
            stage='after'
            r['after']={'gun_world':assert_pose_and_transform(expected),'bones':bones()}
            pivot=tm.point(r['after']['gun_world'],measure['landmarks']['stock_neck_region']['gun_local_cm'])
            r['actual_pivot_drift_cm']=math.dist(pivot,r['fit']['pivot_world_cm'])
            assert r['actual_pivot_drift_cm']<.01
            pad=r['landmarks']['pad_world_cm']
            blade=r['landmarks']['blade_gun_cm']
            r['index_anchor_gap_before_cm']=math.dist(pad,tm.point(r['before']['gun_world'],blade))
            r['index_anchor_gap_after_cm']=math.dist(pad,tm.point(r['after']['gun_world'],blade))
            save()
        if requested is None:
            rh,lh=soldier.mesh.get_socket_location('hand_r'),soldier.mesh.get_socket_location('hand_l')
            center=(rh+lh)/2
            if name=='after_context':center=(center+soldier.mesh.get_socket_location('spine_03'))/2
            if name.endswith('_trigger'):center=unreal.Vector(*r['landmarks']['pad_world_cm'])
            if name.startswith('after_support'):center=unreal.Vector(*r['fit']['left_palm_world_cm'])
            direction={'front':soldier.get_actor_forward_vector(),'right':soldier.get_actor_right_vector(),'top':unreal.Vector(0,0,1)}[axis]
            eye=center+direction*250
            rotation=unreal.MathLibrary.find_look_at_rotation(eye,center)
            if axis=='top':rotation=unreal.Rotator(pitch=-90,yaw=soldier.get_actor_rotation().yaw,roll=0)
            capture.set_world_location(eye,False,False)
            capture.set_world_rotation(rotation,False,False)
            capture.set_editor_property('ortho_width',width)
            capture.clear_show_only_components()
            capture.set_editor_property('show_only_actors',[soldier,gun])
            capture.capture_scene()
            requested=time.monotonic()
            r['captures'].append({'file':name+'.png','stage':stage,'view':axis,'width_cm':width,'eye_cm':xyz(eye),'target_cm':xyz(center)})
            save()
            return
        if time.monotonic()-requested<1.5:return
        unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),name+'.png')
        assert (OUT/(name+'.png')).stat().st_size>15000
        expected=r[stage]['gun_world']
        c=assert_pose_and_transform(expected)
        r['captures'][-1]['gun_drift_cm']=math.dist(c['t'],expected['t'])
        save()
        index+=1
        requested=None
    except Exception:finish(traceback.format_exc())
    finally:busy=False

try:
    cap=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(),unreal.Rotator())
    cap.set_actor_label('PC_AlliedMarkedWebV6Capture')
    for pitch,yaw in ((-25,45),(-25,-135),(-20,135),(-20,-45)):
        light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,300),unreal.Rotator(pitch=pitch,yaw=yaw))
        light.set_actor_label('PC_AlliedMarkedWebV6Fill')
        component=light.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_intensity(6)
        component.set_cast_shadows(False)
    save()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick)
    levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status']='failed_startup'
    save()
    unreal.SystemLibrary.quit_editor()
