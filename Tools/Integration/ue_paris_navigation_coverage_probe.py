"""Unsaved actual-city NavMesh coverage/path trial, not live MoveTo/AI acceptance."""
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ.get('CS549_NAV_COVERAGE_IDENTITY', 'coverage_v1')
LIVE = os.environ.get('CS549_NAV_LIVE', '0') == '1'
assert IDENTITY.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/NavigationAI' / (IDENTITY + '.json')
assert not OUT.exists(), 'Preserve occupied evidence'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
guarded = {}
for name in ('RELOAD_DRAFT_SNAPSHOT_20261002.json', 'CITY_PACKAGE_DRAFT_INVENTORY_20261002.json'):
    for f in json.loads((ROOT / 'Assets/Integration' / name).read_text(encoding='utf-8-sig'))['files']:
        guarded[ROOT / f['path']] = f['sha256']
for p in (STORE / 'Content/WW2City/Maps').glob('*.umap'):
    guarded[p] = hashlib.sha256(p.read_bytes()).hexdigest()
assert all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in guarded.items())
survey = json.loads((STORE / 'Evidence/CityGameplay20261002/Survey/structure_v3.json').read_text())
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
report = {'identity': IDENTITY, 'scope': __doc__ if not LIVE else 'Unsaved actual-city navigation plus two ordinary live MoveTo trials; not shared BT, whole-city or mission acceptance',
          'errors': [], 'status': 'initializing', 'samples': [], 'starts': [], 'live_moves': []}
callback = None
volume = None
world = None
nav_data = None
nav_system = None
started = time.monotonic()
phase = 'setup'
in_tick = False
move_actor = move_controller = move_goal = runtime_world = None
move_index = 0
move_time = sample_time = 0
ending_since = None

def xyz(v):
    return [v.x, v.y, v.z]

def xy_length(v):
    return (v.x * v.x + v.y * v.y) ** .5

def write():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

def finish(error=None):
    global phase
    if error:
        report['errors'].append(error)
    report['status'] = ('failed' if report['errors'] else
                        'completed_two_live_move_trials_not_shared_ai_or_mission_pass' if LIVE else
                        'completed_unsaved_paths_not_move_to_or_ai_pass')
    report['elapsed_wall_seconds'] = time.monotonic() - started
    report['guarded_bytes_unchanged'] = all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in guarded.items())
    if not report['guarded_bytes_unchanged']:
        report['status'] = 'failed'
        report['errors'].append('Unexpected native byte change')
    write()
    if levels.is_in_play_in_editor():
        levels.editor_request_end_play()
        phase = 'ending'
        return
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
    # Live PIE teardown restores editor navigation in a later engine frame.
    # Do not unregister its ordinary volume during that teardown; discard the
    # unsaved editor world through normal unattended exit instead.
    if volume is not None and not LIVE:
        actors.destroy_actor(volume)
    unreal.SystemLibrary.quit_editor()

def project(point):
    if LIVE and runtime_world is not None:
        result = nav_system.call_method('K2_ProjectPointToNavigation', args=(world, point, nav_data, None, unreal.Vector(100, 100, 120)))
        if isinstance(result, tuple):
            if any(isinstance(v, bool) and not v for v in result):
                return None
            return next((v for v in result if isinstance(v, unreal.Vector)), None)
        assert result is None or isinstance(result, unreal.Vector), repr(result)
        return result
    return unreal.NavigationSystemV1.project_point_to_navigation(world, point, nav_data, None, unreal.Vector(100, 100, 120))

def path_record(start, goal, context):
    path = (nav_system.call_method('FindPathToLocationSynchronously', args=(world, start, goal, context, None))
            if LIVE and runtime_world is not None else
            unreal.NavigationSystemV1.find_path_to_location_synchronously(world, start, goal, context))
    if path is None:
        return {'valid': False, 'partial': None, 'points_cm': []}
    pts = list(path.get_editor_property('path_points'))
    return {'valid': path.is_valid(), 'partial': path.is_partial(), 'points_cm': [xyz(p) for p in pts],
            'length_cm': sum((b - a).length() for a, b in zip(pts, pts[1:]))}

def tick(delta):
    global world, volume, nav_data, nav_system, phase, in_tick, runtime_world
    global move_actor, move_controller, move_goal, move_index, move_time, sample_time, ending_since
    if in_tick:
        return
    in_tick = True
    try:
        if phase == 'ending':
            if not levels.is_in_play_in_editor() and editor.get_game_world() is None:
                if ending_since is None:
                    ending_since = time.monotonic()
                elif time.monotonic() - ending_since >= 1:
                    finish()
            return
        if time.monotonic() - started > 180:
            finish('Bounded navigation generation timeout')
            return
        if phase == 'setup':
            assert levels.load_level(ENTRY)
            assert levels.set_current_level_by_name(unreal.Name(ENTRY.rsplit('/', 1)[1]))
            world = editor.get_editor_world()
            assert not any(isinstance(a, unreal.NavMeshBoundsVolume) for a in actors.get_all_level_actors())
            center = survey['sampling']['center_cm']
            # A transient-only volume is intentionally excluded by PIE duplication.
            # Live trials need an ordinary unsaved team-root volume, never a disk save.
            volume = actors.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(center[0], center[1], 200), unreal.Rotator(), transient=not LIVE)
            assert volume and volume.get_outer().get_outer().get_path_name().startswith(ENTRY + '.')
            volume.set_actor_scale3d(unreal.Vector(110, 110, 5))
            origin, extent = volume.get_actor_bounds(False)
            assert abs(extent.x - 11000) < 1 and abs(extent.y - 11000) < 1
            report['volume'] = {'origin_cm': xyz(origin), 'extent_cm': xyz(extent), 'not_mission_boundary': True}
            nav = unreal.NavigationSystemV1.get_navigation_system(world)
            assert nav, 'Editor world has no navigation system'
            nav_system = nav
            nav.on_navigation_bounds_updated(volume)
            phase = 'configure'
            write()
        elif phase == 'configure':
            found = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.RecastNavMesh)]
            if not found:
                return
            nav_data = found[0]
            for key, value in (('agent_radius', 34.0), ('agent_height', 193.0), ('agent_max_slope', 45.0)):
                nav_data.set_editor_property(key, value)
            report['recast'] = {key: str(nav_data.get_editor_property(key)) for key in (
                'agent_radius', 'agent_height', 'agent_max_slope', 'tile_size_uu', 'runtime_generation')}
            # UE 5.8 deprecated/protected the old scalar CellSize/Height/Step fields.
            # Keep its supported per-resolution defaults, conservatively record them.
            params = nav_data.get_editor_property('nav_mesh_resolution_params')
            report['recast']['resolution_params'] = [{key: float(p.get_editor_property(key)) for key in
                ('cell_size', 'cell_height', 'agent_max_step_height')} for p in params]
            unreal.SystemLibrary.execute_console_command(world, 'RebuildNavigation')
            phase = 'building'
            write()
        elif phase == 'building':
            if unreal.NavigationSystemV1.is_navigation_being_built(world):
                return
            roster = [a for a in actors.get_all_level_actors() if a.get_actor_label().startswith('PC_City_')]
            assert len(roster) == 6
            player = next(a for a in roster if a.get_actor_label() == 'PC_City_Player')
            start = project(player.get_actor_location())
            if start is None:
                return
            for actor in roster:
                goal = project(actor.get_actor_location())
                report['starts'].append({'label': actor.get_actor_label(), 'projected_cm': xyz(goal) if goal else None,
                                        'path': path_record(start, goal, player) if goal else None})
            for sample in survey['ground']:
                if not sample['candidate']:
                    continue
                point = unreal.Vector(*sample['hit']['impact_cm'])
                if point.z < -300 or point.z > 600:
                    continue
                goal = project(point)
                report['samples'].append({'grid': sample['grid'], 'ground_cm': xyz(point), 'projected_cm': xyz(goal) if goal else None,
                                         'path': path_record(start, goal, player) if goal else None})
            report['summary'] = {'street_candidates': len(report['samples']),
                'projected': sum(s['projected_cm'] is not None for s in report['samples']),
                'complete_from_player': sum(bool(s['path']) and s['path']['valid'] and not s['path']['partial'] for s in report['samples']),
                'six_starts_projected': all(s['projected_cm'] is not None for s in report['starts']),
                'five_npcs_complete': all(bool(s['path']) and s['path']['valid'] and not s['path']['partial']
                    for s in report['starts'] if s['label'] != 'PC_City_Player')}
            # A same-location player-to-self path can be IsValid=false with one point.
            # Retain that raw result; it is not a failed player-to-NPC connection.
            if not LIVE:
                finish()
            else:
                phase = 'live_wait'
                levels.editor_request_begin_play()
                write()
        elif phase == 'live_wait':
            runtime_world = editor.get_game_world()
            if runtime_world is None or unreal.GameplayStatics.get_player_pawn(runtime_world, 0) is None:
                return
            nav_system = nav_system.call_method('GetNavigationSystem', args=(runtime_world,))
            assert nav_system is not None, 'PIE world navigation system missing'
            world = runtime_world
            found = list(unreal.GameplayStatics.get_all_actors_of_class(world, unreal.RecastNavMesh))
            assert found, 'Unsaved editor NavMesh did not duplicate into PIE'
            nav_data = found[0]
            if unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            phase = 'live_assign'
        elif phase == 'live_assign':
            roster = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                      if a.get_class().get_name().startswith('BP_PCParis')]
            player = unreal.GameplayStatics.get_player_pawn(world, 0)
            chosen = sorted((a for a in roster if a != player and a.get_editor_property('TeamId') == move_index), key=lambda a: a.get_name())
            assert chosen, 'No retained trial NPC'
            move_actor = chosen[0]
            move_controller = unreal.AIHelperLibrary.get_ai_controller(move_actor)
            assert move_controller is not None, 'Placed NPC lacks an engine AIController'
            start_pos = move_actor.get_actor_location()
            candidates = []
            for sample in report['samples']:
                if sample['projected_cm'] is None:
                    continue
                goal = project(unreal.Vector(*sample['ground_cm']))
                if goal is None or not (600 < xy_length(goal - start_pos) < 2000):
                    continue
                if any(xy_length(goal - a.get_actor_location()) < 180 for a in roster):
                    continue
                route = path_record(start_pos, goal, move_actor)
                if route['valid'] and not route['partial'] and route['length_cm'] < 2500:
                    candidates.append((abs(route['length_cm'] - 1200), sample['grid'], goal, route))
            assert candidates, 'No measured complete local live trial route'
            _, grid, move_goal, route = min(candidates, key=lambda c: (c[0], c[1]))
            result = move_controller.move_to_location(move_goal, acceptance_radius=30.0, stop_on_overlap=False,
                use_pathfinding=True, project_destination_to_navigation=False, can_strafe=True, allow_partial_path=False)
            move_time = sample_time = unreal.GameplayStatics.get_time_seconds(world)
            report['live_moves'].append({'team': move_index, 'actor': move_actor.get_class().get_path_name(),
                'controller': move_controller.get_class().get_path_name(), 'start_cm': xyz(start_pos), 'goal_cm': xyz(move_goal),
                'ground_grid': grid, 'complete_path': route, 'request_result': str(result), 'samples': [],
                'request_accepted': result == unreal.PathFollowingRequestResult.REQUEST_SUCCESSFUL})
            assert report['live_moves'][-1]['request_accepted'], 'Native MoveTo rejected request'
            phase = 'live_moving'
            write()
        elif phase == 'live_moving':
            now = unreal.GameplayStatics.get_time_seconds(world)
            pos = move_actor.get_actor_location()
            distance = xy_length(pos - move_goal)
            status = move_controller.get_move_status()
            case = report['live_moves'][-1]
            if now - sample_time >= .25:
                case['samples'].append({'game_seconds': now - move_time, 'position_cm': xyz(pos),
                    'speed_cm_s': move_actor.get_velocity().length(), 'distance_2d_cm': distance, 'move_status': str(status)})
                sample_time = now
            if status == unreal.PathFollowingStatus.IDLE or now - move_time > 25:
                case['elapsed_game_seconds'] = now - move_time
                case['end_cm'] = xyz(pos)
                case['distance_2d_cm'] = distance
                case['displacement_cm'] = xy_length(pos - unreal.Vector(*case['start_cm']))
                case['arrived'] = distance <= 65 and case['displacement_cm'] > 400 and status == unreal.PathFollowingStatus.IDLE
                move_controller.stop_movement()
                write()
                assert case['arrived'], 'MoveTo failed/stalled/timed out before measured arrival'
                move_index += 1
                if move_index == 2:
                    report['two_live_moves_passed'] = all(c['arrived'] for c in report['live_moves'])
                    finish()
                else:
                    phase = 'live_assign'
    except Exception:
        finish(traceback.format_exc())
    finally:
        in_tick = False

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback = unreal.register_slate_post_tick_callback(tick)
write()
