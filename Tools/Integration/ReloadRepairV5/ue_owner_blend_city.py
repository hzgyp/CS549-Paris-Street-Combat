"""Unsaved actual-city reload: native pose, attachment and ammo; observer-only Python."""
import hashlib,json,math,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ['CS549_RELOAD_V5_IDENTITY'];assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(ROOT/'Tools/Integration'))
from ue_player_actions_stage import stage_actions_actor
AUTH_ID=os.environ.get('CS549_RELOAD_V5_CITY_AUTHOR','owner_reframe_author_v2')
assert AUTH_ID!='owner_blend_author_v1','AN004 stopped owner must not be rerun'
auth=json.loads((STORE/'Evidence/ReloadRepairV5'/AUTH_ID/'result.json').read_text());assert not auth['errors']
rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())['files']
for identity in ('blend_capability_v2','transition_proof_author_v2','owner_blend_author_v1'):
    rows+=json.loads((STORE/'Evidence/ReloadRepairV5'/identity/'result.json').read_text())['packages']
rows+=auth['packages']
def guard():return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in rows)
def xyz(v):return [v.x,v.y,v.z]
def tr(t):return {'t':xyz(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w]}
MODE=os.environ.get('CS549_RELOAD_V5_CITY_MODE','natural');assert MODE in ('natural','visual')
r={'status':'starting','mode':MODE,'errors':[],'samples':[],'map_saved':False,'native_authored':False,
   'runtime_control':'new native AnimBP/owner/gun only; Python issues one reload and observes',
   'open_defects':['RLD-01','RLD-02'],'captures':[]}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
callback=None;ending=None;ready=None;requested=None;returned=None;last_sample=-1.;busy=False;wall_start=time.monotonic()
world=player=owner=pose=None;capture_phase=0;capture_wall=None
def snap(now):
    display=owner.skeletal_mesh_component;inst=pose.get_anim_instance();gun=owner.get_editor_property('DisplayGun');cam=player.get_editor_property('ParisPlayerCamera')
    leader=display.get_editor_property('leader_pose_component')
    return {'game_seconds':now,'elapsed_request':now-requested if requested is not None else None,
        'action_state':str(player.get_editor_property('ActionState')),'pose_mode':str(owner.get_editor_property('PoseMode')),
        'weight':float(inst.get_editor_property('ReloadWeight')),'pose_seconds':float(inst.get_editor_property('ReloadSeconds')),
        'idle_seconds':float(inst.get_editor_property('IdleSeconds')),
        'display_leader':leader.get_path_name() if leader else None,'pose_component':pose.get_path_name(),
        'pose_leader':str(pose.get_editor_property('leader_pose_component')),
        'display_world':tr(owner.get_actor_transform()),'gun_world':tr(gun.get_actor_transform()),
        'framing':tr(owner.get_editor_property('FramingT')),
        'right_wrist':xyz(display.get_socket_location('hand_r')),'left_wrist':xyz(display.get_socket_location('hand_l')),
        'index03':xyz(display.get_socket_location('index_03_r')),
        'camera_relative':xyz(cam.get_editor_property('relative_location')),'fov':cam.get_editor_property('field_of_view'),
        'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
        'commits':int(player.get_editor_property('ReloadCommitCount'))}
def assess():
    assert r['samples'] and returned is not None
    before=r['before_request'];after=r['samples'][-1]
    assert before['ammo']==[2,16] and after['ammo']==[8,10],(before['ammo'],after['ammo'])
    assert after['commits']-before['commits']==1
    assert after['action_state']=='Ready' and after['weight']==0.
    assert all(s['display_leader']==s['pose_component'] and s['pose_leader']=='None' for s in r['samples'])
    assert all(s['camera_relative']==[25.,0.,60.] and abs(s['fov']-90)<1e-6 for s in r['samples'])
    pairs=[]
    for a,b in zip(r['samples'],r['samples'][1:]):
        dt=b['game_seconds']-a['game_seconds']
        if returned-.08<=b['game_seconds']<=returned+.5 and 0<dt<=.06:
            pairs.append({'seconds':b['elapsed_request'],'dt':dt,'weight':b['weight'],
                'gun_cm':math.dist(a['gun_world']['t'],b['gun_world']['t']),
                'wrist_cm':math.dist(a['right_wrist'],b['right_wrist']),
                'state':b['action_state']})
    assert len(pairs)>=5,'Insufficient bounded consecutive end samples'
    r['end_pairs']=pairs;r['max_end_gun_step_cm']=max(p['gun_cm'] for p in pairs);r['max_end_wrist_step_cm']=max(p['wrist_cm'] for p in pairs)
    write()
    assert r['max_end_gun_step_cm']<=3. and r['max_end_wrist_step_cm']<=3.,'End-step gate failed; stop this integration'
def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    r['protected_records_unchanged']=guard();r['protected_count']=len(rows)
    r['status']='failed_preserve_stop' if r['errors'] else ('frozen_visual_collected_requires_review' if MODE=='visual' else 'stationary_natural_continuity_pass_not_full_visual_regression')
    write();levels.editor_request_end_play();ending=time.monotonic()
def tick(delta):
    global busy,world,player,owner,pose,ready,requested,returned,last_sample,capture_phase,capture_wall
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>2:
                unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-wall_start<210,'Bounded startup/runtime deadline'
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        owner=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_ReloadBlendOwnerV5'),None)
        if not owner or not owner.get_editor_property('Initialized'):return
        pose=owner.get_editor_property('PoseMesh')
        if ready is None:ready=time.monotonic();return
        if time.monotonic()-ready<8:return
        now=unreal.GameplayStatics.get_time_seconds(world)
        if requested is None:
            r['before_request']=snap(now);player.call_method('PC_ActionReload');requested=now
            assert str(player.get_editor_property('ActionState'))=='Reloading';write()
        if MODE=='visual':
            # Separate diagnostic only. Does not pretend to be the natural-cycle test.
            if capture_phase==0 and str(player.get_editor_property('ActionState'))=='Ready' and now-requested>1:
                unreal.GameplayStatics.set_global_time_dilation(world,.0001);capture_wall=time.monotonic();capture_phase=1
            elif capture_phase==1 and time.monotonic()-capture_wall>.7:
                sample=snap(now);r['captures'].append({'file':'return_blend.png','before':sample})
                controller=unreal.GameplayStatics.get_player_controller(world,0)
                unreal.SystemLibrary.execute_console_command(world,'HighResShot 1280x720 filename="'+(OUT/'return_blend.png').as_posix()+'"',controller)
                capture_wall=time.monotonic();capture_phase=2;write()
            elif capture_phase==2 and time.monotonic()-capture_wall>1.2:
                assert (OUT/'return_blend.png').is_file();r['captures'][-1]['after']=snap(now);finish()
            return
        if now-last_sample>=.01:r['samples'].append(snap(now));last_sample=now
        if str(player.get_editor_property('ActionState'))=='Ready' and now-requested>.2:
            if returned is None:returned=now;r['native_ready_after_s']=now-requested;write()
            elif now-returned>.8:assess();finish()
        assert now-requested<12,'Native return exceeded bound'
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    assert guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6')
    cdo=unreal.get_default_object(cls)
    r['original_timing']={'duration':cdo.get_editor_property('ReloadDuration'),'commit':cdo.get_editor_property('ReloadCommitTime'),'rate':cdo.get_editor_property('ReloadPlayRate')}
    cdo.set_editor_property('ReloadPlayRate',r['original_timing']['duration']/4.133333206176758)
    r['staging'],staged,oldowner=stage_actions_actor();actors.destroy_actor(oldowner)
    newowner=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(auth['owner_package']),staged.get_actor_location(),unreal.Rotator());assert newowner
    newowner.set_actor_label('PC_ReloadBlendOwnerV5');newowner.set_editor_property('Combatant',staged)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True);callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:r['status']='failed_startup';r['errors'].append(traceback.format_exc());r['protected_records_unchanged']=guard();r['protected_count']=len(rows);write();unreal.SystemLibrary.quit_editor()
