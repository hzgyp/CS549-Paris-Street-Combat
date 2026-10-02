"""Read-only existing-city structural/ground survey; never save the vendor map."""
import hashlib
import json
import math
import os
import traceback
from collections import Counter, deque
from datetime import datetime
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/Survey'
IDENTITY = os.environ.get('CS549_CITY_SURVEY_IDENTITY', 'structure_v1')
assert IDENTITY.replace('_', '').isalnum(), 'Unsafe report identity'
DEST = OUT / (IDENTITY + '.json')
assert not DEST.exists(), 'Preserve occupied survey evidence'
OUT.mkdir(parents=True, exist_ok=True)
MAP = '/Game/WW2City/Maps/LV_Paris_WW2'
MAP_FILE = STORE / 'Content/WW2City/Maps/LV_Paris_WW2.umap'
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def xyz(v):
    return [float(v.x), float(v.y), float(v.z)]


def decode(hit):
    # Installed UE signature returns a HitResult, not (bool, HitResult).
    if hit is None:
        return {'blocking': False}
    fields = hit.to_tuple()
    assert len(fields) >= 11 and isinstance(fields[0], bool), 'Unexpected native HitResult break tuple'
    return {'blocking': bool(fields[0]), 'initial_overlap': bool(fields[1]),
            'distance_cm': float(fields[3]), 'location_cm': xyz(fields[4]),
            'impact_cm': xyz(fields[5]), 'normal': xyz(fields[7]),
            'actor': fields[9].get_path_name() if fields[9] else None,
            'label': fields[9].get_actor_label() if fields[9] else None,
            'component': fields[10].get_path_name() if fields[10] else None}


before = digest(MAP_FILE)
snapshot = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
report = {'started_at': datetime.now().astimezone().isoformat(), 'identity': IDENTITY,
          'engine': unreal.SystemLibrary.get_engine_version(), 'source_map': MAP,
          'scope': 'Unsaved actual-city inventory and geometric ground/capsule queries only; not NavMesh, live input, mission, travel-time or performance acceptance',
          'errors': [], 'map_sha256_before': before, 'ground': [], 'segments': []}


def checkpoint():
    DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')


try:
    for item in snapshot['files']:
        path = ROOT / item['path']
        assert path.stat().st_size == item['size_bytes'] and digest(path) == item['sha256'], item['path']
    assert unreal.EditorLevelLibrary.load_level(MAP), 'City map load failed'
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = list(subsystem.get_all_level_actors())
    report['actor_count'] = len(actors)
    report['class_counts'] = dict(Counter(a.get_class().get_name() for a in actors))
    report['level_counts'] = dict(Counter(a.get_outer().get_path_name() for a in actors))
    report['world_api'] = [n for n in dir(world) if any(x in n.lower() for x in ('partition', 'stream', 'level', 'navigation'))]
    report['navigation_actors'] = [{'path': a.get_path_name(), 'class': a.get_class().get_name()}
                                  for a in actors if any(k in a.get_class().get_name() for k in ('NavMesh', 'Recast', 'Navigation'))]
    starts = [a for a in actors if isinstance(a, unreal.PlayerStart)]
    report['player_starts'] = [{'path': a.get_path_name(), 'location_cm': xyz(a.get_actor_location()),
                              'rotation': str(a.get_actor_rotation())} for a in starts]
    report['api_docs'] = {name: getattr(cls, method).__doc__ for name, cls, method in (
        ('line_trace_single', unreal.SystemLibrary, 'line_trace_single'),
        ('capsule_trace_single', unreal.SystemLibrary, 'capsule_trace_single'))}
    report['api_docs']['HitResult'] = unreal.HitResult.__doc__
    report['api_docs']['HitResult.to_tuple'] = unreal.HitResult.to_tuple.__doc__
    report['level_api_docs'] = {n: getattr(unreal.EditorLevelUtils, n).__doc__
                               for n in dir(unreal.EditorLevelUtils)
                               if any(k in n for k in ('add_level', 'create_new_streaming', 'get_levels'))}
    geometry = []
    for actor in actors:
        if isinstance(actor, unreal.StaticMeshActor):
            origin, extent = actor.get_actor_bounds(False)
            geometry.append({'label': actor.get_actor_label(), 'path': actor.get_path_name(),
                             'location_cm': xyz(actor.get_actor_location()), 'origin_cm': xyz(origin),
                             'extent_cm': xyz(extent),
                             'mesh': actor.static_mesh_component.static_mesh.get_path_name() if actor.static_mesh_component.static_mesh else None})
    report['geometry'] = geometry
    if geometry:
        report['geometry_bounds_cm'] = {
            'min': [min(g['origin_cm'][i] - g['extent_cm'][i] for g in geometry) for i in range(3)],
            'max': [max(g['origin_cm'][i] + g['extent_cm'][i] for g in geometry) for i in range(3)]}
    checkpoint()
    assert starts, 'No player start for initial local survey'
    center = starts[0].get_actor_location()
    cls = unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/BP_PCPlayerReloadV1')
    assert cls, 'Retained player reload class missing'
    capsule = unreal.get_default_object(cls).get_editor_property('capsule_component')
    radius = capsule.get_unscaled_capsule_radius()
    half_height = capsule.get_unscaled_capsule_half_height()
    report['capsule_cm'] = {'radius': radius, 'half_height': half_height}
    # This local initial sampling window is not a chosen mission boundary.
    step = 1000
    report['sampling'] = {'center_cm': xyz(center), 'step_cm': step, 'grid_side': 21,
                          'note': 'Initial street-height local probes; expand from actual overhead findings, not a predetermined mission limit'}
    ground = {}
    for i in range(-10, 11):
        for j in range(-10, 11):
            x, y = center.x + i * step, center.y + j * step
            hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, center.z + 300),
                unreal.Vector(x, y, center.z - 2000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                False, [], unreal.DrawDebugTrace.NONE, True)
            sample = {'grid': [i, j], 'xy_cm': [x, y], 'hit': decode(hit)}
            sample['candidate'] = sample['hit']['blocking'] and sample['hit']['normal'][2] >= .7
            if sample['candidate']:
                ground[(i, j)] = sample['hit']['impact_cm']
            report['ground'].append(sample)
    checkpoint()
    edges = {}
    for key, pos in ground.items():
        for di, dj in ((1, 0), (0, 1)):
            other = (key[0] + di, key[1] + dj)
            if other not in ground:
                continue
            target = ground[other]
            if abs(pos[2] - target[2]) > 30:
                continue
            a = unreal.Vector(pos[0], pos[1], pos[2] + half_height + 3)
            b = unreal.Vector(target[0], target[1], target[2] + half_height + 3)
            hit = decode(unreal.SystemLibrary.capsule_trace_single(world, a, b, radius, half_height,
                unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True))
            clear = not hit['blocking']
            report['segments'].append({'from_grid': list(key), 'to_grid': list(other), 'clear': clear, 'hit': hit})
            if clear:
                edges.setdefault(key, []).append(other)
                edges.setdefault(other, []).append(key)
    components = []
    remaining = set(ground)
    while remaining:
        seed = min(remaining)
        reached, queue = {seed}, deque([seed])
        while queue:
            for other in edges.get(queue.popleft(), []):
                if other not in reached:
                    reached.add(other)
                    queue.append(other)
        remaining -= reached
        components.append(sorted(reached))
    components.sort(key=len, reverse=True)
    report['geometric_components'] = [{'count': len(c), 'grid_points': [list(k) for k in c]} for c in components]
    report['status'] = 'pass_readonly_inventory_ground_queries_only'
except Exception:
    report['errors'].append(traceback.format_exc())
    report['status'] = 'failed'
finally:
    report['map_sha256_after'] = digest(MAP_FILE)
    report['map_unchanged'] = report['map_sha256_after'] == before
    report['previous_28_drafts_unchanged'] = all((ROOT / f['path']).stat().st_size == f['size_bytes']
        and digest(ROOT / f['path']) == f['sha256'] for f in snapshot['files'])
    report['finished_at'] = datetime.now().astimezone().isoformat()
    if not report['map_unchanged'] or not report['previous_28_drafts_unchanged']:
        report['errors'].append('Unexpected saved byte change')
        report['status'] = 'failed'
    checkpoint()
unreal.log('CS549_PARIS_CITY_SURVEY ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved city survey report')
