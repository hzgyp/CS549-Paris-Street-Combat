"""V20 thumb-only paired native viewing, NOT AN007 full action/return proof."""
import hashlib
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE = STORE / 'Evidence/LeftSupportV20'
sys.path.insert(0, str(ROOT / 'Tools/Integration/NPCInteractionV1'))
from common import guard_rows, guards_match

identity = os.environ['CS549_LEFT_SUPPORT_V20_ID']
OUT = BASE / identity
assert not OUT.exists(), 'Preserve occupied native identity'
OUT.mkdir()
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
oldpath = STORE / 'Evidence/GripBindingV18/config_v1/binding.json'
newpath = BASE / 'reuse_pose_v2/binding.json'
original = json.loads(oldpath.read_text())
candidate = json.loads(newpath.read_text())
proof = json.loads((BASE / 'config_verification_v1/result.json').read_text())
assert hashlib.sha256(newpath.read_bytes()).hexdigest() == proof['config_sha256']
assert hashlib.sha256(oldpath.read_bytes()).hexdigest() == proof['baseline_config_sha256']
rows = guard_rows()
r = {'identity': identity, 'pid': os.getpid(), 'status': 'starting', 'errors': [],
     'samples': [], 'captures': [], 'selected_formal': False, 'map_saved': False,
     'scope': 'existing-three-left-thumb-rotations-only; paired Ready, left walk, one original reload',
     'full_return_continuity_measured': False, 'sleeve_repair': False,
     'complete_action_acceptance': False, 'guard_count': len(rows),
     'guards_before_match': guards_match(rows),
     'runtime': 'unchanged V19 native C++; Python prepares once/observes/stimulates inputs only'}
assert r['guards_before_match']
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
start = time.monotonic()
callback = None
ready = prepared = bound = ending = None
phase = 0
phase_start = 0
capture_wait = None
busy = False
world = player = owner = controller = baseline = current = None

def write():
    (OUT / 'result.json').write_text(json.dumps(r, indent=2)+'\n')

def xyz(v): return [v.x, v.y, v.z]

def transform(t):
    return {'t': xyz(t.translation), 'q': [t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w], 's': xyz(t.scale3d)}

def angle(a, b):
    aa = [a.x,a.y,a.z,a.w]
    dot = abs(sum(x*y for x,y in zip(aa,b))/math.sqrt(sum(x*x for x in aa)*sum(x*x for x in b)))
    return math.degrees(2*math.acos(max(-1,min(1,dot))))

def bone_local(pose, bone):
    return unreal.MathLibrary.make_relative_transform(pose.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT),pose.get_socket_transform(pose.get_parent_bone(bone),unreal.RelativeTransformSpace.RTS_COMPONENT))

def exact(row):
    path = ROOT / row['path']
    return path.is_file() and path.stat().st_size == row['size_bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']

def snapshot(name):
    camera = player.get_editor_property('ParisPlayerCamera')
    pose = current.get_editor_property('Pose')
    gun = current.get_editor_property('Gun')
    bp = baseline.get_editor_property('Pose')
    bg = baseline.get_editor_property('Gun')
    rel = unreal.MathLibrary.make_relative_transform(gun.get_world_transform(),pose.get_socket_transform('hand_r',unreal.RelativeTransformSpace.RTS_WORLD))
    finger_errors = {n:angle(bone_local(pose,n).rotation,row['q']) for n,row in candidate['fingers_local'].items()}
    unchanged_errors = {n:angle(bone_local(pose,n).rotation,transform(bone_local(bp,n))['q']) for n in original['fingers_local'] if n not in ('thumb_01_l','thumb_02_l','thumb_03_l')}
    wrist_delta = (pose.get_socket_transform('hand_l',unreal.RelativeTransformSpace.RTS_WORLD).translation-bp.get_socket_transform('hand_l',unreal.RelativeTransformSpace.RTS_WORLD).translation).length()
    s = {'name': name, 'action': str(player.get_editor_property('ActionState')),
         'holding_alpha': float(current.get_editor_property('HoldingAppliedAlpha')),
         'native_updates': int(current.get_editor_property('NativePoseUpdates')),
         'error': str(current.get_editor_property('BindingError')),
         'finger_errors_degrees': finger_errors, 'unchanged_finger_errors_degrees': unchanged_errors,
         'left_wrist_pair_delta_cm': wrist_delta,
         'gun_pair_delta_cm': (gun.get_world_transform().translation-bg.get_world_transform().translation).length(),
         'gun_pair_angle_degrees': angle(gun.get_world_transform().rotation,transform(bg.get_world_transform())['q']),
         'gun_hand_cm': (rel.translation-unreal.Vector(*original['gun_hand_relative']['t'])).length(),
         'gun_hand_degrees': angle(rel.rotation,original['gun_hand_relative']['q']),
         'support_cm': float(current.get_editor_property('SupportErrorCm')),
         'limb_length_cm': float(current.get_editor_property('LimbLengthErrorCm')),
         'camera_relative_cm': xyz(camera.get_editor_property('relative_location')),
         'fov': float(camera.get_editor_property('field_of_view')),
         'authoritative_weapon_unchanged': player.get_editor_property('WeaponAppearance') == owner.get_editor_property('DisplayGun'),
         'ammo': [int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
         'commits': int(player.get_editor_property('ReloadCommitCount')),
         'speed_cm_s': player.get_velocity().length(),
         'thumb_locals': {n:transform(bone_local(pose,n)) for n in ('thumb_01_l','thumb_02_l','thumb_03_l')},
         'gun_socket': str(gun.get_attach_socket_name()), 'game_seconds': unreal.GameplayStatics.get_time_seconds(world)}
    assert not s['error'] and s['native_updates']>0
    assert s['authoritative_weapon_unchanged'] and s['gun_socket']=='hand_r'
    assert s['camera_relative_cm']==[25.0,0.0,60.0] and s['fov']==90.0
    assert s['gun_hand_cm']<.01 and s['gun_hand_degrees']<.01
    assert s['left_wrist_pair_delta_cm']<.01 and s['gun_pair_delta_cm']<.01 and s['gun_pair_angle_degrees']<.01
    assert max(unchanged_errors.values())<.01
    if s['action']=='Ready' and s['holding_alpha']>.9999:
        assert max(finger_errors.values())<.01 and s['support_cm']<.2 and s['limb_length_cm']<.01
    r['samples'].append(s)
    return s

def show(which):
    baseline.set_actor_hidden_in_game(which!='baseline')
    current.set_actor_hidden_in_game(which!='candidate')

def capture(name):
    global capture_wait
    sample = snapshot(name)
    unreal.SystemLibrary.execute_console_command(world,'HighResShot 1600x900 filename="'+(OUT/(name+'.png')).as_posix()+'"',controller)
    r['captures'].append({'file': name+'.png', 'request_sample': sample, 'frozen': False})
    capture_wait = time.monotonic()
    write()

def finish(error=None):
    global ending
    if ending is not None:return
    if error:r['errors'].append(error)
    r['guards_after_match']=guards_match(rows)
    r['status']='stopped_local_review' if r['errors'] else 'local_native_views_recorded_requires_visual_and_human_review'
    levels.editor_request_end_play()
    ending=time.monotonic()
    write()

def enter(index):
    global phase,phase_start,capture_wait
    phase=index;phase_start=unreal.GameplayStatics.get_time_seconds(world);capture_wait=None

def tick(delta):
    global busy,world,player,owner,controller,baseline,current,ready,prepared,bound,phase_start
    if busy:return
    busy=True
    try:
        if ending is not None:
            if time.monotonic()-ending>2:
                unreal.unregister_slate_post_tick_callback(callback)
                r['python_observer_unregistered']=True;write();unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic()-start<300, 'Bounded V20 local native review timeout'
        world=editor.get_game_world();player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        owner=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_Player_ContinuousArmsNativeV1'),None)
        if not owner or not owner.get_editor_property('Initialized'):return
        if ready is None:ready=time.monotonic();return
        if time.monotonic()-ready<20:return
        baseline=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFPUpperBodyV19Actor) if a.get_actor_label()=='PC_LeftThumbV20_Baseline')
        current=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFPUpperBodyV19Actor) if a.get_actor_label()=='PC_LeftThumbV20_Candidate')
        controller=unreal.GameplayStatics.get_player_controller(world,0)
        if prepared is None:
            for a in (baseline,current):
                assert a.prepare_holding_source(player.mesh.get_skeletal_mesh_asset(),unreal.load_asset(selected['clip_path']))
            prepared=time.monotonic();return
        if time.monotonic()-prepared<2:return
        if bound is None:
            camera=player.get_editor_property('ParisPlayerCamera');oldgun=owner.get_editor_property('DisplayGun')
            assert player.get_editor_property('WeaponAppearance')==oldgun
            for a,path in ((baseline,oldpath),(current,newpath)):
                cfg=unreal.new_object(unreal.ParisGripV18Config,outer=a);cfg.set_editor_property('BindingJson',path.read_text())
                assert a.bind_existing_pose(player,player.mesh,camera,oldgun,unreal.load_asset(original['source_mesh']),unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'),cfg),str(a.get_editor_property('BindingError'))
            owner.set_actor_hidden_in_game(True);oldgun.set_actor_hidden_in_game(True)
            bound=time.monotonic();show('baseline');enter(0);return
        elapsed=unreal.GameplayStatics.get_time_seconds(world)-phase_start
        if phase==0:
            if capture_wait is None and elapsed>=2:capture('baseline_ready')
            elif capture_wait is not None and time.monotonic()-capture_wait>=1:
                assert (OUT/'baseline_ready.png').is_file();show('candidate');enter(1)
        elif phase==1:
            if capture_wait is None and elapsed>=2:capture('candidate_ready')
            elif capture_wait is not None and time.monotonic()-capture_wait>=1:
                assert (OUT/'candidate_ready.png').is_file();r['status']='paired_ready_views_available';write();enter(2)
        elif phase==2:
            review=OUT/'early_review.json'
            if not review.is_file():return
            r['early_visual_review']=json.loads(review.read_text())
            assert r['early_visual_review']['pass'], 'Native local appearance failed; no further test'
            enter(3)
        elif phase==3:
            player.add_movement_input(unreal.Vector(0,-1,0),1,True)
            if capture_wait is None and elapsed>=.6:capture('candidate_left_walk')
            elif capture_wait is not None and time.monotonic()-capture_wait>=1:
                assert (OUT/'candidate_left_walk.png').is_file();enter(4)
        elif phase==4:
            if elapsed<1:return
            r['reload_before']=snapshot('pre_reload')
            player.call_method('PC_RequestReload')
            assert str(player.get_editor_property('ActionState'))=='Reloading'
            enter(5)
        elif phase==5:
            if capture_wait is None and elapsed>=.9:capture('original_reload_mid')
            if elapsed>=3.5 and str(player.get_editor_property('ActionState'))=='Ready':enter(6)
        elif phase==6:
            if capture_wait is None and elapsed>=1:capture('candidate_post_reload')
            elif capture_wait is not None and time.monotonic()-capture_wait>=1:
                assert (OUT/'candidate_post_reload.png').is_file()
                after=snapshot('post_reload');before=r['reload_before']
                r['one_original_reload_conserved']=after['commits']==before['commits']+1 and sum(after['ammo'])==sum(before['ammo']) and after['ammo'][0]>before['ammo'][0]
                assert r['one_original_reload_conserved']
                finish()
    except Exception:finish(traceback.format_exc())
    finally:busy=False

try:
    verified=json.loads((STORE/'Evidence/FPUpperBodyV19/verification_v1/result.json').read_text())
    plugins=[row for row in verified['files'] if '/Plugins/ParisGripBindingV18/' in row['path']]
    assert plugins and all(exact(row) for row in plugins)
    assert exact(verified['accepted_source'])
    selected=json.loads((STORE/'Evidence/FPUpperBodyV19/holding_selection_v1/selection.json').read_text())
    assert selected['compatible_existing_clip'] and exact(selected['source_inventory'])
    assert hasattr(unreal,'ParisFPUpperBodyV19Actor') and not hasattr(unreal,'ParisBlueprintAuthoring')
    for label in ('PC_LeftThumbV20_Baseline','PC_LeftThumbV20_Candidate'):
        actor=actors.spawn_actor_from_class(unreal.ParisFPUpperBodyV19Actor,unreal.Vector(),unreal.Rotator());assert actor;actor.set_actor_label(label)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='stopped_startup';r['guards_after_match']=guards_match(rows);write();unreal.SystemLibrary.quit_editor()
