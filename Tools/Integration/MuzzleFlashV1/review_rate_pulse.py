"""Separate assistant observation receipt, never a human approval or raw rewrite."""
import argparse
import json
import struct

from common import BASE, ROOT, INTAKE, guards, intake_rows, sha, write


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--all-originals-inspected", action="store_true", required=True)
    args = parser.parse_args()
    assert args.all_originals_inspected
    out = BASE / "rate_pulse_v1_20261008"
    target = out / "visual_review.json"
    assert not target.exists(), "Preserve occupied review identity"
    native = json.loads((out / "result.json").read_text())
    log = json.loads((out / "log_validation.json").read_text(encoding="utf-8-sig"))
    assert native["status"] == "pass_rate_pulse_native_completion_human_review_pending"
    assert native["activation_count"] == 1 and not native["errors"]
    assert native["requested_emission_seconds"] == .10
    assert native["instance_override"]["typed_readback"] == {"value": 20., "valid": True}
    assert len(native["natural_completions"]) == 1
    assert native["natural_completions"][0]["complete"] and native["natural_completions"][0]["age"] <= 8
    assert log["strict_errors"] == log["exit_code"] == 0 and not log["timed_out"]
    assert len(native["captures"]) == 12
    images = []
    for i, capture in enumerate(native["captures"]):
        file = out / capture["file"]
        assert file.name == "rifle_01_%02d.png" % i
        assert sha(file) == capture["sha256"]
        with file.open("rb") as stream:
            header = stream.read(24)
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        dimensions = struct.unpack(">II", header[16:24])
        assert dimensions == (1600, 900)
        images.append({"file": file.name, "sha256": sha(file), "dimensions": dimensions,
            "requested_age": capture["requested_sample"]["age"], "exact_render_age_not_assumed": True,
            "original_inspected": True, "visible_flame": 3 <= i <= 7,
            "visible_spark_only": 8 <= i <= 11, "black_no_visible_effect": i <= 2})
    intake = json.loads((BASE / "intake_remaining_pulse_v1_20261007/intake.json").read_text())
    candidate = ROOT / "tmp/muzzle-flash-v1/Candidate_intake_remaining_pulse_v1_20261007/Content/MsvFx_MuzzleFlash_Pack"
    assert len(intake["closure"]) == 25
    for row in intake["closure"]:
        file = candidate / (ROOT / row["path"]).relative_to(INTAKE)
        assert file.stat().st_size == row["size_bytes"] and sha(file) == row["sha256"]
    review = {"identity": out.name, "native_result_sha256": sha(out / "result.json"),
        "review_basis": "assistant inspected all12 unedited originals using view_image original",
        "status": "visible_isolated_rate_pulse_human_review_pending", "images": images,
        "human_approved": False, "candidate_admitted": False, "formal_integration": False,
        "guard_count": len(guards()), "original_intake_count": len(intake_rows()),
        "candidate_exact_package_count": 25,
        "limits": ["No exact first-pixel timing from capture request ages",
                   "No scale/axis/gun socket/real shot/lifecycle acceptance",
                   "Rate and timer/capture observer changed: not exclusive rate-cause proof",
                   "12frame budget ends at0.202839s; completion at1.252348s is native state, not a late image"]}
    write(target, review)
    print(json.dumps({k: review[k] for k in ("status", "human_approved", "guard_count", "original_intake_count")}))


if __name__ == "__main__":
    main()
