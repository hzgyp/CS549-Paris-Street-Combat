"""Fresh actual-city native PawnSensing faction/loss/private-memory test."""
import json
import os
import sys
import time
import traceback
from math import dist, sqrt
from pathlib import Path

import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, STORE, guard_rows, guards_match

IDENTITY = os.environ["CS549_NPC_IDENTITY"]
AUTHOR_IDENTITY = os.environ["CS549_NPC_AUTHOR_IDENTITY"]
OUT = STORE / "Evidence/NPCInteractionV1" / IDENTITY
RESULT = OUT / "b1_sight_runtime.json"
ENTRY = "/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1"
ALLY = DEST + "/BP_PCAlliedNPCSightV1"
GERMAN = DEST + "/BP_PCGermanNPCSightV1"
rows = guard_rows()
author = json.loads((STORE / "Evidence/NPCInteractionV1" / AUTHOR_IDENTITY / "b1_sight_author.json").read_text())
report = {"identity": IDENTITY, "author_identity": AUTHOR_IDENTITY,
          "scope": "fresh unsaved actual-city native sight/faction/loss/private-memory proof", "samples": [], "errors": []}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
callback = None
phase = "setup"
started = time.monotonic()
runtime_start = loss_start = None
observer = friend = enemy = controller = blackboard = None
remembered = None


def xyz(v):
    return (v.x, v.y, v.z)


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_b1_native_faction_sight_loss_memory" if not report["errors"] else "failed_preserve_b1_sight_evidence"
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global phase, runtime_start, loss_start, observer, friend, enemy, controller, blackboard, remembered
    try:
        elapsed = time.monotonic() - started
        assert elapsed < 180, "B1 sight runtime timeout"
        if phase == "setup":
            assert guards_match(rows) and author["status"].startswith("pass_")
            phase = "loading"
            assert levels.load_level(ENTRY)
            ally_cls = unreal.EditorAssetLibrary.load_blueprint_class(ALLY)
            german_cls = unreal.EditorAssetLibrary.load_blueprint_class(GERMAN)
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            start = anchors["PC_City_Ally1"].get_actor_location()
            end = anchors["PC_City_Ally2"].get_actor_location()
            delta = end - start
            length = sqrt(delta.x * delta.x + delta.y * delta.y + delta.z * delta.z)
            direction = unreal.Vector(delta.x / length, delta.y / length, delta.z / length)
            rotation = unreal.MathLibrary.find_look_at_rotation(start, end)
            for label, cls, location in (
                ("NPCI_Sight_Observer", ally_cls, start),
                ("NPCI_Sight_Friendly", ally_cls, start + direction * 250.0),
                ("NPCI_Sight_Enemy", german_cls, start + direction * 500.0),
            ):
                actor = actors.spawn_actor_from_class(cls, location, rotation)
                assert actor
                actor.set_actor_label(label)
            levels.editor_request_begin_play()
            phase = "wait_pie"
        elif phase == "loading":
            return
        elif phase == "wait_pie":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            combatants = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
            observer = next(a for a in combatants if a.get_actor_label() == "NPCI_Sight_Observer")
            friend = next(a for a in combatants if a.get_actor_label() == "NPCI_Sight_Friendly")
            enemy = next(a for a in combatants if a.get_actor_label() == "NPCI_Sight_Enemy")
            for actor in combatants:
                if actor.get_actor_label().startswith("PC_City_Enemy"):
                    actor.destroy_actor()
            controller = unreal.AIHelperLibrary.get_ai_controller(observer)
            blackboard = controller.get_editor_property("blackboard")
            assert controller and blackboard
            runtime_start = elapsed
            phase = "observe"
        elif phase == "observe":
            target = blackboard.get_value_as_object("TargetActor")
            report["samples"].append({"phase": "observe", "t": elapsed,
                                      "target": target.get_actor_label() if target else None,
                                      "visible": blackboard.get_value_as_bool("HasVisibleTarget")})
            if target is enemy and blackboard.get_value_as_bool("HasVisibleTarget"):
                remembered = blackboard.get_value_as_vector("LastSeenPosition")
                report["seen"] = {"target": target.get_actor_label(), "last_seen": list(xyz(remembered)),
                                  "enemy_location": list(xyz(enemy.get_actor_location())),
                                  "friendly_was_target": target is friend}
                assert dist(xyz(remembered), xyz(enemy.get_actor_location())) < 1.0
                enemy.set_actor_location(enemy.get_actor_location() + unreal.Vector(5000, 5000, 0), False, False)
                loss_start = elapsed
                phase = "loss"
            elif elapsed - runtime_start > 4.0:
                raise AssertionError("Native sight did not acquire the hostile within four seconds")
        elif phase == "loss":
            target = blackboard.get_value_as_object("TargetActor")
            last_seen = blackboard.get_value_as_vector("LastSeenPosition")
            visible = blackboard.get_value_as_bool("HasVisibleTarget")
            report["samples"].append({"phase": "loss", "t": elapsed,
                                      "target": target.get_actor_label() if target else None,
                                      "visible": visible, "last_seen": list(xyz(last_seen)),
                                      "enemy_now": list(xyz(enemy.get_actor_location()))})
            if elapsed - loss_start < 1.25:
                return
            report["loss"] = {"visible": visible,
                              "memory_delta_cm": dist(xyz(remembered), xyz(last_seen)),
                              "hidden_target_delta_cm": dist(xyz(remembered), xyz(enemy.get_actor_location())),
                              "target_retained_for_later_policy": target is enemy}
            assert not visible
            assert report["loss"]["memory_delta_cm"] <= 0.001
            assert report["loss"]["hidden_target_delta_cm"] > 1000
            assert report["seen"]["friendly_was_target"] is False
            levels.editor_request_end_play()
            phase = "end"
        elif phase == "end" and editor.get_game_world() is None:
            finish()
    except Exception:
        report["errors"].append(traceback.format_exc())
        try:
            levels.editor_request_end_play()
        except Exception:
            pass
        finish()


callback = unreal.register_slate_post_tick_callback(tick)
OUT.mkdir(parents=True, exist_ok=True)
RESULT.write_text(json.dumps(report, indent=2) + "\n")
