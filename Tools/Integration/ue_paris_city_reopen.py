"""Bridge-disabled fresh-load check of the new asset-backed city setup, without saving."""
import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/Setup'
IDENTITY = os.environ.get('CS549_CITY_REOPEN_IDENTITY', 'reopen_v2')
assert IDENTITY.replace('_', '').isalnum()
DEST = OUT / (IDENTITY + '.json')
assert not DEST.exists(), 'Preserve occupied fresh-load report'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
PREFIX = '/Game/ParisCombat/Blueprints/CityGameplayV1/'
AUTHOR_IDENTITY = os.environ.get('CS549_CITY_AUTHOR_IDENTITY', 'author_v4')
assert AUTHOR_IDENTITY.replace('_', '').isalnum()
authored = json.loads((OUT / (AUTHOR_IDENTITY + '.json')).read_text(encoding='utf-8'))
assert authored['status'] == 'saved_asset_backed_city_setup_not_gameplay_acceptance'
expected_files = list(authored['saved_files'])
input_evidence = OUT / 'input_v1.json'
if input_evidence.exists():
    controls = json.loads(input_evidence.read_text(encoding='utf-8'))
    assert controls['status'] == 'saved_city_input_bindings_not_device_test'
    assert controls['previous_28_drafts_unchanged'] and controls['other_setup_files_unchanged']
    changed = controls['saved_file']
    assert changed['package'] == PREFIX + 'BP_PCParisPlayerV1'
    expected_files = [changed if f['package'] == changed['package'] else f for f in expected_files]
report = {'scope': 'Read-only native setup reopen; not player input, runtime combat, AI, package or performance acceptance',
          'roster': [], 'weapons': [], 'errors': []}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


try:
    assert unreal.EditorLevelLibrary.load_level(ENTRY)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    levels = list(unreal.EditorLevelUtils.get_levels(world))
    report['levels'] = [l.get_outer().get_path_name() for l in levels]
    expected_names = {'LV_ParisStreetCombat_V1', 'LV_Lighting_Day', 'LV_VFX', 'LV_StructureAsset',
                      'LV_SetDressing', 'LV_Proxy', 'LV_SplineRoads', 'LV_NewsetDressing', 'LV_Powerline'}
    assert {l.get_outer().get_name() for l in levels} == expected_names, 'Retained city level set mismatch'
    report['level_actor_counts'] = {}
    for actor in actors:
        key = actor.get_outer().get_outer().get_path_name()
        report['level_actor_counts'][key] = report['level_actor_counts'].get(key, 0) + 1
    assert not any('Midnight' in p or 'WarFog' in p for p in report['levels'])
    root_level = next(l for l in levels if l.get_outer().get_path_name().startswith(ENTRY + '.'))
    settings = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.WorldSettings)
                    if a.get_outer() == root_level)
    mode_class = unreal.EditorAssetLibrary.load_blueprint_class(PREFIX + 'BP_PCParisGameModeV1')
    assert settings.get_editor_property('default_game_mode') == mode_class
    assert unreal.get_default_object(mode_class).get_editor_property('default_pawn_class') is None
    for actor in actors:
        if actor.get_actor_label().startswith('PC_City_'):
            assert actor.get_outer() == root_level
            mesh = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            report['roster'].append({'label': actor.get_actor_label(), 'class': actor.get_class().get_path_name(),
                                    'mesh': mesh.get_skeletal_mesh_asset().get_path_name(),
                                    'anim_class': mesh.get_editor_property('anim_class').get_path_name(),
                                    'team_id': actor.get_editor_property('TeamId'),
                                    'auto_possess': str(actor.get_editor_property('auto_possess_player'))})
            if actor.get_actor_label() == 'PC_City_Player':
                cameras = actor.get_components_by_class(unreal.CameraComponent)
                assert len(cameras) == 1 and cameras[0].get_editor_property('use_pawn_control_rotation')
                assert actor.get_editor_property('auto_possess_player') == unreal.AutoReceiveInput.PLAYER0
            else:
                assert actor.get_editor_property('auto_possess_player') == unreal.AutoReceiveInput.DISABLED
        elif actor.get_actor_label().startswith('PC_M1_Appearance_'):
            assert actor.get_outer() == root_level
            owner = actor.get_owner()
            assert owner and owner.get_actor_label().startswith('PC_City_')
            root_component = actor.get_editor_property('root_component')
            assert str(root_component.get_attach_socket_name()) == 'hand_r'
            assert root_component.get_attach_parent() == owner.get_component_by_class(unreal.SkeletalMeshComponent)
            report['weapons'].append({'label': actor.get_actor_label(), 'owner': owner.get_actor_label(),
                                      'socket': str(root_component.get_attach_socket_name())})
    assert len(report['roster']) == 6 and len(report['weapons']) == 3
    assert sum(r['team_id'] == 0 for r in report['roster']) == 3
    assert sum(r['team_id'] == 1 for r in report['roster']) == 3
    if input_evidence.exists():
        bp = unreal.load_asset(PREFIX + 'BP_PCParisPlayerV1')
        graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'EventGraph')
        classes = [n.get_class().get_name() for n in graph.list_all_nodes()]
        assert classes.count('K2Node_InputAxisEvent') == 4 and classes.count('K2Node_InputAction') == 1
        report['input_binding_nodes_reopened'] = 5
    report['status'] = 'pass_readonly_city_setup_reopen_not_gameplay_acceptance'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    report['new_setup_bytes_unchanged'] = all(digest(ROOT / f['path']) == f['sha256'] for f in expected_files)
    drafts = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
    report['previous_28_drafts_unchanged'] = all(digest(ROOT / f['path']) == f['sha256'] for f in drafts['files'])
    if not report['new_setup_bytes_unchanged'] or not report['previous_28_drafts_unchanged']:
        report['errors'].append('Unexpected saved byte change')
        report['status'] = 'failed'
    DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_CITY_REOPEN ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved fresh-load report')
