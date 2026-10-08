"""Authorized ONE formal map save after a passed native-bootstrap early gate."""
import json
import os
import shutil
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, STORE, digest, guard_rows, guards_match, package_file
from ue_formal_roster import MAP, LABELS, prop, actor_state, replace_roster

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "formal_combat_author.json"
rows = guard_rows()
map_file = package_file(MAP)
aliases = {map_file.relative_to(ROOT).as_posix(), "Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap"}
map_rows = [r for r in rows if r["path"] in aliases]
other_rows = [r for r in rows if r["path"] not in aliases]
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "map_saved": False,
    "authorization": "2026-10-07 user explicitly permits formal map NPC AI integration and play regression",
    "scope": "five compatible NPC replacements, original gear rewiring, one coordinator/FF OFF; ONE map mutation",
    "original_map_rows": map_rows, "new_map_rows": [], "protected_count": len(rows)}
backup = OUT / "formal_map_before.umap"


try:
    assert guards_match(rows) and len(map_rows) == 2
    assert os.path.samefile(ROOT / map_rows[0]["path"], ROOT / map_rows[1]["path"])
    early_path = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_EARLY_IDENTITY"] / "formal_combat_runtime.json"
    early = json.loads(early_path.read_text())
    assert early["status"] == "pass_formal_native_startup_and_finite_play" and early["protected_guards_unchanged"]
    assert early["protected_count"] == len(rows) and early["python_ai_configuration_calls"] == early["python_combat_requests"] == 0
    assert json.loads((early_path.parent / "result.json").read_text())["protected_hashes"] == rows, "Early test must protect this exact epoch"
    assert all(early["checks"].values()) and len(early["checks"]) == 3
    report["early_proof"] = {"path": early_path.relative_to(ROOT).as_posix(), "sha256": digest(early_path)}
    assert not backup.exists()
    shutil.copy2(map_file, backup)
    assert digest(backup) == map_rows[0]["sha256"]
    report["recovery"] = {"path": backup.relative_to(ROOT).as_posix(), "size_bytes": backup.stat().st_size, "sha256": digest(backup)}
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level(MAP)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_before = actors.get_all_level_actors()
    lookup = {a.get_actor_label(): a for a in all_before}
    replaceable = {lookup[label].get_path_name() for label in LABELS}
    rewired_guns = {prop(lookup[label], "WeaponAppearance").get_path_name() for label in LABELS if prop(lookup[label], "WeaponAppearance")}
    stable = {a.get_path_name(): actor_state(a) for a in all_before if a.get_path_name() not in replaceable | rewired_guns}
    report["replacement"] = replace_roster(os.environ["CS549_NPC_BEHAVIOR_VERSION"])
    after = {a.get_path_name(): actor_state(a) for a in actors.get_all_level_actors()}
    assert all(after.get(path) == state for path, state in stable.items()), "Non-NPC actor state changed"
    report["unchanged_actor_count"] = len(stable)
    assert guards_match(rows), "Stop before save if another protected file changed"
    assert levels.save_current_level()
    report["map_saved"] = True
    for r in map_rows:
        f = ROOT / r["path"]
        report["new_map_rows"].append({"path": r["path"], "size_bytes": f.stat().st_size, "sha256": digest(f)})
    assert len({r["sha256"] for r in report["new_map_rows"]}) == 1
    assert report["new_map_rows"][0]["sha256"] != map_rows[0]["sha256"]
    assert guards_match(other_rows)
    report["authorized_map_mutation_verified"] = True
    report["status"] = "pass_formal_combat_map_saved_fresh_runtime_unpassed"
except Exception:
    report["status"] = "failed_formal_combat_author_preserve"
    report["errors"].append(traceback.format_exc())
    if report["map_saved"] and backup.exists() and guards_match(other_rows):
        shutil.copy2(map_file, OUT / "failed_formal_map_after.umap")
        shutil.copy2(backup, map_file)
        report["owned_map_restored_exact"] = guards_match(map_rows)
finally:
    report["protected_guards_unchanged_except_authorized_map"] = guards_match(other_rows)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
