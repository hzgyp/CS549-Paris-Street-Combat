"""Unsaved Entry PIE: native completion and unedited original effect renders."""
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BASE, guards, intake_rows, write
from asset_gate_contract import classify_systems
from effect_gate_contract import select_effect_candidates

OUT = BASE / os.environ["CS549_MUZZLE_ID"]
MODE = os.environ.get("CS549_MUZZLE_EFFECT_MODE")
PULSE = MODE in ("Pulse", "RemainingPulse")
data = json.loads((BASE / os.environ["CS549_MUZZLE_INTAKE"] / "intake.json").read_text())
report = {"identity": os.environ["CS549_MUZZLE_ID"], "errors": [], "systems": [],
          "samples": [], "captures": [], "natural_completions": [],
          "native_save": False, "map_saved": False, "graph_edited": False,
          "visual_review_pending": True, "city_transaction_passed": False}
report["controlled_pulse"] = PULSE
report["requested_emission_seconds"] = .10 if PULSE else None
report["normal_deactivations"] = []
systems = []
loaded_systems = []
candidate_numbers = []
callback = None
started = time.monotonic()
phase = "compile"
index = 0
component = None
born = 0
capture = None
target = None
next_capture = 0
saw_active = False
deactivated = False
settings = None
old_throttle = None
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ages = (0.01, 0.06, 0.12, 0.3, 1.0)


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
    except Exception:
        report["errors"].append(traceback.format_exc())
    report["status"] = "failed_effect_gate_preserve" if report["errors"] else (
        "pass_controlled_pulse_native_completion_visual_review_pending" if PULSE else "pass_natural_finite_effects_visual_review_pending")
    write(OUT / "result.json", report)
    unreal.SystemLibrary.quit_editor()


def spawn(world, cls, location, rotation=unreal.Rotator()):
    api = unreal.get_default_object(unreal.GameplayStatics)
    transform = unreal.Transform(location=location)
    actor = api.call_method("BeginDeferredActorSpawnFromClass", args=(world, cls.static_class(), transform,
        unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    actor = api.call_method("FinishSpawningActor", args=(actor, transform, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    actor.set_actor_rotation(rotation, False)
    return actor


def setup_capture(world):
    global capture, target
    eye = unreal.Vector(250, -250, 120)
    camera = spawn(world, unreal.SceneCapture2D, eye)
    capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_world_rotation(unreal.MathLibrary.find_look_at_rotation(eye, unreal.Vector(0, 0, 15)), False, False)
    target = unreal.RenderingLibrary.create_render_target2d(world, 1600, 900,
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.08, .1, .12, 1), False, False)
    capture.set_editor_property("texture_target", target)
    capture.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property("capture_every_frame", False)
    capture.set_editor_property("capture_on_movement", False)
    capture.set_editor_property("fov_angle", 50)
    capture.set_editor_property("show_flag_settings", [unreal.EngineShowFlagsSetting(show_flag_name=n, enabled=False)
        for n in ("Fog", "Atmosphere", "DepthOfField", "MotionBlur")])
    light = spawn(world, unreal.DirectionalLight, unreal.Vector(0, 0, 300), unreal.Rotator(-45, 45, 0))
    light.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property("intensity", 4)
    # Entry is an isolated generic fixture. No selected city/character is loaded.
    assert not any(a.get_editor_property("ShotSequence") is not None
        for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
        if "Paris" in a.get_class().get_path_name())


def render(world, name, sample):
    capture.capture_scene()
    path = OUT / name
    unreal.RenderingLibrary.export_render_target(world, target, OUT.as_posix(), path.name)
    assert path.is_file() and path.stat().st_size > 10000, "Native image export absent"
    report["captures"].append({"file": path.name, "requested_sample": sample,
        "unpaused": True, "exact_render_age_not_assumed": True})


def tick(dt):
    global phase, index, component, born, next_capture, saw_active, deactivated
    try:
        assert time.monotonic() - started < 180, "Finite effect gate wall-time deadline"
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if phase == "end":
            if world is None:
                finish()
            return
        if phase == "compile":
            current = [json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_system(s)) for s in loaded_systems]
            report["systems"] = current
            if classify_systems(current) != "ready":
                return
            phase = "wait_world"
            levels.editor_request_begin_play()
            return
        if world is None:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if phase == "wait_world":
            if now < .5:
                return
            setup_capture(world)
            phase = "spawn"
        if phase == "spawn":
            component = unreal.NiagaraFunctionLibrary.spawn_system_at_location(world, systems[index], unreal.Vector(),
                auto_destroy=False, pre_cull_check=False)
            assert component is not None
            born, next_capture, saw_active, deactivated = now, 0, False, False
            phase = "observe"
        if phase == "observe":
            sample = json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_component(component))
            sample.update({"index": index, "candidate_number": candidate_numbers[index],
                "age": now - born, "game_time": now})
            assert sample["component_valid"], sample
            report["samples"].append(sample)
            saw_active |= sample["active"]
            if PULSE and not deactivated and sample["age"] >= .10:
                component.deactivate()
                deactivated = True
                report["normal_deactivations"].append({"index": index, "age": sample["age"],
                    "requested_window": .10, "forced_destruction": False})
            if next_capture < len(ages) and sample["age"] >= ages[next_capture]:
                render(world, "rifle_%02d_%02d.png" % (candidate_numbers[index], next_capture), sample)
                next_capture += 1
            if sample["complete"]:
                assert saw_active and next_capture > 0, "No observed activation/render before completion"
                sample["completion_cause"] = "native_complete_after_requested_deactivation" if PULSE else "native_default_self_termination"
                report["natural_completions"].append(sample)
                component.call_method("K2_DestroyComponent", args=(component,))
                component = None
                index += 1
                if index == len(systems):
                    phase = "end"
                    levels.editor_request_end_play()
                else:
                    phase = "spawn"
            else:
                assert sample["age"] <= 8, "Purchased effect did not complete within8game-seconds"
        write(OUT / "progress.json", {"phase": phase, "index": index,
            "elapsed_seconds": time.monotonic() - started})
    except Exception:
        report["errors"].append(traceback.format_exc())
        phase = "end"
        levels.editor_request_end_play()


try:
    report["guard_count"] = len(guards())
    report["original_intake_count"] = len(intake_rows())
    prior = json.loads((BASE / "native_assets_v4_20261007/result.json").read_text())
    assert prior["status"].startswith("pass_") and not prior["errors"] and prior["rendering_enabled"]
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings"))
    old_throttle = settings.get_editor_property("bThrottleCPUWhenNotForeground")
    settings.set_editor_property("bThrottleCPUWhenNotForeground", False)
    failed_pulse = json.loads((BASE / "effect_pulse_v1_20261007/result.json").read_text()) if MODE == "RemainingPulse" else None
    selected = select_effect_candidates(data["candidates"], MODE, failed_pulse)
    report["tested_candidates"] = selected
    report["excluded_previously_failed_candidates"] = [p for p in data["candidates"] if p not in selected]
    for package in data["candidates"]:
        system = unreal.load_asset(package)
        assert isinstance(system, unreal.NiagaraSystem)
        loaded_systems.append(system)
        if package in selected:
            systems.append(system)
            candidate_numbers.append(int(package.rsplit("_", 1)[-1]))
        unreal.ParisMuzzleFlashLibrary.request_purchased_compile(system)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
except Exception:
    report["errors"].append(traceback.format_exc())
    finish()
