"""Finite unsaved Editor-world grid sampling; never a gameplay pose/movement driver."""
import ast
import json
import math
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

import unreal

ROOT=Path(os.environ['CS549_GRID_ROOT']);OUT=Path(os.environ['CS549_GRID_OUT'])
STAGE=os.environ['CS549_GRID_STAGE'];assert STAGE in ('Early','Full')
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
sys.path.insert(0,str(ROOT/'Tools/Integration/MapGridV1'))
sys.path.insert(0,str(OUT))
from common import STORE,guard_rows,guards_match,digest
from grid_core import PROFILE

INVENTORY=STORE/'Evidence/PureMapSurveyV1/inventory_v4_20261007/inventory.json'
BASE=STORE/'Evidence/PureMapSurveyV1/fixed_static_vehicle_v20_20261007'
inventory=json.loads(INVENTORY.read_text(encoding='utf-8'))
rows=guard_rows();assert len(rows)==703 and guards_match(rows)
(OUT/'guards_before.json').write_text(json.dumps(rows)+'\n',encoding='utf-8')
helper_paths=[ROOT/'Unreal/ParisStreetCombat/Plugins'/name/'Binaries/Win64'/('UnrealEditor-'+name+'.dll')
              for name in ('ParisMapSurveyV1','ParisFormalSurveyV1')]
helper_guards={p.as_posix():digest(p) for p in helper_paths}
report={'identity':OUT.name,'stage':STAGE,'status':'initializing','errors':[],
        'map_saved':False,'formal_navigation_changed':False,'final_layout_selected':False,
        'current_guards':703,'profile':PROFILE,'samples_are_static_geometry_not_movement':True,
        'helper_guards':helper_guards,'inventory_sha256':digest(INVENTORY),
        'grid_helper_sha256':digest(ROOT/'Unreal/ParisStreetCombat/Plugins/ParisGridSurveyV1/Binaries/Win64/UnrealEditor-ParisGridSurveyV1.dll'),
        'plan_sha256':digest(ROOT/'Docs/Development/MissionLoopV1/MAP_GRID_IMPLEMENTATION_20261007.md'),
        'passes':{},'removed':[],'early_controls':[]}
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
phase='setup';busy=False;callback=None;started=time.monotonic()
world=nav=nav_data=volume=probe=perf=saving=None
old_throttle=old_autosave=None
vehicle_snapshots={};vehicles=[]
vehicle_source=BASE/'ue_pure_map_survey.py'
assert digest(vehicle_source)=='3c7af06e369be26fa40f6579b98ecd2c502af442c6cf7737890c8a80f542fc2e'
tree=ast.parse(vehicle_source.read_text(encoding='utf-8'))
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vehicle_snapshot','freeze_environment_vehicle')]
assert len(functions)==2
exec(compile(ast.Module(body=functions,type_ignores=[]),str(vehicle_source),'exec'),globals())
def xyz(v):return [float(v.x),float(v.y),float(v.z)]

job=None;job_log=None;candidate_file=sample_file=None
current_name=None;native_export=None;grid=None;recorded=0;admitted=0;candidate_count=0
pending_batch=[];last_checkpoint=0;expansion_started=0


def write():
    report['phase']=phase;report['elapsed_wall_seconds']=time.monotonic()-started
    report['current_pass']=current_name;report['current_recorded']=recorded
    temp=OUT/'result.writing.json';temp.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');temp.replace(OUT/'result.json')


def environment_check():
    state=json.loads(unreal.ParisGridSurveyLibrary.inspect_grid_world(world))
    assert not state.get('error'),state
    report['native_isolation_state']=state
    assert state['characters']==(1 if probe else 0) and state['controllers']==0,'Native world probe inventory mismatch'
    assert not state['production_contaminants'],'Production actor escaped native inheritance inventory'
    for v in vehicles:
        assert vehicle_snapshot(v)==vehicle_snapshots[v.get_path_name()],'Static environment geometry changed'
        assert all(not c.is_simulating_physics() for c in v.get_components_by_class(unreal.PrimitiveComponent))


def finish(error=None):
    global phase,callback,probe
    if error:report['errors'].append(error)
    for f in (candidate_file,sample_file,job_log):
        if f and not f.closed:f.close()
    if job and job.poll() is None:
        job.terminate();report['errors'].append('Owned offline preparation interrupted')
    if probe and unreal.SystemLibrary.is_valid(probe):
        assert unreal.ParisGridSurveyLibrary.destroy_grid_probe(probe),'Transient probe cleanup failed'
        probe=None
    if perf and old_throttle is not None:perf.set_editor_property('bThrottleCPUWhenNotForeground',old_throttle)
    if saving and old_autosave is not None:saving.set_editor_property('bAutoSaveEnable',old_autosave)
    report['protected_bytes_unchanged']=guards_match(rows)
    report['old_helpers_unchanged']=all(digest(Path(p))==h for p,h in helper_guards.items())
    if not report['protected_bytes_unchanged'] or not report['old_helpers_unchanged']:report['errors'].append('Protected bytes/helper changed')
    report['status']='failed_grid_global_admission' if report['errors'] else 'pass_early_grid_admission' if STAGE=='Early' else 'complete_finite_native_grid_geometry'
    phase='done';write()
    if callback is not None:unreal.unregister_slate_post_tick_callback(callback);callback=None
    unreal.SystemLibrary.quit_editor()


def isolate():
    global world,nav,nav_data,volume,probe,perf,saving,old_throttle,old_autosave,grid
    assert unreal.EditorLevelLibrary.load_level('/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1')
    world=editor.get_editor_world()
    saving=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorLoadingSavingSettings'))
    old_autosave=saving.get_editor_property('bAutoSaveEnable');saving.set_editor_property('bAutoSaveEnable',False)
    perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
    old_throttle=perf.get_editor_property('bThrottleCPUWhenNotForeground');perf.set_editor_property('bThrottleCPUWhenNotForeground',False)
    for a in list(actors.get_all_level_actors()):
        path=a.get_class().get_path_name()
        if isinstance(a,unreal.Character) or path.startswith(('/Game/ParisCombat/','/Script/Paris')) or 'GripPolicy' in path:
            report['removed'].append({'label':a.get_actor_label(),'class':path});assert actors.destroy_actor(a)
    assert len(report['removed'])==inventory['summary']['removed_gameplay_actors']
    for a in actors.get_all_level_actors():
        if isinstance(a,unreal.Pawn):
            assert a.get_class().get_path_name().startswith('/Game/WW2City/CarsSet/')
            vehicles.append(a);freeze_environment_vehicle(a)
    ns=[n for n in unreal.ObjectIterator(unreal.NavigationSystemV1) if 'Default__' not in n.get_path_name() and n.get_outer()==world]
    ms=[a for a in actors.get_all_level_actors() if isinstance(a,unreal.RecastNavMesh)]
    vs=[a for a in actors.get_all_level_actors() if isinstance(a,unreal.NavMeshBoundsVolume)]
    assert len(ns)==len(ms)==len(vs)==1
    nav,nav_data,volume=ns[0],ms[0],vs[0]
    assert all(nav_data.get_editor_property(k)==v for k,v in (('agent_radius',34.0),('agent_height',193.0),('agent_max_slope',45.0),('tile_size_uu',1000.0)))
    o,e=volume.get_actor_bounds(False);report['saved_nav_bounds_cm']={'origin':xyz(o),'extent':xyz(e)}
    # Full extent fixed before either pass, from the authenticated completed survey.
    base_nav=json.loads((BASE/'navmesh.json').read_text(encoding='utf-8'))
    from grid_core import grid_spec
    grid=grid_spec(base_nav);(OUT/'grid_spec.json').write_text(json.dumps(grid,indent=2)+'\n',encoding='utf-8')
    probe=unreal.ParisGridSurveyLibrary.create_grid_probe(world);assert probe,'Native transient Editor probe required'
    environment_check()


def export_nav(name):
    global native_export
    native_export=json.loads(unreal.ParisMapSurveyLibrary.export_navmesh(nav_data))
    assert native_export['active_tiles']==native_export['exported_tiles'] and native_export['invalid_records']==0
    assert native_export['polygons']
    target=OUT/name;target.mkdir()
    (target/'navmesh.json').write_text(json.dumps(native_export,separators=(',',':'))+'\n',encoding='utf-8')
    report['passes'][name]={'nav_polygons':len(native_export['polygons']),'active_tiles':native_export['active_tiles']}


def prepare(name):
    global job,job_log,current_name,recorded,admitted
    current_name=name;recorded=admitted=0
    job_log=(OUT/name/'prepare.log').open('w',encoding='utf-8')
    py='C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    args=[py,'-X','utf8',str(OUT/'prepare_candidates.py'),
          str(OUT/name/'navmesh.json'),str(OUT/name),'--spec',str(OUT/'grid_spec.json')]
    job=subprocess.Popen(args,stdout=job_log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    report['passes'][name]['owned_preparation_pid']=job.pid


def prepare_post(name):
    global job,job_log,current_name,recorded,admitted
    current_name=name;recorded=admitted=0
    report['passes'][name]={}
    job_log=(OUT/('prepare_'+name+'.log')).open('w',encoding='utf-8')
    py='C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    args=[py,'-X','utf8',str(OUT/('prepare_'+('links' if name=='saved_links' else name)+'.py')),str(OUT)]
    if name=='saved_links':args.append('--saved-only')
    job=subprocess.Popen(args,stdout=job_log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    report['passes'][name]['owned_preparation_pid']=job.pid


def sample(batch):
    fn=unreal.ParisGridSurveyLibrary.sample_grid_cells if current_name in ('saved','full','sight') else unreal.ParisGridSurveyLibrary.sample_grid_links
    result=json.loads(fn(nav_data,probe,json.dumps(batch,separators=(',',':'))))
    assert not result.get('error'),result
    assert len(result['samples'])==len(batch)
    for request,result_row in zip(batch,result['samples']):
        assert request['id']==result_row['id']
        if current_name in ('saved','full') and request['p']!='0':assert result_row['exact_surface'] and result_row['xy_drift_cm']<=.01
    return result['samples']


def early():
    # Existing road route is only an observation control; no failed movement rerun.
    road=[14326,-10374,116.665702280093]
    candidates=[]
    by_cell={}
    with (OUT/current_name/'candidates.jsonl').open(encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            d=math.dist(r['xyz'][:2],road[:2])+abs(r['xyz'][2]-road[2])
            candidates.append((d,r))
            key=(r['c'],r['r']);by_cell.setdefault(key,[]).append(r)
    picked=min(candidates,key=lambda v:v[0])[1]
    road_result=sample([picked])[0]
    report['early_controls'].append({'kind':'known_city_road','request':picked,'result':road_result})
    assert road_result['admitted'] and road_result['mesh'].startswith('/Game/WW2City/')
    assert 'Road' in road_result['mesh'] or 'Road' in road_result['component'],'Known road support required'
    stacks=[rs for rs in by_cell.values() if len(rs)>1 and max(r['xyz'][2] for r in rs)-min(r['xyz'][2] for r in rs)>200]
    assert stacks,'Overlapping surface control required'
    stack=min(stacks,key=lambda rs:(min(math.dist(r['xyz'][:2],road[:2]) for r in rs),len(rs)))
    stack=sorted(stack,key=lambda r:r['xyz'][2]);pair=[stack[0],stack[-1]]
    observed=sample(pair)
    report['early_controls'].append({'kind':'same_xy_different_surface','requests':pair,'results':observed})
    assert observed[0]['nav_cm'][:2]==observed[1]['nav_cm'][:2]
    assert abs(observed[0]['nav_cm'][2]-observed[1]['nav_cm'][2])>200
    blocking=next(b for b in inventory['blockers'] if b['class']=='/Script/Engine.BlockingVolume')
    center=blocking['origin_cm'];feet=[center[0],center[1],center[2]-PROFILE['half_height_cm']-PROFILE['floor_gap_cm']]
    request={'id':-1,'p':'0','xyz':feet}
    obstacle=sample([request])[0]
    report['early_controls'].append({'kind':'known_blocking_volume','request':request,'result':obstacle})
    assert obstacle['requested_blockers'] and not obstacle['admitted'],'Known obstruction must remain black'


def expand():
    global expansion_started
    b=inventory['collision_bounds_cm']
    lo=[b['min'][i]-(100 if i<2 else 193) for i in range(3)]
    hi=[b['max'][i]+(100 if i<2 else 193) for i in range(3)]
    center=[(a+b)/2 for a,b in zip(lo,hi)];extent=[(b-a)/2 for a,b in zip(lo,hi)]
    volume.set_actor_location(unreal.Vector(*center),False,False)
    volume.set_actor_scale3d(unreal.Vector(*(v/100 for v in extent)))
    nav.on_navigation_bounds_updated(volume)
    a,e=volume.get_actor_bounds(False)
    assert max(abs(x-y) for x,y in zip(xyz(a),center))<.1 and max(abs(x-y) for x,y in zip(xyz(e),extent))<.1
    report['temporary_bounds_cm']={'min':lo,'max':hi};expansion_started=time.monotonic()


def tick(_delta):
    global phase,busy,candidate_file,sample_file,candidate_count,recorded,admitted,last_checkpoint,expansion_started
    if busy or phase=='done':return
    busy=True
    try:
        assert time.monotonic()-started<3500,'Finite grid deadline'
        if (OUT/'STOP_REQUEST.json').exists():raise AssertionError('Owned stop: '+(OUT/'STOP_REQUEST.json').read_text(encoding='utf-8-sig'))
        if phase=='setup':isolate();phase='saved_ready';write();return
        if phase=='saved_ready':
            assert time.monotonic()-started<600
            state=json.loads(unreal.ParisMapSurveyLibrary.navigation_build_state(nav));assert not state.get('error')
            if state['manual_build_locked']:return
            export_nav('saved');prepare('saved');phase='preparing';write();return
        if phase=='preparing':
            if job.poll() is None:return
            job_log.close();assert job.returncode==0,'Offline candidate preparation failed'
            post=current_name in ('saved_links','links','sight')
            meta=json.loads((OUT/current_name/('manifest.json' if post else 'candidate_manifest.json')).read_text(encoding='utf-8'))
            candidate_count=meta['directed_link_requests' if current_name in ('saved_links','links') else 'sight_requests' if current_name=='sight' else 'candidate_count']
            report['passes'][current_name].update({'candidate_count':candidate_count,'omitted_polygons':0 if post else len(meta['omitted_polygons'])})
            if STAGE=='Early':early();environment_check();finish();return
            candidate_file=(OUT/current_name/('requests.jsonl' if post else 'candidates.jsonl')).open(encoding='utf-8')
            sample_file=(OUT/current_name/'samples.jsonl').open('x',encoding='utf-8')
            phase='sampling';write();return
        if phase=='sampling':
            batch=[]
            for _ in range(512):
                line=candidate_file.readline()
                if not line:break
                batch.append(json.loads(line))
            if batch:
                for request,result in zip(batch,sample(batch)):
                    sample_file.write(json.dumps({**request,**result},separators=(',',':'))+'\n')
                    recorded+=1;admitted+=int(result['admitted'])
                if time.monotonic()-last_checkpoint>5:
                    sample_file.flush();environment_check();write();last_checkpoint=time.monotonic()
                return
            candidate_file.close();sample_file.close()
            assert recorded==candidate_count,'Every scheduled center requires a result'
            report['passes'][current_name].update({'recorded':recorded,'geometry_clear':admitted,'samples_sha256':digest(OUT/current_name/'samples.jsonl')})
            if current_name=='saved':prepare_post('saved_links');phase='preparing';write();return
            if current_name=='saved_links':expand();phase='expanded_ready';write();return
            if current_name=='full':prepare_post('links');phase='preparing';write();return
            if current_name=='links':prepare_post('sight');phase='preparing';write();return
            environment_check();finish();return
        if phase=='expanded_ready':
            assert time.monotonic()-expansion_started<600,'Natural nav unlock deadline'
            state=json.loads(unreal.ParisMapSurveyLibrary.navigation_build_state(nav));assert not state.get('error')
            if state['manual_build_locked']:return
            bounds=state['registered_bounds'];assert len(bounds)==1
            for key in ('min','max'):
                assert max(abs(a-b) for a,b in zip(bounds[0][key+'_cm'],report['temporary_bounds_cm'][key]))<.1
            unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
            expansion_started=time.monotonic();phase='generating';write();return
        if phase=='generating':
            assert time.monotonic()-expansion_started<600,'Disposable generation deadline'
            if unreal.NavigationSystemV1.is_navigation_being_built(world) or time.monotonic()-expansion_started<3:return
            export_nav('full');prepare('full');phase='preparing';write();return
    except Exception:finish(traceback.format_exc())
    finally:busy=False

callback=unreal.register_slate_post_tick_callback(tick)
write()
