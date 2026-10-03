"""Persist/fresh-test only the actual-city navigation foundation; no autonomous AI."""
import hashlib
import json
import os
import re
import shutil
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
IDENTITY = os.environ['CS549_NAV_FOUNDATION_IDENTITY']
AUTHOR = os.environ.get('CS549_NAV_FOUNDATION_AUTHOR', '0') == '1'
RESAVE = os.environ.get('CS549_NAV_FOUNDATION_RESAVE', '0') == '1'
assert not RESAVE or AUTHOR
assert IDENTITY.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/NavigationFoundation' / IDENTITY
assert not OUT.exists(), 'Preserve occupied evidence/recovery identity'
DEST = ROOT / 'Assets/Integration/CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json'
assert not AUTHOR or RESAVE or not DEST.exists(), 'Do not rerun one-time navigation save'
checkpoint = ROOT / 'Assets/Integration/CITY_PACKAGE_DRAFT_INVENTORY_20261002.json' if AUTHOR and not RESAVE else DEST
if not AUTHOR:
    native_name = os.environ.get('CS549_NAV_NATIVE_CHECKPOINT', DEST.name)
    assert native_name in ('CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json', 'CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json', 'CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json', 'CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json')
    checkpoint = ROOT / 'Assets/Integration' / native_name
inventory = json.loads(checkpoint.read_text(encoding='utf-8-sig'))
old = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
map_item = next(f for f in inventory['files'] if f['package'] == ENTRY)
map_file = ROOT / map_item['path']
guarded = {ROOT / f['path']: f['sha256'] for f in inventory['files'] + old['files'] + inventory.get('retained_unselected_rejected_trial', [])}
for p in (STORE / 'Content/WW2City/Maps').rglob('*.umap'):
    guarded[p] = hashlib.sha256(p.read_bytes()).hexdigest()
assert all(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in guarded.items())
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
OUT.mkdir(parents=True)
survey = json.loads((STORE / 'Evidence/CityGameplay20261002/Survey/structure_v3.json').read_text())
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
report = {'identity': IDENTITY, 'mode': 'resave_supported_agent_binding' if RESAVE else 'author' if AUTHOR else 'fresh_load_and_live',
          'scope': __doc__, 'errors': [], 'status': 'initializing', 'samples': [], 'starts': [], 'moves': [],
          'engine': unreal.SystemLibrary.get_engine_version(), 'before_map': map_item,
          'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'engine_config_sha256': hashlib.sha256((ROOT/'Unreal/ParisStreetCombat/Config/DefaultEngine.ini').read_bytes()).hexdigest(),
          'deferred': ['follow', 'patrol', 'decision/Behavior Tree', 'faction interaction', 'mission', 'avoidance/replan policy']}
phase = 'setup'
started = time.monotonic()
callback = None
world = nav = nav_data = volume = None
roster = []
in_tick = False
move_actor = controller = goal = None
move_index = 0
move_time = sample_time = 0
ending_since = None
saved = False


def xyz(v):
    return [v.x, v.y, v.z]


def xy(v):
    return (v.x * v.x + v.y * v.y) ** .5


def write():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


def finish(error=None):
    global phase
    if error:
        report['errors'].append(error)
    report['protected_bytes_unchanged'] = all(hashlib.sha256(p.read_bytes()).hexdigest() == h
        for p, h in guarded.items() if not (AUTHOR and saved and p == map_file))
    if not report['protected_bytes_unchanged']:
        report['errors'].append('Unexpected protected native changes')
    log_path = os.environ.get('CS549_NAV_FOUNDATION_LOG')
    if log_path and Path(log_path).exists():
        log_text = Path(log_path).read_text(encoding='utf-8',errors='replace')
        report['nav_registration_warning_count'] = len(re.findall(r'RegistrationFailed_AgentNotValid|NavData.*will be removed',log_text))
        if not AUTHOR and report['nav_registration_warning_count']:
            report['errors'].append('Fresh navigation was rejected/replaced during loading; not a retained-data pass')
    report['elapsed_wall_seconds'] = time.monotonic() - started
    report['status'] = ('failed' if report['errors'] else
                        'saved_navigation_requires_fresh_test' if AUTHOR else
                        'pass_retained_navigation_only_not_behavior_or_mission_acceptance')
    write()
    if levels.is_in_play_in_editor():
        levels.editor_request_end_play()
        phase = 'ending'
        return
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
    unreal.SystemLibrary.quit_editor()


def project(point):
    result = nav.call_method('K2_ProjectPointToNavigation', args=(world, point, nav_data, None, unreal.Vector(100, 100, 120)))
    if isinstance(result, tuple):
        if any(isinstance(v, bool) and not v for v in result):
            return None
        return next((v for v in result if isinstance(v, unreal.Vector)), None)
    assert result is None or isinstance(result, unreal.Vector), repr(result)
    return result


def path_record(start, target, context):
    path = nav.call_method('FindPathToLocationSynchronously', args=(world, start, target, context, None))
    if path is None:
        return {'valid': False, 'partial': None, 'points_cm': []}
    points = list(path.get_editor_property('path_points'))
    return {'valid': path.is_valid(), 'partial': path.is_partial(), 'points_cm': [xyz(p) for p in points],
            'length_cm': sum((b-a).length() for a, b in zip(points, points[1:]))}


def complete(route):
    return bool(route) and route['valid'] and not route['partial']


def collect_coverage():
    player = next(a for a in roster if a.get_actor_label() == 'PC_City_Player')
    start = project(player.get_actor_location())
    assert start is not None
    for actor in roster:
        target = project(actor.get_actor_location())
        report['starts'].append({'label': actor.get_actor_label(), 'projected_cm': xyz(target) if target is not None else None,
                                'path': path_record(start, target, player) if target is not None else None})
    center = survey['sampling']['center_cm']
    report['sampling'] = {'center_cm': center, 'grid_side': 41, 'step_cm': 1000, 'not_mission_boundary': True}
    for i in range(-20, 21):
        for j in range(-20, 21):
            x, y = center[0]+i*1000, center[1]+j*1000
            hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, center[2]+300),
                unreal.Vector(x, y, center[2]-2000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                False, roster, unreal.DrawDebugTrace.NONE, True)
            if hit is None:
                continue
            fields = hit.to_tuple()
            if not fields[0] or fields[7].z < .7 or not -300 <= fields[5].z <= 600:
                continue
            ground = fields[5]
            target = project(ground)
            report['samples'].append({'grid': [i, j], 'ground_cm': xyz(ground),
                'projected_cm': xyz(target) if target is not None else None,
                'path': path_record(start, target, player) if target is not None else None})
    connected = [s for s in report['samples'] if complete(s['path'])]
    report['summary'] = {'street_candidates': len(report['samples']),
        'projected': sum(s['projected_cm'] is not None for s in report['samples']),
        'complete_from_player': len(connected),
        'partial_from_player': sum(bool(s['path']) and s['path']['partial'] for s in report['samples']),
        'six_starts_projected': all(s['projected_cm'] is not None for s in report['starts']),
        'five_npcs_complete': all(complete(s['path']) for s in report['starts'] if s['label'] != 'PC_City_Player'),
        'max_complete_path_m': max((s['path']['length_cm']/100 for s in connected), default=0)}
    assert report['summary']['six_starts_projected'] and report['summary']['five_npcs_complete']
    assert report['summary']['complete_from_player'] >= 127


def request(target):
    return controller.move_to_location(target, acceptance_radius=30.0, stop_on_overlap=False,
        use_pathfinding=True, project_destination_to_navigation=False, can_strafe=True, allow_partial_path=False)


def select_move(team, long_route):
    global move_actor, controller, goal, move_time, sample_time
    player = unreal.GameplayStatics.get_player_pawn(world, 0)
    chosen = sorted((a for a in roster if a != player and a.get_editor_property('TeamId') == team), key=lambda a: a.get_name())
    assert chosen
    move_actor = chosen[0]
    controller = unreal.AIHelperLibrary.get_ai_controller(move_actor)
    assert controller is not None
    start = move_actor.get_actor_location()
    candidates = []
    for s in report['samples']:
        if s['projected_cm'] is None:
            continue
        target = project(unreal.Vector(*s['ground_cm']))
        if target is None or any(xy(target-a.get_actor_location()) < 180 for a in roster):
            continue
        route = path_record(start, target, move_actor)
        lower, upper, preferred = (3000, 15000, 8000) if long_route else (600, 2500, 1200)
        if complete(route) and lower < route['length_cm'] < upper and xy(target-start) > 600:
            candidates.append((abs(route['length_cm']-preferred), s['grid'], target, route))
    assert candidates, 'No measured complete route for this bounded move'
    _, grid, goal, route = min(candidates, key=lambda x: (x[0], x[1]))
    result = request(goal)
    assert result == unreal.PathFollowingRequestResult.REQUEST_SUCCESSFUL, str(result)
    move_time = sample_time = unreal.GameplayStatics.get_time_seconds(world)
    report['moves'].append({'team': team, 'long_route': long_route, 'start_cm': xyz(start), 'goal_cm': xyz(goal),
        'ground_grid': grid, 'complete_path': route, 'request_result': str(result), 'samples': []})
    # World-only clearance spot checks; live movement is the actual traversability test.
    checks = []
    pts = route['points_cm']
    for a, b in list(zip(pts, pts[1:]))[:10]:
        hit = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(*a)+unreal.Vector(0,0,99.5),
            unreal.Vector(*b)+unreal.Vector(0,0,99.5), 34.0, 96.5, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
            False, roster, unreal.DrawDebugTrace.NONE, True)
        checks.append({'from_cm': a, 'to_cm': b, 'world_blocked': bool(hit and hit.to_tuple()[0])})
    report['moves'][-1]['capsule_spot_checks'] = checks
    write()


def tick(delta):
    global phase, world, nav, nav_data, volume, roster, callback, in_tick, saved
    global move_index, move_time, sample_time, ending_since, goal
    if in_tick:
        return
    in_tick = True
    try:
        if phase == 'ending':
            if not levels.is_in_play_in_editor() and editor.get_game_world() is None:
                if ending_since is None:
                    ending_since = time.monotonic()
                elif time.monotonic()-ending_since >= 1:
                    finish()
            return
        assert time.monotonic()-started < 600, 'Bounded foundation timeout'
        if phase == 'setup':
            assert levels.load_level(ENTRY)
            assert levels.set_current_level_by_name(unreal.Name(ENTRY.rsplit('/',1)[1]))
            world = editor.get_editor_world()
            nav = unreal.NavigationSystemV1.get_navigation_system(world)
            assert nav
            found = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.NavMeshBoundsVolume)]
            if AUTHOR:
                recovery = OUT / 'LV_ParisStreetCombat_V1_before.umap'
                shutil.copyfile(map_file, recovery)
                assert hashlib.sha256(recovery.read_bytes()).hexdigest() == map_item['sha256']
                (OUT/'before_checkpoint.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
                if RESAVE:
                    assert len(found)==1 and found[0].get_actor_label()=='PC_City_NavigationBounds_V1'
                    volume=found[0]
                else:
                    assert not found, 'Do not replace already saved bounds'
                    center = survey['sampling']['center_cm']
                    volume = actors.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(center[0],center[1],200), unreal.Rotator())
                    assert volume
                    volume.set_actor_label('PC_City_NavigationBounds_V1')
                    volume.set_actor_scale3d(unreal.Vector(210,210,5))
                    nav.on_navigation_bounds_updated(volume)
            else:
                assert len(found) == 1, 'Fresh run must load the retained bounds, not create it'
                volume = found[0]
                assert volume.get_actor_label() == 'PC_City_NavigationBounds_V1'
            assert volume.get_outer().get_outer().get_path_name().startswith(ENTRY+'.')
            origin, extent = volume.get_actor_bounds(False)
            assert abs(extent.x-21000)<1 and abs(extent.y-21000)<1 and abs(extent.z-500)<1
            report['volume'] = {'path': volume.get_path_name(), 'origin_cm': xyz(origin), 'extent_cm': xyz(extent)}
            phase = 'configure'
            write()
        elif phase == 'configure':
            found = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.RecastNavMesh)]
            if not found:
                return
            assert len(found) == 1
            nav_data = found[0]
            assert nav_data.get_outer().get_outer().get_path_name().startswith(ENTRY+'.')
            if AUTHOR:
                for key,value in (('agent_radius',34.0),('agent_height',193.0),('agent_max_slope',45.0)):
                    nav_data.set_editor_property(key,value)
            report['recast'] = {key: str(nav_data.get_editor_property(key)) for key in
                ('agent_radius','agent_height','agent_max_slope','tile_size_uu','runtime_generation')}
            report['recast']['path'] = nav_data.get_path_name()
            write()
            assert nav_data.get_editor_property('agent_radius') == 34.0 and nav_data.get_editor_property('agent_height') == 193.0
            assert nav_data.get_editor_property('agent_max_slope') == 45.0
            report['recast']['resolution_params'] = [{k: float(p.get_editor_property(k)) for k in
                ('cell_size','cell_height','agent_max_step_height')} for p in nav_data.get_editor_property('nav_mesh_resolution_params')]
            if AUTHOR:
                unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
            report['explicit_rebuild_requested'] = AUTHOR
            phase = 'coverage'
            write()
        elif phase == 'coverage':
            if unreal.NavigationSystemV1.is_navigation_being_built(world):
                return
            roster = [a for a in actors.get_all_level_actors() if a.get_actor_label().startswith('PC_City_') and isinstance(a,unreal.Character)]
            assert len(roster) == 6
            if project(next(a for a in roster if a.get_actor_label()=='PC_City_Player').get_actor_location()) is None:
                return
            collect_coverage()
            write()
            if AUTHOR:
                assert unreal.EditorAssetLibrary.save_asset(ENTRY,only_if_is_dirty=False)
                saved = True
                after = dict(map_item,size_bytes=map_file.stat().st_size,sha256=hashlib.sha256(map_file.read_bytes()).hexdigest())
                assert after['sha256'] != map_item['sha256']
                report['after_map'] = after
                inventory['scope'] = 'Retained navigation map plus unchanged six city/combat/HUD packages; fresh/runtime acceptance recorded separately'
                inventory['previous_checkpoint'] = 'CITY_PACKAGE_DRAFT_INVENTORY_20261002.json is historical for the map; never restore it over retained navigation'
                if RESAVE:
                    inventory['previous_checkpoint'] = 'Earlier navigation map/metadata retained in '+(OUT/'before_checkpoint.json').relative_to(ROOT).as_posix()+'; older city/package maps are historical, not current restoration authority'
                inventory['evidence'] = (OUT/'result.json').relative_to(ROOT).as_posix()
                inventory['files'] = [after if f['package']==ENTRY else f for f in inventory['files']]
                inventory['total_size_bytes'] = sum(f['size_bytes'] for f in inventory['files'])
                DEST.write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8')
                finish()
            else:
                # Later grip author evidence does not contain navigation coverage.
                coverage_inventory = inventory
                if native_name in ('CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json', 'CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json', 'CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json'):
                    coverage_inventory = json.loads(DEST.read_text(encoding='utf-8-sig'))
                report['retained_navigation_evidence'] = coverage_inventory['evidence']
                prior = json.loads((ROOT/coverage_inventory['evidence']).read_text())
                report['fresh_coverage_matches_saved'] = report['summary'] == prior['summary']
                assert report['fresh_coverage_matches_saved'], 'Fresh retained coverage differs from authoring result'
                levels.editor_request_begin_play()
                phase = 'live_wait'
                write()
        elif phase == 'live_wait':
            runtime = editor.get_game_world()
            if runtime is None or unreal.GameplayStatics.get_player_pawn(runtime,0) is None:
                return
            world = runtime
            nav = nav.call_method('GetNavigationSystem',args=(world,))
            found = list(unreal.GameplayStatics.get_all_actors_of_class(world,unreal.RecastNavMesh))
            assert nav and len(found)==1
            nav_data = found[0]
            if unreal.GameplayStatics.get_time_seconds(world)<3:
                return
            roster = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character) if a.get_class().get_name().startswith('BP_PCParis')]
            assert len(roster)==6
            phase = 'assign'
        elif phase == 'assign':
            select_move(move_index%2,move_index>=2)
            phase = 'moving'
        elif phase == 'moving':
            now = unreal.GameplayStatics.get_time_seconds(world)
            pos = move_actor.get_actor_location()
            distance = xy(pos-goal)
            status = controller.get_move_status()
            case = report['moves'][-1]
            if now-sample_time>=.25:
                case['samples'].append({'game_seconds':now-move_time,'position_cm':xyz(pos),
                    'speed_cm_s':move_actor.get_velocity().length(),'distance_cm':distance,'status':str(status)})
                sample_time = now
            if status==unreal.PathFollowingStatus.IDLE or now-move_time>75:
                case.update(elapsed_game_seconds=now-move_time,end_cm=xyz(pos),distance_cm=distance,
                            displacement_cm=xy(pos-unreal.Vector(*case['start_cm'])),native_status=str(status))
                case['arrived'] = distance<=65 and case['displacement_cm']>400 and status==unreal.PathFollowingStatus.IDLE
                controller.stop_movement()
                write()
                assert case['arrived'], 'Move did not reach measured destination within bound'
                move_index += 1
                phase = 'assign' if move_index<4 else 'unreachable'
        elif phase == 'unreachable':
            far = move_actor.get_actor_location()+unreal.Vector(1000000,1000000,0)
            assert project(far) is None
            result = request(far)
            report['unreachable'] = {'goal_cm':xyz(far),'request_result':str(result),
                'rejected':result==unreal.PathFollowingRequestResult.FAILED,'partial_paths_allowed':False}
            assert report['unreachable']['rejected']
            select_move(0,True)
            # The extra request is cancellation evidence, not an arrival case.
            report['cancel'] = report['moves'].pop()
            phase = 'cancel_wait'
        elif phase == 'cancel_wait':
            elapsed = unreal.GameplayStatics.get_time_seconds(world)-move_time
            progress = xy(move_actor.get_actor_location()-unreal.Vector(*report['cancel']['start_cm']))
            if progress<50:
                assert elapsed<5, 'Cancellation trial failed to start a valid move'
                return
            report['cancel']['progress_before_stop_cm'] = progress
            report['cancel']['status_before_stop'] = str(controller.get_move_status())
            report['cancel']['stop_position_cm'] = xyz(move_actor.get_actor_location())
            controller.stop_movement()
            move_time = unreal.GameplayStatics.get_time_seconds(world)
            phase = 'cancel_observe'
        elif phase == 'cancel_observe':
            if unreal.GameplayStatics.get_time_seconds(world)-move_time<1:
                return
            case = report['cancel']
            case['after_stop_displacement_cm'] = xy(move_actor.get_actor_location()-unreal.Vector(*case['stop_position_cm']))
            case['status_after_stop'] = str(controller.get_move_status())
            case['speed_after_stop_cm_s'] = move_actor.get_velocity().length()
            case['passed'] = controller.get_move_status()==unreal.PathFollowingStatus.IDLE and case['speed_after_stop_cm_s']<1 and case['after_stop_displacement_cm']<100
            assert case['passed']
            finish()
    except Exception:
        finish(traceback.format_exc())
    finally:
        in_tick = False


unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback = unreal.register_slate_post_tick_callback(tick)
write()
