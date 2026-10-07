"""New formal-selection entry; native auto-binding only, Python observes/authoring only."""
import math
import os
import time
import traceback
import sys
from collections import deque
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from formal_common import *

MODE = os.environ['CS549_FORMAL_FP_MODE']
IDENTITY = os.environ['CS549_FORMAL_FP_ID']
assert MODE in ('early','author','fresh','audit')
assert IDENTITY.replace('_','').isalnum()
OUT = BASE/IDENTITY
assert not OUT.exists(); OUT.mkdir(parents=True)
write(OUT/'entry_source.json', {'sha256':sha(Path(__file__)), 'mode':MODE})
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
r = {'mode':MODE, 'status':'starting', 'pid':os.getpid(), 'errors':[], 'samples':[],
     'engine':unreal.SystemLibrary.get_engine_version(),
     'python_binding_calls':0, 'source_motion_changed':False, 'map_saved':False,
     'full_return_gate':False, 'sleeve_gate':False, 'lifecycle_gate':False, 'fps_gate':False}
callback = None
busy = False
start = time.monotonic()
phase = 0
phase_start = None
ending = None
move_start_updates = None


def finish(status):
    global callback
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback); callback = None
    r['status'] = status; r['guards_after'] = check_protected(MODE in ('author','fresh','audit'))
    if r['guards_after']['mismatches']: r['errors'].append(str(r['guards_after']))
    write(OUT/'result.json', r)
    if editor.get_game_world(): levels.editor_request_end_play()
    unreal.SystemLibrary.quit_editor()


def setup_actor(config):
    display = actors.spawn_actor_from_class(unreal.ParisFirstPersonApprovedActor, unreal.Vector(), unreal.Rotator())
    assert display
    display.set_actor_label(LABEL)
    data = read(CONFIG)
    selection = read(STORE/'Evidence/FPUpperBodyV19/holding_selection_v1/selection.json')
    assert selection['compatible_existing_clip'] and exact(selection['source_inventory'])
    for key, value in [('BindingConfig',config),('DisplayMesh',unreal.load_asset(data['source_mesh'])),
        ('RifleMesh',unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand')),
        ('HoldingClip',unreal.load_asset(selection['clip_path']))]:
        assert value; display.set_editor_property(key,value)
    return display


def angle(q, expected):
    actual = [q.x,q.y,q.z,q.w]
    dot = abs(sum(a*b for a,b in zip(actual,expected))/math.sqrt(sum(a*a for a in actual)*sum(b*b for b in expected)))
    return math.degrees(2*math.acos(max(-1,min(1,dot))))


def snapshot(display, player, name):
    config = read(CONFIG)
    camera = player.get_editor_property('ParisPlayerCamera')
    pose = display.get_editor_property('Pose'); gun = display.get_editor_property('Gun')
    rel = camera.get_editor_property('relative_location')
    errors = {}
    for bone,item in config['fingers_local'].items():
        local = unreal.MathLibrary.make_relative_transform(pose.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT),
            pose.get_socket_transform(pose.get_parent_bone(bone),unreal.RelativeTransformSpace.RTS_COMPONENT))
        errors[bone] = angle(local.rotation,item['q'])
    original = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(editor.get_game_world(), unreal.SkeletalMeshActor)
        if a.get_actor_label() == 'PC_Player_ContinuousArmsNativeV1')
    gun_hand = unreal.MathLibrary.make_relative_transform(gun.get_world_transform(),pose.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD))
    return {'name':name, 'initialized':bool(display.get_editor_property('Initialized')),
        'state':str(display.get_editor_property('SetupState')), 'error':str(display.get_editor_property('BindingError')),
        'updates':int(display.get_editor_property('NativePoseUpdates')), 'action':str(player.get_editor_property('ActionState')),
        'holding_alpha':float(display.get_editor_property('HoldingAppliedAlpha')), 'finger_q_error_degrees':errors,
        'gun_hand_translation_error_cm':(gun_hand.translation-unreal.Vector(*config['gun_hand_relative']['t'])).length(),
        'gun_hand_angle_error_degrees':angle(gun_hand.rotation,config['gun_hand_relative']['q']),
        'support_cm':float(display.get_editor_property('SupportErrorCm')), 'limb_cm':float(display.get_editor_property('LimbLengthErrorCm')),
        'camera_cm':[rel.x,rel.y,rel.z], 'fov':float(camera.get_editor_property('field_of_view')),
        'gun_socket':str(gun.get_attach_socket_name()), 'old_visual_hidden':bool(original.get_editor_property('hidden')),
        'original_weapon_preserved':player.get_editor_property('WeaponAppearance')==original.get_editor_property('DisplayGun'),
        'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
        'commits':int(player.get_editor_property('ReloadCommitCount')), 'speed_cm_s':player.get_velocity().length()}


def ready_check(s):
    assert s['initialized'] and not s['error'] and s['updates']>0 and s['state']=='NativeApprovedDisplayReady',s
    assert s['action']=='Ready' and s['holding_alpha']>.9999 and max(s['finger_q_error_degrees'].values())<.01,s
    assert s['gun_hand_translation_error_cm']<.001 and s['gun_hand_angle_error_degrees']<.01,s
    assert s['support_cm']<.001 and s['limb_cm']<.001,s
    assert max(abs(a-b) for a,b in zip(s['camera_cm'],[25,0,60]))<1e-6 and abs(s['fov']-90)<1e-6,s
    assert s['gun_socket']=='hand_r' and s['original_weapon_preserved'] and s['old_visual_hidden'],s


def tick(delta):
    global busy,phase,phase_start,ending,move_start_updates
    if busy:return
    busy = True
    try:
        if ending is not None:
            if time.monotonic()-ending>3:
                assert all((OUT/(s['name']+'.png')).is_file() for s in r['samples']),'Actual native screenshots missing'
                if MODE=='fresh':
                    # Runtime observations are finished. This separate saved-package
                    # read-only audit is not timed as an action/continuity sample.
                    audit_out=BASE/'audit_v1'
                    assert not audit_out.exists(),'Preserve occupied audit identity'
                    write(audit_out/'result.json',{**dependency_report(), 'mode':'audit', 'pid':os.getpid(),
                        'errors':[], 'guards_after':check_protected(True),
                        'engine':unreal.SystemLibrary.get_engine_version()})
                finish('passed_early_native_auto_bind' if MODE=='early' else 'passed_fresh_saved_native_regression')
            return
        assert time.monotonic()-start<240,'Formal test deadline'
        world = editor.get_game_world()
        player = unreal.GameplayStatics.get_player_character(world,0) if world else None
        if not player:return
        displays = unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFirstPersonApprovedActor)
        assert len(displays)==1,'Exactly one selected native first-person display required'
        display = displays[0]
        assert str(display.get_editor_property('SetupState'))!='Stopped',str(display.get_editor_property('BindingError'))
        if not display.get_editor_property('Initialized'):return
        if phase_start is None:phase_start=time.monotonic();return
        elapsed=time.monotonic()-phase_start
        if phase==0 and elapsed>3:
            s=snapshot(display,player,'ready');ready_check(s);assert s['ammo']==[2,16] and s['commits']==0,s
            r['samples'].append(s)
            unreal.SystemLibrary.execute_console_command(world,'HighResShot 1600x900 filename="'+(OUT/'ready.png').as_posix()+'"')
            if MODE=='early':ending=time.monotonic();return
            phase=1;phase_start=time.monotonic();move_start_updates=s['updates']
        elif phase==1:
            # Same native input stimulus as the retained V20 local test. Screenshot
            # latency is not movement time: require actual later native updates.
            player.add_movement_input(unreal.Vector(0,-1,0),1,True)
            if elapsed>1.5 and int(display.get_editor_property('NativePoseUpdates'))>=move_start_updates+4:
                s=snapshot(display,player,'left_walk');ready_check(s);assert 290<s['speed_cm_s']<310,s
                r['samples'].append(s)
                unreal.SystemLibrary.execute_console_command(world,'HighResShot 1600x900 filename="'+(OUT/'left_walk.png').as_posix()+'"')
                phase=2;phase_start=time.monotonic()
        elif phase==2 and elapsed>2:
            # Stimulate original authoritative action once; no source/transaction override.
            player.call_method('PC_RequestReload')
            phase=3;phase_start=time.monotonic()
        elif phase==3 and elapsed>6 and str(player.get_editor_property('ActionState'))=='Ready':
            s=snapshot(display,player,'reload_return');ready_check(s);assert s['ammo']==[8,10] and s['commits']==1,s
            r['samples'].append(s)
            unreal.SystemLibrary.execute_console_command(world,'HighResShot 1600x900 filename="'+(OUT/'reload_return.png').as_posix()+'"')
            ending=time.monotonic()
    except Exception:
        r['errors'].append(traceback.format_exc());finish('failed_preserve_state')
    finally:busy=False


def dependency_report():
    registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
    def closure(soft):
        seen={ENTRY};queue=deque([ENTRY]);edges={};external=set()
        opts=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=soft)
        while queue:
            p=queue.popleft();deps=sorted(str(d) for d in registry.get_dependencies(p,opts));edges[p]=deps
            for d in deps:
                if d.startswith('/Game/') and d not in seen:seen.add(d);queue.append(d)
                elif not d.startswith('/Game/'):external.add(d)
        return seen,edges,external
    seen,edges,external=closure(True);hard,_,_=closure(False)
    files=[];missing=[]
    for package in sorted(seen):
        stem=ROOT/'Unreal/ParisStreetCombat/Content'/package.removeprefix('/Game/')
        paths=[Path(str(stem)+s) for s in ('.uasset','.umap') if Path(str(stem)+s).is_file()]
        if len(paths)!=1:missing.append(package);continue
        files.append({**row(paths[0]),'package':package})
    result={'status':'passed_saved_dependency_closure_with_recorded_soft_gaps' if missing else 'passed_saved_dependency_closure',
        'files':files,'edges':edges,'external_dependencies':sorted(external),'missing_packages':missing,
        'hard_missing_packages':sorted(set(missing)&hard),'missing_referencers':{p:sorted(k for k,d in edges.items() if p in d) for p in missing}}
    assert PACKAGE in seen and not result['hard_missing_packages'],result['hard_missing_packages']
    return result


try:
    assert sha(CONFIG)==CONFIG_SHA
    r['guards_before']=check_protected(MODE in ('fresh','audit'));assert not r['guards_before']['mismatches']
    before=read(BASE/'preflight_v1/result.json')
    assert all(exact(f) for f in before['old_algorithms']) and exact(before['accepted_source'])
    assert hasattr(unreal,'ParisFirstPersonApprovedActor') and not hasattr(unreal,'ParisBlueprintAuthoring')
    if MODE=='audit':
        report=dependency_report();r.update(report);finish(report['status'])
    elif MODE=='author':
        early=read(BASE/'early_v2/result.json');assert early['status']=='passed_early_native_auto_bind' and not early['errors']
        image_review=read(BASE/'early_v2/image_review.json');assert image_review['actual_ready_view_inspected']
        assert not unreal.EditorAssetLibrary.does_asset_exist(PACKAGE)
        assert not any(isinstance(a,unreal.ParisFirstPersonApprovedActor) for a in actors.get_all_level_actors())
        factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.ParisGripV18Config)
        config=unreal.AssetToolsHelpers.get_asset_tools().create_asset(PACKAGE.rsplit('/',1)[1],PACKAGE.rsplit('/',1)[0],unreal.ParisGripV18Config,factory)
        assert config;config.set_editor_property('BindingJson',CONFIG.read_text())
        assert unreal.EditorAssetLibrary.save_loaded_asset(config,False)
        setup_actor(config);assert levels.save_current_level();r['map_saved']=True
        r['saved_files']=[row(ROOT/MAP),row(ROOT/'Unreal/ParisStreetCombat/Content'/ (PACKAGE.removeprefix('/Game/')+'.uasset'))]
        finish('saved_selected_requires_fresh_reopen')
    else:
        if MODE=='early':
            config=unreal.new_object(unreal.ParisGripV18Config);config.set_editor_property('BindingJson',CONFIG.read_text())
            setup_actor(config)
        else:
            assert len([a for a in actors.get_all_level_actors() if isinstance(a,unreal.ParisFirstPersonApprovedActor)])==1
            saved=unreal.load_asset(PACKAGE);assert saved.get_editor_property('BindingJson')==CONFIG.read_text()
            assert all(exact(f) for f in read(BASE/'author_v1/result.json')['saved_files'])
        unreal.EditorPythonScripting.set_keep_python_script_alive(True)
        callback=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());finish('failed_preserve_state')
