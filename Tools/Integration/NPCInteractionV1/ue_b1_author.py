"""Author a new-only B1 native MoveTo Behavior Tree; never edits B0 assets."""
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
RESULT = OUT / "b1_author.json"
PACKAGE = DEST + "/BT_PC_NPCMoveV1"
rows = guard_rows()
report = {"identity": IDENTITY, "scope": "new-only B1 built-in MoveTo tree; no B0/city/shared save",
          "packages": [], "errors": []}

try:
    assert guards_match(rows)
    assert not unreal.EditorAssetLibrary.does_asset_exist(PACKAGE), "Refuse occupied B1 package"
    bb = unreal.load_asset(DEST + "/BB_PC_NPCInteractionV1")
    assert bb
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    bt = tools.create_asset("BT_PC_NPCMoveV1", DEST, unreal.BehaviorTree, unreal.BehaviorTreeFactory())
    assert bt
    bt.set_editor_property("blackboard_asset", bb)
    root = unreal.new_object(unreal.BTComposite_Sequence, outer=bt)
    root.set_editor_property("node_name", "B1 native move then bounded wait")
    move = unreal.new_object(unreal.BTTask_MoveTo, outer=bt)
    move.set_editor_property("node_name", "Move to private DesiredPosition")
    selector = unreal.BlackboardKeySelector()
    selector.set_editor_property("selected_key_name", unreal.Name("DesiredPosition"))
    selector.set_editor_property("selected_key_type", unreal.load_class(None, "/Script/AIModule.BlackboardKeyType_Vector"))
    move.set_editor_property("blackboard_key", selector)
    wait = unreal.new_object(unreal.BTTask_Wait, outer=bt)
    wait.set_editor_property("node_name", "B1 arrival hold")
    children = []
    for task in (move, wait):
        child = unreal.BTCompositeChild()
        child.set_editor_property("child_task", task)
        children.append(child)
    root.set_editor_property("children", children)
    bt.set_editor_property("root_node", root)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bt, only_if_is_dirty=False)
    report["packages"].append(PACKAGE)
    path = package_file(PACKAGE)
    report["files"] = [{"package": PACKAGE, "path": path.relative_to(ROOT).as_posix(),
                        "size_bytes": path.stat().st_size, "sha256": digest(path)}]
    report["tree"] = {"root": root.get_class().get_name(), "tasks": [move.get_class().get_name(), wait.get_class().get_name()],
                      "selected_key": str(move.get_editor_property("blackboard_key").get_editor_property("selected_key_name"))}
    report["status"] = "pass_b1_native_move_tree_authored_requires_runtime"
except Exception:
    report["status"] = "failed_preserve_b1_evidence"
    report["errors"].append(traceback.format_exc())
finally:
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
