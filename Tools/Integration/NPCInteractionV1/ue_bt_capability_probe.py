"""Transient UE5.8 Behavior Tree/Blackboard authoring proof. Saves no package."""
import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1"
IDENTITY = os.environ["CS549_NPC_IDENTITY"]
OUT = STORE / "Evidence/NPCInteractionV1" / IDENTITY
RESULT = OUT / "native_capability.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


snapshot = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadIndexContactV6/map_recovery_v1/result.json"
guards = json.loads(snapshot.read_text())["files"]
known = {row["path"] for row in guards}
lane_b = json.loads((ROOT / "Docs/Development/NPCInteractionV1/NPC_INTERACTION_V1_DRAFT_INVENTORY_20261004.json").read_text())["files"]
guards += [row for row in lane_b if row["path"] not in known]
assert len(guards) == 558
report = {
    "identity": IDENTITY,
    "engine": unreal.SystemLibrary.get_engine_version(),
    "scope": "transient Blackboard/Behavior Tree construction proof; no package save or city load",
    "protected_count": len(guards),
    "classes": {},
    "attempts": [],
    "errors": [],
}


def attempt(label, fn):
    try:
        value = fn()
        report["attempts"].append({"label": label, "ok": True, "value": str(value)})
        return value
    except Exception as exc:
        report["attempts"].append({"label": label, "ok": False, "error": repr(exc)})
        raise


try:
    assert len(guards) == 514
    for row in guards:
        path = ROOT / row["path"]
        assert path.is_file() and path.stat().st_size == row["size_bytes"] and digest(path) == row["sha256"], row["path"]
    names = (
        "BehaviorTree", "BlackboardData", "BlackboardEntry",
        "BTComposite_Selector", "BTComposite_Sequence",
        "BTCompositeChild", "BTTask_Wait", "BTTask_MoveTo",
    )
    for name in names:
        obj = getattr(unreal, name, None)
        report["classes"][name] = {"available": obj is not None, "doc": str(getattr(obj, "__doc__", ""))[:1200] if obj else None}
    assert all(report["classes"][n]["available"] for n in names)
    vector_key_class = unreal.load_class(None, "/Script/AIModule.BlackboardKeyType_Vector")
    object_key_class = unreal.load_class(None, "/Script/AIModule.BlackboardKeyType_Object")
    report["classes"]["BlackboardKeyType_Vector"] = {"available": vector_key_class is not None, "source": "/Script/AIModule.BlackboardKeyType_Vector"}
    report["classes"]["BlackboardKeyType_Object"] = {"available": object_key_class is not None, "source": "/Script/AIModule.BlackboardKeyType_Object"}
    assert vector_key_class and object_key_class

    bb = attempt("new transient BlackboardData", lambda: unreal.new_object(unreal.BlackboardData))
    vector_type = attempt("new vector key type", lambda: unreal.new_object(vector_key_class, outer=bb))
    entry = unreal.BlackboardEntry()
    attempt("set Blackboard entry name", lambda: entry.set_editor_property("entry_name", unreal.Name("LastSeenPosition")))
    attempt("set Blackboard entry key type", lambda: entry.set_editor_property("key_type", vector_type))
    attempt("set Blackboard keys", lambda: bb.set_editor_property("keys", [entry]))

    tree = attempt("new transient BehaviorTree", lambda: unreal.new_object(unreal.BehaviorTree))
    attempt("bind Blackboard asset", lambda: tree.set_editor_property("blackboard_asset", bb))
    root = attempt("new Selector root", lambda: unreal.new_object(unreal.BTComposite_Selector, outer=tree))
    wait = attempt("new executable Wait task", lambda: unreal.new_object(unreal.BTTask_Wait, outer=tree))
    child = unreal.BTCompositeChild()
    attempt("set child task", lambda: child.set_editor_property("child_task", wait))
    attempt("set root children", lambda: root.set_editor_property("children", [child]))
    attempt("set tree root node", lambda: tree.set_editor_property("root_node", root))

    keys = bb.get_editor_property("keys")
    children = root.get_editor_property("children")
    report["proof"] = {
        "blackboard_key_count": len(keys),
        "blackboard_key": str(keys[0].get_editor_property("entry_name")),
        "tree_blackboard_same": tree.get_editor_property("blackboard_asset") == bb,
        "root_class": root.get_class().get_name(),
        "child_count": len(children),
        "child_task_class": children[0].get_editor_property("child_task").get_class().get_name(),
    }
    assert report["proof"] == {
        "blackboard_key_count": 1,
        "blackboard_key": "LastSeenPosition",
        "tree_blackboard_same": True,
        "root_class": "BTComposite_Selector",
        "child_count": 1,
        "child_task_class": "BTTask_Wait",
    }
    report["status"] = "pass_transient_real_bt_structure_authoring_capability"
except Exception:
    report["status"] = "failed_stop_before_native_asset_authoring"
    report["errors"].append(traceback.format_exc())
finally:
    report["protected_guards_unchanged"] = all(
        (ROOT / row["path"]).is_file()
        and (ROOT / row["path"]).stat().st_size == row["size_bytes"]
        and digest(ROOT / row["path"]) == row["sha256"] for row in guards
    )
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.log("CS549_NPC_CAPABILITY " + report["status"])
    unreal.SystemLibrary.quit_editor()
