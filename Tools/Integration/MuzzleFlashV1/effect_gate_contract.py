"""Never replay the stopped rifle01 pulse while completing untested variants."""


def select_effect_candidates(packages, mode, prior=None):
    assert len(packages) == 4
    assert [p.rsplit("_", 1)[-1] for p in packages] == ["01", "02", "03", "04"]
    if mode != "RemainingPulse":
        return list(packages)
    assert prior and prior["identity"] == "effect_pulse_v1_20261007"
    assert prior["status"] == "failed_effect_gate_preserve" and prior["errors"]
    assert prior["controlled_pulse"] and prior["requested_emission_seconds"] == .10
    assert {s["index"] for s in prior["samples"]} == {0}, "Preserve tested candidates"
    assert len(prior["natural_completions"]) == 1
    assert prior["natural_completions"][0]["complete"]
    return list(packages[1:])
