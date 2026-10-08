"""Finite native mission observer. Deliberate damage fixtures are not natural combat."""
import gc,hashlib,json,math,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(os.environ['CS549_G1_ROOT'])
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,guard_rows,guards_match,digest
from ue_formal_roster import prop,xyz
OUT=Path(os.environ['CS549_G1_OUT']);assert OUT.is_dir() and not (OUT/'result.json').exists()
STAGE=os.environ['CS549_G1_STAGE'];rows=guard_rows();assert len(rows)==703 and guards_match(rows)
selected_epoch=STORE/'Evidence/G1MissionV1/staging_author_v2_20261008/result.json'
config_file=STORE/('Evidence/G1MissionV1/staging_config_v2_20261008/config.json' if selected_epoch.exists() else 'Evidence/G1MissionV1/config_v1_20261008/config.json')
config=json.loads(config_file.read_text())
trial=json.loads((STORE/'Evidence/G1MissionV1/staging_config_v2_20261008/config.json').read_text()) if STAGE=='spawnview' else None
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
report={'identity':OUT.name,'stage':STAGE,'status':'initializing','errors':[],'checks':{},'samples':[],'captures':[],
 'deliberate_original_damage_fixture':STAGE in ('functional','outcomes'),'python_pose_driver':False,'protected_count':703}
phase='setup';callback=None;world=None;mission=None;roster={};started=time.monotonic();phase_time=0;last_sample=-1;busy=False;capture_wait_started=0
initial=None;expected=None;save_clock=0;load_called=False;old_generation=None
travel_points=[[1950,-20650,114.26299010216593],[5850,-20250,110.14999471592469]]
travel_index=0;travel_started=0;travel_deadline=0;regroup_started=None
view_index=0;view_yaws=(0,90,180,270)
reload_generation=None

def state():return json.loads(mission.read_mission_state())
def now():return unreal.GameplayStatics.get_time_seconds(world)
def write():
 report['observer_phase']=phase;report['elapsed_wall_seconds']=time.monotonic()-started
 (OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n')
def capture(name):
 path=OUT/(name+'.png')
 unreal.SystemLibrary.execute_console_command(world,'HighResShot 1280x720 filename="'+path.as_posix()+'"',unreal.GameplayStatics.get_player_controller(world,0))
 report['captures'].append(str(path.relative_to(ROOT)))
def finish(error=None):
 global phase,callback,capture_wait_started
 if error:report['errors'].append(error)
 if not report['errors'] and levels.is_in_play_in_editor() and any(not (ROOT/p).is_file() for p in report['captures']):
  phase='capture_wait';capture_wait_started=time.monotonic();write();return
 if levels.is_in_play_in_editor():levels.editor_request_end_play();phase='ending';write();return
 report['protected_unchanged']=guards_match(rows)
 report['status']='failed_mission_entry_preserve' if report['errors'] or not report['protected_unchanged'] else 'pass_'+STAGE+'_native_mission'
 phase='done';write()
 if callback is not None:unreal.unregister_slate_post_tick_callback(callback);callback=None
 unreal.SystemLibrary.quit_editor()
def snapshot():
 result=[]
 pc=unreal.GameplayStatics.get_player_controller(world,0)
 if pc:
  location,rotation=pc.get_player_view_point()
  report['view_diagnostics']={'location_cm':xyz(location),'rotation':[rotation.pitch,rotation.yaw,rotation.roll],
   'view_target':pc.get_view_target().get_path_name(),'viewport_size':list(pc.get_viewport_size())}
 for id,a in roster.items():
  c=unreal.AIHelperLibrary.get_ai_controller(a)
  result.append({'id':id,'health':prop(a,'Health'),'loaded':prop(a,'LoadedAmmo'),'reserve':prop(a,'ReserveAmmo'),
   'shots':prop(a,'ShotSequence'),'dead':prop(a,'IsDead'),'location_cm':xyz(a.get_actor_location()),
   'walking':a.character_movement.is_moving_on_ground(),'controller':c.get_class().get_path_name() if c else None,
   'brain_running':prop(c,'brain_component').is_running() if c and prop(c,'brain_component') else False})
 return result
def isolate_outcome_fixture():
 for a in list(roster.values())[1:]:
  c=unreal.AIHelperLibrary.get_ai_controller(a);c.call_method('PC_EnableCombat',args=(False,))
  prop(c,'brain_component').stop_logic('Finite mission-outcome fixture, not encounter evidence');c.stop_movement()
  a.get_component_by_class(unreal.PawnSensingComponent).set_sensing_updates_enabled(False)
def place_player(feet):
 p=roster['Player'];p.character_movement.stop_movement_immediately()
 assert p.set_actor_location(unreal.Vector(feet[0],feet[1],feet[2]+p.capsule_component.get_scaled_capsule_half_height()+.5),False,True)
def verify_isolated_journal():
 prefix=prop(mission,'slot_prefix');isolated='G1Corruption_'+OUT.name
 controls=[unreal.GameplayStatics.load_game_from_slot(prefix+s,0) for s in ('_A','_B')]
 assert all(controls)
 hashes=[(prop(x,'payload'),prop(x,'checksum')) for x in controls]
 assert [json.loads(x[0])['serial'] for x in hashes]==[1,2]
 assert not any(unreal.GameplayStatics.does_save_game_exist(isolated+s,0) for s in ('_A','_B')),'Preserve previous corruption fixture'
 def bad_save(variant):
  payload=json.loads(hashes[1][0])
  if variant=='schema':payload['schema']=99
  if variant=='identity':payload['actors'][1]['id']='Player'
  if variant=='ammo':payload['actors'][0]['reserve']+=1
  text=json.dumps(payload);obj=unreal.GameplayStatics.create_save_game_object(unreal.ParisBridgeSave)
  obj.set_editor_property('payload',text)
  obj.set_editor_property('checksum','invalid' if variant=='checksum' else hashlib.md5(text.encode()).hexdigest())
  return obj
 try:
  mission.set_editor_property('slot_prefix',isolated)
  assert unreal.GameplayStatics.save_game_to_slot(controls[0],isolated+'_A',0)
  assert unreal.GameplayStatics.save_game_to_slot(bad_save('checksum'),isolated+'_B',0)
  journal=json.loads(mission.inspect_checkpoint_journal());report['journal_fallback']=journal
  assert journal['valid'] and journal['serial']==1 and journal['snapshot']['phase']=='Ready',journal
  report['checks']['corrupt_newest_falls_back_to_previous_valid']=True
  for variant in ('checksum','schema','identity','ammo'):
   bad=bad_save(variant)
   for suffix in ('_A','_B'):assert unreal.GameplayStatics.save_game_to_slot(bad,isolated+suffix,0)
   before=state()['snapshot'];assert not mission.load_checkpoint(),variant
   assert state()['snapshot']==before,'Rejected load partially changed current state'
   report.setdefault('rejection_feedback',{})[variant]=state()['feedback']
   report['checks']['reject_'+variant+'_without_partial_restore']=True
 finally:
  mission.set_editor_property('slot_prefix',prefix)
  reread=[unreal.GameplayStatics.load_game_from_slot(prefix+s,0) for s in ('_A','_B')]
  assert [(prop(x,'payload'),prop(x,'checksum')) for x in reread]==hashes,'Valid controls changed'
  report['checks']['valid_control_slots_unchanged']=True
def tick(dt):
 global phase,world,mission,roster,initial,phase_time,last_sample,expected,save_clock,load_called,old_generation,travel_index,travel_started,travel_deadline,regroup_started,busy,view_index,reload_generation
 if busy:return
 busy=True
 try:
  assert time.monotonic()-started<420,'Bounded mission observer wall deadline'
  if phase=='ending':
   if not levels.is_in_play_in_editor():finish()
   return
  if phase=='capture_wait':
   if any(not (ROOT/p).is_file() for p in report['captures']):
    assert time.monotonic()-capture_wait_started<10,'Deferred native viewport capture missing'
    return
   finish();return
  if phase=='lifecycle_error':
   if now()-phase_time<.5:return
   assert state()['phase']=='Error' and not mission.save_checkpoint()
   report['checks']['unrecorded_required_actor_removal_errors_without_counted_kill_or_save']=True
   old_generation=state()['generation'];mission.restart_mission();phase='lifecycle_restart'
   mission=None;roster={};world=None;gc.collect();return
  if phase in ('lifecycle_restart','lifecycle_load'):
   world=editor.get_game_world();found=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisBridgeMission) if world else []
   if not found:return
   mission=found[0];s=state()
   if s['generation']==old_generation or s['phase']=='Preparing':return
   assert s['phase']=='Ready' and s['generation']!=old_generation
   roster={p['id']:unreal.GameplayStatics.get_all_actors_with_tag(world,unreal.Name('G1_'+p['id']))[0] for p in config['roster']}
   assert all(a['health']==100 and a['loaded']==2 and a['reserve']==16 and a['shots']==0 and not a['dead'] for a in snapshot())
   assert len(unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor))==5
   if phase=='lifecycle_restart':
    report['checks']['missing_actor_error_recovers_only_by_full_new_roster_restart']=True
    assert mission.save_checkpoint() and mission.start_mission();isolate_outcome_fixture()
    p=roster['Player'];p.call_method('PC_RequestReload',args=())
    assert str(prop(p,'ActionState'))=='Reloading';reload_generation=prop(p,'ReloadGeneration')
    assert not mission.save_checkpoint() and state()['save_serial']==1
    report['checks']['unsafe_reload_save_rejected_good_revision_retained']=True
    old_generation=state()['generation'];assert mission.load_checkpoint();phase='lifecycle_load'
    mission=None;roster={};world=None;gc.collect();return
   if s['ready_seconds']<4:return
   assert prop(roster['Player'],'RestoreGeneration')!=reload_generation
   assert str(prop(roster['Player'],'ActionState'))=='Ready'
   report['checks']['load_during_original_reload_new_generation_no_late_ammo_commit']=True
   assert mission.start_mission() and not mission.start_mission();report['checks']['restored_ready_start_once']=True
   capture('lifecycle_restored');finish();return
  if phase=='outcome_restart':
   world=editor.get_game_world();found=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisBridgeMission) if world else []
   if not found:return
   mission=found[0];s=state()
   if s['generation']==old_generation or s['phase']=='Preparing':return
   assert s['phase']=='Ready' and s['generation']!=old_generation
   roster={p['id']:unreal.GameplayStatics.get_all_actors_with_tag(world,unreal.Name('G1_'+p['id']))[0] for p in config['roster']}
   fresh=snapshot();assert all(x['health']==100 and x['loaded']==2 and x['reserve']==16 and x['shots']==0 and not x['dead'] for x in fresh)
   assert len(unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor))==5
   report['checks']['full_restart_new_generation_original_roster_resources_no_duplicate_bindings']=True
   assert mission.start_mission();isolate_outcome_fixture()
   for id in ('German1','German2','German3','Ally2'):roster[id].call_method('PC_ApplyDamage',args=(100.0,))
   place_player([5837.5,-20237.5,110.1500057220459]);phase='outcome_occupy_win';phase_time=now();return
  if phase=='setup':
   world=editor.get_game_world()
   if not world:return
   found=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisBridgeMission)
   if not found:return
   assert len(found)==1;mission=found[0]
   for p in config['roster']:
    found=unreal.GameplayStatics.get_all_actors_with_tag(world,unreal.Name('G1_'+p['id']))
    assert len(found)==1;roster[p['id']]=found[0]
   initial=snapshot();report['initial']=initial
   pc=unreal.GameplayStatics.get_player_controller(world,0)
   assert isinstance(pc,unreal.ParisBridgePlayerController)
   pc.set_control_rotation(unreal.Rotator(pitch=0,yaw=(trial or config)['roster'][0]['yaw'],roll=0))
   eye,_=pc.get_player_view_point();report['view_rays']=[]
   for yaw in (35,125,215,305):
    end=eye+unreal.Vector(math.cos(math.radians(yaw))*1000,math.sin(math.radians(yaw))*1000,0)
    hit=unreal.SystemLibrary.line_trace_single(world,eye,end,unreal.TraceTypeQuery.ECC_VISIBILITY,True,[roster['Player']],unreal.DrawDebugTrace.NONE,True)
    if hit is None:
     report['view_rays'].append({'yaw':yaw,'blocked':False,'point_cm':None,'actor':None});continue
    values=hit.to_tuple()
    report['view_rays'].append({'yaw':yaw,'blocked':values[0],'point_cm':xyz(values[5]),
      'actor':values[9].get_path_name() if values[9] else None})
   report['vertical_view_rays']=[]
   for direction in (-1,1):
    hit=unreal.SystemLibrary.line_trace_single(world,eye,eye+unreal.Vector(0,0,direction*10000),unreal.TraceTypeQuery.ECC_VISIBILITY,True,list(roster.values()),unreal.DrawDebugTrace.NONE,True)
    values=hit.to_tuple() if hit else None
    report['vertical_view_rays'].append({'direction':direction,'blocked':bool(values and values[0]),
      'point_cm':xyz(values[5]) if values else None,'actor':values[9].get_path_name() if values and values[9] else None})
   candidates=[];direction=(math.cos(math.radians(35)),math.sin(math.radians(35)),0)
   for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.StaticMeshActor):
    origin,extent=a.get_actor_bounds(False);lo=0;hi=2000
    for p,o,e,d in zip(xyz(eye),xyz(origin),xyz(extent),direction):
     if abs(d)<1e-8:
      if not o-e<=p<=o+e:hi=-1;break
     else:
      t=sorted(((o-e-p)/d,(o+e-p)/d));lo=max(lo,t[0]);hi=min(hi,t[1])
    if lo>hi:continue
    c=a.static_mesh_component;m=c.get_editor_property('static_mesh')
    candidates.append({'actor':a.get_path_name(),'mesh':m.get_path_name() if m else None,'bounds_ray_start_cm':lo,
      'origin_cm':xyz(origin),'extent_cm':xyz(extent),'collision':str(c.get_collision_enabled()),'actor_collision':a.get_actor_enable_collision(),'visible':c.is_visible()})
   report['render_ray_bounds_candidates']=sorted(candidates,key=lambda x:(x['bounds_ray_start_cm'],math.prod(x['extent_cm'])))[:20]
   report['lighting_streams']={}
   for name in ('LV_Lighting_Day','LV_Lighting_Midnight','LV_Lighting_WarFog'):
    stream=unreal.GameplayStatics.get_streaming_level(world,'/Game/WW2City/Maps/'+name)
    if stream:report['lighting_streams'][name]={'loaded':stream.is_level_loaded(),'visible':stream.is_level_visible()}
   report['scene_lights']=[]
   for cls,component in ((unreal.DirectionalLight,unreal.DirectionalLightComponent),(unreal.SkyLight,unreal.SkyLightComponent)):
    for light in unreal.GameplayStatics.get_all_actors_of_class(world,cls):
     c=light.get_component_by_class(component)
     report['scene_lights'].append({'actor':light.get_path_name(),'rotation':[light.get_actor_rotation().pitch,light.get_actor_rotation().yaw,light.get_actor_rotation().roll],
      'mobility':str(prop(c,'mobility')),'intensity':prop(c,'intensity'),'visible':c.is_visible()})
   report['post_process_exposure']=[]
   for volume in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.PostProcessVolume):
    settings=prop(volume,'settings')
    report['post_process_exposure'].append({'actor':volume.get_path_name(),'unbound':prop(volume,'unbound'),
      'priority':prop(volume,'priority'),'exposure':{n:str(prop(settings,n)) for n in
       ('auto_exposure_method','auto_exposure_min_brightness','auto_exposure_max_brightness','auto_exposure_bias',
        'override_auto_exposure_method','override_auto_exposure_min_brightness','override_auto_exposure_max_brightness','override_auto_exposure_bias')}})
   phase='ready';write();return
  if phase=='wait_load':
   world=editor.get_game_world()
   found=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisBridgeMission) if world else []
   if not found:return
   mission=found[0]
   if state()['generation']==old_generation or state()['phase']=='Preparing':return
   roster={p['id']:unreal.GameplayStatics.get_all_actors_with_tag(world,unreal.Name('G1_'+p['id']))[0] for p in config['roster']}
   phase='ready';return
  s=state()
  assert s['phase']!='Error',s
  if now()-last_sample>=.5:
   report['samples'].append({'time':now(),'mission':s,'actors':snapshot()});last_sample=now();write()
  if phase=='ready':
   if s['phase']=='Preparing':return
   if STAGE=='load':
    if not load_called:
     if s['phase']!='Ready':return
     old_generation=s['generation'];assert mission.load_checkpoint();load_called=True;phase='wait_load'
     mission=None;roster={};world=None;gc.collect();return
    expected_file=STORE/('Evidence/G1MissionV1/functional_v4_20261008/expected_save.json' if selected_epoch.exists() else 'Evidence/G1MissionV1/functional_v2_20261008/expected_save.json')
    expected=json.loads(expected_file.read_text())
    assert s['phase']==expected['phase'],(s,expected)
    verified=json.loads(prop(mission,'verified_restore_state'))
    assert verified['source_generation']!=expected['source_generation']
    for got,want in zip(verified['actors'],expected['actors']):
     for n in ('id','class','health','loaded','reserve','shots','dead'):assert got[n]==want[n],(n,got,want)
     assert math.dist(got['location'],want['location'])<1.0,(got,want)
    report['checks']['fresh_process_exact_restore']=True
    verify_isolated_journal()
    if selected_epoch.exists():
     prefix=prop(mission,'slot_prefix');before=state()['snapshot']
     mission.set_editor_property('slot_prefix','G1Functional2_20261008')
     try:
      assert not mission.load_checkpoint() and state()['snapshot']==before
      report['checks']['previous_staging_fingerprint_rejected_without_partial_restore']=True
     finally:mission.set_editor_property('slot_prefix',prefix)
    capture('restored');finish();return
   assert s['phase']=='Ready',s
   if s['ready_seconds']<10:return
   final=snapshot()
   for a,b in zip(initial,final):
    assert all(a[n]==b[n] for n in ('id','health','loaded','reserve','shots','dead')),(a,b)
    assert math.dist(a['location_cm'][:2],b['location_cm'][:2])<35 and b['walking'] and not b['brain_running'],(a,b)
   bindings=list(unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisNPCGripActor))
   assert len(bindings)==5
   for a in list(roster.values())[1:]:
    c=unreal.AIHelperLibrary.get_ai_controller(a);assert prop(c,'BootstrapReady') and not prop(c,'CombatEnabled')
    assert len([b for b in bindings if prop(b,'Target')==a and prop(b,'Initialized')])==1
    pp=a.mesh.get_post_process_instance();assert pp and prop(pp,'ValidInput') and prop(pp,'Evaluations')>0 and prop(pp,'ProtectionError')<.0001
   assert len({prop(unreal.AIHelperLibrary.get_ai_controller(a),'blackboard').get_path_name() for a in list(roster.values())[1:]})==5
   report['checks']['ready_ten_seconds_no_actions']=True;report['checks']['five_selected_bindings_private_blackboards']=True
   capture('ready');phase='ready_capture';phase_time=now();return
  if phase=='ready_capture':
   if now()-phase_time<1:return
   if STAGE in ('view','spawnview'):
    unreal.GameplayStatics.get_player_controller(world,0).set_control_rotation(unreal.Rotator(pitch=0,yaw=view_yaws[0],roll=0))
    phase='view_turn';phase_time=now();return
   if STAGE=='ready':
    assert not mission.load_checkpoint(),'Ready fixture must start without a save'
    report['checks']['no_save_rejected_without_travel']=state()['phase']=='Ready'
    assert mission.start_mission();assert not mission.start_mission();report['checks']['start_once']=state()['phase']=='Crossing'
    phase='started';phase_time=now();return
   if STAGE=='functional':
    assert mission.save_checkpoint();report['checks']['ready_save_readback']=state()['save_serial']==1
    assert mission.start_mission();isolate_outcome_fixture()
    old_config=json.loads((STORE/'Evidence/G1MissionV1/config_v1_20261008/config.json').read_text())
    report['isolated_save_fixture_one_time_allied_placements']=[]
    for placement in old_config['roster'][:3]:
     a=roster[placement['id']];feet=placement['feet_cm'];a.character_movement.stop_movement_immediately()
     assert a.set_actor_location(unreal.Vector(feet[0],feet[1],feet[2]+a.capsule_component.get_scaled_capsule_half_height()+.5),False,True)
     report['isolated_save_fixture_one_time_allied_placements'].append(placement)
    phase='fixture';phase_time=now();return
   if STAGE=='travel':
    assert mission.start_mission()
    # Isolate navigation only; these hidden live defenders are not encounter evidence.
    for id in ('German1','German2','German3'):
     a=roster[id];c=unreal.AIHelperLibrary.get_ai_controller(a)
     c.call_method('PC_EnableCombat',args=(False,));prop(c,'brain_component').stop_logic('G1 corridor-only fixture')
     a.set_actor_hidden_in_game(True)
    report['travel_enemy_behavior_isolated']=True;phase='travel_request';return
   if STAGE=='encounter':
    assert mission.start_mission();phase='encounter';phase_time=now();return
   if STAGE=='outcomes':
    assert not mission.load_checkpoint(),'Outcome fixture must have no saved result initially'
    report['checks']['no_save_rejected_without_travel']=state()['phase']=='Ready'
    assert mission.start_mission();isolate_outcome_fixture()
    for id in ('German1','German2','German3','Ally2'):roster[id].call_method('PC_ApplyDamage',args=(100.0,))
    place_player([7087.5,-20287.5,132.78399721182612]);phase='outcome_order';phase_time=now();return
   if STAGE=='lifecycle':
    assert mission.start_mission();isolate_outcome_fixture();roster['Ally1'].destroy_actor()
    phase='lifecycle_error';phase_time=now();return
   raise AssertionError('Travel/encounter require their separately frozen native runner')
  if phase=='view_turn':
   if now()-phase_time<1:return
   report.setdefault('cardinal_views',[]).append({'requested_yaw':view_yaws[view_index],'view':report['view_diagnostics']})
   capture('view_yaw_'+str(view_yaws[view_index]));phase='view_next';phase_time=now();return
  if phase=='view_next':
   if now()-phase_time<1:return
   view_index+=1
   if view_index==len(view_yaws):
    assert state()['phase']=='Ready' and all(x['shots']==0 and x['health']==100 for x in snapshot())
    report['checks']['readonly_four_cardinal_views_no_start_resources_unchanged']=True;finish();return
   unreal.GameplayStatics.get_player_controller(world,0).set_control_rotation(unreal.Rotator(pitch=0,yaw=view_yaws[view_index],roll=0))
   phase='view_turn';phase_time=now();return
  if phase=='started':
   if now()-phase_time<1:return
   assert all(prop(unreal.AIHelperLibrary.get_ai_controller(a),'CombatEnabled') for a in list(roster.values())[1:])
   report['checks']['retained_combat_released']=True;capture('started');finish();return
  if phase=='fixture':
   if now()-phase_time<.5:return
   p=roster['Player'];p.call_method('PC_ApplyDamage',args=(25.0,))
   roster['Ally2'].call_method('PC_ApplyDamage',args=(100.0,));roster['German1'].call_method('PC_ApplyDamage',args=(100.0,))
   eye=p.get_actor_location()+unreal.Vector(0,0,40)
   p.call_method('PC_RequestFire',args=(eye,unreal.Vector(.5,0,.866025403784)))
   report['original_fire_result']={n:prop(p,n) for n in ('LoadedAmmo','ReserveAmmo','ShotSequence')}
   report['original_fire_result']['ActionState']=str(prop(p,'ActionState'))
   assert prop(p,'ShotSequence')==1 and prop(p,'LoadedAmmo')==1,'Original finite shot was not admitted'
   phase='save_nondefault';phase_time=now();return
  if phase=='outcome_order':
   if now()-phase_time<.5:return
   assert s['phase']=='Crossing' and s['living_defenders']==0 and s['living_allies']==1
   report['checks']['early_kills_retained_ally_death_not_failure_out_of_order_reach_rejected']=True
   place_player([5837.5,-20237.5,110.1500057220459]);phase='outcome_occupy_loss';phase_time=now();return
  if phase=='outcome_occupy_loss':
   if now()-phase_time<.5:return
   assert s['phase']=='Occupying';report['checks']['sealed_clear_after_reach']=True
   place_player([7087.5,-20287.5,132.78399721182612]);roster['Player'].call_method('PC_ApplyDamage',args=(100.0,))
   phase='outcome_loss';phase_time=now();return
  if phase=='outcome_loss':
   if now()-phase_time<.5:return
   assert s['phase']=='Lost';report['checks']['same_update_player_death_wins_over_occupation']=True
   assert not mission.save_checkpoint();report['checks']['lost_save_rejected']=True
   old_generation=s['generation'];mission.restart_mission();phase='outcome_restart'
   mission=None;roster={};world=None;gc.collect();return
  if phase=='outcome_occupy_win':
   if now()-phase_time<.5:return
   assert s['phase']=='Occupying'
   place_player([7087.5,-20287.5,132.78399721182612]);phase='outcome_win';phase_time=now();return
  if phase=='outcome_win':
   if now()-phase_time<.5:return
   assert s['phase']=='Won' and s['living_allies']==1 and s['living_defenders']==0
   report['checks']['living_occupation_wins_with_ally_casualty']=True
   if not mission.save_checkpoint():
    assert now()-phase_time<5,'Won snapshot not saveable';return
   report['checks']['won_result_saved']=True;capture('won');finish();return
  if phase=='save_nondefault':
   assert now()-phase_time<30,'No stable save boundary within declared deadline'
   if not mission.save_checkpoint():return
   expected=state()['snapshot'];report['expected_save']=expected
   assert expected['phase']=='Crossing' and expected['actors'][0]['health']==75 and expected['actors'][0]['loaded']==1
   assert expected['actors'][2]['dead'] and expected['actors'][3]['dead']
   (OUT/'expected_save.json').write_text(json.dumps(expected,indent=2)+'\n')
   report['checks']['nondefault_snapshot_two_casualties_and_spent_round']=True
   # Bad-slot mutation belongs to the independent fresh-load stage and namespace.
   capture('saved_nondefault');finish();return
  if phase=='travel_request':
   pc=unreal.GameplayStatics.get_player_controller(world,0);p=roster['Player'];goal=unreal.Vector(*travel_points[travel_index])
   v=goal-p.get_actor_location();heading=math.degrees(math.atan2(v.y,v.x));pc.set_control_rotation(unreal.Rotator(pitch=0,yaw=heading,roll=0))
   systems=[n for n in unreal.ObjectIterator(unreal.NavigationSystemV1) if 'Default__' not in n.get_path_name() and n.get_outer()==world]
   assert len(systems)==1
   route=systems[0].call_method('FindPathToLocationSynchronously',args=(world,p.get_actor_location(),goal,p,None))
   assert route and route.is_valid() and not route.is_partial(),'Frozen corridor query incomplete'
   points=[xyz(x) for x in prop(route,'path_points')];length=sum(math.dist(a,b) for a,b in zip(points,points[1:]))
   report.setdefault('legs',[]).append({'index':travel_index,'goal_feet_cm':travel_points[travel_index],'path_cm':points,'length_cm':length,'heading':heading})
   unreal.AIHelperLibrary.simple_move_to_location(pc,goal)
   travel_started=now();travel_deadline=travel_started+length/300*2+20;regroup_started=None;phase='travel_move';return
  if phase=='encounter':
   if now()-phase_time<30 and state()['phase']!='Lost':return
   final=snapshot();allied=sum(x['shots'] for x in final if x['id'].startswith('Ally'));german=sum(x['shots'] for x in final if x['id'].startswith('German'))
   report['encounter_final']=final;report['actual_faction_shots']={'allied':allied,'german':german}
   assert allied>0 and german>0,'Both factions did not actually shoot'
   assert any(x['health']<100 for x in final if x['id'].startswith('Ally')) and any(x['health']<100 for x in final if x['id'].startswith('German')),'Two-sided hostile damage not observed'
   report['checks']['bridgehead_two_sided_native_encounter']=True;capture('encounter_final');finish();return
  if phase=='travel_move':
   p=roster['Player'];goal=travel_points[travel_index];feet=p.get_actor_location()-unreal.Vector(0,0,p.capsule_component.get_scaled_capsule_half_height())
   assert now()<travel_deadline,'Player did not physically arrive in the frozen distance-scaled window'
   assert state()['phase'] not in ('Lost','Error'),'Travel isolation failed'
   if math.dist(xyz(feet)[:2],goal[:2])>55:return
   if regroup_started is None:regroup_started=now()
   allies=[]
   for id in ('Ally1','Ally2'):
    a=roster[id];c=unreal.AIHelperLibrary.get_ai_controller(a);held=prop(c,'HeldGoal')
    error=math.dist(xyz(a.get_actor_location()),xyz(held))
    allies.append({'id':id,'feet_cm':xyz(a.get_actor_location()-unreal.Vector(0,0,a.capsule_component.get_scaled_capsule_half_height())),
     'held_goal_cm':xyz(held),'body_error_cm':error,'squad_failed':prop(c,'SquadFailed')})
   report['legs'][-1]['actual_player_feet_cm']=xyz(feet);report['legs'][-1]['allies']=allies
   if not all(x['body_error_cm']<=55 and not x['squad_failed'] for x in allies):
    assert now()-regroup_started<25,'Both Allies did not regroup within original55cm/25s gate'
    return
   report['legs'][-1]['actual_elapsed_seconds']=now()-travel_started;capture('travel_leg_'+str(travel_index))
   travel_index+=1
   if travel_index==len(travel_points):
    assert all(x['feet_cm'][0]>=5600 for x in allies),'An Ally remains west of the far-bank gate'
    report['checks']['player_two_allies_actual_bridge_corridor']=True;finish();return
   phase='travel_request';return
 except Exception:finish(traceback.format_exc())
 finally:busy=False

try:
 assert levels.load_level(config['map'])
 author_file=STORE/'Evidence/G1MissionV1/bridge_hook_v1_20261008/result.json'
 if not author_file.exists():author_file=STORE/'Evidence/G1MissionV1/headings_v1_20261008/result.json'
 if selected_epoch.exists():author_file=selected_epoch
 author=json.loads(author_file.read_text());report['owned_admission']=str(author_file.relative_to(ROOT))
 assert author['status'].startswith('pass_')
 assert author['map_saved'] and author['protected_unchanged'] and author['collision_restored']
 assert all(digest(ROOT/f['path'])==f['sha256'] for f in author['files'])
 aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();lookup={a.get_actor_label():a for a in aa}
 for p in config['roster']:
  a=lookup[p['label']];feet=a.get_actor_location()-unreal.Vector(0,0,a.capsule_component.get_scaled_capsule_half_height())
  assert math.dist(xyz(feet),p['feet_cm'])<1 and a.get_actor_enable_collision()
  assert unreal.Name('G1_'+p['id']) in prop(a,'tags')
  rotation=a.get_actor_rotation();assert abs(rotation.pitch)<1e-8 and abs(rotation.roll)<1e-8 and abs(rotation.yaw-p['yaw'])<1e-8
  if p['id']!='Player':assert prop(a,'ai_controller_class').get_path_name()==config['controller']+'.BP_PCG1ControllerV1_C'
 assert editor.get_editor_world().get_world_settings().get_editor_property('default_game_mode')==unreal.ParisBridgeGameMode.static_class()
 mesh=next(a for a in aa if isinstance(a,unreal.RecastNavMesh))
 saved=json.loads(unreal.ParisMapSurveyLibrary.export_navmesh(mesh))
 assert len(saved['polygons'])==author['nav_polygons'] and saved['active_tiles']==author['nav_tiles']
 report['checks']['fresh_saved_map_roster_navigation']=True
 editor_mission=next(a for a in aa if isinstance(a,unreal.ParisBridgeMission))
 if STAGE=='encounter':
  encounter=json.loads((STORE/'Evidence/G1MissionV1/encounter_config_v2_20261008/config.json').read_text());report['encounter_frozen_config']=encounter
  for p in config['roster']:
   if p['id'] not in encounter['points']:continue
   a=lookup[p['label']];feet=encounter['points'][p['id']]['feet_cm'];h=a.capsule_component.get_scaled_capsule_half_height()
   a.set_actor_location_and_rotation(unreal.Vector(feet[0],feet[1],feet[2]+h+.5),unreal.Rotator(pitch=0,yaw=0,roll=0),False,True)
 if STAGE=='spawnview':
  report['unsaved_staging_trial']=trial
  for p in trial['roster'][:3]:
   a=lookup[p['label']];feet=p['feet_cm'];h=a.capsule_component.get_scaled_capsule_half_height()
   assert a.set_actor_location_and_rotation(unreal.Vector(feet[0],feet[1],feet[2]+h+.5),unreal.Rotator(pitch=0,yaw=p['yaw'],roll=0),False,True)
 editor_mission.set_editor_property('slot_prefix','G1Functional_20261008' if STAGE in ('functional','load') else 'G1Ready_20261008')
 if STAGE=='load':
  # Explicit world URL loading is used in ordinary runtime; PIE invokes its native load entry after startup.
  pass
 levels.editor_request_begin_play();callback=unreal.register_slate_post_tick_callback(tick)
except Exception:finish(traceback.format_exc())
