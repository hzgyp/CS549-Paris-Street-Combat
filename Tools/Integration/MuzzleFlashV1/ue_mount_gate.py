"""Two unchanged selected rifles, one measured pulse each, isolated unsaved PIE."""
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BASE, guards, intake_rows, sha, write
from geometry_mounts import measured_profiles
from asset_gate_contract import classify_systems
from scale_contract import IDENTITY, INSTANCE_SCALE, scaled_profiles

OUT = BASE / os.environ["CS549_MUZZLE_ID"]
assert OUT.name == IDENTITY, "One user-requested instance scale comparison"
profiles = scaled_profiles(measured_profiles())
prior_directory = BASE / "mount_named_rotation_v2_20261008"
prior_review = json.loads((prior_directory / "visual_review.json").read_text())
assert prior_review["native_result_sha256"] == sha(prior_directory / "result.json")
assert not prior_review["scale_accepted"] and not prior_review["candidate_admitted"]
report = {"identity": OUT.name, "errors": [], "profiles": profiles, "samples": [],
          "captures": [], "completions": [], "activation_count": 0,
          "native_save": False, "map_saved": False, "graph_edited": False,
          "ballistic_logic_changed": False, "human_review_pending": True,
          "instance_scale": INSTANCE_SCALE, "prior_visual_review_sha256": sha(prior_directory / "visual_review.json"),
          "same_camera_and_lighting_as_unit_mount": True}
started = time.monotonic()
phase = "compile"
callback = None
system = None
meshes = []
rifle = None
component = None
capture = None
targets = []
frames = []
index = 0
born = 0
last_time = None
saw_active = False
settle_until = 0
settings = None
old_throttle = None
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def spawn(world, cls, location, rotation=unreal.Rotator()):
    api = unreal.get_default_object(unreal.GameplayStatics)
    transform = unreal.Transform(location=location)
    actor = api.call_method("BeginDeferredActorSpawnFromClass", args=(world, cls.static_class(), transform,
        unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    actor = api.call_method("FinishSpawningActor", args=(actor, transform, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    actor.set_actor_rotation(rotation, False)
    return actor


def sample_image(sample, kind):
    target = targets[len(frames)]
    capture.set_editor_property("texture_target", target)
    capture.capture_scene()
    frames.append((target, dict(sample), index, kind))


def export_frames(world):
    for number, (target, sample, rifle_index, kind) in enumerate(frames):
        name = "rifle_%d_%s_%02d.png" % (rifle_index, kind, number)
        unreal.RenderingLibrary.export_render_target(world, target, OUT.as_posix(), name)
        file = OUT / name
        assert file.is_file() and file.stat().st_size > 10000
        report["captures"].append({"file": name, "sha256": sha(file), "bytes": file.stat().st_size,
            "rifle_index": rifle_index, "requested_sample": sample,
            "unpaused": True, "exported_after_observation": True, "exact_render_age_not_assumed": True})


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
    report["status"] = "failed_measured_mount_preserve" if report["errors"] else "pass_measured_mount_native_completion_visual_pending"
    write(OUT / "result.json", report)
    unreal.SystemLibrary.quit_editor()


def tick(dt):
    global phase, capture, rifle, component, index, born, last_time, saw_active, settle_until
    world = None
    try:
        assert time.monotonic() - started < 210, "Finite script deadline"
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if phase == "end":
            if world is None:
                finish()
            return
        if phase == "compile":
            row = json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_system(system))
            if classify_systems([row]) != "ready":
                return
            report["system_ready"] = row
            phase = "world"
            levels.editor_request_begin_play()
            return
        if world is None:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if phase == "world":
            if now < .5:
                return
            assert not unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
            eye = unreal.Vector(200, 65, 90)
            camera = spawn(world, unreal.SceneCapture2D, eye)
            capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
            capture.set_world_rotation(unreal.MathLibrary.find_look_at_rotation(eye, unreal.Vector(0, 40, 3)), False, False)
            capture.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property("capture_every_frame", False)
            capture.set_editor_property("capture_on_movement", False)
            capture.set_editor_property("fov_angle", 50)
            capture.set_editor_property("show_flag_settings", [unreal.EngineShowFlagsSetting(show_flag_name=n, enabled=False)
                for n in ("Fog", "Atmosphere", "DepthOfField", "MotionBlur")])
            report["positional_constructor_readback"] = {n: getattr(unreal.Rotator(0, 90, 0), n) for n in ("pitch", "yaw", "roll")}
            light = spawn(world, unreal.DirectionalLight, unreal.Vector(0, 0, 300), unreal.Rotator(pitch=-45, yaw=45, roll=0))
            light.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property("intensity", 4)
            fill = spawn(world, unreal.PointLight, eye)
            fill_component = fill.get_component_by_class(unreal.PointLightComponent)
            fill_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            fill_component.set_intensity_units(type(fill_component.get_editor_property("intensity_units")).LUMENS)
            fill_component.set_intensity(10000)
            fill_component.set_attenuation_radius(1000)
            fill_component.set_cast_shadows(False)
            report["diagnostic_fill_lumens"] = 10000
            for _ in range(26):
                targets.append(unreal.RenderingLibrary.create_render_target2d(world, 1600, 900,
                    unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.08, .1, .12, 1), False, False))
            phase = "rifle"
        if phase == "rifle":
            actor = spawn(world, unreal.StaticMeshActor, unreal.Vector())
            rifle = actor.get_component_by_class(unreal.StaticMeshComponent)
            rifle.set_mobility(unreal.ComponentMobility.MOVABLE)
            rifle.set_static_mesh(meshes[index])
            rifle.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            settle_until = now + .3
            phase = "settle"
            return
        if phase == "settle":
            if now < settle_until:
                return
            sample_image({"age": None, "mesh": meshes[index].get_path_name()}, "before")
            row = profiles["profiles"][index]
            rotation = unreal.Rotator(pitch=0, yaw=90, roll=0)
            assert rotation.pitch == 0 and rotation.yaw == 90 and rotation.roll == 0
            local = unreal.Transform(location=unreal.Vector(*row["location_cm"]), rotation=rotation, scale=unreal.Vector(*row["scale"]))
            component = unreal.ParisMuzzleFlashLibrary.spawn_measured_pulse(system, rifle, local)
            assert component is not None
            born = unreal.GameplayStatics.get_time_seconds(world)
            report["activation_count"] += 1
            last_time, saw_active = None, False
            phase = "observe"
        if phase == "observe":
            now = unreal.GameplayStatics.get_time_seconds(world)
            if now == last_time:
                return
            last_time = now
            sample = json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_component(component))
            sample.update({"age": now - born, "rifle_index": index})
            assert sample["component_valid"] and sample["instance_rate_valid"] and sample["instance_rate"] == 20
            expected = profiles["profiles"][index]["location_cm"]
            sample["mount_position_error_cm"] = sum((a - b) ** 2 for a, b in zip(sample["location"], expected)) ** .5
            sample["mount_forward_error"] = sum((a - b) ** 2 for a, b in zip(sample["forward"], [0, 1, 0])) ** .5
            actual_scale = component.get_editor_property("relative_scale3d")
            sample["relative_scale"] = [actual_scale.x, actual_scale.y, actual_scale.z]
            report["samples"].append(sample)
            assert sample["mount_position_error_cm"] <= .01 and sample["mount_forward_error"] <= .0001, sample
            assert all(abs(v - INSTANCE_SCALE) <= .000001 for v in sample["relative_scale"]), sample
            saw_active |= sample["active"]
            if sum(1 for _, _, i, k in frames if i == index and k == "pulse") < 12:
                sample_image(sample, "pulse")
            if sample["complete"]:
                assert saw_active and not sample["active"] and sample["age"] <= 8
                report["completions"].append(dict(sample))
                component.call_method("K2_DestroyComponent", args=(component,))
                component = None
                rifle.get_owner().destroy_actor()
                rifle = None
                index += 1
                if index == len(meshes):
                    assert report["activation_count"] == 2
                    export_frames(world)
                    phase = "end"
                    levels.editor_request_end_play()
                else:
                    phase = "rifle"
            else:
                assert sample["age"] <= 8, "True completion cap exceeded"
        write(OUT / "progress.json", {"phase": phase, "rifle_index": index,
            "captured_targets": len(frames), "elapsed_seconds": time.monotonic() - started})
    except Exception:
        report["errors"].append(traceback.format_exc())
        if world is not None and frames and not report["captures"]:
            try:
                export_frames(world)
            except Exception:
                report["errors"].append(traceback.format_exc())
        phase = "end"
        levels.editor_request_end_play()


try:
    report["guard_count"] = len(guards())
    report["original_intake_count"] = len(intake_rows())
    system = unreal.load_asset("/Game/MsvFx_MuzzleFlash_Pack/Prefabs/Niagara_Riffle_MuzzleFlash_01")
    meshes = [unreal.load_asset(row["mesh"]) for row in profiles["profiles"]]
    assert isinstance(system, unreal.NiagaraSystem) and all(isinstance(m, unreal.StaticMesh) for m in meshes)
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings"))
    old_throttle = settings.get_editor_property("bThrottleCPUWhenNotForeground")
    settings.set_editor_property("bThrottleCPUWhenNotForeground", False)
    unreal.ParisMuzzleFlashLibrary.request_purchased_compile(system)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
except Exception:
    report["errors"].append(traceback.format_exc())
    finish()
