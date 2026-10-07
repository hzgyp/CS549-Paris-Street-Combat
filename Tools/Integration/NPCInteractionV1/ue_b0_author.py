"""Author only new B0 BB/BT/controller/derived trial pawns."""
import json
import os
import sys
import traceback
from pathlib import Path

import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match, package_file

IDENTITY = os.environ["CS549_NPC_IDENTITY"]
OUT = STORE / "Evidence/NPCInteractionV1" / IDENTITY
RESULT = OUT / "native_author.json"
PACKAGES = {
    "bb": DEST + "/BB_PC_NPCInteractionV1",
    "bt": DEST + "/BT_PC_NPCInteractionV1",
    "controller": DEST + "/BP_PCNPCControllerV1",
    "allied": DEST + "/BP_PCAlliedNPCInteractionV1",
    "german": DEST + "/BP_PCGermanNPCInteractionV1",
}
rows = guard_rows()
report = {"identity": IDENTITY, "engine": unreal.SystemLibrary.get_engine_version(),
          "scope": "new-only B0 assets; no city/shared-base/player/config save", "packages": [], "errors": []}


def save(asset, package):
    if isinstance(asset, unreal.Blueprint):
        assert unreal.BlueprintEditorLibrary.compile_blueprint(asset), package
        errors = [str(node) for graph in unreal.BlueprintEditorLibrary.list_graphs(asset)
                  for node in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
        assert not errors, (package, errors)
    assert unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False), package
    report["packages"].append(package)


try:
    assert guards_match(rows)
    assert all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in PACKAGES.values()), "Refuse occupied B0 package"
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    bb = tools.create_asset("BB_PC_NPCInteractionV1", DEST, unreal.BlackboardData, unreal.BlackboardDataFactory())
    assert bb
    key_specs = (
        ("TeamId", "Int"), ("Role", "Name"), ("TargetActor", "Object"),
        ("LastSeenPosition", "Vector"), ("LastSeenTime", "Float"),
        ("HasVisibleTarget", "Bool"), ("DesiredPosition", "Vector"),
        ("TaskID", "Int"), ("RequestID", "Int"), ("RestoreGeneration", "Int"),
        ("RetryCount", "Int"), ("WaitingReason", "Name"), ("ReservationID", "Int"),
        ("MoveRequestID", "Int"), ("SearchDeadline", "Float"),
        ("ChaseTravelDistance", "Float"), ("HasMoveGoal", "Bool"),
    )
    entries = []
    for name, kind in key_specs:
        cls = unreal.load_class(None, "/Script/AIModule.BlackboardKeyType_" + kind)
        assert cls, kind
        key = unreal.new_object(cls, outer=bb)
        entry = unreal.BlackboardEntry()
        entry.set_editor_property("entry_name", unreal.Name(name))
        entry.set_editor_property("entry_description", "NPCInteractionV1 private per-controller state")
        entry.set_editor_property("instance_synced", False)
        entry.set_editor_property("key_type", key)
        entries.append(entry)
    bb.set_editor_property("keys", entries)
    save(bb, PACKAGES["bb"])

    bt = tools.create_asset("BT_PC_NPCInteractionV1", DEST, unreal.BehaviorTree, unreal.BehaviorTreeFactory())
    assert bt
    bt.set_editor_property("blackboard_asset", bb)
    root = unreal.new_object(unreal.BTComposite_Selector, outer=bt)
    root.set_editor_property("node_name", "NPCInteractionV1 Root")
    wait = unreal.new_object(unreal.BTTask_Wait, outer=bt)
    wait.set_editor_property("node_name", "Bounded idle wait")
    child = unreal.BTCompositeChild()
    child.set_editor_property("child_task", wait)
    root.set_editor_property("children", [child])
    bt.set_editor_property("root_node", root)
    save(bt, PACKAGES["bt"])

    lib = unreal.BlueprintEditorLibrary
    pins = unreal.BlueprintGraphPinLibrary
    controller = lib.create_blueprint_asset_with_parent(PACKAGES["controller"], unreal.AIController.static_class())
    assert controller
    events = unreal.BlueprintGraphEditor.get_graph_editor_by_name(controller, "EventGraph")
    begin = lib.add_event_override(controller, "ReceiveBeginPlay", unreal.IntPoint(0, 0))
    assert begin
    use = events.add_call_function_node("UseBlackboard")
    run = events.add_call_function_node("RunBehaviorTree")
    assert use and run
    assert pins.set_pin_value(lib.find_input_pin(use, "BlackboardAsset"), bb.get_path_name())
    assert pins.set_pin_value(lib.find_input_pin(run, "BTAsset"), bt.get_path_name())
    assert pins.try_create_connection(lib.find_then_pin(begin), lib.find_execute_pin(use))
    assert pins.try_create_connection(lib.find_then_pin(use), lib.find_execute_pin(run))
    save(controller, PACKAGES["controller"])
    controller_class = unreal.EditorAssetLibrary.load_blueprint_class(PACKAGES["controller"])
    assert controller_class

    parents = {
        "allied": unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisAlliedNPCV1"),
        "german": unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisGermanNPCV1"),
    }
    for label in ("allied", "german"):
        assert parents[label]
        bp = lib.create_blueprint_asset_with_parent(PACKAGES[label], parents[label])
        assert bp
        save(bp, PACKAGES[label])
        cls = unreal.EditorAssetLibrary.load_blueprint_class(PACKAGES[label])
        cdo = unreal.get_default_object(cls)
        cdo.set_editor_property("ai_controller_class", controller_class)
        cdo.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
        save(bp, PACKAGES[label])

    report["blackboard_keys"] = [str(e.get_editor_property("entry_name")) for e in bb.get_editor_property("keys")]
    report["tree"] = {"root": bt.get_editor_property("root_node").get_class().get_name(),
                      "children": len(bt.get_editor_property("root_node").get_editor_property("children")),
                      "child_task": bt.get_editor_property("root_node").get_editor_property("children")[0].get_editor_property("child_task").get_class().get_name()}
    report["status"] = "pass_new_only_b0_authored_requires_fresh_runtime"
except Exception:
    report["status"] = "failed_preserve_new_only_b0_drafts"
    report["errors"].append(traceback.format_exc())
finally:
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["files"] = []
    for package in report["packages"]:
        path = package_file(package)
        if path.is_file():
            report["files"].append({"package": package, "path": path.relative_to(ROOT).as_posix(),
                                    "size_bytes": path.stat().st_size, "sha256": digest(path)})
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.log("CS549_NPC_B0_AUTHOR " + report["status"])
    unreal.SystemLibrary.quit_editor()
