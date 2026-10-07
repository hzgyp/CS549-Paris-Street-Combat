"""Matched frozen actual-city viewport evidence separate from native motion tests."""
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from weapon_animation_reuse_common import STORE,RELOAD,SHOOT,output,guard
from ue_weapon_animation_stage import stage_candidate
OUT=output(os.environ['CS549_ANIMATION_IDENTITY'])
WITH_RECOIL=os.environ.get('CS549_ANIMATION_WITH_RECOIL')=='1'
r={'status':'starting','errors':[],'samples':[],'captures':[],'map_saved':False,
   'scope':'Actual target/rifle/protected-camera pose gate; frozen captures are not functional or continuous-motion acceptance'}
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
start=time.monotonic();ending=ready=None;callback=None;busy=False
world=player=view=controller=None;phase=-1;issued=False;shot_time=0;freeze_start=None
phases=[('holding',None),('reload_early',.4),('reload_take',1.2),('reload_operate',2.2),('reload_return',3.4),('reload_complete',3.98)]
if WITH_RECOIL:phases = [('holding',None),('recoil_start',.02),('recoil_peak',.1),('recoil_recover',.5),('holding_after',None)]


def write():
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')


def xyz(v):return [v.x,v.y,v.z]


def snapshot():
    cam=player.get_component_by_class(unreal.CameraComponent)
    mesh=view.get_editor_property('PoseMesh')
    gun=view.get_editor_property('DisplayGun')
    return {'phase':phases[phase][0],'state':str(player.get_editor_property('ActionState')),
        'body_position':player.mesh.get_position() if 'Reloading' in str(player.get_editor_property('ActionState')) else None,
        'pose_mode':str(view.get_editor_property('PoseMode')),
        'pose_position':mesh.get_position() if not 'Reload' in str(view.get_editor_property('PoseMode')) else None,
        'left_hand_world':xyz(view.skeletal_mesh_component.get_socket_location('hand_l')),
        'right_hand_world':xyz(view.skeletal_mesh_component.get_socket_location('hand_r')),
        'source_left_hand_world':xyz(mesh.get_socket_location('hand_l')),
        'gun_world':xyz(gun.get_actor_location()),
        'muzzle_world':xyz(unreal.MathLibrary.transform_location(gun.get_actor_transform(),unreal.Vector(0,83.23,0))),
        'camera_world':xyz(cam.get_world_location()),'camera_local':xyz(cam.get_editor_property('relative_location')),
        'fov':cam.get_editor_property('field_of_view'),
        'collision':str(gun.static_mesh_component.get_collision_enabled()),
        'loaded':player.get_editor_property('LoadedAmmo'),'reserve':player.get_editor_property('ReserveAmmo')}


def unfreeze():
    if world:
        player.mesh.set_editor_property('pause_anims',False)
        view.get_editor_property('PoseMesh').set_editor_property('pause_anims',False)
        player.mesh.set_play_rate(1)
        view.get_editor_property('PoseMesh').set_play_rate(1)
        unreal.GameplayStatics.set_global_time_dilation(world,1)


def enter(i):
    global phase,issued,shot_time,freeze_start
    unfreeze();phase=i;issued=False;freeze_start=None
    player.call_method('PC_ResetLifecycle')
    name,target=phases[phase]
    if name.startswith('reload'):player.call_method('PC_RequestReload')
    r.setdefault('entries',[]).append({'phase':name,'class':player.get_class().get_path_name(),
        'mesh':player.mesh.get_skeletal_mesh_asset().get_path_name(),
        'state':str(player.get_editor_property('ActionState')),
        'duration':player.get_editor_property('ReloadDuration'),
        'commit':player.get_editor_property('ReloadCommitTime'),
        'body_position':player.mesh.get_position(),
        'elapsed':player.get_editor_property('ReloadElapsed'),
        'timeout_count':player.get_editor_property('ReloadTimeoutCount')})
    if name.startswith('reload'):assert str(player.get_editor_property('ActionState'))=='Reloading',r['entries'][-1]
    if name.startswith('recoil'):
        player.call_method('PC_RequestFire',args=(player.get_actor_location()+unreal.Vector(0,0,60),unreal.Vector(0,0,1)))
    shot_time=unreal.GameplayStatics.get_time_seconds(world)


def finish(error=None):
    global ending
    if ending:return
    if error:r['errors'].append(error)
    unfreeze();r['protected_files_unchanged']=guard()
    r['status']='failed' if r['errors'] else 'matched_target_viewports_recorded_requires_image_review'
    write();ending=time.monotonic();levels.editor_request_end_play()


def tick(delta):
    global busy,world,player,view,controller,ready,callback,freeze_start,issued
    if busy:return
    busy=True
    try:
        if ending:
            if time.monotonic()-ending>3:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<300
        world=editor.get_game_world()
        player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        if ready is None:
            controller=unreal.GameplayStatics.get_player_controller(world,0)
            view=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_AnimationOwnerViewTrial')
            ready=time.monotonic();return
        if phase<0:
            if time.monotonic()-ready>18:enter(0)
            return
        name,target=phases[phase]
        elapsed=unreal.GameplayStatics.get_time_seconds(world)-shot_time
        if freeze_start is None:
            position=player.mesh.get_position() if name.startswith('reload') else view.get_editor_property('PoseMesh').get_position() if name.startswith('recoil') else elapsed
            if position<(target if target is not None else 1):return
            # Zero single-node playback speed, not PauseAnims on a leader.
            # Continue bone refresh/leader publication while holding the phase.
            player.mesh.set_play_rate(0)
            view.get_editor_property('PoseMesh').set_play_rate(0)
            unreal.GameplayStatics.set_global_time_dilation(world,.0001)
            freeze_start=time.monotonic();return
        if not issued and time.monotonic()-freeze_start>1.2:
            s=snapshot();r['samples'].append(s)
            s['elapsed']=player.get_editor_property('ReloadElapsed')
            s['timeout_count']=player.get_editor_property('ReloadTimeoutCount')
            assert s['camera_local']==[25,0,60] and abs(s['fov']-90)<1e-6
            if name.startswith('reload'):assert s['state']=='Reloading' and s['body_position']>=target
            file=name+'.png'
            unreal.SystemLibrary.execute_console_command(world,'HighResShot 1280x720 filename="'+(OUT/file).as_posix()+'"',controller)
            r['captures'].append({'file':file,'frozen_sample':s});write();issued=True;freeze_start=time.monotonic();return
        if issued and time.monotonic()-freeze_start>1.5:
            assert (OUT/(name+'.png')).is_file()
            if phase+1==len(phases):finish()
            else:enter(phase+1)
    except Exception:finish(traceback.format_exc())
    finally:busy=False


try:
    assert not hasattr(unreal,'ParisBlueprintAuthoring')
    r['staging'],_,_=stage_candidate(WITH_RECOIL)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_startup';write();unreal.SystemLibrary.quit_editor()
