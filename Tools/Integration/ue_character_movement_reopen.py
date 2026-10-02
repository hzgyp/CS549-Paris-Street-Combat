"""Read-only fresh load with ParisEditorBridge DISABLED; dependency/graph check."""
import json
import traceback
from datetime import datetime
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2/Movement'
BP = '/Game/ParisCombat/Blueprints/Characters/'
REPORT = {'started_at': datetime.now().astimezone().isoformat(), 'errors': [], 'actors': [], 'blueprints': [],
          'engine': unreal.SystemLibrary.get_engine_version(), 'bridge_reflected': hasattr(unreal, 'ParisBlueprintAuthoring')}
try:
    if REPORT['bridge_reflected']:
        raise RuntimeError('Fresh reopen must NOT enable the editor bridge')
    authored = json.loads((OUT / 'authoring.json').read_text(encoding='utf-8'))
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    options = unreal.AssetRegistryDependencyOptions(include_hard_package_references=True, include_soft_package_references=True)
    for path in authored['bridge']['assets']:
        asset = unreal.load_asset(path)
        if not asset:
            raise RuntimeError('Missing generated draft: ' + path)
        dependencies = [str(v) for v in registry.get_dependencies(path, options)]
        if any('ParisEditorBridge' in v for v in dependencies):
            raise RuntimeError('Unwanted bridge dependency: ' + path)
        if isinstance(asset, unreal.Blueprint):
            unreal.BlueprintEditorLibrary.compile_blueprint(asset)
            cls = asset.generated_class()
            if not cls:
                raise RuntimeError('Generated class missing: ' + path)
            REPORT['blueprints'].append({'path': path, 'class': cls.get_path_name(), 'dependencies': dependencies})
    if not unreal.EditorLevelLibrary.load_level(authored['map']):
        raise RuntimeError('Movement map fresh load failed')
    expected = {a['label']: a for a in authored['actors']}
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in actors.get_all_level_actors():
        label = actor.get_actor_label()
        if label not in expected:
            continue
        e = expected[label]
        mesh = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        capsule = actor.get_component_by_class(unreal.CapsuleComponent)
        values = {'label': label, 'character': isinstance(actor, unreal.Character),
                  'class': actor.get_class().get_path_name(), 'mesh': mesh.get_skinned_asset().get_path_name(),
                  'anim_class': mesh.get_editor_property('anim_class').get_path_name(),
                  'capsule_half_height_cm': capsule.get_unscaled_capsule_half_height(),
                  'mesh_z_offset_cm': mesh.get_editor_property('relative_location').z,
                  'team': actor.get_editor_property('TeamId'), 'role': str(actor.get_editor_property('RoleId'))}
        if not values['character'] or any(values[k] != e[k] for k in ('class', 'mesh', 'anim_class')):
            raise RuntimeError('Persisted configuration mismatch: ' + label)
        REPORT['actors'].append(values)
    if len(REPORT['actors']) != 6:
        raise RuntimeError('Six persisted Characters required')
    REPORT['result'] = 'pass_fresh_load_without_bridge'
except Exception:
    REPORT['errors'].append(traceback.format_exc())
    REPORT['result'] = 'fail'
REPORT['finished_at'] = datetime.now().astimezone().isoformat()
(OUT / 'fresh_reopen.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')
unreal.log('CS549_MOVEMENT_REOPEN_DONE ' + REPORT['result'])
if REPORT['errors']:
    raise RuntimeError('Read Movement/fresh_reopen.json')
