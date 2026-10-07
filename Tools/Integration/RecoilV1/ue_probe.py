"""New read-only clip and original-shot observer, not a stopped author rerun."""
import json
import os
import sys
import time
import traceback
import math
from pathlib import Path
import unreal

sys.path.insert(0, os.environ.get("CS549_RECOIL_TOOL_DIR", str(Path(__file__).resolve().parent)))
from common import BASE, CLIP, MAP, ROOT, guards, write

OUT = BASE / os.environ["CS549_RECOIL_ID"]
MODE = os.environ["CS549_RECOIL_MODE"]
report = {"mode": MODE, "errors": [], "samples": [], "summary": {}, "map_saved": False,
          "python_pose_driver": False, "original_transaction_only": True}
callback = None
started = time.monotonic()
phase = "wait"
stamp = 0
subjects = []
subject_index = 0
shot_before = None
old_throttle = None
settings = None
scenario = None
pending = None
review_camera = None
peak_requested = False
before_requested = False
review_capture = None
review_target = None
review_light = None


def enc(t):
    return {"t": [t.translation.x, t.translation.y, t.translation.z],
            "q": [t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w],
            "s": [t.scale3d.x, t.scale3d.y, t.scale3d.z]}


def prop(obj, name):
    return obj.get_editor_property(name)


def finish():
    global callback
    if settings is not None:
        settings.set_editor_property("bThrottleCPUWhenNotForeground", old_throttle)
    try:
        report["protected_count"] = len(guards())
    except Exception:
        report["errors"].append(traceback.format_exc())
    report["status"] = "pass_read_only_recoil_" + MODE + "_diagnosis" if not report["errors"] else "failed_probe_preserve"
    write(OUT / "result.json", report)
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def clip_probe():
    clip = unreal.load_asset(CLIP)
    assert isinstance(clip, unreal.AnimSequence)
    length = unreal.AnimationLibrary.get_sequence_length(clip)
    meshes = ["/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1",
              "/Game/ParisCombat/Characters/Adaptation/Meshes/SK_German_Soldier_UE582_v1"]
    # Discover actual German mesh from its unchanged selected private config.
    data = unreal.load_asset("/Game/ParisCombat/Animation/GermanGripV14/DA_PC_GermanGripV11")
    meshes[1] = json.loads(prop(data, "BindingJson"))["source_mesh"].split(".")[0]
    report["source_clip"] = {"path": clip.get_path_name(), "length": length,
        "skeleton": prop(clip, "skeleton").get_path_name(),
        "tracks": [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(clip)]}
    report["meshes"] = []
    for path in meshes:
        mesh = unreal.load_asset(path)
        assert isinstance(mesh, unreal.SkeletalMesh), path
        report["meshes"].append({"path": mesh.get_path_name(), "skeleton": prop(mesh, "skeleton").get_path_name()})
    component = unreal.new_object(unreal.SkeletalMeshComponent)
    component.set_skeletal_mesh_asset(unreal.load_asset(meshes[0]))
    names = [component.get_bone_name(i) for i in range(component.get_num_bones())]
    parents = {str(n): str(component.get_parent_bone(n)) for n in names}
    for i in range(31):
        seconds = length * i / 30
        local = {str(n): unreal.AnimationLibrary.get_bone_pose_for_time(clip, n, seconds, False) for n in names}
        world = {}
        for n in names:
            name, parent = str(n), parents[str(n)]
            world[name] = unreal.MathLibrary.compose_transforms(local[name], world[parent]) if parent in world else local[name]
        hand = world["hand_r"]
        if i == 0:
            reference = hand
        relative = unreal.MathLibrary.make_relative_transform(hand, reference)
        report["samples"].append({"time": seconds, "right": enc(hand), "left": enc(world["hand_l"]),
            "right_from_first": enc(relative)})
    report["parents"] = parents
    report["summary"] = {"existing_clip_sampled": 31,
        "maximum_right_translation_cm": max(unreal.Vector(*s["right_from_first"]["t"]).length() for s in report["samples"]),
        "last_right_from_first": report["samples"][-1]["right_from_first"],
        "skeleton_identity": [x["skeleton"] == report["source_clip"]["skeleton"] for x in report["meshes"]]}


def native_source_probe():
    actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.ParisFirstPersonApprovedActor, unreal.Vector(0, 0, 0))
    report["native_source"] = json.loads(actor.inspect_existing_recoil_source())
    assert report["native_source"]["valid"], report["native_source"]
    baseline = json.loads((BASE / "source_v1_20261007/result.json").read_text(encoding="utf-8"))
    source = report["native_source"]["samples"]
    assert len(source) == 31
    errors = [sum((x-y)**2 for x,y in zip(a["t"], b["right_from_first"]["t"]))**.5
              for a,b in zip(source, baseline["samples"])]
    angles = [math.degrees(2 * math.acos(min(1., abs(sum(x*y for x,y in zip(a["q"], b["right_from_first"]["q"]))))))
              for a,b in zip(source, baseline["samples"])]
    report["summary"] = {"maximum_native_editor_translation_difference_cm": max(errors),
        "maximum_native_editor_angle_difference_deg": max(angles),
        "native_source_maximum_cm": report["native_source"]["maximum"], "sample_count": len(source)}
    assert max(errors) <= .05 and max(angles) <= .05, report["summary"]


def shot_sample(world, pawn):
    gun = prop(pawn, "WeaponAppearance")
    fp = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.ParisFirstPersonApprovedActor)
               if prop(a, "Initialized")), None) if pawn.is_player_controlled() else None
    mesh = prop(fp, "Pose") if fp else pawn.mesh
    visible_gun = prop(fp, "Gun") if fp else gun.static_mesh_component
    parent = pawn.get_actor_transform()
    pp = pawn.mesh.get_post_process_instance()
    binding = fp if fp else next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.ParisNPCGripActor) if prop(a, "Target") == pawn)
    sample = {"label": pawn.get_actor_label(), "time": unreal.GameplayStatics.get_time_seconds(world),
        "sequence": prop(pawn, "ShotSequence"), "generation": prop(pawn, "RestoreGeneration"),
        "action": str(prop(pawn, "ActionState")), "ammo": [prop(pawn, "LoadedAmmo"), prop(pawn, "ReserveAmmo")],
        "outcome": str(prop(pawn, "ShotOutcome")), "right": enc(unreal.MathLibrary.make_relative_transform(mesh.get_socket_transform("hand_r", unreal.RelativeTransformSpace.RTS_WORLD), parent)),
        "left": enc(unreal.MathLibrary.make_relative_transform(mesh.get_socket_transform("hand_l", unreal.RelativeTransformSpace.RTS_WORLD), parent)),
        "gun": enc(unreal.MathLibrary.make_relative_transform(visible_gun.get_world_transform(), parent)),
        "gun_hand": enc(unreal.MathLibrary.make_relative_transform(visible_gun.get_world_transform(), mesh.get_socket_transform("hand_r", unreal.RelativeTransformSpace.RTS_WORLD))),
        "main_anim": pawn.mesh.get_anim_instance().get_class().get_path_name() if pawn.mesh.get_anim_instance() else None,
        "holding_weight": prop(pp, "HoldingWeight") if pp else prop(fp, "ExistingGripWeight"),
        "display_error": str(prop(binding, "BindingError")),
        "visible_display": fp.get_class().get_path_name() if fp else pp.get_class().get_path_name()}
    if MODE in ("candidate", "contract", "visual", "visual_isolated", "installed"):
        sample.update({"recoil_starts": prop(binding, "RecoilStarts"), "recoil_active": prop(binding, "RecoilActive"),
            "recoil_age": prop(binding, "RecoilAge"), "recoil_error": str(prop(binding, "RecoilError")),
            "source_maximum": prop(binding, "RecoilSourceMaximumCm"),
            "hand_goal_error": prop(pp, "RecoilHandErrorCm") if pp else 0})
        if pp:
            sample.update({"valid_input": prop(pp, "ValidInput"), "evaluations": prop(pp, "Evaluations"),
                "protection_error": prop(pp, "ProtectionError"),
                "protected_quat_component_error": prop(pp, "ProtectedQuatComponentError"),
                "gun_error_cm": prop(binding, "GunErrorCm"), "gun_error_deg": prop(binding, "GunErrorDegrees")})
            # Existing animation-mode changes can recreate an unevaluated
            # instance. Record it as pending, never count it as an audited pose.
            # The unchanged native actor still enforces its0.5s evaluation gate.
            sample["audit_pending"] = MODE == "contract" and sample["evaluations"] == 0
            if not sample["audit_pending"]:
                assert sample["valid_input"] and sample["evaluations"] > 0 and sample["protection_error"] <= .0001, sample
                assert sample["protected_quat_component_error"] == 0, sample
                assert sample["gun_error_cm"] <= .01 and sample["gun_error_deg"] <= .01, sample
        assert not sample["display_error"] and not sample["recoil_error"] and sample["hand_goal_error"] <= .01, sample
        assert .5 < sample["source_maximum"] <= 8, "Native source curve must have actual bounded motion"
    return sample


def fire(pawn):
    before = prop(pawn, "ShotSequence")
    pawn.call_method("PC_RequestFire", args=(pawn.get_actor_location() + unreal.Vector(0, 0, 70), unreal.Vector(0, 0, 1)))
    return prop(pawn, "ShotSequence") - before


def screenshot(world, pawn, name, sample):
    path = OUT / (pawn.get_actor_label() + "_" + name + ".png")
    if MODE == "visual_isolated" and not pawn.is_player_controlled():
        review_capture.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, review_target, OUT.as_posix(), path.name)
        assert path.is_file() and path.stat().st_size > 10000
    else:
        unreal.SystemLibrary.execute_console_command(world, 'HighResShot 1600x900 filename="' + path.as_posix() + '"')
    report.setdefault("captures", []).append({"file": path.name, "requested_sample": sample,
        "unpaused": True, "exact_render_pose_not_assumed": True,
        "isolated_diagnostic_only": MODE == "visual_isolated" and not pawn.is_player_controlled()})


def frame_subject(world, pawn):
    global review_camera, peak_requested, before_requested, review_capture, review_target, review_light
    peak_requested = False
    before_requested = False
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
        if not a.is_player_controlled():
            gun = prop(a, "WeaponAppearance")
            if gun:
                gun.set_actor_hidden_in_game(a != pawn)
    if pawn.is_player_controlled():
        pc.set_view_target_with_blend(pawn, 0)
        return
    if review_camera is None:
        transform = unreal.Transform(location=unreal.Vector(0, 0, 0))
        api = unreal.get_default_object(unreal.GameplayStatics.static_class())
        review_camera = api.call_method("BeginDeferredActorSpawnFromClass", args=(world, unreal.CameraActor.static_class(), transform,
            unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        review_camera = api.call_method("FinishSpawningActor", args=(review_camera, transform, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        review_camera.get_component_by_class(unreal.CameraComponent).set_field_of_view(40)
    for a in subjects:
        if not a.is_player_controlled():
            a.set_actor_hidden_in_game(a != pawn)
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.ParisFirstPersonApprovedActor):
        a.set_actor_hidden_in_game(True)
    point = pawn.get_actor_location()
    eye = point + pawn.get_actor_forward_vector() * 450 + pawn.get_actor_right_vector() * 300 + unreal.Vector(0, 0, 35)
    target = point + unreal.Vector(0, 0, -10)
    review_camera.set_actor_location(eye, False, False)
    review_camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(eye, target), False)
    pc.set_view_target_with_blend(review_camera, 0)
    if MODE == "visual_isolated":
        if review_light is None:
            api = unreal.get_default_object(unreal.GameplayStatics.static_class())
            light_transform = unreal.Transform(location=eye)
            review_light = api.call_method("BeginDeferredActorSpawnFromClass", args=(world, unreal.PointLight.static_class(), light_transform,
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            review_light = api.call_method("FinishSpawningActor", args=(review_light, light_transform, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            light = review_light.get_component_by_class(unreal.PointLightComponent)
            light.set_mobility(unreal.ComponentMobility.MOVABLE)
            light.set_intensity_units(type(prop(light,"intensity_units")).LUMENS)
            light.set_intensity(10000)
            light.set_attenuation_radius(1200)
            light.set_cast_shadows(False)
            report["diagnostic_light"] = {"intensity":10000,"units":str(prop(light,"intensity_units")),"radius_cm":1200,"saved":False}
        review_light.set_actor_location(eye,False,False)
        if review_capture is None:
            api = unreal.get_default_object(unreal.GameplayStatics.static_class())
            transform = unreal.Transform(location=eye)
            capture_actor = api.call_method("BeginDeferredActorSpawnFromClass", args=(world, unreal.SceneCapture2D.static_class(), transform,
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            capture_actor = api.call_method("FinishSpawningActor", args=(capture_actor, transform, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            review_capture = capture_actor.get_component_by_class(unreal.SceneCaptureComponent2D)
            review_target = unreal.RenderingLibrary.create_render_target2d(world,1600,900,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.12,.14,.17,1),False,False)
            review_capture.set_editor_property("texture_target", review_target)
            review_capture.set_editor_property("primitive_render_mode", unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
            review_capture.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            review_capture.set_editor_property("capture_every_frame", False)
            review_capture.set_editor_property("capture_on_movement", False)
            review_capture.set_editor_property("fov_angle", 40)
            review_capture.set_editor_property("show_flag_settings", [unreal.EngineShowFlagsSetting(show_flag_name=n,enabled=False)
                for n in ("Fog","Atmosphere","Bloom","DepthOfField","MotionBlur")])
        review_capture.set_world_location(eye,False,False)
        review_capture.set_world_rotation(unreal.MathLibrary.find_look_at_rotation(eye,target),False,False)
        review_capture.clear_show_only_components()
        review_capture.set_editor_property("show_only_actors", [pawn,prop(pawn,"WeaponAppearance")])


def native_contract(world):
    for pawn in subjects:
        label = pawn.get_actor_label()
        state = lambda: shot_sample(world, pawn)
        initial = state()["recoil_starts"]
        total = prop(pawn, "LoadedAmmo") + prop(pawn, "ReserveAmmo")
        assert initial == 0 and fire(pawn) == 1 and fire(pawn) == 0
        yield .5, lambda: state()["recoil_active"]
        assert state()["recoil_starts"] == initial + 1
        yield .3, None
        assert fire(pawn) == 1
        yield .5, lambda: state()["recoil_active"]
        assert state()["recoil_starts"] == initial + 2 and prop(pawn, "LoadedAmmo") == 0
        yield .3, None
        assert unreal.GameplayStatics.get_time_seconds(world) >= prop(pawn, "NextShotTime")
        assert fire(pawn) == 0
        yield 1., None
        assert not state()["recoil_active"] and state()["recoil_starts"] == initial + 2
        pawn.call_method("PC_RequestReload")
        assert str(prop(pawn, "ActionState")) == "Reloading" and fire(pawn) == 0
        yield 8., lambda: str(prop(pawn, "ActionState")) == "Ready"
        assert prop(pawn, "LoadedAmmo") == 8 and prop(pawn, "LoadedAmmo") + prop(pawn, "ReserveAmmo") == total - 2
        assert state()["recoil_starts"] == initial + 2 and not state()["recoil_active"]
        assert fire(pawn) == 1
        yield .5, lambda: state()["recoil_active"]
        pawn.call_method("PC_RequestReload")
        assert str(prop(pawn, "ActionState")) == "Reloading" and fire(pawn) == 0
        yield .5, lambda: not state()["recoil_active"]
        assert state()["recoil_starts"] == initial + 3
        yield 8., lambda: str(prop(pawn, "ActionState")) == "Ready"
        assert not state()["recoil_active"] and state()["recoil_starts"] == initial + 3
        assert fire(pawn) == 1
        yield .5, lambda: state()["recoil_active"]
        pawn.call_method("PC_Die")
        assert prop(pawn, "IsDead") and fire(pawn) == 0
        yield .5, lambda: not state()["recoil_active"]
        assert state()["recoil_starts"] == initial + 4
        generation = prop(pawn, "RestoreGeneration")
        pawn.call_method("PC_ResetLifecycle")
        assert prop(pawn, "RestoreGeneration") == generation + 1 and not prop(pawn, "IsDead")
        yield .4, None
        assert not state()["recoil_active"] and state()["recoil_starts"] == initial + 4
        assert fire(pawn) == 1
        yield .5, lambda: state()["recoil_active"]
        assert state()["recoil_starts"] == initial + 5
        pawn.call_method("PC_ResetLifecycle")
        yield .5, lambda: not state()["recoil_active"]
        yield .4, None
        assert not state()["recoil_active"] and state()["recoil_starts"] == initial + 5
        assert prop(pawn, "LoadedAmmo") + prop(pawn, "ReserveAmmo") == total - 5
        report.setdefault("native_contract", {})[label] = {
            "five_commits_five_starts": True, "repeat_restarts_source": True,
            "cooldown_empty_busy_dead_reject": True, "reload_interrupt_and_return_no_replay": True,
            "death_reset_and_ready_reset_cancel": True}


def tick(delta):
    global phase, stamp, subjects, subject_index, shot_before, scenario, pending, peak_requested, before_requested
    try:
        assert time.monotonic() - started < 210, (phase, "deadline")
        editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        world = editor.get_game_world()
        if phase == "end":
            if world is None:
                finish()
            return
        if world is None:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        if phase == "visual_return":
            if now - stamp >= .5:
                subject_index += 1
                if subject_index == len(subjects):
                    phase = "end"
                    levels.editor_request_end_play()
                else:
                    phase, stamp = "quiet", now
                    frame_subject(world, subjects[subject_index])
            return
        if phase == "wait":
            if now < 4:
                return
            chars = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)}
            for a in chars.values():
                if not a.is_player_controlled():
                    c = unreal.AIHelperLibrary.get_ai_controller(a)
                    c.call_method("PC_EnableCombat", args=(False,))
                    c.call_method("PC_EnablePolicy", args=(False,))
                    c.call_method("PC_PolicyHold")
                    c.stop_movement()
            subjects = [unreal.GameplayStatics.get_player_character(world, 0), chars["PC_City_Ally1"], chars["PC_City_Enemy1"]]
            assert all(prop(a, "Health") == 100 and prop(a, "ShotSequence") == 0 and prop(a, "LoadedAmmo") == 2 for a in subjects)
            phase, stamp = "quiet", now
            if MODE in ("visual", "visual_isolated"):
                frame_subject(world, subjects[0])
            if MODE == "contract":
                scenario = native_contract(world)
                phase = "contract"
        if phase == "contract":
            for pawn in subjects:
                sample = shot_sample(world, pawn)
                sample["stage"] = "contract"
                report["samples"].append(sample)
            if pending is not None:
                duration, condition = pending
                if condition is not None:
                    if not condition():
                        assert now - stamp < duration, "Native contract condition deadline"
                        return
                elif now - stamp < duration:
                    return
            try:
                pending = next(scenario)
                stamp = now
            except StopIteration:
                report["summary"] = report["native_contract"]
                phase = "end"
                levels.editor_request_end_play()
            return
        if phase in ("quiet", "shot"):
            pawn = subjects[subject_index]
            sample = shot_sample(world, pawn)
            sample["stage"] = phase
            report["samples"].append(sample)
            if MODE in ("visual", "visual_isolated") and phase == "quiet" and now - stamp >= .3 and not before_requested:
                screenshot(world, pawn, "before", sample)
                before_requested = True
            if phase == "quiet" and now - stamp >= .75:
                shot_before = sample
                pawn.call_method("PC_RequestFire", args=(pawn.get_actor_location() + unreal.Vector(0, 0, 70), unreal.Vector(0, 0, 1)))
                assert prop(pawn, "ShotSequence") == shot_before["sequence"] + 1
                pawn.call_method("PC_RequestFire", args=(pawn.get_actor_location() + unreal.Vector(0, 0, 70), unreal.Vector(0, 0, 1)))
                assert prop(pawn, "ShotSequence") == shot_before["sequence"] + 1, "Cooldown rejection must not commit"
                phase, stamp = "shot", now
            elif phase == "shot" and MODE in ("visual", "visual_isolated") and not peak_requested and sample["recoil_active"] and sample["recoil_age"] >= .075:
                screenshot(world, pawn, "during", sample)
                peak_requested = True
            elif phase == "shot" and now - stamp >= 1:
                assert prop(pawn, "LoadedAmmo") == shot_before["ammo"][0] - 1
                if MODE in ("candidate", "visual", "visual_isolated", "installed"):
                    observed = [s for s in report["samples"] if s["label"] == sample["label"] and s["stage"] == "shot"]
                    assert sample["recoil_starts"] == 1 and not sample["recoil_active"], sample
                    assert any(s["recoil_active"] for s in observed), "No native recoil observation"
                    assert sum(s["recoil_active"] for s in observed) >= 8, "Insufficient actual recoil frame observations"
                    distance = lambda a, b: sum((x-y)**2 for x,y in zip(a,b))**.5
                    excursion = max(distance(s["gun"]["t"], shot_before["gun"]["t"]) for s in observed)
                    assert excursion > .5, (sample["label"], "No visible-transform excursion", excursion)
                    attachment = max(distance(s["gun_hand"]["t"], shot_before["gun_hand"]["t"]) for s in observed)
                    assert attachment <= .01, (sample["label"], "Gun-hand binding moved", attachment)
                    report.setdefault("candidate_excursion_cm", {})[sample["label"]] = excursion
                    report.setdefault("gun_hand_delta_cm", {})[sample["label"]] = attachment
                    if MODE in ("visual", "visual_isolated"):
                        assert peak_requested
                        screenshot(world, pawn, "return", sample)
                        phase, stamp = "visual_return", now
                        return
                subject_index += 1
                if subject_index == len(subjects):
                    report["summary"] = {"subjects": [a.get_actor_label() for a in subjects],
                        "each_committed_one_shot": True, "each_cooldown_rejected": True,
                        "actions_during_shots": sorted(set(s["action"] for s in report["samples"] if s["stage"] == "shot")),
                        "cadence_max": max(b["time"] - a["time"] for a, b in zip(report["samples"], report["samples"][1:]) if b["label"] == a["label"])}
                    phase = "end"
                    levels.editor_request_end_play()
                else:
                    phase, stamp = "quiet", now
                    if MODE in ("visual", "visual_isolated"):
                        frame_subject(world, subjects[subject_index])
    except Exception:
        report["errors"].append(traceback.format_exc())
        finish()


try:
    report["protected_count"] = len(guards())
    if MODE == "native_source":
        native_source_probe()
        finish()
    elif MODE == "source":
        clip_probe()
        finish()
    else:
        settings = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings"))
        old_throttle = prop(settings, "bThrottleCPUWhenNotForeground")
        settings.set_editor_property("bThrottleCPUWhenNotForeground", False)
        # Loading can pump Slate. Do not register a callback until synchronous
        # map loading and the one-time unsaved isolation setup are complete.
        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        assert levels.load_level(MAP)
        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        for a in actors.get_all_level_actors():
            if isinstance(a, unreal.Character):
                a.set_actor_hidden_in_game(True)
        unreal.EditorPythonScripting.set_keep_python_script_alive(True)
        callback = unreal.register_slate_post_tick_callback(tick)
        levels.editor_request_begin_play()
except Exception:
    report["errors"].append(traceback.format_exc())
    finish()
