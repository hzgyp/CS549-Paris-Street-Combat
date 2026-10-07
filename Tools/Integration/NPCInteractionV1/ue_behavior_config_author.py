"""Add a public native configuration entry; retain V3 BT/tasks byte-exact."""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match, package_file
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ue_paris_graph_helpers import lib, pin, wire, value, call, pure, get, run

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "behavior_author.json"
VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "packages": [], "errors": [],
          "scope": "new controller/public patrol config and two Pawn derivatives; original V3 BT/tasks unchanged"}
rows = guard_rows()


def put(g, flow, name, datum):
    node = g.add_set_member_variable_node(name)
    value(pin(node, name), datum)
    return run(g, flow, node)


def bbput(g, flow, name, kind, datum):
    field = {"Bool": "BoolValue", "Int": "IntValue", "Name": "NameValue"}[kind]
    return run(g, flow, call(g, "/Script/AIModule.BlackboardComponent.SetValueAs" + kind,
                             self=get(g, "NPCBlackboard"),
                             KeyName=pure(g, "/Script/Engine.KismetSystemLibrary.MakeLiteralName", Value=name), **{field: datum}))


def save(bp, package):
    assert lib.compile_blueprint(bp)
    assert all(not unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors() for g in lib.list_graphs(bp))
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report["packages"].append(package)


try:
    assert guards_match(rows)
    package = DEST + "/BP_PCNPCBehavior" + VERSION
    assert not unreal.EditorAssetLibrary.does_asset_exist(package)
    bp = lib.create_blueprint_asset_with_parent(package, unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCNPCBehaviorV3"))
    g = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, "PC_SetPatrol")
    g.set_function_is_public()
    enabled = g.add_graph_input_parameter("Enabled", lib.get_basic_type_by_name("bool"))
    point = g.add_graph_input_parameter("Point", lib.get_struct_type(unreal.load_object(None, "/Script/CoreUObject.Vector")))
    flow = put(g, g.find_graph_entry_pin(), "PatrolEnabled", enabled)
    flow = put(g, flow, "PatrolPoint", point)
    node = g.add_branch_node()
    wire(flow, lib.find_execute_pin(node))
    value(pin(node, "Condition"), enabled)
    yes, no = pin(node, "then", True), pin(node, "else", True)
    yes = bbput(g, yes, "RetryCount", "Int", 0)
    bbput(g, yes, "WaitingReason", "Name", "PatrolAssigned")
    no = bbput(g, no, "HasMoveGoal", "Bool", False)
    no = run(g, no, call(g, "/Script/Engine.Controller.StopMovement"))
    no = bbput(g, no, "RequestID", "Int", 0)
    bbput(g, no, "WaitingReason", "Name", "GuardAssigned")
    save(bp, package)
    cls = unreal.EditorAssetLibrary.load_blueprint_class(package)
    for name in ("BP_PCAlliedBehavior", "BP_PCGermanBehavior"):
        package = DEST + "/" + name + VERSION
        assert not unreal.EditorAssetLibrary.does_asset_exist(package)
        bp = lib.create_blueprint_asset_with_parent(package, unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + name + "V3"))
        assert lib.compile_blueprint(bp)
        unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(package)).set_editor_property("ai_controller_class", cls)
        save(bp, package)
    report["status"] = "pass_native_behavior_authored_requires_city"
except Exception:
    report["status"] = "failed_behavior_config_author_preserve"
    report["errors"].append(traceback.format_exc())
finally:
    report["files"] = []
    for package in report["packages"]:
        file = package_file(package)
        report["files"].append({"package": package, "path": file.relative_to(ROOT).as_posix(),
                                "size_bytes": file.stat().st_size, "sha256": digest(file)})
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
