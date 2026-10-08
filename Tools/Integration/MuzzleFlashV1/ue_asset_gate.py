"""Purchased asset hard-reference/class/compile gate; never save source packages."""
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, BASE, guards, intake_rows, write
from asset_gate_contract import classify_systems

OUT = BASE / os.environ["CS549_MUZZLE_ID"]
INTAKE = BASE / os.environ["CS549_MUZZLE_INTAKE"] / "intake.json"
report = {"identity": os.environ["CS549_MUZZLE_ID"], "errors": [], "systems": [],
          "dependencies": [], "native_save": False, "map_saved": False, "runtime_passed": False}
report["state_transitions"] = []
report["rendering_enabled"] = os.environ.get("CS549_MUZZLE_RENDERING") == "true"
started = time.monotonic()
callback = None
systems = []


def progress(stage, package=None):
    report["stage"] = stage
    report["current_package"] = package
    write(OUT / "progress.json", {"stage": stage, "package": package,
          "elapsed_seconds": time.monotonic() - started})
    print("MUZZLE_GATE " + stage + " " + str(package), flush=True)


def finish():
    global callback
    try:
        report["guard_count"] = len(guards())
        report["original_intake_count"] = len(intake_rows())
    except Exception:
        report["errors"].append(traceback.format_exc())
    report["status"] = "pass_purchased_native_dependency_and_compile_gate_runtime_unpassed" if not report["errors"] else "failed_purchased_asset_gate_preserve"
    write(OUT / "result.json", report)
    if callback is not None:
        unreal.unregister_slate_post_tick_callback(callback)
        callback = None
    unreal.SystemLibrary.quit_editor()


def tick(dt):
    try:
        assert time.monotonic() - started < 180, "Purchased Niagara compilation gate timed out"
        current = [json.loads(unreal.ParisMuzzleFlashLibrary.inspect_purchased_system(s)) for s in systems]
        report["systems"] = current
        state = classify_systems(current)
        signature = [(x["valid"], x["ready"], x.get("compiling", False)) for x in current]
        if not report["state_transitions"] or signature != report["state_transitions"][-1]["signature"]:
            report["state_transitions"].append({"state": state, "signature": signature,
                "elapsed_seconds": time.monotonic() - started})
            progress(state)
        if state != "ready":
            return
        finish()
    except Exception:
        report["errors"].append(traceback.format_exc())
        finish()


try:
    progress("native_registry")
    data = json.loads(INTAKE.read_text())
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([data["package_root"]], force_rescan=True)
    hard_options = unreal.AssetRegistryDependencyOptions(
        include_soft_package_references=False, include_hard_package_references=True,
        include_searchable_names=False, include_soft_management_references=False,
        include_hard_management_references=False)
    soft_options = unreal.AssetRegistryDependencyOptions(
        include_soft_package_references=True, include_hard_package_references=False,
        include_searchable_names=False, include_soft_management_references=False,
        include_hard_management_references=False)
    for row in data["closure"]:
        package = row["package"]
        progress("classify_dependencies", package)
        hard = registry.get_dependencies(package, hard_options)
        soft = registry.get_dependencies(package, soft_options)
        assert hard is not None and soft is not None, "Unavailable registry dependency data: " + package
        missing_hard = [str(p) for p in hard if str(p).startswith(("/Game/", "/Engine/", "/Niagara/"))
                        and not unreal.EditorAssetLibrary.does_asset_exist(str(p))]
        missing_soft = [str(p) for p in soft if str(p).startswith(("/Game/", "/Engine/", "/Niagara/"))
                        and not unreal.EditorAssetLibrary.does_asset_exist(str(p))]
        report["dependencies"].append({"package": package, "hard": [str(p) for p in hard],
            "soft": [str(p) for p in soft], "missing_hard": missing_hard, "missing_soft": missing_soft})
    missing = [d for d in report["dependencies"] if d["missing_hard"]]
    assert not missing, "Actual missing hard dependencies: " + str(missing)
    for package in data["candidates"]:
        progress("load_purchased_system", package)
        system = unreal.load_asset(package)
        assert isinstance(system, unreal.NiagaraSystem), "Actual class is not NiagaraSystem: " + package
        systems.append(system)
        progress("request_purchased_compile", package)
        unreal.ParisMuzzleFlashLibrary.request_purchased_compile(system)
    progress("wait_compile_callbacks")
    callback = unreal.register_slate_post_tick_callback(tick)
except Exception:
    report["errors"].append(traceback.format_exc())
    finish()
