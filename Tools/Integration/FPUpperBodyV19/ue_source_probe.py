"""Isolated socket-only existing-clip diagnostic; no native skin/vertex reads."""
import json,os,sys,time,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parents[1]/'GripBindingV18'))
from common import ROOT,STORE,guard,inventory
OUT=STORE/'Evidence/FPUpperBodyV19'/os.environ['CS549_FP_V19_ID']
assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
r={'status':'starting','errors':[],'samples':[],'guards_before':guard(),'saved_packages':[]}
assert not r['guards_before']['mismatches']
assetpaths=['/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle',
            '/Game/USParatrooper/Animation/ThirdPersonIdle',
            '/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Idle_IP'] if os.environ.get('CS549_FP_V19_PROBE')=='holding' else ['/Game/RifleAnimsetPro/Animations/InPlace/'+n for n in ['Rifle_Idle','Rifle_WalkFwdLoop','Rifle_StrafeLeftLoop','Rifle_RunFwdLoop','Rifle_StrafeRunLeftLoop']]
clips=[p.rsplit('/',1)[1] for p in assetpaths]
bones=['root','pelvis','spine_01','spine_02','spine_03','clavicle_r','upperarm_r','lowerarm_r','hand_r','clavicle_l','upperarm_l','lowerarm_l','hand_l']
phases=[(n,i/8) for n in range(len(clips)) for i in range(8)]
callback=None;start=time.monotonic();due=None;index=0;busy=False
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
mesh=None
runtime_ready=None
def tr(t):return {'t':[t.translation.x,t.translation.y,t.translation.z],'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':[t.scale3d.x,t.scale3d.y,t.scale3d.z]}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def finish(error=None):
    if error:r['errors'].append(error)
    r['guards_after']=guard();r['status']='stopped' if r['errors'] else 'existing_component_bones_sampled'
    r['input_inventory_after']=[inventory(p) for p in assetpaths]
    r['source_inputs_unchanged']=r['input_inventory_before']==r['input_inventory_after']
    r['max_phase_hand_shift_cm']=max(sum((a-b)**2 for a,b in zip(x['component']['hand_r']['t'],y['component']['hand_r']['t']))**.5 for x in r['samples'] for y in r['samples']) if r['samples'] else 0
    if r['max_phase_hand_shift_cm']<.01:r['errors'].append('No refreshed animation bone motion')
    r['status']='stopped' if r['errors'] else 'existing_component_bones_sampled'
    write();unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
def prepare():
    global due
    n,fraction=phases[index];clip=assets[n]
    mesh.play_animation(clip,True);mesh.set_play_rate(0)
    mesh.set_position(clip.get_play_length()*fraction,False)
    due=time.monotonic()+.35
def tick(delta):
    global index,busy,mesh,runtime_ready
    if busy:return
    busy=True
    try:
        assert time.monotonic()-start<90,'Socket diagnostic deadline'
        if mesh is None:
            world=editor.get_game_world()
            actor=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_V19SourceProbe'),None) if world else None
            if not actor:return
            mesh=actor.skeletal_mesh_component;runtime_ready=time.monotonic();return
        if due is None:
            if time.monotonic()-runtime_ready<5:return
            prepare();return
        if time.monotonic()<due:return
        n,fraction=phases[index]
        component={b:mesh.get_socket_transform(b,unreal.RelativeTransformSpace.RTS_COMPONENT) for b in bones}
        local={b:unreal.MathLibrary.make_relative_transform(component[b],mesh.get_socket_transform(mesh.get_parent_bone(b),unreal.RelativeTransformSpace.RTS_COMPONENT)) if str(mesh.get_parent_bone(b))!='None' else component[b] for b in bones}
        r['samples'].append({'clip':clips[n],'fraction':fraction,'position_s':mesh.get_position(),'component':{b:tr(t) for b,t in component.items()},'local':{b:tr(t) for b,t in local.items()}})
        write();index+=1
        if index==len(phases):finish()
        else:prepare()
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    assert not hasattr(unreal,'ParisBlueprintAuthoring')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor=actors.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(),unreal.Rotator())
    actor.set_actor_label('PC_V19SourceProbe')
    source=actor.skeletal_mesh_component
    source.set_skeletal_mesh_asset(unreal.load_asset('/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1'))
    source.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    source.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
    assets=[unreal.load_asset(p) for p in assetpaths];assert all(assets)
    r['input_inventory_before']=[inventory(p) for p in assetpaths]
    r['skeleton']=source.get_skeletal_mesh_asset().get_editor_property('skeleton').get_path_name()
    r['clip_skeletons']=[a.get_editor_property('skeleton').get_path_name() for a in assets]
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='startup_failed';write();unreal.SystemLibrary.quit_editor()
