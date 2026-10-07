"""Actual-city native allied movement/reservation/lifecycle; no AI pose driver."""
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

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "squad_runtime.json"
VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
AUTHOR = os.environ["CS549_NPC_AUTHOR_IDENTITY"]
author = json.loads((STORE / "Evidence/NPCInteractionV1" / AUTHOR / "squad_author.json").read_text())
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "samples": [], "map_saved": False,
          "scope": "native two allied follow/reservation/short-chase/death-restore proof; not combat/grip/gait/FF acceptance"}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
phase, started, phase_time, sampled = "setup", time.monotonic(), 0, 0
callback = None
npcs = controllers = blackboards = enemies = None
player = coordinator = None
direction = perpendicular = origin = target_point = None
retained = None
previous = None
previous_time = 0
episode_peaks = {}
enemy_relocated = False
dead_position = None
dead_slot = survivor_slot = None
comparison_goals = None
comparison_origin_time = 0
comparison_nearest_separation = 1e9


def xyz(v):
    return [v.x, v.y, v.z]


def prop(obj, name):
    return obj.get_editor_property(name)


def write():
    RESULT.write_text(json.dumps(report, indent=2) + "\n")


def end():
    global phase
    levels.editor_request_end_play()
    phase = "end"


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_native_two_allied_reservation_chase_lifecycle" if not report["errors"] else "failed_native_squad_preserve"
    write()
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global phase, phase_time, sampled, npcs, controllers, blackboards, player, coordinator, direction, perpendicular, origin
    global retained, previous, previous_time, enemies, enemy_relocated, target_point, dead_position, dead_slot, survivor_slot, comparison_goals, comparison_origin_time, comparison_nearest_separation
    try:
        elapsed = time.monotonic() - started
        assert elapsed < 200, "Squad bounded runtime timeout"
        if phase == "loading":
            return
        if phase == "setup":
            assert guards_match(rows) and author["status"].startswith("pass_")
            phase = "loading"
            assert levels.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            origin, destination = (anchors[name].get_actor_location() for name in ("PC_City_Ally1", "PC_City_Ally2"))
            lane = destination - origin
            length = sqrt(lane.x**2 + lane.y**2 + lane.z**2)
            direction = unreal.Vector(lane.x / length, lane.y / length, 0)
            perpendicular = unreal.Vector(-direction.y, direction.x, 0)
            yaw = unreal.MathLibrary.find_look_at_rotation(origin, destination)
            formal_player = anchors["PC_City_Player"]
            formal_player.set_actor_location(origin + direction * 800, False, False)
            formal_player.set_actor_rotation(yaw, False)
            for actor in list(anchors.values()):
                if actor.get_actor_label().startswith(("PC_City_Ally", "PC_City_Enemy")):
                    actors.destroy_actor(actor)
            coord = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCSquadReservation" + VERSION), origin, unreal.Rotator())
            coord.set_actor_label("NPCI_Squad_Coordinator")
            for i, side in enumerate((-180, 180)):
                npc = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCAlliedSquad" + VERSION), origin + perpendicular * side, yaw)
                npc.set_actor_label("NPCI_Squad_Ally" + str(i))
            for i in range(3):
                npc = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCGermanSquad" + VERSION), destination + direction * (3000 + i * 200), yaw)
                npc.set_actor_label("NPCI_Squad_Enemy" + str(i))
                npc.set_actor_hidden_in_game(True)
            levels.editor_request_begin_play()
            phase = "wait"
            return
        if phase == "wait":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            roster = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)}
            player = unreal.GameplayStatics.get_player_pawn(world, 0)
            npcs = [roster["NPCI_Squad_Ally" + str(i)] for i in range(2)]
            enemies = [roster["NPCI_Squad_Enemy" + str(i)] for i in range(3)]
            controllers = [unreal.AIHelperLibrary.get_ai_controller(a) for a in npcs]
            all_controllers = controllers + [unreal.AIHelperLibrary.get_ai_controller(a) for a in enemies]
            all_boards = [c.get_editor_property("blackboard") for c in all_controllers]
            blackboards = all_boards[:2]
            assert len({b.get_path_name() for b in all_boards}) == 5
            assert len({c.get_class().get_path_name() for c in all_controllers}) == 1
            report["five_npc_common_controller_private_boards"] = True
            all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
            report["runtime_coordinator_diagnostics"] = [{"label": a.get_actor_label(), "class": a.get_class().get_path_name()}
                for a in all_actors if "Squad" in a.get_actor_label() or "Reservation" in a.get_class().get_name()]
            candidates = [a for a in all_actors if a.get_actor_label() == "NPCI_Squad_Coordinator"]
            assert len(candidates) == 1
            coordinator = candidates[0]
            for c, a in zip(controllers, npcs):
                assert a.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property("use_rvo_avoidance")
                c.call_method("PC_EnableSquad", args=(True,))
            previous, previous_time = [xyz(a.get_actor_location()) for a in npcs], elapsed
            report["start_positions"] = previous
            phase, phase_time = "follow", elapsed
            return
        if phase == "end":
            if editor.get_game_world() is None:
                finish()
            return
        if phase == "comparison_end_world":
            if editor.get_game_world() is None:
                levels.editor_request_begin_play()
                phase = "comparison_wait"
            return
        if phase == "comparison_wait":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            roster = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)}
            player = unreal.GameplayStatics.get_player_pawn(world, 0)
            npcs = [roster["NPCI_Squad_Ally" + str(i)] for i in range(2)]
            controllers = [unreal.AIHelperLibrary.get_ai_controller(a) for a in npcs]
            blackboards = [c.get_editor_property("blackboard") for c in controllers]
            initial = [xyz(a.get_actor_location()) for a in npcs]
            assert all(dist(a, b) <= 1 for a, b in zip(initial, report["start_positions"]))
            pool = [unreal.Vector(*point) for point in report["comparison_point_pool"]]
            comparison_goals = [min(pool, key=lambda p: dist(initial[i], xyz(p))) for i in range(2)]
            for c, goal in zip(controllers, comparison_goals):
                assert not prop(c, "SquadEnabled")
                c.call_method("PC_GotoPolicyGoal", args=(goal, "IndependentNearest"))
            previous, previous_time = initial, elapsed
            phase, phase_time = "comparison_independent", elapsed
            comparison_origin_time = elapsed
            return
        if phase == "comparison_independent":
            comparison_nearest_separation = min(comparison_nearest_separation, dist(xyz(npcs[0].get_actor_location()), xyz(npcs[1].get_actor_location())))
            if all(dist(xyz(a.get_actor_location()), xyz(goal)) <= 55 for a, goal in zip(npcs, comparison_goals)) or elapsed - phase_time > 15:
                report["matched_comparison"] = {"same_world_editor_start": True, "same_two_pawns": True, "same_rvo": True,
                    "same_candidate_point_pool": report["comparison_point_pool"],
                    "coordinated_seconds": report["follow"]["seconds"], "independent_seconds": elapsed - comparison_origin_time,
                    "independent_goal_errors_cm": [dist(xyz(a.get_actor_location()), xyz(goal)) for a, goal in zip(npcs, comparison_goals)],
                    "independent_destinations": [xyz(g) for g in comparison_goals],
                    "independent_min_body_center_separation_cm": comparison_nearest_separation,
                    "independent_failures": sum(dist(xyz(a.get_actor_location()), xyz(g)) > 55 for a, g in zip(npcs, comparison_goals)),
                    "conclusion": "bounded matched comparison, not proof of superiority or crowded-city scalability"}
                end()
            return
        if elapsed - sampled < .1:
            return
        sampled = elapsed
        positions = [xyz(a.get_actor_location()) for a in npcs]
        if phase == "follow":
            report["coordinated_min_body_center_separation_cm"] = min(report.get("coordinated_min_body_center_separation_cm", 1e9), dist(positions[0], positions[1]))
        dt = elapsed - previous_time
        for i, (a, c, b) in enumerate(zip(npcs, controllers, blackboards)):
            assert dist(previous[i], positions[i]) <= 600 * dt + 15, "Body movement discontinuity"
            rid = prop(c, "SquadReservationID")
            episode = prop(c, "ChaseEpisode")
            travel = prop(c, "ChaseDistance")
            mode = str(prop(c, "SquadMode"))
            player_distance = dist(positions[i], xyz(player.get_actor_location()))
            episode_peaks[str((i, episode))] = max(episode_peaks.get(str((i, episode)), 0), travel)
            assert travel <= 1000, "Native accumulated chase exceeds 10m"
            if mode == "Chase":
                assert player_distance <= 1000, "Chase body leaves 10m player radius"
            report["samples"].append({"t": elapsed, "phase": phase, "npc": i, "position": positions[i],
                "reservation": rid, "slot": prop(c, "FormationSlot"), "goal": xyz(prop(c, "HeldGoal")),
                "mode": mode, "action": str(prop(a, "ActionState")), "task_id": b.get_value_as_int("TaskID"),
                "request_id": b.get_value_as_int("RequestID"), "generation": prop(a, "RestoreGeneration"),
                "visible": b.get_value_as_bool("HasVisibleTarget"), "reason": str(b.get_value_as_name("WaitingReason")),
                "chase_active": prop(c, "ChaseActive"), "chase_episode": episode, "chase_distance": travel,
                "player_distance": player_distance, "move_status": str(c.get_move_status())})
        # Low-frequency diagnostic checkpoint; not a completion assertion.
        if int(elapsed) != int(previous_time):
            write()
        previous, previous_time = positions, elapsed
        if phase == "follow":
            arrived = all(dist(positions[i], xyz(prop(c, "HeldGoal"))) <= 55 and prop(c, "SquadReservationID") > 0 for i, c in enumerate(controllers))
            if arrived:
                retained = [prop(c, "SquadReservationID") for c in controllers]
                assert len(set(retained)) == 2
                separation = dist(xyz(prop(controllers[0], "HeldGoal")), xyz(prop(controllers[1], "HeldGoal")))
                assert separation >= 150
                assert all(300 <= dist(p, xyz(player.get_actor_location())) <= 600 for p in positions)
                report["follow"] = {"goal_errors_cm": [dist(positions[i], xyz(prop(c, "HeldGoal"))) for i, c in enumerate(controllers)],
                                     "reservation_ids": retained, "point_separation_cm": separation, "seconds": elapsed - phase_time}
                report["comparison_point_pool"] = [xyz(prop(c, "HeldGoal")) for c in controllers]
                phase, phase_time = "retained_idle", elapsed
            else:
                assert elapsed - phase_time < 15, "Native allies did not reach distinct reserved follow points"
        elif phase == "retained_idle" and elapsed - phase_time >= 1:
            assert retained == [prop(c, "SquadReservationID") for c in controllers]
            report["idle_retains_reservations"] = True
            total = prop(npcs[0], "LoadedAmmo") + prop(npcs[0], "ReserveAmmo")
            npcs[0].call_method("PC_RequestReload")
            assert str(prop(npcs[0], "ActionState")) == "Reloading", "Original NPC reload not admitted"
            report["reload_ammo_total_before"] = total
            phase, phase_time = "reload", elapsed
        elif phase == "reload":
            assert retained == [prop(c, "SquadReservationID") for c in controllers]
            if str(prop(npcs[0], "ActionState")) == "Ready":
                assert prop(npcs[0], "LoadedAmmo") + prop(npcs[0], "ReserveAmmo") == report["reload_ammo_total_before"]
                report["original_reload_reservation_and_ammo_conserved"] = True
                target_point = player.get_actor_location() + direction * 500
                enemies[0].set_actor_location(target_point, False, False)
                enemies[0].set_actor_hidden_in_game(False)
                phase, phase_time = "chase", elapsed
            else:
                assert elapsed - phase_time < 8, "Original NPC reload did not finish"
        elif phase == "chase":
            if all(prop(c, "ChaseActive") and prop(c, "ChaseDistance") >= 100 for c in controllers) and not enemy_relocated:
                report["before_target_change"] = [{"episode": prop(c, "ChaseEpisode"), "travel": prop(c, "ChaseDistance"), "task": b.get_value_as_int("TaskID")}
                                                  for c, b in zip(controllers, blackboards)]
                enemies[0].set_actor_hidden_in_game(True)
                enemies[0].set_actor_location(enemies[0].get_actor_location() + unreal.Vector(5000, 5000, 0), False, False)
                # Same independently proved visible location; hidden old fixture
                # must not leave its capsule blocking the replacement sight ray.
                enemies[1].set_actor_location(target_point, False, False)
                enemies[1].set_actor_hidden_in_game(False)
                report["replacement_los_before_wait"] = [c.line_of_sight_to(enemies[1]) for c in controllers]
                enemy_relocated = True
                phase, phase_time = "new_target", elapsed
            else:
                assert elapsed - phase_time < 12, "Native short chase did not move"
        elif phase == "new_target":
            if all(b.get_value_as_object("TargetActor") is enemies[1] and b.get_value_as_bool("HasVisibleTarget") for b in blackboards):
                for before, c in zip(report["before_target_change"], controllers):
                    assert prop(c, "ChaseEpisode") == before["episode"]
                    assert prop(c, "ChaseDistance") >= before["travel"]
                report["native_target_change_preserves_budget"] = True
                # Original damage entry on the actually visible replacement.
                # Do not hide it: prove the native observation rejects a corpse.
                enemies[1].call_method("PC_ApplyDamage", args=(1000.0,))
                phase, phase_time = "observed_death", elapsed
            else:
                assert elapsed - phase_time < 5, "Native sensor did not acquire replacement target"
        elif phase == "observed_death":
            if all(b.get_value_as_object("TargetActor") is None and not b.get_value_as_bool("HasVisibleTarget") for b in blackboards):
                assert all(b.get_value_as_float("LastSeenTime") == 0 for b in blackboards)
                report["observed_target_death_clears_memory"] = True
                phase, phase_time = "regroup", elapsed
            else:
                assert elapsed - phase_time < 4, "Observed dead target was retained/reacquired"
        elif phase == "regroup":
            if all(not prop(c, "ChaseActive") and dist(positions[i], xyz(prop(c, "HeldGoal"))) <= 55 for i, c in enumerate(controllers)):
                report["chase_episode_peak_cm"] = episode_peaks
                phase, phase_time = "settle_follow", elapsed
            else:
                assert elapsed - phase_time < 12, "No physical regroup after loss"
        elif phase == "settle_follow" and elapsed - phase_time >= 1:
            # Regroup -> Follow is a legal duty reassignment. Capture idle
            # ownership only after that native transition, not one tick before.
            assert all(str(prop(c, "SquadMode")) == "Follow" and prop(c, "SquadReservationID") > 0
                       and dist(positions[i], xyz(prop(c, "HeldGoal"))) <= 55 for i, c in enumerate(controllers))
            if all(str(prop(c, "SquadMode")) == "Follow" for c in controllers):
                retained = [prop(c, "SquadReservationID") for c in controllers]
                dead_slot, survivor_slot = [prop(c, "FormationSlot") for c in controllers]
                report["settled_follow_before_death"] = {"reservations": retained, "slots": [dead_slot, survivor_slot],
                    "tasks": [b.get_value_as_int("TaskID") for b in blackboards]}
                npcs[0].call_method("PC_ApplyDamage", args=(1000.0,))
                dead_position = xyz(npcs[0].get_actor_location())
                phase, phase_time = "death", elapsed
        elif phase == "death" and elapsed - phase_time >= .75:
            assert prop(controllers[0], "SquadReservationID") == 0
            assert prop(coordinator, "Owner" + str(dead_slot)) is None and prop(coordinator, "RID" + str(dead_slot)) == 0
            assert prop(controllers[1], "SquadReservationID") == retained[1] and prop(controllers[1], "FormationSlot") == survivor_slot
            assert dist(dead_position, positions[0]) <= 1 and blackboards[0].get_value_as_int("RequestID") == 0
            report["death_release_and_survivor_slot_stable"] = True
            old_generation = prop(npcs[0], "RestoreGeneration")
            report["generation_before_restore"] = old_generation
            npcs[0].call_method("PC_ResetLifecycle")
            phase, phase_time = "restore", elapsed
        elif phase == "restore" and elapsed - phase_time >= .75:
            assert prop(npcs[0], "RestoreGeneration") == report["generation_before_restore"] + 1
            assert prop(controllers[0], "SquadGeneration") == prop(npcs[0], "RestoreGeneration")
            assert prop(controllers[0], "SquadReservationID") > 0 and prop(controllers[0], "SquadReservationID") != retained[0]
            assert prop(controllers[1], "FormationSlot") == survivor_slot
            report["restore_new_generation_new_reservation"] = True
            levels.editor_request_end_play()
            phase = "comparison_end_world"
    except Exception:
        report["errors"].append(traceback.format_exc())
        write()
        try:
            end()
        except Exception:
            phase = "end"


callback = unreal.register_slate_post_tick_callback(tick)
write()
