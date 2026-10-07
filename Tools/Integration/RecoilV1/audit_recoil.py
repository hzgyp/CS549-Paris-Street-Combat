"""Finite evidence audit; compilation and transforms are not visual sign-off."""
import json
from pathlib import Path
from common import BASE, ROOT, sha, guards, write


def validate_receipt(result, log):
    assert result["status"].startswith("pass_") and not result["errors"]
    assert result["protected_count"] == 703
    assert log["strict_errors"] == 0 and log["exit_code"] == 0 and not log["timed_out"]


def validate_motion(result):
    expected = {"PC_City_Player", "PC_City_Ally1", "PC_City_Enemy1"}
    assert set(result["summary"]["subjects"]) == expected
    assert result["summary"]["each_committed_one_shot"] and result["summary"]["each_cooldown_rejected"]
    assert result["summary"]["cadence_max"] <= .25
    for name in expected:
        rows = [r for r in result["samples"] if r["label"] == name and r["stage"] == "shot"]
        assert sum(r["recoil_active"] for r in rows) >= 8
        assert rows[-1]["recoil_starts"] == 1 and not rows[-1]["recoil_active"]
        assert all(r["sequence"] == 1 and r["action"] == "Ready" and r["ammo"] == [1, 16] for r in rows)
        assert result["candidate_excursion_cm"][name] > .5 and result["gun_hand_delta_cm"][name] <= .01


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--identity", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--motion", required=True)
    p.add_argument("--contract", required=True)
    p.add_argument("--visual", required=True)
    args = p.parse_args()
    output = BASE / args.identity
    assert not output.exists()
    receipts = {}
    for kind in ("source", "motion", "contract", "visual"):
        folder = BASE / getattr(args, kind)
        result_path = folder / "result.json"
        r = json.loads(result_path.read_text(encoding="utf-8-sig"))
        log = json.loads((folder / "log_validation.json").read_text(encoding="utf-8-sig"))
        validate_receipt(r, log)
        receipts[kind] = {"path": result_path.relative_to(ROOT).as_posix(), "sha256": sha(result_path)}
        if kind == "motion":
            validate_motion(r)
        if kind == "contract":
            assert len(r["native_contract"]) == 3 and all(all(c.values()) for c in r["native_contract"].values())
        if kind == "visual":
            assert len(r["captures"]) == 9
            for capture in r["captures"]:
                image = folder / capture["file"]
                assert image.is_file() and image.stat().st_size > 10000
    rows = guards()
    output.mkdir(parents=True)
    write(output / "result.json", {"status": "pass_finite_candidate_receipts_visual_review_separate",
        "receipts": receipts, "guard_count": len(rows), "installed": False,
        "visual_human_acceptance": False, "scope": "finite original firing presentation, not full NPC/mission/FPS/Shipping acceptance"})
    print("Four candidate receipts audited,703 exact; images still need actual inspection")
