"""Authenticate finite native transactions and separately inspected originals."""
import argparse
import json

from common import BASE, sha, write


def transaction_receipt(identity, require_visual=True):
    directory = BASE / identity
    path = directory / "result.json"
    result = json.loads(path.read_text())
    log = json.loads((directory / "log_validation.json").read_text(encoding="utf-8-sig"))
    assert result["status"] == "pass_real_transactions_native_visual_pending" and not result["errors"]
    assert log == {"strict_errors": 0, "exit_code": 0, "timed_out": False}, log
    assert result["guard_count"] == 703 and result["original_intake_count"] == 68
    assert result["candidate_purchased_count_exact"] == 25
    assert result["entry_readiness_verified_before_city"]
    assert result["native_profile_readback_exact"] and not result["map_saved"]
    assert not result["pose_writer"] and not result["ammo_property_writes"]
    assert result["private_configure_calls"] == (1 if result["mode"] == "Transient" else 0)
    assert result["checks"] and all(result["checks"].values())
    assert result["checks"]["world_owned_effects_cleared"]
    assert result["checks"]["world_owned_components_invalid"]
    assert result["native_lifetime_before"] == {"subsystem_valid": True, "tracked_components": 2, "valid_components": 2}
    assert result["native_lifetime_after"] == {"subsystem_valid": False, "tracked_components": 2, "valid_components": 0}
    assert result["checks"]["continuous_original_two_commits_two_live_pulses"]
    assert result["checks"]["post_export_distinct_frame_before_commits"]
    assert result["checks"]["six_original_native_bindings_no_replay"]
    assert result["equipment_loss_mechanism"] == "unsaved_owned_display_hidden_restored_not_destroyed"
    if identity != "transactions_v4_20261008":  # Immutable historical native pass, visually rejected.
        batches = result["native_fire_batches"]
        assert len(batches) == 32 and sum(sum(r["sequence_deltas"]) for r in batches) == 20
        assert sum(len(r["sequence_deltas"]) for r in batches) == 35
        for row in batches:
            assert row["mechanism"] == "native_world_pre_actor_tick_original_PC_RequestFire"
            assert row["executed"] and not row["error"] and row["dispatch_frame"] > 0
            assert 0 <= row["dispatch_world_time"] - row["queued_world_time"] <= .5
            assert row["sequence_after"] - row["sequence_before"] == sum(row["sequence_deltas"])
        assert sum(r["sequence_deltas"] == [1, 0] for r in batches) == 3
    assert len(result["subjects_final"]) == 3
    labels = {row["label"] for row in result["subjects_final"]}
    assert len(labels) == 3
    for row in result["subjects_final"]:
        assert [row[n] for n in ("started", "completed", "cancelled", "live_count", "timed_out", "missed_sequences")] == [6, 2, 4, 0, 0, 0]
        for suffix in ("runtime_equipment_hidden", "runtime_equipment_restored", "equipment_same_binding_restored", "equipment_no_replay"):
            assert result["checks"][row["label"] + "_" + suffix]
    assert len(result["captures"]) == 39
    for label in labels:
        captures = [row for row in result["captures"] if row["label"] == label]
        assert len(captures) == 13
        assert sum(row["kind"] == "before" for row in captures) == 1
        assert sum(row["kind"] == "pulse" for row in captures) == 12
    for row in result["captures"]:
        file = directory / row["file"]
        assert file.stat().st_size == row["bytes"] and sha(file) == row["sha256"]
        assert row["original_unpaused"] and row["deferred_png_export"]
    if identity not in ("transactions_v4_20261008", "transactions_v6_20261008", "fresh_profile_v1_20261008"):
        assert result["capture_mechanism"] == "native_world_post_actor_deferred_twelve_unique_targets"
        for label in labels:
            native = [r["requested_sample"]["native_deferred_request"] for r in result["captures"]
                      if r["label"] == label and r["kind"] == "pulse"]
            assert len(native) == 12
            assert all(r["shot_sequence"] == r["started"] == r["live_count"] == 1 for r in native)
            assert all(a["frame"] < b["frame"] and a["world_time"] < b["world_time"] for a, b in zip(native, native[1:]))
            assert result["checks"][label+"_native_deferred_capture_armed"]
            assert result["checks"][label+"_native_deferred_twelve_and_unregistered"]
    refs = {"result": {"path": str(path), "sha256": sha(path)},
            "log": {"path": str(directory / "log_validation.json"), "sha256": sha(directory / "log_validation.json")}}
    if require_visual:
        file = directory / "visual_review.json"
        review = json.loads(file.read_text())
        assert review["native_result_sha256"] == sha(path)
        assert review["candidate_runtime_visual_admitted"]
        assert review["all_originals_inspected"] and len(review["images"]) == 39
        assert review["images"] == [{"file": r["file"], "sha256": r["sha256"]} for r in result["captures"]]
        assert set(review["readable_flame"]) == labels
        for label, names in review["readable_flame"].items():
            assert names and all(any(r["file"] == n and r["label"] == label and r["kind"] == "pulse" for r in result["captures"]) for n in names)
        refs["visual"] = {"path": str(file), "sha256": sha(file)}
    return result, refs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("identity")
    args = parser.parse_args()
    result, references = transaction_receipt(args.identity)
    out = BASE / args.identity / "audit.json"
    assert not out.exists(), "Preserve occupied audit"
    write(out, {"status": "pass_real_transactions_and_original_visual_review", "receipts": references,
        "mode": result["mode"], "guard_count": 703, "originals": 39,
        "scope": "finite local presentation, not ballistic/near-wall/FPS/Shipping/MVP acceptance"})
    print("Finite native transactions and inspected originals authenticate")
