"""Actual-city frozen-pose framing and occluder isolation, without saving assets."""
import hashlib,json,math,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
VARIANT=os.environ.get('CS549_FP_VARIANT')=='1'
VIEW_ISOLATE=os.environ.get('CS549_FP_VIEW_ISOLATE')=='1'
if VARIANT:
    from ue_first_person_view_runtime import stage,trial_records
else:
    from ue_player_aim_runtime_preview import stage,trial_records
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/CityGameplay20261002/FirstPersonViewV1'/os.environ['CS549_FP_IDENTITY']
assert OUT.name.replace('_','').isalnum() and not OUT.exists();OUT.mkdir(parents=True)
inv=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
dep=json.loads((ROOT/inv['retained_dependency_inventory']).read_text())
records=inv['files']+dep['files']+inv['retained_unselected_rejected_trial']+trial_records()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(digest(ROOT/e['path'])==e['sha256'] for e in records)
r={'scope':__doc__,'errors':[],'samples':[],'isolations':[],'status':'initializing'}
r['variant']=VARIANT
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2))
def xyz(v):return [v.x,v.y,v.z]
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
started=time.monotonic();ending=None;busy=False;callback=None;phase=-1;at=0;isolate=None;iso_step=0
specs=[('idle',0,0,0,0,1.5),('forward_start',1,0,0,0,.12),('forward',1,0,0,0,.55),
       ('forward_late',1,0,0,0,.35),('stop',0,0,0,0,.25),('backward',-1,0,0,0,.55),
       ('left',0,-1,0,0,.55),('right',0,1,0,0,.55),('up30',0,0,30,0,.4),
       ('down30',0,0,-30,0,.4),('turn45',1,0,0,45,.45)]
if VIEW_ISOLATE:
    specs=[('idle',0,0,0,0,1.5),('moving_down',1,0,-30,0,.6)]
elif os.environ.get('CS549_FP_DIAG_FOCUSED')=='1':
    specs=[('idle',0,0,0,0,1.5),('down30_moving',1,0,-30,0,.6),('down30_stopped',0,0,-30,0,.35)]
elif VARIANT:
    specs += [('fire',0,0,0,90,.5),('reload_still_start',0,0,0,90,.45),
      ('reload_still_mid',0,0,0,90,.7),('reload_still_done',0,0,0,90,3.0),
      ('fire_again',0,0,0,90,.6),('reload_move_start',1,0,0,90,.45),
      ('reload_move_mid',1,0,0,90,.7),('reload_move_done',1,0,0,90,3.0),
      ('death',0,0,0,90,.6),('reset',0,0,0,90,1.2)]
bones=['pelvis','spine_03','neck_01','head','upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r']
def measure():
    t=eye.get_world_transform();data={}
    data['camera_world']=xyz(eye.get_world_location())
    data['player_world']=xyz(player.get_actor_location())
    data['camera_relative']=xyz(eye.get_editor_property('relative_location'))
    assert (eye.get_world_location()-player.get_actor_location()).length()<150,'Diagnostic camera drifted away from player'
    for n in bones:
        v=unreal.MathLibrary.inverse_transform_location(t,mesh.get_socket_location(n))
        uv=[.5+v.y/(2*v.x),.5-v.z/(2*v.x/(16/9))] if v.x>0.001 else None
        data[n]={'camera_cm':xyz(v),'screen_uv_16_9':uv,'scale':xyz(mesh.get_socket_transform(n).scale3d)}
    data['gun_origin']={'camera_cm':xyz(unreal.MathLibrary.inverse_transform_location(t,gun.get_actor_location()))}
    return data
def capture(name,hidden=None):
    unreal.SystemLibrary.execute_console_command(world,'Shot SHOWUI -nosuffix filename="'+(OUT/(name+'.png')).as_posix()+'"',controller)
def local_pose(component):
    result={}
    for side in ('l','r'):
        for finger in ('thumb','index','middle','ring','pinky'):
            for segment in (1,2,3):
                n=finger+'_0'+str(segment)+'_'+side
                p='hand_'+side if segment==1 else finger+'_0'+str(segment-1)+'_'+side
                t=component.get_socket_transform(n);parent=component.get_socket_transform(p)
                result[n]={'translation':xyz(unreal.MathLibrary.inverse_transform_location(parent,t.translation)),
                  'axes':[xyz(unreal.MathLibrary.inverse_transform_direction(parent,unreal.MathLibrary.transform_direction(t,v))) for v in (unreal.Vector(1,0,0),unreal.Vector(0,1,0),unreal.Vector(0,0,1))]}
    return result
def contact():
    def center(side):
        fs=('middle','ring','pinky') if side=='r' else ('index','middle','ring','pinky')
        ns=[f+'_0'+str(s)+'_'+side for f in fs for s in (2,3)]+['thumb_02_'+side,'thumb_03_'+side]
        return sum((mesh.get_socket_location(n) for n in ns),unreal.Vector())/len(ns)
    t=gun.get_actor_transform();start=eye.get_world_location();end=start+eye.get_forward_vector()*20000
    hit=unreal.SystemLibrary.line_trace_single(world,start,end,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[player],unreal.DrawDebugTrace.NONE,True)
    goal=hit.to_tuple()[5] if hit else end
    muzzle=unreal.MathLibrary.transform_location(t,unreal.Vector(0,83.23,0));direction=unreal.MathLibrary.transform_direction(t,unreal.Vector(0,1,0));delta=goal-muzzle
    display_goal=start+eye.get_forward_vector()*150 if VARIANT and (goal-start).length()<150 else goal
    display_delta=display_goal-muzzle
    return {'rear_cm':(unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,-8,0))-center('r')).length(),
      'support_cm':(unreal.MathLibrary.transform_location(t,unreal.Vector(-.5,22.2,0))-center('l')).length(),
      'barrel_error_deg':math.degrees(math.acos(max(-1,min(1,direction.dot(delta)/delta.length())))),
      'ray_miss_cm':(delta-direction*direction.dot(delta)).length(),'target_camera_distance_cm':(goal-start).length(),
      'barrel_camera_dot':direction.dot(eye.get_forward_vector()),
      'presentation_barrel_error_deg':math.degrees(math.acos(max(-1,min(1,direction.dot(display_delta)/display_delta.length()))))}
def finish(error=None):
    global ending
    if ending:return
    if error:r['errors'].append(error)
    r['status']='failed' if r['errors'] else 'completed_diagnosis_not_visual_acceptance'
    levels.editor_request_end_play();ending=time.monotonic();write()
def next_case(now):
    global phase,at
    phase+=1;at=now
    if phase>=len(specs):finish();return
    name,fwd,side,pitch,yaw,duration=specs[phase]
    controller.set_control_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0))
    if not fwd and not side:movement.stop_movement_immediately()
    if name in ('fire','reload_move_start'):
        player.set_actor_location(unreal.Vector(*r['initial_location']),False,True)
        movement.stop_movement_immediately()
    if name in ('fire','fire_again'):r['pending_fire']=True
    if name in ('reload_still_start','reload_move_start'):player.call_method('PC_RequestReload')
    if name=='death':player.call_method('PC_ApplyDamage',args=(1000.0,))
    if name=='reset':player.call_method('PC_ResetLifecycle')
def tick(dt):
    global busy,world,player,controller,mesh,source_mesh,eye,gun,movement,camera,capture_component,target,phase,at,isolate,iso_step
    if busy:return
    busy=True
    try:
        if ending:
            if not levels.is_in_play_in_editor() and time.monotonic()-ending>3:
                r['protected_40_unchanged']=all(digest(ROOT/e['path'])==e['sha256'] for e in records)
                r['protected_file_count']=len(records)
                write();unreal.unregister_slate_post_tick_callback(callback);unreal.SystemLibrary.quit_editor()
            return
        if time.monotonic()-started>240:finish('probe timeout');return
        world=editor.get_game_world()
        player=unreal.GameplayStatics.get_player_pawn(world,0) if world else None
        if not player:return
        now=unreal.GameplayStatics.get_real_time_seconds(world)
        if phase<0:
            r['variant']=stage(world,player)
            r['initial_location']=xyz(player.get_actor_location())
            controller=unreal.GameplayStatics.get_player_controller(world,0)
            source_mesh=player.get_component_by_class(unreal.SkeletalMeshComponent)
            gun=player.get_editor_property('WeaponAppearance')
            mesh=gun.get_editor_property('GripMesh')
            eye=player.get_component_by_class(unreal.CameraComponent)
            movement=player.get_component_by_class(unreal.CharacterMovementComponent)
            mesh.set_tickable_when_paused(True)
            r['mesh']=mesh.get_skeletal_mesh_asset().get_path_name()
            r['camera']={'relative_location':xyz(eye.get_editor_property('relative_location')),'fov':eye.get_editor_property('field_of_view')}
            r['components']=[{'name':c.get_name(),'class':c.get_class().get_path_name()} for c in player.get_components_by_class(unreal.ActorComponent)]
            r['materials']=[str(mesh.get_material(i)) for i in range(mesh.get_num_materials())]
            if VIEW_ISOLATE:
                r['material_debug']={}
                r['nanite_settings']=str(mesh.get_skeletal_mesh_asset().get_editor_property('nanite_settings'))
                for slot in (2,8):
                    mi=mesh.get_material(slot);base=mi.get_editor_property('parent');overrides=mi.get_editor_property('base_property_overrides')
                    r['material_debug'][slot]={'base':base.get_path_name(),'blend':str(base.get_editor_property('blend_mode')),
                      'overrides':{k:str(overrides.get_editor_property(k)) for k in ('override_blend_mode','blend_mode','override_opacity_mask_clip_value','opacity_mask_clip_value')},
                      'nanite_override':str(mi.get_nanite_overide_material()),
                      'opacity_input':str(unreal.MaterialEditingLibrary.get_material_property_input_node(base,unreal.MaterialProperty.MP_OPACITY_MASK))}
            r['anim_api']={n:str(getattr(mesh.get_anim_instance(),n).__doc__) for n in dir(mesh.get_anim_instance()) if 'time' in n and ('asset' in n or 'sync' in n)}
            next_case(now);return
        if VARIANT and not r.get('warm_complete'):
            r['warm_frames']=r.get('warm_frames',0)+1
            if r['warm_frames']<30:return
            r['warm_complete']=True;at=now
        if isolate is not None:
            if now-at<.2:return
            stem=specs[phase][0]
            if VARIANT and VIEW_ISOLATE:
                steps=[('full',None),
                  ('no_motion_blur',lambda:unreal.SystemLibrary.execute_console_command(world,'r.MotionBlurQuality 0',controller)),
                  ('classic_renderer',lambda:mesh.set_force_disable_nanite(True)),
                  ('no_view',lambda:mesh.set_visibility(False)),
                  ('no_source',lambda:(mesh.set_visibility(True),source_mesh.set_visibility(False))),
                  ('no_jacket',lambda:(source_mesh.set_visibility(True),mesh.call_method('ShowMaterialSection',args=(2,-1,False,0)))),
                  ('no_skin',lambda:(mesh.call_method('ShowMaterialSection',args=(2,-1,True,0)),mesh.call_method('ShowMaterialSection',args=(8,-1,False,0)))),
                  ('unhide_head',lambda:(mesh.call_method('ShowMaterialSection',args=(8,-1,True,0)),mesh.un_hide_bone_by_name('head')))]
                if iso_step<len(steps)*2:
                    label,action=steps[iso_step//2]
                    if iso_step%2==0:
                        if action:action()
                    else:capture(stem+'_'+label)
                    iso_step+=1;at=now;return
                mesh.hide_bone_by_name('head',unreal.PhysBodyOp.PBO_NONE)
                mesh.set_force_disable_nanite(False)
                unreal.SystemLibrary.execute_console_command(world,'r.MotionBlurQuality 4',controller)
                isolate=None;mesh.set_editor_property('pause_anims',False,unreal.PropertyAccessChangeNotifyMode.NEVER)
                source_mesh.set_editor_property('pause_anims',False,unreal.PropertyAccessChangeNotifyMode.NEVER)
                unreal.GameplayStatics.set_game_paused(world,False);write();next_case(now);return
            if VARIANT:
                if iso_step==0:
                    capture(stem+'_full');iso_step=1;at=now;return
                r['isolations'].append({'name':stem,'scope':'Frozen candidate capture; preserve its owner-view bone visibility'})
                isolate=None
                mesh.set_editor_property('pause_anims',False,unreal.PropertyAccessChangeNotifyMode.NEVER)
                unreal.GameplayStatics.set_game_paused(world,False)
                write();next_case(now);return
            if iso_step==0:
                capture(stem+'_full');iso_step=1;at=now;return
            if iso_step==1:
                gun.static_mesh_component.set_visibility(False);iso_step=2;at=now;return
            if iso_step==2:
                capture(stem+'_without_rifle');iso_step=3;at=now;return
            if iso_step==3:
                gun.static_mesh_component.set_visibility(True);mesh.set_visibility(False);iso_step=4;at=now;return
            if iso_step==4:
                capture(stem+'_without_body');iso_step=5;at=now;return
            if iso_step==5:
                mesh.set_visibility(True)
                isolate['frozen_before_head_hide']=measure()
                mesh.hide_bone_by_name('head',unreal.PhysBodyOp.PBO_NONE);iso_step=6;at=now;return
            if iso_step==6:
                capture(stem+'_without_head');isolate['head_hidden']=measure()
                iso_step=7;at=now;return
            if iso_step==7:
                mesh.un_hide_bone_by_name('head');mesh.hide_bone_by_name('neck_01',unreal.PhysBodyOp.PBO_NONE)
                iso_step=8;at=now;return
            if iso_step==8:
                capture(stem+'_without_neck');isolate['neck_hidden']=measure();iso_step=9;at=now;return
            mesh.un_hide_bone_by_name('neck_01');r['isolations'].append(isolate);isolate=None
            mesh.set_editor_property('pause_anims',False,unreal.PropertyAccessChangeNotifyMode.NEVER)
            unreal.GameplayStatics.set_game_paused(world,False)
            write();next_case(now);return
        name,fwd,side,pitch,yaw,duration=specs[phase]
        direction=unreal.MathLibrary.get_forward_vector(unreal.Rotator(pitch=0,yaw=yaw,roll=0))*fwd+unreal.MathLibrary.get_right_vector(unreal.Rotator(pitch=0,yaw=yaw,roll=0))*side
        if fwd or side:player.add_movement_input(direction,1,True)
        if r.get('pending_fire') and now-at>=.2:
            player.call_method('PC_PlayerFire');r['pending_fire']=False
        if VARIANT and str(player.get_editor_property('ActionState'))=='Reloading' and player.get_velocity().length()>100:
            r['moving_reload_frames']=r.get('moving_reload_frames',0)+1
        if now-at<duration:return
        sample={'name':name,'world_time':now,'velocity':xyz(player.get_velocity()),'pose':measure(),'action':str(player.get_editor_property('ActionState')),'contact':contact()}
        if VARIANT:
            sample['ammo']={n:str(player.get_editor_property(n)) for n in ('LoadedAmmo','ReserveAmmo','ShotSequence','ActionState','IsDead')}
            sample['view_state']={'source_owner_hidden':source_mesh.get_editor_property('owner_no_see'),
              'only_owner':mesh.get_editor_property('only_owner_see'),'head_hidden':mesh.is_bone_hidden_by_name('head'),
              'initialized':mesh.get_owner().get_editor_property('ViewInitialized'),
              'view_cloth_disabled':mesh.get_editor_property('disable_cloth_simulation'),
              'view_cloth_weight':mesh.get_editor_property('cloth_blend_weight'),
              'source_cloth_disabled':source_mesh.get_editor_property('disable_cloth_simulation'),
              'source_class':source_mesh.get_anim_instance().get_class().get_name()}
            a,b=local_pose(source_mesh),local_pose(mesh)
            sample['finger_local_max_translation_delta_cm']=max((unreal.Vector(*a[n]['translation'])-unreal.Vector(*b[n]['translation'])).length() for n in a)
            sample['finger_local_max_axis_delta']=max((unreal.Vector(*a[n]['axes'][i])-unreal.Vector(*b[n]['axes'][i])).length() for n in a for i in range(3))
        r['samples'].append(sample)
        unreal.SystemLibrary.execute_console_command(world,'Shot SHOWUI -nosuffix filename="'+(OUT/(name+'_viewport.png')).as_posix()+'"',controller)
        mesh.set_editor_property('pause_anims',True,unreal.PropertyAccessChangeNotifyMode.NEVER)
        if VIEW_ISOLATE:source_mesh.set_editor_property('pause_anims',True,unreal.PropertyAccessChangeNotifyMode.NEVER)
        assert unreal.GameplayStatics.set_game_paused(world,True)
        isolate={'name':name,'captured_pose':sample['pose']};iso_step=0;at=now;write()
    except Exception:finish(traceback.format_exc())
    finally:busy=False
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback=unreal.register_slate_post_tick_callback(tick)
write();levels.editor_request_begin_play()
