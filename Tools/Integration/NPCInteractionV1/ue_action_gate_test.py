"""Native default equipment rejection, stale IDs, actual stop and observer proof."""
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
from ue_equipment_fixture import allied_config, stage_allied

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "action_gate_runtime.json"
VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
AUTHOR = os.environ["CS549_NPC_AUTHOR_IDENTITY"]
author = json.loads((STORE / "Evidence/NPCInteractionV1" / AUTHOR / "action_gate_author.json").read_text())
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "checks": {}, "samples": [], "map_saved": False,
          "scope": "native action IDs/equipment rejection/actual stop; no human contact acceptance or legal autonomous fire"}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
started, phase, phase_time = time.monotonic(), "setup", 0
callback = None
npc = unarmed = ctrl = other = bb = None
goal = stop_position = initial = None
task = generation = 0


def xyz(v):
    return [v.x, v.y, v.z]


def prop(a, name):
    return a.get_editor_property(name)


def request(c, action, tid, rid, gen):
    c.call_method("PC_RequestNPCAction", args=(action, tid, rid, gen))
    result = {"action": action, "task": tid, "request": rid, "generation": gen,
              "reply_task": prop(c, "ReplyTaskID"), "reply_request": prop(c, "ReplyRequestID"), "reply_generation": prop(c, "ReplyGeneration"),
              "result": str(prop(c, "ActionReplyResult")), "reason": str(prop(c, "ActionReplyReason"))}
    report["samples"].append(result)
    assert (result["reply_task"], result["reply_request"], result["reply_generation"]) == (tid, rid, gen)
    return result


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_native_action_identity_stop_equipment_gate" if not report["errors"] else "failed_action_gate_runtime_preserve"
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global phase, phase_time, npc, unarmed, ctrl, other, bb, goal, stop_position, initial, task, generation
    try:
        elapsed = time.monotonic() - started
        assert elapsed < 190
        if phase == "loading":
            return
        if phase == "setup":
            assert guards_match(rows) and author["status"].startswith("pass_")
            assert unreal.load_class(None, "/Script/ParisEditorBridge.ParisBlueprintAuthoring") is None
            report["editor_authoring_bridge_disabled"] = True
            phase = "loading"
            assert levels.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            allied_equipment = allied_config(anchors["PC_City_Ally1"])
            start, goal = (anchors[n].get_actor_location() for n in ("PC_City_Ally1", "PC_City_Ally2"))
            enemy_start = anchors["PC_City_Enemy1"].get_actor_location()
            rotation = unreal.MathLibrary.find_look_at_rotation(start, goal)
            for actor in list(anchors.values()):
                if actor.get_actor_label().startswith(("PC_City_Ally", "PC_City_Enemy")):
                    actors.destroy_actor(actor)
            for label, prefix, point in (("Armed", "BP_PCAlliedActionGate", start), ("Unarmed", "BP_PCGermanActionGate", enemy_start)):
                a = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + prefix + VERSION), point, rotation)
                a.set_actor_label("NPCI_ActionGate_" + label)
                if label == "Armed":
                    report["allied_fixture_equipment"] = stage_allied(a, allied_equipment)
            levels.editor_request_begin_play()
            phase = "wait"
            return
        if phase == "wait":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            roster = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)}
            npc, unarmed = (roster["NPCI_ActionGate_" + s] for s in ("Armed", "Unarmed"))
            ctrl, other = (unreal.AIHelperLibrary.get_ai_controller(a) for a in (npc, unarmed))
            bb = prop(ctrl, "blackboard")
            task, generation = bb.get_value_as_int("TaskID"), prop(npc, "RestoreGeneration")
            before = [prop(npc, n) for n in ("LoadedAmmo", "ReserveAmmo", "ShotSequence")]
            assert request(ctrl, "Fire", task, 1, generation - 1)["reason"] == "StaleGeneration"
            assert request(ctrl, "Fire", task + 5, 2, generation)["reason"] == "StaleTask"
            assert request(ctrl, "Fire", task, 3, generation)["reason"] == "EquipmentUnverified"
            ctrl.call_method("PC_ConfigureNPCEquipment", args=(True, False))
            assert request(ctrl, "Fire", task, 4, generation)["reason"] == "EquipmentNeedsHumanReview"
            assert request(other, "Fire", prop(other, "blackboard").get_value_as_int("TaskID"), 1, prop(unarmed, "RestoreGeneration"))["reason"] == "Unarmed"
            assert before == [prop(npc, n) for n in ("LoadedAmmo", "ReserveAmmo", "ShotSequence")]
            report["checks"]["stale_equipment_unarmed_rejections_no_ammo"] = True
            initial = xyz(npc.get_actor_location())
            ctrl.call_method("PC_SetPatrol", args=(True, goal))
            phase, phase_time = "move", elapsed
            return
        if phase == "end":
            if editor.get_game_world() is None:
                finish()
            return
        if phase == "move":
            if dist(initial, xyz(npc.get_actor_location())) >= 100:
                task, generation = bb.get_value_as_int("TaskID"), prop(npc, "RestoreGeneration")
                assert request(ctrl, "Stop", task, 10, generation)["result"] == "Started"
                stop_position = xyz(npc.get_actor_location())
                assert request(ctrl, "Stop", task, 10, generation)["result"] == "Running"
                assert request(ctrl, "Fire", task, 10, generation)["reason"] == "RequestActionMismatch"
                assert request(ctrl, "Stop", task, 99, generation)["reason"] == "ActionBusy"
                phase, phase_time = "stop", elapsed
            else:
                assert elapsed - phase_time < 12
        elif phase == "stop":
            report["samples"].append({"stop_drift_cm": dist(stop_position, xyz(npc.get_actor_location())),
                                      "reply": str(prop(ctrl, "ActionReplyResult")), "reason": str(prop(ctrl, "ActionReplyReason"))})
            assert dist(stop_position, xyz(npc.get_actor_location())) <= 1
            if str(prop(ctrl, "ActionReplyResult")) == "Completed":
                assert str(prop(ctrl, "ActionReplyReason")) == "BodyStopObserved"
                assert (prop(ctrl, "ReplyTaskID"), prop(ctrl, "ReplyRequestID"), prop(ctrl, "ReplyGeneration")) == (task, 10, generation)
                assert request(ctrl, "Stop", task, 10, generation)["reason"] == "AlreadyObserved"
                assert request(ctrl, "Stop", task, 9, generation)["reason"] == "StaleRequest"
                report["checks"]["native_observer_stop_stable_duplicate_no_restart"] = True
                # Pending stop interrupted by ORIGINAL death, never fake health.
                assert request(ctrl, "Stop", task, 11, generation)["result"] == "Started"
                npc.call_method("PC_ApplyDamage", args=(1000.0,))
                phase, phase_time = "death", elapsed
            else:
                assert elapsed - phase_time < 5
        elif phase == "death" and elapsed - phase_time >= .75:
            assert str(prop(ctrl, "ActionReplyResult")) == "Cancelled"
            assert str(prop(ctrl, "ActionReplyReason")) == "PawnDied"
            report["checks"]["death_cancels_pending_request"] = True
            npc.call_method("PC_ResetLifecycle")
            phase, phase_time = "restored", elapsed
        elif phase == "restored" and elapsed - phase_time >= .75:
            assert request(ctrl, "Fire", task, 12, generation)["reason"] == "StaleGeneration"
            task, generation = bb.get_value_as_int("TaskID"), prop(npc, "RestoreGeneration")
            assert request(ctrl, "Stop", task, 13, generation)["result"] == "Started"
            npc.call_method("PC_ResetLifecycle")
            phase, phase_time = "restore", elapsed
        elif phase == "restore" and elapsed - phase_time >= .75:
            assert str(prop(ctrl, "ActionReplyResult")) == "Cancelled"
            assert str(prop(ctrl, "ActionReplyReason")) == "LifecycleGenerationChanged"
            assert request(ctrl, "Fire", task, 12, generation)["reason"] == "StaleGeneration"
            report["checks"]["restore_cancels_pending_old_generation"] = True
            task, generation = bb.get_value_as_int("TaskID"), prop(npc, "RestoreGeneration")
            assert request(ctrl, "Stop", task, 14, generation)["result"] == "Started"
            ctrl.call_method("PC_SetPatrol", args=(True, goal))
            # One native BT reevaluation stimulus, not a Python movement/AI loop.
            # Do not wait out the Stop observation window before starting the task.
            prop(ctrl, "brain_component").restart_logic()
            phase, phase_time = "supersede", elapsed
        elif phase == "supersede" and elapsed - phase_time >= .75:
            if bb.get_value_as_int("TaskID") == task or str(prop(ctrl, "ActionReplyResult")) == "Started":
                assert elapsed - phase_time < 5, "Native next task/observer did not progress"
                return
            assert bb.get_value_as_int("TaskID") != task
            assert str(prop(ctrl, "ActionReplyResult")) == "Cancelled"
            assert str(prop(ctrl, "ActionReplyReason")) == "TaskSuperseded"
            assert (prop(ctrl, "ReplyTaskID"), prop(ctrl, "ReplyRequestID"), prop(ctrl, "ReplyGeneration")) == (task, 14, generation)
            report["checks"]["native_task_supersession_cancels_original_request_identity"] = True
            ctrl.call_method("PC_PolicyHold")
            levels.editor_request_end_play()
            phase = "end"
    except Exception:
        report["errors"].append(traceback.format_exc())
        RESULT.write_text(json.dumps(report, indent=2) + "\n")
        try:
            levels.editor_request_end_play()
        except Exception:
            pass
        phase = "end"


callback = unreal.register_slate_post_tick_callback(tick)
RESULT.write_text(json.dumps(report, indent=2) + "\n")
