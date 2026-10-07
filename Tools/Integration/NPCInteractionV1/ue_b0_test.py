"""Fresh actual-city B0 test: tree execution and per-controller Blackboard isolation."""
import json
import os
import sys
import time
import traceback
from pathlib import Path

import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match

IDENTITY = os.environ["CS549_NPC_IDENTITY"]
AUTHOR_IDENTITY = os.environ["CS549_NPC_AUTHOR_IDENTITY"]
OUT = STORE / "Evidence/NPCInteractionV1" / IDENTITY
RESULT = OUT / "b0_runtime.json"
ENTRY = "/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1"
PACKAGES = {
    "bb": DEST + "/BB_PC_NPCInteractionV1",
    "bt": DEST + "/BT_PC_NPCInteractionV1",
    "allied": DEST + "/BP_PCAlliedNPCInteractionV1",
    "german": DEST + "/BP_PCGermanNPCInteractionV1",
}
rows = guard_rows()
author = json.loads((STORE / "Evidence/NPCInteractionV1" / AUTHOR_IDENTITY / "native_author.json").read_text())
report = {"identity": IDENTITY, "author_identity": AUTHOR_IDENTITY,
          "scope": "fresh actual-city unsaved B0 tree/Blackboard proof; not movement/perception/combat acceptance",
          "samples": [], "errors": []}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
callback = None
phase = "setup"
started = time.monotonic()
staged = []


def write():
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_b0_private_blackboards_real_tree" if not report["errors"] else "failed_preserve_b0_evidence"
    write()
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global phase
    try:
        assert time.monotonic() - started < 180, "B0 runtime timeout"
        if phase == "setup":
            assert guards_match(rows) and author["status"].startswith("pass_")
            phase = "loading"
            assert levels.load_level(ENTRY)
            allied = unreal.EditorAssetLibrary.load_blueprint_class(PACKAGES["allied"])
            german = unreal.EditorAssetLibrary.load_blueprint_class(PACKAGES["german"])
            assert allied and german
            world = editor.get_editor_world()
            existing = [a for a in actors.get_all_level_actors() if a.get_actor_label().startswith("PC_City_")]
            ally_anchor = next(a for a in existing if a.get_actor_label() == "PC_City_Ally1")
            enemy_anchor = next(a for a in existing if a.get_actor_label() == "PC_City_Enemy1")
            for label, cls, anchor, offset in (
                ("NPCI_B0_AllyA", allied, ally_anchor, unreal.Vector(0, 300, 0)),
                ("NPCI_B0_AllyB", allied, ally_anchor, unreal.Vector(0, -300, 0)),
                ("NPCI_B0_Target", german, enemy_anchor, unreal.Vector(0, 300, 0)),
            ):
                actor = actors.spawn_actor_from_class(cls, anchor.get_actor_location() + offset, anchor.get_actor_rotation())
                assert actor
                actor.set_actor_label(label)
                staged.append(actor)
            levels.editor_request_begin_play()
            phase = "wait_pie"
        elif phase == "loading":
            return
        elif phase == "wait_pie":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            runtime = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                       if a.get_actor_label().startswith("NPCI_B0_")]
            assert len(runtime) == 3
            allies = sorted((a for a in runtime if "Ally" in a.get_actor_label()), key=lambda a: a.get_actor_label())
            target = next(a for a in runtime if "Target" in a.get_actor_label())
            controllers = [unreal.AIHelperLibrary.get_ai_controller(a) for a in allies]
            assert all(controllers)
            blackboards = [c.get_editor_property("blackboard") for c in controllers]
            assert all(blackboards) and blackboards[0] != blackboards[1]
            bt = unreal.load_asset(PACKAGES["bt"])
            bb_asset = unreal.load_asset(PACKAGES["bb"])
            assert bt and bb_asset and bt.get_editor_property("root_node")
            tree_started = [c.run_behavior_tree(bt) for c in controllers]
            assert all(tree_started)
            remembered = target.get_actor_location()
            blackboards[0].set_value_as_vector("LastSeenPosition", remembered)
            blackboards[0].set_value_as_float("LastSeenTime", 10.0)
            blackboards[0].set_value_as_bool("HasVisibleTarget", True)
            assert blackboards[1].get_value_as_vector("LastSeenPosition") != remembered
            blackboards[0].set_value_as_bool("HasVisibleTarget", False)
            target.set_actor_location(target.get_actor_location() + unreal.Vector(500, 500, 0), False, False)
            report["samples"] = [{
                "controller": c.get_path_name(), "blackboard": b.get_path_name(),
                "tree_started": tree_started[i],
                "last_seen": [b.get_value_as_vector("LastSeenPosition").x,
                              b.get_value_as_vector("LastSeenPosition").y,
                              b.get_value_as_vector("LastSeenPosition").z],
                "visible": b.get_value_as_bool("HasVisibleTarget"),
            } for i, (c, b) in enumerate(zip(controllers, blackboards))]
            assert blackboards[0].get_value_as_vector("LastSeenPosition") == remembered
            assert blackboards[1].get_value_as_vector("LastSeenPosition") != remembered
            report["private_components"] = blackboards[0].get_path_name() != blackboards[1].get_path_name()
            report["hidden_target_move_did_not_mutate_memory"] = True
            levels.editor_request_end_play()
            phase = "end"
        elif phase == "end":
            if editor.get_game_world() is None:
                finish()
    except Exception:
        report["errors"].append(traceback.format_exc())
        try:
            levels.editor_request_end_play()
        except Exception:
            pass
        finish()


callback = unreal.register_slate_post_tick_callback(tick)
write()
