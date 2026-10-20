def policy_evidence(value):
    """Strip observer-only sight diagnostics; preserve every policy input/result."""
    if isinstance(value, dict):
        return {key: policy_evidence(item) for key, item in value.items() if key != 'player_sight'}
    if isinstance(value, list):
        return [policy_evidence(item) for item in value]
    return value
