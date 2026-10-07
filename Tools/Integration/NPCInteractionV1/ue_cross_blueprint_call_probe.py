"""Unsaved probe for a cross-Blueprint PC_RecordSight call with declaring class."""
import json
import os
import sys
import traceback
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, STORE, guard_rows, guards_match

IDENTITY = os.environ["CS549_NPC_IDENTITY"]
OUT = STORE / "Evidence/NPCInteractionV1" / IDENTITY
RESULT = OUT / "cross_blueprint_call_probe.json"
PAWN = DEST + "/BP_PCAlliedNPCInteractionV1"
CONTROLLER = DEST + "/BP_PCNPCControllerSightV3"
rows = guard_rows()
report = {
    "identity": IDENTITY,
    "scope": "unsaved cross-Blueprint function-node type/declaring-class probe",
    "errors": [], "assets_saved": [], "map_saved": False,
}

try:
    assert guards_match(rows)
    pawn_bp = unreal.load_asset(PAWN, unreal.Blueprint)
    controller_bp = unreal.load_asset(CONTROLLER, unreal.Blueprint)
    controller_cls = unreal.EditorAssetLibrary.load_blueprint_class(CONTROLLER)
    assert pawn_bp and controller_bp and controller_cls
    controller_graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(controller_bp, "EventGraph")
    pawn_graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(pawn_bp, "EventGraph")
    assert controller_graph and pawn_graph
    available = list(controller_graph.list_available_nodes([]))
    matches = [name for name in available if "pcrecordsight" in name.replace(" ", "").lower()]
    report["controller_available_node_count"] = len(available)
    report["matches"] = matches
    assert matches, "PC_RecordSight node type not discoverable in controller context"
    exact = next((name for name in matches if name.replace(" ", "").lower().endswith("|pcrecordsight")), matches[0])
    node = pawn_graph.create_node_from_name(exact, unreal.Vector2D(0, 0), [], controller_cls)
    assert node, "PC_RecordSight creation with declaring class failed"
    report["selected_type_id"] = exact
    report["node_title"] = node.get_node_title()
    report["pins"] = [str(unreal.BlueprintGraphPinLibrary.get_pin_name(p))
                      for p in unreal.BlueprintEditorLibrary.list_all_pins(node)]
    assert "self" in report["pins"] and "SeenPawn" in report["pins"]
    pawn_graph.remove_nodes([node])
    report["removed_after_probe"] = True
    report["status"] = "pass_cross_blueprint_record_sight_call_tooling"
except Exception:
    report["status"] = "failed_stop_cross_blueprint_call_probe"
    report["errors"].append(traceback.format_exc())
finally:
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
