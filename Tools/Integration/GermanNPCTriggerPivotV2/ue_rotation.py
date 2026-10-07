"""Unsaved one trigger-pivot gun rotation; every character bone stays fixed."""
import os,sys,time,traceback,math
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import *
BASE=STORE/'Evidence/GermanNPCTriggerPivotV2'
IDENTITY=os.environ['CS549_GERMAN_PIVOT_ID'];assert IDENTITY.replace('_','').isalnum()
OUT=BASE/IDENTITY;assert not OUT.exists();OUT.mkdir(parents=True)
PROOF=BASE/'marked_rotation_v1/result.json';fit=read(PROOF)
assert fit['status']=='one_marked_trigger_pivot_rotation'
for entry in (fit['v1_result'],fit['v1_landmarks'],fit['model']):assert sha(ROOT/entry['path'])==entry['sha256']
v1=read(ROOT/fit['v1_result']['path'])
source=read(ROOT/fit['v1_landmarks']['path'])['fixed_source']
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
r={'status':'starting','errors':[],'pid':os.getpid(),'identity':IDENTITY,'guards_before':guards(),
   'captures':[],'map_saved':False,'formal_selected':False,'hand_arm_digit_changed':False,
   'gun_scale_changed':False,'independent_translation':False,'contact_gameplay_accepted':False,
   'proof_sha256':sha(PROOF),'angle_deg':fit['angle_deg']}
write(OUT/'entry_source.json',row(Path(__file__)))
start=time.monotonic();ready=ending=callback=world=soldier=gun=capture=target=None
index=0;requested=None;busy=rotated=False
views=[('before_top','top',78),('before_right','right',78),('after_top','top',78),
       ('after_right','right',78),('after_front','front',78),('after_reverse','left',78),
       ('after_context','right',155),('after_trigger','right',32),
       ('after_palm_top','top',32),('after_palm_reverse','left',32)]
def xyz(v):return [v.x,v.y,v.z]
def enc(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
def native(t):
    value=unreal.Transform(location=unreal.Vector(*t['t']),rotation=unreal.Quat(*t['q']).rotator(),scale=unreal.Vector(*t['s']))
    assert math.dist(enc(value)['t'],t['t'])<.001 and tm.angle(enc(value)['q'],t['q'])<.01
    return value
def bones():
    m=soldier.mesh
    return {str(m.get_bone_name(i)):enc(m.get_socket_transform(m.get_bone_name(i),unreal.RelativeTransformSpace.RTS_WORLD)) for i in range(m.get_num_bones())}
def current_gun():return enc(gun.get_component_by_class(unreal.StaticMeshComponent).get_world_transform())
def save():write(OUT/'result.json',r)
def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    try:
        r['guards_after']=guards()
        r['retained_inputs_exact']=all(sha(ROOT/e['path'])==e['sha256'] for e in (fit['v1_result'],fit['v1_landmarks'],fit['model']))
        assert r['retained_inputs_exact'] and sha(PROOF)==r['proof_sha256']
    except Exception:r['errors'].append(traceback.format_exc())
    r['status']='failed_preserved' if r['errors'] else 'rotated_native_views_require_user_review'
    save()
    if world:
        unreal.GameplayStatics.set_game_paused(world,False);levels.editor_request_end_play()
    ending=time.monotonic()
def tick(dt):
    global ready,ending,callback,world,soldier,gun,capture,target,index,requested,busy,rotated
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>3:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<240,'Capture deadline'
        world=editor.get_game_world()
        if not world or not unreal.GameplayStatics.get_player_pawn(world,0):return
        if ready is None:
            soldier=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character) if a.get_actor_label()=='PC_City_Enemy1')
            gun=soldier.get_editor_property('WeaponAppearance')
            assert gun and gun.get_editor_property('GripMesh')==soldier.mesh and gun.get_editor_property('Combatant')==soldier
            assert soldier.get_class().get_path_name()==source['class'] and gun.get_class().get_path_name()==source['gun_class']
            cap=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SceneCapture2D) if a.get_actor_label()=='PC_GermanTriggerPivotCapture')
            capture=cap.get_component_by_class(unreal.SceneCaptureComponent2D)
            target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
            capture.set_editor_property('texture_target',target)
            capture.set_editor_property('primitive_render_mode',unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
            capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
            capture.set_editor_property('capture_every_frame',False);capture.set_editor_property('capture_on_movement',False)
            capture.set_editor_property('show_flag_settings',[unreal.EngineShowFlagsSetting(show_flag_name=n,enabled=False) for n in ('Fog','Atmosphere','Bloom','DepthOfField','MotionBlur')])
            ready=time.monotonic();return
        if time.monotonic()-ready<15:return
        component=gun.get_component_by_class(unreal.StaticMeshComponent)
        if 'before' not in r:
            assert str(soldier.get_editor_property('ActionState'))=='Ready' and soldier.get_velocity().length()<.1
            assert soldier.mesh.get_skeletal_mesh_asset().get_path_name()==source['skeletal_mesh']
            assert soldier.mesh.get_anim_instance().get_class().get_path_name()==source['anim_class']
            assert soldier.mesh.get_post_process_instance() is None
            assert component.get_editor_property('static_mesh').get_path_name()==source['gun_mesh']
            assert str(component.get_collision_enabled())==source['collision']
            assert [soldier.mesh.get_material(i).get_path_name() for i in range(soldier.mesh.get_num_materials())]==source['materials']
            assert [component.get_material(i).get_path_name() for i in range(component.get_num_materials())]==source['gun_materials']
            assert unreal.GameplayStatics.set_game_paused(world,True)
            fixed=bones();H=fixed['hand_r'];rel=fit['v1_gun_hand_relative']
            r['source_index_local_error_deg']=tm.index_errors(v1['after']['bones'],fixed)
            assert max(r['source_index_local_error_deg'].values())<.05
            expected={'t':tm.point(H,rel['t']),'q':tm.qmul(H['q'],rel['q']),'s':rel['s']}
            assert math.dist(enc(gun.get_actor_transform())['t'],current_gun()['t'])<.01
            assert tm.angle(enc(gun.get_actor_transform())['q'],current_gun()['q'])<.01
            gun.set_actor_transform(native(expected),False,False)
            actual=current_gun()
            r['v1_recreated_position_cm']=math.dist(actual['t'],expected['t'])
            r['v1_recreated_rotation_deg']=tm.angle(actual['q'],expected['q'])
            assert r['v1_recreated_position_cm']<.01 and r['v1_recreated_rotation_deg']<.01 and actual['s']==expected['s']
            assert bones()==fixed
            r['before']={'bones':fixed,'gun_world':actual,'mesh_world':enc(soldier.mesh.get_world_transform()),'collision':str(component.get_collision_enabled()),'materials':source['materials'],'gun_materials':source['gun_materials']}
            pivot=tm.point(actual,fit['pivot_gun_cm'])
            radians=math.radians(fit['angle_deg']);axis=fit['axis_world']
            q=[*(v*math.sin(radians/2) for v in axis),math.cos(radians/2)]
            r['pivot_before_world_cm']=pivot
            r['rotation_axis_world']=axis
            r['goal']={'t':[pivot[i]+v for i,v in enumerate(tm.rotate(q,[actual['t'][i]-pivot[i] for i in range(3)]))],
                'q':tm.qmul(q,actual['q']),'s':actual['s']}
            allied=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor)
            assert len(allied)==2 and all(a.get_editor_property('Initialized') and not str(a.get_editor_property('BindingError')) for a in allied)
            fp=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFirstPersonApprovedActor)
            assert len(fp)==1 and fp[0].get_editor_property('Initialized') and not str(fp[0].get_editor_property('BindingError'))
            r['approved_allied_and_fp_preserved']=True;save()
        if index>=len(views):finish();return
        name,axis,width=views[index]
        if index==2 and not (OUT/'early_acceptance.json').is_file():return
        if name.startswith('after') and not rotated:
            gun.set_actor_transform(native(r['goal']),False,False);rotated=True
            actual=current_gun();r['after']={'gun_world':actual,'bones':bones()}
            assert r['after']['bones']==r['before']['bones'] and actual['s']==r['before']['gun_world']['s']
            r['pivot_residual_cm']=math.dist(tm.point(actual,fit['pivot_gun_cm']),r['pivot_before_world_cm'])
            r['actual_rotation_deg']=tm.angle(r['before']['gun_world']['q'],actual['q'])
            r['rotation_goal_error_deg']=tm.angle(actual['q'],r['goal']['q'])
            r['position_goal_error_cm']=math.dist(actual['t'],r['goal']['t'])
            r['all_bones_exact']=True
            assert r['pivot_residual_cm']<.01 and r['rotation_goal_error_deg']<.01 and r['position_goal_error_cm']<.01
            save()
        if requested is None:
            rh,lh=soldier.mesh.get_socket_location('hand_r'),soldier.mesh.get_socket_location('hand_l');center=(rh+lh)/2
            if name=='after_context':center=(center+soldier.mesh.get_socket_location('spine_03'))/2
            if name=='after_trigger':center=unreal.Vector(*r['pivot_before_world_cm'])
            if 'palm' in name:center=rh
            direction={'front':soldier.get_actor_forward_vector(),'right':soldier.get_actor_right_vector(),'left':-soldier.get_actor_right_vector(),'top':unreal.Vector(0,0,1)}[axis]
            eye=center+direction*250;rotation=unreal.MathLibrary.find_look_at_rotation(eye,center)
            if axis=='top':rotation=unreal.Rotator(pitch=-90,yaw=soldier.get_actor_rotation().yaw,roll=0)
            capture.set_world_location(eye,False,False);capture.set_world_rotation(rotation,False,False)
            capture.set_editor_property('ortho_width',width);capture.clear_show_only_components()
            capture.set_editor_property('show_only_actors',[soldier,gun]);capture.capture_scene();requested=time.monotonic()
            r['captures'].append({'file':name+'.png','view':axis,'width_cm':width,'eye_cm':xyz(eye),'target_cm':xyz(center),
                'rotation_pitch_yaw_roll':[rotation.pitch,rotation.yaw,rotation.roll]});save();return
        if time.monotonic()-requested<1.5:return
        unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),name+'.png')
        assert (OUT/(name+'.png')).stat().st_size>15000 and bones()==r['before']['bones']
        expected=r['after']['gun_world'] if rotated else r['before']['gun_world'];actual=current_gun()
        drift=math.dist(actual['t'],expected['t']);assert drift<.01 and actual['q']==expected['q'] and actual['s']==expected['s']
        r['captures'][-1]['gun_drift_cm']=drift;save();index+=1;requested=None
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    source_actor=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_City_Enemy1')
    assert source_actor.get_editor_property('WeaponAppearance') is None
    cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Weapons/GermanRifleUEV1/BP_PC_GermanRifleAttachmentV2')
    staged=actors.spawn_actor_from_class(cls,source_actor.get_actor_location(),unreal.Rotator())
    staged.set_actor_label('PC_GermanTriggerPivotCandidate');staged.set_editor_property('GripMesh',source_actor.mesh)
    staged.set_editor_property('Combatant',source_actor);staged.set_owner(source_actor)
    assert staged.attach_to_component(source_actor.mesh,'hand_r',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
    source_actor.set_editor_property('WeaponAppearance',staged)
    cap=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(),unreal.Rotator());cap.set_actor_label('PC_GermanTriggerPivotCapture')
    for pitch,yaw in ((-25,45),(-25,-135),(-20,135),(-20,-45)):
        light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,300),unreal.Rotator(pitch=pitch,yaw=yaw))
        light.set_actor_label('PC_GermanTriggerPivotFill');c=light.get_component_by_class(unreal.DirectionalLightComponent)
        c.set_intensity(6);c.set_cast_shadows(False)
    save();unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_startup';save();unreal.SystemLibrary.quit_editor()
