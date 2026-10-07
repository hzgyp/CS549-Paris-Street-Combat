"""Fresh actual-city B1 proof: real BT MoveTo, continuous body samples, explicit stop."""
import json
import os
import sys
import time
import traceback
from math import dist
from pathlib import Path

import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, STORE, guard_rows, guards_match

IDENTITY = os.environ["CS549_NPC_IDENTITY"]
AUTHOR_IDENTITY = os.environ["CS549_NPC_AUTHOR_IDENTITY"]
OUT = STORE / "Evidence/NPCInteractionV1" / IDENTITY
RESULT = OUT / "b1_runtime.json"
ENTRY = "/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1"
ALLY = DEST + "/BP_PCAlliedNPCInteractionV1"
TREE = DEST + "/BT_PC_NPCMoveV1"
rows = guard_rows()
author = json.loads((STORE / "Evidence/NPCInteractionV1" / AUTHOR_IDENTITY / "b1_author.json").read_text())
report = {"identity": IDENTITY, "author_identity": AUTHOR_IDENTITY,
          "scope": "fresh unsaved actual-city B1 built-in BT MoveTo/stop proof", "samples": [], "errors": []}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
callback = None
phase = "setup"
started = time.monotonic()
last_sample = 0.0
runtime_actor = controller = blackboard = None
goal = None
stop_position = None
stop_time = None


def xyz(value):
    return (value.x, value.y, value.z)


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_b1_native_move_continuity_stop" if not report["errors"] else "failed_preserve_b1_evidence"
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global phase, last_sample, runtime_actor, controller, blackboard, goal, stop_position, stop_time
    try:
        elapsed = time.monotonic() - started
        assert elapsed < 180, "B1 runtime timeout"
        if phase == "setup":
            assert guards_match(rows) and author["status"].startswith("pass_")
            phase = "loading"
            assert levels.load_level(ENTRY)
            cls = unreal.EditorAssetLibrary.load_blueprint_class(ALLY)
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            start_anchor, goal_anchor = anchors["PC_City_Ally1"], anchors["PC_City_Ally2"]
            staged = actors.spawn_actor_from_class(cls, start_anchor.get_actor_location(), start_anchor.get_actor_rotation())
            assert staged
            staged.set_actor_label("NPCI_B1_Mover")
            goal = goal_anchor.get_actor_location()
            levels.editor_request_begin_play()
            phase = "wait_pie"
        elif phase == "loading":
            return
        elif phase == "wait_pie":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            runtime_actor = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                                 if a.get_actor_label() == "NPCI_B1_Mover")
            controller = unreal.AIHelperLibrary.get_ai_controller(runtime_actor)
            assert controller
            blackboard = controller.get_editor_property("blackboard")
            tree = unreal.load_asset(TREE)
            assert blackboard and tree
            blackboard.set_value_as_vector("DesiredPosition", goal)
            blackboard.set_value_as_int("TaskID", 101)
            blackboard.set_value_as_int("RequestID", 1)
            assert controller.run_behavior_tree(tree)
            report["start"] = list(xyz(runtime_actor.get_actor_location()))
            report["goal"] = list(xyz(goal))
            phase = "moving"
            last_sample = elapsed
        elif phase == "moving":
            if elapsed - last_sample < 0.1:
                return
            last_sample = elapsed
            p = runtime_actor.get_actor_location()
            report["samples"].append({"t": elapsed, "position": list(xyz(p)), "velocity": list(xyz(runtime_actor.get_velocity())),
                                      "goal_distance": dist(xyz(p), xyz(goal))})
            if dist(xyz(p), xyz(goal)) < 120:
                controller.stop_movement()
                stop_position = xyz(p)
                stop_time = elapsed
                phase = "stopped"
            elif len(report["samples"]) > 120:
                raise AssertionError("MoveTo did not reach full goal within bounded samples")
        elif phase == "stopped":
            if elapsed - stop_time < 0.75:
                return
            p = xyz(runtime_actor.get_actor_location())
            points = [tuple(s["position"]) for s in report["samples"]]
            segments = [dist(a, b) for a, b in zip(points, points[1:])]
            report["movement"] = {"distance_cm": sum(segments), "max_segment_cm": max(segments, default=0.0),
                                  "stop_drift_cm": dist(stop_position, p), "sample_count": len(points),
                                  "task_id": blackboard.get_value_as_int("TaskID"),
                                  "request_id": blackboard.get_value_as_int("RequestID")}
            assert report["movement"]["distance_cm"] > 100
            assert report["movement"]["max_segment_cm"] < 200
            assert report["movement"]["stop_drift_cm"] <= 1.0
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
