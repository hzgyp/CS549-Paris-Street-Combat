"""Repair only the authored FF world query's missing native exec edge."""
import json
import os
import shutil
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, STORE, digest, guard_rows, guards_match, package_file
from ue_graph import lib, pins, pin, wire, run

BASE = "/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2"
OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "friendly_fire_author.json"
rows = guard_rows()
allowed = {r["path"] for r in rows if Path(r["path"]).name == "BP_PCParisCombatantV2.uasset"}
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "files": [], "errors": [], "protected_count": len(rows),
          "scope": "existing authorized FF query exec-edge repair; no other old node edits", "map_saved": False}
try:
    assert len(allowed) == 2 and guards_match(rows)
    report["old_shared_rows"] = [r for r in rows if r["path"] in allowed]
    shutil.copy2(package_file(BASE), OUT / "shared_base_before.uasset")
    report["backup_sha256"] = digest(OUT / "shared_base_before.uasset")
    bp = unreal.load_asset(BASE)
    g = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "PC_DoShot")
    queries = [n for n in g.list_all_nodes() if pins.is_valid(lib.find_input_pin(n, "ActorClass"))
               and "BP_PCFriendlyFirePolicyV1" in pins.get_pin_value(lib.find_input_pin(n, "ActorClass"))]
    assert len(queries) == 1
    query = queries[0]
    assert not pins.list_connected_pins(lib.find_execute_pin(query))
    consumers = list(pins.list_connected_pins(pin(query, "ReturnValue", True)))
    assert len(consumers) == 1
    cast_node = consumers[0].get_owning_node()
    cast_exec = lib.find_execute_pin(cast_node)
    upstream = list(pins.list_connected_pins(cast_exec))
    assert len(upstream) == 1
    report["before_exec_chain"] = [upstream[0].get_owning_node().get_name(), cast_node.get_name()]
    pins.break_pin_links(cast_exec)
    wire(run(g, upstream[0], query), cast_exec)
    assert lib.compile_blueprint(bp)
    assert all(not unreal.BlueprintGraphEditor.get_graph_editor(gr).list_nodes_with_errors() for gr in lib.list_graphs(bp))
    assert guards_match(rows)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report["new_shared_rows"] = [{**r, "size_bytes": (ROOT / r["path"]).stat().st_size, "sha256": digest(ROOT / r["path"])} for r in rows if r["path"] in allowed]
    report["authorized_shared_mutations_verified"] = len({r["sha256"] for r in report["new_shared_rows"]}) == 1
    report["status"] = "pass_authorized_ff_exec_edge_requires_regression"
except Exception:
    report["status"] = "failed_ff_exec_repair_preserve"
    report["errors"].append(traceback.format_exc())
finally:
    report["protected_guards_unchanged"] = guards_match(rows)
    report["protected_guards_unchanged_except_authorized_mutations"] = guards_match([r for r in rows if r["path"] not in allowed])
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
