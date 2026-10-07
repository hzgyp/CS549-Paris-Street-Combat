"""New German-only adoption entry; native pose/equipment, original transactions."""
import os,sys,time,math,traceback
from collections import deque
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import *
MODE=os.environ['CS549_GERMAN_FORMAL_MODE'];IDENTITY=os.environ['CS549_GERMAN_FORMAL_ID']
assert MODE in ('early','compat','author','fresh','audit') and IDENTITY.replace('_','').isalnum()
OUT=BASE/IDENTITY;assert not OUT.exists();OUT.mkdir(parents=True)
cfg=read(CONFIG)
r={'mode':MODE,'pid':os.getpid(),'status':'starting','errors':[],'samples':[],
   'map_saved':False,'python_pose_updates':0,'source_motion_changed':False,
   'full_motion_fps_shipping_second_machine':'not certified by adoption'}
write(OUT/'entry_source.json',row(Path(__file__)))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
callback=None;busy=False;start=time.monotonic();stamp=None;phase=0;phase_start=None
future=None;capture=None;target=None;view_index=0;view_requested=None
reload_start=None;reload_ready=None;walk_start=None;walk_game=None;walk_location=None
views=['right','front','top','reverse','context']

def finish(status):
    global callback
    if callback is not None:unreal.unregister_slate_post_tick_callback(callback);callback=None
    r['status']=status
    try:r['guards_after']=guards(MODE in ('author','fresh','audit'))
    except Exception:r['errors'].append(traceback.format_exc())
    write(OUT/'result.json',r)
    if editor.get_game_world():levels.editor_request_end_play()
    unreal.SystemLibrary.quit_editor()

def angle(q,expected):
    v=[q.x,q.y,q.z,q.w]
    dot=abs(sum(a*b for a,b in zip(v,expected))/math.sqrt(sum(a*a for a in v)*sum(b*b for b in expected)))
    return math.degrees(2*math.acos(max(-1,min(1,dot))))

def enc(t):return {'t':[t.translation.x,t.translation.y,t.translation.z],
    'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':[t.scale3d.x,t.scale3d.y,t.scale3d.z]}

def snap(world,soldier,name,ready=True):
    adapters=[a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor)
              if a.get_editor_property('Target')==soldier]
    assert len(adapters)==1,(name,'adapter count',len(adapters))
    adapter=adapters[0];pp=soldier.mesh.get_post_process_instance()
    assert pp and pp.get_class()==expected_class
    gun=soldier.get_editor_property('WeaponAppearance');assert gun and gun.get_class()==gun_class
    gunmesh=gun.get_component_by_class(unreal.StaticMeshComponent)
    rel=unreal.MathLibrary.make_relative_transform(gunmesh.get_world_transform(),soldier.mesh.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD))
    errors={}
    for rule in cfg['rules']:
        bone=rule['bone'];local=unreal.MathLibrary.make_relative_transform(
            soldier.mesh.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT),
            soldier.mesh.get_socket_transform(soldier.mesh.get_parent_bone(bone),unreal.RelativeTransformSpace.RTS_COMPONENT))
        errors[bone]=angle(local.rotation,rule['accepted_q'])
    s={'name':name,'actor':soldier.get_name(),'team':int(soldier.get_editor_property('TeamId')),
       'initialized':adapter.get_editor_property('Initialized'),'error':str(adapter.get_editor_property('BindingError')),
       'updates':adapter.get_editor_property('NativeUpdates'),'valid_input':pp.get_editor_property('ValidInput'),
       'evaluations':pp.get_editor_property('Evaluations'),'holding_alpha':pp.get_editor_property('HoldingWeight'),
       'protection':pp.get_editor_property('ProtectionError'),'ready_locals_deg':errors,
       'gun_cm':math.dist([rel.translation.x,rel.translation.y,rel.translation.z],cfg['gun_hand_relative']['t']),
       'gun_deg':angle(rel.rotation,cfg['gun_hand_relative']['q']),
       'source_preserved':gun.get_editor_property('GripMesh')==soldier.mesh,
       'combatant_preserved':gun.get_editor_property('Combatant')==soldier,
       'config_preserved':adapter.get_editor_property('BindingConfig')==data,
       'gun_mesh':gunmesh.get_editor_property('static_mesh').get_path_name(),
       'actual_collision':str(gunmesh.get_collision_enabled()),
       'mesh':soldier.mesh.get_editor_property('skeletal_mesh_asset').get_path_name(),
       'ammo':[int(soldier.get_editor_property(n)) for n in ('LoadedAmmo','ReserveAmmo')],
       'action':str(soldier.get_editor_property('ActionState')),'speed':soldier.get_velocity().length(),
       'game_time':unreal.GameplayStatics.get_time_seconds(world)}
    assert s['initialized'] and not s['error'] and s['updates']>0 and s['valid_input'] and s['evaluations']>0,s
    assert s['protection']<.0001 and s['gun_cm']<.01 and s['gun_deg']<.01,s
    assert s['team']==1 and s['source_preserved'] and s['combatant_preserved'] and s['config_preserved'] and s['mesh']==cfg['source_mesh'],s
    assert gunmesh.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION and gunmesh.get_editor_property('static_mesh')==rifle_mesh,s
    if ready:assert s['action']=='Ready' and max(errors.values())<.01 and s['holding_alpha']>.999,s
    r['samples'].append(s);return s

def other_selections(world):
    player=unreal.GameplayStatics.get_player_character(world,0)
    assert player.mesh.get_post_process_instance() is None
    fp=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFirstPersonApprovedActor)
    assert len(fp)==1 and fp[0].get_editor_property('Initialized') and not str(fp[0].get_editor_property('BindingError'))
    policies=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisAlliedGripPolicy)
    assert len(policies)==1 and policies[0].get_editor_property('RegisteredNPCs')==2 and not str(policies[0].get_editor_property('SetupError'))
    allies=unreal.GameplayStatics.get_all_actors_of_class(world,ally_class)
    assert len(allies)==2
    records=[]
    allied_cfg=read(STORE/'Evidence/AlliedNPCUEV15/preflight_v16/binding.json')
    for ally in allies:
        a=next(x for x in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor) if x.get_editor_property('Target')==ally)
        pp=ally.mesh.get_post_process_instance();assert pp and pp.get_editor_property('ValidInput')
        assert a.get_editor_property('Initialized') and not str(a.get_editor_property('BindingError'))
        assert a.get_editor_property('GunErrorCm')<.01 and a.get_editor_property('GunErrorDegrees')<.01
        assert a.get_editor_property('BindingConfig').get_editor_property('BindingJson')==json.dumps(allied_cfg,indent=2)+'\n'
        errors={}
        for rule in allied_cfg['rules']:
            bone=rule['bone'];t=unreal.MathLibrary.make_relative_transform(
                ally.mesh.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT),
                ally.mesh.get_socket_transform(ally.mesh.get_parent_bone(bone),unreal.RelativeTransformSpace.RTS_COMPONENT))
            errors[bone]=angle(t.rotation,rule['accepted_q'])
        assert max(errors.values())<.01
        records.append({'actor':ally.get_name(),'ready_local_error_deg':max(errors.values()),'gun_cm':a.get_editor_property('GunErrorCm')})
    r['approved_allied_fp_native_regression']=records

def setup():
    policy=actors.spawn_actor_from_class(unreal.ParisGermanGripPolicy,unreal.Vector(),unreal.Rotator())
    assert policy;policy.set_actor_label(LABEL)
    policy.set_editor_property('GermanNPCClass',german_class);policy.set_editor_property('BindingConfig',data)
    policy.set_editor_property('RifleAppearanceClass',gun_class);policy.set_editor_property('RifleMesh',rifle_mesh)
    return policy

def aim_view(world,soldier,view):
    global capture,target
    gun=soldier.get_editor_property('WeaponAppearance')
    assert capture is not None,'Capture must be staged before PIE'
    hand=soldier.mesh.get_socket_location('hand_r');left=soldier.mesh.get_socket_location('hand_l')
    center=(hand+left)/2
    if view=='context':center=(center+soldier.mesh.get_socket_location('spine_01'))/2
    direction={'right':soldier.get_actor_right_vector(),'front':soldier.get_actor_forward_vector(),
        'top':unreal.Vector(0,0,1),'reverse':-soldier.get_actor_right_vector(),'context':soldier.get_actor_right_vector()}[view]
    eye=center+direction*300;rot=unreal.MathLibrary.find_look_at_rotation(eye,center)
    if view=='top':rot=unreal.Rotator(pitch=-90,yaw=soldier.get_actor_rotation().yaw,roll=0)
    capture.set_world_location(eye,False,False);capture.set_world_rotation(rot,False,False)
    capture.set_editor_property('ortho_width',250 if view=='context' else 150)
    capture.clear_show_only_components();capture.set_editor_property('show_only_actors',[soldier,gun]);capture.capture_scene()

def get_capture(world):
    global capture,target
    cap=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SceneCapture2D) if a.get_actor_label()=='PC_GermanFormalV14Capture')
    capture=cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    target=unreal.RenderingLibrary.create_render_target2d(world,1400,900,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
    capture.set_editor_property('texture_target',target)
    capture.set_editor_property('primitive_render_mode',unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
    capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
    capture.set_editor_property('capture_every_frame',False);capture.set_editor_property('capture_on_movement',False)
    capture.set_editor_property('show_flag_settings',[unreal.EngineShowFlagsSetting(show_flag_name=n,enabled=False) for n in ('Fog','Atmosphere','Bloom','DepthOfField','MotionBlur')])

def export(world,name):
    unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),name+'.png')
    assert (OUT/(name+'.png')).stat().st_size>15000

def closure():
    registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
    registry.scan_paths_synchronous([DATA.rsplit('/',1)[0]],True)
    def collect(soft):
        seen={ENTRY};queue=deque([ENTRY]);edges={};external=set()
        opts=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=soft)
        while queue:
            p=queue.popleft();deps=registry.get_dependencies(p,opts)
            assert deps is not None,'Unavailable dependency query: '+p
            edges[p]=sorted(str(d) for d in deps)
            for d in edges[p]:
                if d.startswith('/Game/') and d not in seen:seen.add(d);queue.append(d)
                elif not d.startswith('/Game/'):external.add(d)
        return seen,edges,external
    seen,edges,external=collect(True);hard,_,_=collect(False);files=[];missing=[]
    for p in sorted(seen):
        stem=ROOT/'Unreal/ParisStreetCombat/Content'/p.removeprefix('/Game/')
        paths=[Path(str(stem)+suffix) for suffix in ('.uasset','.umap') if Path(str(stem)+suffix).is_file()]
        if len(paths)!=1:missing.append(p)
        else:files.append({**row(paths[0]),'package':p})
    assert DATA in seen and GRAPH in seen and GUN in seen and GUNMESH in seen
    hard_missing=sorted(set(missing)&hard);assert not hard_missing,hard_missing
    return {'files':files,'external_dependencies':sorted(external),'hard_missing_packages':hard_missing,
        'missing_packages':missing,'missing_referencers':{p:sorted(k for k,v in edges.items() if p in v) for p in missing},'edges':edges}

def tick(delta):
    global busy,stamp,phase,phase_start,future,view_index,view_requested,reload_start,reload_ready,walk_start,walk_game,walk_location
    if busy:return
    busy=True
    try:
        assert time.monotonic()-start<240,'New adoption entry deadline'
        world=editor.get_game_world()
        if not world or not unreal.GameplayStatics.get_player_character(world,0):return
        if stamp is None:stamp=time.monotonic();return
        if time.monotonic()-stamp<12:return
        policies=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisGermanGripPolicy)
        assert len(policies)==1;policy=policies[0];assert not str(policy.get_editor_property('SetupError'))
        soldiers=sorted(unreal.GameplayStatics.get_all_actors_of_class(world,german_class),key=lambda a:a.get_name())
        if phase==0:
            assert len(soldiers)==3 and policy.get_editor_property('RegisteredNPCs')==3
            for i,s in enumerate(soldiers):snap(world,s,'existing_german'+str(i+1))
            other_selections(world);get_capture(world);phase=1
        elif phase==1:
            if view_index==len(views):
                phase=2;phase_start=time.monotonic();return
            view=views[view_index]
            if view_requested is None:aim_view(world,soldiers[0],view);view_requested=time.monotonic();return
            if time.monotonic()-view_requested<1.5:return
            snap(world,soldiers[0],'ready_'+view);export(world,'ready_'+view)
            view_requested=None;view_index+=1
        elif phase==2:
            transform=unreal.Transform(location=soldiers[0].get_actor_location()+unreal.Vector(0,500,0))
            api=unreal.get_default_object(unreal.GameplayStatics)
            future=api.call_method('BeginDeferredActorSpawnFromClass',args=(world,german_class,transform,
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            assert future
            future=api.call_method('FinishSpawningActor',args=(future,transform,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            assert future;phase=3;phase_start=time.monotonic()
        elif phase==3 and time.monotonic()-phase_start>5:
            assert policy.get_editor_property('RegisteredNPCs')==4
            snap(world,future,'later_spawn');future.destroy_actor();phase=4;phase_start=time.monotonic()
        elif phase==4 and time.monotonic()-phase_start>2:
            assert policy.get_editor_property('RegisteredNPCs')==3
            assert len(unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor))==5
            assert len(unreal.GameplayStatics.get_all_actors_of_class(world,gun_class))==3
            r['future_spawn_and_owned_cleanup']=True
            if MODE!='compat':
                if MODE=='fresh':
                    audit_out=BASE/'audit_v1';assert not audit_out.exists()
                    audit=closure()
                    write(audit_out/'result.json',{'status':'passed_saved_dependency_closure','errors':[],
                        'pid':os.getpid(),'mode':'read_only_audit_within_fresh_entry','map_saved':False,
                        'guards_after':guards(True),**audit})
                    r['saved_dependency_audit']='audit_v1/result.json (same fresh-load process)'
                finish('passed_three_germans_and_future_native_binding');return
            walk_location=soldiers[0].get_actor_location();walk_game=unreal.GameplayStatics.get_time_seconds(world)
            phase=5;walk_start=time.monotonic()
        elif phase==5:
            soldiers[0].add_movement_input(soldiers[0].get_actor_forward_vector(),1,True)
            if unreal.GameplayStatics.get_time_seconds(world)-walk_game>1:
                s=snap(world,soldiers[0],'walk');assert s['speed']>10,s
                r['walk_distance_cm']=(soldiers[0].get_actor_location()-walk_location).length()
                assert r['walk_distance_cm']>10
                aim_view(world,soldiers[0],'context');phase=6;phase_start=time.monotonic()
        elif phase==6 and time.monotonic()-phase_start>1.5:
            export(world,'walk_context');before=snap(world,soldiers[0],'before_reload');assert before['ammo']==[2,16]
            soldiers[0].call_method('PC_RequestReload');assert str(soldiers[0].get_editor_property('ActionState'))=='Reloading'
            reload_start=unreal.GameplayStatics.get_time_seconds(world);phase=7
        elif phase==7:
            now=unreal.GameplayStatics.get_time_seconds(world);assert now-reload_start<10
            if str(soldiers[0].get_editor_property('ActionState'))=='Ready':reload_ready=now;phase=8;return
            pp=soldiers[0].mesh.get_post_process_instance()
            if pp and pp.get_editor_property('Evaluations')>0 and now-reload_start>.6 and 'reload_mid' not in r:
                s=snap(world,soldiers[0],'reload_mid',False);assert s['holding_alpha']<.001,s
                aim_view(world,soldiers[0],'context');r['reload_mid']=s
        elif phase==8 and unreal.GameplayStatics.get_time_seconds(world)-reload_ready>1:
            if 'reload_mid' in r:export(world,'reload_mid_context')
            s=snap(world,soldiers[0],'reload_return');assert s['ammo']==[8,10] and sum(s['ammo'])==18,s
            aim_view(world,soldiers[0],'context');phase=9;phase_start=time.monotonic()
        elif phase==9 and time.monotonic()-phase_start>1.5:
            export(world,'reload_return_context');r['original_reload_conserved_and_returned']=True
            other_selections(world);finish('passed_bounded_native_walk_reload_compatibility_not_full_motion')
    except Exception:r['errors'].append(traceback.format_exc());finish('failed_preserve_state')
    finally:busy=False

try:
    r['guards_before']=guards(MODE in ('fresh','audit'))
    german_class=unreal.EditorAssetLibrary.load_blueprint_class(CLASS)
    ally_class=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisAlliedNPCV1')
    gun_class=unreal.EditorAssetLibrary.load_blueprint_class(GUN);rifle_mesh=unreal.load_asset(GUNMESH)
    assert german_class and ally_class and gun_class and rifle_mesh and hasattr(unreal,'ParisGermanGripPolicy')
    if MODE=='early':
        assert not unreal.EditorAssetLibrary.does_asset_exist(GRAPH) and not unreal.EditorAssetLibrary.does_asset_exist(DATA)
        abp=unreal.ParisNPCGripAssetFactory.create_adapter(unreal.load_asset(cfg['source_mesh']),GRAPH,CONFIG.read_text())
        assert abp and unreal.EditorAssetLibrary.save_loaded_asset(abp,False)
        expected_class=unreal.EditorAssetLibrary.load_blueprint_class(GRAPH);assert expected_class
        factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.ParisNPCGripConfig)
        data=unreal.AssetToolsHelpers.get_asset_tools().create_asset(DATA.rsplit('/',1)[1],DATA.rsplit('/',1)[0],unreal.ParisNPCGripConfig,factory)
        assert data;data.set_editor_property('PostProcessClass',expected_class);data.set_editor_property('BindingJson',CONFIG.read_text())
        assert unreal.EditorAssetLibrary.save_loaded_asset(data,False)
        write(BASE/'candidate_assets.json',{'files':[row(STORE/'Content'/(p.removeprefix('/Game/')+'.uasset')) for p in (DATA,GRAPH)]})
    else:
        assert all(exact(f) for f in read(BASE/'candidate_assets.json')['files'])
        data=unreal.load_asset(DATA);expected_class=unreal.EditorAssetLibrary.load_blueprint_class(GRAPH)
    assert data and expected_class and data.get_editor_property('BindingJson')==CONFIG.read_text()
    assert data.get_editor_property('PostProcessClass')==expected_class
    policies=[a for a in actors.get_all_level_actors() if isinstance(a,unreal.ParisGermanGripPolicy)]
    if MODE=='author':
        for name in ('early_v1','compat_v1'):
            proof=read(BASE/name/'result.json');assert not proof['errors'] and proof['status'].startswith('passed_')
            assert read(BASE/name/'image_review.json')['native_originals_inspected']
        assert not policies;setup();assert levels.save_current_level();r['map_saved']=True;r['saved_files']=[row(MAP)]
        finish('saved_german_policy_requires_fresh_verification')
    elif MODE=='audit':r.update(closure());finish('passed_saved_dependency_closure')
    else:
        if MODE in ('early','compat'):assert not policies;setup()
        else:
            assert len(policies)==1 and policies[0].get_editor_property('BindingConfig')==data
            assert all(exact(f) for f in read(BASE/'author_v1/result.json')['saved_files'])
        cap=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(),unreal.Rotator());cap.set_actor_label('PC_GermanFormalV14Capture')
        for pitch,yaw in ((-25,45),(-25,-135),(-20,135),(-20,-45)):
            light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(),unreal.Rotator(pitch=pitch,yaw=yaw,roll=0))
            light.set_actor_label('PC_GermanFormalV14TemporaryFill')
            c=light.get_component_by_class(unreal.DirectionalLightComponent);c.set_intensity(6);c.set_cast_shadows(False)
        unreal.EditorPythonScripting.set_keep_python_script_alive(True)
        callback=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play()
except Exception:r['errors'].append(traceback.format_exc());finish('failed_preserve_state')
