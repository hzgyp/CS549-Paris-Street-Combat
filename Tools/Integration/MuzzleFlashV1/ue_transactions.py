"""Finite original transactions and native owner-aware rendering; no pose writer."""
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BASE, ROOT, INTAKE, guards, intake_rows, sha, write
from formal_contract import approved_profiles, PROFILE_PACKAGE, INTAKE_ID

OUT = BASE / os.environ["CS549_MUZZLE_ID"]
MODE = os.environ["CS549_MUZZLE_TRANSACTION_MODE"]
assert MODE in ("Api", "Transient", "SaveFresh", "Fresh", "Formal")
profiles = approved_profiles()
report = {"identity": OUT.name, "mode": MODE, "errors": [], "samples": [],
          "checks": {}, "captures": [], "profiles": profiles, "map_saved": False,
          "pose_writer": False, "ammo_property_writes": False, "private_configure_calls": 0,
          "capture_mechanism": "native_world_post_actor_deferred_twelve_unique_targets"}
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
callback = None
started = time.monotonic()
phase = "wait"
pending = None
scenario = None
stamp = 0
subsystem = profile = settings = old_throttle = None
subjects = []
roster = []
targets = []
frames = []
capture = None
capture_pawn = None
capture_count = 0
capture_finished = False
seen_frame_time = None
last_time = None
teardown_components = []
system = None
lifetime_probe = None
prewarm_started = None


def prop(obj, name):
    return obj.get_editor_property(name)


def xyz(value):
    return [value.x, value.y, value.z]


def locals_for(row):
    return unreal.Transform(location=unreal.Vector(*row["location_cm"]),
        rotation=unreal.Rotator(pitch=0, yaw=90, roll=0), scale=unreal.Vector(*row["scale"]))


def fill_profile(data):
    data.set_editor_property("effect", system)
    data.set_editor_property("maximum_lifetime_seconds", 8.)
    data.set_editor_property("rifles", [unreal.ParisRifleMuzzleProfile(
        rifle_mesh=unreal.load_asset(row["mesh"]), muzzle_local=locals_for(row)) for row in profiles["profiles"]])
    return data


def observation(pawn):
    found = [o for o in prop(subsystem, "observations") if prop(o, "target") == pawn]
    assert len(found) == 1, (pawn.get_actor_label(), len(found))
    return found[0]


def snap(pawn):
    o = observation(pawn)
    result = {name: prop(o, name) for name in
              ("started", "completed", "cancelled", "timed_out", "missed_sequences", "live_count")}
    result.update({"label": pawn.get_actor_label(), "sequence": prop(pawn, "ShotSequence"),
        "generation": prop(pawn, "RestoreGeneration"), "action": str(prop(pawn, "ActionState")),
        "ammo": [prop(pawn, "LoadedAmmo"), prop(pawn, "ReserveAmmo")], "dead": prop(pawn, "IsDead"),
        "error": str(prop(o, "error"))})
    assert not result["error"] and not result["timed_out"] and not result["missed_sequences"], result
    return result


def check(name, value):
    assert value, name
    report["checks"][name] = True


def fire(pawn, requests=1):
    batch = unreal.ParisMuzzleFlashLibrary.queue_review_fire(pawn, requests)
    assert batch, "Original PC_RequestFire signature/native dispatch queue rejected"
    yield .5, lambda: prop(batch, "executed")
    row = {name: prop(batch, name) for name in ("executed", "error", "sequence_before", "sequence_after",
            "queued_world_time", "dispatch_world_time", "dispatch_frame")}
    row.update(label=pawn.get_actor_label(), sequence_deltas=list(prop(batch, "sequence_deltas")),
               mechanism="native_world_pre_actor_tick_original_PC_RequestFire")
    report.setdefault("native_fire_batches", []).append(row)
    assert row["executed"] and not row["error"] and len(row["sequence_deltas"]) == requests, row
    assert 0 <= row["dispatch_world_time"]-row["queued_world_time"] <= .5 and row["dispatch_frame"] > 0, row
    assert row["sequence_after"]-row["sequence_before"] == sum(row["sequence_deltas"]), row
    return row["sequence_deltas"]


def sample_image(pawn, kind, state):
    target = targets[len(frames)]
    capture.set_editor_property("texture_target", target)
    capture.capture_scene()
    frames.append((target, pawn.get_actor_label(), kind, dict(state)))


def frame_pawn(world, pawn):
    global capture, capture_pawn, capture_count, capture_finished, seen_frame_time
    player = subjects[0]
    o = observation(pawn)
    gun = prop(o, "visible_rifle")
    assert gun and gun.get_owner()
    pawn.set_actor_hidden_in_game(False)
    gun.get_owner().set_actor_hidden_in_game(False)
    capture = unreal.ParisMuzzleFlashLibrary.create_review_capture(player)
    assert capture and prop(capture, "review_view_owner") == player
    capture.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property("capture_every_frame", False)
    capture.set_editor_property("capture_on_movement", False)
    capture.set_editor_property("primitive_render_mode", unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
    capture.set_editor_property("show_only_actors", [gun.get_owner()] if pawn == player else [pawn, gun.get_owner()])
    capture.set_editor_property("show_flag_settings", [unreal.EngineShowFlagsSetting(show_flag_name=n, enabled=False)
        for n in ("Fog", "Atmosphere", "DepthOfField", "MotionBlur")])
    if pawn == player:
        camera = unreal.GameplayStatics.get_player_camera_manager(world, 0)
        eye, rotation, fov = camera.get_camera_location(), camera.get_camera_rotation(), camera.get_fov_angle()
    else:
        eye = pawn.get_actor_location() + pawn.get_actor_forward_vector()*350 + pawn.get_actor_right_vector()*280 + unreal.Vector(0, 0, 35)
        rotation = unreal.MathLibrary.find_look_at_rotation(eye, pawn.get_actor_location()+unreal.Vector(0, 0, 20))
        fov = 40.
    capture.set_world_location(eye, False, False)
    capture.set_world_rotation(rotation, False, False)
    capture.set_editor_property("fov_angle", fov)
    # v4's camera-centred 4000lm fill overexposed the nearby FP rifle.
    # v5 removes only that extra FP diagnostic light, retaining actual city
    # lighting, original player camera/owner flags and every effect parameter.
    # NPC diagnostic fill is unchanged. No material/camera/scene is saved.
    fill_lumens = 0 if pawn == player else 4000
    if fill_lumens:
        api = unreal.get_default_object(unreal.GameplayStatics)
        transform = unreal.Transform(location=eye)
        light_actor = api.call_method("BeginDeferredActorSpawnFromClass", args=(world, unreal.PointLight.static_class(), transform,
            unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        light_actor = api.call_method("FinishSpawningActor", args=(light_actor, transform, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        light = light_actor.get_component_by_class(unreal.PointLightComponent)
        light.set_mobility(unreal.ComponentMobility.MOVABLE)
        light.set_intensity_units(type(prop(light, "intensity_units")).LUMENS)
        light.set_intensity(fill_lumens)
        light.set_attenuation_radius(1000)
        light.set_cast_shadows(False)
    report.setdefault("views", []).append({"label": pawn.get_actor_label(), "eye": xyz(eye), "fov": fov,
        "player_view_owner": player.get_actor_label(), "original_player_camera": pawn == player,
        "rifle_only_owner_see": prop(gun, "bOnlyOwnerSee"), "rifle_owner_no_see": prop(gun, "bOwnerNoSee"),
        "diagnostic_fill_lumens": fill_lumens, "show_only": True,
        "fp_observer_correction": "no_added_camera_fill_original_camera_and_city_lighting"})
    capture_pawn, capture_count, capture_finished, seen_frame_time = pawn, 0, False, None
    sample_image(pawn, "before", snap(pawn))
    assert capture.arm_deferred_review(pawn, targets[len(frames):len(frames)+12])
    check(pawn.get_actor_label()+"_native_deferred_capture_armed", prop(capture, "review_armed"))


def transaction_sequence(world):
    global capture_finished, teardown_components, phase
    for pawn in subjects:
        label = pawn.get_actor_label()
        state = lambda: snap(pawn)
        initial = state()
        total = sum(initial["ammo"])
        check(label+"_initial_no_replay", initial["started"] == 0 and initial["ammo"][0] == 2)
        frame_pawn(world, pawn)
        yield .3, None
        check(label+"_one_commit_and_cooldown_reject", (yield from fire(pawn, 2)) == [1, 0])
        yield .5, lambda: state()["started"] == 1 and state()["live_count"] == 1
        yield 8., lambda: state()["completed"] == 1 and state()["live_count"] == 0
        check(label+"_first_effect_complete", state()["started"] == 1)
        check(label+"_native_deferred_twelve_and_unregistered", capture_count == 12 and not prop(capture, "review_armed")
              and not prop(capture, "capture_error"))
        capture_finished = True
        check(label+"_second_commit", (yield from fire(pawn)) == [1])
        yield .5, lambda: state()["started"] == 2
        yield 8., lambda: state()["completed"] == 2 and state()["live_count"] == 0
        check(label+"_empty_reject", prop(pawn, "LoadedAmmo") == 0 and (yield from fire(pawn)) == [0])
        pawn.call_method("PC_RequestReload")
        check(label+"_busy_reject", str(prop(pawn, "ActionState")) == "Reloading" and (yield from fire(pawn)) == [0])
        yield 8., lambda: str(prop(pawn, "ActionState")) == "Ready"
        check(label+"_reload_conserved", prop(pawn, "LoadedAmmo") == 8 and sum(state()["ammo"]) == total-2 and state()["started"] == 2)
        check(label+"_third_commit", (yield from fire(pawn)) == [1])
        yield .5, lambda: state()["started"] == 3 and state()["live_count"] == 1
        pawn.call_method("PC_RequestReload")
        check(label+"_reload_interrupt_busy_reject", (yield from fire(pawn)) == [0])
        yield .5, lambda: state()["cancelled"] == 1 and state()["live_count"] == 0
        yield 8., lambda: str(prop(pawn, "ActionState")) == "Ready"
        check(label+"_reload_no_replay", state()["started"] == 3 and state()["completed"] == 2)
        check(label+"_fourth_commit", (yield from fire(pawn)) == [1])
        yield .5, lambda: state()["started"] == 4 and state()["live_count"] == 1
        pawn.call_method("PC_Die")
        check(label+"_dead_reject", prop(pawn, "IsDead") and (yield from fire(pawn)) == [0])
        yield .5, lambda: state()["cancelled"] == 2 and state()["live_count"] == 0
        generation = prop(pawn, "RestoreGeneration")
        pawn.call_method("PC_ResetLifecycle")
        check(label+"_reset_generation", prop(pawn, "RestoreGeneration") == generation+1 and not prop(pawn, "IsDead"))
        yield .4, None
        check(label+"_reset_no_replay", state()["started"] == 4)
        check(label+"_fifth_commit", (yield from fire(pawn)) == [1])
        yield .5, lambda: state()["started"] == 5 and state()["live_count"] == 1
        pawn.call_method("PC_ResetLifecycle")
        yield .5, lambda: state()["cancelled"] == 3 and state()["live_count"] == 0
        yield .4, None
        check(label+"_ready_reset_no_replay", state()["started"] == 5 and sum(state()["ammo"]) == total-5)
        check(label+"_sixth_commit_equipment", (yield from fire(pawn)) == [1])
        yield .5, lambda: state()["started"] == 6 and state()["live_count"] == 1
        gun = prop(observation(pawn), "visible_rifle")
        # Availability loss is distinct from the failed destructive grip test.
        # Keep the accepted attachment/equipment alive and hide its display only.
        owner = gun.get_owner()
        owner.set_actor_hidden_in_game(True)
        check(label+"_runtime_equipment_hidden", prop(owner, "hidden"))
        yield .5, lambda: state()["cancelled"] == 4 and state()["live_count"] == 0
        owner.set_actor_hidden_in_game(False)
        check(label+"_runtime_equipment_restored", unreal.SystemLibrary.is_valid(owner) and not prop(owner, "hidden"))
        yield .4, None
        check(label+"_equipment_no_replay", state()["started"] == 6 and state()["completed"] == 2)
        check(label+"_equipment_same_binding_restored", prop(observation(pawn), "visible_rifle") == gun)
        report.setdefault("subjects_final", []).append(state())
    # Finish potentially slow image IO before the nonempty world-teardown test.
    # The last two pulses must still genuinely live immediately before PIE ends.
    phase = "exporting"
    export(world)
    assert time.monotonic()-started < 210, "script deadline after original PNG export"
    phase = "transactions"
    report["export_finished_world_time"] = unreal.GameplayStatics.get_time_seconds(world)
    yield 0., None  # Consume the blocked export frame BEFORE committing a shot.
    report["post_export_world_time"] = unreal.GameplayStatics.get_time_seconds(world)
    check("post_export_distinct_frame_before_commits", report["post_export_world_time"] > report["export_finished_world_time"])
    extra = next(p for p in roster if p not in subjects and prop(p, "TeamId") == 0)
    check("world_teardown_original_extra_no_replay", snap(extra)["started"] == 0 and snap(extra)["sequence"] == 0)
    check("world_teardown_original_extra_commit", (yield from fire(extra)) == [1])
    yield .5, lambda: snap(extra)["started"] == 1 and snap(extra)["live_count"] == 1
    yield .27, None
    check("continuous_original_next_cadence_commit", (yield from fire(extra)) == [1])
    yield .5, lambda: snap(extra)["started"] == 2 and snap(extra)["live_count"] == 2
    check("continuous_original_two_commits_two_live_pulses", snap(extra)["sequence"] == 2)
    report["continuous_subject_final"] = snap(extra)
    teardown_components = list(subsystem.get_owned_components())
    check("world_teardown_had_two_live_components", len(teardown_components) == 2)
    check("native_lifetime_probe_tracks_two", lifetime_probe.track_owned_effects() == 2)
    report["native_lifetime_before"] = json.loads(lifetime_probe.inspect_lifetime())


def observe(world, now):
    global capture_count, seen_frame_time
    for pawn in subjects:
        row = snap(pawn)
        row["time"] = now
        report["samples"].append(row)
    for component in subsystem.get_owned_components():
        row = json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_component(component))
        gun = component.get_attach_parent()
        match = next(p for p in profiles["profiles"] if p["mesh"] == prop(gun, "static_mesh").get_path_name())
        relative = unreal.MathLibrary.make_relative_transform(component.get_world_transform(), gun.get_world_transform())
        q, wanted = relative.rotation, locals_for(match).rotation
        dot = abs((q.x*wanted.x+q.y*wanted.y+q.z*wanted.z+q.w*wanted.w) /
            math.sqrt((q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w)*(wanted.x*wanted.x+wanted.y*wanted.y+wanted.z*wanted.z+wanted.w*wanted.w)))
        row.update({"time": now, "relative_position_error_cm": math.dist(xyz(relative.translation), match["location_cm"]),
            "relative_angle_error_deg": math.degrees(2*math.acos(min(1., dot))), "scale": xyz(relative.scale3d),
            "only_owner_see": prop(component, "bOnlyOwnerSee"), "owner_no_see": prop(component, "bOwnerNoSee")})
        report.setdefault("component_samples", []).append(row)
        assert row["component_valid"] and row["instance_rate_valid"] and row["instance_rate"] == 20
        assert row["relative_position_error_cm"] <= .01 and row["relative_angle_error_deg"] <= .01, row
        assert all(abs(x-.25) < 1e-6 for x in row["scale"]), row
        assert row["only_owner_see"] == prop(gun, "bOnlyOwnerSee") and row["owner_no_see"] == prop(gun, "bOwnerNoSee")
    if capture_pawn is not None and not capture_finished and capture_count < 12:
        assert not prop(capture, "capture_error"), prop(capture, "capture_error")
        records = list(prop(capture, "capture_records"))
        for record in records[capture_count:]:
            native = {name: prop(record, name) for name in ("frame", "world_time", "shot_sequence", "started", "live_count")}
            assert native["shot_sequence"] == native["started"] == native["live_count"] == 1
            current = snap(capture_pawn)
            current["native_deferred_request"] = native
            # The native diagnostic already queued the matching unique target.
            # Python only retains references/records for later unedited export.
            frames.append((targets[len(frames)], capture_pawn.get_actor_label(), "pulse", current))
            capture_count += 1


def export(world):
    for i, (target, label, kind, sample) in enumerate(frames):
        name = "%s_%s_%02d.png" % (label, kind, i)
        unreal.RenderingLibrary.export_render_target(world, target, OUT.as_posix(), name)
        file = OUT / name
        assert file.is_file() and file.stat().st_size > 10000
        report["captures"].append({"file": name, "bytes": file.stat().st_size, "sha256": sha(file),
            "label": label, "kind": kind, "requested_sample": sample, "original_unpaused": True,
            "exact_render_age_not_assumed": True, "deferred_png_export": True})


def finish():
    global callback
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    if settings is not None:
        settings.set_editor_property("bThrottleCPUWhenNotForeground", old_throttle)
    try:
        report["guard_count"], report["original_intake_count"] = len(guards()), len(intake_rows())
        intake = json.loads((BASE / INTAKE_ID / "intake.json").read_text())
        home = Path(unreal.Paths.project_content_dir()) / "MsvFx_MuzzleFlash_Pack"
        for row in intake["closure"]:
            file = home / (ROOT / row["path"]).relative_to(INTAKE)
            assert file.stat().st_size == row["size_bytes"] and sha(file) == row["sha256"]
        report["candidate_purchased_count_exact"] = len(intake["closure"])
    except Exception:
        report["errors"].append(traceback.format_exc())
    report["status"] = "failed_real_transactions_preserve" if report["errors"] else (
        "pass_native_api_smoke_no_transactions" if MODE == "Api" else
        "pass_private_profile_saved_only_fresh_pending" if MODE == "SaveFresh" else
        "pass_real_transactions_native_visual_pending")
    write(OUT / "result.json", report)
    unreal.SystemLibrary.quit_editor()


def begin_world():
    global settings, old_throttle, callback
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings"))
    old_throttle = prop(settings, "bThrottleCPUWhenNotForeground")
    settings.set_editor_property("bThrottleCPUWhenNotForeground", False)
    # No callback exists while synchronous level load can pump Slate.
    if MODE != "Api":
        assert levels.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if isinstance(actor, unreal.Character):
            actor.set_actor_hidden_in_game(True)
    callback = unreal.register_slate_post_tick_callback(tick)
    levels.editor_request_begin_play()


def prewarm_tick(dt):
    global callback
    try:
        assert time.monotonic()-prewarm_started < 15, "Entry compilation/readiness deadline"
        readiness = json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_system(system))
        report.setdefault("entry_readiness_samples", []).append(readiness)
        if not readiness["ready"]:
            return
        assert readiness["valid"] and not readiness["compiling"], readiness
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
        report["entry_readiness_verified_before_city"] = True
        begin_world()
    except Exception:
        report["errors"].append(traceback.format_exc())
        finish()


def tick(dt):
    global phase, stamp, subsystem, subjects, roster, scenario, pending, last_time, teardown_components, lifetime_probe
    world = None
    try:
        assert time.monotonic()-started < 210, (phase, "script deadline")
        world = editor.get_game_world()
        if phase == "exporting":
            return  # Synchronous PNG export must not re-enter the generator.
        if phase == "end":
            if world is None:
                # The probe lives outside PIE and observes native weak refs;
                # no dead Python wrapper is queried or passed back to C++.
                observed = json.loads(lifetime_probe.inspect_lifetime())
                report["native_lifetime_after"] = observed
                check("world_subsystem_invalid", not observed["subsystem_valid"])
                check("world_owned_effects_cleared", observed["valid_components"] == 0)
                check("world_owned_components_invalid", observed["valid_components"] == 0)
                check("native_lifetime_expected_track_count", observed["tracked_components"] == (0 if MODE == "Api" else 2))
                finish()
            return
        if world is None:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if MODE == "Api":
            if now < 1:
                return
            subsystem = unreal.ParisMuzzleFlashLibrary.get_presentation_subsystem(world)
            check("native_public_subsystem_getter", subsystem is not None)
            lifetime_probe = unreal.ParisMuzzleFlashLibrary.create_lifetime_probe(world)
            check("native_lifetime_probe_empty_smoke", lifetime_probe.track_owned_effects() == 0)
            owner = unreal.GameplayStatics.get_player_pawn(world, 0)
            native_capture = unreal.ParisMuzzleFlashLibrary.create_review_capture(owner)
            check("native_owner_aware_factory", prop(native_capture, "review_view_owner") == owner)
            api = unreal.get_default_object(unreal.GameplayStatics)
            transform = unreal.Transform()
            actor = api.call_method("BeginDeferredActorSpawnFromClass", args=(world, unreal.StaticMeshActor.static_class(), transform,
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            actor = api.call_method("FinishSpawningActor", args=(actor, transform, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            mesh = actor.get_component_by_class(unreal.StaticMeshComponent)
            report["native_visibility_flag_readback"] = [prop(mesh, "bOnlyOwnerSee"), prop(mesh, "bOwnerNoSee")]
            actor.destroy_actor()
            check("void_destroy_validity_readback", not unreal.SystemLibrary.is_valid(actor))
            phase = "end"
            levels.editor_request_end_play()
            return
        if phase == "wait":
            for pawn in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
                if not pawn.is_player_controlled():
                    controller = unreal.AIHelperLibrary.get_ai_controller(pawn)
                    if controller:
                        controller.call_method("PC_EnableCombat", args=(False,))
                        controller.call_method("PC_EnablePolicy", args=(False,))
                        controller.call_method("PC_PolicyHold")
                        controller.stop_movement()
            if now < 4:
                return
            chars = {p.get_actor_label(): p for p in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)}
            roster = [p for p in chars.values() if not p.is_player_controlled()]
            subjects = [unreal.GameplayStatics.get_player_character(world, 0), chars["PC_City_Ally1"], chars["PC_City_Enemy1"]]
            check("finite_original_roster_no_unrelated_shots", len(roster) == 5 and all(prop(p, "Health") == 100 and prop(p, "ShotSequence") == 0 for p in roster+subjects[:1]))
            subsystem = unreal.ParisMuzzleFlashLibrary.get_presentation_subsystem(world)
            assert subsystem
            lifetime_probe = unreal.ParisMuzzleFlashLibrary.create_lifetime_probe(world)
            assert lifetime_probe
            phase, stamp = ("configure" if MODE == "Transient" else "binding"), now
            return
        if phase == "configure":
            assert now-stamp < 15, "Native effect readiness deadline"
            readiness = json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_system(system))
            report["effect_readiness"] = readiness
            if not readiness["ready"]:
                return
            assert readiness["valid"], readiness
            assert subsystem.configure_private_candidate(profile)
            report["private_configure_calls"] += 1
            phase, stamp = "binding", now
        if phase == "binding":
            assert now-stamp < 15, "Native display/binding readiness deadline"
            if str(prop(subsystem, "state")) != "NativeCommittedShotPresentationReady":
                return
            observations = list(prop(subsystem, "observations"))
            if not all(any(prop(o, "target") == p for o in observations) for p in roster+subjects[:1]):
                return
            check("three_original_native_rifles_bound", all(prop(observation(p), "visible_rifle") for p in subjects))
            check("six_original_native_bindings_no_replay", all(prop(observation(p), "visible_rifle") and snap(p)["started"] == 0 for p in roster+subjects[:1]))
            report["equipment_loss_mechanism"] = "unsaved_owned_display_hidden_restored_not_destroyed"
            report["initial_observations"] = [snap(p) for p in subjects]
            for o in observations:
                pawn = prop(o, "target")
                if pawn in subjects:
                    report.setdefault("muzzle_discrepancy_cm", {})[pawn.get_actor_label()] = (
                        prop(o, "visual_muzzle").translation-prop(o, "legacy_shot_muzzle")).length()
            targets.extend(unreal.RenderingLibrary.create_render_target2d(world, 1600, 900,
                unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.08,.1,.12,1), False, False) for _ in range(39))
            scenario = transaction_sequence(world)
            phase = "transactions"
        if phase == "transactions":
            if now == last_time:
                return
            last_time = now
            observe(world, now)
            if pending is not None:
                duration, condition = pending
                if condition is not None and not condition():
                    assert now-stamp < duration, ("condition deadline", duration, [snap(p) for p in subjects])
                    return
                if condition is None and now-stamp < duration:
                    return
            try:
                pending = next(scenario)
                stamp = now
            except StopIteration:
                check("original_exports_complete_before_teardown_pulses", len(report["captures"]) == 39)
                phase = "end"
                levels.editor_request_end_play()
        write(OUT / "progress.json", {"phase": phase, "elapsed_seconds": time.monotonic()-started,
            "capture_targets": len(frames), "checks": len(report["checks"])})
    except Exception:
        phase = "exporting"
        report["errors"].append(traceback.format_exc())
        if world and frames and not report["captures"]:
            try:
                export(world)
            except Exception:
                report["errors"].append(traceback.format_exc())
        # A failed entry is not a successful teardown proof.
        finish()


try:
    report["guard_count"], report["original_intake_count"] = len(guards()), len(intake_rows())
    if MODE != "Api":
        api_path = BASE / "api_smoke_v3_20261008/result.json"
        smoke = json.loads(api_path.read_text())
        assert smoke["status"] == "pass_native_api_smoke_no_transactions" and not smoke["errors"]
        validation = json.loads((api_path.parent / "log_validation.json").read_text(encoding="utf-8-sig"))
        assert validation == {"strict_errors": 0, "exit_code": 0, "timed_out": False}
        report["api_smoke_sha256"] = sha(api_path)
    system = unreal.load_asset("/Game/MsvFx_MuzzleFlash_Pack/Prefabs/Niagara_Riffle_MuzzleFlash_01")
    assert isinstance(system, unreal.NiagaraSystem)
    if MODE in ("Api", "Transient"):
        profile = fill_profile(unreal.new_object(unreal.ParisMuzzleFlashProfile))
    elif MODE == "SaveFresh":
        previous = json.loads((BASE / os.environ["CS549_MUZZLE_PREVIOUS"] / "visual_review.json").read_text())
        assert previous["candidate_runtime_visual_admitted"]
        assert not unreal.EditorAssetLibrary.does_asset_exist(PROFILE_PACKAGE), "Preserve occupied profile"
        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", unreal.ParisMuzzleFlashProfile)
        profile = unreal.AssetToolsHelpers.get_asset_tools().create_asset(PROFILE_PACKAGE.rsplit("/",1)[1],
            PROFILE_PACKAGE.rsplit("/",1)[0], unreal.ParisMuzzleFlashProfile, factory)
        fill_profile(profile)
        assert unreal.EditorAssetLibrary.save_loaded_asset(profile, False)
        report["private_profile_saved"] = True
    else:
        profile = unreal.load_asset(PROFILE_PACKAGE)
        assert isinstance(profile, unreal.ParisMuzzleFlashProfile)
    assert len(prop(profile, "rifles")) == 2
    assert prop(profile, "effect") == system and prop(profile, "maximum_lifetime_seconds") == 8
    for native, expected in zip(prop(profile, "rifles"), profiles["profiles"]):
        assert prop(native, "rifle_mesh").get_path_name() == expected["mesh"]
        local = prop(native, "muzzle_local")
        assert math.dist(xyz(local.translation), expected["location_cm"]) < 1e-5
        assert xyz(local.scale3d) == [.25]*3
        q, wanted = local.rotation, locals_for(expected).rotation
        assert abs(q.x*wanted.x+q.y*wanted.y+q.z*wanted.z+q.w*wanted.w) > .999999
    report["native_profile_readback_exact"] = True
    if MODE == "SaveFresh":
        # Saving is not a transaction proof. The next fresh process must load
        # the persisted native asset without a private Configure call.
        finish()
    else:
        unreal.EditorPythonScripting.set_keep_python_script_alive(True)
        if MODE == "Api":
            begin_world()
        else:
            report["explicit_entry_compile_requested"] = unreal.ParisMuzzleFlashLibrary.request_purchased_compile(system)
            prewarm_started = time.monotonic()
            callback = unreal.register_slate_post_tick_callback(prewarm_tick)
except Exception:
    report["errors"].append(traceback.format_exc())
    finish()
