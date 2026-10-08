"""Finite isolated field observation only; no probe, route, rebuild or admission."""
import ast
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal
ROOT, OUT = Path(os.environ["CS549_PURE_ROOT"]), Path(os.environ["CS549_PURE_OUT"])
sys.path.insert(0, str(ROOT / "Tools/Integration/NPCInteractionV1"))
from common import guard_rows, guards_match
rows = guard_rows()
assert len(rows) == 703 and guards_match(rows)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
report = {"identity": OUT.name, "status": "diagnostic_only_no_admission", "errors": [], "steps": [],
          "summary": {"physical_attempts": 0}, "protected_bytes_unchanged": False}
tree = ast.parse((OUT / "snapshot_source.py").read_text())
selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("xyz", "vehicle_snapshot")]
exec(compile(ast.Module(body=selected, type_ignores=[]), "installed_snapshot_functions", "exec"))
started, phase, callback = time.monotonic(), "setup", None
busy = False
gm = perf = saving = None
old = {}

def write(): (OUT / "survey.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")

def finish(error=None):
    global phase
    if error: report["errors"].append(error)
    if levels.is_in_play_in_editor(): levels.editor_request_end_play(); phase = "ending"; write(); return
    if gm:
        for k in ("default_pawn_class", "hud_class"): gm.set_editor_property(k, old[k])
    if perf: perf.set_editor_property("bThrottleCPUWhenNotForeground", old["throttle"])
    if saving: saving.set_editor_property("bAutoSaveEnable", old["auto_save"])
    report["protected_bytes_unchanged"] = guards_match(rows)
    assert report["protected_bytes_unchanged"]
    phase = "done"; write(); unreal.unregister_slate_post_tick_callback(callback); unreal.SystemLibrary.quit_editor()

def tick(_):
    global phase, gm, perf, saving, busy
    if busy or phase == "done": return
    busy = True
    try:
        assert time.monotonic()-started < 300
        if (OUT / "STOP_REQUEST.json").exists() and phase != "ending":
            finish("Owned strict stop: " + (OUT / "STOP_REQUEST.json").read_text(encoding="utf-8-sig")); return
        if phase == "ending":
            if editor.get_game_world() is None: finish()
            return
        if phase == "setup":
            saving = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorLoadingSavingSettings"))
            old["auto_save"] = saving.get_editor_property("bAutoSaveEnable"); saving.set_editor_property("bAutoSaveEnable", False)
            perf = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings"))
            old["throttle"] = perf.get_editor_property("bThrottleCPUWhenNotForeground"); perf.set_editor_property("bThrottleCPUWhenNotForeground", False)
            assert unreal.EditorLevelLibrary.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
            world = editor.get_editor_world()
            for a in list(actors.get_all_level_actors()):
                if isinstance(a, unreal.Character) or a.get_class().get_path_name().startswith(("/Game/ParisCombat/", "/Script/Paris")):
                    assert actors.destroy_actor(a)
                elif isinstance(a, unreal.Pawn):
                    a.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
                    a.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.DISABLED)
            world.get_world_settings().set_editor_property("default_game_mode", unreal.GameModeBase.static_class())
            gm = unreal.get_default_object(unreal.GameModeBase)
            for k in ("default_pawn_class", "hud_class"): old[k] = gm.get_editor_property(k); gm.set_editor_property(k, None)
            levels.editor_request_begin_play(); phase = "runtime"; write(); return
        world = editor.get_game_world()
        if not world or unreal.GameplayStatics.get_time_seconds(world) < 2: return
        for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
            if a.get_class().get_path_name().startswith(("/Game/ParisCombat/", "/Script/Paris")): a.destroy_actor()
        vehicles = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Pawn) if a.get_class().get_path_name().startswith("/Game/WW2City/CarsSet/")]
        assert len(vehicles) == 1
        vehicle = vehicles[0]; assert vehicle.get_controller() is None
        report["steps"].append({"operation": "before", "snapshot": vehicle_snapshot(vehicle)}); write()
        vehicle.set_actor_tick_enabled(False)
        for c in vehicle.get_components_by_class(unreal.ActorComponent):
            c.set_component_tick_enabled(False)
            if isinstance(c, unreal.MovementComponent): c.deactivate()
        report["steps"].append({"operation": "ticks_disabled", "snapshot": vehicle_snapshot(vehicle)}); write()
        for c in vehicle.get_components_by_class(unreal.PrimitiveComponent):
            c.set_simulate_physics(False)
            report["steps"].append({"operation": "simulate_false:"+c.get_path_name(), "snapshot": vehicle_snapshot(vehicle)}); write()
            if isinstance(c, unreal.SkeletalMeshComponent):
                c.set_all_bodies_simulate_physics(False)
                report["steps"].append({"operation": "all_bodies_false:"+c.get_path_name(), "snapshot": vehicle_snapshot(vehicle)}); write()
        finish()
    except Exception: finish(traceback.format_exc())
    finally: busy = False

callback = unreal.register_slate_post_tick_callback(tick)
