"""Inspect installed shot/UMG graph APIs read-only; no native saves."""
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/Setup/combat_api_v1.json'
assert not OUT.exists(), 'Preserve occupied API probe'
report = {'scope': 'Read-only installed combat/UMG authoring API inspection', 'docs': {}, 'classes': {}}
for name in ('BlueprintGraphEditor', 'BlueprintEditorLibrary', 'BlueprintGraphPinLibrary',
             'WidgetBlueprintFactory', 'WidgetBlueprint', 'WidgetTree', 'CanvasPanel', 'CanvasPanelSlot',
             'TextBlock', 'UserWidget', 'Object'):
    cls = getattr(unreal, name, None)
    report['classes'][name] = [m for m in dir(cls) if not m.startswith('_')] if cls else None
    for method in ('add_member_variable', 'add_graph_input_parameter', 'add_graph_output_parameter',
                   'find_graph_entry_pin', 'add_branch_node', 'add_return_node', 'add_get_member_variable_node',
                   'add_set_member_variable_node', 'get_basic_type_by_name', 'get_object_reference_type',
                   'get_struct_type', 'get_array_type', 'get_pin_name', 'get_pin_type', 'set_pin_value',
                   'get_pin_value', 'list_all_pins', 'add_child_to_canvas', 'set_anchors', 'set_offsets',
                   'set_alignment', 'set_auto_size', 'set_position', 'set_size', 'set_text', 'new_object'):
        member = getattr(cls, method, None)
        if member:
            report['docs'][name + '.' + method] = member.__doc__
bp = unreal.load_asset('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1')
assert bp
graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'EventGraph')
available = graph.list_available_nodes([])
report['candidate_nodes'] = [n for n in available if any(k in n for k in
    ('CombatantReload', 'MakeArray', 'BreakHitResult', 'BeginPlay', 'CreateWidget', 'Create Widget',
     'GetOwningPlayerPawn', 'EventTick', 'LineTraceByChannel', 'SphereTraceByChannel'))]
report['status'] = 'read_only_complete'
OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
