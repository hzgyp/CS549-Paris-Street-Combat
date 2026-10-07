"""Unsaved UE embedded-Python probe for Blueprint cast-node discovery/retarget."""
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
RESULT = OUT / "ue_python_tool_probe.json"
BP_PATH = DEST + "/BP_PCAlliedNPCInteractionV1"
CONTROLLER_PATH = DEST + "/BP_PCNPCControllerSightV2"
rows = guard_rows()
report = {
    "identity": IDENTITY,
    "scope": "unsaved UE embedded-Python node discovery/create/retarget/remove probe only",
    "python": {
        "version": sys.version,
        "executable": sys.executable,
        "prefix": sys.prefix,
        "path": list(sys.path),
    },
    "editor_toolset_importable_before": False,
    "errors": [],
    "assets_saved": [],
    "map_saved": False,
}

try:
    assert guards_match(rows)
    try:
        import editor_toolset  # noqa: F401
        report["editor_toolset_importable_before"] = True
    except Exception as exc:
        report["editor_toolset_import_error"] = repr(exc)

    bp = unreal.load_asset(BP_PATH, unreal.Blueprint)
    controller_cls = unreal.EditorAssetLibrary.load_blueprint_class(CONTROLLER_PATH)
    assert bp and controller_cls
    graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "EventGraph")
    assert graph
    available = list(graph.list_available_nodes([]))
    matches = [name for name in available if "casttoactor" in name.replace(" ", "").lower()]
    report["available_node_count"] = len(available)
    report["cast_to_actor_matches"] = matches
    assert matches, "No CastToActor node type in EventGraph context"

    node = graph.create_node_from_name(matches[0], unreal.Vector2D(0, 0), [])
    assert node, "CastToActor creation with empty context failed"
    report["created_node_title"] = node.get_node_title()
    report["retargeted"] = bool(graph.retarget_node_class(
        node, unreal.Actor.static_class(), controller_cls))
    assert report["retargeted"], "Cast node retarget failed"
    report["retargeted_node_title"] = node.get_node_title()
    report["retargeted_pins"] = [str(unreal.BlueprintGraphPinLibrary.get_pin_name(p))
                                  for p in unreal.BlueprintEditorLibrary.list_all_pins(node)]
    graph.remove_nodes([node])
    report["removed_after_probe"] = True
    report["status"] = "pass_embedded_python_blueprint_cast_tooling"
except Exception:
    report["status"] = "failed_stop_embedded_python_tool_probe"
    report["errors"].append(traceback.format_exc())
finally:
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
