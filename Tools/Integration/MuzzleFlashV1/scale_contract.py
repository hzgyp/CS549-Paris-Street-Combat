"""One user-requested instance-size comparison; no asset or timing adaptation."""
import copy

IDENTITY = "mount_scale_v3_20261008"
INSTANCE_SCALE = .25


def scaled_profiles(measured):
    assert measured["status"] == "measured_private_profiles_pending_actual_mount_render"
    assert not measured["ballistic_logic_changed"] and len(measured["profiles"]) == 2
    result = copy.deepcopy(measured)
    for row in result["profiles"]:
        assert row["scale"] == [1, 1, 1], "Only the inspected unit-scale baseline"
        assert row["rotation_pitch_yaw_roll_deg"] == [0, 90, 0]
        row["scale"] = [INSTANCE_SCALE] * 3
    result["instance_scale_relative_to_unit_mount"] = INSTANCE_SCALE
    result["human_scale_accepted"] = False
    result["status"] = "user_requested_quarter_scale_comparison_human_pending"
    return result
