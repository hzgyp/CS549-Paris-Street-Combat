"""Unsaved city diagnostic. Python observes; it never writes NPC memory."""
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
RESULT = OUT / "sight_causal.json"
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [],
          "samples": [], "raw_events": [], "map_saved": False,
          "scope": "native sensing/LOS/BB causal diagnostic, not complete NPC acceptance"}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
phase = "setup"
started = time.monotonic()
phase_start = sample_time = 0
callback = None
observer = friend = enemy = controller = bb = sensor = None
direction = None
remembered = None


def xyz(v):
    return [v.x, v.y, v.z]


def observed(call):
    try:
        return call()
    except Exception as exc:
        return {"api_error": str(exc)}


def raw_seen(pawn):
    report["raw_events"].append({"t": time.monotonic() - started,
                                 "phase": phase, "pawn": pawn.get_actor_label()})


def sample(elapsed):
    target = bb.get_value_as_object("TargetActor")
    eyes = observer.get_actor_eyes_view_point()
    hit = unreal.SystemLibrary.line_trace_single(
        observer, eyes[0], enemy.get_actor_eyes_view_point()[0],
        unreal.TraceTypeQuery.ECC_VISIBILITY, False, [observer],
        unreal.DrawDebugTrace.NONE, True)
    hit_data = hit[1].to_tuple() if isinstance(hit, tuple) else hit.to_tuple()
    blocker = hit_data[9]
    report["samples"].append({
        "t": elapsed, "phase": phase,
        "target": target.get_actor_label() if target else None,
        "visible": bb.get_value_as_bool("HasVisibleTarget"),
        "last_seen": xyz(bb.get_value_as_vector("LastSeenPosition")),
        "last_seen_time": bb.get_value_as_float("LastSeenTime"),
        "observer": xyz(observer.get_actor_location()),
        "friend": xyz(friend.get_actor_location()), "enemy": xyz(enemy.get_actor_location()),
        "rotation": str(observer.get_actor_rotation()), "eyes": xyz(eyes[0]),
        "could_see": observed(lambda: sensor.could_see_pawn(enemy, False)),
        "controller_los": observed(lambda: controller.line_of_sight_to(enemy)),
        "visibility_blocker": blocker.get_actor_label() if blocker else None,
        "observer_team": observer.get_editor_property("TeamId"),
        "enemy_team": enemy.get_editor_property("TeamId"),
    })
    return target


def finish():
    global callback
    if sensor is not None:
        observed(lambda: sensor.on_see_pawn.remove_callable(raw_seen))
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_sight_causal_diagnostic" if not report["errors"] else "failed_sight_causal_preserve"
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global phase, phase_start, sample_time, observer, friend, enemy, controller, bb, sensor, direction, remembered
    try:
        elapsed = time.monotonic() - started
        assert elapsed < 180, "Diagnostic runtime timeout"
        if phase == "setup":
            assert guards_match(rows)
            phase = "loading"
            assert levels.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            start = anchors["PC_City_Ally1"].get_actor_location()
            end = anchors["PC_City_Ally2"].get_actor_location()
            lane = end - start
            length = sqrt(lane.x**2 + lane.y**2 + lane.z**2)
            direction = unreal.Vector(lane.x / length, lane.y / length, lane.z / length)
            rotation = unreal.MathLibrary.find_look_at_rotation(start, end)
            for label, package, distance in (("NPCI_Causal_Observer", "BP_PCAlliedNPCSightV4", 0),
                                             ("NPCI_Causal_Friend", "BP_PCAlliedNPCSightV4", 250),
                                             ("NPCI_Causal_Enemy", "BP_PCGermanNPCSightV4", 500)):
                actor = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(
                    DEST + "/" + package), start + direction * distance, rotation)
                assert actor
                actor.set_actor_label(label)
            levels.editor_request_begin_play()
            phase = "wait"
        elif phase == "wait":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            pawns = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
            by_label = {a.get_actor_label(): a for a in pawns}
            observer, friend, enemy = (by_label["NPCI_Causal_" + name] for name in ("Observer", "Friend", "Enemy"))
            for actor in pawns:
                if actor.get_actor_label().startswith("PC_City_Enemy"):
                    actor.destroy_actor()
            controller = unreal.AIHelperLibrary.get_ai_controller(observer)
            bb = controller.get_editor_property("blackboard")
            sensor = observer.get_component_by_class(unreal.PawnSensingComponent)
            assert sensor and controller and bb
            report["sensor"] = {name: observed(lambda name=name: sensor.get_editor_property(name))
                                for name in ("sensing_interval", "sight_radius", "peripheral_vision_angle",
                                             "only_sense_players", "see_pawns", "enable_sensing_updates")}
            report["sensor"]["native_delegate_bound_before_listener"] = sensor.on_see_pawn.is_bound()
            report["sensor"]["owner"] = sensor.get_owner().get_actor_label()
            phase_start = elapsed
            phase = "baseline"
        elif phase in ("baseline", "listener", "isolated", "loss"):
            target = None
            if elapsed - sample_time >= .1:
                sample_time = elapsed
                target = sample(elapsed)
            if phase == "baseline" and elapsed - phase_start >= 2:
                sensor.on_see_pawn.add_callable(raw_seen)
                phase, phase_start = "listener", elapsed
            elif phase == "listener" and elapsed - phase_start >= 2:
                perpendicular = unreal.Vector(-direction.y, direction.x, 0)
                friend.set_actor_location(friend.get_actor_location() + perpendicular * 180, False, False)
                for actor in unreal.GameplayStatics.get_all_actors_of_class(observer, unreal.Character):
                    if actor.get_actor_label().startswith("PC_City_Ally"):
                        actor.destroy_actor()
                phase, phase_start = "isolated", elapsed
            elif phase == "isolated":
                if target is enemy and bb.get_value_as_bool("HasVisibleTarget"):
                    remembered = xyz(bb.get_value_as_vector("LastSeenPosition"))
                    report["native_acquisition"] = True
                    enemy.set_actor_location(enemy.get_actor_location() + unreal.Vector(5000, 5000, 0), False, False)
                    phase, phase_start = "loss", elapsed
                elif elapsed - phase_start >= 4:
                    report["native_acquisition"] = False
                    levels.editor_request_end_play()
                    phase = "end"
            elif phase == "loss" and elapsed - phase_start >= 1.25:
                report["loss"] = {"visible": bb.get_value_as_bool("HasVisibleTarget"),
                                  "memory_delta_cm": dist(remembered, xyz(bb.get_value_as_vector("LastSeenPosition")))}
                assert not report["loss"]["visible"] and report["loss"]["memory_delta_cm"] <= .001
                levels.editor_request_end_play()
                phase = "end"
        elif phase == "end" and editor.get_game_world() is None:
            finish()
    except Exception:
        report["errors"].append(traceback.format_exc())
        observed(levels.editor_request_end_play)
        finish()


callback = unreal.register_slate_post_tick_callback(tick)
RESULT.write_text(json.dumps(report, indent=2) + "\n")
