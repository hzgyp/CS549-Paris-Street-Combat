"""Read-only active-project character inspection plus bounded city package probe."""
import json
import os
import runpy
import traceback
from datetime import datetime
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P1'
OUT.mkdir(parents=True, exist_ok=True)
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
os.environ['CS549_INVENTORY_OUT'] = str(OUT)
os.environ['CS549_INVENTORY_PREFIXES'] = '/Game/GermanSoldier,/Game/USParatrooper,/Game/RifleAnimsetPro,/Game/ParisCombat/Characters/Adaptation'
runpy.run_path(str(ROOT / 'Tools/AssetValidation/ue_inventory.py'), run_name='__main__')
inventory = json.loads((OUT / 'ue_load_inventory.json').read_text(encoding='utf-8'))
report = {'engine': unreal.SystemLibrary.get_engine_version(),
    'project': str(Path(unreal.Paths.project_dir()).resolve()), 'checked_at': datetime.now().astimezone().isoformat(),
    'character_packages': inventory['loaded_count'], 'errors': list(inventory['errors']),
    'city_probe_limit': 'World package object only; no editor viewport, streamed external actors, city survey, rendering, collision/NavMesh or gameplay pass',
    'city_world': None, 'adapted_models': [], 'blueprint_api': {}}
try:
    world = unreal.load_asset('/Game/WW2City/Maps/LV_Paris_WW2')
    if not world:
        raise RuntimeError('City World package did not load')
    report['city_world'] = {'path': world.get_path_name(), 'class': world.get_class().get_name()}
except Exception:
    report['errors'].append({'city_world': traceback.format_exc()})
assets = {a['path']: a for a in inventory['assets']}
for name in ('SK_WWII_GermanSoldier_varA_UE582_v1', 'SK_WWII_GermanSoldier_varB_UE582_v1',
             'SK_WWII_US_Paratrooper_simple_UE582_v1', 'SK_WWII_US_Paratrooper_simpleB_UE582_v1'):
    path = '/Game/ParisCombat/Characters/Adaptation/Meshes/' + name
    entry = assets.get(path, {})
    eyes = [m for m in entry.get('materials', []) if '/M_EyePBR_' in (m['material'] or '')]
    report['adapted_models'].append({'path': path, 'eye_bindings': eyes, 'skeleton': entry.get('skeleton'), 'physics_asset': entry.get('physics_asset')})
    if len(eyes) != 1 or not entry.get('loaded'):
        report['errors'].append({'adaptation': 'Expected one persisted eye material on ' + path})
for name in ('BlueprintEditorLibrary', 'BlueprintFactory', 'SubobjectDataSubsystem', 'AnimBlueprintFactory'):
    if hasattr(unreal, name):
        report['blueprint_api'][name] = [n for n in dir(getattr(unreal, name)) if not n.startswith('_')]
report['finished_at'] = datetime.now().astimezone().isoformat()
report['next_step_api_docs'] = {}
for class_name, method_names in {
    'BlueprintEditorLibrary': ('create_blueprint_asset_with_parent', 'compile_blueprint', 'add_member_variable'),
    'Character': ('get_component_by_class', 'get_editor_property'),
    'SkeletalMeshComponent': ('override_animation_data', 'set_skeletal_mesh_asset'),
    'EditorLevelLibrary': ('new_level', 'save_current_level'),
}.items():
    cls = getattr(unreal, class_name, None)
    for method_name in method_names:
        method = getattr(cls, method_name, None)
        if method:
            report['next_step_api_docs'][class_name + '.' + method_name] = method.__doc__
report['result'] = 'pass_structural_probe' if inventory['loaded_count'] == 540 and not report['errors'] else 'fail'
(OUT / 'active_project_probe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_ACTIVE_PROJECT_PROBE_DONE ' + report['result'])
if report['result'] != 'pass_structural_probe':
    raise RuntimeError('Read active_project_probe.json for actual failures')
