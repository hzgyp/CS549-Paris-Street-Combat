"""Disposable full-domain Recast export and independent native Character tests."""
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path(os.environ["CS549_PURE_ROOT"])
OUT = Path(os.environ["CS549_PURE_OUT"])
PROFILE = os.environ.get("CS549_PURE_PROFILE", "Early")
PREVIOUS = os.environ.get("CS549_PURE_PREVIOUS", "")
assert PROFILE in ("Early", "FixedSurvey")
sys.path.insert(0, str(ROOT / "Tools/Integration/NPCInteractionV1"))
sys.path.insert(0, str(OUT))
from common import guard_rows, guards_match, digest
from pure_map_graph import build, components
from vehicle_prefix import verify as verify_vehicle_prefix
SOURCE = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/inventory_v4_20261007/inventory.json"
inventory = json.loads(SOURCE.read_text(encoding="utf-8"))
assert inventory["status"] == "pass_p0_inventory_only" and inventory["protected_bytes_unchanged"]
rows = guard_rows()
assert len(rows) == 703 and guards_match(rows)
guard_snapshot = OUT / "guards_before.json"
guard_snapshot.write_text(json.dumps(rows)+"\n", encoding="utf-8")
binary_authority = ROOT / "Docs/Development/RecoilV1/AUTHORIZED_LOCAL_BINARIES_20261007.json"
helper_binary = ROOT / "Unreal/ParisStreetCombat/Plugins/ParisMapSurveyV1/Binaries/Win64/UnrealEditor-ParisMapSurveyV1.dll"
report = {"identity": OUT.name, "status": "initializing", "phase": "setup", "errors": [],
          "execution_profile": PROFILE, "not_fps_or_visual_acceptance": True,
          "current_guards": 703, "inventory_sha256": digest(SOURCE), "map_saved": False,
          "guards_before_sha256": digest(guard_snapshot), "helper_sha256": digest(helper_binary),
          "recoil_local_binary_authority_sha256": digest(binary_authority) if binary_authority.exists() else None,
          "nav_rebuild_scope": "unsaved isolated test world only", "original_assets_preserved": True,
          "positions_are_temporary_tests": True, "movement_driver": "native CharacterMovement + AIController MoveTo",
          "cases": [], "initializations": [], "completions": [], "removed": [], "captures": [],
          "control_cases": [], "surface_controls": [], "batch_wall_budget_seconds": 3000,
          "vehicle_controls": [], "environment_fixture_version": "static_vehicle_v1",
          "surface_sampling_version": "native_specific_polygon_surface_v2",
          "profile": {"radius_cm": 34, "half_height_cm": 96.5, "step_cm": 35, "slope_degrees": 45,
                      "speed_cm_s": 600, "acceleration_cm_s2": 2048, "gravity_scale": 1,
                      "early_time_dilation": 1, "broad_time_dilation": 4, "max_frame_seconds": .1,
                      "arrival_xy_cm": 30, "measurement_margin_cm": 5, "foot_height_error_cm": 35}}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
spawn_api = unreal.get_default_object(unreal.GameplayStatics)
started = time.monotonic()
phase = "setup"
callback = None
busy = False
world = nav = nav_data = probe = controller = graph = None
perf = gm = saving = None
old_settings = {}
vehicles = []
vehicle_origins = {}
vehicle_snapshots = {}
case_index = 0
control_index = 0
current = None
stamp = sample_stamp = 0
blocked_sources = {}
prior_source_provenance = {}
remote_negative_cache = {}
observer = None
mesh_asset = animation_class = None


def xyz(v): return [float(v.x), float(v.y), float(v.z)]


def vehicle_snapshot(vehicle):
    values = {"actor_location_cm": xyz(vehicle.get_actor_location()),
        "actor_rotation": [float(getattr(vehicle.get_actor_rotation(), k)) for k in ("pitch", "yaw", "roll")], "actor_scale": xyz(vehicle.get_actor_scale3d()), "components": []}
    channels = [getattr(unreal.CollisionChannel, n) for n in dir(unreal.CollisionChannel)
                if isinstance(getattr(unreal.CollisionChannel, n), unreal.CollisionChannel)
                and "MAX" not in n.upper() and "DEPRECATED" not in n.upper()]
    for c in vehicle.get_components_by_class(unreal.PrimitiveComponent):
        origin, extent, _ = unreal.SystemLibrary.get_component_bounds(c)
        item = {"component": c.get_path_name(), "location_cm": xyz(c.get_world_location()),
            "rotation": [float(getattr(c.get_world_rotation(), k)) for k in ("pitch", "yaw", "roll")], "scale": xyz(c.get_world_scale()),
            "bounds_origin_cm": xyz(origin), "bounds_extent_cm": xyz(extent),
            "collision": str(c.get_collision_enabled()), "profile": str(c.get_collision_profile_name()),
            "responses": {str(ch): str(c.get_collision_response_to_channel(ch)) for ch in channels}}
        if isinstance(c, unreal.SkeletalMeshComponent):
            mesh = c.get_editor_property("skeletal_mesh_asset")
            asset = c.get_editor_property("physics_asset_override") or (mesh.get_editor_property("physics_asset") if mesh else None)
            item.update({"mesh": mesh.get_path_name() if mesh else None,
                         "physics_asset": asset.get_path_name() if asset else None})
        values["components"].append(item)
    return values


def freeze_environment_vehicle(vehicle):
    before = vehicle_snapshot(vehicle)
    vehicle.set_actor_tick_enabled(False)
    for c in vehicle.get_components_by_class(unreal.ActorComponent):
        c.set_component_tick_enabled(False)
        if isinstance(c, unreal.MovementComponent): c.deactivate()
        if isinstance(c, unreal.PrimitiveComponent):
            c.set_simulate_physics(False)
            if isinstance(c, unreal.SkeletalMeshComponent): c.set_all_bodies_simulate_physics(False)
    after = vehicle_snapshot(vehicle)
    assert before == after, "Static vehicle freeze changed collision geometry"
    assert all(not c.is_simulating_physics() for c in vehicle.get_components_by_class(unreal.PrimitiveComponent))
    vehicle_snapshots[vehicle.get_path_name()] = after
    report.setdefault("static_vehicle_admission", []).append({"before": before, "after": after,
        "collision_geometry_exact": True, "simulation_disabled": True, "max_drift_cm": 0.})


def clean_cache_interruption(path, prior):
    stop_path = path / "STOP_REQUEST.json"
    if path.name != "fixed_surface_v10_20261007" or not stop_path.exists(): return False
    stop_text = stop_path.read_text(encoding="utf-8-sig")
    stop = json.loads(stop_text)
    return (stop.get("kind") == "preserve_unchanged_prior_source_rejections" and
        stop.get("sources") == ["region_03541", "region_03573"] and
        prior["errors"] == ["Owned stop request: " + stop_text] and
        prior["summary"]["failed_cases"] == 0 and prior["status"] == "failed_api_or_isolation_gate")


def clean_remote_interruption(path, prior):
    stop_path = path / "STOP_REQUEST.json"
    if path.name != "fixed_static_vehicle_v18_20261007" or not stop_path.exists(): return False
    stop_text = stop_path.read_text(encoding="utf-8-sig")
    stop = json.loads(stop_text)
    return (stop.get("kind") == "preserve_remote_negative_after_quarantined_prefix" and
        stop.get("cases") == ["case_11637"] and prior["errors"] == ["Owned stop request: " + stop_text] and
        prior["environment_fixture_version"] == "static_vehicle_v1" and prior["static_vehicle_admission"][0]["max_drift_cm"] == 0 and
        prior["resume_control_gate"] == "pass_two_native_legs" and prior["status"] == "failed_api_or_isolation_gate")


def checkpoint():
    report["phase"] = phase
    report["elapsed_wall_seconds"] = time.monotonic()-started
    report["completed_cases"] = len(report["cases"])
    report["summary"] = {"planned_cases": len(graph["cases"]) if graph else None,
        "completed_cases": len(report["cases"]), "passed_cases": sum(c.get("status") == "passed" for c in report["cases"]),
        "standing_passes": sum(c.get("status") == "standing_passed" for c in report["cases"]),
        "failed_cases": sum(c.get("status") not in ("passed", "standing_passed") for c in report["cases"]),
        "full_physical_acceptance": False}
    (OUT / "survey.json").write_text(json.dumps(report, separators=(",", ":"))+"\n", encoding="utf-8")


def teardown_probe():
    global probe, controller, observer
    if controller and unreal.SystemLibrary.is_valid(controller):
        if observer: controller.receive_move_completed.remove_callable(observer)
        assert unreal.ParisMapSurveyLibrary.destroy_survey_probe(probe, controller), "Exact native owned-probe cleanup required"
    elif probe and unreal.SystemLibrary.is_valid(probe):
        assert probe.get_class() == unreal.Character.static_class()
        probe.destroy_actor()
    probe = controller = observer = None


def finish(error=None):
    global phase
    if error: report["errors"].append(error)
    if levels.is_in_play_in_editor():
        try: teardown_probe()
        except Exception: report["errors"].append("Cleanup: " + traceback.format_exc())
        levels.editor_request_end_play(); phase = "ending"; checkpoint(); return
    if perf: perf.set_editor_property("bThrottleCPUWhenNotForeground", old_settings["throttle"])
    if saving and "auto_save" in old_settings: saving.set_editor_property("bAutoSaveEnable", old_settings["auto_save"])
    if gm:
        for key in ("default_pawn_class", "hud_class"): gm.set_editor_property(key, old_settings[key])
    report["protected_bytes_unchanged"] = guards_match(rows)
    if not report["protected_bytes_unchanged"]: report["errors"].append("Protected source mismatch")
    phase = "done"
    report["status"] = ("failed_api_or_isolation_gate" if report["errors"] else
        "bounded_normal_time_probe_lifecycle_pass" if PROFILE == "Early" else
        "partial_finite_clean_survey_batch" if report.get("batch_budget_stop") else
        "complete_finite_pure_map_survey_with_negative_edges_retained")
    checkpoint()
    if graph:
        passed = {(c["from"], c["to"]) for c in report["cases"] if c.get("status") == "passed"}
        covered = {node for edge in passed for node in edge}
        adjacency = {n: set() for n in sorted(covered)}
        for source, target in passed: adjacency[source].add(target)
        physical_groups = components(adjacency)
        report["physical_components"] = physical_groups
        report["physical_component_scope"] = "Evidence graph of passed-edge endpoints only; other regions are unknown, not proven disconnected"
        report["coverage"] = {"mapped_polygons": graph["polygon_count"], "total_polygons": graph["polygon_count"],
            "total_regions": len(graph["regions"]), "regions_on_passed_edges": len(covered),
            "physical_components": len(physical_groups), "all_scheduled_cases_finished": len(report["cases"]) == len(graph["cases"]),
            "regions_without_passed_edge_evidence": len(graph["regions"])-len(covered),
            "unmeasured_cases": len(graph["cases"])-len(report["cases"]),
            "regions_with_standing_check": len({c["from"] for c in report["cases"] if c.get("standing")}),
            "all_geometry_or_floor_access_proven": False}
        checkpoint()
    if callback is not None: unreal.unregister_slate_post_tick_callback(callback)
    unreal.SystemLibrary.quit_editor()


def live_nav(w):
    found = [n for n in unreal.ObjectIterator(unreal.NavigationSystemV1)
             if "Default__" not in n.get_path_name() and n.get_outer() == w]
    assert len(found) == 1, "One actual navigation receiver required"
    return found[0]


def isolate():
    global world, nav, nav_data, gm, perf, saving, vehicles, mesh_asset, animation_class
    assert unreal.EditorLevelLibrary.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
    world = editor.get_editor_world()
    for a in list(actors.get_all_level_actors()):
        path = a.get_class().get_path_name()
        if isinstance(a, unreal.Character) or path.startswith(("/Game/ParisCombat/", "/Script/Paris")) or "GripPolicy" in path:
            report["removed"].append({"label": a.get_actor_label(), "class": path})
            assert actors.destroy_actor(a)
    left = list(actors.get_all_level_actors())
    assert not any(isinstance(a, unreal.Character) for a in left)
    assert len(report["removed"]) == inventory["summary"]["removed_gameplay_actors"]
    for a in left:
        if isinstance(a, unreal.Pawn):
            assert a.get_class().get_path_name().startswith("/Game/WW2City/CarsSet/"), "Undeclared environment Pawn"
            a.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
            a.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.DISABLED)
    world.get_world_settings().set_editor_property("default_game_mode", unreal.GameModeBase.static_class())
    gm = unreal.get_default_object(unreal.GameModeBase)
    for key in ("default_pawn_class", "hud_class"):
        old_settings[key] = gm.get_editor_property(key); gm.set_editor_property(key, None)
    perf = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings"))
    old_settings["throttle"] = perf.get_editor_property("bThrottleCPUWhenNotForeground")
    perf.set_editor_property("bThrottleCPUWhenNotForeground", False)
    saving_class = unreal.load_class(None, "/Script/UnrealEd.EditorLoadingSavingSettings")
    assert saving_class, "Installed reflected loading/saving settings class required"
    saving = unreal.get_default_object(saving_class)
    old_settings["auto_save"] = saving.get_editor_property("bAutoSaveEnable")
    saving.set_editor_property("bAutoSaveEnable", False)
    mesh_asset = unreal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
    animation_class = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed")
    assert mesh_asset and animation_class, "Installed Epic default character dependency"
    nav = live_nav(world)
    volumes = [a for a in left if isinstance(a, unreal.NavMeshBoundsVolume)]
    meshes = [a for a in left if isinstance(a, unreal.RecastNavMesh)]
    assert len(volumes) == len(meshes) == 1
    nav_data = meshes[0]
    assert all(nav_data.get_editor_property(k) == v for k, v in
               (("agent_radius", 34.0), ("agent_height", 193.0), ("agent_max_slope", 45.0), ("tile_size_uu", 1000.0)))
    bounds = inventory["collision_bounds_cm"]
    lo = [bounds["min"][i]-(100 if i < 2 else 193) for i in range(3)]
    hi = [bounds["max"][i]+(100 if i < 2 else 193) for i in range(3)]
    center = [(a+b)/2 for a, b in zip(lo, hi)]
    extent = [(b-a)/2 for a, b in zip(lo, hi)]
    volumes[0].set_actor_location(unreal.Vector(*center), False, False)
    volumes[0].set_actor_scale3d(unreal.Vector(*(v/100 for v in extent)))
    nav.on_navigation_bounds_updated(volumes[0])
    actual_center, actual_extent = volumes[0].get_actor_bounds(False)
    assert max(abs(a-b) for a, b in zip(xyz(actual_center), center)) < .1
    assert max(abs(a-b) for a, b in zip(xyz(actual_extent), extent)) < .1
    report["test_bounds_cm"] = {"center": center, "extent": extent, "min": lo, "max": hi,
                               "actual_center": xyz(actual_center), "actual_extent": xyz(actual_extent),
                               "original_collision_bounds": bounds}


def assert_isolation():
    state = json.loads(unreal.ParisMapSurveyLibrary.inspect_survey_world(world))
    assert not state.get("error")
    assert state["characters"] == (1 if probe else 0), "Unexpected Character in pure-map world"
    assert state["ai_controllers"] == (1 if controller else 0), "Unexpected AI controller"
    assert not state["production_contaminants"], "Production actor contamination"
    report["last_native_isolation_state"] = state
    for vehicle in vehicles:
        assert vehicle.get_controller() is None
        if vehicle.get_path_name() in vehicle_origins:
            drift = (vehicle.get_actor_location()-unreal.Vector(*vehicle_origins[vehicle.get_path_name()])).length()
            report["static_vehicle_admission"][0]["max_drift_cm"] = max(drift, report["static_vehicle_admission"][0]["max_drift_cm"])
            assert drift <= 5, "Environment vehicle no longer stationary"
            assert vehicle_snapshot(vehicle) == vehicle_snapshots[vehicle.get_path_name()], "Static vehicle geometry/collision changed"
            assert all(not c.is_simulating_physics() for c in vehicle.get_components_by_class(unreal.PrimitiveComponent)), "Environment physics resumed"


def spawn_probe(spec):
    global probe, controller, observer, stamp
    teardown_probe()
    source = spec["source_cm"]
    t = unreal.Transform(location=unreal.Vector(source[0], source[1], source[2]+99.5))
    probe = spawn_api.call_method("BeginDeferredActorSpawnFromClass", args=(world, unreal.Character.static_class(), t,
        unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    assert probe
    probe.capsule_component.set_capsule_size(34, 96.5, True)
    probe.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
    probe.set_editor_property("ai_controller_class", unreal.AIController.static_class())
    movement = probe.character_movement
    movement.set_editor_property("max_walk_speed", 600)
    movement.set_editor_property("max_step_height", 35)
    movement.set_walkable_floor_angle(45)
    movement.set_editor_property("orient_rotation_to_movement", True)
    probe.set_editor_property("use_controller_rotation_yaw", False)
    probe.mesh.set_skeletal_mesh_asset(mesh_asset)
    probe.mesh.set_relative_location(unreal.Vector(0, 0, -96.5), False, False)
    probe.mesh.set_relative_rotation(unreal.Rotator(0, -90, 0), False, False)
    probe.mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    probe.mesh.set_anim_instance_class(animation_class)
    probe = spawn_api.call_method("FinishSpawningActor", args=(probe, t, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    controller = unreal.AIHelperLibrary.get_ai_controller(probe)
    assert controller and controller.get_class() == unreal.AIController.static_class()
    case_identifier = spec["id"]
    def completed(request_id, result):
        report["completions"].append({"case": case_identifier, "request_id": str(request_id), "result": str(result),
                                      "request_id_value": unreal.ParisMapSurveyLibrary.decode_request_id(request_id),
                                      "controller": controller.get_path_name(),
                                      "game_seconds": unreal.GameplayStatics.get_time_seconds(world)})
    observer = completed
    controller.receive_move_completed.add_callable(observer)
    stamp = unreal.GameplayStatics.get_time_seconds(world)
    report["initializations"].append({"case": spec["id"], "source_region": spec["from"], "body_cm": xyz(probe.get_actor_location()),
        "not_a_traversal": True, "game_seconds": stamp})
    assert_isolation()


def standing():
    body = probe.get_actor_location()
    floor = json.loads(unreal.ParisMapSurveyLibrary.survey_floor_state(probe))
    assert not floor.get("error"), "Native CurrentFloor observation required"
    overlaps = unreal.SystemLibrary.capsule_overlap_components(world, body, 34, 96.5,
        [unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1, unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY2], None, [probe])
    if isinstance(overlaps, tuple) and any(isinstance(item, bool) for item in overlaps):
        arrays = [item for item in overlaps if not isinstance(item, bool) and hasattr(item, "__iter__")]
        assert len(arrays) == 1, "Explicit CapsuleOverlap output array required"
        overlap_components = list(arrays[0])
    elif isinstance(overlaps, bool):
        assert not overlaps, "Blocking overlap without component output"
        overlap_components = []
    else:
        overlap_components = list(overlaps or [])
    assert all(isinstance(c, unreal.PrimitiveComponent) for c in overlap_components)
    blockers = [c.get_path_name() for c in overlap_components
                if c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN) == unreal.CollisionResponseType.ECR_BLOCK]
    source = current["source_cm"]
    foot = body.z-96.5
    return {"body_cm": xyz(body), "foot_z_cm": foot, "foot_error_cm": abs(foot-source[2]),
            "xy_cm": math.hypot(body.x-source[0], body.y-source[1]),
            "mode": str(probe.character_movement.get_editor_property("movement_mode")), "blockers": blockers,
            "native_floor": floor}


def reject_case(reason, extra=None):
    global phase, case_index
    current.update({"status": "failed", "reason": reason, **(extra or {})})
    if current.get("vehicle_admission_control"):
        report["vehicle_controls"].append(current)
        raise AssertionError("Static vehicle early route failed: " + reason)
    if current.get("surface_admission_control"):
        report["surface_controls"].append(current)
        raise AssertionError("Exact-poly surface calibration failed: " + reason)
    report["control_cases" if current.get("control_reproduction") else "cases"].append(current)
    if case_index < 2 or current.get("control_reproduction"): raise AssertionError("Early/control physical gate failed: " + reason)
    teardown_probe(); case_index += 1; phase = "next"
    if case_index % 25 == 0: checkpoint()


def tick(_delta):
    global phase, busy, world, nav, nav_data, graph, current, case_index, control_index, stamp, sample_stamp, vehicles
    if busy or phase == "done": return
    busy = True
    try:
        assert time.monotonic()-started < 3200, "Finite pure-map wall deadline"
        if (OUT / "STOP_REQUEST.json").exists() and phase != "ending":
            finish("Owned stop request: " + (OUT / "STOP_REQUEST.json").read_text(encoding="utf-8-sig")); return
        if phase == "ending":
            if editor.get_game_world() is None: finish()
            return
        if phase == "setup":
            isolate(); phase = "load_ready"; checkpoint(); return
        if phase == "load_ready":
            assert time.monotonic()-started < 600, "Finite wait for natural navigation unlock"
            state = json.loads(unreal.ParisMapSurveyLibrary.navigation_build_state(nav))
            assert not state.get("error")
            report["navigation_build_state"] = state
            if state["manual_build_locked"]: return
            registered = state["registered_bounds"]
            assert len(registered) == 1, "One registered disposable bounds required"
            assert max(abs(a-b) for a, b in zip(registered[0]["min_cm"], report["test_bounds_cm"]["min"])) < .1
            assert max(abs(a-b) for a, b in zip(registered[0]["max_cm"], report["test_bounds_cm"]["max"])) < .1
            report["generation_started_wall_seconds"] = time.monotonic()-started
            unreal.SystemLibrary.execute_console_command(world, "RebuildNavigation")
            phase = "generation"; checkpoint(); return
        if phase == "generation":
            assert time.monotonic()-started < 600, "Full-domain disposable generation deadline"
            if unreal.NavigationSystemV1.is_navigation_being_built(world): return
            if time.monotonic()-started-report["generation_started_wall_seconds"] < 3: return
            export = json.loads(unreal.ParisMapSurveyLibrary.export_navmesh(nav_data))
            assert export["polygons"], "Rebuild yielded no navigation surfaces"
            (OUT / "navmesh.json").write_text(json.dumps(export)+"\n", encoding="utf-8")
            graph = build(export)
            (OUT / "graph.json").write_text(json.dumps(graph)+"\n", encoding="utf-8")
            report["graph_summary"] = graph["summary"]
            report["graph_sha256"] = digest(OUT / "graph.json")
            report["navmesh_sha256"] = digest(OUT / "navmesh.json")
            if PROFILE == "FixedSurvey":
                historical_path = OUT.parent / "fixed_clean_v7_20261007/survey.json"
                historical = json.loads(historical_path.read_text())
                region_index = {r["id"]: r for r in graph["regions"]}
                report["prior_source_cache"] = []
                for identifier in ("case_07102", "case_07152"):
                    rejected = next(c for c in historical["cases"] if c["id"] == identifier)
                    assert rejected["reason"] == "source_not_safe_standing_surface"
                    source_delta = math.dist(region_index[rejected["from"]]["point_cm"], rejected["source_cm"])
                    assert source_delta <= .001, "Prior negative source must remain equivalent within10microns"
                    state = rejected["standing"]
                    assert state["blockers"] or state["xy_cm"] > 35 or state["foot_error_cm"] > 35
                    blocked_sources[rejected["from"]] = state
                    prior_source_provenance[rejected["from"]] = {"not_new_physical_attempt": True,
                        "prior_failure_identity": "fixed_clean_v7_20261007", "prior_failure_case": identifier,
                        "prior_failure_receipt_sha256": digest(historical_path), "prior_source_equivalence_cm": .001,
                        "prior_source_delta_cm": source_delta}
                    report["prior_source_cache"].append({"region": rejected["from"], "source_cm": rejected["source_cm"],
                        **prior_source_provenance[rejected["from"]]})
                baseline_path = OUT.parent / "early_static_vehicle_v17_20261007/survey.json"
                baseline = json.loads(baseline_path.read_text())
                assert baseline["status"] == "bounded_normal_time_probe_lifecycle_pass"
                assert baseline["protected_bytes_unchanged"] and len(baseline["cases"]) == 2
                assert all(c["status"] == "passed" for c in baseline["cases"])
                assert baseline["surface_sampling_gate"] == "pass_known_exact_poly_standing"
                assert baseline["environment_fixture_version"] == "static_vehicle_v1"
                assert baseline["vehicle_control_gate"] == "pass_native_near_vehicle"
                assert baseline["surface_sampling_version"] == graph["sampling_version"]
                prior_graph = json.loads((baseline_path.parent / "graph.json").read_text())
                assert graph["summary"] == prior_graph["summary"], "Fixed profile graph denominator changed"
                assert [(r["id"], r["tile"], r["point_cm"], r["z_range_cm"]) for r in graph["regions"]] == [(r["id"], r["tile"], r["point_cm"], r["z_range_cm"]) for r in prior_graph["regions"]], "Surface identity/profile reference mismatch"
                assert {(e["from"], e["to"]) for e in graph["directed_edges"]} == {(e["from"], e["to"]) for e in prior_graph["directed_edges"]}
                report["normal_time_reference_sha256"] = digest(baseline_path)
                if PREVIOUS:
                    prior_path = OUT.parent / PREVIOUS
                    prior = json.loads((prior_path / "survey.json").read_text())
                    prior_exit = json.loads((prior_path / "exit.json").read_text(encoding="utf-8-sig"))
                    cache_interruption = clean_cache_interruption(prior_path, prior) or clean_remote_interruption(prior_path, prior)
                    remote_prefix = PREVIOUS == "fixed_surface_v12_20261007"
                    prefix_count = len(prior["cases"])
                    if remote_prefix:
                        prefix_path = ROOT / "Docs/Development/MissionLoopV1/VEHICLE_REMOTE_PREFIX_RECEIPT_20261007.json"
                        verified, prefix_count = verify_vehicle_prefix(OUT.parent, prefix_path)
                        assert verified == prior
                        report["remote_prefix_admission_sha256"] = digest(prefix_path)
                        report["remote_prefix_retained_count"] = prefix_count
                        from vehicle_prefix import near_case
                        admission = json.loads(prefix_path.read_text())
                        for rejected in prior["cases"][prefix_count:]:
                            if rejected["status"] == "failed" and not near_case(rejected, admission["exclusion_xy_cm"]):
                                remote_negative_cache[rejected["id"]] = rejected
                    assert prior["execution_profile"] == PROFILE and (prior["status"] == "partial_finite_clean_survey_batch" or cache_interruption or remote_prefix)
                    assert (not prior["errors"] or cache_interruption or remote_prefix) and prior["protected_bytes_unchanged"]
                    assert prior_exit["exit_code"] == 0 and prior_exit["strict_log_errors"] == 0
                    assert prior["inventory_sha256"] == report["inventory_sha256"]
                    if not remote_prefix: assert prior["normal_time_reference_sha256"] == report["normal_time_reference_sha256"]
                    else: report["historical_normal_time_reference_sha256"] = prior["normal_time_reference_sha256"]
                    assert prior["helper_sha256"] == report["helper_sha256"] and prior["recoil_local_binary_authority_sha256"] == report["recoil_local_binary_authority_sha256"]
                    prior_graph = json.loads((prior_path / "graph.json").read_text())
                    assert [(r["id"], r["tile"], r["point_cm"], r["z_range_cm"]) for r in graph["regions"]] == [(r["id"], r["tile"], r["point_cm"], r["z_range_cm"]) for r in prior_graph["regions"]]
                    assert {(e["from"], e["to"]) for e in graph["directed_edges"]} == {(e["from"], e["to"]) for e in prior_graph["directed_edges"]}
                    assert [c["id"] for c in prior["cases"]] == [c["id"] for c in graph["cases"][:len(prior["cases"])]]
                    report["cases"] = prior["cases"][:prefix_count]
                    for c in report["cases"]:
                        c.setdefault("origin_run", PREVIOUS)
                        if c.get("reason") == "source_not_safe_standing_surface": blocked_sources[c["from"]] = c["standing"]
                    report["previous_identity"] = PREVIOUS
                    report["previous_receipt_sha256"] = digest(prior_path / "survey.json")
                    report["prior_batches"] = prior.get("prior_batches", []) + [PREVIOUS]
                    case_index = len(report["cases"])
            checkpoint(); levels.editor_request_begin_play(); phase = "runtime_ready"; return
        world = editor.get_game_world()
        if world is None: return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if phase == "runtime_ready":
            if now < 2: return
            nav = live_nav(world)
            vehicles = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Pawn)
                        if a.get_class().get_path_name().startswith("/Game/WW2City/CarsSet/")]
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Pawn):
                if a not in vehicles:
                    assert not isinstance(a, unreal.Character), "Production Character spawned"
                    report.setdefault("suppressed_native_bootstrap_pawns", []).append(a.get_class().get_path_name())
                    a.destroy_actor()
            assert_isolation()
            for vehicle in vehicles:
                freeze_environment_vehicle(vehicle)
                vehicle_origins[vehicle.get_path_name()] = xyz(vehicle.get_actor_location())
            report["environment_vehicle_origins_after_bootstrap"] = vehicle_origins.copy()
            report["runtime_isolation"] = {"original_characters": 0, "project_policies": 0, "environment_vehicles": len(vehicles)}
            report["runtime_isolation"].update({"project_gameplay_native_and_blueprint_actors": 0, "inheritance_scan": True})
            phase = "next"; checkpoint(); return
        if phase == "next":
            if PROFILE == "Early" and case_index == 2 and report["surface_controls"] and not report["vehicle_controls"]:
                current = dict(graph["cases"][11633]); current["samples"] = []
                current.update({"id": "vehicle_admission_case_11633", "vehicle_admission_control": True, "origin_run": OUT.name})
                assert current["kind"] == "movement"
                spawn_probe(current); phase = "standing"; return
            if PROFILE == "Early" and case_index == 2 and not report["surface_controls"]:
                r = next(r for r in graph["regions"] if r["id"] == "region_03597")
                assert abs(r["point_cm"][2]-r["raw_center_cm"][2]) > 35, "Known calibration must expose the old center discrepancy"
                current = {"id": "surface_admission_region_03597", "from": r["id"], "to": r["id"],
                    "source_cm": r["point_cm"], "goal_cm": r["point_cm"], "source_poly": r["representative_poly"],
                    "target_poly": r["representative_poly"], "kind": "standing_only", "samples": [],
                    "surface_admission_control": True, "raw_center_cm": r["raw_center_cm"], "origin_run": OUT.name}
                spawn_probe(current); phase = "standing"; return
            if case_index == (2 if PROFILE == "Early" else len(graph["cases"])): finish(); return
            if PROFILE == "FixedSurvey" and time.monotonic()-started >= 3000:
                report["batch_budget_stop"] = True; finish(); return
            is_control = bool(PREVIOUS) and control_index < 2
            current = dict(graph["cases"][control_index if is_control else case_index]); current["samples"] = []
            current["origin_run"] = OUT.name
            if is_control:
                current["control_reproduction"] = True
                current["id"] = "resume_control_" + current["id"]
            if current["from"] in blocked_sources:
                reject_case("source_previously_rejected_no_retry", {"standing": blocked_sources[current["from"]],
                    "not_new_physical_attempt": True, **prior_source_provenance.get(current["from"], {})}); return
            if current["id"] in remote_negative_cache:
                previous_case = remote_negative_cache[current["id"]]
                assert previous_case["source_cm"] == current["source_cm"] and previous_case["goal_cm"] == current["goal_cm"]
                reject_case("previously_rejected_remote_case_no_retry", {"not_new_physical_attempt": True,
                    "prior_failure_identity": "fixed_surface_v12_20261007", "prior_failure_case": previous_case["id"],
                    "prior_failure_reason": previous_case["reason"],
                    "prior_failure_receipt_sha256": digest(OUT.parent / "fixed_surface_v12_20261007/survey.json")}); return
            if (current["from"], current["to"]) == ("region_07016", "region_07024"):
                old_path = OUT.parent / "early_surface_v8_20261007/survey.json"
                old = json.loads(old_path.read_text())
                old_case = old["cases"][0]
                assert old_case["reason"] == "runtime_query_missing_or_partial"
                assert old_case["source_cm"] == current["source_cm"] and old_case["goal_cm"] == current["goal_cm"]
                reject_case("previously_rejected_exact_surface_query_no_retry", {"not_new_physical_attempt": True,
                    "prior_failure_identity": "early_surface_v8_20261007", "prior_failure_case": old_case["id"],
                    "prior_failure_receipt_sha256": digest(old_path)}); return
            unreal.GameplayStatics.set_global_time_dilation(world, 1 if case_index < 2 or is_control else 4)
            spawn_probe(current); phase = "standing"; return
        if phase == "standing":
            if now-stamp < .4: return
            state = standing(); current["standing"] = state
            if state["blockers"] or state["foot_error_cm"] > 35 or state["xy_cm"] > 35 or "WALKING" not in state["mode"].upper() or not state["native_floor"]["walkable_floor"]:
                blocked_sources[current["from"]] = state
                reject_case("source_not_safe_standing_surface", {"standing": state}); return
            if current["kind"] == "standing_only":
                current.update({"status": "standing_passed", "not_a_connectivity_edge": True})
                if current.get("surface_admission_control"):
                    report["surface_controls"].append(current)
                    report["surface_sampling_gate"] = "pass_known_exact_poly_standing"
                    teardown_probe(); phase = "next"; checkpoint(); return
                report["cases"].append(current)
                teardown_probe(); case_index += 1; phase = "next"
                if case_index % 25 == 0: checkpoint()
                return
            body = probe.get_actor_location()
            feet = unreal.Vector(body.x, body.y, body.z-96.5)
            path = nav.call_method("FindPathToLocationSynchronously", args=(world, feet,
                  unreal.Vector(*current["goal_cm"]), probe, None))
            if not path or not path.is_valid() or path.is_partial():
                reject_case("runtime_query_missing_or_partial"); return
            points = list(path.get_editor_property("path_points"))
            length = sum((b-a).length() for a, b in zip(points, points[1:]))
            current["path_cm"] = [xyz(p) for p in points]
            current["path_length_cm"] = length
            current["start_game_seconds"] = now
            current["deadline_game_seconds"] = max(8, length/600*2+5)
            request = controller.move_to_location(unreal.Vector(*current["goal_cm"]), acceptance_radius=30,
                stop_on_overlap=False, use_pathfinding=True, project_destination_to_navigation=False,
                can_strafe=False, allow_partial_path=False)
            current["request"] = str(request)
            if request != unreal.PathFollowingRequestResult.REQUEST_SUCCESSFUL:
                reject_case("native_request_not_started"); return
            current["request_id_value"] = unreal.ParisMapSurveyLibrary.current_request_id(controller)
            current["controller"] = controller.get_path_name()
            assert current["request_id_value"] > 0, "Started native request ID required"
            stamp = now; sample_stamp = now; phase = "moving"; return
        if phase == "moving":
            body = probe.get_actor_location(); goal = current["goal_cm"]
            xy = math.hypot(body.x-goal[0], body.y-goal[1]); dz = abs(body.z-96.5-goal[2])
            frame = unreal.GameplayStatics.get_world_delta_seconds(world)
            assert frame <= .1, "Declared simulation frame exceeded0.1s"
            if now >= sample_stamp:
                current["samples"].append({"game_seconds": now, "body_cm": xyz(body), "foot_z_cm": body.z-96.5,
                    "xy_cm": xy, "foot_error_cm": dz, "world_frame_seconds": frame,
                    "speed_cm_s": probe.get_velocity().length(), "mode": str(probe.character_movement.get_editor_property("movement_mode")),
                    "native_floor": json.loads(unreal.ParisMapSurveyLibrary.survey_floor_state(probe))})
                sample_stamp = now+.25
            events = [e for e in report["completions"] if e["case"] == current["id"]]
            if controller.get_move_status() == unreal.PathFollowingStatus.IDLE:
                if not events or "SUCCESS" not in events[-1]["result"].upper() or events[-1]["request_id_value"] != current["request_id_value"] or events[-1]["controller"] != current["controller"] or xy > 35 or dz > 35:
                    reject_case("native_completion_or_endpoint_failed", {"xy_cm": xy, "foot_error_cm": dz, "completion": events[-1:]}); return
                assert "WALKING" in str(probe.character_movement.get_editor_property("movement_mode")).upper(), "Arrival not grounded"
                final_floor = json.loads(unreal.ParisMapSurveyLibrary.survey_floor_state(probe))
                assert not final_floor.get("error") and final_floor["walkable_floor"], "Native arrival ground observation required"
                current.update({"status": "passed", "xy_cm": xy, "foot_error_cm": dz, "elapsed_game_seconds": now-stamp,
                                "final_body_cm": xyz(body), "completion": events[-1], "final_native_floor": final_floor})
                report["vehicle_controls" if current.get("vehicle_admission_control") else "control_cases" if current.get("control_reproduction") else "cases"].append(current)
                if case_index < 2 or current.get("control_reproduction"): checkpoint()
                teardown_probe(); phase = "next"
                if current.get("vehicle_admission_control"):
                    report["vehicle_control_gate"] = "pass_native_near_vehicle"; assert_isolation(); checkpoint(); return
                if current.get("control_reproduction"):
                    control_index += 1
                    if control_index == 2:
                        report["resume_control_gate"] = "pass_two_native_legs"; assert guards_match(rows); checkpoint()
                    return
                case_index += 1
                if case_index == 2:
                    report["normal_time_early_gate"] = "pass_two_native_legs"
                    assert guards_match(rows); checkpoint()
                elif case_index % 25 == 0:
                    assert_isolation(); checkpoint()
            elif now-stamp > current["deadline_game_seconds"]:
                reject_case("native_stall_deadline", {"xy_cm": xy, "foot_error_cm": dz})
    except Exception:
        finish(traceback.format_exc())
    finally:
        busy = False


callback = unreal.register_slate_post_tick_callback(tick)
