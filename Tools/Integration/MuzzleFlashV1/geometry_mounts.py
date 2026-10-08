"""Derive private muzzle profiles from saved native terminal barrel rings."""
import json
import math

from common import BASE, sha, write


def terminal_ring(mesh):
    points = [row[1:] for row in mesh["vertices"]]
    assert mesh["valid"] and len(points) > 100 and not mesh["sockets"]
    spans = [max(p[i] for p in points) - min(p[i] for p in points) for i in range(3)]
    assert spans[1] > 5 * max(spans[0], spans[2]), "Unknown rifle long axis"
    end = max(p[1] for p in points)
    ring = sorted({tuple(p) for p in points if abs(p[1] - end) < .0001})
    assert len(ring) >= 16, "Terminal plane is not a measured barrel ring"
    centre = [(min(p[i] for p in ring) + max(p[i] for p in ring)) / 2 for i in range(3)]
    radii = sorted(math.hypot(p[0] - centre[0], p[2] - centre[2]) for p in ring)
    gaps = [(radii[i + 1] - radii[i], i) for i in range(len(radii) - 1)]
    gap, split = max(gaps)
    inner, outer = radii[:split + 1], radii[split + 1:]
    assert gap > .1 and len(inner) >= 8 and len(outer) >= 8, "No distinct bore and outer rim"
    assert max(inner) - min(inner) < .01 and max(outer) - min(outer) < .01, "Non-circular terminal ring"
    return {"mesh": mesh["path"], "selector": mesh["selected_by"], "location_cm": centre,
            "rotation_pitch_yaw_roll_deg": [0, 90, 0], "scale": [1, 1, 1],
            "outward_axis_local": [0, 1, 0], "terminal_unique_vertices": len(ring),
            "inner_radius_range_cm": [min(inner), max(inner)],
            "outer_radius_range_cm": [min(outer), max(outer)],
            "legacy_reference_delta_cm": [centre[0], centre[1] - 83.23, centre[2]],
            "axis_inference": "terminal constant-Y bore/rim plane at positive end of dominant Y shaft; visual check required"}


def measured_profiles():
    source = BASE / "rifle_geometry_v1_20261008/result.json"
    result = json.loads(source.read_text())
    log = json.loads((source.parent / "log_validation.json").read_text(encoding="utf-8-sig"))
    assert result["status"] == "pass_saved_rifle_geometry_read_only" and not result["errors"]
    assert log["exit_code"] == 0 and log["strict_errors"] == 0 and not log["timed_out"]
    assert result["guard_count"] == 703 and result["original_intake_count"] == 68
    assert not any(result[k] for k in ("map_saved", "mesh_saved", "pie_started"))
    rows = [terminal_ring(mesh) for mesh in result["rifles"]]
    assert len(rows) == 2 and len({r["mesh"] for r in rows}) == 2
    return {"geometry_result_sha256": sha(source), "profiles": rows,
            "status": "measured_private_profiles_pending_actual_mount_render",
            "scale_calibrated": False, "ballistic_logic_changed": False}


if __name__ == "__main__":
    output = BASE / "rifle_geometry_v1_20261008/measured_profiles.json"
    assert not output.exists(), "Preserve occupied measurement"
    result = measured_profiles()
    write(output, result)
    print(json.dumps(result, indent=2))
