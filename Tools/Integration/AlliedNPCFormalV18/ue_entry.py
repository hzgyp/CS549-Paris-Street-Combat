"""Adoption-only entry: native policy, both Allies, later spawn, saved closure."""
import os,sys,time,math,traceback
from collections import deque
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import *

MODE=os.environ['CS549_ALLIED_FORMAL_MODE'];IDENTITY=os.environ['CS549_ALLIED_FORMAL_ID']
assert MODE in ('early','author','fresh','audit') and IDENTITY.replace('_','').isalnum()
OUT=BASE/IDENTITY;assert not OUT.exists();OUT.mkdir(parents=True)
r={'mode':MODE,'pid':os.getpid(),'status':'starting','errors':[],'samples':[],
   'map_saved':False,'python_binding_calls':0,'source_motion_changed':False,
   'full_motion_fps_shipping_second_machine':'not tested by adoption'}
write(OUT/'entry_source.json',row(Path(__file__)))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cfg=read(CONFIG);callback=None;busy=False;start=time.monotonic();stamp=None
phase=0;phase_start=None;future=None;ending=None
rifle_count_before=None

def finish(status):
    global callback
    if callback is not None:unreal.unregister_slate_post_tick_callback(callback);callback=None
    r['status']=status
    try:r['guards_after']=guards(MODE in ('author','fresh','audit'),MODE!='early')
    except Exception:r['errors'].append(traceback.format_exc())
    write(OUT/'result.json',r)
    if editor.get_game_world():levels.editor_request_end_play()
    unreal.SystemLibrary.quit_editor()

def setup():
    policy=actors.spawn_actor_from_class(unreal.ParisAlliedGripPolicy,unreal.Vector(),unreal.Rotator())
    assert policy;policy.set_actor_label(LABEL)
    policy.set_editor_property('AlliedNPCClass',ally_class)
    policy.set_editor_property('BindingConfig',data)
    original=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_City_Ally1')
    rifle=original.get_editor_property('WeaponAppearance');assert rifle
    policy.set_editor_property('RifleAppearanceClass',rifle.get_class())
    policy.set_editor_property('RifleMesh',rifle.get_component_by_class(unreal.StaticMeshComponent).get_editor_property('static_mesh'))
    return policy

def angle(q,expected):
    v=[q.x,q.y,q.z,q.w]
    dot=abs(sum(a*b for a,b in zip(v,expected))/math.sqrt(sum(a*a for a in v)*sum(b*b for b in expected)))
    return math.degrees(2*math.acos(max(-1,min(1,dot))))

def snap(world,soldier,name):
    adapters=[a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor)
              if a.get_editor_property('Target')==soldier]
    assert len(adapters)==1,(name,'adapter count',len(adapters))
    adapter=adapters[0];pp=soldier.mesh.get_post_process_instance()
    assert pp and pp.get_class()==expected_class
    gun=soldier.get_editor_property('WeaponAppearance');assert gun
    gunmesh=gun.get_component_by_class(unreal.StaticMeshComponent)
    rel=unreal.MathLibrary.make_relative_transform(gunmesh.get_world_transform(),soldier.mesh.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD))
    errors={}
    for rule in cfg['rules']:
        bone=rule['bone'];local=unreal.MathLibrary.make_relative_transform(
            soldier.mesh.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT),
            soldier.mesh.get_socket_transform(soldier.mesh.get_parent_bone(bone),unreal.RelativeTransformSpace.RTS_COMPONENT))
        errors[bone]=angle(local.rotation,rule['accepted_q'])
    s={'name':name,'actor':soldier.get_name(),'class':soldier.get_class().get_path_name(),
       'initialized':adapter.get_editor_property('Initialized'),'error':str(adapter.get_editor_property('BindingError')),
       'updates':adapter.get_editor_property('NativeUpdates'),'valid_input':pp.get_editor_property('ValidInput'),
       'protection':pp.get_editor_property('ProtectionError'),'ready_locals_deg':errors,
       'gun_cm':math.dist([rel.translation.x,rel.translation.y,rel.translation.z],cfg['gun_hand_relative']['t']),
       'gun_deg':angle(rel.rotation,cfg['gun_hand_relative']['q']),
       'source_preserved':gun.get_editor_property('GripMesh')==soldier.mesh,
       'config_preserved':adapter.get_editor_property('BindingConfig')==data,
       'mesh':soldier.mesh.get_editor_property('skeletal_mesh_asset').get_path_name(),
       'ammo':[int(soldier.get_editor_property(n)) for n in ('LoadedAmmo','ReserveAmmo')],
       'action':str(soldier.get_editor_property('ActionState'))}
    assert s['initialized'] and not s['error'] and s['updates']>0 and s['valid_input'],s
    assert s['protection']<.0001 and s['gun_cm']<.01 and s['gun_deg']<.01,s
    assert s['source_preserved'] and s['config_preserved'] and s['mesh']==cfg['source_mesh'],s
    assert s['action']=='Ready' and max(errors.values())<.01,s
    r['samples'].append(s);return s

def view(world,soldier,name):
    player=unreal.GameplayStatics.get_player_character(world,0)
    camera=player.get_editor_property('ParisPlayerCamera');before=camera.get_editor_property('relative_location')
    fov=camera.get_editor_property('field_of_view')
    player.set_actor_location(soldier.get_actor_location()+soldier.get_actor_right_vector()*280,True,False)
    unreal.GameplayStatics.get_player_controller(world,0).set_control_rotation(
        unreal.MathLibrary.find_look_at_rotation(camera.get_world_location(),soldier.mesh.get_socket_location('spine_03')))
    assert (camera.get_editor_property('relative_location')-before).length()<1e-6
    assert camera.get_editor_property('field_of_view')==fov
    unreal.SystemLibrary.execute_console_command(world,'HighResShot 1600x900 filename="'+(OUT/(name+'.png')).as_posix()+'"')

def closure():
    registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
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
    assert DATA in seen and GRAPH in seen
    hard_missing=sorted(set(missing)&hard);assert not hard_missing,hard_missing
    return {'files':files,'external_dependencies':sorted(external),'hard_missing_packages':hard_missing,
        'missing_packages':missing,'missing_referencers':{p:sorted(k for k,v in edges.items() if p in v) for p in missing},'edges':edges}

def tick(delta):
    global busy,stamp,phase,phase_start,future,ending,rifle_count_before
    if busy:return
    busy=True
    try:
        assert time.monotonic()-start<240,'Adoption entry deadline'
        world=editor.get_game_world()
        if not world or not unreal.GameplayStatics.get_player_character(world,0):return
        if stamp is None:stamp=time.monotonic();return
        if time.monotonic()-stamp<12:return
        policies=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisAlliedGripPolicy)
        assert len(policies)==1;policy=policies[0]
        assert not str(policy.get_editor_property('SetupError'))
        soldiers=sorted(unreal.GameplayStatics.get_all_actors_of_class(world,ally_class),key=lambda a:a.get_name())
        if phase==0:
            assert len(soldiers)==2 and policy.get_editor_property('RegisteredNPCs')==2
            for i,soldier in enumerate(soldiers):snap(world,soldier,'existing_ally'+str(i+1))
            player=unreal.GameplayStatics.get_player_character(world,0)
            assert player.mesh.get_post_process_instance() is None,'Policy touched player body'
            fp=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFirstPersonApprovedActor)
            assert len(fp)==1 and fp[0].get_editor_property('Initialized') and not str(fp[0].get_editor_property('BindingError'))
            germans=[a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character) if int(a.get_editor_property('TeamId'))==1]
            assert len(germans)==3 and all(a.mesh.get_post_process_instance() is None for a in germans)
            r['player_fp_germans_unchanged']=True;view(world,soldiers[0],'ally1');phase=1;phase_start=time.monotonic()
        elif phase==1 and time.monotonic()-phase_start>3:
            view(world,soldiers[1],'ally2');phase=2;phase_start=time.monotonic()
        elif phase==2 and time.monotonic()-phase_start>3:
            rifle_count_before=len(unreal.GameplayStatics.get_all_actors_of_class(world,policy.get_editor_property('RifleAppearanceClass')))
            transform=unreal.Transform(location=soldiers[0].get_actor_location()+unreal.Vector(0,500,0))
            api=unreal.get_default_object(unreal.GameplayStatics)
            future=api.call_method('BeginDeferredActorSpawnFromClass',args=(world,ally_class,transform,
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            assert future
            future=api.call_method('FinishSpawningActor',args=(future,transform,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            assert future;phase=3;phase_start=time.monotonic()
        elif phase==3 and time.monotonic()-phase_start>5:
            assert policy.get_editor_property('RegisteredNPCs')==3
            assert len(unreal.GameplayStatics.get_all_actors_of_class(world,policy.get_editor_property('RifleAppearanceClass')))==rifle_count_before+1
            snap(world,future,'later_spawn');future.destroy_actor();phase=4;phase_start=time.monotonic()
        elif phase==4 and time.monotonic()-phase_start>2:
            assert policy.get_editor_property('RegisteredNPCs')==2
            assert len(unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor))==2
            assert len(unreal.GameplayStatics.get_all_actors_of_class(world,policy.get_editor_property('RifleAppearanceClass')))==rifle_count_before
            r['future_spawn_and_destroy_cleanup']=True
            assert all((OUT/(name+'.png')).is_file() for name in ('ally1','ally2'))
            finish('passed_two_allies_and_future_native_binding')
    except Exception:r['errors'].append(traceback.format_exc());finish('failed_preserve_state')
    finally:busy=False

try:
    r['guards_before']=guards(MODE in ('fresh','audit'),MODE!='early')
    assert all(exact(f) for f in read(BASE/'preflight/result.json')['accepted_algorithm_files'])
    data=unreal.load_asset(DATA);expected_class=unreal.EditorAssetLibrary.load_blueprint_class(GRAPH)
    ally_class=unreal.EditorAssetLibrary.load_blueprint_class(CLASS)
    assert data and expected_class and ally_class and hasattr(unreal,'ParisAlliedGripPolicy')
    assert data.get_editor_property('BindingJson')==CONFIG.read_text()
    assert data.get_editor_property('PostProcessClass')==expected_class
    policies=[a for a in actors.get_all_level_actors() if isinstance(a,unreal.ParisAlliedGripPolicy)]
    if MODE=='author':
        early=read(BASE/'early_v2/result.json');assert early['status']=='passed_two_allies_and_future_native_binding' and not early['errors']
        assert read(BASE/'early_v2/image_review.json')['both_native_views_inspected']
        assert not policies and not any(isinstance(a,unreal.ParisNPCGripActor) for a in actors.get_all_level_actors())
        setup();assert levels.save_current_level();r['map_saved']=True;r['saved_files']=[row(MAP)]
        finish('saved_allied_policy_requires_fresh_verification')
    elif MODE=='audit':r.update(closure());finish('passed_saved_dependency_closure')
    else:
        if MODE=='early':assert not policies;setup()
        else:
            assert len(policies)==1 and policies[0].get_editor_property('BindingConfig')==data
            assert all(exact(f) for f in read(BASE/'author_v1/result.json')['saved_files'])
        unreal.EditorPythonScripting.set_keep_python_script_alive(True)
        callback=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play()
except Exception:r['errors'].append(traceback.format_exc());finish('failed_preserve_state')
