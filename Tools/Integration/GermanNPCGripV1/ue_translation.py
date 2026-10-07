"""Unsaved German gun-only translation; both hands/all bones fixed."""
import os,sys,time,traceback,math
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import *
IDENTITY=os.environ['CS549_GERMAN_GRIP_ID']
assert IDENTITY.replace('_','').isalnum()
OUT=BASE/IDENTITY;assert not OUT.exists();OUT.mkdir(parents=True)
fit=read(BASE/'marked_landmarks_v1/result.json')
assert fit['status']=='measured_one_marked_translation'
assert sha(GLB)==fit['model']['sha256'] and sha(REFERENCE/'result.json')==fit['reference_sha256']
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
r={'status':'starting','errors':[],'pid':os.getpid(),'guards_before':guards(),'captures':[],
   'map_saved':False,'formal_selected':False,'hand_arm_digit_changed':False,
   'gun_rotation_scale_changed':False,'contact_gameplay_accepted':False,
   'landmark_proof_sha256':sha(BASE/'marked_landmarks_v1/result.json')}
write(OUT/'entry_source.json',row(Path(__file__)))
start=time.monotonic();ready=ending=callback=world=soldier=gun=capture=target=None
index=0;requested=None;busy=moved=False
views=[('before_right','right',78),('after_right','right',78),('after_front','front',78),
       ('after_top','top',78),('after_reverse','left',78),('after_context','right',155),('after_trigger','right',32)]
def xyz(v):return [v.x,v.y,v.z]
def enc(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':xyz(t.scale3d)}
def bones():
    m=soldier.mesh
    return {str(m.get_bone_name(i)):enc(m.get_socket_transform(m.get_bone_name(i),unreal.RelativeTransformSpace.RTS_WORLD)) for i in range(m.get_num_bones())}
def save():write(OUT/'result.json',r)
def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    try:r['guards_after']=guards()
    except Exception:r['errors'].append(traceback.format_exc())
    r['status']='failed_preserved' if r['errors'] else 'translated_native_views_require_user_review'
    save()
    if world:
        unreal.GameplayStatics.set_game_paused(world,False)
        levels.editor_request_end_play()
    ending=time.monotonic()
def tick(dt):
    global ready,ending,callback,world,soldier,gun,capture,target,index,requested,busy,moved
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
        if not world or not unreal.GameplayStatics.get_player_pawn(world,0):return
        if ready is None:
            soldier=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character) if a.get_actor_label()=='PC_City_Enemy1')
            gun=soldier.get_editor_property('WeaponAppearance')
            assert gun and gun.get_editor_property('GripMesh')==soldier.mesh and gun.get_editor_property('Combatant')==soldier
            assert soldier.get_class().get_path_name()==fit['fixed_source']['class']
            assert gun.get_class().get_path_name()==fit['fixed_source']['gun_class']
            cap=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SceneCapture2D) if a.get_actor_label()=='PC_GermanGunTranslationCapture')
            capture=cap.get_component_by_class(unreal.SceneCaptureComponent2D)
            target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,
                unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
            capture.set_editor_property('texture_target',target)
            capture.set_editor_property('primitive_render_mode',unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
            capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
            capture.set_editor_property('capture_every_frame',False)
            capture.set_editor_property('capture_on_movement',False)
            capture.set_editor_property('show_flag_settings',[unreal.EngineShowFlagsSetting(show_flag_name=n,enabled=False) for n in ('Fog','Atmosphere','Bloom','DepthOfField','MotionBlur')])
            ready=time.monotonic();return
        if time.monotonic()-ready<15:return
        component=gun.get_component_by_class(unreal.StaticMeshComponent)
        if 'before' not in r:
            assert str(soldier.get_editor_property('ActionState'))=='Ready' and soldier.get_velocity().length()<.1
            assert soldier.mesh.get_skeletal_mesh_asset().get_path_name()==fit['fixed_source']['skeletal_mesh']
            assert soldier.mesh.get_anim_instance().get_class().get_path_name()==fit['fixed_source']['anim_class']
            assert soldier.mesh.get_post_process_instance() is None
            assert component.get_editor_property('static_mesh').get_path_name()==fit['fixed_source']['gun_mesh']
            assert str(component.get_collision_enabled())==fit['fixed_source']['collision']
            assert [soldier.mesh.get_material(i).get_path_name() for i in range(soldier.mesh.get_num_materials())]==fit['fixed_source']['materials']
            assert [component.get_material(i).get_path_name() for i in range(component.get_num_materials())]==fit['fixed_source']['gun_materials']
            assert unreal.GameplayStatics.set_game_paused(world,True)
            r['before']={'bones':bones(),'gun_world':enc(component.get_world_transform()),'mesh_world':enc(soldier.mesh.get_world_transform()),
                'collision':str(component.get_collision_enabled()),'actor':soldier.get_actor_label(),
                'mesh':soldier.mesh.get_skeletal_mesh_asset().get_path_name(),'anim_class':soldier.mesh.get_anim_instance().get_class().get_path_name()}
            r['source_index_local_error_deg']=tm.index_errors(fit['fixed_source']['bone_world'],r['before']['bones'])
            assert max(r['source_index_local_error_deg'].values())<.05,'Source index changed before translation'
            point=tm.point(r['before']['bones']['hand_r'],fit['target_hand_cm'])
            blade=tm.point(r['before']['gun_world'],fit['blade_gun_cm'])
            r['landmarks']={'target_world_cm':point,'blade_before_world_cm':blade,'blade_gun_cm':fit['blade_gun_cm'],
                'delta_world_cm':[point[i]-blade[i] for i in range(3)]}
            r['translation_cm']=math.dist(point,blade)
            assert r['translation_cm']<10
            allied=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor)
            assert len(allied)==2 and all(a.get_editor_property('Initialized') and not str(a.get_editor_property('BindingError')) for a in allied)
            fp=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFirstPersonApprovedActor)
            assert len(fp)==1 and fp[0].get_editor_property('Initialized') and not str(fp[0].get_editor_property('BindingError'))
            r['approved_allied_and_fp_preserved']=True;save()
        if index>=len(views):finish();return
        name,axis,width=views[index]
        if index==1 and not (OUT/'early_acceptance.json').is_file():return
        if name.startswith('after') and not moved:
            gun.set_actor_location(gun.get_actor_location()+unreal.Vector(*r['landmarks']['delta_world_cm']),False,False)
            moved=True
            r['after']={'gun_world':enc(component.get_world_transform()),'bones':bones()}
            assert r['after']['bones']==r['before']['bones'],'Character bones changed'
            assert r['after']['gun_world']['q']==r['before']['gun_world']['q'] and r['after']['gun_world']['s']==r['before']['gun_world']['s']
            r['landmark_residual_cm']=math.dist(tm.point(r['after']['gun_world'],fit['blade_gun_cm']),r['landmarks']['target_world_cm'])
            r['all_bones_exact']=True;save();assert r['landmark_residual_cm']<.01
        if requested is None:
            rh,lh=soldier.mesh.get_socket_location('hand_r'),soldier.mesh.get_socket_location('hand_l')
            center=(rh+lh)/2
            if name=='after_context':center=(center+soldier.mesh.get_socket_location('spine_03'))/2
            if name=='after_trigger':center=unreal.Vector(*r['landmarks']['target_world_cm'])
            direction={'front':soldier.get_actor_forward_vector(),'right':soldier.get_actor_right_vector(),'left':-soldier.get_actor_right_vector(),'top':unreal.Vector(0,0,1)}[axis]
            eye=center+direction*250
            rotation=unreal.MathLibrary.find_look_at_rotation(eye,center)
            if axis=='top':rotation=unreal.Rotator(pitch=-90,yaw=soldier.get_actor_rotation().yaw,roll=0)
            capture.set_world_location(eye,False,False);capture.set_world_rotation(rotation,False,False)
            capture.set_editor_property('ortho_width',width);capture.clear_show_only_components()
            capture.set_editor_property('show_only_actors',[soldier,gun]);capture.capture_scene()
            requested=time.monotonic()
            r['captures'].append({'file':name+'.png','view':axis,'width_cm':width,'eye_cm':xyz(eye),'target_cm':xyz(center)})
            save();return
        if time.monotonic()-requested<1.5:return
        unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),name+'.png')
        assert (OUT/(name+'.png')).stat().st_size>15000
        assert bones()==r['before']['bones'],'Character capture drift'
        expected=r['after']['gun_world'] if moved else r['before']['gun_world']
        current=enc(component.get_world_transform());drift=math.dist(current['t'],expected['t'])
        assert drift<.01 and current['q']==expected['q'] and current['s']==expected['s']
        r['captures'][-1]['gun_drift_cm']=drift;save();index+=1;requested=None
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    source=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_City_Enemy1')
    assert source.get_editor_property('WeaponAppearance') is None,'Preserve unexpectedly equipped formal German'
    cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Weapons/GermanRifleUEV1/BP_PC_GermanRifleAttachmentV2')
    staged=actors.spawn_actor_from_class(cls,source.get_actor_location(),unreal.Rotator())
    staged.set_actor_label('PC_GermanGunTranslationCandidate');staged.set_editor_property('GripMesh',source.mesh)
    staged.set_editor_property('Combatant',source);staged.set_owner(source)
    assert staged.attach_to_component(source.mesh,'hand_r',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
    source.set_editor_property('WeaponAppearance',staged)
    cap=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(),unreal.Rotator());cap.set_actor_label('PC_GermanGunTranslationCapture')
    for pitch,yaw in ((-25,45),(-25,-135),(-20,135),(-20,-45)):
        light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,300),unreal.Rotator(pitch=pitch,yaw=yaw))
        light.set_actor_label('PC_GermanGunTranslationFill');c=light.get_component_by_class(unreal.DirectionalLightComponent)
        c.set_intensity(6);c.set_cast_shadows(False)
    save();unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_startup';save();unreal.SystemLibrary.quit_editor()
