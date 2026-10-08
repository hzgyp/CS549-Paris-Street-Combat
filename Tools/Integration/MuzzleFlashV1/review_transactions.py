"""Record actual agent inspection separately; never infer visibility from counters."""
import argparse
import json

from common import BASE, sha, write
from runtime_audit import transaction_receipt
from formal_contract import approved_profiles, APPROVAL_ID


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("identity")
    parser.add_argument("--visible-file", action="append", default=[])
    parser.add_argument("--reject-role", action="append", default=[])
    parser.add_argument("--all-originals-inspected", action="store_true", required=True)
    parser.add_argument("--notes", required=True)
    args = parser.parse_args()
    result, _ = transaction_receipt(args.identity, require_visual=False)
    approved_profiles()
    directory = BASE / args.identity
    output = directory / "visual_review.json"
    assert not output.exists(), "Preserve occupied visual review"
    assert args.all_originals_inspected
    captures = {row["file"]: row for row in result["captures"]}
    readable = {}
    for name in args.visible_file:
        image = captures[name]
        assert image["kind"] == "pulse"
        readable.setdefault(image["label"], []).append(name)
    labels = {row["label"] for row in result["subjects_final"]}
    rejected = set(args.reject_role)
    assert rejected <= labels and not (rejected & set(readable))
    assert set(readable) | rejected == labels, "Every role needs an explicit visual finding"
    write(output, {"native_result_sha256": sha(directory / "result.json"),
        "status": "failed_readable_flame_preserve" if rejected else "pass_original_visual_review",
        "candidate_runtime_visual_admitted": not rejected, "all_originals_inspected": True,
        "images": [{"file": r["file"], "sha256": r["sha256"]} for r in result["captures"]],
        "readable_flame": readable, "unreadable_roles": sorted(rejected),
        "reviewer": "agent inspecting each unedited original",
        "human_reviewed_this_transaction_image_set": False,
        "earlier_human_size_approval_sha256": sha(BASE / APPROVAL_ID / "approval.json"),
        "notes": args.notes, "scope": "presentation only, not city-clearance/ballistics/FPS/Shipping/MVP"})
    print("Actual original-image review recorded separately from native result")
