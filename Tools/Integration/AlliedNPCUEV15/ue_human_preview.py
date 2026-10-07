"""One-time preparation for a user-owned Allied native candidate viewing."""
import builtins,os,sys,time,traceback,math
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import *
import transform_math as tm
import human_controls

identity=os.environ['CS549_ALLIED_HUMAN_ID']
assert identity.replace('_','').isalnum()
OUT=BASE/identity;assert not OUT.exists();OUT.mkdir(parents=True)
write(OUT/'entry_sources.json',{p.name:sha(p) for p in
    (Path(__file__),Path(__file__).parent/'human_controls.py')})
r={'identity':identity,'pid':os.getpid(),'status':'starting','errors':[],
    'map_saved':False,'selected':False,'automated_actions':False,
    'python_pose_updates':0,'python_preparation_unregistered':False,'human_acceptance':False}
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
callback=None;busy=False;settled=bound=None;start=time.monotonic()
soldier=gun=wrapper=None

def unregister():
    global callback
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback);callback=None
    r['python_preparation_unregistered']=True

def stop():
    r['errors'].append(traceback.format_exc());r['status']='stopped_preparation'
    unregister()
    try:r['guards_after']=guards(False)
    except Exception:r['errors'].append(traceback.format_exc())
    write(OUT/'result.json',r)
    if editor.get_game_world():levels.editor_request_end_play()
    unreal.log_error('Allied human preparation stopped; no save. '+r['errors'][-1])

def tick(delta):
    global busy,settled,bound,soldier,gun,wrapper
    if busy:return
    busy=True
    try:
        assert time.monotonic()-start<240,'Human preparation deadline'
        world=editor.get_game_world()
        player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        if settled is None:settled=time.monotonic();return
        if time.monotonic()-settled<12:return
        if bound is None:
            soldier=human_controls.current();gun=soldier.get_editor_property('WeaponAppearance')
            assert gun and gun.get_editor_property('GripMesh')==soldier.mesh
            wrapper=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor)
                         if a.get_actor_label()=='PC_AlliedHumanV16')
            wrapper.set_editor_property('Target',soldier)
            bound=time.monotonic();return
        if time.monotonic()-bound<3:return
        pp=soldier.mesh.get_post_process_instance()
        assert pp and pp.get_class()==expected_class
        native={n:wrapper.get_editor_property(n) for n in
                ('Initialized','BindingError','NativeUpdates','PendingEvaluationFrames')}
        native={n:(str(v) if n=='BindingError' else v) for n,v in native.items()}
        native['evaluations']=pp.get_editor_property('Evaluations')
        native['valid_input']=pp.get_editor_property('ValidInput')
        native['protection_error']=pp.get_editor_property('ProtectionError')
        mesh=gun.get_component_by_class(unreal.StaticMeshComponent)
        relation=unreal.MathLibrary.make_relative_transform(mesh.get_world_transform(),soldier.mesh.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD))
        native['gun_error_cm']=math.dist([relation.translation.x,relation.translation.y,relation.translation.z],cfg['gun_hand_relative']['t'])
        native['gun_error_deg']=tm.angle([relation.rotation.x,relation.rotation.y,relation.rotation.z,relation.rotation.w],cfg['gun_hand_relative']['q'])
        native['ammo']=[int(soldier.get_editor_property(n)) for n in ('LoadedAmmo','ReserveAmmo')]
        native['original_weapon_preserved']=soldier.get_editor_property('WeaponAppearance')==gun
        native['original_source_preserved']=gun.get_editor_property('GripMesh')==soldier.mesh
        assert native['Initialized'] and not native['BindingError'] and native['NativeUpdates']>0,native
        assert native['evaluations']>0 and native['valid_input'] and native['protection_error']<.0001,native
        assert native['gun_error_cm']<.01 and native['gun_error_deg']<.01,native
        assert native['original_weapon_preserved'] and native['original_source_preserved'],native
        controller=unreal.GameplayStatics.get_player_controller(world,0);assert controller
        camera=player.get_editor_property('ParisPlayerCamera')
        before=camera.get_editor_property('relative_location')
        fov=camera.get_editor_property('field_of_view')
        original=player.get_actor_location()
        desired=soldier.get_actor_location()+soldier.get_actor_right_vector()*250
        player.set_actor_location(desired,True,False)
        controller.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_world_location(),soldier.mesh.get_socket_location('spine_03')))
        after=camera.get_editor_property('relative_location')
        assert (after-before).length()<1e-6 and camera.get_editor_property('field_of_view')==fov
        r['player_view_setup']={'before_cm':[original.x,original.y,original.z],
            'after_cm':[player.get_actor_location().x,player.get_actor_location().y,player.get_actor_location().z],
            'distance_to_npc_cm':(player.get_actor_location()-soldier.get_actor_location()).length(),
            'camera_relative_preserved':True,'npc_actor':soldier.get_name()}
        r['native_ready']=native;r['guards_after']=guards(False)
        for row in draft['files']:
            assert sha(ROOT/row['path'])==row['sha256']
        builtins.npc=human_controls
        unregister();r['status']='ready_user_owned';write(OUT/'result.json',r)
        unreal.log('ALLIED HUMAN READY: WASD/mouse inspect NPC; console py npc.reload() / py npc.fire(); Escape ends PIE; do not save. Preparation unregistered.')
    except Exception:stop()
    finally:busy=False

try:
    r['guards_before']=guards(False)
    closure=read(BASE/'closure_v17/result.json')
    for row in closure['compiled_source_exact']:assert sha(ROOT/row['path'])==row['sha256']
    build=ROOT/'tmp/allied-npc-ue-v15/Build_cpp_lifecycle17'
    for p in (PLUGIN/'Binaries').rglob('*'):
        if p.is_file():assert sha(p)==sha(build/p.relative_to(PLUGIN))
    draft=read(BASE/'draft_asset_read_v17/result.json');assert not draft['errors']
    for row in draft['files']:assert sha(ROOT/row['path'])==row['sha256']
    cfg_path=BASE/'preflight_v16/binding.json'
    assert sha(cfg_path)==draft['config_sha256'];cfg=read(cfg_path)
    data=unreal.load_asset('/Game/ParisCombat/Animation/AlliedGripV15/DA_PC_AlliedGripV16');assert data
    assert data.get_editor_property('BindingJson')==cfg_path.read_text()
    expected_class=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Animation/AlliedGripV15/ABP_PC_AlliedGripPostV16')
    assert data.get_editor_property('PostProcessClass')==expected_class
    actor=actors.spawn_actor_from_class(unreal.ParisNPCGripActor,unreal.Vector(),unreal.Rotator());assert actor
    actor.set_actor_label('PC_AlliedHumanV16');actor.set_editor_property('BindingConfig',data)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick)
    write(OUT/'result.json',r);levels.editor_request_begin_play()
except Exception:stop()
