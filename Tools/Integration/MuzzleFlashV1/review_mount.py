"""Record completed manual inspection of all26 originals, never edit raw receipts."""
import ast
import json
from pathlib import Path
import subprocess

from common import BASE, ROOT, INTAKE, guards, intake_rows, sha, write


def review():
    directory = BASE / "mount_named_rotation_v2_20261008"
    result_file = directory / "result.json"
    result = json.loads(result_file.read_text())
    log = json.loads((directory / "log_validation.json").read_text(encoding="utf-8-sig"))
    assert result["status"] == "pass_measured_mount_native_completion_visual_pending" and not result["errors"]
    assert log["exit_code"] == 0 and log["strict_errors"] == 0 and not log["timed_out"]
    assert result["activation_count"] == 2 and len(result["completions"]) == 2
    assert result["positional_constructor_readback"] == {"pitch": 90., "yaw": 0., "roll": 0.}
    for row in result["completions"]:
        assert row["component_valid"] and row["complete"] and not row["active"] and row["age"] <= 8
    assert len(result["captures"]) == 26
    images = []
    for row in result["captures"]:
        file = directory / row["file"]
        assert sha(file) == row["sha256"] and file.stat().st_size == row["bytes"]
        number = int(file.stem.rsplit("_", 1)[1])
        if number in (0, 13):
            finding = "original_rifle_before_pulse_diagnostic_fill_some_highlight_saturation"
        elif number in range(1, 6) or number in range(14, 18):
            finding = "rifle_visible_no_flame"
        elif number in (12, 25):
            finding = "main_flame_gone_remaining_sparks"
        else:
            finding = "clear_outward_flame_unit_scale_large_covers_barrel_segment_tail_clipped_in_later_frames"
        images.append({"file": file.name, "sha256": row["sha256"], "finding": finding,
                       "inspected_original": True, "image_edited": False})
    samples = result["samples"]
    evidence = {"native_result_sha256": sha(result_file), "images": images,
        "status": "failed_unit_scale_visual_admission_human_decision_pending",
        "native_position_direction_completion_passed": True,
        "clear_early_flame_observed_each_rifle": True, "human_approved": False,
        "scale_accepted": False, "candidate_admitted": False,
        "exact_full_flame_length_claimed": False,
        "limitation": "Large flash overlaps barrel; peak tail clips camera edge. Do not infer full world size or zero-overlap from component origin.",
        "diagnostic_lighting_not_production_material_change": True,
        "maximum_position_error_cm": max(s["mount_position_error_cm"] for s in samples),
        "maximum_forward_vector_error": max(s["mount_forward_error"] for s in samples),
        "completion_seconds": [s["age"] for s in result["completions"]],
        "first_inactive_observed_seconds": [next(s["age"] for s in samples if s["rifle_index"] == i and not s["active"]) for i in range(2)],
        "request_ages_not_exact_render_ages": True,
        "no_city_transaction_or_formal_install": True}
    for name in ("visual_review.json", "final_verification.json"):
        assert not (directory / name).exists(), "Preserve occupied review"
    verification = {"guard_count": len(guards()), "original_intake_count": len(intake_rows())}
    intake = json.loads((BASE / "intake_transaction_v1_20261008/intake.json").read_text())
    candidate = ROOT / "tmp/muzzle-flash-v1/Candidate_intake_transaction_v1_20261008/Content/MsvFx_MuzzleFlash_Pack"
    assert len(intake["closure"]) == 25
    for row in intake["closure"]:
        file = candidate / (ROOT / row["path"]).relative_to(INTAKE)
        assert file.stat().st_size == row["size_bytes"] and sha(file) == row["sha256"]
    verification["private_candidate_exact_packages"] = 25
    tools = list((ROOT / "Tools/Integration/MuzzleFlashV1").glob("*.py"))
    for file in tools:
        ast.parse(file.read_text(encoding="utf-8"))
    verification["python_sources_parsed"] = len(tools)
    process_query = r'''Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'UnrealEditor*' -or ($_.ProcessId -ne $PID -and $_.Name -match '^(powershell|pwsh|python|pythonw)\.exe$' -and $_.CommandLine -match 'Tools[/\\]Integration[/\\].*(run_|launch_)')} | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Depth 3'''
    output = subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", process_query], text=True)
    verification["native_or_integration_launcher_inventory"] = json.loads(output) if output.strip() else []
    write(directory / "visual_review.json", evidence)
    write(directory / "final_verification.json", verification)
    print(json.dumps({"review_status": evidence["status"], "images": len(images), **verification}, indent=2))


if __name__ == "__main__":
    review()
