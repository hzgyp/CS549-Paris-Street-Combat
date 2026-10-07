"""Fresh native existing-pose crossfade. Single command; Python observes, never interpolates."""
import hashlib,json,os,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ['CS549_RELOAD_V5_IDENTITY'];assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
proof=json.loads((STORE/'Evidence/ReloadRepairV5/transition_proof_author_v2/result.json').read_text());assert not proof['errors']
rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())['files']
rows+=json.loads((STORE/'Evidence/ReloadRepairV5/blend_capability_v2/result.json').read_text())['packages']+proof['packages']
def guard():return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in rows)
def xyz(v):return [v.x,v.y,v.z]
def tr(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w]}
BONES=('hand_r','hand_l','lowerarm_r','lowerarm_l','index_03_r','thumb_03_r')
def bones(m):return {n:tr(m.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT)) for n in BONES}
def error(a,b):
    positional=max(sum((a[n]['t'][i]-b[n]['t'][i])**2 for i in range(3))**.5 for n in BONES)
    # Quaternion sign is immaterial.
    angular=max(min(sum((a[n]['q'][i]-b[n]['q'][i])**2 for i in range(4))**.5,
                    sum((a[n]['q'][i]+b[n]['q'][i])**2 for i in range(4))**.5) for n in BONES)
    return {'position_cm':positional,'quaternion_distance':angular}
r={'status':'starting','errors':[],'samples':[],'map_saved':False,'native_authored':False,
   'runtime_control':'BlueprintUpdateAnimation FInterpConstantTo; one native target command only',
   'selection':'diagnostic temporal proof, not target FP/contact/framing/gameplay acceptance'}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
wall_start=time.monotonic();ending=None;ready=None;request=None;finished=None;last=None;busy=False;callback=None
def finish(message=None):
    global ending
    if ending is not None:return
    if message:r['errors'].append(message)
    r['protected_516_unchanged']=guard();r['status']='failed_preserve_stop' if r['errors'] else 'native_crossfade_proof_pass_target_integration_pending'
    write();levels.editor_request_end_play();ending=time.monotonic()
def tick(delta):
    global ready,request,finished,last,busy
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>2:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-wall_start<150,'Bounded startup/proof timeout'
        world=editor.get_game_world()
        if not world:return
        actors={str(a.get_actor_label()):a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor)}
        if not all('V5Blend_'+n in actors for n in ('blend','idle','reload')):return
        mesh={n:actors['V5Blend_'+n].skeletal_mesh_component for n in ('blend','idle','reload')}
        inst=mesh['blend'].get_anim_instance();assert inst
        now=unreal.GameplayStatics.get_time_seconds(world)
        if ready is None:
            # PlayAnimation/SetPosition act on transient instances, not serialized
            # actor defaults. Initialize reference-only instances after PIE duplication.
            for label in ('idle','reload'):
                clip=unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle' if label=='idle' else '/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1')
                mesh[label].play_animation(clip,False)
                mesh[label].set_position(0. if label=='idle' else clip.get_play_length(),False)
                mesh[label].set_play_rate(0.)
            r['reference_runtime_initialization']='one-time after PIE; reference actors only, never blend updater'
            ready=now;return
        if now-ready<.6:return
        if request is None:
            r['start_weight']=float(inst.get_editor_property('ReloadWeight'))
            r['start_pose']=bones(mesh['blend']);r['reload_reference']=bones(mesh['reload'])
            r['reference_states']={n:{'position':mesh[n].get_position(),
                 'asset':mesh[n].get_anim_instance().get_animation_asset().get_path_name()} for n in ('idle','reload')}
            r['start_endpoint_error']=error(r['start_pose'],r['reload_reference'])
            assert r['start_weight']==1.
            assert r['start_endpoint_error']['position_cm']<.01,r['start_endpoint_error']
            assert r['start_endpoint_error']['quaternion_distance']<.001,r['start_endpoint_error']
            inst.call_method('PC_SetTransitionTarget',args=(0.,));request=now;write()
        if last!=now:
            r['samples'].append({'seconds':now-request,'weight':float(inst.get_editor_property('ReloadWeight')),'bones':bones(mesh['blend'])});last=now
        weight=float(inst.get_editor_property('ReloadWeight'))
        if weight==0.:
            if finished is None:finished=now;r['completed_after_s']=now-request;write()
            elif now-finished>.25:
                r['end_pose']=bones(mesh['blend']);r['idle_reference']=bones(mesh['idle'])
                r['end_endpoint_error']=error(r['end_pose'],r['idle_reference'])
                assert r['end_endpoint_error']['position_cm']<.01,r['end_endpoint_error']
                assert r['end_endpoint_error']['quaternion_distance']<.001,r['end_endpoint_error']
                assert any(0<s['weight']<1 for s in r['samples']),'No actual intermediate poses observed'
                assert all(a['weight']>=b['weight'] for a,b in zip(r['samples'],r['samples'][1:]))
                finish();return
        assert now-request<2,'Native blend did not finish'
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    assert guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    cls=unreal.EditorAssetLibrary.load_blueprint_class(proof['packages'][0]['package']);assert cls
    actor_subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world=editor.get_editor_world()
    world.get_world_settings().set_editor_property('default_game_mode',unreal.GameModeBase.static_class())
    model=unreal.load_asset('/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1')
    for i,label in enumerate(('blend','idle','reload')):
        actor=actor_subsystem.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(i*200,0,0));assert actor
        actor.set_actor_label('V5Blend_'+label);mesh=actor.skeletal_mesh_component
        mesh.set_skeletal_mesh_asset(model);mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        mesh.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        if label=='blend':mesh.set_anim_instance_class(cls)
        else:
            clip=unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle' if label=='idle' else '/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1')
            mesh.play_animation(clip,False);mesh.set_position(0. if label=='idle' else clip.get_play_length(),False);mesh.set_play_rate(0.)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['status']='failed_startup';r['errors'].append(traceback.format_exc());r['protected_516_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
