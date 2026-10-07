"""Three actual-city Germans: native sight, frozen finite search, unarmed rejection."""
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
RESULT = OUT / "search_runtime.json"
AUTHOR = os.environ["CS549_NPC_AUTHOR_IDENTITY"]
VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
author = json.loads((STORE / "Evidence/NPCInteractionV1" / AUTHOR / "search_author.json").read_text())
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "samples": [],
          "scope": "three native German noncombat search/role/unarmed proof; no legal armed fire or visual acceptance", "map_saved": False}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
phase, started, phase_time, sample_time = "setup", time.monotonic(), 0, 0
callback = None
npcs = controllers = blackboards = None
target = role_point = None
memory = deadlines = None
search_starts = {}
homes = None
health_before = None


def xyz(v):
    return [v.x, v.y, v.z]


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_three_native_german_finite_search" if not report["errors"] else "failed_native_search_preserve"
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global phase, phase_time, sample_time, npcs, controllers, blackboards, target, role_point, memory, deadlines, homes, health_before
    try:
        elapsed = time.monotonic() - started
        assert elapsed < 200, "Search runtime timeout"
        if phase == "loading":
            return
        if phase == "setup":
            assert guards_match(rows) and author["status"].startswith("pass_")
            phase = "loading"
            assert levels.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            start, end = anchors["PC_City_Ally1"].get_actor_location(), anchors["PC_City_Ally2"].get_actor_location()
            lane = end - start
            length = sqrt(lane.x**2 + lane.y**2 + lane.z**2)
            direction = unreal.Vector(lane.x / length, lane.y / length, lane.z / length)
            perpendicular = unreal.Vector(-direction.y, direction.x, 0)
            role_point = end + perpendicular * 180
            for actor in list(anchors.values()):
                if actor.get_actor_label().startswith(("PC_City_Ally", "PC_City_Enemy")):
                    actors.destroy_actor(actor)
                elif actor.get_actor_label() == "PC_City_Player":
                    actor.set_actor_hidden_in_game(True)
            enemy_cls = unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCGermanSearch" + VERSION)
            for i, offset in enumerate((-180, 0, 180)):
                location = start + perpendicular * offset
                rotation = unreal.MathLibrary.find_look_at_rotation(location, start + direction * 500)
                actor = actors.spawn_actor_from_class(enemy_cls, location, rotation)
                actor.set_actor_label("NPCI_Search_" + str(i))
            actor = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCAlliedNPCSightV4"),
                                                 start + direction * 500, unreal.MathLibrary.find_look_at_rotation(start, end))
            actor.set_actor_label("NPCI_Search_Target")
            levels.editor_request_begin_play()
            phase = "wait"
            return
        if phase == "wait":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            roster = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)}
            npcs = [roster["NPCI_Search_" + str(i)] for i in range(3)]
            target = roster["NPCI_Search_Target"]
            controllers = [unreal.AIHelperLibrary.get_ai_controller(a) for a in npcs]
            blackboards = [c.get_editor_property("blackboard") for c in controllers]
            assert len({b.get_path_name() for b in blackboards}) == 3
            homes = [xyz(a.get_actor_location()) for a in npcs]
            health_before = target.get_editor_property("Health")
            for i, c in enumerate(controllers):
                c.call_method("PC_SetSearchRole", args=(i == 2, role_point, 200.0))
                c.call_method("PC_EnablePolicy", args=(True,))
                assert npcs[i].get_editor_property("WeaponAppearance") is None
            phase, phase_time = "acquire", elapsed
            return
        if phase == "end":
            if editor.get_game_world() is None:
                finish()
            return
        if elapsed - sample_time < .2:
            return
        sample_time = elapsed
        now = unreal.GameplayStatics.get_time_seconds(npcs[0])
        for i, (a, c, b) in enumerate(zip(npcs, controllers, blackboards)):
            report["samples"].append({"phase": phase, "npc": i, "t": elapsed, "game_time": now,
                "position": xyz(a.get_actor_location()), "last_seen": xyz(b.get_value_as_vector("LastSeenPosition")),
                "visible": b.get_value_as_bool("HasVisibleTarget"), "search_active": c.get_editor_property("SearchActive"),
                "index": c.get_editor_property("SearchIndex"), "visited": c.get_editor_property("SearchVisitedCount"),
                "deadline": c.get_editor_property("PolicyDeadline"), "state": str(c.get_editor_property("PolicyState")),
                "task_id": b.get_value_as_int("TaskID"), "request_id": b.get_value_as_int("RequestID"),
                "reason": str(b.get_value_as_name("WaitingReason"))})
        if phase == "acquire":
            if all(b.get_value_as_object("TargetActor") is target and b.get_value_as_bool("HasVisibleTarget") for b in blackboards):
                memory = [xyz(b.get_value_as_vector("LastSeenPosition")) for b in blackboards]
                for npc in npcs:
                    before = (npc.get_editor_property("LoadedAmmo"), npc.get_editor_property("ShotSequence"))
                    eye = npc.get_actor_eyes_view_point()[0]
                    npc.call_method("PC_RequestFire", args=(eye, target.get_actor_location() - eye))
                    assert before == (npc.get_editor_property("LoadedAmmo"), npc.get_editor_property("ShotSequence"))
                assert target.get_editor_property("Health") == health_before
                report["unarmed_fire_rejected"] = True
                target.set_actor_hidden_in_game(True)
                target.set_actor_location(target.get_actor_location() + unreal.Vector(5000, 5000, 0), False, False)
                phase, phase_time = "search", elapsed
            else:
                assert elapsed - phase_time < 4, "Not all three native sensors acquired the actual target"
        elif phase == "search":
            for i, (c, b) in enumerate(zip(controllers, blackboards)):
                assert dist(memory[i], xyz(b.get_value_as_vector("LastSeenPosition"))) <= .001
                if c.get_editor_property("SearchActive") and i not in search_starts:
                    search_starts[i] = {"start": now, "deadline": c.get_editor_property("PolicyDeadline")}
                    assert 14.5 <= search_starts[i]["deadline"] - now <= 15.1
                if i in search_starts:
                    assert abs(search_starts[i]["deadline"] - c.get_editor_property("PolicyDeadline")) <= .001
                assert c.get_editor_property("SearchIndex") <= 5
            if len(search_starts) == 3 and all(not c.get_editor_property("SearchActive") for c in controllers):
                report["search"] = [{"npc": i, **search_starts[i], "end": now,
                                     "index": c.get_editor_property("SearchIndex"), "visited": c.get_editor_property("SearchVisitedCount")}
                                    for i, c in enumerate(controllers)]
                assert all(row["end"] <= row["deadline"] + 1 for row in report["search"])
                assert sum(row["visited"] for row in report["search"]) > 0
                phase, phase_time = "return", elapsed
            else:
                assert elapsed - phase_time < 30
        elif phase == "return":
            if all(dist(homes[i], xyz(npcs[i].get_actor_location())) <= 55 for i in (0, 1)) and str(controllers[2].get_editor_property("PolicyState")) == "RolePatrol":
                report["role_return"] = {"guard_errors_cm": [dist(homes[i], xyz(npcs[i].get_actor_location())) for i in (0, 1)],
                                         "patrol_state": str(controllers[2].get_editor_property("PolicyState"))}
                assert target.get_editor_property("Health") == health_before
                levels.editor_request_end_play()
                phase = "end"
            else:
                assert elapsed - phase_time < 20, "Search ended but physical role return failed"
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
