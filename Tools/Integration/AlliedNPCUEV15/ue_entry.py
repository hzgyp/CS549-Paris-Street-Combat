"""Native Allied candidate author/observer: no Python pose updates, no map save."""
import os,sys,time,math,traceback,json
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import *
import transform_math as tm
V16=os.environ.get('CS549_ALLIED_UE_VARIANT')=='v16'
MODE=os.environ.get('CS549_ALLIED_UE_MODE','early')
assert MODE in ('early','motion','reload')
assert MODE!='motion','Stopped full-city proof; see AN008. A new lifecycle/timing mechanism needs its own entry.'
if V16:
    CONFIG=BASE/'preflight_v16/binding.json'
    PACKAGE='/Game/ParisCombat/Animation/AlliedGripV15/ABP_PC_AlliedGripPostV16'
IDENTITY=os.environ['CS549_ALLIED_UE_V15_ID']
assert IDENTITY.replace('_','').isalnum()
OUT=BASE/IDENTITY;assert not OUT.exists();OUT.mkdir(parents=True)
cfg=read(CONFIG);r={'status':'starting','pid':os.getpid(),'errors':[],
    'guards_before':guards(False),'native_pose_driver':True,'python_pose_updates':0,
    'map_saved':False,'selected':False,'samples':[],'captures':[],'bone_samples':[]}
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
callback=None;busy=False;ending=None;start=time.monotonic();phase='settle';stamp=None
world=soldier=gun=wrapper=capture=target=data=None
capture_index=0;capture_stamp=None
wall=None;reload_start=None;reload_ready=None;mid_target=None;walk_target=None
views=['right','front','top','reverse','context']

def enc(t):return {'t':[t.translation.x,t.translation.y,t.translation.z],
    'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],
    's':[t.scale3d.x,t.scale3d.y,t.scale3d.z]}
def bones():return {str(soldier.mesh.get_bone_name(i)):enc(soldier.mesh.get_socket_transform(soldier.mesh.get_bone_name(i),unreal.RelativeTransformSpace.RTS_WORLD)) for i in range(soldier.mesh.get_num_bones())}
def sample(name):
    pp=soldier.mesh.get_post_process_instance()
    g=gun.get_component_by_class(unreal.StaticMeshComponent)
    relation=enc(unreal.MathLibrary.make_relative_transform(g.get_world_transform(),soldier.mesh.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD)))
    return {'name':name,'time':unreal.GameplayStatics.get_time_seconds(world),'action':str(soldier.get_editor_property('ActionState')),
        'initialized':bool(wrapper.get_editor_property('Initialized')),'error':str(wrapper.get_editor_property('BindingError')),
        'native_updates':int(wrapper.get_editor_property('NativeUpdates')),
        'pending_evaluation_frames':int(wrapper.get_editor_property('PendingEvaluationFrames')),
        'postprocess':pp.get_class().get_path_name() if pp else None,
        'evaluations':int(pp.get_editor_property('Evaluations')) if pp else 0,
        'protection_error':float(pp.get_editor_property('ProtectionError')) if pp else None,
        'valid_input':bool(pp.get_editor_property('ValidInput')) if pp else False,
        'holding_alpha':float(pp.get_editor_property('HoldingWeight')) if pp else None,
        'protected_quat_component_error':float(pp.get_editor_property('ProtectedQuatComponentError')) if pp else None,
        'source_quat_norm_error':float(pp.get_editor_property('SourceQuatNormError')) if pp else None,
        'raw_protected_angle':float(pp.get_editor_property('RawProtectedAngle')) if pp else None,
        'gun_error_cm':math.dist(relation['t'],cfg['gun_hand_relative']['t']),
        'gun_error_deg':tm.angle(relation['q'],cfg['gun_hand_relative']['q']),
        'gun_hand':relation,'weapon_preserved':soldier.get_editor_property('WeaponAppearance')==gun,
        'source_preserved':gun.get_editor_property('GripMesh')==soldier.mesh,
        'ammo':[int(soldier.get_editor_property('LoadedAmmo')),int(soldier.get_editor_property('ReserveAmmo'))],
        'health':float(soldier.get_editor_property('Health')),'speed':soldier.get_velocity().length(),
        'shot':int(soldier.get_editor_property('ShotSequence')),'outcome':str(soldier.get_editor_property('ShotOutcome')),
        'source_animation':soldier.mesh.get_anim_instance().get_class().get_path_name() if soldier.mesh.get_anim_instance() else None,
        'animation_mode':str(soldier.mesh.get_editor_property('animation_mode'))}
def check(s):
    assert s['initialized'] and not s['error'] and s['evaluations']>0 and s['valid_input'],s
    assert s['protection_error']<.0001 and s['gun_error_cm']<.01 and s['gun_error_deg']<.01,s
    assert s['weapon_preserved'] and s['source_preserved'],s
def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    if wrapper and MODE in ('motion','reload'):
        try:r['native_observation_buffer']=json.loads(wrapper.observation_json())
        except Exception:r['errors'].append(traceback.format_exc())
    if MODE in ('motion','reload') and world:
        # Timed observation is over, including on failure. Retain actual views.
        for name,rt in [('walk_right',walk_target),('reload_mid_right',mid_target)]:
            if rt:
                try:unreal.RenderingLibrary.export_render_target(world,rt,OUT.as_posix(),name+'.png')
                except Exception:r['errors'].append(traceback.format_exc())
    try:r['guards_after']=guards(False)
    except Exception:r['errors'].append(traceback.format_exc())
    r['status']='stopped_preserved' if r['errors'] else ('native_lifecycle_reload_diagnostic_not_full_motion_acceptance' if MODE=='reload' else ('native_motion_candidate_requires_visual_gate' if MODE=='motion' else 'native_ready_candidate_requires_visual_gate'))
    write(OUT/'result.json',r)
    if editor.get_game_world():levels.editor_request_end_play()
    ending=time.monotonic()
def aim_camera(view):
    hand=soldier.mesh.get_socket_location('hand_r');left=soldier.mesh.get_socket_location('hand_l')
    center=(hand+left)/2
    if view=='context':center=(center+soldier.mesh.get_socket_location('spine_01'))/2
    # Source surveyed Ally1 faces +X; capture axes match the accepted diagnostic.
    direction={'right':unreal.Vector(0,1,0),'front':unreal.Vector(1,0,0),
        'top':unreal.Vector(0,0,1),'reverse':unreal.Vector(0,-1,0),'context':unreal.Vector(0,1,0)}[view]
    eye=center+direction*300
    rot=unreal.MathLibrary.find_look_at_rotation(eye,center)
    if view=='top':rot=unreal.Rotator(pitch=-90,yaw=0,roll=0)
    capture.set_world_location(eye,False,False);capture.set_world_rotation(rot,False,False)
    capture.set_editor_property('ortho_width',260 if view=='context' else 180)
    capture.clear_show_only_components();capture.set_editor_property('show_only_actors',[soldier,gun])
    capture.capture_scene()
def tick(delta):
    global callback,busy,world,soldier,gun,wrapper,capture,target,stamp,phase,capture_index,capture_stamp,wall,reload_start,reload_ready,mid_target,walk_target
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>3:
                unreal.unregister_slate_post_tick_callback(callback);callback=None;unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<180,'Native candidate deadline'
        world=editor.get_game_world()
        if not world or not unreal.GameplayStatics.get_player_pawn(world,0):return
        if stamp is None:stamp=time.monotonic();return
        if phase=='settle' and time.monotonic()-stamp>12:
            soldier=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character) if a.get_actor_label()=='PC_City_Ally1')
            gun=soldier.get_editor_property('WeaponAppearance')
            assert gun and gun.get_editor_property('GripMesh')==soldier.mesh
            r['original_bones']=bones();r['original_action']=str(soldier.get_editor_property('ActionState'))
            assert r['original_action']=='Ready'
            # ONE runtime author stimulus; pose and attachment thereafter are native.
            wrapper=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor) if a.get_actor_label()=='PC_AlliedUEV15Candidate')
            wrapper.set_editor_property('Target',soldier)
            capture=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SceneCapture2D) if a.get_actor_label()=='PC_AlliedUEV15Capture').get_component_by_class(unreal.SceneCaptureComponent2D)
            target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
            capture.set_editor_property('texture_target',target)
            capture.set_editor_property('primitive_render_mode',unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
            capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
            capture.set_editor_property('capture_every_frame',False);capture.set_editor_property('capture_on_movement',False)
            capture.set_editor_property('show_flag_settings',[unreal.EngineShowFlagsSetting(show_flag_name=n,enabled=False) for n in ('Fog','Atmosphere','Bloom','DepthOfField','MotionBlur')])
            phase='bind';stamp=time.monotonic()
        elif phase=='bind' and time.monotonic()-stamp>3:
            s=sample('ready');r['samples'].append(s);check(s)
            r['accepted_native_bones']=bones()
            parents=read(GRIP/'pivot_raise_measure_v7/result.json')['parents']
            local_errors={item['bone']:tm.angle(tm.local_q(r['accepted_native_bones'][parents[item['bone']]],r['accepted_native_bones'][item['bone']]),item['accepted_q']) for item in cfg['rules']}
            r['ready_local_reference_errors_deg']=local_errors
            assert max(local_errors.values())<(.01 if V16 else 3),'Actual Ready differs from accepted phase; stop before motion'
            phase='capture';stamp=time.monotonic()
        elif phase=='capture':
            if capture_index>=len(views):
                if MODE=='early':finish();return
                if MODE=='reload':phase='reload_request';stamp=time.monotonic();return
                phase='walk';stamp=time.monotonic();return
            view=views[capture_index]
            if capture_stamp is None:
                aim_camera(view);capture_stamp=time.monotonic();return
            if time.monotonic()-capture_stamp<1.5:return
            unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),'ready_'+view+'.png')
            assert (OUT/('ready_'+view+'.png')).stat().st_size>15000
            s=sample('ready_'+view);r['samples'].append(s);check(s)
            r['captures'].append({'file':'ready_'+view+'.png','actual_original_component':True})
            capture_index+=1;capture_stamp=None
        elif phase=='walk':
            soldier.add_movement_input(soldier.get_actor_forward_vector(),1,True)
            if time.monotonic()-stamp>2.5:
                s=sample('walk');r['samples'].append(s);check(s);assert s['speed']>10,s
                r['walk_bones']=bones();aim_camera('right')
                walk_target=target
                target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
                capture.set_editor_property('texture_target',target)
                phase='fire';stamp=time.monotonic()
        elif phase=='fire' and time.monotonic()-stamp>2:
            before=sample('before_fire');r['samples'].append(before);check(before)
            eye=soldier.get_actor_location()+unreal.Vector(0,0,40)
            soldier.call_method('PC_RequestFire',args=(eye,unreal.Vector(0,0,1)))
            after=sample('after_fire');r['samples'].append(after)
            assert after['ammo'][0]==before['ammo'][0]-1 and after['shot']==before['shot']+1,after
            assert after['ammo'][0]+after['ammo'][1]+after['shot']==18
            phase='reload_request';stamp=time.monotonic()
        elif phase=='reload_request' and time.monotonic()-stamp>1:
            soldier.call_method('PC_RequestReload')
            reload_start=unreal.GameplayStatics.get_time_seconds(world)
            assert str(soldier.get_editor_property('ActionState'))=='Reloading'
            r['reload_start_game_time']=reload_start;phase='reload';stamp=time.monotonic()
        elif phase=='reload':
            now=unreal.GameplayStatics.get_time_seconds(world)
            assert now-reload_start<10,'Original reload did not return'
            if mid_target is None and now-reload_start>.65:
                s=sample('reload_mid');r['samples'].append(s);check(s)
                r['reload_mid_bones']=bones();aim_camera('right');mid_target=target
            if str(soldier.get_editor_property('ActionState'))=='Ready':
                reload_ready=now;phase='return';stamp=time.monotonic()
                r['reload_ready_game_time']=now
        elif phase=='return' and unreal.GameplayStatics.get_time_seconds(world)-reload_ready>1:
            s=sample('reload_return');r['samples'].append(s);check(s)
            assert s['ammo']==([8,10] if MODE=='reload' else [8,9]) and s['shot']==(0 if MODE=='reload' else 1) and s['holding_alpha']>.999,s
            r['reload_return_bones']=bones()
            observations=json.loads(wrapper.observation_json())['observations']
            timed=[x for x in observations if reload_start-.15<=x['time']<=reload_ready+.35]
            steps=[]
            for previous,current in zip(timed,timed[1:]):
                steps.append({'time':current['time'],'dt':current['dt'],'action':current['action'],'alpha':current['alpha'],
                    'gun_cm':math.dist(previous['gun'],current['gun']),'right_cm':math.dist(previous['right'],current['right']),
                    'left_cm':math.dist(previous['left'],current['left'])})
            r['full_reload_steps']=steps
            r['reload_long_frames']=[x for x in steps if x['dt']>.1]
            r['reload_discontinuities']=[x for x in steps if x['dt']<=.1 and max(x['gun_cm'],x['right_cm'],x['left_cm'])>3]
            if MODE=='reload':
                r['full_motion_gate']=False
                r['pending_initialization_frames_recorded_not_audited']=s['pending_evaluation_frames']
                target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
                capture.set_editor_property('texture_target',target);aim_camera('right')
                phase='diagnostic_return_capture';stamp=time.monotonic();return
            # Evaluate before render export/report writes. Do not retry/blend-tune a failed return.
            assert not r['reload_discontinuities'],'Full native reload/return discontinuity; stop selection'
            assert not r['reload_long_frames'],'Full native transition confounded by >100ms frames; unpassed'
            if walk_target:unreal.RenderingLibrary.export_render_target(world,walk_target,OUT.as_posix(),'walk_right.png')
            if mid_target:unreal.RenderingLibrary.export_render_target(world,mid_target,OUT.as_posix(),'reload_mid_right.png')
            aim_camera('right');phase='return_capture';stamp=time.monotonic()
        elif phase=='return_capture' and time.monotonic()-stamp>1.5:
            unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),'reload_return_right.png')
            wall=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.StaticMeshActor) if a.get_actor_label()=='PC_AlliedUEV16NearWall')
            muzzle=unreal.MathLibrary.transform_location(gun.get_actor_transform(),unreal.Vector(0,83.23,0))
            wall.set_actor_location(muzzle,False,False);r['near_wall_muzzle_cm']=[muzzle.x,muzzle.y,muzzle.z]
            phase='nearwall';stamp=time.monotonic()
        elif phase=='diagnostic_return_capture' and time.monotonic()-stamp>1.5:
            unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),'reload_return_right.png')
            finish()
        elif phase=='nearwall' and time.monotonic()-stamp>1:
            before=sample('before_nearwall');r['samples'].append(before)
            eye=soldier.get_actor_location()+unreal.Vector(0,0,40)
            soldier.call_method('PC_RequestFire',args=(eye,soldier.get_actor_forward_vector()))
            after=sample('after_nearwall');r['samples'].append(after)
            assert after['outcome'] in ('Barrel blocked','Muzzle blocked'),after
            assert after['ammo'][0]+after['ammo'][1]+after['shot']==18
            wall.set_actor_location(unreal.Vector(-100000,0,0),False,False)
            soldier.call_method('PC_ResetLifecycle');phase='reset';stamp=time.monotonic()
        elif phase=='reset' and time.monotonic()-stamp>1:
            s=sample('ready_after_reset');r['samples'].append(s);check(s)
            assert s['health']==100 and s['action']=='Ready'
            r['lifecycle_scope']='Existing normal Ready reset only; death/interruption not tested'
            finish()
    except Exception:finish(traceback.format_exc())
    finally:busy=False

try:
    if MODE in ('motion','reload'):
        assert V16
        early=read(BASE/'native_hold_v16_early/result.json')
        review=read(BASE/'native_hold_v16_early/visual_review.json')
        assert not early['errors'] and review['actual_ready_views_inspected'] and review['static_visual_gate']
    assert hasattr(unreal,'ParisNPCGripAssetFactory') and not hasattr(unreal,'ParisBlueprintAuthoring')
    if unreal.EditorAssetLibrary.does_asset_exist(PACKAGE):
        first=read(BASE/('native_hold_v16_early' if V16 else 'native_ready_v1')/'result.json')
        assert first['candidate_abp_saved_unselected']==PACKAGE
        p=STORE/'Content'/ (PACKAGE.removeprefix('/Game/')+'.uasset')
        expected=first.get('candidate_abp_sha256','870b9440e95a6ffae006a78cbba23dd2954816cc77b105f0e9327d1a146125c2')
        assert sha(p)==expected,'Preserve exact first graph'
        abp=unreal.load_asset(PACKAGE)
        r['existing_graph_exact_reused']=sha(p)
    else:
        abp=unreal.ParisNPCGripAssetFactory.create_adapter(unreal.load_asset(cfg['source_mesh']),PACKAGE,CONFIG.read_text())
        assert abp,'Native graph factory failed'
        assert unreal.EditorAssetLibrary.save_loaded_asset(abp,False)
    cls=unreal.EditorAssetLibrary.load_blueprint_class(PACKAGE);assert cls
    r['candidate_abp_saved_unselected']=PACKAGE
    r['candidate_abp_sha256']=sha(STORE/'Content'/ (PACKAGE.removeprefix('/Game/')+'.uasset'))
    data=unreal.new_object(unreal.ParisNPCGripConfig)
    data.set_editor_property('PostProcessClass',cls);data.set_editor_property('BindingJson',CONFIG.read_text())
    native_actor=actors.spawn_actor_from_class(unreal.ParisNPCGripActor,unreal.Vector(),unreal.Rotator())
    native_actor.set_actor_label('PC_AlliedUEV15Candidate');native_actor.set_editor_property('BindingConfig',data)
    # Unset Target gates native binding until the one-time runtime setup stimulus.
    cap=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(),unreal.Rotator());cap.set_actor_label('PC_AlliedUEV15Capture')
    if MODE=='motion':
        blocker=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(-100000,0,0),unreal.Rotator())
        blocker.set_actor_label('PC_AlliedUEV16NearWall')
        component=blocker.get_component_by_class(unreal.StaticMeshComponent)
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube.Cube'))
        component.set_world_scale3d(unreal.Vector(.5,.5,.5))
        component.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
        component.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_BLOCK)
    # Identical diagnostic lighting convention, not source-material authoring.
    for pitch,yaw in ((-25,45),(-25,-135),(-20,135),(-20,-45)):
        light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(),unreal.Rotator(pitch=pitch,yaw=yaw,roll=0))
        light.set_actor_label('PC_AlliedUEV15Fill')
        c=light.get_component_by_class(unreal.DirectionalLightComponent)
        c.set_intensity(6);c.set_cast_shadows(False)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play()
except Exception:
    finish(traceback.format_exc());unreal.SystemLibrary.quit_editor()
