"""Bounded fixtures on selected formal brains; native AI, read-only assets."""
import json
import os
import sys
import time
import traceback
from math import dist, hypot
from pathlib import Path
import unreal

sys.path.insert(0, os.environ.get("CS549_NPC_SOURCE_DIR",str(Path(__file__).resolve().parent)))
from common import STORE, guard_rows, guards_match
from ue_formal_roster import LABELS, MAP, prop, xyz, ready_snapshot

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
SCENARIO = os.environ["CS549_NPC_ACCEPT_SCENARIO"]
LONG_FRAME = os.environ.get("CS549_NPC_ACCEPT_LONG_FRAME") == "1"
rows = guard_rows()
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "scenario": SCENARIO,
          "errors": [], "checks": {}, "samples": [], "stimuli": [], "summary": {}, "captures": [],
          "map_saved": False, "python_ai_decision_or_pose_driver": False,
          "scope": "formal-brain finite functional fixtures; not complete visual/FPS/mission acceptance"}
started = time.monotonic()
phase = "setup"
phase_time = 0
next_sample = 0
callback = None
roster = ctrls = boards = None
player = policy = coord = None
origin = player_point = None
direction = unreal.Vector(0, 1, 0)
side = unreal.Vector(-1, 0, 0)
saved_homes = []
previous = []
previous_time = 0
episode = []
before_switch = []
cutoffs = {}
searches = {}
memory = []
dead = {}
initial = []
retained = []
frame_intervals = []
patrol_visits = []
patrol_origin = None
review_camera = None
blockers = []
perf_settings = None
old_throttle = None
initial_check_done = False
active_ally = 0


def write():
    (OUT / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")


def call(obj, name, *args):
    obj.call_method(name, args=args)


def stimulus(name, now, **data):
    report["stimuli"].append({"name": name, "game_time": now, **data})
    write()


def stage(name, now):
    global phase, phase_time
    phase, phase_time = name, now


def place(actor, point, facing=None, hidden=False):
    actor.set_actor_location(point, False, False)
    actor.set_actor_hidden_in_game(hidden)
    if facing is not None:
        rot = unreal.MathLibrary.find_look_at_rotation(point, facing)
        actor.set_actor_rotation(rot, False)
        c = unreal.AIHelperLibrary.get_ai_controller(actor)
        if actor == player:
            c = unreal.GameplayStatics.get_player_controller(player,0)
        if c:
            c.set_control_rotation(rot)


def complete():
    global phase
    levels.editor_request_end_play()
    phase = "end"


def finish():
    global callback
    if perf_settings is not None:
        perf_settings.set_editor_property("bThrottleCPUWhenNotForeground", old_throttle)
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    for entry in report["captures"]:
        entry["exists"] = (OUT/entry["file"]).is_file()
    report["status"] = "pass_formal_" + SCENARIO + "_bounded_acceptance" if not report["errors"] and report["protected_guards_unchanged"] else "failed_acceptance_preserve"
    if frame_intervals:
        values = sorted(frame_intervals)
        report["observed_cadence"] = {"count": len(values), "median_game_seconds": values[len(values)//2],
                                      "maximum_game_seconds": max(values), "long_frame_requested": LONG_FRAME,
                                      "benchmark_fps_acceptance": False}
    write()
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def live_navigation(world):
    # Public object iterator avoids the Python CLASS lookup's CDO world-context
    # ensure and does not bypass World's protected NavigationSystem property.
    matches = [obj for obj in unreal.ObjectIterator(unreal.NavigationSystemV1)
               if "Default__" not in obj.get_path_name() and obj.get_outer() == world]
    assert len(matches) == 1, ("Require one actual PIE navigation instance", [obj.get_path_name() for obj in matches])
    return matches[0]


def projected_body(pawn, point):
    unreal.log("ACCEPT_NAV_API instance_begin")
    world=editor.get_game_world()
    nav=live_navigation(world)
    unreal.log("ACCEPT_NAV_API instance_end")
    assert nav and "Default__" not in nav.get_path_name(),"Require the actual live world navigation system"
    unreal.log("ACCEPT_NAV_API project_begin")
    value=nav.call_method("K2_ProjectPointToNavigation",args=(world,point,None,None,unreal.Vector(200,200,200)))
    unreal.log("ACCEPT_NAV_API project_end")
    if isinstance(value,tuple):
        assert not any(isinstance(x,bool) and not x for x in value),("Projection rejected",xyz(point))
        value=next((x for x in value if isinstance(x,unreal.Vector)),None)
    assert isinstance(value,unreal.Vector),("No projected point",xyz(point),str(value))
    capsule=pawn.get_component_by_class(unreal.CapsuleComponent)
    body=value+unreal.Vector(0,0,capsule.get_scaled_capsule_half_height())
    report.setdefault("fixture_projections",[]).append({"pawn":pawn.get_actor_label(),"raw":xyz(point),"ground":xyz(value),"body":xyz(body)})
    return body


def park_nonparticipants():
    # Three distinct, original settled roster/anchor sites; never guess a far
    # coordinate beyond measured floor coverage. Hidden bodies keep collision.
    sites=(saved_homes[3],saved_homes[4],saved_homes[1])
    for actor,site in zip(roster[2:],sites):
        place(actor,unreal.Vector(*site),hidden=True)


def boundary_fixture(now):
    global previous,before_switch
    a,c=roster[active_ally],ctrls[active_ally]
    call(c,"PC_EnableCombat",False)
    call(c,"PC_PolicyHold")
    start=player_point+direction*(750 if SCENARIO=="radius" else -400)-side*200
    target=player_point+direction*(1600 if SCENARIO=="radius" else 900)
    place(a,projected_body(a,start),target)
    place(roster[2],target,hidden=False)
    report.setdefault("fixture_paths",[]).append(path_check(a,player_point+direction*(1250 if SCENARIO=="radius" else 550)-side*200))
    call(c,"PC_EnableCombat",True)
    assert prop(c,"FormationSlot")==0,"Sequential boundary fixture requires naturally released slot0"
    before_switch=[]
    previous=[]
    stimulus("individual_original_ally_boundary_fixture",now,ally=active_ally,start=xyz(a.get_actor_location()),target=xyz(target),generation=prop(a,"RestoreGeneration"))
    stage("boundary",now)


def path_check(pawn, raw_goal):
    goal=projected_body(pawn,raw_goal)
    world=editor.get_game_world()
    nav=live_navigation(world)
    unreal.log("ACCEPT_NAV_API path_begin")
    path = nav.call_method("FindPathToLocationSynchronously",args=(world,pawn.get_actor_location(),goal,pawn,None))
    unreal.log("ACCEPT_NAV_API path_end")
    assert path and path.is_valid() and not path.is_partial(), ("Fixture path unavailable", pawn.get_actor_label(), xyz(goal))
    points = list(prop(path, "path_points"))
    assert points and hypot(points[-1].x-goal.x, points[-1].y-goal.y) <= 50
    return {"pawn": pawn.get_actor_label(), "raw_goal":xyz(raw_goal),"goal": xyz(goal), "path": [xyz(p) for p in points]}


def capture(now, name, entries):
    # Independent unpaused locomotion diagnostics, not a stopped motion proof.
    pc=unreal.GameplayStatics.get_player_controller(player,0)
    eye=origin+direction*700+side*120+unreal.Vector(0,0,100)
    target=origin+direction*200+unreal.Vector(0,0,-20)
    review_camera.set_actor_location(eye,False,False)
    review_camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(eye,target),False)
    pc.set_view_target_with_blend(review_camera,0)
    path=OUT/(name+".png")
    unreal.SystemLibrary.execute_console_command(player,'Shot -nosuffix filename="'+path.as_posix()+'"',pc)
    report["captures"].append({"file":path.name,"request_game_time":now,"frozen":False,"npc_states":entries[:2],"full_motion_acceptance":False})


def role_goal_diagnostic(i):
    pawn=roster[i]
    raw=unreal.Vector(*saved_homes[i])
    world=editor.get_game_world()
    nav=live_navigation(world)
    path=nav.call_method("FindPathToLocationSynchronously",args=(world,pawn.get_actor_location(),raw,pawn,None))
    points=[xyz(p) for p in prop(path,"path_points")] if path else []
    capsule=pawn.get_component_by_class(unreal.CapsuleComponent)
    hit=unreal.SystemLibrary.sphere_trace_single(pawn,pawn.get_actor_location(),raw,
        capsule.get_scaled_capsule_radius(),unreal.TraceTypeQuery.ECC_VISIBILITY,False,
        [pawn],unreal.DrawDebugTrace.NONE,True)
    hit_data=hit[1].to_tuple() if isinstance(hit,tuple) else hit.to_tuple()
    blocker=hit_data[9]
    return {"native_anchor":xyz(raw),"actual_body":xyz(pawn.get_actor_location()),
            "projected_body":xyz(projected_body(pawn,raw)),
            "raw_path_valid":bool(path and path.is_valid()),"raw_path_partial":bool(path and path.is_partial()),
            "raw_path_points":points,"capsule_radius":capsule.get_scaled_capsule_radius(),
            "center_sphere_visibility_blocker":blocker.get_actor_label() if blocker else None,
            "move_status":str(ctrls[i].get_move_status()),
            "policy_goal":xyz(prop(ctrls[i],"PolicyGoal")),
            "scope":"Read-only path/projection and center-sphere collision diagnostic, not complete capsule clearance"}


def start_unreachable(now):
    call(ctrls[2],"PC_SetSearchRole",True,unreal.Vector(10000000,10000000,10000000),200.0)
    stimulus("unreachable_formal_role_destination",now)
    stage("unreachable",now)


def sample(now):
    global previous, previous_time
    entries = []
    for i, (a, c, b) in enumerate(zip(roster, ctrls, boards)):
        pos = xyz(a.get_actor_location())
        item = {"npc": i, "team": prop(a, "TeamId"), "position": pos, "speed": a.get_velocity().length(),
                "health": prop(a, "Health"), "loaded": prop(a, "LoadedAmmo"), "reserve": prop(a, "ReserveAmmo"),
                "shots": prop(a, "ShotSequence"), "generation": prop(a, "RestoreGeneration"),
                "shot_outcome":str(prop(a,"ShotOutcome")),
                "task": b.get_value_as_int("TaskID"), "request": b.get_value_as_int("RequestID"),
                "visible": b.get_value_as_bool("HasVisibleTarget"), "target": str(b.get_value_as_object("TargetActor")),
                "last_seen": xyz(b.get_value_as_vector("LastSeenPosition")), "retry": b.get_value_as_int("RetryCount"),
                "reason": str(b.get_value_as_name("WaitingReason")), "reply": str(prop(c, "ActionReplyReason")),
                "action": str(prop(a, "ActionState")), "combat_phase": str(prop(c, "CombatPhase")),
                "squad_mode": str(prop(c, "SquadMode")), "reservation": prop(c, "SquadReservationID"),
                "slot": prop(c, "FormationSlot"), "goal": xyz(prop(c, "HeldGoal")),
                "episode": prop(c, "ChaseEpisode"), "chase": prop(c, "ChaseActive"),
                "travel": prop(c, "ChaseDistance"), "player_distance": dist(pos, xyz(player.get_actor_location())),
                "search": prop(c, "SearchActive"), "deadline": prop(c, "PolicyDeadline"),
                "search_index": prop(c, "SearchIndex"), "visited": prop(c, "SearchVisitedCount"),
                "policy_state": str(prop(c, "PolicyState")),
                "left_foot_relative": xyz(a.mesh.get_socket_location("foot_l") - a.get_actor_location()),
                "right_foot_relative": xyz(a.mesh.get_socket_location("foot_r") - a.get_actor_location())}
        assert item["loaded"] + item["reserve"] + item["shots"] == 18, item
        assert item["speed"] <= 300.01, item
        if previous and now > previous_time:
            assert dist(pos, previous[i]) <= 600*(now-previous_time)+15, ("Movement discontinuity", item)
        entries.append(item)
    previous, previous_time = [x["position"] for x in entries], now
    report["samples"].append({"phase": phase, "game_time": now, "roster": entries, "player_health": prop(player, "Health"),
                              "player_forward":xyz(player.get_actor_forward_vector()),
                              "world_frame_seconds":unreal.GameplayStatics.get_world_delta_seconds(player)})
    if phase in ("boundary","replacement"):
        observer=roster[active_ally]
        target=roster[3 if phase=="replacement" else 2]
        sensor=observer.get_component_by_class(unreal.PawnSensingComponent)
        hit=unreal.SystemLibrary.line_trace_single(observer,observer.get_actor_eyes_view_point()[0],
                target.get_actor_eyes_view_point()[0],unreal.TraceTypeQuery.ECC_VISIBILITY,
                False,[observer],unreal.DrawDebugTrace.NONE,True)
        hit_data=hit[1].to_tuple() if isinstance(hit,tuple) else hit.to_tuple()
        blocker=hit_data[9]
        eyes,eye_rot=observer.get_actor_eyes_view_point()
        eye_delta=target.get_actor_eyes_view_point()[0]-eyes
        sensor_delta=target.get_actor_location()-eyes
        report["samples"][-1]["boundary_sight"]={
            "actor_rotation":str(observer.get_actor_rotation()),
            "controller_rotation":str(ctrls[active_ally].get_control_rotation()),
            "target_position":xyz(target.get_actor_location()),
            "sight_radius":prop(sensor,"sight_radius"),
            "eye_rotation":str(eye_rot),
            "target_eye_distance":eye_delta.length(),
            "eye_forward_dot_target":unreal.MathLibrary.get_forward_vector(eye_rot).dot(eye_delta)/max(eye_delta.length(),.0001),
            "native_sensor_actor_forward_dot_target":observer.get_actor_forward_vector().dot(sensor_delta)/max(sensor_delta.length(),.0001),
            "peripheral_vision_angle":prop(sensor,"peripheral_vision_angle"),
            "controller_los":ctrls[active_ally].line_of_sight_to(target),
            "visibility_blocker":blocker.get_actor_label() if blocker else None}
    if len(report["samples"]) % 10 == 0:
        write()
    return entries


def tick(delta):
    global phase, phase_time, next_sample, roster, ctrls, boards, player, policy, coord, origin, player_point
    global saved_homes, previous, previous_time, episode, before_switch, memory, initial, retained
    global perf_settings, old_throttle, initial_check_done, patrol_origin, review_camera, blockers, active_ally
    try:
        assert time.monotonic()-started < 205, (phase, "Overall timeout")
        if phase == "loading":
            return
        if phase == "setup":
            assert len(rows) == 703 and guards_match(rows)
            assert unreal.load_class(None, "/Script/ParisEditorBridge.ParisBlueprintAuthoring") is None
            # Installed EditorEngine uses this setting for background throttling.
            # In-memory only; restore on exit. Measure cadence, do not infer FPS.
            perf_settings = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings"))
            old_throttle = prop(perf_settings, "bThrottleCPUWhenNotForeground")
            perf_settings.set_editor_property("bThrottleCPUWhenNotForeground", False)
            phase = "loading"
            assert levels.load_level(MAP)
            lookup = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            origin = lookup[LABELS[0]].get_actor_location()
            if SCENARIO in ("travel","radius"):
                # NavigationAI coverage_v2 uses the midpoint X of the two saved
                # Allies as the measured connected street center. The old west
                # offset selected an elevated/disconnected surface, not this lane.
                second=lookup[LABELS[1]].get_actor_location()
                origin=unreal.Vector((origin.x+second.x)/2,origin.y,origin.z)
            player_point = origin + direction*400
            if SCENARIO=="radius":
                # Same proven eastern walking segment; the player is farther
                # south so the near-radius crossing occurs within that segment.
                player_point=origin-direction*400
            # Hidden finite roster cannot shoot during its first native bootstrap.
            for label in (*LABELS, "PC_City_Player"):
                lookup[label].set_actor_hidden_in_game(True)
            if SCENARIO == "roles":
                review_camera=actors.spawn_actor_from_class(unreal.CameraActor,origin,unreal.Rotator())
                review_camera.set_actor_label("NPCI_AcceptanceReviewCamera")
            if SCENARIO == "blocked":
                for i,offset in enumerate((-220,0,220)):
                    obstacle=actors.spawn_actor_from_class(unreal.StaticMeshActor,origin+direction*200+side*offset,unreal.Rotator())
                    obstacle.static_mesh_component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cube"))
                    obstacle.static_mesh_component.set_collision_profile_name("BlockAll")
                    obstacle.set_actor_scale3d(unreal.Vector(2.4,1.5,2))
                    obstacle.set_actor_label("NPCI_AcceptanceBlocker"+str(i))
            levels.editor_request_begin_play()
            stage("wait", 0)
            return
        world = editor.get_game_world()
        if phase == "end":
            if world is None:
                finish()
            return
        if world is None:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if phase == "wait":
            if now < 3:
                return
            lookup = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)}
            roster = [lookup[label] for label in LABELS]
            player = unreal.GameplayStatics.get_player_character(world, 0)
            ctrls = [unreal.AIHelperLibrary.get_ai_controller(a) for a in roster]
            boards = [prop(c, "blackboard") for c in ctrls]
            report["equipment"] = ready_snapshot(world, roster)
            assert len(set(c.get_path_name() for c in ctrls)) == 5
            assert all(prop(a, "Health") == 100 and prop(a, "ShotSequence") == 0 for a in roster)
            policy = lookup["PC_City_FriendlyFirePolicy"]
            coord = lookup["PC_City_SquadCoordinator"]
            blockers=[a for label,a in lookup.items() if label.startswith("NPCI_AcceptanceBlocker")]
            if SCENARIO=="roles":
                review_camera=lookup["NPCI_AcceptanceReviewCamera"]
            assert sum(a.get_class() == policy.get_class() for a in lookup.values()) == 1
            assert sum(a.get_class() == coord.get_class() for a in lookup.values()) == 1
            report["checks"]["selected_five_formal_bootstraps_private_brains_single_policies_finite_initial_roster"] = True
            saved_homes = [xyz(prop(c,"GuardAnchor")) for c in ctrls]
            report["role_anchors"]={"native_guard_anchors":saved_homes,
                                    "settled_starting_bodies":[xyz(a.get_actor_location()) for a in roster]}
            for c in ctrls:
                call(c, "PC_EnableCombat", False)
                call(c, "PC_EnablePolicy", False)
                call(c, "PC_PolicyHold")
            if LONG_FRAME:
                unreal.SystemLibrary.execute_console_command(world, "t.MaxFPS 4")
            if SCENARIO.startswith("combat_"):
                call(policy, "PC_SetFriendlyFire", SCENARIO == "combat_on")
                place(player, origin-direction*350, origin+direction*700)
                for i, a in enumerate(roster):
                    p = origin + side*(200*i if i < 2 else 200*(i-3)) + direction*(0 if i < 2 else 700)
                    place(a, p, origin+direction*(700 if i < 2 else 0))
                    call(ctrls[i], "PC_EnablePolicy", True)
                    call(ctrls[i], "PC_EnableCombat", True)
                initial = [prop(a, "ShotSequence") for a in roster]
                stimulus("six_finite_crowded_native_combat", now, ff=SCENARIO == "combat_on", player=xyz(player.get_actor_location()), positions=[xyz(a.get_actor_location()) for a in roster])
                stage("combat", now)
            else:
                # Negative equipment admission isolates movement without replacing
                # guns or disabling the inherited formal policy/squad services.
                for c in ctrls:
                    call(c, "PC_ConfigureNPCEquipment", False, False)
                park_nonparticipants()
                place(player, player_point, player_point+direction*100)
                if SCENARIO in ("roles","blocked"):
                    player_point = origin+direction*800
                    place(player, player_point, player_point+direction*100)
                for i in (0, 1):
                    base = origin if SCENARIO in ("roles","blocked") else player_point-direction*400
                    place(roster[i], base+side*(-200 if i == 0 else 200), player_point+direction*100)
                    if SCENARIO not in ("travel","radius"):
                        call(ctrls[i], "PC_EnableCombat", True)
                if SCENARIO in ("travel","radius"):
                    call(ctrls[1],"PC_EnableSquad",False)
                    place(roster[1],unreal.Vector(*saved_homes[2]),hidden=True)
                    boundary_fixture(now)
                else:
                    stage("blocked" if SCENARIO=="blocked" else "follow", now)
                stimulus("finite_noncombat_admission_fixture", now, positions=[xyz(a.get_actor_location()) for a in roster], player=xyz(player.get_actor_location()))
            previous = []
            next_sample = now
            return
        if now < next_sample:
            return
        next_sample = now+.05
        if previous_time:
            frame_intervals.append(now-previous_time)
        data = sample(now)
        if phase == "combat":
            for item in data:
                i = item["npc"]
                assert item["team"]==(0 if i<2 else 1),"Faction changed during combat"
                assert item["shot_outcome"]!="Friendly hit",("Autonomous AI fired into a friendly lane",item)
                sensed=boards[i].get_value_as_object("TargetActor")
                if item["visible"] and sensed is not None:
                    assert prop(sensed,"TeamId")!=item["team"],"AI selected a friendly target"
                if item["health"] <= 0:
                    if i not in dead:
                        dead[i] = (now, item["shots"], item["position"])
                    else:
                        when, shots, pos = dead[i]
                        assert item["shots"] == shots
                        if now-when > .75:
                            assert item["speed"] == 0 and dist(pos,item["position"]) <= 1 and item["reservation"] == 0
                else:
                    assert i not in dead, "Unrequested resurrection"
            if now-phase_time >= 18:
                shots = [sum(x["shots"]-initial[x["npc"]] for x in data if x["team"] == team) for team in (0,1)]
                assert all(x > 0 for x in shots) and dead, data
                report["summary"] = {"faction_shots": shots, "dead_npcs": len(dead), "ff_enabled": prop(policy,"FriendlyFireEnabled"), "player_health": prop(player,"Health")}
                report["checks"]["crowded_six_native_combat_conservation_death_release_no_resurrection"] = True
                report["checks"]["observed_autonomous_friend_lane_avoidance_factions_unchanged_no_friendly_target"] = True
                complete()
        elif phase in ("boundary", "replacement"):
            assert player.get_actor_forward_vector().dot(direction)>.999,"Player controller heading differs from fixture path geometry"
            for i in (active_ally,):
                x=data[i]
                assert x["travel"] <= 1000, x
                if x["squad_mode"] == "Chase":
                    assert x["player_distance"] <= 1000, x
                if x["chase"] and not episode:
                    episode = [prop(c,"ChaseEpisode") for c in ctrls[:2]]
                if i not in cutoffs and x["squad_mode"] == "Regroup" and (x["travel"] >= 850 if SCENARIO == "travel" else x["player_distance"] >= 900):
                    cutoffs[i] = x
            current=data[active_ally]
            if SCENARIO == "travel" and phase == "boundary" and current["travel"] >= 300:
                before_switch = [{"episode":current["episode"], "travel":current["travel"]}]
                old = roster[2].get_actor_location()
                place(roster[2],unreal.Vector(*saved_homes[3]),hidden=True)
                place(roster[3], old, hidden=False)
                stimulus("visible_hostile_replacement_same_goal", now, before=before_switch, point=xyz(old))
                previous = []
                stage("replacement", now)
            if phase == "replacement" and boards[active_ally].get_value_as_object("TargetActor") == roster[3] and boards[active_ally].get_value_as_bool("HasVisibleTarget"):
                for before,x in zip(before_switch,[current]):
                    assert x["episode"] == before["episode"] and x["travel"] >= before["travel"], x
                report["checks"]["real_native_target_switch_preserves_episode_and_budget_ally"+str(active_ally)] = True
            if active_ally in cutoffs:
                if SCENARIO == "travel":
                    assert report["checks"].get("real_native_target_switch_preserves_episode_and_budget_ally"+str(active_ally))
                report["summary"]["cutoffs"] = cutoffs
                park_nonparticipants()
                previous=[]
                stimulus("park_finite_hostiles_after_individual_cutoff", now,ally=active_ally,
                         positions=[xyz(a.get_actor_location()) for a in roster[2:]])
                stage("regroup", now)
            else:
                assert now-phase_time < 18, ("Cutoff not exercised", data[:2])
        elif phase == "regroup":
            x=data[active_ally]
            if dist(x["position"],x["goal"])>55:
                assert x["chase"] and x["travel"]>=cutoffs[active_ally]["travel"],"Budget reset before actual regroup arrival"
            if not x["chase"] and x["travel"] == 0 and dist(x["position"],x["goal"]) <= 55:
                assert x["player_distance"] <= 600 and x["reservation"] > 0
                report["checks"]["actual_cutoff_and_physical_regroup_ally"+str(active_ally)] = True
                report["summary"].setdefault("regroup_errors_cm",{})[active_ally]=dist(x["position"],x["goal"])
                if active_ally==0:
                    # Finite isolation, not gameplay respawn: first body dies
                    # through original damage, second gets one original reset
                    # to release its old slot1 generation before the same-lane test.
                    call(roster[0],"PC_ApplyDamage",1000.0)
                    call(roster[1],"PC_ResetLifecycle")
                    call(ctrls[1],"PC_EnableSquad",True)
                    call(ctrls[1],"PC_EnableCombat",True)
                    active_ally=1
                    stage("next_ally",now)
                    return
                if LONG_FRAME:
                    actual_long=sum(s["world_frame_seconds"]>=.20 and any(x["squad_mode"]=="Chase" for x in s["roster"][:2]) for s in report["samples"])
                    assert actual_long>=5,("Too few actual long chase frames",actual_long)
                    report["summary"]["actual_long_chase_frames"]=actual_long
                    report["checks"]["declared_quarter_second_frames_actual_chase_below_1000cm"] = True
                complete()
            else:
                assert now-phase_time < 18, ("Regroup failed", data[:2])
        elif phase=="next_ally":
            if prop(coord,"Owner0") == ctrls[1] and prop(ctrls[1],"FormationSlot")==0:
                boundary_fixture(now)
            else:
                assert now-phase_time<3,"Native death/reset did not release old owners for the second independent fixture"
        elif phase == "follow":
            moving=[x for x in data[:2] if x["speed"]>100]
            if moving and not report["captures"]:
                assert all((pp:=a.mesh.get_post_process_instance()) and prop(pp,"Evaluations")>0 and prop(pp,"ValidInput") and prop(pp,"ProtectionError")<.0001 for a in roster[:2])
                capture(now,"allied_walk_early",data)
            elif moving and len(report["captures"])==1 and now-report["captures"][0]["request_game_time"]>=.6:
                capture(now,"allied_walk_later",data)
            if all(x["reservation"] > 0 and dist(x["position"],x["goal"]) <= 55 for x in data[:2]):
                retained = [x["reservation"] for x in data[:2]]
                assert len(set(retained)) == 2 and dist(data[0]["goal"],data[1]["goal"]) >= 150
                report["checks"]["formal_two_allied_distinct_reserved_body_arrivals"] = True
                capture(now,"allied_arrived",data)
                stage("idle", now)
            else:
                assert now-phase_time < 15, data[:2]
        elif phase == "idle" and now-phase_time >= 1:
            assert [x["reservation"] for x in data[:2]] == retained
            slot = data[0]["slot"]
            call(roster[0],"PC_ApplyDamage",1000.0)
            report["summary"]["dead_slot"] = slot
            stimulus("original_allied_death",now,slot=slot,reservations=retained)
            stage("release",now)
        elif phase == "release" and now-phase_time >= 1:
            slot = report["summary"]["dead_slot"]
            assert data[0]["reservation"] == 0 and prop(coord,"Owner"+str(slot)) is None and prop(coord,"RID"+str(slot)) == 0
            assert data[1]["reservation"] == retained[1]
            report["checks"]["formal_idle_retention_death_release_survivor_identity"] = True
            call(ctrls[1],"PC_EnableCombat",False)
            call(ctrls[1],"PC_EnableSquad",False)
            call(ctrls[1],"PC_PolicyHold")
            player.set_actor_hidden_in_game(True)
            player.set_actor_location(unreal.Vector(*saved_homes[1]),False,False)
            target_point = origin+direction*650
            place(roster[1],target_point,hidden=False)
            for i in (2,3,4):
                place(roster[i],unreal.Vector(*saved_homes[i]),target_point)
                call(ctrls[i],"PC_EnablePolicy",True)
                call(ctrls[i],"PC_EnableCombat",True)
                call(ctrls[i],"PC_SetSearchRole",i==4,origin+direction*200,200.0)
            stimulus("formal_three_german_native_sight_fixture",now,target=xyz(target_point))
            previous=[]
            stage("acquire",now)
        elif phase == "acquire":
            if all(b.get_value_as_object("TargetActor")==roster[1] and b.get_value_as_bool("HasVisibleTarget") for b in boards[2:]):
                memory=[x["last_seen"] for x in data[2:]]
                place(roster[1],unreal.Vector(*saved_homes[0]),hidden=True)
                stimulus("hide_and_move_actual_target_once",now,memory=memory)
                previous=[]
                stage("search",now)
            else:
                assert now-phase_time<6,("German sensing fixture failed",data[2:])
        elif phase == "search":
            for i,x in enumerate(data[2:]):
                assert dist(x["last_seen"],memory[i]) < .001, x
                assert x["search_index"] <= 5 and x["retry"] <= 2, x
                if x["search"] and i not in searches:
                    searches[i]={"start":now,"deadline":x["deadline"]}
                    assert 14.5 <= x["deadline"]-now <= 15.1
                if i in searches:
                    assert abs(x["deadline"]-searches[i]["deadline"]) < .001
            if len(searches)==3 and all(not x["search"] for x in data[2:]):
                assert all(now <= x["deadline"]+1 for x in data[2:])
                report["summary"]["searches"]=[{**searches[i],"end":now,"visited":x["visited"]} for i,x in enumerate(data[2:])]
                report["checks"]["formal_three_private_frozen_memory_finite_search_no_new_deadline"] = True
                stage("roles_return",now)
            else:
                assert now-phase_time < 24, data[2:]
        elif phase == "roles_return":
            errors=[dist(x["position"],saved_homes[i]) for i,x in enumerate(data) if i in (2,3)]
            diagnostics=report.setdefault("role_goal_diagnostics",{})
            for i in (2,3):
                if data[i]["speed"]==0 and data[i]["reason"]=="Arrived" and dist(data[i]["position"],saved_homes[i])>55 and str(i) not in diagnostics:
                    diagnostics[str(i)]=role_goal_diagnostic(i)
            if all(x<=55 for x in errors) and data[4]["policy_state"]=="RolePatrol":
                report["summary"]["guard_return_errors_cm"]=errors
                report["checks"]["formal_guard_physical_return_and_patrol_resume"] = True
                patrol_origin=data[4]["position"]
                stage("patrol_roundtrip",now)
            else:
                if now-phase_time>=20:
                    report["summary"]["guard_return_errors_cm"]=errors
                    report["checks"]["formal_guard_physical_return_and_patrol_resume"]=False
                    report["errors"].append("Role-return body gate failed: "+str(errors))
                    stage("patrol_roundtrip",now)
        elif phase == "patrol_roundtrip":
            x=data[4]
            expected="destination" if len(patrol_visits)==1 else "home"
            goal=xyz(origin+direction*200) if expected=="destination" else saved_homes[4]
            if len(patrol_visits)<3 and dist(x["position"],goal)<=55:
                patrol_visits.append(expected)
            if len(patrol_visits)==3:
                report["summary"]["patrol_physical_order"]=patrol_visits
                report["checks"]["formal_german_physical_home_destination_home_roundtrip"] = True
                start_unreachable(now)
            else:
                if now-phase_time>=20:
                    report["checks"]["formal_german_physical_home_destination_home_roundtrip"]=False
                    report["summary"]["patrol_physical_order"]=patrol_visits
                    report["errors"].append("Patrol physical roundtrip gate failed: "+str(patrol_visits))
                    start_unreachable(now)
        elif phase == "unreachable":
            x=data[2]
            assert x["retry"]<=2,x
            if x["reason"]=="PathExhausted" and x["retry"]==2:
                report["summary"]["unreachable_position"]=x["position"]
                stage("exhausted_hold",now)
            else:
                assert now-phase_time<10,("Unreachable goal not bounded",x)
        elif phase == "exhausted_hold" and now-phase_time>=2:
            x=data[2]
            assert x["retry"]==2 and x["reason"]=="PathExhausted" and x["speed"]==0 and dist(x["position"],report["summary"]["unreachable_position"])<=1,x
            report["checks"]["formal_unreachable_two_replans_then_stable_wait_no_teleport"] = True
            complete()
        elif phase == "blocked":
            assert len(blockers)==3 and all(x["retry"]<=2 for x in data[:2]),data[:2]
            arrived=all(x["reservation"]>0 and dist(x["position"],x["goal"])<=55 for x in data[:2])
            failed=all(prop(c,"SquadFailed") for c in ctrls[:2])
            if arrived or failed:
                report["summary"]["blocked_response"]={"actual_arrival":arrived,"bounded_failed_wait":failed,"seconds":now-phase_time,"retries":[x["retry"] for x in data[:2]],"positions":[x["position"] for x in data[:2]]}
                if failed:
                    assert all(x["reservation"]==0 and x["speed"]==0 for x in data[:2]),data[:2]
                for obstacle in blockers:
                    obstacle.set_actor_enable_collision(False)
                    obstacle.set_actor_hidden_in_game(True)
                # A new player assignment is explicit recovery, not a hidden
                # reset of exhausted requests for an unchanged destination.
                place(player,player_point+direction*250,player_point+direction*500)
                stimulus("remove_blockers_and_new_player_assignment_once",now)
                stage("blocked_recovery",now)
            else:
                assert now-phase_time<30,("Blocked move did not resolve",data[:2])
        elif phase == "blocked_recovery":
            if all(x["reservation"]>0 and dist(x["position"],x["goal"])<=55 for x in data[:2]):
                assert dist(data[0]["goal"],data[1]["goal"])>=150
                report["summary"]["recovery_seconds"]=now-phase_time
                report["checks"]["two_formal_allied_obstacle_response_and_new_assignment_recovery"] = True
                complete()
            else:
                assert now-phase_time<15,("New assignment recovery failed",data[:2])
    except Exception:
        report["errors"].append(traceback.format_exc())
        write()
        try:
            complete()
        except Exception:
            finish()


callback = unreal.register_slate_post_tick_callback(tick)
write()
