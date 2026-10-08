"""Exactly one user-authorized instance adaptation; no search or default retry."""
RATE_NAME = "User.MuzzleFlash_SpawnRate"
RATE = 20.0
WINDOW = .10
CAP = 8.0
MAX_CAPTURES = 12


def select_rate_candidate(packages, previous_reviews):
    assert len(packages) == 4
    assert [p.rsplit("_", 1)[-1] for p in packages] == ["01", "02", "03", "04"]
    assert len(previous_reviews) == 2
    for identity, review in zip(("effect_pulse_v1_20261007", "remaining_pulse_v1_20261007"), previous_reviews):
        assert review["identity"] == identity
        assert review["status"] == "failed_visible_pulse_preserve"
        assert review["candidate_admitted"] is False
        assert all(i["original_inspected"] and not i["visible_flame"] for i in review["images"])
    assert len(previous_reviews[0]["images"]) == 3
    assert len(previous_reviews[1]["images"]) == 9
    return packages[0]
