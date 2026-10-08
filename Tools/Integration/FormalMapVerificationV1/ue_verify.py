"""Bounded unsaved formal-body/native-policy map verification, not mission authoring."""
import ast,json,math,os,sys,time,traceback
from pathlib import Path
import unreal

ROOT=Path(os.environ['CS549_FORMAL_ROOT']);OUT=Path(os.environ['CS549_FORMAL_OUT'])
STAGE=os.environ['CS549_FORMAL_STAGE'];CATEGORY=os.environ.get('CS549_FORMAL_CATEGORY','flat')
BOOTSTRAP_LATCH=os.environ.get('CS549_FORMAL_LATCH','0')=='1'
assert not BOOTSTRAP_LATCH or (STAGE=='Encounter' and CATEGORY=='height')
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,guard_rows,guards_match,digest
from ue_formal_roster import LABELS,MAP,prop,xyz,actor_state,ready_snapshot
BANK_PATH=STORE/'Evidence/FormalMapVerificationV1/case_bank_v3_20261007/cases.json'
bank=json.loads(BANK_PATH.read_text());routes=bank['routes'];rows=guard_rows()
assert len(rows)==703 and guards_match(rows)
(OUT/'guards_before.json').write_text(json.dumps(rows)+'\n')
report={'identity':OUT.name,'stage':STAGE,'category':CATEGORY,'errors':[],'cases':[],'captures':[],
    'status':'initializing','map_saved':False,'nav_rebuilt':False,'final_layout_selected':False,
    'all_coordinates_temporary_tests':True,'bank_sha256':digest(BANK_PATH),'current_guards':703,
    'python_pose_or_ai_decision_driver':False,'original_player_possession_preserved':True,
    'helper_sha256':digest(ROOT/'Unreal/ParisStreetCombat/Plugins/ParisFormalSurveyV1/Binaries/Win64/UnrealEditor-ParisFormalSurveyV1.dll'),
    'pure_helper_sha256':digest(ROOT/'Unreal/ParisStreetCombat/Plugins/ParisMapSurveyV1/Binaries/Win64/UnrealEditor-ParisMapSurveyV1.dll'),
    'source_plan_sha256':digest(ROOT/'Docs/Development/MissionLoopV1/FORMAL_ROLE_SQUAD_TEST_PLAN_20261007.md')}
report['pre_admission_latch_enabled']=BOOTSTRAP_LATCH
report['bootstrap_latches']=[]
if BOOTSTRAP_LATCH:report['height_admission_plan_sha256']=digest(ROOT/'Docs/Development/MissionLoopV1/FORMAL_HEIGHT_ADMISSION_PLAN_20261007.md')
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
phase='setup';busy=False;callback=None;started=time.monotonic();phase_time=0;sample_time=0
world=pc=nav=camera=perf=scene_capture=render_target=None;old_throttle=None
bodies=[];controllers=[];queue=[];current=None;vehicles=[];vehicle_origins={};vehicle_snapshots={}
active=[];saved_profiles=[];initial_resources=[];fp=None;previous_case=None;binding_actors=[];latched={}

# Reuse only the three admitted static-fixture functions, without importing its
# module or registering that module's survey callback.
vehicle_source=STORE/'Evidence/PureMapSurveyV1/fixed_static_vehicle_v20_20261007/ue_pure_map_survey.py'
assert digest(vehicle_source)=='3c7af06e369be26fa40f6579b98ecd2c502af442c6cf7737890c8a80f542fc2e'
tree=ast.parse(vehicle_source.read_text())
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vehicle_snapshot','freeze_environment_vehicle')]
assert len(functions)==2
exec(compile(ast.Module(body=functions,type_ignores=[]),str(vehicle_source),'exec'),globals())

def write():
    report['phase']=phase;report['elapsed_wall_seconds']=time.monotonic()-started
    report['summary']={'planned':report.get('planned_cases',0),'recorded':len(report['cases']),
        'passed':sum(c.get('status')=='passed' for c in report['cases']),
        'negative':sum(c.get('status')=='negative' for c in report['cases']),
        'unmeasured':report.get('planned_cases',0)-sum(c.get('status') in ('passed','negative') for c in report['cases'])}
    temp=OUT/'result.writing.json';temp.write_text(json.dumps(report,indent=2)+'\n');temp.replace(OUT/'result.json')

def resource(a):return [prop(a,n) for n in ('Health','LoadedAmmo','ReserveAmmo','ShotSequence','IsDead')]
def native(a):
    d=json.loads(unreal.ParisFormalSurveyLibrary.read_formal_character(a));assert not d.get('error'),d;return d
def control(c):
    d=json.loads(unreal.ParisFormalSurveyLibrary.read_formal_controller(c));assert not d.get('error'),d;return d
def call(a,n,*args):a.call_method(n,args=args)
def game_time():return unreal.GameplayStatics.get_time_seconds(world)

def finish(error=None):
    global phase,callback
    if error:report['errors'].append(error)
    if levels.is_in_play_in_editor():
        for c in controllers:
            if c:c.stop_movement()
        levels.editor_request_end_play();phase='ending';write();return
    if perf is not None:perf.set_editor_property('bThrottleCPUWhenNotForeground',old_throttle)
    report['protected_bytes_unchanged']=guards_match(rows)
    if not report['protected_bytes_unchanged']:report['errors'].append('Protected bytes changed')
    report['status']='failed_global_admission' if report['errors'] else 'complete_bounded_formal_verification_with_negatives_retained'
    for image in report['captures']:image['exists']=(OUT/image['file']).exists()
    phase='done';write()
    if callback is not None:unreal.unregister_slate_post_tick_callback(callback);callback=None
    unreal.SystemLibrary.quit_editor()

def move_place(a,feet,facing=None,hidden=True):
    c=unreal.AIHelperLibrary.get_ai_controller(a)
    if c:c.stop_movement()
    a.character_movement.stop_movement_immediately()
    h=a.capsule_component.get_scaled_capsule_half_height()
    a.set_actor_location(unreal.Vector(feet[0],feet[1],feet[2]+h+3),False,False)
    a.set_actor_hidden_in_game(hidden)
    if facing is not None:
        rotation=unreal.MathLibrary.find_look_at_rotation(a.get_actor_location(),unreal.Vector(facing[0],facing[1],feet[2]+h))
        a.set_actor_rotation(rotation,False)
        controller=pc if bodies and a==bodies[0] else c
        if controller:controller.set_control_rotation(rotation)

def standing(i,feet):
    a=bodies[i];d=native(a);body=unreal.Vector(*d['body_cm'])
    overlaps=unreal.SystemLibrary.capsule_overlap_components(world,body,d['radius_cm'],d['half_height_cm'],
        [unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1,unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY2,unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY3],None,[a])
    if isinstance(overlaps,tuple) and any(isinstance(x,bool) for x in overlaps):
        arrays=[x for x in overlaps if not isinstance(x,bool) and hasattr(x,'__iter__')];assert len(arrays)==1;parts=list(arrays[0])
    elif isinstance(overlaps,bool):assert not overlaps;parts=[]
    else:parts=list(overlaps or [])
    blockers=[x.get_path_name() for x in parts if x.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)==unreal.CollisionResponseType.ECR_BLOCK]
    d.update({'index':i,'xy_error_cm':math.dist(d['feet_cm'][:2],feet[:2]),'feet_error_cm':abs(d['feet_cm'][2]-feet[2]),'blockers':blockers})
    d['standing_pass']=d['xy_error_cm']<=35 and d['feet_error_cm']<=35 and not blockers and d['movement_mode']==1 and d['walkable_floor']
    return d

def invariant():
    assert unreal.GameplayStatics.get_player_pawn(world,0)==bodies[0] and bodies[0].get_controller()==pc,'Lost original player possession'
    assert prop(fp,'Initialized') and not str(prop(fp,'BindingError')),'FP native binding lost'
    for i,a in enumerate(bodies):
        current_profile=native(a)
        for key in ('class','radius_cm','half_height_cm','max_speed_cm_s','max_step_cm','slope_degrees','gravity_scale','rvo'):
            assert current_profile[key]==saved_profiles[i][key],('Formal profile changed',i,key)
        if STAGE!='Encounter':assert resource(a)==initial_resources[i],('Resource changed in locomotion fixture',i,resource(a))
        assert prop(a.mesh,'skeletal_mesh_asset').get_path_name()==report['editor_roster'][i]['mesh']
    for v in vehicles:
        assert vehicle_snapshot(v)==vehicle_snapshots[v.get_path_name()],'Static vehicle field changed'
        drift=math.dist(xyz(v.get_actor_location()),vehicle_origins[v.get_path_name()])
        report['vehicle_max_drift_cm']=max(report.get('vehicle_max_drift_cm',0),drift);assert drift==0

def isolate_policies():
    for i,c in enumerate(controllers[1:],1):
        call(c,'PC_EnableCombat',False);call(c,'PC_EnablePolicy',False);call(c,'PC_EnableSquad',False);call(c,'PC_PolicyHold')
        prop(c,'brain_component').stop_logic('Bounded formal map locomotion isolation')
        bodies[i].get_component_by_class(unreal.PawnSensingComponent).set_sensing_updates_enabled(False)

def frame_capture(now):
    middle=(unreal.Vector(*current['source_cm'])+unreal.Vector(*current['goal_cm']))*.5
    look=middle+unreal.Vector(0,0,95);location=middle+unreal.Vector(250,-200,650)
    camera.set_actor_location(location,False,False)
    camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(location,look),False)
    current['camera_fixed_game_seconds']=now

def capture(name,now):
    if not active:return
    path=OUT/(name+'.png')
    scene_capture.capture_scene()
    unreal.RenderingLibrary.export_render_target(world,render_target,OUT.as_posix(),path.name)
    assert path.is_file() and path.stat().st_size>10000,'Native render-target export missing'
    rot=camera.get_actor_rotation()
    report['captures'].append({'file':path.name,'request_game_seconds':now,'case':current['id'],'frozen':False,
        'positions_cm':[xyz(bodies[i].get_actor_location()) for i in active],'not_full_motion_acceptance':True,
        'mechanism':'native whole-scene render target, fixed unsaved diagnostic view',
        'camera_location_cm':xyz(camera.get_actor_location()),'camera_rotation':[rot.pitch,rot.yaw,rot.roll],
        'camera_fixed_game_seconds':current['camera_fixed_game_seconds'],'gameplay_view_target':pc.get_view_target().get_path_name()})

def begin_case(spec,now):
    global active,current,phase,phase_time,sample_time
    isolate_policies()
    route=routes[spec['route']];direction=spec.get('direction','out')
    source=route['source_cm'] if direction=='out' else route['goal_cm']
    goal=route['goal_cm'] if direction=='out' else route['source_cm']
    starts=route['source_sites'] if direction=='out' else route['goal_sites']
    goals=route['goal_sites'] if direction=='out' else route['source_sites']
    current={**spec,'category':route['category'],'status':'standing','samples':[],'members':[],'placements':[],
        'started_game_seconds':now,'source_cm':source,'goal_cm':goal}
    active=spec['members']
    for i,a in enumerate(bodies):
        if i not in active:move_place(a,bank['parking_sites'][i]['feet_cm'],hidden=True)
    if spec['kind']=='allied_follow':
        move_place(bodies[0],route['leader_'+direction]['feet_cm'],goal,True)
        # Leader heading is the declared route direction, not its short vector
        # back toward the follower endpoint.
        rotation=unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*source),unreal.Vector(*goal))
        bodies[0].set_actor_rotation(rotation,False);pc.set_control_rotation(rotation)
    for slot,i in enumerate(active):
        p=source if spec['kind']=='solo' else starts[slot]['feet_cm']
        target=goal if spec['kind']=='solo' else goals[slot]['feet_cm']
        if spec['kind']=='opposing' and i>=3:p=route['goal_sites'][slot-2]['feet_cm'];target=route['source_sites'][slot-2]['feet_cm']
        continuity=(spec['kind']=='solo' and direction=='back' and previous_case and previous_case['status']=='passed' and previous_case['members'][0]['index']==i)
        if not continuity:move_place(bodies[i],p,target,False)
        else:bodies[i].set_actor_hidden_in_game(False)
        current['members'].append({'index':i,'source_cm':p,'goal_cm':target,'source_placement':not bool(continuity)})
        current['placements'].append({'index':i,'feet_cm':p,'continuity_from_previous':bool(continuity)})
    frame_capture(now)
    report['cases'].append(current);phase='settle';phase_time=now;sample_time=now;write()

def reject(reason,now,details=None):
    global phase,previous_case
    current.update({'status':'negative','reason':reason,'ended_game_seconds':now,'details':details})
    for i in active:controllers[i].stop_movement()
    previous_case=current;phase='next';write()
    if STAGE=='Early':finish('Early physical gate failed: '+reason)

def sample_members(now):
    result=[]
    for m in current['members']:
        i=m['index'];a=bodies[i];d=native(a);c=controllers[i]
        d.update({'index':i,'speed_cm_s':a.get_velocity().length(),'controller':control(c),'resources':resource(a)})
        if i>0:
            d.update({'slot':prop(c,'FormationSlot'),'reservation':prop(c,'SquadReservationID'),'held_goal_cm':xyz(prop(c,'HeldGoal')),
                'squad_mode':str(prop(c,'SquadMode')),'squad_failed':prop(c,'SquadFailed'),'retry':prop(c,'blackboard').get_value_as_int('RetryCount')})
            if current['kind']=='allied_follow' and d['slot'] in (0,1):
                raw=bodies[0].get_actor_location()-bodies[0].get_actor_forward_vector()*400+bodies[0].get_actor_right_vector()*(-200 if d['slot']==0 else 200)
                d['raw_leader_slot_body_cm']=xyz(raw)
        result.append(d)
    current['samples'].append({'game_seconds':now,'world_frame_seconds':unreal.GameplayStatics.get_world_delta_seconds(world),'members':result})
    return result

def encounter_setup(now):
    global current,active,phase,phase_time,sample_time
    route=next(r for r in routes if r['category']==CATEGORY)
    active=[1,2,3,4,5]
    current={'id':'encounter_'+CATEGORY,'kind':'encounter','category':CATEGORY,'status':'standing','members':[],
        'samples':[],'source_cm':route['source_cm'],'goal_cm':route['goal_cm'],'started_game_seconds':now,'seen_factions':[],
        'real_opponent_shot_factions':[],'enemy_health_loss':False,'shot_events':[],'dead_observations':{}}
    for i in active:
        site=route['source_sites'][i-1] if i<3 else route['goal_sites'][i-3]
        state=standing(i,site['feet_cm']);current['members'].append({'index':i,'initial_standing':state})
    report['cases'].append(current)
    if not all(m['initial_standing']['standing_pass'] for m in current['members']):reject('encounter_initial_standing_rejected',now,current['members']);return
    for i in active:
        c=controllers[i];bodies[i].set_actor_hidden_in_game(False)
        facing=route['goal_cm'] if i<3 else route['source_cm']
        rotation=unreal.MathLibrary.find_look_at_rotation(bodies[i].get_actor_location(),unreal.Vector(*facing)+unreal.Vector(0,0,95))
        bodies[i].set_actor_rotation(rotation,False);c.set_control_rotation(rotation)
        call(c,'PC_EnableCombat',True);call(c,'PC_EnablePolicy',True)
        bodies[i].get_component_by_class(unreal.PawnSensingComponent).set_sensing_updates_enabled(True)
        prop(c,'brain_component').restart_logic()
    current['initial_los']=[{'observer':i,'opponent':j,'los':controllers[i].line_of_sight_to(bodies[j],unreal.Vector(),False)} for i in active for j in active if prop(bodies[i],'TeamId')!=prop(bodies[j],'TeamId')]
    current['initial_resources']=[resource(a) for a in bodies]
    current['native_guard_anchors']=[xyz(prop(c,'GuardAnchor')) for c in controllers[1:]]
    frame_capture(now)
    phase='encounter';phase_time=now;sample_time=now;write()

def tick(_delta):
    global busy,phase,phase_time,sample_time,world,pc,nav,camera,perf,old_throttle,bodies,controllers,fp,saved_profiles,initial_resources,queue,previous_case,callback,scene_capture,render_target
    if busy or phase=='done':return
    busy=True
    try:
        assert time.monotonic()-started<840,'Owned bounded test deadline'
        if (OUT/'STOP_REQUEST.json').exists() and phase!='ending':finish('Owned strict-log stop: '+(OUT/'STOP_REQUEST.json').read_text());return
        if phase=='ending':
            if editor.get_game_world() is None:finish()
            return
        if phase=='setup':
            phase='loading';assert levels.load_level(MAP)
            lookup={a.get_actor_label():a for a in actors.get_all_level_actors()}
            selected=[lookup[n] for n in ('PC_City_Player',*LABELS)]
            report['editor_roster']=[actor_state(a) for a in selected]
            for a in selected:a.set_actor_hidden_in_game(True)
            if STAGE=='Encounter':
                r=next(x for x in routes if x['category']==CATEGORY)
                for i,a in enumerate(selected):
                    feet=r['leader_out']['feet_cm'] if i==0 else (r['source_sites'][i-1]['feet_cm'] if i<3 else r['goal_sites'][i-3]['feet_cm'])
                    h=a.capsule_component.get_scaled_capsule_half_height();a.set_actor_location(unreal.Vector(feet[0],feet[1],feet[2]+h+3),False,False)
            camera=actors.spawn_actor_from_class(unreal.SceneCapture2D,selected[0].get_actor_location(),unreal.Rotator());camera.set_actor_label('FormalMapVerificationCamera')
            perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
            old_throttle=perf.get_editor_property('bThrottleCPUWhenNotForeground');perf.set_editor_property('bThrottleCPUWhenNotForeground',False)
            report['navigation_scope']='saved formal navigation only, no manual rebuild or bounds edit'
            levels.editor_request_begin_play();phase='ready';write();return
        world=editor.get_game_world()
        if world is None:return
        now=game_time()
        if phase=='ready':
            if BOOTSTRAP_LATCH:
                early_lookup={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)}
                for label in LABELS:
                    a=early_lookup.get(label)
                    if not a or label in latched:continue
                    c=unreal.AIHelperLibrary.get_ai_controller(a)
                    if not c or not prop(c,'BootstrapReady'):continue
                    flags={n:prop(c,n) for n in ('CombatEnabled','PolicyEnabled','SquadEnabled')}
                    assert all(flags.values()) and resource(a)==[100.0,2,16,0,False],'Native latch transition not pristine'
                    latched[label]=flags
                    report['bootstrap_latches'].append({'label':label,'game_seconds':now,'enabled_flags':flags,
                        'character':native(a),'controller':control(c),'resources':resource(a),
                        'original_editor_state':next(x for x in report['editor_roster'] if x['label']==label)})
                    call(c,'PC_EnableCombat',False);call(c,'PC_EnablePolicy',False);call(c,'PC_EnableSquad',False);call(c,'PC_PolicyHold')
                    c.stop_movement();prop(c,'brain_component').stop_logic('Once-only native bootstrap admission isolation')
                    a.get_component_by_class(unreal.PawnSensingComponent).set_sensing_updates_enabled(False)
                    write()
            if now<4:return
            assert now<40,'Native bootstrap admission deadline'
            lookup={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)}
            bodies=[lookup[n] for n in ('PC_City_Player',*LABELS)];pc=unreal.GameplayStatics.get_player_controller(world,0)
            controllers=[pc]+[unreal.AIHelperLibrary.get_ai_controller(a) for a in bodies[1:]]
            if not all(c and prop(c,'BootstrapReady') for c in controllers[1:]):return
            fps=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFirstPersonApprovedActor)
            if len(fps)!=1 or not prop(fps[0],'Initialized'):return
            if BOOTSTRAP_LATCH:
                assert len(latched)==5,'Missing original native Ready latch'
                for c in controllers[1:]:call(c,'PC_EnableCombat',True)
            fp=fps[0];report['equipment']=ready_snapshot(world,bodies[1:])
            assert all(resource(a)==[100.0,2,16,0,False] for a in bodies),'Depleted bootstrap is not admitted'
            assert len({prop(c,'blackboard').get_path_name() for c in controllers[1:]})==5
            saved_profiles=[native(a) for a in bodies];initial_resources=[resource(a) for a in bodies]
            report['formal_profiles']=saved_profiles;report['startup_resources']=initial_resources
            coordinator=lookup['PC_City_SquadCoordinator'];friendly=lookup['PC_City_FriendlyFirePolicy']
            assert len(unreal.GameplayStatics.get_all_actors_of_class(world,coordinator.get_class()))==1,'Duplicate squad coordinator'
            assert len(unreal.GameplayStatics.get_all_actors_of_class(world,friendly.get_class()))==1 and prop(friendly,'FriendlyFireEnabled') is False,'FF policy admission'
            report['global_policies']={'coordinator':coordinator.get_path_name(),'unique_coordinator':True,
                'friendly_fire_policy':friendly.get_path_name(),'friendly_fire_off':True}
            camera=lookup['FormalMapVerificationCamera']
            scene_capture=camera.get_component_by_class(unreal.SceneCaptureComponent2D)
            render_target=unreal.RenderingLibrary.create_render_target2d(world,1600,900,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(0,0,0,1),False,False)
            scene_capture.set_editor_property('texture_target',render_target)
            scene_capture.set_editor_property('primitive_render_mode',unreal.SceneCapturePrimitiveRenderMode.PRM_RENDER_SCENE_PRIMITIVES)
            scene_capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            scene_capture.set_editor_property('capture_every_frame',False);scene_capture.set_editor_property('capture_on_movement',False)
            scene_capture.set_editor_property('fov_angle',70)
            navs=[n for n in unreal.ObjectIterator(unreal.NavigationSystemV1) if 'Default__' not in n.get_path_name() and n.get_outer()==world];assert len(navs)==1;nav=navs[0]
            for v in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Pawn):
                if v.get_class().get_path_name().startswith('/Game/WW2City/CarsSet/'):
                    freeze_environment_vehicle(v);vehicles.append(v);vehicle_origins[v.get_path_name()]=xyz(v.get_actor_location())
            isolate_policies()
            report['native_bootstrap_gate']='pass_original_six_bodies_five_brains_selected_bindings_resources'
            if STAGE=='Encounter':report['planned_cases']=1;encounter_setup(now);return
            if STAGE in ('Early','Solo'):
                for route_index in ([0] if STAGE=='Early' else range(3)):
                    for i in ([0,1,3] if STAGE=='Early' else range(6)):
                        for direction in ('out','back'):queue.append({'id':f'{STAGE.lower()}_{route_index}_{i}_{direction}','kind':'solo','route':route_index,'members':[i],'direction':direction})
            else:
                for ri in range(3):
                    for kind,members in [('allied_follow',[1,2]),('german_traffic',[3,4,5])]:
                        for direction in ('out','back'):queue.append({'id':f'{kind}_{ri}_{direction}','kind':kind,'route':ri,'members':members,'direction':direction})
                for ri in (0,1):queue.append({'id':f'opposing_{ri}','kind':'opposing','route':ri,'members':[1,2,3,4,5],'direction':'out'})
            report['planned_cases']=len(queue);phase='next';write();return
        invariant()
        if phase=='next':
            if not queue:finish();return
            begin_case(queue.pop(0),now);return
        if phase=='settle':
            if now-phase_time<.6:return
            for m in current['members']:m['standing']=standing(m['index'],m['source_cm'])
            if not all(m['standing']['standing_pass'] for m in current['members']):reject('source_standing_rejected',now,[m['standing'] for m in current['members']]);return
            if current['kind']=='allied_follow':
                for i in active:
                    c=controllers[i];control(c);call(c,'PC_EnablePolicy',True);call(c,'PC_EnableSquad',True);prop(c,'brain_component').restart_logic()
                current['deadline_game_seconds']=25
            else:
                for m in current['members']:
                    response=json.loads(unreal.ParisFormalSurveyLibrary.begin_formal_move(controllers[m['index']],unreal.Vector(*m['goal_cm'])))
                    assert not response.get('error'),response
                    m['request']=response
                    if response.get('rejection') or not response.get('started'):reject('saved_native_path_or_request_rejected',now,response);return
                current['deadline_game_seconds']=max(max(12,m['request']['path_length_cm']/max(1,saved_profiles[m['index']]['max_speed_cm_s'])*2+10) for m in current['members'])
            phase='moving';phase_time=now;sample_time=now;write();return
        if phase=='moving':
            if now<sample_time:return
            sample_time=now+.2;data=sample_members(now)
            if not current.get('capture_requested') and any(x['speed_cm_s']>50 for x in data):
                current['capture_requested']=True
                if STAGE=='Early' or current['kind']!='solo' or current['members'][0]['index'] in (1,3):capture(current['id']+'_walking',now)
            all_arrived=True
            for m,x in zip(current['members'],data):
                if current['kind']=='allied_follow':
                    target=x['held_goal_cm'];error=math.dist(x['body_cm'],target)
                    travelled=math.dist(m['standing']['body_cm'],x['body_cm'])
                    m['final']=x;m['body_goal_error_cm']=error
                    arrived=x['reservation']>0 and x['slot'] in (0,1) and error<=55 and x['walkable_floor'] and x['movement_mode']==1 and travelled>=100
                else:
                    goal=m['goal_cm'];events=[e for e in x['controller']['events'] if e['request_id']==m['request']['request_id'] and e['controller']==m['request']['controller']]
                    xy=math.dist(x['feet_cm'][:2],goal[:2]);dz=abs(x['feet_cm'][2]-goal[2])
                    m['final']=x;m['xy_error_cm']=xy;m['feet_error_cm']=dz;m['completion']=events[-1] if events else None
                    arrived=x['controller']['status_code']==0 and bool(events) and events[-1]['result_code']==0 and xy<=35 and dz<=35 and x['walkable_floor'] and x['movement_mode']==1
                    if x['controller']['status_code']==0 and events and not arrived:reject('native_completion_or_endpoint_rejected',now,m);return
                all_arrived=all_arrived and arrived
            if current['kind']=='allied_follow' and all_arrived:
                all_arrived=len({x['slot'] for x in data})==2 and len({x['reservation'] for x in data})==2
            if all_arrived:
                current.update({'status':'passed','ended_game_seconds':now,'elapsed_game_seconds':now-phase_time});previous_case=current;phase='next';write();return
            if now-phase_time>current['deadline_game_seconds']:reject('native_travel_or_formation_deadline',now,data);return
            if len(current['samples'])%8==0:write()
        elif phase=='encounter':
            if now<sample_time:return
            sample_time=now+.2;data=[]
            for i in active:
                a=bodies[i];c=controllers[i];bb=prop(c,'blackboard');target=bb.get_value_as_object('TargetActor')
                team=prop(a,'TeamId');valid_target=target in [bodies[j] for j in active if prop(bodies[j],'TeamId')!=team]
                row={'index':i,'team':team,'position_cm':xyz(a.get_actor_location()),'resources':resource(a),'action':str(prop(a,'ActionState')),
                    'outcome':str(prop(a,'ShotOutcome')),'visible':bb.get_value_as_bool('HasVisibleTarget'),
                    'target':target.get_path_name() if target else None,'opponent_is_active_npc':valid_target,
                    'los_to_target':c.line_of_sight_to(target,unreal.Vector(),False) if target else False,
                    'combat_phase':str(prop(c,'CombatPhase')),'decisions':prop(c,'CombatDecisionCount'),'speed_cm_s':a.get_velocity().length()}
                health,loaded,reserve,shots,dead=row['resources'];assert loaded+reserve+shots==18,('Ammo conservation',row)
                row.update({'reservation':prop(c,'SquadReservationID'),'generation':prop(a,'RestoreGeneration')})
                if BOOTSTRAP_LATCH:
                    row.update({'action_reply_reason':str(prop(c,'ActionReplyReason')),'combat_last_request_action':str(prop(c,'CombatLastRequestAction')),
                        'policy_state':str(prop(c,'PolicyState')),'squad_mode':str(prop(c,'SquadMode'))})
                if row['visible'] and valid_target and row['los_to_target'] and team not in current['seen_factions']:current['seen_factions'].append(team)
                assert row['outcome']!='Friendly hit',('Friendly damage during FF OFF',row)
                data.append(row)
            previous={x['index']:x for x in current['samples'][-1]['members']} if current['samples'] else {}
            for row in data:
                i=row['index'];old=previous.get(i);before=old['resources'] if old else current['initial_resources'][i]
                delta=row['resources'][3]-before[3];assert delta>=0,'Shot sequence reset'
                if delta>0 and row['opponent_is_active_npc'] and row['los_to_target']:
                    target_index=next(j for j in active if bodies[j].get_path_name()==row['target'])
                    target_row=next(x for x in data if x['index']==target_index)
                    target_before=previous[target_index]['resources'][0] if target_index in previous else current['initial_resources'][target_index][0]
                    event={'game_seconds':now,'shooter':i,'team':row['team'],'target':target_index,'delta':delta,
                        'outcome':row['outcome'],'target_health_before':target_before,'target_health_after':target_row['resources'][0],
                        'native_los':True,'new_shot_and_same_interval_only':True}
                    current['shot_events'].append(event)
                    if row['team'] not in current['real_opponent_shot_factions']:current['real_opponent_shot_factions'].append(row['team'])
                    if row['outcome']=='Hostile hit' and target_row['resources'][0]<target_before:current['enemy_health_loss']=True
                if row['resources'][4]:
                    key=str(i)
                    if key not in current['dead_observations']:
                        current['dead_observations'][key]={'first_seconds':now,'position_cm':row['position_cm'],'shots':row['resources'][3],
                            'generation':row['generation'],'settled_checks':0}
                    dead=current['dead_observations'][key]
                    if now-dead['first_seconds']>=.75:
                        ok=row['speed_cm_s']<=1 and math.dist(row['position_cm'],dead['position_cm'])<=1 and row['resources'][3]==dead['shots'] and row['generation']==dead['generation'] and row['reservation']==0
                        dead['settled_checks']+=1;dead['last_stop_pass']=ok
                        assert ok,('Dead body resumed movement/shot/reservation/reset',row,dead)
                elif str(i) in current['dead_observations']:raise AssertionError('Casualty reset in engaged encounter')
            current['samples'].append({'game_seconds':now,'members':data,'player_resources':resource(bodies[0]),'world_frame_seconds':unreal.GameplayStatics.get_world_delta_seconds(world)})
            if len(current['samples'])==2:capture('encounter_initial',now)
            if len(current['samples'])==6:capture('encounter_active',now)
            if now-phase_time>=30:
                current.update({'status':'passed' if set(current['seen_factions'])==set(current['real_opponent_shot_factions'])=={0,1} and current['enemy_health_loss'] else 'negative',
                    'reason':'native_opposing_npc_interaction_observed' if set(current['real_opponent_shot_factions'])=={0,1} and current['enemy_health_loss'] else 'opposing_factions_not_both_interacting',
                    'ended_game_seconds':now})
                write();finish();return
            if len(current['samples'])%8==0:write()
    except Exception:finish(traceback.format_exc())
    finally:busy=False

callback=unreal.register_slate_post_tick_callback(tick)
