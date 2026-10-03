"""Unsaved fresh player aiming/contact comparison with original fingers and reload."""
import hashlib,json,math,os,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/CityGameplay20261002/RifleCrosshairV4'/os.environ['CS549_PLAYER_AIM_LIVE_IDENTITY']
assert OUT.name.replace('_','').isalnum() and not OUT.exists()
OUT.mkdir(parents=True)
inventory=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
deps=json.loads((ROOT/inventory['retained_dependency_inventory']).read_text())
author=json.loads((OUT.parent/os.environ['CS549_PLAYER_AIM_SOURCE_AUTHOR']/'result.json').read_text())
assert not author['errors'] and author['status'].startswith('saved_unselected')
records=inventory['files']+deps['files']+inventory['retained_unselected_rejected_trial']+[author['saved_trial']]+author['aim_dependencies']
rifle_author=None
if os.environ.get('CS549_PLAYER_RIFLE_SOURCE_AUTHOR'):
    rifle_author=json.loads((OUT.parent/os.environ['CS549_PLAYER_RIFLE_SOURCE_AUTHOR']/'result.json').read_text())
    assert not rifle_author['errors'] and rifle_author['status'].startswith('saved_unselected')
    records.append(rifle_author['saved_trial'])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(digest(ROOT/e['path'])==e['sha256'] for e in records)
r={'scope':__doc__,'status':'initializing','errors':[],'samples':[],'captures':[],'frames':[]}
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
phase=-1; phase_start=0; ending=None; busy=False; started=time.monotonic(); callback=None
specs=[('source_idle',0,0,False,False),('aim_idle',0,0,False,True),
       ('up15',15,0,False,True),('down15',-15,0,False,True),
       ('up30',30,0,False,True),('down30',-30,0,False,True),
       ('up60',60,0,False,True),('down60',-60,0,False,True),
       ('yaw45',0,45,False,True),('near0',0,0,False,True),('near15',15,0,False,True),
       ('walk0',0,0,True,True),('walk15',15,0,True,True),
       ('reload_walk',0,0,True,True),('reset',0,0,False,True)]
def xyz(v):return [v.x,v.y,v.z]
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2))
def center(side):
    fs=('middle','ring','pinky') if side=='r' else ('index','middle','ring','pinky')
    names=[f+'_0'+str(s)+'_'+side for f in fs for s in (2,3)]+['thumb_02_'+side,'thumb_03_'+side]
    return sum((mesh.get_socket_location(n) for n in names),unreal.Vector())/len(names)
def local_pose():
    data={}
    for side in ('l','r'):
        for finger in ('thumb','index','middle','ring','pinky'):
            for segment in (1,2,3):
                n=finger+'_0'+str(segment)+'_'+side
                parent='hand_'+side if segment==1 else finger+'_0'+str(segment-1)+'_'+side
                t=mesh.get_socket_transform(n);p=mesh.get_socket_transform(parent)
                data[n]={'translation':xyz(unreal.MathLibrary.inverse_transform_location(p,t.translation)),
                         'axes':[xyz(unreal.MathLibrary.inverse_transform_direction(p,unreal.MathLibrary.transform_direction(t,v))) for v in (unreal.Vector(1,0,0),unreal.Vector(0,1,0),unreal.Vector(0,0,1))]}
    return data
def measure(goal):
    t=gun.get_actor_transform();muzzle=unreal.MathLibrary.transform_location(t,unreal.Vector(0,83.23,0))
    direction=unreal.MathLibrary.transform_direction(t,unreal.Vector(0,1,0));delta=goal-muzzle
    projection=direction.dot(delta)
    return {'angle_deg':math.degrees(math.acos(max(-1,min(1,projection/delta.length())))),
            'ray_miss_cm':(delta-direction*projection).length(),'target_in_front':projection>0,
            'support_error_cm':(unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,22.2,0))-center('l')).length(),
            'rear_error_cm':(unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,-8,0))-center('r')).length()}
def converge(goal):
    right=center('r')
    for _ in range(4):
        look=unreal.MathLibrary.find_look_at_rotation(gun.get_actor_location(),goal)
        gun.set_actor_rotation(unreal.Rotator(pitch=0,yaw=look.yaw-90,roll=-look.pitch),False)
        anchor=unreal.MathLibrary.transform_location(gun.get_actor_transform(),unreal.Vector(-.5,-8,0))
        gun.set_actor_location(gun.get_actor_location()+right-anchor,False,False)
def views(stem):
    mid=(mesh.get_socket_location('hand_l')+mesh.get_socket_location('hand_r'))/2
    for label,offset,fov in (('front',unreal.Vector(160,120,50),50),('side',unreal.Vector(150,-110,70),50),('fp',None,90)):
        at=mid+offset if offset else eye.get_world_location()
        rot=unreal.MathLibrary.find_look_at_rotation(at,mid) if offset else eye.get_world_rotation()
        camera.set_actor_location(at,False,False);camera.set_actor_rotation(rot,False)
        capture.set_editor_property('fov_angle',fov);capture.capture_scene()
        file=stem+'_'+label+'.png';unreal.RenderingLibrary.export_render_target(world,target,str(OUT),file);r['captures'].append(file)
def finish(error=None):
    global ending
    if ending:return
    if error:r['errors'].append(error)
    r['status']='failed' if r['errors'] else 'unsaved_aim_contact_trial_not_city_acceptance'
    levels.editor_request_end_play();ending=time.monotonic();write()
def begin_case(index,now):
    global phase,phase_start
    phase=index;phase_start=now
    name,pitch,yaw,moving,enabled=specs[index]
    pawn.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
    controller.set_control_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0))
    if mesh.get_anim_instance():mesh.get_anim_instance().set_editor_property('AimEnabled',enabled)
    if name.startswith('near'):
        at=eye.get_world_location()+unreal.MathLibrary.get_forward_vector(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0))*350
        near_wall.set_actor_location(at,False,False)
    else:near_wall.set_actor_location(unreal.Vector(0,0,-10000),False,False)
    if name=='reload_walk':
        r['before_reload']={n:str(pawn.get_editor_property(n)) for n in ('LoadedAmmo','ReserveAmmo','ActionState')}
        pawn.call_method('PC_RequestReload')
    if name=='reset':pawn.call_method('PC_ResetLifecycle')
def tick(delta):
    global busy,phase,phase_start,pawn,mesh,gun,world,eye,camera,capture,target,controller,near_wall
    if busy:return
    busy=True
    try:
        if ending:
            if not levels.is_in_play_in_editor() and time.monotonic()-ending>3:
                r['all_protected_bytes_unchanged']=all(digest(ROOT/e['path'])==e['sha256'] for e in records)
                write();unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        if time.monotonic()-started>180:finish('Bounded aim probe timeout');return
        world=editor.get_game_world()
        if not world:return
        now=unreal.GameplayStatics.get_time_seconds(world)
        if phase==-1:
            pawn=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character) if a.get_actor_label()=='AimPlayer')
            mesh=pawn.get_component_by_class(unreal.SkeletalMeshComponent)
            eye=pawn.get_component_by_class(unreal.CameraComponent)
            gun=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.StaticMeshActor) if a.get_actor_label()=='AimGun')
            controller=unreal.GameplayStatics.get_player_controller(world,0);controller.possess(pawn)
            assert author['saved_trial']['package'].rsplit('/',1)[1]+'_C' in mesh.get_anim_instance().get_class().get_path_name()
            spawn=unreal.get_default_object(unreal.GameplayStatics.static_class())
            camera=spawn.call_method('BeginDeferredActorSpawnFromClass',args=(world,unreal.SceneCapture2D.static_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,pawn,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            camera=spawn.call_method('FinishSpawningActor',args=(camera,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            near_wall=spawn.call_method('BeginDeferredActorSpawnFromClass',args=(world,unreal.StaticMeshActor.static_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,pawn,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            near_wall=spawn.call_method('FinishSpawningActor',args=(near_wall,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            near_wall.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            near_wall.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
            near_wall.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
            near_wall.static_mesh_component.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_BLOCK)
            capture=camera.get_component_by_class(unreal.SceneCaptureComponent2D)
            capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('capture_every_frame',False);capture.set_editor_property('override_custom_near_clipping_plane',True);capture.set_editor_property('custom_near_clipping_plane',1)
            target=unreal.RenderingLibrary.create_render_target2d(world,1280,720,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(0,0,0,1),False);capture.set_editor_property('texture_target',target)
            begin_case(0,now);return
        name,pitch,yaw,moving,enabled=specs[phase]
        if moving:pawn.add_movement_input(eye.get_forward_vector()*unreal.Vector(1,1,0),1,True)
        action=str(pawn.get_editor_property('ActionState'))
        if name=='reload_walk':
            r['frames'].append({'action':action,'velocity':xyz(pawn.get_velocity()),'rear_error_cm':measure(eye.get_world_location()+eye.get_forward_vector()*20000)['rear_error_cm']})
            if now-phase_start>1 and not r.get('reload_captured'):views('reload');r['reload_captured']=True
            if now-phase_start<3.8:return
            assert action=='Ready' and int(pawn.get_editor_property('LoadedAmmo'))+int(pawn.get_editor_property('ReserveAmmo'))==18
            r['after_reload_class']=mesh.get_anim_instance().get_class().get_path_name();assert author['saved_trial']['package'].rsplit('/',1)[1]+'_C' in r['after_reload_class']
        elif now-phase_start<1.5:return
        if action=='Ready':
            anim=mesh.get_anim_instance()
            ray_start=eye.get_world_location();ray_end=ray_start+eye.get_forward_vector()*20000
            hit=unreal.SystemLibrary.line_trace_single(world,ray_start,ray_end,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[pawn],unreal.DrawDebugTrace.NONE,True)
            goal=hit.to_tuple()[5] if hit else ray_end
            sample={'name':name,'pitch':pitch,'yaw':yaw,'velocity':xyz(pawn.get_velocity()),'alpha':anim.get_editor_property('AimAlpha'),
                    'target':xyz(goal),'target_distance_cm':(goal-ray_start).length(),'anim_target_delta_cm':(anim.get_editor_property('AimTargetWorld')-goal).length(),
                    'original_fit':measure(goal),'finger_local':local_pose(),
                    'lower_body_local':{n:xyz(unreal.MathLibrary.inverse_transform_location(mesh.get_world_transform(),mesh.get_socket_location(n))) for n in ('pelvis','thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r')}}
            views(name+'_fit')
            old=gun.get_actor_transform();converge(goal);sample['residual_converged']=measure(goal)
            if enabled:views(name+'_converged')
            gun.set_actor_transform(old,False,True)
            r['samples'].append(sample)
        if phase+1==len(specs):
            source=r['samples'][0]['finger_local'];aimed=r['samples'][1]['finger_local']
            r['idle_finger_local_max_axis_delta']=max((unreal.Vector(*source[n]['axes'][i])-unreal.Vector(*aimed[n]['axes'][i])).length() for n in source for i in range(3))
            r['idle_finger_local_max_translation_delta_cm']=max((unreal.Vector(*source[n]['translation'])-unreal.Vector(*aimed[n]['translation'])).length() for n in source)
            r['moving_reload_frames']=sum(f['action']=='Reloading' and unreal.Vector(*f['velocity']).length()>100 for f in r['frames'])
            finish();return
        begin_case(phase+1,now);write()
    except Exception:finish(traceback.format_exc())
    finally:busy=False
try:
    assert levels.load_level('/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001')
    for a in actors.get_all_level_actors():
        if isinstance(a,unreal.Character):actors.destroy_actor(a)
    pawn=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'),unreal.Vector(0,0,100));pawn.set_actor_label('AimPlayer')
    mesh=pawn.get_component_by_class(unreal.SkeletalMeshComponent)
    mesh.set_anim_instance_class(unreal.EditorAssetLibrary.load_blueprint_class(author['saved_trial']['package']))
    gun_package=rifle_author['package'] if rifle_author else '/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3'
    gun=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(gun_package),unreal.Vector());gun.set_actor_label('AimGun')
    gun.set_editor_property('GripMesh',mesh);gun.set_editor_property('Combatant',pawn);gun.set_owner(pawn);pawn.set_editor_property('WeaponAppearance',gun)
    assert gun.attach_to_component(mesh,'hand_r',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
    light=actors.spawn_actor_from_class(unreal.PointLight,unreal.Vector(80,-80,220));c=light.get_component_by_class(unreal.PointLightComponent);c.set_editor_property('intensity',20);c.set_editor_property('attenuation_radius',700)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True);callback=unreal.register_slate_post_tick_callback(tick);write();levels.editor_request_begin_play()
except Exception:
    r['status']='failed_startup';r['errors'].append(traceback.format_exc());r['all_protected_bytes_unchanged']=all(digest(ROOT/e['path'])==e['sha256'] for e in records);write();unreal.SystemLibrary.quit_editor()
