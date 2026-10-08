"""Record manual inspection of the single quarter-scale comparison, not adoption."""
import ast
import json
import subprocess

from common import BASE, ROOT, INTAKE, guards, intake_rows, sha, write
from scale_contract import IDENTITY, INSTANCE_SCALE, scaled_profiles
from geometry_mounts import measured_profiles


def review():
    directory = BASE / IDENTITY
    for name in ("visual_review.json", "final_verification.json"):
        assert not (directory / name).exists(), "Preserve occupied review"
    result_file = directory / "result.json"
    result = json.loads(result_file.read_text())
    log = json.loads((directory / "log_validation.json").read_text(encoding="utf-8-sig"))
    assert result["identity"] == IDENTITY and result["instance_scale"] == INSTANCE_SCALE
    assert result["status"] == "pass_measured_mount_native_completion_visual_pending" and not result["errors"]
    assert log == {"exit_code": 0, "strict_errors": 0, "timed_out": False}
    assert result["profiles"] == scaled_profiles(measured_profiles())
    assert result["same_camera_and_lighting_as_unit_mount"]
    assert result["activation_count"] == len(result["completions"]) == 2
    for row in result["completions"]:
        assert row["component_valid"] and row["complete"] and not row["active"] and row["age"] <= 8
    for row in result["samples"]:
        assert row["relative_scale"] == [.25] * 3
        assert row["mount_position_error_cm"] <= .01 and row["mount_forward_error"] <= .0001
        assert row["instance_rate_valid"] and row["instance_rate"] == 20
    assert len(result["captures"]) == 26
    images = []
    for number, row in enumerate(result["captures"]):
        file = directory / row["file"]
        assert int(file.stem.rsplit("_", 1)[1]) == number
        assert sha(file) == row["sha256"] and file.stat().st_size == row["bytes"]
        if number in (0, 13):
            finding = "before_pulse_rifle_visible_diagnostic_highlight_saturation"
        elif number in (5, 17, 18, 19):
            finding = "clear_compact_outward_main_flame_contained_in_frame"
        elif number in (6, 7, 20, 21, 22, 23):
            finding = "main_flame_gone_remaining_spark_some_edge_clipping"
        elif number in (1, 2, 3, 4, 14, 15, 16):
            finding = "early_rifle_visible_no_flame"
        else:
            finding = "later_rifle_visible_no_visible_particles"
        images.append({"file": file.name, "sha256": row["sha256"], "finding": finding,
                       "inspected_original": True, "image_edited": False})
    evidence = {
        "status": "pass_compact_flame_comparison_human_size_review_pending",
        "native_result_sha256": sha(result_file), "images": images,
        "review_source_sha256": sha(__file__), "instance_scale": INSTANCE_SCALE,
        "clear_early_flame_observed_each_rifle": True, "visible_flame_smaller_than_unit_baseline": True,
        "main_flame_contained_in_inspected_frames": True,
        "human_approved": False, "scale_accepted": False, "candidate_admitted": False,
        "sampled_frame_pixel_ratio_or_world_length_claimed": False,
        "zero_barrel_overlap_claimed": False,
        "limitations": "Only one pulse each; stochastic particles and different request ages are not exact pixel-ratio/timing proof. M1 has one clear main-flame frame, German three; sparks reach the camera edge. Diagnostic highlights saturate. No reverse-view, first-person, city transaction or formal installation acceptance.",
        "completion_seconds": [row["age"] for row in result["completions"]],
        "maximum_position_error_cm": max(s["mount_position_error_cm"] for s in result["samples"]),
        "maximum_forward_vector_error": max(s["mount_forward_error"] for s in result["samples"]),
        "ordinary_deactivate_request_seconds": .10, "exact_callback_age_observed": False,
        "no_city_transaction_or_formal_install": True,
    }
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
    query = r'''Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'UnrealEditor*' -or ($_.ProcessId -ne $PID -and $_.Name -match '^(powershell|pwsh|python|pythonw)\.exe$' -and $_.CommandLine -match 'Tools[/\\]Integration[/\\].*(run_|launch_)')} | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Depth 3'''
    output = subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", query], text=True)
    verification["native_or_integration_launcher_inventory"] = json.loads(output) if output.strip() else []
    assert not verification["native_or_integration_launcher_inventory"], "Do not claim native slot release"
    write(directory / "visual_review.json", evidence)
    write(directory / "final_verification.json", verification)
    print(json.dumps({"review_status": evidence["status"], "images": len(images), **verification}, indent=2))


if __name__ == "__main__":
    review()
