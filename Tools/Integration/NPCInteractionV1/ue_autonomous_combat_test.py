"""Native decisions only: two faction encounters, blocking, reload/death/reset."""
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, STORE, guard_rows, guards_match

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "autonomous_combat_runtime.json"
VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
rows = guard_rows()
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "checks": {}, "samples": [],
          "equipment": [], "map_saved": False, "python_combat_decision_requests": 0, "stale_admission_probes": 0,
          "scope": "native BT autonomous faction combat in real city; not formal selection or full visual/FPS/mission acceptance"}
started = time.monotonic()
phase = "setup"
phase_time = 0
callback = None
roster = []
player = shooter = target = friend = ctrl = bb = wall = None
point = direction = side = None
index = 0
initial = blocker_ammo = None
reload_commits = 0
interrupt_ids = None
joint_dead = {}
joint_start_shots = []
reset_expected = None


def prop(a, n):
    return a.get_editor_property(n)


def xyz(v):
    return [v.x, v.y, v.z]


def snap():
    return {"phase": phase, "team": prop(shooter, "TeamId"), "game_time": unreal.GameplayStatics.get_time_seconds(shooter),
        "health": prop(shooter, "Health"), "target_health": prop(target, "Health"),
        "body": xyz(shooter.get_actor_location()), "speed": shooter.get_velocity().length(),
        "loaded": prop(shooter, "LoadedAmmo"), "reserve": prop(shooter, "ReserveAmmo"),
        "shots": prop(shooter, "ShotSequence"), "commit": prop(shooter, "ReloadCommitCount"),
        "action": str(prop(shooter, "ActionState")), "shot_outcome": str(prop(shooter, "ShotOutcome")),
        "generation": prop(shooter, "RestoreGeneration"), "decision_count": prop(ctrl, "CombatDecisionCount"),
        "combat_phase": str(prop(ctrl, "CombatPhase")), "holding": prop(ctrl, "CombatHold"),
        "reply": str(prop(ctrl, "ActionReplyResult")), "reason": str(prop(ctrl, "ActionReplyReason")),
        "ids": [prop(ctrl, n) for n in ("ReplyTaskID", "ReplyRequestID", "ReplyGeneration")],
        "visible": bb.get_value_as_bool("HasVisibleTarget"), "target": str(bb.get_value_as_object("TargetActor")),
        "current_los": ctrl.line_of_sight_to(target, unreal.Vector(), False),
        "target_body": xyz(target.get_actor_location()), "player_body": xyz(player.get_actor_location()),
        "friend_body": xyz(friend.get_actor_location()), "forward": xyz(shooter.get_actor_forward_vector()),
        "chase_distance": prop(ctrl, "ChaseDistance"), "player_distance": (player.get_actor_location() - shooter.get_actor_location()).length(),
        "last_seen": xyz(bb.get_value_as_vector("LastSeenPosition")),
        "combat_enabled": prop(ctrl, "CombatEnabled"), "equipment_flags": [prop(ctrl, "EquipmentNumericVerified"), prop(ctrl, "EquipmentHumanAccepted")],
        "reservation": prop(ctrl, "SquadReservationID")}


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_native_autonomous_faction_combat" if not report["errors"] else "failed_autonomous_combat_preserve"
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def prepare(now, interrupted=False):
    global shooter, target, friend, ctrl, bb, phase, phase_time, initial, reload_commits
    for i, a in enumerate(roster):
        c = unreal.AIHelperLibrary.get_ai_controller(a)
        c.call_method("PC_EnableCombat", args=(False,))
        c.call_method("PC_PolicyHold")
        a.call_method("PC_ResetLifecycle")
        a.set_actor_location(point + direction * (3000 + i * 250) + side * 1500, False, False)
    shooter, target, friend = (roster[0], roster[2], roster[1]) if index == 0 else (roster[2], roster[0], roster[3])
    player.set_actor_location(point - direction * 350, False, False)
    shooter.set_actor_location(point, False, False)
    target.set_actor_location(point + direction * 700, False, False)
    if interrupted:
        # Lifecycle reset deliberately preserves ammo. Provide three finite
        # real opposing bodies, enough to exhaust the remaining magazine before
        # an ORIGINAL reload. No ammo/health assignment or infinite revival.
        roster[1].set_actor_location(point + direction * 700 + side * 220, False, False)
        player.call_method("PC_ResetLifecycle")
        player.set_actor_location(point + direction * 700 - side * 220, False, False)
    rot = unreal.MathLibrary.find_look_at_rotation(point, target.get_actor_location())
    shooter.set_actor_rotation(rot, False)
    ctrl = unreal.AIHelperLibrary.get_ai_controller(shooter)
    ctrl.set_control_rotation(rot)
    bb = prop(ctrl, "blackboard")
    initial = (prop(shooter, "LoadedAmmo"), prop(shooter, "ReserveAmmo"), prop(shooter, "ShotSequence"))
    reload_commits = prop(shooter, "ReloadCommitCount")
    # Native perception is a fixture prerequisite, not a Python-written target.
    phase, phase_time = ("acquire_interrupt" if interrupted else "acquire"), now


def tick(delta):
    global phase, phase_time, roster, player, point, direction, side, wall, index, blocker_ammo, interrupt_ids, joint_dead, reset_expected, joint_start_shots
    try:
        now = time.monotonic() - started
        assert now < 190, (phase, "overall timeout")
        if phase == "loading":
            return
        if phase == "setup":
            assert guards_match(rows)
            assert unreal.load_class(None, "/Script/ParisEditorBridge.ParisBlueprintAuthoring") is None
            phase = "loading"
            assert levels.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            point = anchors["PC_City_Ally1"].get_actor_location()
            d = anchors["PC_City_Ally2"].get_actor_location() - point
            direction = unreal.MathLibrary.normal(unreal.Vector(d.x, d.y, 0))
            side = unreal.Vector(-direction.y, direction.x, 0)
            anchors["PC_City_Player"].set_actor_location(point - direction * 350, False, False)
            for a in list(anchors.values()):
                if a.get_actor_label().startswith(("PC_City_Ally", "PC_City_Enemy")):
                    actors.destroy_actor(a)
            for i in range(5):
                prefix = "BP_PCAlliedCombat" if i < 2 else "BP_PCGermanCombat"
                a = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + prefix + VERSION),
                    point + side * (1500 + 200 * i), unreal.Rotator())
                a.set_actor_label("NPCI_Auto_" + str(i))
            coordinator_class = unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCSquadReservationV4")
            coordinators = [a for a in actors.get_all_level_actors() if a.get_class() == coordinator_class]
            assert len(coordinators) <= 1, "Duplicate native squad coordinators"
            report["reused_saved_squad_coordinator"] = bool(coordinators)
            if not coordinators:
                actors.spawn_actor_from_class(coordinator_class, point + side * 3000, unreal.Rotator())
            levels.editor_request_begin_play()
            phase = "wait"
            return
        world = editor.get_game_world()
        if phase == "wait":
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            all_actors = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)}
            roster = [all_actors["NPCI_Auto_" + str(i)] for i in range(5)]
            player = unreal.GameplayStatics.get_player_character(world, 0)
            for a in roster:
                adapters = [x for x in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.ParisNPCGripActor) if prop(x, "Target") == a]
                assert len(adapters) == 1 and prop(adapters[0], "Initialized") and not str(prop(adapters[0], "BindingError"))
                assert prop(a, "WeaponAppearance") and a.mesh.get_post_process_instance()
                c = unreal.AIHelperLibrary.get_ai_controller(a)
                c.call_method("PC_ConfigureNPCEquipment", args=(True, True))
                report["equipment"].append({"team": prop(a, "TeamId"), "config": prop(adapters[0], "BindingConfig").get_path_name(),
                                            "controller": c.get_class().get_path_name(), "bb": prop(c, "blackboard").get_path_name()})
            assert len(set(x["bb"] for x in report["equipment"])) == 5
            report["checks"]["six_roster_five_private_controllers_memory_selected_equipment"] = True
            prepare(now)
            return
        if phase == "end":
            if world is None:
                finish()
            return
        if phase == "joint":
            joint = []
            for i, a in enumerate(roster):
                c = unreal.AIHelperLibrary.get_ai_controller(a)
                item = {"npc": i, "team": prop(a, "TeamId"), "health": prop(a, "Health"), "shots": prop(a, "ShotSequence"),
                    "loaded": prop(a, "LoadedAmmo"), "reserve": prop(a, "ReserveAmmo"), "generation": prop(a, "RestoreGeneration"),
                    "action": str(prop(a, "ActionState")), "decisions": prop(c, "CombatDecisionCount"),
                    "reservation": prop(c, "SquadReservationID"), "body": xyz(a.get_actor_location()), "speed": a.get_velocity().length()}
                assert item["loaded"] + item["reserve"] + item["shots"] == 18, item
                if item["health"] <= 0:
                    if i not in joint_dead:
                        joint_dead[i] = (now, item["shots"], item["body"])
                    else:
                        when, shots, position = joint_dead[i]
                        assert item["shots"] == shots, item
                        if now - when > .75:
                            assert item["speed"] == 0 and sum((x-y)**2 for x,y in zip(position,item["body"])) <= 1, item
                elif i in joint_dead:
                    raise AssertionError("Unrequested resurrection")
                joint.append(item)
            report["samples"].append({"phase": "joint", "time": now - phase_time, "roster": joint, "player_health": prop(player, "Health")})
            if now - phase_time >= 12:
                assert sum(x["shots"] - joint_start_shots[x["npc"]] for x in joint if x["team"] == 0) > 0
                assert sum(x["shots"] - joint_start_shots[x["npc"]] for x in joint if x["team"] == 1) > 0
                assert joint_dead, "No legitimate casualty observed"
                report["checks"]["six_actor_simultaneous_both_factions_conserved_finite_casualties"] = True
                phase = "end"
                levels.editor_request_end_play()
            return
        s = snap()
        report["samples"].append(s)
        assert s["loaded"] + s["reserve"] + s["shots"] == sum(initial)
        if phase in ("acquire", "acquire_interrupt"):
            sensed = bb.get_value_as_object("TargetActor")
            allowed = (roster[0], roster[1], player) if phase == "acquire_interrupt" else (target,)
            if sensed in allowed and s["visible"]:
                ctrl.call_method("PC_EnableCombat", args=(True,))
                phase, phase_time = ("interrupt_encounter" if phase == "acquire_interrupt" else "encounter"), now
            else:
                assert now - phase_time < 5, s
        elif phase == "encounter":
            assert s["speed"] <= 300.01
            if s["shots"] == 1:
                assert s["target_health"] == 65 and s["loaded"] == 1
                blocker_ammo = (s["loaded"], s["reserve"], s["shots"])
                friend.set_actor_location(point + direction * 350, False, False)
                phase, phase_time = "blocked", now
            else:
                assert now - phase_time < 12, s
        elif phase == "blocked":
            assert (s["loaded"], s["reserve"], s["shots"]) == blocker_ammo and prop(friend, "Health") == 100 and s["target_health"] == 65, s
            if now - phase_time >= 1.5:
                report["checks"]["friendly_lane_wait_no_ammo_team_" + str(s["team"])] = True
                friend.set_actor_location(point + side * 2500, False, False)
                # After genuine sight loss/role return, place the same hostile
                # in the new forward field once, to test native reacquisition.
                target.set_actor_location(shooter.get_actor_location() + shooter.get_actor_forward_vector() * 700, False, False)
                player.set_actor_location(shooter.get_actor_location() - shooter.get_actor_forward_vector() * 350, False, False)
                phase, phase_time = "fight", now
        elif phase == "fight":
            if s["target_health"] <= 0:
                assert s["shots"] == 3 and s["commit"] == reload_commits + 1, s
                report["checks"]["autonomous_stop_turn_fire_reload_death_team_" + str(s["team"])] = True
                phase, phase_time = "corpse", now
            else:
                assert now - phase_time < 15, s
        elif phase == "corpse" and now - phase_time >= 1.25:
            sensed = bb.get_value_as_object("TargetActor")
            assert sensed != target, s
            if index == 0:
                assert s["shots"] == 3 and not s["visible"] and sensed is None, s
            else:
                # A nearer live player is a legitimate NEW hostile after the
                # corpse is cleared, not a reason for all German attacks to stop.
                assert sensed is None or sensed == player, s
                assert 3 <= s["shots"] <= 6 and prop(player, "Health") == max(0, 100 - 35 * (s["shots"] - 3)), s
                if sensed is not None:
                    assert prop(player, "Health") > 0, s
                report["checks"]["German_corpse_clear_allows_legitimate_player_reacquisition"] = True
            report["checks"]["observed_dead_target_not_reselected_team_" + str(s["team"])] = True
            index += 1
            if index < 2:
                prepare(now)
            else:
                index = 1
                prepare(now, interrupted=True)
        elif phase == "interrupt_encounter":
            if s["action"] == "Reloading":
                interrupt_ids = (s["ids"], prop(shooter, "ActionID"), prop(shooter, "ReloadCommitCount"))
                shooter.call_method("PC_ApplyDamage", args=(1000.0,))
                phase, phase_time = "dead_reload", now
            else:
                assert now - phase_time < 15, s
        elif phase == "dead_reload" and now - phase_time >= 1:
            assert s["health"] == 0 and s["reply"] == "Cancelled" and s["reason"] == "PawnDied", s
            assert s["commit"] == interrupt_ids[2] and s["speed"] == 0, s
            old_ids = interrupt_ids[0]
            reset_expected = (s["loaded"], s["reserve"], s["shots"])
            shooter.call_method("PC_ResetLifecycle")
            ctrl.call_method("PC_EnableCombat", args=(False,))
            ctrl.call_method("PC_RequestNPCAction", args=("Fire", old_ids[0], old_ids[1], old_ids[2]))
            report["stale_admission_probes"] += 1
            assert str(prop(ctrl, "ActionReplyReason")) == "StaleGeneration"
            report["checks"]["death_cancels_real_autoreload_old_generation_rejected"] = True
            phase, phase_time = "reset", now
        elif phase == "reset" and now - phase_time >= 3:
            assert (s["loaded"], s["reserve"], s["shots"]) == reset_expected
            report["checks"]["no_old_reload_commit_after_original_reset"] = True
            # One declared joint fixture, then observe all five native brains.
            # No per-frame teleport/target/ammo/decision command follows.
            for i, a in enumerate(roster):
                c = unreal.AIHelperLibrary.get_ai_controller(a)
                c.call_method("PC_EnableCombat", args=(False,))
                c.call_method("PC_PolicyHold")
                a.call_method("PC_ResetLifecycle")
                p = point + side * (200 * i if i < 2 else 200 * (i - 3)) + direction * (0 if i < 2 else 700)
                a.set_actor_location(p, False, False)
                facing = unreal.MathLibrary.find_look_at_rotation(p, point + direction * (700 if i < 2 else 0))
                a.set_actor_rotation(facing, False)
                c.set_control_rotation(facing)
                c.call_method("PC_EnableCombat", args=(True,))
            joint_start_shots = [prop(a, "ShotSequence") for a in roster]
            report["joint_start_shots"] = joint_start_shots
            player.call_method("PC_ResetLifecycle")
            player.set_actor_location(point - direction * 350, False, False)
            phase, phase_time = "joint", now
    except Exception:
        report["errors"].append(traceback.format_exc())
        finish()


callback = unreal.register_slate_post_tick_callback(tick)
