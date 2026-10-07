"""Explicitly authorized minimal shared friendly-hit continuation patch."""
import json
import os
import shutil
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match, package_file
from ue_graph import lib, pins, pin, wire, value, pure, get, run, math, branch, put, function, cast, call

BASE = "/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2"
POLICY = DEST + "/BP_PCFriendlyFirePolicyV1"
OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "friendly_fire_author.json"
rows = guard_rows()
base_file = package_file(BASE)
allowed = {r["path"] for r in rows if Path(r["path"]).name == base_file.name}
assert len(allowed) == 2, "Resolve exactly the two known aliases of the one shared file"
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "files": [], "map_saved": False,
          "authorization": "2026-10-05 user: allow this window to integrate shared change and test",
          "scope": "one world FF policy and minimal shared friendly terminal only", "protected_count": len(rows)}
settings = None
original_promotion = None


def write():
    RESULT.write_text(json.dumps(report, indent=2) + "\n")


def record(package):
    p = package_file(package)
    return {"package": package, "path": p.relative_to(ROOT).as_posix(), "size_bytes": p.stat().st_size, "sha256": digest(p)}


try:
    assert guards_match(rows) and not unreal.EditorAssetLibrary.does_asset_exist(POLICY)
    report["old_shared_rows"] = [r for r in rows if r["path"] in allowed]
    shutil.copy2(base_file, OUT / "shared_base_before.uasset")
    assert digest(OUT / "shared_base_before.uasset") == digest(base_file)
    report["backup_sha256"] = digest(base_file)
    write()
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/BlueprintGraph.BlueprintEditorSettings"))
    original_promotion = settings.get_editor_property("bEnableTypePromotion")
    settings.set_editor_property("bEnableTypePromotion", False)
    assert settings.get_editor_property("bEnableTypePromotion") is False
    policy = lib.create_blueprint_asset_with_parent(POLICY, unreal.Actor.static_class())
    ev = unreal.BlueprintGraphEditor.get_graph_editor_by_name(policy, "EventGraph")
    assert ev.add_member_variable("FriendlyFireEnabled", lib.get_basic_type_by_name("bool"), "false")
    g, flow, args = function(policy, "PC_SetFriendlyFire", (("Enabled", "bool"),))
    put(g, flow, "FriendlyFireEnabled", args[0])
    assert lib.compile_blueprint(policy)
    assert all(not unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors() for g in lib.list_graphs(policy))
    policy_cls = unreal.EditorAssetLibrary.load_blueprint_class(POLICY)
    bp = unreal.load_asset(BASE)
    graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "PC_DoShot")
    nodes = list(graph.list_all_nodes())
    setters = [n for n in nodes if pins.is_valid(lib.find_input_pin(n, "ShotOutcome"))
               and pins.get_pin_value(lib.find_input_pin(n, "ShotOutcome")) == "Friendly blocked"]
    assert len(setters) == 1, "Ambiguous original friendly terminal"
    terminal = setters[0]
    assert len(pins.list_connected_pins(lib.find_execute_pin(terminal))) == 1
    tail = lib.find_then_pin(terminal)
    assert not pins.list_connected_pins(tail), "Do not overwrite an existing friendly continuation"
    damage_nodes = [n for n in nodes if "applydamage" in n.get_node_title().replace(" ", "").lower()]
    assert len(damage_nodes) == 1, "Expected one untouched hostile damage call"
    target_pins = list(pins.list_connected_pins(lib.find_self_pin(damage_nodes[0])))
    assert len(target_pins) == 1
    target = target_pins[0]
    report["original_node_count"] = len(nodes)
    report["original_hostile_damage_node"] = damage_nodes[0].get_name()
    query = call(graph, "/Script/Engine.GameplayStatics.GetActorOfClass", ActorClass=policy_cls.get_path_name())
    flow, typed = cast(graph, run(graph, tail, query), pin(query, "ReturnValue", True), policy_cls)
    enabled, _ = branch(graph, flow, get(graph, "FriendlyFireEnabled", policy_cls.get_path_name(), typed))
    parent_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/BP_PCCombatantReloadV1")
    living, _ = branch(graph, enabled, math(graph, "Greater_DoubleDouble", A=get(graph, "Health", parent_cls.get_path_name(), target), B=0))
    damage = call(graph, "PC_ApplyDamage", Amount=35)
    wire(target, lib.find_self_pin(damage))
    living = run(graph, living, damage)
    put(graph, living, "ShotOutcome", "Friendly hit")
    assert lib.compile_blueprint(bp)
    assert all(not unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors() for g in lib.list_graphs(bp))
    assert all(n in graph.list_all_nodes() for n in nodes), "Do not remove old graph nodes"
    report["new_node_count"] = len(graph.list_all_nodes())
    # Save only these two assets. No parent/child/map Save All.
    assert guards_match(rows)
    assert unreal.EditorAssetLibrary.save_loaded_asset(policy, only_if_is_dirty=False)
    report["files"].append(record(POLICY))
    write()
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report["new_shared_rows"] = [{**r, "size_bytes": (ROOT / r["path"]).stat().st_size, "sha256": digest(ROOT / r["path"])} for r in rows if r["path"] in allowed]
    assert len({r["sha256"] for r in report["new_shared_rows"]}) == 1
    assert all(r["sha256"] != report["backup_sha256"] for r in report["new_shared_rows"])
    report["authorized_shared_mutations_verified"] = True
    report["status"] = "pass_authorized_shared_ff_patch_requires_regression"
except Exception:
    report["status"] = "failed_shared_ff_author_preserve"
    report["errors"].append(traceback.format_exc())
finally:
    if settings is not None and original_promotion is not None:
        settings.set_editor_property("bEnableTypePromotion", original_promotion)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["protected_guards_unchanged_except_authorized_mutations"] = guards_match([r for r in rows if r["path"] not in allowed])
    write()
    unreal.SystemLibrary.quit_editor()
