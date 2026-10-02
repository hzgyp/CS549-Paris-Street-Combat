"""Read-only real-city cooking dependency audit. Never saves native assets."""
import hashlib
import json
import os
import traceback
from collections import deque
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ.get('CS549_PACKAGE_AUDIT_IDENTITY', 'dependencies_v1')
assert IDENTITY.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/Packaging' / (IDENTITY + '.json')
assert not OUT.exists(), 'Preserve occupied evidence'
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
BAD = '/Game/WW2City/Library_Meshingun/Showcase_Meshingun/Overview/Blueprint/BP_Category_Platform'
files = []
current = ('CITY_PACKAGE_DRAFT_INVENTORY_20261002.json'
           if (ROOT / 'Assets/Integration/CITY_PACKAGE_DRAFT_INVENTORY_20261002.json').exists()
           else 'CITY_COMBAT_DRAFT_INVENTORY_20261002.json')
for inventory in ('RELOAD_DRAFT_SNAPSHOT_20261002.json', current):
    files.extend(json.loads((ROOT / 'Assets/Integration' / inventory).read_text(encoding='utf-8-sig'))['files'])
guarded = {ROOT / f['path']: f['sha256'] for f in files}
for path in (STORE / 'Content/WW2City/Maps').rglob('*.umap'):
    guarded[path] = hashlib.sha256(path.read_bytes()).hexdigest()
bad_file = STORE / ('Content' + BAD.removeprefix('/Game') + '.uasset')
guarded[bad_file] = hashlib.sha256(bad_file.read_bytes()).hexdigest()
report = {'identity': IDENTITY, 'engine': unreal.SystemLibrary.get_engine_version(),
          'scope': 'Read-only hard/soft registry closure and editor showcase graph; no cook/runtime pass',
          'entry': ENTRY, 'suspect': BAD, 'errors': []}
try:
    for path, expected in guarded.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, str(path)
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    for mode, soft in (('hard', False), ('hard_and_soft', True)):
        options = unreal.AssetRegistryDependencyOptions(
            include_hard_package_references=True, include_soft_package_references=soft)
        queue, parents = deque([ENTRY]), {ENTRY: None}
        edges = {}
        while queue:
            package = queue.popleft()
            dependencies = sorted(str(x) for x in registry.get_dependencies(package, options))
            edges[package] = dependencies
            for dependency in dependencies:
                if dependency.startswith(('/Game/', '/ACLPlugin/')) and dependency not in parents:
                    parents[dependency] = package
                    queue.append(dependency)
        chain = []
        if BAD in parents:
            node = BAD
            while node is not None:
                chain.append(node)
                node = parents[node]
            chain.reverse()
        report[mode] = {'package_count': len(parents), 'suspect_reachable': BAD in parents,
                        'chain': chain, 'edges': edges,
                        'suspect_direct_referencers': sorted(str(x) for x in registry.get_referencers(BAD, options))}
    bp = unreal.load_asset(BAD)
    assert bp is not None
    report['suspect_class'] = bp.get_class().get_path_name()
    for name in ('parent_class', 'is_editor_only', 'run_construction_script_on_drag'):
        try:
            report[name] = str(bp.get_editor_property(name))
        except Exception as exc:
            report[name] = 'Unavailable: ' + str(exc)
    report['graphs'] = {g.get_name(): [{'name': n.get_name(), 'title': str(unreal.BlueprintEditorLibrary.get_node_title(n)),
                                      'class': n.get_class().get_name()}
                                     for n in unreal.BlueprintGraphEditor.get_graph_editor(g).list_all_nodes()]
                        for g in unreal.BlueprintEditorLibrary.list_graphs(bp)}
    assert unreal.EditorLevelLibrary.load_level(ENTRY)
    report['placed_showcase_actors'] = []
    loaded_actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
    report['loaded_actor_count'] = len(loaded_actors)
    report['roster_labels'] = sorted(a.get_actor_label() for a in loaded_actors if a.get_actor_label().startswith('PC_City_'))
    report['weapon_labels'] = sorted(a.get_actor_label() for a in loaded_actors if a.get_actor_label().startswith('PC_M1_Appearance_'))
    assert len(report['roster_labels']) == 6 and len(report['weapon_labels']) == 3
    for actor in loaded_actors:
        class_path = actor.get_class().get_path_name()
        if 'Showcase_Meshingun' in class_path:
            details = {'path': actor.get_path_name(), 'label': actor.get_actor_label(), 'class': class_path,
                       'level': actor.get_outer().get_outer().get_path_name()}
            for name in ('is_editor_only_actor', 'hidden', 'actor_enable_collision'):
                try:
                    details[name] = str(actor.get_editor_property(name))
                except Exception as exc:
                    details[name] = 'Unavailable: ' + str(exc)
            report['placed_showcase_actors'].append(details)
    report['status'] = 'pass_readonly_dependency_audit'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    report['guarded_files'] = len(guarded)
    report['guarded_bytes_unchanged'] = all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in guarded.items())
    if not report['guarded_bytes_unchanged']:
        report['status'] = 'failed'
        report['errors'].append('Unexpected native byte change')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_PACKAGE_AUDIT ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved package audit report')
