"""Actual city BT guard/patrol/unreachable/lifecycle test; no per-frame AI driver."""
import json
import os
import sys
import time
import traceback
from math import dist, hypot
from pathlib import Path

import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, STORE, guard_rows, guards_match

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "behavior_runtime.json"
AUTHOR = os.environ["CS549_NPC_AUTHOR_IDENTITY"]
author = json.loads((STORE / "Evidence/NPCInteractionV1" / AUTHOR / "behavior_author.json").read_text())
VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "author_identity": AUTHOR,
          "errors": [], "samples": [], "map_saved": False,
          "scope": "native BT noncombat guard/patrol/two-replan/death-restore proof; not combat, gait or complete NPC acceptance"}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
started = time.monotonic()
phase, phase_start, last_sample = "setup", 0, 0
callback = None
mover = guard = invalid = ctrl = guard_ctrl = invalid_ctrl = bb = bad_bb = None
goal = start_pos = guard_pos = stop_pos = dead_pos = None
max_guard_drift = max_step = max_speed = 0
previous = None
previous_time = 0
outbound_arrived = False
cancel_start = None


def xyz(v):
    return [v.x, v.y, v.z]


def horizontal(a, b):
    return hypot(a[0] - b[0], a[1] - b[1])


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_native_behavior_guard_patrol_replan_lifecycle" if not report["errors"] else "failed_behavior_runtime_preserve"
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global phase, phase_start, last_sample, mover, guard, invalid, ctrl, guard_ctrl, invalid_ctrl, bb, bad_bb
    global goal, start_pos, guard_pos, stop_pos, dead_pos, max_guard_drift, max_step, max_speed, previous, previous_time, outbound_arrived, cancel_start
    try:
        elapsed = time.monotonic() - started
        assert elapsed < 180, "Behavior test timeout"
        if phase == "loading":
            # Loading pumps Slate callbacks reentrantly; no runtime objects yet.
            return
        if phase == "setup":
            assert guards_match(rows) and author["status"].startswith("pass_")
            phase = "loading"
            assert levels.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            origin = anchors["PC_City_Ally1"].get_actor_location()
            goal = anchors["PC_City_Ally2"].get_actor_location()
            guard_origin = anchors["PC_City_Enemy1"].get_actor_location()
            bad_origin = anchors["PC_City_Enemy2"].get_actor_location()
            rotation = unreal.MathLibrary.find_look_at_rotation(origin, goal)
            for actor in list(anchors.values()):
                if actor.get_actor_label().startswith(("PC_City_Ally", "PC_City_Enemy")):
                    actors.destroy_actor(actor)
            for label, cls, location in (("Mover", "BP_PCAlliedBehavior", origin),
                                         ("Guard", "BP_PCGermanBehavior", guard_origin),
                                         ("Invalid", "BP_PCGermanBehavior", bad_origin)):
                actor = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + cls + VERSION), location, rotation)
                assert actor
                actor.set_actor_label("NPCI_Behavior_" + label)
            levels.editor_request_begin_play()
            phase = "wait"
            return
        if phase == "wait":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            pawns = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)}
            mover, guard, invalid = (pawns["NPCI_Behavior_" + name] for name in ("Mover", "Guard", "Invalid"))
            ctrl, guard_ctrl, invalid_ctrl = (unreal.AIHelperLibrary.get_ai_controller(a) for a in (mover, guard, invalid))
            bb, bad_bb = ctrl.get_editor_property("blackboard"), invalid_ctrl.get_editor_property("blackboard")
            assert bb and bad_bb and bb is not bad_bb
            report["runtime_controller"] = ctrl.get_class().get_path_name()
            report["brain_class"] = ctrl.get_editor_property("brain_component").get_class().get_name()
            start_pos, guard_pos = xyz(mover.get_actor_location()), xyz(guard.get_actor_location())
            previous, previous_time = start_pos, elapsed
            phase, phase_start = "guard", elapsed
            return
        if phase == "end":
            if editor.get_game_world() is None:
                finish()
            return
        if elapsed - last_sample < .1:
            return
        last_sample = elapsed
        position = xyz(mover.get_actor_location())
        velocity = xyz(mover.get_velocity())
        speed = hypot(velocity[0], velocity[1])
        step = dist(previous, position)
        dt = elapsed - previous_time
        if phase in ("patrol", "cancel_move"):
            assert step <= 600 * dt + 15, "Unexplained movement discontinuity"
            max_step = max(max_step, step)
            max_speed = max(max_speed, speed)
        previous, previous_time = position, elapsed
        max_guard_drift = max(max_guard_drift, dist(guard_pos, xyz(guard.get_actor_location())))
        report["samples"].append({"phase": phase, "t": elapsed, "position": position, "speed": speed,
                                  "patrol_leg": ctrl.get_editor_property("PatrolLeg"),
                                  "reason": str(bb.get_value_as_name("WaitingReason")),
                                  "task_id": bb.get_value_as_int("TaskID"), "request_id": bb.get_value_as_int("RequestID"),
                                  "generation": bb.get_value_as_int("RestoreGeneration"),
                                  "replans": bb.get_value_as_int("RetryCount"),
                                  "move_status": str(ctrl.get_move_status()),
                                  "bad_replans": bad_bb.get_value_as_int("RetryCount"),
                                  "bad_reason": str(bad_bb.get_value_as_name("WaitingReason"))})
        if phase == "guard" and elapsed - phase_start >= .75:
            assert dist(start_pos, position) <= 1 and max_guard_drift <= 1
            report["guard_drift_cm"] = max_guard_drift
            ctrl.call_method("PC_SetPatrol", args=(True, goal))
            invalid_ctrl.call_method("PC_SetPatrol", args=(True, unreal.Vector(10000000, 10000000, 10000000)))
            phase, phase_start = "patrol", elapsed
        elif phase == "patrol":
            assert elapsed - phase_start < 25, "Native patrol did not complete bounded roundtrip"
            leg = ctrl.get_editor_property("PatrolLeg")
            if leg and not outbound_arrived:
                assert horizontal(position, xyz(goal)) <= 50, "Arrival flag without body arrival"
                report["outbound"] = {"position": position, "goal_error_xy_cm": horizontal(position, xyz(goal)),
                                      "request_id": bb.get_value_as_int("RequestID")}
                outbound_arrived = True
            elif outbound_arrived and not leg:
                assert horizontal(position, start_pos) <= 50
                assert str(bad_bb.get_value_as_name("WaitingReason")) == "PathExhausted"
                assert bad_bb.get_value_as_int("RetryCount") == 2
                report["roundtrip"] = {"home_error_xy_cm": horizontal(position, start_pos),
                                       "max_speed_cm_s": max_speed, "max_observed_step_cm": max_step,
                                       "request_id": bb.get_value_as_int("RequestID"), "replan_cap": 2}
                ctrl.call_method("PC_SetPatrol", args=(False, goal))
                stop_pos = position
                phase, phase_start = "hold", elapsed
        elif phase == "hold" and elapsed - phase_start >= .75:
            assert dist(stop_pos, position) <= 1
            assert bad_bb.get_value_as_int("RetryCount") == 2
            report["arrival_hold_drift_cm"] = dist(stop_pos, position)
            ctrl.call_method("PC_SetPatrol", args=(True, goal))
            cancel_start = position
            phase, phase_start = "cancel_move", elapsed
        elif phase == "cancel_move":
            assert elapsed - phase_start < 10, "Second native move did not start"
            if horizontal(position, cancel_start) >= 100:
                report["pre_death_request"] = bb.get_value_as_int("RequestID")
                mover.call_method("PC_ApplyDamage", args=(1000.0,))
                phase, phase_start = "dead_settle", elapsed
        elif phase == "dead_settle" and elapsed - phase_start >= .3:
            assert mover.get_editor_property("Health") <= 0
            assert not bb.get_value_as_bool("HasMoveGoal")
            assert bb.get_value_as_int("RequestID") == 0
            assert bb.get_value_as_object("TargetActor") is None
            dead_pos = position
            phase, phase_start = "dead_hold", elapsed
        elif phase == "dead_hold" and elapsed - phase_start >= .75:
            assert dist(dead_pos, position) <= 1
            report["death"] = {"drift_cm": dist(dead_pos, position), "request_id": bb.get_value_as_int("RequestID"),
                               "move_status": str(ctrl.get_move_status())}
            ctrl.call_method("PC_SetPatrol", args=(False, goal))
            mover.call_method("PC_ResetLifecycle")
            phase, phase_start = "restore_settle", elapsed
        elif phase == "restore_settle" and elapsed - phase_start >= .3:
            assert mover.get_editor_property("Health") > 0
            assert bb.get_value_as_int("RestoreGeneration") == mover.get_editor_property("RestoreGeneration")
            stop_pos = position
            phase, phase_start = "restored_hold", elapsed
        elif phase == "restored_hold" and elapsed - phase_start >= .75:
            assert dist(stop_pos, position) <= 1 and bb.get_value_as_int("RequestID") == 0
            report["restore"] = {"drift_cm": dist(stop_pos, position),
                                 "generation": bb.get_value_as_int("RestoreGeneration"), "request_id": 0}
            report["max_guard_drift_cm"] = max_guard_drift
            assert max_guard_drift <= 1
            levels.editor_request_end_play()
            phase = "end"
    except Exception:
        report["errors"].append(traceback.format_exc())
        RESULT.write_text(json.dumps(report, indent=2) + "\n")
        try:
            levels.editor_request_end_play()
        except Exception:
            pass
        # Quit only on a later callback after PIE teardown, not inside loading.
        phase = "end"


callback = unreal.register_slate_post_tick_callback(tick)
RESULT.write_text(json.dumps(report, indent=2) + "\n")
