"""Unsaved daylight city views and paired road-collision observations."""
import hashlib
import json
import os
import traceback
from datetime import datetime
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ.get('CS549_CITY_CAPTURE_IDENTITY', 'views_v1')
assert IDENTITY.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/Survey' / IDENTITY
assert not OUT.exists(), 'Preserve occupied views'
OUT.mkdir(parents=True)
MAP = os.environ.get('CS549_CITY_CAPTURE_MAP', '/Game/WW2City/Maps/LV_Paris_WW2')
assert MAP in ('/Game/WW2City/Maps/LV_Paris_WW2', '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1')
MAP_FILE = STORE / 'Content' / (MAP.removeprefix('/Game/') + '.umap')
before = hashlib.sha256(MAP_FILE.read_bytes()).hexdigest()
report = {'started_at': datetime.now().astimezone().isoformat(), 'engine': unreal.SystemLibrary.get_engine_version(),
          'scope': 'Unsaved daylight visual/collision survey; no route, mission, NavMesh, gameplay or performance pass',
          'captures': [], 'paired_ground': [], 'hidden_lighting': [], 'errors': []}
camera = None


def xyz(v):
    return [v.x, v.y, v.z]


def checkpoint():
    (OUT / 'capture.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


try:
    editor_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if not editor_world or editor_world.get_path_name() != MAP + '.' + MAP.rsplit('/', 1)[1]:
        assert unreal.EditorLevelLibrary.load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    report['level_visibility_api'] = unreal.EditorLevelUtils.set_level_visibility.__doc__
    for level in unreal.EditorLevelUtils.get_levels(world):
        package = level.get_outer().get_path_name()
        if any(k in package for k in ('LV_Lighting_Midnight', 'LV_Lighting_WarFog')):
            unreal.EditorLevelUtils.set_level_visibility(level, False, False)
            report['hidden_lighting'].append(package)
    loaded_actors = actors.get_all_level_actors()
    start = next((a for a in loaded_actors if a.get_actor_label() == 'PC_City_Player'), None)
    if not start:
        start = next(a for a in loaded_actors if isinstance(a, unreal.PlayerStart))
    at = start.get_actor_location()
    report['player_start_cm'] = xyz(at)
    ignored_roster = [a for a in loaded_actors if a.get_actor_label().startswith('PC_City_')]
    report['ground_query_ignored_roster'] = [a.get_actor_label() for a in ignored_roster]
    checkpoint()
    for dx, dy in ((0, 0), (-400, 0), (400, 0), (0, -400), (0, 400),
                   (-2000, 0), (2000, 0), (0, -2000), (0, 2000)):
        sample = {'xy_cm': [at.x + dx, at.y + dy], 'hits': []}
        for complex_query in (False, True):
            hit = unreal.SystemLibrary.line_trace_single(world,
                unreal.Vector(at.x + dx, at.y + dy, at.z + 300),
                unreal.Vector(at.x + dx, at.y + dy, at.z - 2000),
                unreal.TraceTypeQuery.ECC_VISIBILITY, complex_query, ignored_roster, unreal.DrawDebugTrace.NONE, True)
            item = {'complex': complex_query, 'blocking': bool(hit)}
            if hit:
                values = hit.to_tuple()
                item.update({'blocking': bool(values[0]), 'impact_cm': xyz(values[5]),
                             'normal': xyz(values[7]), 'label': values[9].get_actor_label() if values[9] else None})
                component = values[10]
                if isinstance(component, unreal.StaticMeshComponent):
                    mesh = component.static_mesh
                    item['mesh'] = mesh.get_path_name() if mesh else None
                    item['collision_profile'] = str(component.get_collision_profile_name())
                    item['collision_enabled'] = str(component.get_collision_enabled())
            sample['hits'].append(item)
        report['paired_ground'].append(sample)
    checkpoint()
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    camera = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(at.x, at.y, 25000))
    capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property('capture_every_frame', False)
    capture.set_editor_property('capture_on_movement', False)
    target = unreal.RenderingLibrary.create_render_target2d(world, 1536, 1024,
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.05, .05, .05, 1), False)
    capture.set_editor_property('texture_target', target)
    shots = [('city_overhead', (at.x, at.y, 45000), (at.x, at.y, 0), 90),
             ('start_overhead', (at.x, at.y, 17000), (at.x, at.y, 0), 90),
             ('street_forward', (at.x, at.y, at.z + 64), (at.x + 2500, at.y, at.z + 64), 90),
             ('street_reverse', (at.x, at.y, at.z + 64), (at.x - 2500, at.y, at.z + 64), 90)]
    if start.get_actor_label() == 'PC_City_Player':
        eye = start.get_component_by_class(unreal.CameraComponent).get_world_location()
        report['actual_player_camera_cm'] = xyz(eye)
        shots.append(('player_camera_candidate', tuple(xyz(eye)), (eye.x + 2500, eye.y, eye.z), 90))
        shots.append(('roster_staging', (at.x - 800, at.y - 500, at.z + 300),
                      (at.x, at.y + 200, at.z - 30), 65))
    for name, position, aim, fov in shots:
        location = unreal.Vector(*position)
        camera.set_actor_location(location, False, False)
        camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(location, unreal.Vector(*aim)), False)
        capture.set_editor_property('fov_angle', fov)
        # Repeated captures provide temporal exposure/streaming settling, not FPS data.
        for unused in range(4):
            capture.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), name + '.png')
        file = OUT / (name + '.png')
        assert file.is_file() and file.stat().st_size > 1000
        report['captures'].append({'file': file.relative_to(ROOT).as_posix(), 'size_bytes': file.stat().st_size,
                                   'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                                   'camera_cm': list(position), 'aim_cm': list(aim)})
        checkpoint()
    report['status'] = 'captured_readonly_views_for_review'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    if camera:
        actors.destroy_actor(camera)
    report['map_unchanged'] = hashlib.sha256(MAP_FILE.read_bytes()).hexdigest() == before
    if not report['map_unchanged']:
        report['errors'].append('Unexpected city save')
        report['status'] = 'failed'
    report['finished_at'] = datetime.now().astimezone().isoformat()
    checkpoint()
unreal.log('CS549_CITY_CAPTURE ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved capture report')
