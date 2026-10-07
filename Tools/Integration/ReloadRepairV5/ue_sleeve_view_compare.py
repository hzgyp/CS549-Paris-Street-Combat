"""Frozen same-view old/new skin comparison. No stopped owner authoring or transactions."""
import json,os,sys,time,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import ROOT,STORE,records,check
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from ue_player_actions_stage import stage_actions_actor
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ['CS549_RELOAD_V5_IDENTITY'];assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes());rows=records(True)
SOURCE='/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1'
OLD='/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3'
NEW='/Game/ParisCombat/Characters/ReloadRepairV5/SK_PC_SleeveWeightsV5'
CLIP='/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1'
GUN='/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'
relative=json.loads((STORE/'Evidence/ReloadContactBindingV3/binding_proof_author_v2/result.json').read_text())['audit_phase0_hand_relative']
r={'scope':__doc__,'status':'starting','errors':[],'captures':[],'map_saved':False,'native_authored':False,
   'runtime_control':'native component animation/leader/attachment; explicit frozen phase setup only',
   'limitations':['fixed unchanged ordinary-holding frame; no full reload lifecycle or movement/return integration',
                 'old failed D059 derivative is a diagnostic source, not selected production content']}
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
callback=None;ending=ready=None;start=time.monotonic();busy=False;phase=-1;version=0;pending=None;world=player=owner=driver=None
display=[];guns=[];phases=[0.,1.2,2.2,3.4,4.1]
def xyz(v):return [v.x,v.y,v.z]
def tr(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w]}
def make_t(row):
    t=unreal.Transform();t.translation=unreal.Vector(*row['t']);t.rotation=unreal.Quat(*row['q']);t.scale3d=unreal.Vector(*row.get('s',[1,1,1]));return t
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def snap():
    a=display[0].skeletal_mesh_component;b=display[1].skeletal_mesh_component;p=driver.skeletal_mesh_component;camera=player.get_editor_property('ParisPlayerCamera')
    deltas={n:(a.get_socket_location(n)-b.get_socket_location(n)).length() for n in ('hand_l','hand_r','index_03_r','thumb_03_r','upperarm_l','upperarm_r')}
    assert max(deltas.values())<.01,deltas
    assert xyz(camera.get_editor_property('relative_location'))==[25.,0.,60.] and abs(camera.get_editor_property('field_of_view')-90)<1e-6
    assert a.get_editor_property('leader_pose_component')==p and b.get_editor_property('leader_pose_component')==p
    assert a.get_skeletal_mesh_asset().get_path_name()==OLD+'.'+OLD.rsplit('/',1)[-1]
    assert b.get_skeletal_mesh_asset().get_path_name()==NEW+'.'+NEW.rsplit('/',1)[-1]
    gun_delta=(guns[0].get_actor_location()-guns[1].get_actor_location()).length();assert gun_delta<.01
    return {'phase':phases[phase],'version':('before','after')[version],'pose_position':p.get_position(),'socket_delta_cm':deltas,
       'display_meshes':[a.get_skeletal_mesh_asset().get_path_name(),b.get_skeletal_mesh_asset().get_path_name()],'gun_pair_delta_cm':gun_delta,
       'camera_relative':xyz(camera.get_editor_property('relative_location')),'fov':camera.get_editor_property('field_of_view'),
       'camera_world':tr(camera.get_socket_transform('',unreal.RelativeTransformSpace.RTS_WORLD)),
       'display_world':tr(display[version].get_actor_transform()),'gun_world':tr(guns[version].get_actor_transform()),
       'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
       'display_lod':[a.get_predicted_lod_level(),b.get_predicted_lod_level()]}
def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    r['protected_count']=len(rows);r['protected_records_unchanged']=check(rows)
    r['status']='failed_preserve_stop' if r['errors'] else 'same_phase_fp_views_collected_requires_visual_review'
    write();levels.editor_request_end_play();ending=time.monotonic()
def visibility():
    for i in range(2):display[i].set_actor_hidden_in_game(i!=version);guns[i].set_actor_hidden_in_game(i!=version)
def enter():
    global pending
    p=driver.skeletal_mesh_component;p.set_position(phases[phase],False);p.set_play_rate(0.);visibility();pending={'stage':'refresh','wall':time.monotonic()}
def init():
    global driver,display,guns
    allactors=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)
    bylabel={a.get_actor_label():a for a in allactors}
    driver=bylabel['PC_SleeveDriverV5'];display=[bylabel['PC_SleeveBeforeV5'],bylabel['PC_SleeveAfterV5']];guns=[bylabel['PC_SleeveGunBeforeV5'],bylabel['PC_SleeveGunAfterV5']]
    source=owner.get_editor_property('PoseMesh');source_t=source.get_socket_transform('',unreal.RelativeTransformSpace.RTS_WORLD);view_t=owner.get_actor_transform()
    r['fixed_source_world']=tr(source_t);r['fixed_display_world']=tr(view_t)
    owner.set_actor_hidden_in_game(True)
    for prop in ('DisplayGun','PoseGun'):
        gun=owner.get_editor_property(prop)
        if gun:gun.set_actor_hidden_in_game(True)
    driver.set_actor_transform(source_t,False,True);p=driver.skeletal_mesh_component
    p.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
    p.set_hidden_in_game(True);p.play_animation(unreal.load_asset(CLIP),False);p.set_play_rate(0.)
    for a,g in zip(display,guns):
        a.set_actor_transform(view_t,False,True);c=a.skeletal_mesh_component;c.set_leader_pose_component(p,True,False);c.add_tick_prerequisite_component(p);c.set_forced_lod(1)
        assert g.attach_to_component(c,'hand_r',unreal.AttachmentRule.SNAP_TO_TARGET,unreal.AttachmentRule.SNAP_TO_TARGET,unreal.AttachmentRule.SNAP_TO_TARGET,False),'Native gun attach failed'
        g.root_component.set_relative_transform(make_t(relative),False,False)
        assert g.root_component.get_attach_parent()==c and str(g.root_component.get_attach_socket_name())=='hand_r'
    unreal.GameplayStatics.set_global_time_dilation(world,.0001)
def tick(delta):
    global busy,world,player,owner,ready,phase,version,pending
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>2:unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<210,'Bounded visual deadline'
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        owner=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_ActionOwnerViewTrial'),None)
        if not owner or not owner.get_editor_property('Initialized'):return
        if ready is None:ready=time.monotonic();return
        if phase<0:
            if time.monotonic()-ready<10:return
            init();phase=0;enter();return
        if pending['stage']=='refresh':
            if time.monotonic()-pending['wall']<.8:return
            sample=snap();assert abs(sample['pose_position']-phases[phase])<1e-5
            file='phase_'+str(phases[phase])+'_'+('before','after')[version]+'.png';r['captures'].append({'file':file,'before':sample});write()
            controller=unreal.GameplayStatics.get_player_controller(world,0)
            unreal.SystemLibrary.execute_console_command(world,'HighResShot 1280x720 filename="'+(OUT/file).as_posix()+'"',controller)
            pending={'stage':'file','wall':time.monotonic()};return
        if time.monotonic()-pending['wall']<1.2:return
        assert (OUT/r['captures'][-1]['file']).is_file();r['captures'][-1]['after']=snap();write()
        if version==0:version=1;visibility();pending={'stage':'refresh','wall':time.monotonic()}
        elif phase+1<len(phases):version=0;phase+=1;enter()
        else:finish()
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    assert check(rows) and not hasattr(unreal,'ParisBlueprintAuthoring')
    r['staging'],staged,old=stage_actions_actor()
    for label,mesh in (('PC_SleeveDriverV5',SOURCE),('PC_SleeveBeforeV5',OLD),('PC_SleeveAfterV5',NEW)):
        a=actors.spawn_actor_from_class(unreal.SkeletalMeshActor,staged.get_actor_location(),unreal.Rotator());a.set_actor_label(label);c=a.skeletal_mesh_component
        c.set_skeletal_mesh_asset(unreal.load_asset(mesh));c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        a.set_actor_hidden_in_game(True)
    for label in ('PC_SleeveGunBeforeV5','PC_SleeveGunAfterV5'):
        a=actors.spawn_actor_from_class(unreal.StaticMeshActor,staged.get_actor_location(),unreal.Rotator());a.set_actor_label(label);a.static_mesh_component.set_static_mesh(unreal.load_asset(GUN));a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);a.set_actor_hidden_in_game(True)
        a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True);callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_startup';r['protected_count']=len(rows);r['protected_records_unchanged']=check(rows);write();unreal.SystemLibrary.quit_editor()
