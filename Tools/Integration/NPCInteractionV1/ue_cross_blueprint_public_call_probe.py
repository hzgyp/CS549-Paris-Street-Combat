"""Unsaved proof that public PC_RecordSight can be called from a Pawn graph."""
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
RESULT = OUT / "cross_blueprint_public_call_probe.json"
PAWN = DEST + "/BP_PCAlliedNPCInteractionV1"
CONTROLLER = DEST + "/BP_PCNPCControllerSightV3"
rows = guard_rows()
report = {"identity": IDENTITY, "scope": "unsaved public cross-Blueprint call probe",
          "errors": [], "assets_saved": [], "map_saved": False}

try:
    assert guards_match(rows)
    pawn_bp = unreal.load_asset(PAWN, unreal.Blueprint)
    controller_bp = unreal.load_asset(CONTROLLER, unreal.Blueprint)
    assert pawn_bp and controller_bp
    function_graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(controller_bp, "PC_RecordSight")
    pawn_graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(pawn_bp, "EventGraph")
    assert function_graph and pawn_graph
    function_graph.set_function_is_public()
    assert unreal.BlueprintEditorLibrary.compile_blueprint(controller_bp)
    controller_cls = unreal.EditorAssetLibrary.load_blueprint_class(CONTROLLER)
    assert controller_cls
    matches = [name for name in pawn_graph.list_available_nodes([])
               if "pcrecordsight" in name.replace(" ", "").lower()]
    report["pawn_matches_after_public_compile"] = matches
    assert matches
    node = pawn_graph.create_node_from_name(matches[0], unreal.Vector2D(0, 0), [], controller_cls)
    assert node, "Public PC_RecordSight call creation failed"
    report["selected_type_id"] = matches[0]
    report["pins"] = [str(unreal.BlueprintGraphPinLibrary.get_pin_name(p))
                      for p in unreal.BlueprintEditorLibrary.list_all_pins(node)]
    assert "self" in report["pins"] and "SeenPawn" in report["pins"]
    pawn_graph.remove_nodes([node])
    report["removed_after_probe"] = True
    report["status"] = "pass_public_cross_blueprint_record_sight_call"
except Exception:
    report["status"] = "failed_stop_public_cross_blueprint_call_probe"
    report["errors"].append(traceback.format_exc())
finally:
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
