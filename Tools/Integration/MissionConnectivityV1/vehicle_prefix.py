"""Read-only conservative admission of a failed batch's remote prefix."""
import hashlib
import json
import re
from pathlib import Path


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def intersects(a, b, bounds):
    # Slab intersection of a closed XY segment and closed rectangle.
    low, high = 0., 1.
    for axis in range(2):
        delta = b[axis]-a[axis]
        lo, hi = bounds[axis], bounds[axis+2]
        if abs(delta) < 1e-12:
            if not lo <= a[axis] <= hi: return False
        else:
            first, last = sorted(((lo-a[axis])/delta, (hi-a[axis])/delta))
            low, high = max(low, first), min(high, last)
            if low > high: return False
    return True


def near_case(case, bounds):
    points = [case["source_cm"], case["goal_cm"]]
    for key in ("standing",):
        if case.get(key): points.append(case[key]["body_cm"])
    if case.get("final_body_cm"): points.append(case["final_body_cm"])
    if any(intersects(p, p, bounds) for p in points): return True
    for line in (case.get("path_cm", []), [s["body_cm"] for s in case.get("samples", [])]):
        if any(intersects(p, p, bounds) for p in line): return True
        if any(intersects(a, b, bounds) for a, b in zip(line, line[1:])): return True
    actual = ([case["standing"]["body_cm"]] if case.get("standing") else []) + [s["body_cm"] for s in case.get("samples", [])]
    if case.get("final_body_cm"): actual.append(case["final_body_cm"])
    return any(intersects(a, b, bounds) for a, b in zip(actual, actual[1:]))


def verify(evidence, receipt):
    receipt = read(receipt) if isinstance(receipt, (str, Path)) else receipt
    assert receipt["identity"] == "fixed_surface_v12_20261007"
    directory = evidence / receipt["identity"]
    for name, sha in receipt["input_sha256"].items(): assert digest(directory / name) == sha
    r = read(directory / "survey.json")
    e = read(directory / "exit.json")
    assert e["owned_pid"] == 36488 and e["exit_code"] == e["strict_log_errors"] == 0
    assert r["protected_bytes_unchanged"] and len(r["errors"]) == 1
    assert r["errors"][0].endswith("AssertionError: Environment vehicle no longer stationary\n")
    assert r["status"] == "failed_api_or_isolation_gate" and r["summary"]["completed_cases"] == 11645
    inventory = read(evidence / "inventory_v4_20261007/inventory.json")
    car = next(b for b in inventory["blockers"] if b["class"].endswith("BP_Car_02a_C"))
    bounds = [car["origin_cm"][i]-car["extent_cm"][i]-300 for i in range(2)] + [car["origin_cm"][i]+car["extent_cm"][i]+300 for i in range(2)]
    assert bounds == receipt["exclusion_xy_cm"]
    first = next((i for i, c in enumerate(r["cases"]) if near_case(c, bounds)), len(r["cases"]))
    assert first == receipt["retained_count"] and first < len(r["cases"])
    prefix = r["cases"][:first]
    assert digest_bytes(prefix) == receipt["retained_cases_sha256"]
    assert [c["id"] for c in r["cases"][first:]] == receipt["quarantined_cases"]
    for c in prefix:
        if c["status"] == "passed":
            assert "SUCCESS" in c["completion"]["result"].upper()
            assert c["completion"]["request_id_value"] == c["request_id_value"] > 0
            assert c["completion"]["controller"] == c["controller"]
            assert c["xy_cm"] <= 35 and c["foot_error_cm"] <= 35
            assert c["standing"]["xy_cm"] <= 35 and c["standing"]["foot_error_cm"] <= 35 and not c["standing"]["blockers"]
            assert c["standing"]["native_floor"]["walkable_floor"] and c["final_native_floor"]["walkable_floor"]
        assert not near_case(c, bounds)
    return r, first


def digest_bytes(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=True).encode()).hexdigest()
