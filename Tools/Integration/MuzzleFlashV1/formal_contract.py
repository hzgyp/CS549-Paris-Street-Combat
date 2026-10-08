"""Approved size receipt and narrow formal integration identities."""
import json

from common import BASE, guards, intake_rows, sha, write
from geometry_mounts import measured_profiles
from scale_contract import scaled_profiles, IDENTITY

APPROVAL_ID = "size_approval_v1_20261008"
BUILD_ID = "native_formal_v13_20261008"
INTAKE_ID = "intake_formal_v6_20261008"
PROFILE_PACKAGE = "/Game/ParisCombat/VFX/MuzzleFlashV1/DA_PC_MuzzleFlashV1"
AUTHORITY = "2026-10-08 user approves smaller muzzle images and requests formal local asset integration"


def approved_profiles():
    approval = json.loads((BASE / APPROVAL_ID / "approval.json").read_text())
    assert approval["authorization"] == AUTHORITY and approval["human_size_accepted"]
    assert approval["native_result_sha256"] == sha(BASE / IDENTITY / "result.json")
    assert approval["visual_review_sha256"] == sha(BASE / IDENTITY / "visual_review.json")
    profiles = scaled_profiles(measured_profiles())
    profiles["human_scale_accepted"] = True
    profiles["status"] = "human_size_accepted_local_integration_pending_runtime_gates"
    return profiles


if __name__ == "__main__":
    out = BASE / APPROVAL_ID
    assert not out.exists(), "Preserve occupied approval"
    guard_count, source_count = len(guards()), len(intake_rows())
    review = json.loads((BASE / IDENTITY / "visual_review.json").read_text())
    assert review["visible_flame_smaller_than_unit_baseline"] and len(review["images"]) == 26
    for row in review["images"]:
        assert sha(BASE / IDENTITY / row["file"]) == row["sha256"]
    out.mkdir()
    write(out / "approval.json", {"authorization": AUTHORITY,
        "user_message": "非常好，同步的正式资产", "human_size_accepted": True,
        "instance_scale": .25, "guard_count": guard_count, "source_count": source_count,
        "native_result_sha256": sha(BASE / IDENTITY / "result.json"),
        "visual_review_sha256": sha(BASE / IDENTITY / "visual_review.json"),
        "formal_runtime_gates_passed": False, "publication_authorized": False})
    print("Human quarter-size approval recorded separately; old receipts unchanged")
