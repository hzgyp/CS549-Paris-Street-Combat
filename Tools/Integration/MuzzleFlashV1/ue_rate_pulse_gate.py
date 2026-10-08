"""One inactive-spawn instance override and ordinary native timer; stop for review."""
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BASE, ROOT, INTAKE, guards, intake_rows, sha, write
from asset_gate_contract import classify_systems
from rate_pulse_contract import RATE_NAME, RATE, WINDOW, CAP, MAX_CAPTURES, select_rate_candidate

OUT = BASE / os.environ["CS549_MUZZLE_ID"]
assert OUT.name == "rate_pulse_v1_20261008", "Only the single authorized identity"
report = {"identity": OUT.name, "status": "running", "errors": [], "samples": [],
          "captures": [], "activation_count": 0, "systems": [], "natural_completions": [],
          "requested_emission_seconds": WINDOW, "completion_cap_seconds": CAP,
          "instance_override": {"name": RATE_NAME, "value": RATE},
          "native_save": False, "map_saved": False, "graph_edited": False,
          "runtime_adapter_enabled": False, "city_transaction_passed": False,
          "human_review_pending": True, "candidate_admitted": False,
          "exact_timer_callback_age_not_assumed": True}
started = time.monotonic()
phase = "compile"
callback = None
system = None
component = None
capture = None
targets = []
pending_frames = []
settings = None
old_throttle = None
born = None
last_frame_time = None
timer = None
saw_active = False
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
api = unreal.get_default_object(unreal.SystemLibrary)


def inspect_system():
    return json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_system(system))


def defaults(row):
    return {p["name"]: p["float_value"] for p in row["exposed_asset_defaults"] if p.get("available")}


def spawn(world, cls, location, rotation=unreal.Rotator()):
    gameplay = unreal.get_default_object(unreal.GameplayStatics)
    transform = unreal.Transform(location=location)
    actor = gameplay.call_method("BeginDeferredActorSpawnFromClass", args=(world, cls.static_class(), transform,
        unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    actor = gameplay.call_method("FinishSpawningActor", args=(actor, transform, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    actor.set_actor_rotation(rotation, False)
    return actor


def setup_capture(world):
    global capture
    eye = unreal.Vector(250, -250, 120)
    camera = spawn(world, unreal.SceneCapture2D, eye)
    capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_world_rotation(unreal.MathLibrary.find_look_at_rotation(eye, unreal.Vector(0, 0, 15)), False, False)
    capture.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property("capture_every_frame", False)
    capture.set_editor_property("capture_on_movement", False)
    capture.set_editor_property("fov_angle", 50)
    capture.set_editor_property("show_flag_settings", [unreal.EngineShowFlagsSetting(show_flag_name=n, enabled=False)
        for n in ("Fog", "Atmosphere", "DepthOfField", "MotionBlur")])
    light = spawn(world, unreal.DirectionalLight, unreal.Vector(0, 0, 300), unreal.Rotator(-45, 45, 0))
    light.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property("intensity", 4)
    for _ in range(MAX_CAPTURES):
        targets.append(unreal.RenderingLibrary.create_render_target2d(world, 1600, 900,
            unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.08, .1, .12, 1), False, False))


def capture_frame(sample):
    if len(pending_frames) >= MAX_CAPTURES:
        return
    target = targets[len(pending_frames)]
    capture.set_editor_property("texture_target", target)
    capture.capture_scene()
    pending_frames.append((target, dict(sample)))


def export_frames(world):
    for i, (target, sample) in enumerate(pending_frames):
        filename = "rifle_01_%02d.png" % i
        unreal.RenderingLibrary.export_render_target(world, target, OUT.as_posix(), filename)
        file = OUT / filename
        assert file.is_file() and file.stat().st_size > 10000, "Original native PNG absent"
        report["captures"].append({"file": filename, "sha256": sha(file), "bytes": file.stat().st_size,
            "requested_sample": sample, "unpaused": True, "exported_after_observation": True,
            "exact_render_age_not_assumed": True})


def finish():
    global callback
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    if settings is not None:
        settings.set_editor_property("bThrottleCPUWhenNotForeground", old_throttle)
    try:
        report["guard_count"] = len(guards())
        report["original_intake_count"] = len(intake_rows())
        report["final_asset_defaults"] = defaults(inspect_system())
        assert report["final_asset_defaults"] == report["initial_asset_defaults"]
    except Exception:
        report["errors"].append(traceback.format_exc())
    report["status"] = "failed_rate_pulse_preserve" if report["errors"] else "pass_rate_pulse_native_completion_human_review_pending"
    write(OUT / "result.json", report)
    unreal.SystemLibrary.quit_editor()


def tick(dt):
    global phase, component, born, last_frame_time, timer, saw_active
    world = None
    try:
        assert time.monotonic() - started < 180, "Bounded script deadline"
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if phase == "end":
            if world is None:
                finish()
            return
        if phase == "compile":
            row = inspect_system()
            report["systems"] = [row]
            if classify_systems([row]) != "ready":
                return
            report["initial_asset_defaults"] = defaults(row)
            assert report["initial_asset_defaults"][RATE_NAME] == 5.0
            assert abs(report["initial_asset_defaults"]["User.MuzzleFlash_Lifetime"] - .10) < 1e-6
            phase = "world"
            levels.editor_request_begin_play()
            return
        if world is None:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if phase == "world":
            if now < .5:
                return
            setup_capture(world)
            component = unreal.NiagaraFunctionLibrary.spawn_system_at_location(world, system, unreal.Vector(),
                auto_destroy=False, auto_activate=False, pre_cull_check=False)
            assert component is not None
            assert not json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_component(component))["active"]
            component.call_method("SetVariableFloat", args=(RATE_NAME, RATE))
            value, valid = component.call_method("GetVariableFloat", args=(RATE_NAME,))
            report["instance_override"]["typed_readback"] = {"value": value, "valid": valid}
            assert valid and value == RATE, "Instance float override not verified"
            component.activate(True)
            report["activation_count"] += 1
            assert report["activation_count"] == 1
            born = unreal.GameplayStatics.get_time_seconds(world)
            timer = api.call_method("K2_SetTimer", args=(component, "Deactivate", WINDOW, False, False, 0., 0.))
            assert api.call_method("K2_IsValidTimerHandle", args=(timer,))
            assert api.call_method("K2_IsTimerActiveHandle", args=(world, timer))
            report["timer_scheduled"] = {"function": "Deactivate", "looping": False,
                "seconds": WINDOW, "valid": True, "active_at_schedule": True}
            phase = "observe"
        if phase == "observe":
            now = unreal.GameplayStatics.get_time_seconds(world)
            if now == last_frame_time:
                return
            last_frame_time = now
            sample = json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_component(component))
            sample.update({"age": now - born, "game_time": now,
                "timer_active": api.call_method("K2_IsTimerActiveHandle", args=(world, timer))})
            assert sample["component_valid"]
            report["samples"].append(sample)
            saw_active |= sample["active"]
            capture_frame(sample)
            if not sample["active"] and "first_inactive_observed_upper_bound_seconds" not in report:
                report["first_inactive_observed_upper_bound_seconds"] = sample["age"]
            if sample["complete"]:
                assert saw_active and not sample["active"] and not sample["timer_active"]
                assert sample["age"] <= CAP, "Complete after unchanged8s cap"
                sample["completion_cause"] = "native_complete_after_native_timer_ordinary_deactivate"
                report["natural_completions"].append(dict(sample))
                export_frames(world)
                component.call_method("K2_DestroyComponent", args=(component,))
                report["cleanup_after_true_complete"] = True
                component = None
                phase = "end"
                levels.editor_request_end_play()
            else:
                assert sample["age"] <= CAP, "Instance did not complete within8game-seconds"
        write(OUT / "progress.json", {"phase": phase, "elapsed_seconds": time.monotonic() - started,
            "activation_count": report["activation_count"], "captured_targets": len(pending_frames)})
    except Exception:
        report["errors"].append(traceback.format_exc())
        if world is not None and pending_frames and not report["captures"]:
            try:
                export_frames(world)
            except Exception:
                report["errors"].append(traceback.format_exc())
        phase = "end"
        levels.editor_request_end_play()


try:
    report["guard_count"] = len(guards())
    report["original_intake_count"] = len(intake_rows())
    intake = json.loads((BASE / os.environ["CS549_MUZZLE_INTAKE"] / "intake.json").read_text())
    candidate = ROOT / ("tmp/muzzle-flash-v1/Candidate_" + os.environ["CS549_MUZZLE_INTAKE"]) / "Content/MsvFx_MuzzleFlash_Pack"
    assert len(intake["closure"]) == 25
    for row in intake["closure"]:
        file = candidate / (ROOT / row["path"]).relative_to(INTAKE)
        assert file.stat().st_size == row["size_bytes"] and sha(file) == row["sha256"]
    report["candidate_exact_package_count"] = 25
    reviews = []
    for identity in ("effect_pulse_v1_20261007", "remaining_pulse_v1_20261007"):
        review = json.loads((BASE / identity / "visual_review.json").read_text())
        assert review["native_result_sha256"] == sha(BASE / identity / "result.json")
        for image in review["images"]:
            assert image["sha256"] == sha(BASE / identity / image["file"])
        reviews.append(review)
    package = select_rate_candidate(intake["candidates"], reviews)
    report["tested_candidates"] = [package]
    system = unreal.load_asset(package)
    assert isinstance(system, unreal.NiagaraSystem)
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings"))
    old_throttle = settings.get_editor_property("bThrottleCPUWhenNotForeground")
    settings.set_editor_property("bThrottleCPUWhenNotForeground", False)
    unreal.ParisMuzzleFlashLibrary.request_purchased_compile(system)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
except Exception:
    report["errors"].append(traceback.format_exc())
    finish()
