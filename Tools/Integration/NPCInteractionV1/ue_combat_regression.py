"""Shared FF actual-city regression; original transactions, existing native guns."""
import json
import os
import sys
import time
import traceback
from math import sqrt
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match
from ue_equipment_fixture import allied_config, stage_allied

OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "combat_regression.json"
VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
SELECTED = os.environ.get("CS549_NPC_MODE") == "selected_combat_regression"
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "cases": [], "errors": [], "map_saved": False,
          "scope": "player/Allied/German original native shot FF transaction regression; no grip/AI visual approval"}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
phase, started, phase_time = "setup", time.monotonic(), 0
callback = None
player = allies = germans = policy = wall = None
policy_class = None
origin = direction = perpendicular = yaw = None
index = 0
fixture = None
reload_started_game_time = 0
cases = [(role, enabled) for role in ("player", "allied", "german") for enabled in (False, True)]


def xyz(v):
    return [v.x, v.y, v.z]


def prop(a, name):
    return a.get_editor_property(name)


def state(a):
    return {n: prop(a, n) if n not in ("ActionState", "ShotOutcome") else str(prop(a, n))
            for n in ("Health", "TeamId", "LoadedAmmo", "ReserveAmmo", "ShotSequence", "ActionState", "ShotOutcome", "RestoreGeneration")}


def write():
    RESULT.write_text(json.dumps(report, indent=2) + "\n")


def finish():
    global callback
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["status"] = "pass_shared_ff_three_shooter_native_regression" if not report["errors"] else "failed_shared_ff_regression_preserve"
    write()
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def stage_gun(soldier, authored):
    assert prop(soldier, "WeaponAppearance") is None
    gun = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(authored["package"]), soldier.get_actor_location(), unreal.Rotator())
    gun.set_editor_property("Combatant", soldier)
    gun.set_editor_property("GripMesh", soldier.mesh)
    gun.set_owner(soldier)
    gun.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    assert gun.attach_to_component(soldier.mesh, "hand_r", unreal.AttachmentRule.KEEP_RELATIVE,
                                  unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
    soldier.set_editor_property("WeaponAppearance", gun)


def prepare(role, enabled):
    global fixture, reload_started_game_time
    roster = [player] + allies + germans
    for i, a in enumerate(roster):
        if SELECTED and i:
            controller = unreal.AIHelperLibrary.get_ai_controller(a)
            controller.call_method("PC_EnableCombat", args=(False,))
            controller.call_method("PC_PolicyHold")
        a.call_method("PC_ResetLifecycle")
        a.set_actor_location(origin + direction * (2000 + i * 250) + perpendicular * 1000, False, False)
    if role == "player":
        shooter, friendly, hostile = player, allies[0], germans[0]
    elif role == "allied":
        shooter, friendly, hostile = allies[0], allies[1], germans[0]
    else:
        shooter, friendly, hostile = germans[0], germans[1], allies[0]
    shooter.set_actor_location(origin, False, False)
    shooter.set_actor_rotation(yaw, False)
    controller = unreal.GameplayStatics.get_player_controller(shooter, 0) if role == "player" else unreal.AIHelperLibrary.get_ai_controller(shooter)
    controller.set_control_rotation(yaw)
    friendly.set_actor_location(origin + direction * 500, False, False)
    hostile.set_actor_location(origin + direction * 900, False, False)
    policy.call_method("PC_SetFriendlyFire", args=(enabled,))
    fixture = (role, enabled, shooter, friendly, hostile)
    # Lifecycle reset deliberately does not refill ammunition. Continue through
    # the original reload transaction, never write LoadedAmmo/ReserveAmmo.
    if prop(shooter, "LoadedAmmo") < 2:
        shooter.call_method("PC_RequestReload")
        assert str(prop(shooter, "ActionState")) == "Reloading"
        reload_started_game_time = unreal.GameplayStatics.get_time_seconds(shooter)


def shot(aim_at):
    role, enabled, shooter, friendly, hostile = fixture
    weapon = prop(shooter, "WeaponAppearance")
    assert weapon is not None
    eye = shooter.get_actor_location() + unreal.Vector(0, 0, 40)
    vector = aim_at.get_actor_location() + unreal.Vector(0, 0, 20) - eye
    vector = vector / max(vector.length(), .0001)
    muzzle = unreal.MathLibrary.transform_location(weapon.get_actor_transform(), unreal.Vector(0, 83.23, 0))
    before = [state(a) for a in (shooter, friendly, hostile)]
    shooter.call_method("PC_RequestFire", args=(eye, vector))
    after = [state(a) for a in (shooter, friendly, hostile)]
    entry = {"role": role, "friendly_fire": enabled, "before": before, "after": after,
             "origin": xyz(eye), "direction": xyz(vector), "muzzle": xyz(muzzle), "gun": weapon.get_class().get_path_name()}
    capsule = friendly.get_component_by_class(unreal.CapsuleComponent)
    entry["friendly_collision"] = {"position": xyz(friendly.get_actor_location()),
        "enabled": str(capsule.get_collision_enabled()), "visibility": str(capsule.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY)),
        "half_height_cm": capsule.get_scaled_capsule_half_height()}
    report["cases"].append(entry)
    write()
    return before, after


def begin_world_case():
    global phase, phase_time, reload_started_game_time
    shooter = fixture[2]
    wall.set_actor_location(origin + direction * 700 + unreal.Vector(0, 0, 60), False, False)
    if prop(shooter, "LoadedAmmo") == 0:
        shooter.call_method("PC_RequestReload")
        assert str(prop(shooter, "ActionState")) == "Reloading"
        reload_started_game_time = unreal.GameplayStatics.get_time_seconds(shooter)
    phase, phase_time = "world", time.monotonic() - started


def next_case():
    global index, phase, phase_time
    wall.set_actor_location(origin + perpendicular * 3000, False, False)
    index += 1
    if index == len(cases):
        report["friendly_modes_all_three_shooters"] = True
        levels.editor_request_end_play()
        phase = "end"
    else:
        prepare(*cases[index])
        phase, phase_time = "friendly", time.monotonic() - started


def tick(delta):
    global phase, phase_time, player, allies, germans, policy, policy_class, wall, origin, direction, perpendicular, yaw, index, reload_started_game_time
    try:
        elapsed = time.monotonic() - started
        assert elapsed < 190, "Combat regression timeout"
        if phase == "loading":
            return
        if phase == "setup":
            assert guards_match(rows)
            assert unreal.load_class(None, "/Script/ParisEditorBridge.ParisBlueprintAuthoring") is None
            report["editor_authoring_bridge_disabled"] = True
            if not SELECTED:
                imported = json.loads((STORE / "Evidence/GermanRifleUEV1/import_v3/result.json").read_text())
                authored = json.loads((STORE / "Evidence/GermanRifleUEV1/author_v2/result.json").read_text())
                for r in imported["native_files"] + authored["native_files"]:
                    assert (ROOT / r["path"]).stat().st_size == r["size_bytes"] and digest(ROOT / r["path"]) == r["sha256"]
            phase = "loading"
            assert levels.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
            anchors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
            if not SELECTED:
                allied_equipment = allied_config(anchors["PC_City_Ally1"])
            origin, destination = [anchors[n].get_actor_location() for n in ("PC_City_Ally1", "PC_City_Ally2")]
            lane = destination - origin
            direction = unreal.Vector(lane.x, lane.y, 0) / sqrt(lane.x**2 + lane.y**2)
            perpendicular = unreal.Vector(-direction.y, direction.x, 0)
            yaw = unreal.MathLibrary.find_look_at_rotation(origin, origin + direction * 500)
            for a in list(anchors.values()):
                if a.get_actor_label().startswith(("PC_City_Ally", "PC_City_Enemy")):
                    actors.destroy_actor(a)
            for team, count, prefix in ((0, 2, "BP_PCAlliedSquad"), (1, 3, "BP_PCGermanSquad")):
                if SELECTED:
                    prefix = "BP_PCAlliedCombat" if team == 0 else "BP_PCGermanCombat"
                cls = unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + prefix + VERSION)
                for i in range(count):
                    npc = actors.spawn_actor_from_class(cls, origin + perpendicular * (1000 + team * 800 + i * 180), yaw)
                    npc.set_actor_label("NPCI_Combat_" + str(team) + "_" + str(i))
                    if not SELECTED:
                        if team == 1:
                            stage_gun(npc, authored)
                        else:
                            report.setdefault("allied_fixture_equipment", []).append(stage_allied(npc, allied_equipment))
            # The formal map now has the one native global policy. Reuse it;
            # do not silently create a second competing policy for regression.
            policy_class = unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCFriendlyFirePolicyV1")
            existing = [a for a in actors.get_all_level_actors() if a.get_class() == policy_class]
            assert len(existing) <= 1, "Duplicate native friendly-fire policies"
            report["reused_saved_ff_policy"] = bool(existing)
            if not existing:
                a = actors.spawn_actor_from_class(policy_class, origin, unreal.Rotator())
                a.set_actor_label("NPCI_FriendlyFirePolicy")
            obstacle = actors.spawn_actor_from_class(unreal.StaticMeshActor, origin + perpendicular * 3000, yaw)
            obstacle.set_actor_label("NPCI_TransactionWall")
            obstacle.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            obstacle.static_mesh_component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cube.Cube"))
            obstacle.static_mesh_component.set_collision_profile_name("BlockAll")
            obstacle.set_actor_scale3d(unreal.Vector(.5, 4, 4))
            levels.editor_request_begin_play()
            phase = "wait"
            return
        if phase == "wait":
            world = editor.get_game_world()
            if world is None or unreal.GameplayStatics.get_time_seconds(world) < 3:
                return
            roster = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)}
            player = unreal.GameplayStatics.get_player_pawn(world, 0)
            allies = [roster["NPCI_Combat_0_" + str(i)] for i in range(2)]
            germans = [roster["NPCI_Combat_1_" + str(i)] for i in range(3)]
            if SELECTED:
                for a in allies + germans:
                    adapters = [x for x in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.ParisNPCGripActor)
                                if prop(x, "Target") == a]
                    assert len(adapters) == 1 and prop(adapters[0], "Initialized") and not str(prop(adapters[0], "BindingError"))
                    config = prop(adapters[0], "BindingConfig").get_path_name()
                    assert config.endswith("DA_PC_AlliedGripV16.DA_PC_AlliedGripV16" if prop(a, "TeamId") == 0
                                           else "DA_PC_GermanGripV11.DA_PC_GermanGripV11"), config
                    assert prop(a, "WeaponAppearance") and a.mesh.get_post_process_instance()
                    c = unreal.AIHelperLibrary.get_ai_controller(a)
                    c.call_method("PC_ConfigureNPCEquipment", args=(True, True))
                    assert not prop(a, "WeaponAppearance").get_actor_enable_collision()
                    report.setdefault("selected_equipment", []).append({"team": prop(a, "TeamId"), "config": config,
                        "gun": prop(a, "WeaponAppearance").get_class().get_path_name()})
                report["historical_manual_staging"] = False
            policies = unreal.GameplayStatics.get_all_actors_of_class(world, policy_class)
            assert len(policies) == 1
            policy = policies[0]
            wall = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor)
                        if a.get_actor_label() == "NPCI_TransactionWall")
            assert prop(policy, "FriendlyFireEnabled") is False
            report["six_character_roster"] = [a.get_class().get_path_name() for a in [player] + allies + germans]
            prepare(*cases[index])
            phase, phase_time = "friendly", elapsed
            return
        if phase == "end":
            if editor.get_game_world() is None:
                finish()
            return
        if elapsed - phase_time < .5:
            return
        role, enabled, shooter, friendly, hostile = fixture
        now = unreal.GameplayStatics.get_time_seconds(shooter)
        if phase in ("friendly", "world") and str(prop(shooter, "ActionState")) == "Reloading":
            assert now - reload_started_game_time < 8
            return
        # Wall time can advance during editor/shader stalls while game time is
        # clamped. Honor the original cooldown's actual clock, not a wall delay.
        if phase in ("friendly", "hostile", "dead_body", "world") and now < prop(shooter, "NextShotTime") + .05:
            return
        if phase == "friendly":
            before, after = shot(hostile)  # Friendly between shooter and enemy.
            assert before[0]["LoadedAmmo"] - after[0]["LoadedAmmo"] == 1
            assert after[0]["ShotSequence"] - before[0]["ShotSequence"] == 1
            assert after[0]["LoadedAmmo"] + after[0]["ReserveAmmo"] + after[0]["ShotSequence"] == 18
            assert before[2]["Health"] == after[2]["Health"], "Friendly did not block damage behind it"
            assert before[1]["Health"] - after[1]["Health"] == (35 if enabled else 0)
            assert after[0]["ShotOutcome"] == ("Friendly hit" if enabled else "Friendly blocked")
            assert [a["TeamId"] for a in before] == [a["TeamId"] for a in after]
            # Immediate duplicate request is rejected by existing cooldown.
            eye = shooter.get_actor_location() + unreal.Vector(0, 0, 40)
            d = hostile.get_actor_location() - eye
            shooter.call_method("PC_RequestFire", args=(eye, d / d.length()))
            assert prop(shooter, "ShotSequence") == after[0]["ShotSequence"]
            friendly.set_actor_location(origin + perpendicular * 1000, False, False)
            phase, phase_time = "hostile", elapsed
        elif phase == "hostile":
            before, after = shot(hostile)
            assert before[0]["LoadedAmmo"] - after[0]["LoadedAmmo"] == 1
            assert after[0]["LoadedAmmo"] + after[0]["ReserveAmmo"] + after[0]["ShotSequence"] == 18
            assert before[2]["Health"] - after[2]["Health"] == 35
            assert after[0]["ShotOutcome"] == "Hostile hit"
            if enabled:
                friendly.set_actor_location(origin + direction * 500, False, False)
                friendly.call_method("PC_ApplyDamage", args=(1000.0,))
                shooter.call_method("PC_RequestReload")
                assert str(prop(shooter, "ActionState")) == "Reloading"
                reload_started_game_time = now
                phase, phase_time = "dead_reload", elapsed
            else:
                begin_world_case()
        elif phase == "dead_reload":
            if str(prop(shooter, "ActionState")) == "Ready":
                assert prop(shooter, "LoadedAmmo") > 0
                phase, phase_time = "dead_body", elapsed
            else:
                assert now - reload_started_game_time < 8
        elif phase == "dead_body":
            before, after = shot(hostile)
            assert before[0]["LoadedAmmo"] - after[0]["LoadedAmmo"] == 1
            assert after[0]["LoadedAmmo"] + after[0]["ReserveAmmo"] + after[0]["ShotSequence"] == 18
            assert before[1]["Health"] == after[1]["Health"] == 0
            # Preserve original death/collision semantics: a corpse may no longer
            # intersect this standing-height ray. Do not invent a new tall wall.
            assert friendly.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION
            assert before[2]["Health"] - after[2]["Health"] == 35
            death_commits = prop(friendly, "ActionID")
            friendly.call_method("PC_ApplyDamage", args=(35.0,))
            assert prop(friendly, "Health") == 0 and prop(friendly, "ActionID") == death_commits
            report["cases"][-1]["dead_damage_entry_no_second_death"] = True
            begin_world_case()
        elif phase == "world":
            before, after = shot(hostile)
            assert before[0]["LoadedAmmo"] - after[0]["LoadedAmmo"] == 1
            assert after[0]["ShotSequence"] - before[0]["ShotSequence"] == 1
            assert after[0]["LoadedAmmo"] + after[0]["ReserveAmmo"] + after[0]["ShotSequence"] == 18
            assert before[1]["Health"] == after[1]["Health"] and before[2]["Health"] == after[2]["Health"]
            assert after[0]["ShotOutcome"] == "World blocked"
            report["cases"][-1]["unsaved_world_obstruction_verified"] = True
            next_case()
    except Exception:
        report["errors"].append(traceback.format_exc())
        write()
        try:
            levels.editor_request_end_play()
        except Exception:
            pass
        phase = "end"


callback = unreal.register_slate_post_tick_callback(tick)
write()
