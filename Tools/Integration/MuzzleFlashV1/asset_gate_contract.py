"""Final validity is mandatory, but outstanding compilation is not final state."""


def classify_systems(current):
    assert current and all(x.get("loaded") and x.get("emitters") for x in current), current
    # A finished invalid system fails even while another system is compiling.
    assert all(x.get("compiling", False) or x.get("valid") for x in current), current
    if any(x.get("compiling", False) for x in current):
        return "compiling"
    if not all(x.get("ready") for x in current):
        return "waiting_readiness"
    return "ready"
