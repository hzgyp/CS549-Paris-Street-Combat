"""One-time V20 manual preparation, never the stopped AN007 proof launcher."""
import hashlib,json,math,os,sys,time,traceback
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import guard_rows
rows=guard_rows()
BASE=STORE/'Evidence/LeftSupportV20'
CONFIG=BASE/'reuse_pose_v2/binding.json'
identity=os.environ['CS549_LEFT_SUPPORT_V20_HUMAN_ID']
OUT=BASE/identity
assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
r={'status':'starting','identity':identity,'pid':os.getpid(),'errors':[],
   'view_only':True,'map_saved':False,'selected_formal':False,
   'action_acceptance':False,'python_preparation_unregistered':False}
callback=None;busy=False;ready=prepared=bound=None
start=time.monotonic()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
label='PC_LeftSupportV20Human'

def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def exact(row):
    p=ROOT/row['path']
    return p.is_file() and p.stat().st_size==row['size_bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
def guard():return {'count':len(rows),'mismatches':[row['path'] for row in rows if not exact(row)]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def angle(q,b):
    a=[q.x,q.y,q.z,q.w]
    dot=abs(sum(x*y for x,y in zip(a,b))/math.sqrt(sum(x*x for x in a)*sum(x*x for x in b)))
    return math.degrees(2*math.acos(max(-1,min(1,dot))))
def unregister():
    if callback is not None:unreal.unregister_slate_post_tick_callback(callback)
    r['python_preparation_unregistered']=True
def stop():
    r['errors'].append(traceback.format_exc());r['status']='stopped_preparation'
    unregister();r['guards_after']=guard();write()
    levels.editor_request_end_play()
    unreal.log_error('V20 human preparation stopped, no save: '+r['errors'][-1])

def tick(delta):
    global busy,ready,prepared,bound
    if busy:return
    busy=True
    try:
        assert time.monotonic()-start<240,'V20 human preparation deadline'
        world=editor.get_game_world()
        player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        owner=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_actor_label()=='PC_Player_ContinuousArmsNativeV1'),None)
        if not owner or not owner.get_editor_property('Initialized'):return
        if ready is None:ready=time.monotonic();return
        if time.monotonic()-ready<20:return
        new=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFPUpperBodyV19Actor) if a.get_actor_label()==label)
        if prepared is None:
            assert new.prepare_holding_source(player.mesh.get_skeletal_mesh_asset(),unreal.load_asset(selected['clip_path']))
            prepared=time.monotonic();return
        if time.monotonic()-prepared<2:return
        if bound is None:
            cfg=unreal.new_object(unreal.ParisGripV18Config,outer=new)
            cfg.set_editor_property('BindingJson',CONFIG.read_text())
            camera=player.get_editor_property('ParisPlayerCamera');oldgun=owner.get_editor_property('DisplayGun')
            assert player.get_editor_property('WeaponAppearance')==oldgun
            assert new.bind_existing_pose(player,player.mesh,camera,oldgun,unreal.load_asset(c['source_mesh']),unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'),cfg),str(new.get_editor_property('BindingError'))
            owner.set_actor_hidden_in_game(True);oldgun.set_actor_hidden_in_game(True)
            bound=time.monotonic();return
        if time.monotonic()-bound<2:return
        camera=player.get_editor_property('ParisPlayerCamera');rel=camera.get_editor_property('relative_location')
        pose=new.get_editor_property('Pose');thumb_errors={}
        for name in ('thumb_01_l','thumb_02_l','thumb_03_l'):
            local=unreal.MathLibrary.make_relative_transform(pose.get_socket_transform(name,unreal.RelativeTransformSpace.RTS_COMPONENT),pose.get_socket_transform(pose.get_parent_bone(name),unreal.RelativeTransformSpace.RTS_COMPONENT))
            thumb_errors[name]=angle(local.rotation,c['fingers_local'][name]['q'])
        n={
            'initialized':bool(new.get_editor_property('Initialized')),
            'binding_error':str(new.get_editor_property('BindingError')),
            'native_updates':int(new.get_editor_property('NativePoseUpdates')),
            'holding_alpha':float(new.get_editor_property('HoldingAppliedAlpha')),
            'action':str(player.get_editor_property('ActionState')),
            'camera_relative_cm':[rel.x,rel.y,rel.z],
            'fov':float(camera.get_editor_property('field_of_view')),
            'authoritative_weapon_unchanged':player.get_editor_property('WeaponAppearance')==owner.get_editor_property('DisplayGun'),
            'ammo':[int(player.get_editor_property('LoadedAmmo')),int(player.get_editor_property('ReserveAmmo'))],
            'holding_clip':selected['clip_path'],
            'gun_socket':str(new.get_editor_property('Gun').get_attach_socket_name()),
            'v20_thumb_local_errors_degrees':thumb_errors}
        r['native_ready']=n
        assert n['initialized'] and not n['binding_error'] and n['native_updates']>0,n
        assert n['authoritative_weapon_unchanged'] and n['gun_socket']=='hand_r',n
        assert n['action']=='Ready' and n['holding_alpha']>=.9999 and max(thumb_errors.values())<.01,n
        assert max(abs(a-b) for a,b in zip(n['camera_relative_cm'],[25,0,60]))<1e-6 and abs(n['fov']-90)<1e-6,n
        assert n['ammo']==[2,16],n
        r['guards_after']=guard();assert not r['guards_after']['mismatches']
        unregister();r['status']='ready_user_owned';write()
        unreal.log('V20 HUMAN READY: click viewport, WASD/mouse/R; do not save staged map. Python preparation removed.')
    except Exception:stop()
    finally:busy=False

try:
    r['guards_before']=guard();assert not r['guards_before']['mismatches']
    verified=json.loads((BASE/'verification_v1/result.json').read_text())
    oldconfig=STORE/'Evidence/GripBindingV18/config_v1/binding.json'
    assert sha(CONFIG)==verified['config_sha256'] and sha(oldconfig)==verified['baseline_config_sha256']
    c=json.loads(CONFIG.read_text());old=json.loads(oldconfig.read_text());expected=json.loads(oldconfig.read_text())
    for name in ('thumb_01_l','thumb_02_l','thumb_03_l'):expected['fingers_local'][name]['q']=c['fingers_local'][name]['q']
    assert expected==c,'Manual V20 entry exceeds three existing rotations'
    runtime=json.loads((STORE/'Evidence/FPUpperBodyV19/verification_v1/result.json').read_text())
    pluginrows=[row for row in runtime['files'] if '/Plugins/ParisGripBindingV18/' in row['path']]
    assert pluginrows and all(exact(row) for row in pluginrows) and exact(runtime['accepted_source'])
    selected=json.loads((STORE/'Evidence/FPUpperBodyV19/holding_selection_v1/selection.json').read_text())
    assert selected['compatible_existing_clip'] and exact(selected['source_inventory'])
    r['immutable_runtime_inputs_verified']=True;r['config_sha256']=sha(CONFIG)
    assert hasattr(unreal,'ParisFPUpperBodyV19Actor') and not hasattr(unreal,'ParisBlueprintAuthoring')
    actor=actors.spawn_actor_from_class(unreal.ParisFPUpperBodyV19Actor,unreal.Vector(),unreal.Rotator());assert actor
    actor.set_actor_label(label)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:stop()
