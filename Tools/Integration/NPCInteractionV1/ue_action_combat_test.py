"""Fresh selected-policy equipment and actual identified actions; no pose driver."""
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

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "action_combat_runtime.json"
rows = guard_rows()
VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "checks": {},
          "samples": [], "equipment": [], "map_saved": False,
          "scope": "identified Stop/Turn/original Fire/Reload with selected native policies; not autonomous decision or visual motion acceptance"}
phase = "setup"
started = time.monotonic()
callback = None
roster = []
index = 0
shooter = target = friend = ctrl = bb = wall = policy = None
policy_class = None
point = direction = side = None
request_id = 0
before = stop_point = reload_commit = ammo_total = None
cancel_ids = cancel_tokens = cancel_ammo = None
phase_time = 0


def prop(a, n):
    return a.get_editor_property(n)


def xyz(v):
    return [v.x, v.y, v.z]


def state(a):
    return {n: str(prop(a, n)) if n in ("ActionState", "ShotOutcome") else prop(a, n)
            for n in ("LoadedAmmo", "ReserveAmmo", "ShotSequence", "Health", "RestoreGeneration", "ActionState", "ShotOutcome", "ActionID", "ReloadActionID", "ReloadGeneration")}


def request(action):
    global request_id
    request_id += 1
    tid, gen = bb.get_value_as_int("TaskID"), prop(shooter, "RestoreGeneration")
    return send(action, tid, request_id, gen)


def send(action, tid, rid, gen):
    ctrl.call_method("PC_RequestNPCAction", args=(action, tid, rid, gen))
    receipt = {"team": prop(shooter, "TeamId"), "action": action, "task": tid,
               "request": rid, "generation": gen,
               "result": str(prop(ctrl, "ActionReplyResult")), "reason": str(prop(ctrl, "ActionReplyReason")),
               "reply_ids": [prop(ctrl, n) for n in ("ReplyTaskID", "ReplyRequestID", "ReplyGeneration")],
               "body": xyz(shooter.get_actor_location()), "state": state(shooter), "target_health": prop(target, "Health")}
    report["samples"].append(receipt)
    assert receipt["reply_ids"] == [tid, rid, gen], receipt
    return receipt


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_selected_faction_original_actions" if not report["errors"] else "failed_action_combat_preserve"
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def equipment(world, soldier):
    adapters = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.ParisNPCGripActor)
                if prop(a, "Target") == soldier]
    assert len(adapters) == 1, (soldier.get_name(), len(adapters))
    adapter = adapters[0]
    gun = prop(soldier, "WeaponAppearance")
    pp = soldier.mesh.get_post_process_instance()
    team = prop(soldier, "TeamId")
    expected = "/Game/ParisCombat/Animation/" + ("AlliedGripV15/DA_PC_AlliedGripV16" if team == 0 else "GermanGripV14/DA_PC_GermanGripV11")
    assert prop(adapter, "BindingConfig") == unreal.load_asset(expected)
    assert prop(adapter, "Initialized") and not str(prop(adapter, "BindingError")) and prop(adapter, "NativeUpdates") > 0
    assert pp and prop(pp, "ValidInput") and prop(pp, "Evaluations") > 0
    assert gun and prop(gun, "GripMesh") == soldier.mesh and prop(gun, "Combatant") == soldier
    mesh = gun.get_component_by_class(unreal.StaticMeshComponent)
    report["equipment"].append({"team": team, "class": soldier.get_class().get_path_name(),
        "gun_class": gun.get_class().get_path_name(), "mesh": prop(mesh, "static_mesh").get_path_name(),
        "config": expected, "postprocess": pp.get_class().get_path_name(), "native_updates": prop(adapter, "NativeUpdates"),
        "component_collision": str(mesh.get_collision_enabled()), "actor_collision": gun.get_actor_enable_collision()})
    # Actor disable is an effective collision gate even if a component's stored
    # profile reports QueryAndPhysics. Record both; never rewrite the fixture.
    assert not gun.get_actor_enable_collision() or mesh.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION, report["equipment"][-1]


def prepare(now):
    global shooter, target, friend, ctrl, bb, phase, phase_time, stop_point
    for i, a in enumerate(roster):
        a.call_method("PC_ResetLifecycle")
        a.set_actor_location(point + direction * (2500 + i * 250) + side * 1500, False, False)
    shooter, target, friend = (roster[0], roster[2], roster[1]) if index == 0 else (roster[2], roster[0], roster[3])
    shooter.set_actor_location(point, False, False)
    target.set_actor_location(point + direction * 700, False, False)
    # Face the hostile so native PawnSensing can acquire it; Turn is then tested
    # with a one-time body rotation after observation, not a fabricated BB target.
    rotation = unreal.MathLibrary.find_look_at_rotation(point, target.get_actor_location())
    shooter.set_actor_rotation(rotation, False)
    ctrl = unreal.AIHelperLibrary.get_ai_controller(shooter)
    ctrl.set_control_rotation(rotation)
    bb = prop(ctrl, "blackboard")
    stop_point = xyz(shooter.get_actor_location())
    phase, phase_time = "acquire", now


def tick(delta):
    global phase, phase_time, roster, point, direction, side, wall, policy, policy_class, before, index, ammo_total, reload_commit, callback, stop_point, cancel_ids, cancel_tokens, cancel_ammo
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
            end = anchors["PC_City_Ally2"].get_actor_location()
            direction = unreal.MathLibrary.normal(end - point)
            direction.z = 0
            direction = unreal.MathLibrary.normal(direction)
            side = unreal.Vector(-direction.y, direction.x, 0)
            player = anchors["PC_City_Player"]
            player.set_actor_location(point + side * 2500, False, False)
            for a in list(anchors.values()):
                if a.get_actor_label().startswith(("PC_City_Ally", "PC_City_Enemy")):
                    actors.destroy_actor(a)
            for i in range(5):
                prefix = "BP_PCAlliedActionGate" if i < 2 else "BP_PCGermanActionGate"
                a = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + prefix + VERSION),
                    point + side * (1000 + 200 * i), unreal.Rotator())
                a.set_actor_label("NPCI_Combat_" + str(i))
            wall = actors.spawn_actor_from_class(unreal.StaticMeshActor, point + side * 4000, unreal.Rotator())
            wall.set_actor_label("NPCI_Wall")
            wall.static_mesh_component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cube"))
            wall.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            wall.static_mesh_component.set_collision_profile_name("BlockAll")
            wall.set_actor_scale3d(unreal.Vector(1.5, 1.5, 3))
            policy_class = unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCFriendlyFirePolicyV1")
            policies = unreal.GameplayStatics.get_all_actors_of_class(editor.get_editor_world(), policy_class)
            assert len(policies) <= 1, "Duplicate friendly-fire policies"
            if not policies:
                assert actors.spawn_actor_from_class(policy_class, point + side * 4000, unreal.Rotator())
            levels.editor_request_begin_play()
            phase = "wait"
            return
        world = editor.get_game_world()
        if phase == "wait":
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            all_actors = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)}
            roster = [all_actors["NPCI_Combat_" + str(i)] for i in range(5)]
            wall = all_actors["NPCI_Wall"]
            # Resolve the editor-only Blueprint class BEFORE PIE; the runtime
            # query uses that retained class, not an editor asset API in play.
            policies = unreal.GameplayStatics.get_all_actors_of_class(world, policy_class)
            assert len(policies) == 1
            policy = policies[0]
            policy.call_method("PC_SetFriendlyFire", args=(False,))
            for a in roster:
                c = unreal.AIHelperLibrary.get_ai_controller(a)
                c.call_method("PC_ConfigureNPCEquipment", args=(True, True))
                equipment(world, a)
            report["checks"]["both_selected_native_policies_bind_five_B_subclasses"] = True
            prepare(now)
            return
        if phase == "end":
            if world is None:
                finish()
            return
        report["samples"].append({"phase": phase, "team": prop(shooter, "TeamId"), "state": state(shooter),
            "drift_cm": dist(stop_point, xyz(shooter.get_actor_location())), "reply": str(prop(ctrl, "ActionReplyResult"))})
        if phase == "acquire":
            if bb.get_value_as_object("TargetActor") == target and bb.get_value_as_bool("HasVisibleTarget"):
                assert request("Stop")["result"] == "Started"
                # Measure from actual admitted stop, not earlier placement:
                # each faction settles its own capsule height on the city floor.
                stop_point = xyz(shooter.get_actor_location())
                phase, phase_time = "stop", now
            else:
                assert now - phase_time < 5, ("native acquisition", bb.get_value_as_object("TargetActor"))
        elif phase == "stop":
            assert dist(stop_point, xyz(shooter.get_actor_location())) <= 1
            if str(prop(ctrl, "ActionReplyResult")) == "Completed":
                shooter.set_actor_rotation(unreal.Rotator(yaw=shooter.get_actor_rotation().yaw + 45), False)
                assert request("Fire")["reason"] == "BodyNotFacingTarget"
                assert request("Turn")["reason"] == "BodyFacingObserved"
                phase, phase_time = "settle", now
            else:
                assert now - phase_time < 3
        elif phase == "settle" and now - phase_time >= .6:
            before = state(shooter)
            receipt = request("Fire")
            assert receipt["result"] == "Completed", receipt
            assert prop(shooter, "ShotSequence") == before["ShotSequence"] + 1
            assert prop(shooter, "LoadedAmmo") == before["LoadedAmmo"] - 1
            assert prop(target, "Health") == 65, receipt
            friend.set_actor_location(point + direction * 350, False, False)
            phase, phase_time = "friendly", now
        elif phase == "friendly" and now - phase_time >= .4:
            before = state(shooter)
            receipt = request("Fire")
            assert receipt["result"] == "Rejected", receipt
            assert state(shooter) == before and prop(target, "Health") == 65 and prop(friend, "Health") == 100
            policy.call_method("PC_SetFriendlyFire", args=(True,))
            assert prop(policy, "FriendlyFireEnabled")
            assert request("Fire")["result"] == "Rejected"
            assert state(shooter) == before and prop(target, "Health") == 65 and prop(friend, "Health") == 100
            report["checks"]["AI_friend_lane_rejection_FF_off_on_team_" + str(prop(shooter, "TeamId"))] = True
            policy.call_method("PC_SetFriendlyFire", args=(False,))
            friend.set_actor_location(point + side * 2000, False, False)
            wall.set_actor_location(point + direction * 350, False, False)
            phase, phase_time = "wall", now
        elif phase == "wall" and now - phase_time >= .4:
            before = state(shooter)
            assert request("Fire")["result"] == "Rejected"
            assert state(shooter) == before and prop(target, "Health") == 65
            wall.set_actor_location(point + side * 4000, False, False)
            phase, phase_time = "reacquire", now
        elif phase == "reacquire":
            if bb.get_value_as_object("TargetActor") == target and bb.get_value_as_bool("HasVisibleTarget") and now - phase_time > .6:
                assert request("Fire")["result"] == "Completed"
                assert prop(target, "Health") == 30 and prop(shooter, "LoadedAmmo") == 0
                ammo_total = prop(shooter, "LoadedAmmo") + prop(shooter, "ReserveAmmo")
                reload_commit = prop(shooter, "ReloadCommitCount")
                assert request("Reload")["result"] == "Started"
                phase, phase_time = "reload", now
            else:
                assert now - phase_time < 5
        elif phase == "reload":
            assert prop(shooter, "LoadedAmmo") + prop(shooter, "ReserveAmmo") == ammo_total
            if str(prop(ctrl, "ActionReplyResult")) == "Completed":
                assert str(prop(ctrl, "ActionReplyReason")) == "OriginalReloadReadyOneCommitConserved"
                assert prop(shooter, "ReloadCommitCount") == reload_commit + 1
                assert prop(shooter, "LoadedAmmo") == 8 and prop(shooter, "ReserveAmmo") == 8
                report["checks"]["allied" if index == 0 else "german"] = True
                tid, gen = bb.get_value_as_int("TaskID"), prop(shooter, "RestoreGeneration")
                completed = state(shooter)
                assert send("Reload", tid, request_id, gen)["reason"] == "AlreadyObserved"
                shooter.call_method("PC_CommitReload", args=(prop(shooter, "ReloadActionID"), prop(shooter, "ReloadGeneration")))
                shooter.call_method("PC_EndReload", args=(prop(shooter, "ReloadActionID"), prop(shooter, "ReloadGeneration")))
                assert state(shooter) == completed and prop(shooter, "ReloadCommitCount") == reload_commit + 1
                report["checks"]["completed_reload_duplicate_no_second_commit_team_" + str(prop(shooter, "TeamId"))] = True
                phase, phase_time = "cancel_prepare", now
            else:
                assert now - phase_time < 12, ("reload", str(prop(ctrl, "ActionReplyReason")))
        elif phase == "cancel_prepare" and now - phase_time >= .6:
            assert request("Fire")["result"] == "Completed"
            assert prop(target, "Health") == 0 and prop(shooter, "LoadedAmmo") == 7
            admitted = request("Reload")
            assert admitted["result"] == "Started"
            cancel_ids = admitted["reply_ids"]
            cancel_tokens = (prop(shooter, "ReloadActionID"), prop(shooter, "ReloadGeneration"))
            cancel_ammo = (prop(shooter, "LoadedAmmo"), prop(shooter, "ReserveAmmo"), prop(shooter, "ShotSequence"), prop(shooter, "ReloadCommitCount"))
            ctrl.call_method("PC_SetPatrol", args=(True, point + direction * 900))
            prop(ctrl, "brain_component").restart_logic()
            phase, phase_time = "cancel_reload", now
        elif phase == "cancel_reload":
            if bb.get_value_as_int("TaskID") != cancel_ids[0] and str(prop(ctrl, "ActionReplyResult")) != "Started":
                assert str(prop(ctrl, "ActionReplyResult")) == "Cancelled" and str(prop(ctrl, "ActionReplyReason")) == "TaskSuperseded"
                assert [prop(ctrl, n) for n in ("ReplyTaskID", "ReplyRequestID", "ReplyGeneration")] == cancel_ids
                assert str(prop(shooter, "ActionState")) == "Ready"
                ctrl.call_method("PC_PolicyHold")
                shooter.call_method("PC_CommitReload", args=cancel_tokens)
                shooter.call_method("PC_EndReload", args=cancel_tokens)
                phase, phase_time = "late_reload", now
            else:
                assert now - phase_time < 5, ("task supersession", str(prop(ctrl, "ActionReplyReason")))
        elif phase == "late_reload":
            assert (prop(shooter, "LoadedAmmo"), prop(shooter, "ReserveAmmo"), prop(shooter, "ShotSequence"), prop(shooter, "ReloadCommitCount")) == cancel_ammo
            if now - phase_time > prop(shooter, "ReloadDuration") + .75:
                report["checks"]["task_supersedes_real_reload_late_tokens_no_commit_team_" + str(prop(shooter, "TeamId"))] = True
                index += 1
                if index < 2:
                    prepare(now)
                else:
                    phase = "end"
                    levels.editor_request_end_play()
    except Exception:
        report["errors"].append(traceback.format_exc())
        finish()


callback = unreal.register_slate_post_tick_callback(tick)
