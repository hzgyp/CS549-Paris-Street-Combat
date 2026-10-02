"""Read-only graph wiring audit of the saved real-city shot worker."""
import hashlib
import json
from pathlib import Path
import unreal
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/Setup/shot_graph_audit_v1.json'
assert not OUT.exists()
bp = unreal.load_asset('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2')
g = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'PC_DoShot')
lib, pins = unreal.BlueprintEditorLibrary, unreal.BlueprintGraphPinLibrary
report = []
for n in g.list_all_nodes():
    ps = list(lib.list_all_pins(n))
    context = lib.find_input_pin(n, 'WorldContextObject')
    if pins.is_valid(context):
        ps.append(context)
    report.append({'name': n.get_name(), 'title': str(lib.get_node_title(n)), 'class': n.get_class().get_name(),
        'pins': [{'name': str(pins.get_pin_name(p)), 'value': pins.get_pin_value(p),
            'links': [{'node': pins.get_owning_node(q).get_name(), 'pin': str(pins.get_pin_name(q))}
                      for q in pins.list_connected_pins(p)]} for p in ps]})
OUT.write_text(json.dumps(report, indent=2))
