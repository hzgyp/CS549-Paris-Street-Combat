"""Fresh startup and finite interaction; no Python AI configuration/requests."""
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, STORE, guard_rows, guards_match
from ue_formal_roster import LABELS, MAP, prop, xyz, actor_state, replace_roster, ready_snapshot

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "formal_combat_runtime.json"
MODE = os.environ["CS549_NPC_MODE"]
VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
rows = guard_rows()
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "checks": {}, "samples": [],
          "python_ai_configuration_calls": 0, "python_combat_requests": 0, "map_saved": False,
          "scope": "native bootstrap and bounded finite functional play; not visual/full route/FPS acceptance"}
phase = "setup"
started = time.monotonic()
phase_time = 0
callback = None
roster = []
player = None
initial_shots = []
dead = {}
next_sample = 0


def finish():
    global callback
    report["status"] = "pass_formal_native_startup_and_finite_play" if not report["errors"] else "failed_formal_combat_runtime_preserve"
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global phase, phase_time, roster, player, initial_shots, next_sample
    try:
        now = time.monotonic() - started
        assert now < 190, (phase, "overall timeout")
        if phase == "loading":
            return
        if phase == "setup":
            assert guards_match(rows)
            assert unreal.load_class(None, "/Script/ParisEditorBridge.ParisBlueprintAuthoring") is None
            phase = "loading"
            assert levels.load_level(MAP)
            if MODE == "bootstrap_test":
                report["replacement"] = replace_roster(VERSION)
            lookup = {a.get_actor_label(): a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
            report["saved_initial_roster"] = [actor_state(lookup[label]) for label in LABELS]
            report["saved_player"] = actor_state(lookup["PC_City_Player"])
            levels.editor_request_begin_play()
            phase, phase_time = "wait", now
            return
        world = editor.get_game_world()
        if phase == "end":
            if world is None:
                finish()
            return
        if world is None:
            return
        game_time = unreal.GameplayStatics.get_time_seconds(world)
        if phase == "wait":
            if game_time < 4:
                return
            lookup = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)}
            roster = [lookup[label] for label in LABELS]
            player = unreal.GameplayStatics.get_player_character(world, 0)
            report["equipment"] = ready_snapshot(world, roster)
            assert [prop(a, "TeamId") for a in roster] == [0, 0, 1, 1, 1]
            assert all(a.get_class().get_name().endswith("FormalCombat" + VERSION + "_C") for a in roster)
            ff = [a for a in lookup.values() if a.get_class().get_name() == "BP_PCFriendlyFirePolicyV1_C"]
            squad = [a for a in lookup.values() if a.get_class().get_name() == "BP_PCSquadReservationV4_C"]
            assert len(ff) == len(squad) == 1 and prop(ff[0], "FriendlyFireEnabled") is False
            assert player.get_class().get_path_name() == report["saved_player"]["class"]
            assert prop(player.mesh, "skeletal_mesh_asset").get_path_name() == report["saved_player"]["mesh"]
            assert player.mesh.get_post_process_instance() is None
            report["checks"]["five_native_bootstrap_selected_binding_private_memory_ff_off_original_player"] = True
            report["natural_roster"] = [{"label": a.get_actor_label(), "position": xyz(a.get_actor_location()),
                "decisions": prop(unreal.AIHelperLibrary.get_ai_controller(a), "CombatDecisionCount"),
                "squad": str(prop(unreal.AIHelperLibrary.get_ai_controller(a), "SquadMode")), "health": prop(a, "Health")} for a in roster]
            report["checks"]["saved_startup_observed_without_python_configuration"] = True
            # The native saved-layout encounter already starts before this
            # observer's readiness gate. Compare to BEFORE PIE, not a second
            # artificial encounter after real casualties. No reset/teleport.
            initial_shots = [x["shots"] for x in report["saved_initial_roster"]]
            report["joint_initial"] = report["saved_initial_roster"]
            phase, phase_time, next_sample = "joint", game_time, game_time
            return
        if phase == "joint":
            if game_time < next_sample:
                return
            next_sample = game_time + .25
            sample = []
            for i, a in enumerate(roster):
                c = unreal.AIHelperLibrary.get_ai_controller(a)
                item = {"label": a.get_actor_label(), "team": prop(a, "TeamId"), "health": prop(a, "Health"),
                        "loaded": prop(a, "LoadedAmmo"), "reserve": prop(a, "ReserveAmmo"), "shots": prop(a, "ShotSequence"),
                        "decisions": prop(c, "CombatDecisionCount"), "reason": str(prop(c, "ActionReplyReason")),
                        "speed": a.get_velocity().length(), "position": xyz(a.get_actor_location()),
                        "target": str(prop(c, "blackboard").get_value_as_object("TargetActor"))}
                assert item["loaded"] + item["reserve"] + item["shots"] == 18, item
                if item["health"] <= 0:
                    if i not in dead:
                        dead[i] = (game_time, item["shots"], item["position"])
                    else:
                        when, shots, position = dead[i]
                        assert item["shots"] == shots, item
                        if game_time - when > .75:
                            assert item["speed"] == 0 and sum((x-y)**2 for x,y in zip(position,item["position"])) <= 1, item
                elif i in dead:
                    raise AssertionError("Unrequested resurrection")
                sample.append(item)
            report["samples"].append({"game_time": game_time, "joint_time": game_time-phase_time, "roster": sample, "player_health": prop(player, "Health")})
            if game_time - phase_time >= 14:
                assert sum(x["shots"]-initial_shots[i] for i,x in enumerate(sample) if x["team"] == 0) > 0, sample
                assert sum(x["shots"]-initial_shots[i] for i,x in enumerate(sample) if x["team"] == 1) > 0, sample
                assert dead, "No real casualty"
                report["checks"]["native_finite_both_factions_damage_ammo_conserved_dead_stop_no_resurrection"] = True
                phase = "end"
                levels.editor_request_end_play()
    except Exception:
        report["errors"].append(traceback.format_exc())
        finish()


callback = unreal.register_slate_post_tick_callback(tick)
