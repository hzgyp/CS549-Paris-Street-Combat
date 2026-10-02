"""Unsaved editor API/volume capability probe on the real Paris entry; no nav pass."""
import hashlib
import json
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ.get('CS549_NAV_API_IDENTITY', 'api_v1')
assert IDENTITY.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/NavigationAI' / (IDENTITY + '.json')
assert not OUT.exists(), 'Preserve occupied evidence'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
guarded = {}
for name in ('RELOAD_DRAFT_SNAPSHOT_20261002.json', 'CITY_PACKAGE_DRAFT_INVENTORY_20261002.json'):
    for item in json.loads((ROOT / 'Assets/Integration' / name).read_text(encoding='utf-8-sig'))['files']:
        guarded[ROOT / item['path']] = item['sha256']
for p in (STORE / 'Content/WW2City/Maps').rglob('*.umap'):
    guarded[p] = hashlib.sha256(p.read_bytes()).hexdigest()
report = {'identity': IDENTITY, 'engine': unreal.SystemLibrary.get_engine_version(),
          'scope': 'Installed API and transient volume brush capability only; no saved navigation, MoveTo, AI or route pass',
          'classes': {}, 'errors': []}
trial = None
try:
    assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
    for path, expected in guarded.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, str(path)
    for name in ('NavigationSystemV1', 'NavigationPath', 'NavMeshBoundsVolume', 'RecastNavMesh', 'AIController',
                 'BlackboardData', 'BlackboardEntry', 'BlackboardDataFactory', 'BehaviorTreeFactory',
                 'BTService_BlueprintBase', 'BTTask_BlueprintBase'):
        cls = getattr(unreal, name, None)
        report['classes'][name] = {'available': cls is not None}
        if cls is not None:
            methods = [n for n in dir(cls) if any(s in n.lower() for s in ('navigation', 'project_point', 'find_path',
                       'move_to', 'stop_move', 'blackboard', 'behavior_tree', 'runtime_generation', 'bounds', 'path_point'))]
            report['classes'][name]['methods'] = {n: str(getattr(cls, n).__doc__) for n in methods}
    assert unreal.EditorLevelLibrary.load_level(ENTRY)
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_current_level_by_name(unreal.Name(ENTRY.rsplit('/', 1)[1]))
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = list(subsystem.get_all_level_actors())
    report['existing_navigation'] = [{'path': a.get_path_name(), 'class': a.get_class().get_path_name()}
                                     for a in actors if isinstance(a, (unreal.NavMeshBoundsVolume, unreal.RecastNavMesh))]
    report['capsules'] = []
    for actor in actors:
        if actor.get_actor_label().startswith('PC_City_'):
            capsule = actor.get_component_by_class(unreal.CapsuleComponent)
            report['capsules'].append({'label': actor.get_actor_label(), 'radius_cm': capsule.get_unscaled_capsule_radius(),
                                       'half_height_cm': capsule.get_unscaled_capsule_half_height()})
    assert len(report['capsules']) == 6
    trial = subsystem.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(0, 0, 100),
                                             unreal.Rotator(), transient=True)
    assert trial is not None, 'Standard editor actor factory did not create a volume'
    report['trial_level'] = trial.get_outer().get_outer().get_path_name()
    assert report['trial_level'].startswith(ENTRY + '.'), 'Trial belongs only in the team root'
    origin, extent = trial.get_actor_bounds(False)
    report['trial_bounds_initial'] = {'origin': [origin.x, origin.y, origin.z], 'extent': [extent.x, extent.y, extent.z]}
    assert min(extent.x, extent.y, extent.z) > 0, 'Actor transform alone cannot substitute for a brush'
    trial.set_actor_scale3d(unreal.Vector(2, 3, 4))
    origin, scaled = trial.get_actor_bounds(False)
    report['trial_bounds_scaled'] = {'origin': [origin.x, origin.y, origin.z], 'extent': [scaled.x, scaled.y, scaled.z]}
    assert abs(scaled.x / extent.x - 2) < .001 and abs(scaled.y / extent.y - 3) < .001 and abs(scaled.z / extent.z - 4) < .001
    report['status'] = 'pass_unsaved_api_volume_probe_not_navigation_acceptance'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    if trial is not None:
        unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(trial)
    report['guarded_bytes_unchanged'] = all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in guarded.items())
    if not report['guarded_bytes_unchanged']:
        report['status'] = 'failed'
        report['errors'].append('Unexpected native byte change')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_NAV_API ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved navigation API report')
