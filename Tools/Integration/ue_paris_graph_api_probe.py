"""Read installed Blueprint/input authoring interfaces without editing native assets."""
import json
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002'
DEST = OUT / 'graph_api_v1.json'
assert not DEST.exists(), 'Preserve occupied API evidence'
report = {'scope': 'Read-only API inspection; no graph/native asset writes', 'classes': {}, 'docs': {}}
for name in ('BlueprintGraphEditor', 'BlueprintGraphPinLibrary', 'BlueprintEditorLibrary',
             'InputAction', 'InputMappingContext', 'InputActionFactory', 'InputMappingContextFactory',
             'EnhancedInputLocalPlayerSubsystem', 'EnhancedInputLibrary', 'SubsystemBlueprintLibrary',
             'InputModifierNegate', 'InputModifierSwizzleAxis', 'EditorLevelUtils'):
    cls = getattr(unreal, name, None)
    report['classes'][name] = [n for n in dir(cls) if not n.startswith('_')] if cls else None
    for method in ('get_graph_editor_by_name', 'create_node_from_name', 'list_available_nodes',
                   'add_call_function_node', 'add_custom_event_node', 'add_get_member_variable_node',
                   'map_key', 'add_mapping_context', 'get_local_player_subsystem_from_player_controller',
                   'get_input_action_value', 'conv_input_action_value_to_axis2d',
                   'make_level_current', 'remove_level_from_world'):
        obj = getattr(cls, method, None)
        if obj:
            report['docs'][name + '.' + method] = obj.__doc__
bp = unreal.load_asset('/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/BP_PCPlayerReloadV1')
assert bp
graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'EventGraph')
assert graph
available = graph.list_available_nodes([])
report['node_count'] = len(available)
report['input_and_parent_actions'] = [n for n in available if any(t.lower() in n.lower()
    for t in ('Enhanced Input', 'InputAction', 'Mapping Context', 'PC_Request', 'Mouse X', 'Mouse Y'))]
report['status'] = 'read_only_api_inspection_complete'
DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_CITY_GRAPH_API_COMPLETE')
