"""New frozen-bank native A* locomotion observer; no moving-frame pose/position driver."""
import ast,json,math,os,sys,time,traceback
from pathlib import Path
import unreal

ROOT=Path(os.environ['CS549_CONVERGE_ROOT']);OUT=Path(os.environ['CS549_CONVERGE_OUT'])
STAGE=os.environ['CS549_CONVERGE_STAGE'];assert STAGE in ('Early','Full','Crowd')
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
from ue_formal_roster import LABELS,MAP,prop,xyz,actor_state,ready_snapshot
BANK=STORE/'Evidence/NativeConvergenceV1/crowd_bank_v1_20261007/bank.json'
bank=json.loads(BANK.read_text());rows=guard_rows()
assert rows==bank['protected_rows'] and guards_match(rows),'Explicit frozen current epoch required'
source=STORE/bank['source'];assert all(digest(source/n)==h for n,h in bank['source_sha256'].items())
inventory_path=STORE/'Evidence/PureMapSurveyV1/inventory_v4_20261007/inventory.json'
assert digest(inventory_path)=='072719794c3fa2f20f48688b1a64b14094c03ba96ba7bc2aa1a303bac87d10e9'
original_supports={s['component'] for s in json.loads(inventory_path.read_text())['blockers']}
for name,h in bank['helpers'].items():assert digest(ROOT/f'Unreal/ParisStreetCombat/Plugins/{name}/Binaries/Win64/UnrealEditor-{name}.dll')==h
report={'identity':OUT.name,'stage':STAGE,'status':'initializing','errors':[],'cases':[],'captures':[],
        'bank_sha256':digest(BANK),'protected_rows':703,'navigation_scope':'saved','source_white_scope':'saved',
        'map_saved':False,'nav_rebuilt':False,'final_layout_selected':False,'moving_frame_python_positioning':False,
        'terrain_phase_mutual_test_character_collision_ignored':STAGE!='Crowd','time_dilation':1,'bootstrap_latches':[]}
(OUT/'guards_before.json').write_text(json.dumps(rows)+'\n')
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
phase='setup';busy=False;callback=None;world=None;pc=None;fp=None;bodies=[];controllers=[]
profiles=[];resources=[];vehicles=[];vehicle_state={};latched=set();queue=[];active={};finished_ids=set()
# Required global contract of the authenticated extracted vehicle function.
vehicle_snapshots=vehicle_state
perf=saving=None;old_throttle=old_autosave=None;camera=target=None
started=time.monotonic();phase_time=last_sample=0;last_write=0;hub_checks={}
vehicle_source=STORE/'Evidence/PureMapSurveyV1/fixed_static_vehicle_v20_20261007/ue_pure_map_survey.py'
assert digest(vehicle_source)=='3c7af06e369be26fa40f6579b98ecd2c502af442c6cf7737890c8a80f542fc2e'
tree=ast.parse(vehicle_source.read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vehicle_snapshot','freeze_environment_vehicle')]
assert len(functions)==2
exec(compile(ast.Module(body=functions,type_ignores=[]),str(vehicle_source),'exec'),globals())

def native(a):
    x=json.loads(unreal.ParisFormalSurveyLibrary.read_formal_character(a));assert not x.get('error'),x;return x
def control(c):
    x=json.loads(unreal.ParisFormalSurveyLibrary.read_formal_controller(c));assert not x.get('error'),x;return x
def resource(a):return [prop(a,n) for n in ('Health','LoadedAmmo','ReserveAmmo','ShotSequence','IsDead')]
def call(a,n,*args):a.call_method(n,args=args)
def now():return unreal.GameplayStatics.get_time_seconds(world)
def write():
    report['phase']=phase;report['elapsed_wall_seconds']=time.monotonic()-started
    report['summary']={'planned':report.get('planned_cases',0),'recorded':len(report['cases']),
        'passed':sum(c['status']=='passed' for c in report['cases']),
        'negative':sum(c['status']=='negative' for c in report['cases']),
        'unmeasured':report.get('planned_cases',0)-len(report['cases'])}
    report['active_progress']=[{'id':s['id'],'source_cm':s['source_cm'],'samples':s.get('sample_count',0)} for s in active.values()]
    tmp=OUT/'result.writing.json';tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(OUT/'result.json')
def finish(error=None):
    global phase,callback
    if error:report['errors'].append(error)
    if levels.is_in_play_in_editor():
        for c in controllers:
            if c:c.stop_movement()
        levels.editor_request_end_play();phase='ending';write();return
    if perf:perf.set_editor_property('bThrottleCPUWhenNotForeground',old_throttle)
    if saving:saving.set_editor_property('bAutoSaveEnable',old_autosave)
    report['protected_bytes_unchanged']=guards_match(rows)
    report['helpers_unchanged']=all(digest(ROOT/f'Unreal/ParisStreetCombat/Plugins/{n}/Binaries/Win64/UnrealEditor-{n}.dll')==h for n,h in bank['helpers'].items())
    if not report['protected_bytes_unchanged'] or not report['helpers_unchanged']:report['errors'].append('Protected bytes/helper changed')
    report['status']='failed_global_admission' if report['errors'] else 'complete_finite_native_convergence'
    if STAGE=='Early' and not report['errors']:
        assert all(any(c['role']==role and c['status']=='passed' for c in report['cases']) for role in ('allied','german')),'Early movement mechanism did not pass both roles'
        report['status']='pass_early_native_convergence'
    phase='done';write()
    if callback is not None:unreal.unregister_slate_post_tick_callback(callback);callback=None
    unreal.SystemLibrary.quit_editor()
def isolate(a,c):
    call(c,'PC_EnableCombat',False);call(c,'PC_EnablePolicy',False);call(c,'PC_EnableSquad',False);call(c,'PC_PolicyHold')
    c.stop_movement();prop(c,'brain_component').stop_logic('Frozen native convergence terrain isolation')
    a.get_component_by_class(unreal.PawnSensingComponent).set_sensing_updates_enabled(False)
def place(i,feet,visible=False):
    a=bodies[i];controllers[i].stop_movement();a.character_movement.stop_movement_immediately()
    a.set_actor_enable_collision(True)
    a.character_movement.set_component_tick_enabled(True)
    h=a.capsule_component.get_scaled_capsule_half_height()
    a.set_actor_location(unreal.Vector(feet[0],feet[1],feet[2]+h+3),False,False)
    a.set_actor_hidden_in_game(not visible)
    a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(a.get_actor_location(),unreal.Vector(*bank['hub']['feet_cm'])+unreal.Vector(0,0,h)),False)
def standing(i,goal):
    a=bodies[i];x=native(a)
    if x['walkable_floor']:assert x['floor_component'].replace('UEDPIE_0_','') in original_supports,('Unknown terrain support',x)
    parts=unreal.SystemLibrary.capsule_overlap_components(world,unreal.Vector(*x['body_cm']),x['radius_cm'],x['half_height_cm'],
        [unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1,unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY2,unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY3],None,bodies)
    if isinstance(parts,tuple) and any(isinstance(p,bool) for p in parts):
        arrays=[p for p in parts if not isinstance(p,bool) and hasattr(p,'__iter__')];assert len(arrays)==1;parts=list(arrays[0])
    elif isinstance(parts,bool):assert not parts;parts=[]
    else:parts=list(parts or [])
    blockers=[p.get_path_name() for p in parts if p.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)==unreal.CollisionResponseType.ECR_BLOCK]
    x.update({'xy_error_cm':math.dist(x['feet_cm'][:2],goal[:2]),'feet_error_cm':abs(x['feet_cm'][2]-goal[2]),'terrain_blockers':blockers})
    x['standing_pass']=x['xy_error_cm']<=35 and x['feet_error_cm']<=35 and not blockers and x['walkable_floor'] and x['movement_mode']==1
    return x
def invariant():
    assert unreal.GameplayStatics.get_player_pawn(world,0)==bodies[0] and bodies[0].get_controller()==pc
    assert prop(fp,'Initialized') and not str(prop(fp,'BindingError'))
    for i,a in enumerate(bodies):
        p=native(a)
        for k in ('class','radius_cm','half_height_cm','max_speed_cm_s','max_step_cm','slope_degrees','gravity_scale','rvo'):assert p[k]==profiles[i][k],(i,k)
        assert resource(a)==resources[i],('Resource changed',i)
        assert prop(a.mesh,'skeletal_mesh_asset').get_path_name()==report['editor_roster'][i]['mesh']
    for v in vehicles:assert vehicle_snapshot(v)==vehicle_state[v.get_path_name()]
def record(i,status,reason=None):
    s=active.pop(i);controllers[i].stop_movement();s.update({'status':status,'reason':reason,'ended_game_seconds':now()})
    report['cases'].append(s);finished_ids.add(s['id']);bodies[i].character_movement.stop_movement_immediately();write()
def capture(i,s):
    if STAGE!='Early' or s.get('capture'):return
    a=bodies[i];look=a.get_actor_location()+unreal.Vector(0,0,35);pos=look+unreal.Vector(280,-300,180)
    camera.set_actor_location(pos,False,False);camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(pos,look),False)
    cap=camera.get_component_by_class(unreal.SceneCaptureComponent2D);cap.capture_scene()
    name=s['id']+'_native_walking.png';unreal.RenderingLibrary.export_render_target(world,target,OUT.as_posix(),name)
    assert (OUT/name).is_file() and (OUT/name).stat().st_size>10000
    s['capture']=name;report['captures'].append({'file':name,'role':s['role'],'case':s['id'],'game_seconds':now(),'moving_pose_not_frozen':True})
def start_batch():
    global phase,phase_time
    for i in range(1,6):
        role='allied' if i<3 else 'german'
        k=next((k for k,s in enumerate(queue) if s['role']==role),None)
        if k is None:continue
        s=dict(queue.pop(k));s.update({'actor_index':i,'actor':bodies[i].get_path_name(),'samples_file':s['id']+'_samples.jsonl','sample_count':0,'peak_speed_cm_s':0})
        assert s['id'] not in finished_ids
        active[i]=s;place(i,s['source_cm'],True)
    phase='settle';phase_time=now();write()
def tick(_delta):
    global phase,busy,world,pc,fp,bodies,controllers,profiles,resources,perf,saving,old_throttle,old_autosave,camera,target,queue,phase_time,last_sample,last_write
    if busy or phase=='done':return
    busy=True
    try:
        assert time.monotonic()-started<3500,'Owned convergence deadline'
        if (OUT/'STOP_REQUEST.json').exists() and phase!='ending':finish('Strict live-log stop');return
        if phase=='ending':
            if editor.get_game_world() is None:finish()
            return
        if phase=='setup':
            assert STAGE=='Crowd','Separate frozen crowd observer only'
            assert levels.load_level(MAP)
            lookup={a.get_actor_label():a for a in actors.get_all_level_actors()}
            report['editor_roster']=[actor_state(lookup[n]) for n in ('PC_City_Player',*LABELS)]
            for n in ('PC_City_Player',*LABELS):lookup[n].set_actor_hidden_in_game(True)
            camera=actors.spawn_actor_from_class(unreal.SceneCapture2D,lookup['PC_City_Player'].get_actor_location(),unreal.Rotator());camera.set_actor_label('NativeConvergenceCamera')
            perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));old_throttle=prop(perf,'bThrottleCPUWhenNotForeground');perf.set_editor_property('bThrottleCPUWhenNotForeground',False)
            saving=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorLoadingSavingSettings'));old_autosave=prop(saving,'bAutoSaveEnable');saving.set_editor_property('bAutoSaveEnable',False)
            levels.editor_request_begin_play();phase='ready';write();return
        world=editor.get_game_world()
        if world is None:return
        t=now()
        if phase=='ready':
            lookup={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)}
            for n in LABELS:
                a=lookup.get(n);c=unreal.AIHelperLibrary.get_ai_controller(a) if a else None
                if not c or n in latched or not prop(c,'BootstrapReady'):continue
                flags={k:prop(c,k) for k in ('CombatEnabled','PolicyEnabled','SquadEnabled')}
                assert all(flags.values()) and resource(a)==[100.0,2,16,0,False]
                report['bootstrap_latches'].append({'label':n,'game_seconds':t,'flags':flags,'resources':resource(a)});latched.add(n);isolate(a,c)
            if t<4:return
            assert t<40 and len(latched)==5,'Native bootstrap gate failed'
            bodies=[lookup[n] for n in ('PC_City_Player',*LABELS)];pc=unreal.GameplayStatics.get_player_controller(world,0)
            controllers=[pc]+[unreal.AIHelperLibrary.get_ai_controller(a) for a in bodies[1:]]
            fps=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ParisFirstPersonApprovedActor)
            if len(fps)!=1 or not prop(fps[0],'Initialized'):return
            fp=fps[0]
            # The source readiness inspector reads original enabled state;
            # re-enable only during this synchronous inspection, before a tick.
            for c in controllers[1:]:call(c,'PC_EnableCombat',True)
            report['equipment']=ready_snapshot(world,bodies[1:])
            for a,c in zip(bodies[1:],controllers[1:]):isolate(a,c)
            profiles=[native(a) for a in bodies];resources=[resource(a) for a in bodies];assert all(x==[100.0,2,16,0,False] for x in resources)
            report['profiles']=profiles;report['original_resources']=resources
            report['avoidance_group_isolation']=[]
            for a in bodies:
                mask=prop(a.character_movement,'groups_to_avoid')
                before=[bool(prop(mask,'bGroup'+str(j))) for j in range(32)]
                if STAGE=='Full':a.character_movement.set_groups_to_avoid(0)
                after=[bool(prop(prop(a.character_movement,'groups_to_avoid'),'bGroup'+str(j))) for j in range(32)]
                if STAGE=='Full':assert not any(after),'RVO test-agent isolation readback failed'
                report['avoidance_group_isolation'].append({'actor':a.get_path_name(),'before':before,'after':after,'native_rvo_enabled':native(a)['rvo']})
            for a in bodies:
                a.set_actor_enable_collision(False);a.set_actor_hidden_in_game(True)
                a.character_movement.stop_movement_immediately();a.character_movement.set_component_tick_enabled(False)
                for other in bodies:
                    if other!=a:a.capsule_component.ignore_actor_when_moving(other,True)
                report.setdefault('move_ignore_inventory',[]).append({'actor':a.get_path_name(),'ignored':[x.get_path_name() for x in a.capsule_component.copy_array_of_move_ignore_actors()]})
            for v in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Pawn):
                if v.get_class().get_path_name().startswith('/Game/WW2City/CarsSet/'):
                    freeze_environment_vehicle(v);vehicles.append(v);vehicle_state[v.get_path_name()]=vehicle_snapshot(v)
            camera=lookup['NativeConvergenceCamera'];target=unreal.RenderingLibrary.create_render_target2d(world,1600,900,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(0,0,0,1),False,False)
            cap=camera.get_component_by_class(unreal.SceneCaptureComponent2D);cap.set_editor_property('texture_target',target);cap.set_editor_property('capture_every_frame',False);cap.set_editor_property('capture_on_movement',False)
            cap.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR);cap.set_editor_property('fov_angle',70)
            early=set(bank['early_ids']);queue=[c for c in bank['cases'] if (c['id'] in early)==(STAGE=='Early')]
            report['planned_cases']=len(queue)
            if STAGE=='Full':
                prior=json.loads((STORE/'Evidence/NativeConvergenceV1/early_v2_20261007/audit.json').read_text());assert prior['status']=='pass_independent_convergence_audit' and prior['early_mechanism_pass']
                report['reused_early_audit']=prior
            for i in (1,3):place(i,bank['hub']['feet_cm'])
            phase='hub_settle';phase_time=t;write();return
        invariant()
        if phase=='hub_settle':
            if t-phase_time<.8:return
            for i in (1,3):
                h=standing(i,bank['hub']['feet_cm']);assert h['standing_pass'],('Central hub admission failed',i,h)
                hub_checks[str(i)]=h;bodies[i].set_actor_enable_collision(False)
                bodies[i].character_movement.set_component_tick_enabled(False)
            report['hub_standing']=hub_checks
            report['crowd_move_ignore_before_travel']=[]
            for a in bodies:
                for other in bodies:
                    if other!=a:a.capsule_component.ignore_actor_when_moving(other,False)
                remaining=[x.get_path_name() for x in a.capsule_component.copy_array_of_move_ignore_actors()]
                assert not remaining
                report['crowd_move_ignore_before_travel'].append({'actor':a.get_path_name(),'remaining':remaining,'pawn_response':str(a.capsule_component.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN))})
            assert all(x['before']==x['after'] for x in report['avoidance_group_isolation'])
            phase='next';write();return
        if phase=='next':
            if not queue:finish();return
            start_batch();return
        if phase=='settle':
            if t-phase_time<.8:return
            for i,s in list(active.items()):
                h=standing(i,s['source_cm']);s['source_standing']=h
                if not h['standing_pass']:record(i,'negative','source_standing_rejected');continue
                req=json.loads(unreal.ParisFormalSurveyLibrary.begin_formal_move(controllers[i],unreal.Vector(*bank['hub']['feet_cm'])))
                assert not req.get('error'),req;s['request']=req
                if req.get('rejection') or not req.get('started'):record(i,'negative','saved_navigation_complete_path_rejected');continue
                assert req['path_cm'] and req['path_length_cm']>0
                s['moving_started_game_seconds']=t;s['deadline_seconds']=max(12,req['path_length_cm']/profiles[i]['max_speed_cm_s']*2+10)
            phase='moving';last_sample=t;write();return
        if phase=='moving':
            if t-last_sample<.2:return
            last_sample=t
            for i,s in list(active.items()):
                x=native(bodies[i]);ctr=control(controllers[i]);speed=bodies[i].get_velocity().length()
                if x['walkable_floor']:assert x['floor_component'].replace('UEDPIE_0_','') in original_supports,('Unknown moving support',i,x)
                events=[e for e in ctr['events'] if e['controller']==s['request']['controller'] and e['request_id']==s['request']['request_id']]
                sample={**x,'other_bodies_cm':{str(j):xyz(bodies[j].get_actor_location()) for j in (1,2,3) if j!=i},'game_seconds':t,'speed_cm_s':speed,'path_status':ctr['status_code'],'completion':events[-1] if events else None}
                with (OUT/s['samples_file']).open('a',encoding='utf-8') as f:f.write(json.dumps(sample)+'\n')
                s['sample_count']+=1;s['peak_speed_cm_s']=max(s['peak_speed_cm_s'],speed);s['final']=sample
                if speed>50:capture(i,s)
                if ctr['status_code']==0 and events:
                    h=standing(i,bank['hub']['feet_cm']);s['arrival_standing']=h;s['completion']=events[-1]
                    if events[-1]['result_code']!=0:record(i,'negative','native_path_following_failed');continue
                    if not h['standing_pass']:record(i,'negative','endpoint_standing_rejected');continue
                    if 'arrival_first_game_seconds' not in s:s['arrival_first_game_seconds']=t
                    if t-s['arrival_first_game_seconds']>=.6:
                        s['travel_seconds']=t-s['moving_started_game_seconds'];record(i,'passed');continue
                if t-s['moving_started_game_seconds']>s['deadline_seconds']:record(i,'negative','distance_scaled_travel_deadline')
            if not active:phase='next';write();return
            if t-last_write>=2:last_write=t;write()
    except Exception:
        finish(traceback.format_exc())
    finally:busy=False

callback=unreal.register_slate_post_tick_callback(tick)
write()
