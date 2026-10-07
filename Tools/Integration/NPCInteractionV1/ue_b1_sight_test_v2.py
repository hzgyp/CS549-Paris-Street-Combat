"""Fresh actual-city V2 Pawn-owned native sight/faction/loss/private-memory test."""
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
VERSION = os.environ.get("CS549_NPC_SIGHT_VERSION", "V2")
CLEAR_SCENE = os.environ.get("CS549_NPC_SIGHT_CLEAR_SCENE") == "1"
RESULT = OUT / os.environ.get("CS549_NPC_SIGHT_RUNTIME_RESULT", "b1_sight_runtime_v2.json")
ENTRY = "/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1"
ALLY = DEST + "/BP_PCAlliedNPCSight" + VERSION
GERMAN = DEST + "/BP_PCGermanNPCSight" + VERSION
rows = guard_rows()
author = json.loads((STORE / "Evidence/NPCInteractionV1" / AUTHOR_IDENTITY /
                     os.environ.get("CS549_NPC_SIGHT_AUTHOR_RESULT", "b1_sight_author_v2.json")).read_text())
report = {
    "identity": IDENTITY, "author_identity": AUTHOR_IDENTITY,
    "scope": "fresh unsaved actual-city V2 Pawn-owned native sight/faction/loss/private-memory proof",
    "samples": [], "errors": [], "map_saved": False,
}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
callback = None
phase = "setup"
started = time.monotonic()
runtime_start = loss_start = None
enemy_position = None
observer = friend = enemy = controller = blackboard = None
remembered = None


def xyz(v):
    return (v.x, v.y, v.z)


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = ("pass_b1_v2_native_faction_sight_loss_memory"
                        if not report["errors"] else "failed_preserve_b1_v2_sight_evidence")
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta_seconds):
    global phase, runtime_start, loss_start, observer, friend, enemy, controller, blackboard, remembered, enemy_position
    try:
        elapsed = time.monotonic() - started
        assert elapsed < 180, "B1 V2 sight runtime timeout"
        if phase == "setup":
            assert guards_match(rows) and author["status"].startswith("pass_")
            phase = "loading"
            assert levels.load_level(ENTRY)
            ally_cls = unreal.EditorAssetLibrary.load_blueprint_class(ALLY)
            german_cls = unreal.EditorAssetLibrary.load_blueprint_class(GERMAN)
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            start = anchors["PC_City_Ally1"].get_actor_location()
            end = anchors["PC_City_Ally2"].get_actor_location()
            lane = end - start
            length = sqrt(lane.x * lane.x + lane.y * lane.y + lane.z * lane.z)
            direction = unreal.Vector(lane.x / length, lane.y / length, lane.z / length)
            rotation = unreal.MathLibrary.find_look_at_rotation(start, end)
            if CLEAR_SCENE:
                # Replace only unsaved test-world occupants, not map assets.
                for actor in list(anchors.values()):
                    if actor.get_actor_label().startswith(("PC_City_Ally", "PC_City_Enemy")):
                        actors.destroy_actor(actor)
            perpendicular = unreal.Vector(-direction.y, direction.x, 0)
            enemy_position = start + direction * 500.0
            for label, cls, location in (
                ("NPCI_SightV2_Observer", ally_cls, start),
                ("NPCI_SightV2_Friendly", ally_cls, start + direction * 250.0 + perpendicular * (180.0 if CLEAR_SCENE else 0)),
                ("NPCI_SightV2_Enemy", german_cls, enemy_position + (unreal.Vector(5000, 5000, 0) if CLEAR_SCENE else unreal.Vector())),
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
            observer = next(a for a in combatants if a.get_actor_label() == "NPCI_SightV2_Observer")
            friend = next(a for a in combatants if a.get_actor_label() == "NPCI_SightV2_Friendly")
            enemy = next(a for a in combatants if a.get_actor_label() == "NPCI_SightV2_Enemy")
            for actor in combatants:
                if actor.get_actor_label().startswith("PC_City_Enemy"):
                    actor.destroy_actor()
            controller = unreal.AIHelperLibrary.get_ai_controller(observer)
            assert controller
            blackboard = controller.get_editor_property("blackboard")
            assert blackboard
            report["runtime_classes"] = {
                "observer": observer.get_class().get_path_name(),
                "controller": controller.get_class().get_path_name(),
            }
            if CLEAR_SCENE:
                sensor = observer.get_component_by_class(unreal.PawnSensingComponent)
                assert sensor and sensor.on_see_pawn.is_bound()
                report["native_sensing_bound_without_python_listener"] = True
                other_controller = unreal.AIHelperLibrary.get_ai_controller(friend)
                assert other_controller and other_controller.get_editor_property("blackboard") is not blackboard
                report["independent_blackboards"] = True
            runtime_start = elapsed
            phase = "friendly_only" if CLEAR_SCENE else "observe"
        elif phase == "friendly_only":
            assert blackboard.get_value_as_object("TargetActor") is None, "Friendly-only scene acquired a target"
            assert not blackboard.get_value_as_bool("HasVisibleTarget")
            if elapsed - runtime_start >= .75:
                report["friendly_only_rejected"] = True
                enemy.set_actor_location(enemy_position, False, False)
                runtime_start = elapsed
                phase = "observe"
        elif phase == "observe":
            target = blackboard.get_value_as_object("TargetActor")
            report["samples"].append({
                "phase": "observe", "t": elapsed,
                "target": target.get_actor_label() if target else None,
                "visible": blackboard.get_value_as_bool("HasVisibleTarget"),
            })
            if target is enemy and blackboard.get_value_as_bool("HasVisibleTarget"):
                remembered = blackboard.get_value_as_vector("LastSeenPosition")
                report["seen"] = {
                    "target": target.get_actor_label(), "last_seen": list(xyz(remembered)),
                    "enemy_location": list(xyz(enemy.get_actor_location())),
                    "friendly_was_target": target is friend,
                }
                assert dist(xyz(remembered), xyz(enemy.get_actor_location())) < 1.0
                if CLEAR_SCENE:
                    assert controller.line_of_sight_to(enemy)
                    report["actual_los_on_acquisition"] = True
                enemy.set_actor_location(enemy.get_actor_location() + unreal.Vector(5000, 5000, 0), False, False)
                loss_start = elapsed
                phase = "loss"
            elif elapsed - runtime_start > 4.0:
                raise AssertionError("V2 native Pawn-owned sight did not acquire hostile within four seconds")
        elif phase == "loss":
            target = blackboard.get_value_as_object("TargetActor")
            last_seen = blackboard.get_value_as_vector("LastSeenPosition")
            visible = blackboard.get_value_as_bool("HasVisibleTarget")
            report["samples"].append({
                "phase": "loss", "t": elapsed,
                "target": target.get_actor_label() if target else None,
                "visible": visible, "last_seen": list(xyz(last_seen)),
                "enemy_now": list(xyz(enemy.get_actor_location())),
            })
            if elapsed - loss_start < 1.25:
                return
            report["loss"] = {
                "visible": visible,
                "memory_delta_cm": dist(xyz(remembered), xyz(last_seen)),
                "hidden_target_delta_cm": dist(xyz(remembered), xyz(enemy.get_actor_location())),
                "target_retained_for_later_policy": target is enemy,
            }
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
