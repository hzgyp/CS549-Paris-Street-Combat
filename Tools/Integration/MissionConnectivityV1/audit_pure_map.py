"""Independent receipt/denominator audit; no terrain or engine mutation."""
import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("identity")
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]
evidence_root = root / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1"
directory = evidence_root / args.identity
sys.path.insert(0, str(root / "Tools/Integration/NPCInteractionV1"))
from common import guard_rows, guards_match, digest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pure_map_graph import components
from vehicle_prefix import verify as verify_vehicle_prefix
remote_checked = {}


def remote_prefix_stop(identity, r):
    if identity != "fixed_surface_v12_20261007": return False
    if identity not in remote_checked:
        verified, count = verify_vehicle_prefix(evidence_root,
            root / "Docs/Development/MissionLoopV1/VEHICLE_REMOTE_PREFIX_RECEIPT_20261007.json")
        assert verified == r
        admission = read(root / "Docs/Development/MissionLoopV1/VEHICLE_REMOTE_PREFIX_RECEIPT_20261007.json")
        assert admission["log_sha256"] == digest(root / "tmp/pure-map-survey-v1" / (identity + ".log"))
        remote_checked[identity] = count
    return True

pattern = r"Error:|Fatal:|Ensure condition failed|=== Handled ensure|RegistrationFailed_AgentNotValid|NavData.*will be removed|Navigation NOT building|navigation build is locked"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def clean_cache_interruption(identity, r):
    p = evidence_root / identity / "STOP_REQUEST.json"
    if identity == "fixed_static_vehicle_v18_20261007" and p.exists():
        stop_text = p.read_text(encoding="utf-8-sig")
        stop = json.loads(stop_text)
        return (stop.get("kind") == "preserve_remote_negative_after_quarantined_prefix" and
            stop.get("cases") == ["case_11637"] and r["errors"] == ["Owned stop request: " + stop_text] and
            r["environment_fixture_version"] == "static_vehicle_v1" and r["static_vehicle_admission"][0]["max_drift_cm"] == 0 and
            r["resume_control_gate"] == "pass_two_native_legs" and r["status"] == "failed_api_or_isolation_gate")
    if identity != "fixed_surface_v10_20261007" or not p.exists(): return False
    stop_text = p.read_text(encoding="utf-8-sig")
    stop = json.loads(stop_text)
    return (stop.get("kind") == "preserve_unchanged_prior_source_rejections" and
        stop.get("sources") == ["region_03541", "region_03573"] and
        r["errors"] == ["Owned stop request: " + stop_text] and
        r["summary"]["failed_cases"] == 0 and r["status"] == "failed_api_or_isolation_gate")


def accepted_move(c):
    assert c["kind"] == "movement" and "SUCCESS" in c["completion"]["result"].upper()
    assert c["completion"]["case"] == c["id"] and c["xy_cm"] <= 35 and c["foot_error_cm"] <= 35
    assert c["standing"]["xy_cm"] <= 35 and c["standing"]["foot_error_cm"] <= 35 and not c["standing"]["blockers"]
    assert "WALKING" in c["standing"]["mode"].upper()
    assert c["final_native_floor"]["walkable_floor"] and c["standing"]["native_floor"]["walkable_floor"]
    assert c["request_id_value"] == c["completion"]["request_id_value"] > 0
    assert c["controller"] == c["completion"]["controller"]


def verify_batch(identity, r, g):
    d = evidence_root / identity
    e = read(d / "exit.json")
    entry = read(d / "entry.json")
    assert e["owned_pid"] == entry["owned_pid"] and entry["identity"] == r["identity"] == identity
    assert e["exit_code"] == 0 and (not r["errors"] or clean_cache_interruption(identity, r) or remote_prefix_stop(identity, r)) and r["protected_bytes_unchanged"]
    log = root / "tmp/pure-map-survey-v1" / (identity + ".log")
    assert len(re.findall(pattern, log.read_text(encoding="utf-8", errors="replace"))) == e["strict_log_errors"] == 0
    assert r["graph_sha256"] == digest(d / "graph.json") and r["navmesh_sha256"] == digest(d / "navmesh.json")
    before = read(d / "guards_before.json")
    assert digest(d / "guards_before.json") == r["guards_before_sha256"]
    assert before == guards and guards_match(before), "Entry guard epoch changed"
    assert r["helper_sha256"] == digest(root / "Unreal/ParisStreetCombat/Plugins/ParisMapSurveyV1/Binaries/Win64/UnrealEditor-ParisMapSurveyV1.dll")
    assert not r["map_saved"] and r["positions_are_temporary_tests"] and r["original_assets_preserved"]
    assert r["runtime_isolation"] == {"original_characters": 0, "project_policies": 0, "environment_vehicles": 1,
        "project_gameplay_native_and_blueprint_actors": 0, "inheritance_scan": True}
    assert not r["last_native_isolation_state"]["production_contaminants"]
    assert [c["id"] for c in r["cases"]] == [c["id"] for c in g["cases"][:len(r["cases"])]], "Scheduled prefix omitted/reordered"
    assert r["summary"]["completed_cases"] == r["completed_cases"] == len(r["cases"])
    assert r["summary"]["planned_cases"] == len(g["cases"])
    assert r["summary"]["passed_cases"] == sum(c["status"] == "passed" for c in r["cases"])
    assert r["summary"]["standing_passes"] == sum(c["status"] == "standing_passed" for c in r["cases"])
    assert r["summary"]["failed_cases"] == sum(c["status"] not in ("passed", "standing_passed") for c in r["cases"])
    controls = r["control_cases"]
    own_cases = [c for c in r["cases"] if c.get("origin_run") == identity] + controls + r["surface_controls"] + r.get("vehicle_controls", [])
    initializations = {c["case"]: c for c in r["initializations"]}
    assert len(initializations) == len(r["initializations"]), "Repeated initialization hidden inside one case"
    expected_initialized = {c["id"] for c in own_cases if c.get("reason") not in
        ("source_previously_rejected_no_retry", "previously_rejected_exact_surface_query_no_retry", "previously_rejected_remote_case_no_retry")}
    extras = set(initializations)-expected_initialized
    assert expected_initialized <= set(initializations), "Missing owned initialization"
    if extras:
        assert (clean_cache_interruption(identity, r) or remote_prefix_stop(identity, r)) and extras == {g["cases"][len(r["cases"])]["id"]}, "Unexpected ungraded initialization"
    for c in own_cases:
        if c["status"] == "passed":
            assert c["completion"] in r["completions"], "Copied completion absent from owning run"
        if c["id"] in initializations:
            assert initializations[c["id"]]["not_a_traversal"]
            assert initializations[c["id"]]["source_region"] == c["from"]
    if r.get("previous_identity"):
        assert r["resume_control_gate"] == "pass_two_native_legs" and len(controls) == 2
        for c, spec in zip(controls, g["cases"][:2]):
            assert c["id"] == "resume_control_" + spec["id"] and c["control_reproduction"] and c["status"] == "passed"
            assert c["source_cm"] == spec["source_cm"] and c["goal_cm"] == spec["goal_cm"]
            accepted_move(c)
    else:
        assert not controls and r["normal_time_early_gate"] == "pass_two_native_legs"
    if r.get("environment_fixture_version") == "static_vehicle_v1":
        revision = read(root / "Docs/Development/MissionLoopV1" / ("STATIC_VEHICLE_SOURCE_RECEIPT_V3_20261007.json" if identity in ("early_static_vehicle_v17_20261007", "fixed_static_vehicle_v18_20261007") else "STATIC_VEHICLE_SOURCE_RECEIPT_V5_20261007.json"))
        assert digest(d / "ue_pure_map_survey.py") == revision["source_sha256"]
        assert len(r["static_vehicle_admission"]) == 1
        vehicle = r["static_vehicle_admission"][0]
        assert vehicle["before"] == vehicle["after"] and vehicle["collision_geometry_exact"] and vehicle["simulation_disabled"]
        assert vehicle["max_drift_cm"] == 0
        for c in r.get("vehicle_controls", []): accepted_move(c)
    return {"identity": identity, "cases": len(r["cases"]), "controls": len(controls), "status": r["status"],
        "admitted_cases": remote_checked.get(identity, len(r["cases"])),
        "ungraded_interrupted_initializations": sorted(extras),
        "owned_pid": e["owned_pid"], "exit_code": 0, "log_errors": 0, "receipt_sha256": digest(d / "survey.json"),
        "source_sha256": digest(d / "ue_pure_map_survey.py"), "graph_builder_sha256": digest(d / "pure_map_graph.py")}

report = json.loads((directory / "survey.json").read_text())
graph = json.loads((directory / "graph.json").read_text())
native = json.loads((directory / "navmesh.json").read_text())
exit_receipt = json.loads((directory / "exit.json").read_text(encoding="utf-8-sig"))
cases = report["cases"]
assert len({c["id"] for c in cases}) == len(cases), "Duplicate physical case receipt"
schedule = {c["id"]: c for c in graph["cases"]}
assert all(c["id"] in schedule and c["source_cm"] == schedule[c["id"]]["source_cm"] and
           c["goal_cm"] == schedule[c["id"]]["goal_cm"] for c in cases)
assert len(graph["polygon_to_region"]) == len(native["polygons"]) == graph["polygon_count"]
assert native["active_tiles"] == native["exported_tiles"] and native["invalid_records"] == 0
assert native["sampling_version"] == graph["sampling_version"] == report["surface_sampling_version"] == "native_specific_polygon_surface_v2"
poly_index = {p["id"]: p for p in native["polygons"]}
assert all(p["surface_xy_drift_cm"] <= .01 for p in native["polygons"])
assert all(r["point_cm"] == poly_index[r["representative_poly"]]["surface_cm"] and
           r["raw_center_cm"] == poly_index[r["representative_poly"]]["center_cm"] for r in graph["regions"])
assert report["graph_sha256"] == digest(directory / "graph.json")
assert report["navmesh_sha256"] == digest(directory / "navmesh.json")
passed = [c for c in cases if c["status"] == "passed"]
for c in passed:
    accepted_move(c)
for c in cases:
    assert c["status"] in ("passed", "standing_passed", "failed")
    assert not any(s["native_floor"].get("error") for s in c.get("samples", []))
    if c["status"] == "standing_passed":
        assert c["kind"] == "standing_only" and c["not_a_connectivity_edge"]
        assert not c["standing"]["blockers"] and c["standing"]["native_floor"]["walkable_floor"]
        assert c["standing"]["xy_cm"] <= 35 and c["standing"]["foot_error_cm"] <= 35
    if c.get("prior_failure_identity"):
        prior_path = evidence_root / c["prior_failure_identity"] / "survey.json"
        prior = read(prior_path)
        assert digest(prior_path) == c["prior_failure_receipt_sha256"] and c["not_new_physical_attempt"]
        prior_case = next(x for x in prior["cases"] if x["id"] == c["prior_failure_case"])
        if c["reason"] == "previously_rejected_remote_case_no_retry":
            from vehicle_prefix import near_case
            admission = read(root / "Docs/Development/MissionLoopV1/VEHICLE_REMOTE_PREFIX_RECEIPT_20261007.json")
            assert c["prior_failure_identity"] == "fixed_surface_v12_20261007" and not near_case(prior_case, admission["exclusion_xy_cm"])
            assert prior_case["status"] == "failed" and prior_case["reason"] == c["prior_failure_reason"]
            assert prior_case["source_cm"] == c["source_cm"] and prior_case["goal_cm"] == c["goal_cm"]
        elif c["reason"] == "previously_rejected_exact_surface_query_no_retry":
            assert prior_case["reason"] == "runtime_query_missing_or_partial"
            assert (prior_case["from"], prior_case["to"], prior_case["source_cm"], prior_case["goal_cm"]) == (c["from"], c["to"], c["source_cm"], c["goal_cm"])
        else:
            assert c["reason"] == "source_previously_rejected_no_retry" and prior_case["reason"] == "source_not_safe_standing_surface"
            assert math.dist(prior_case["source_cm"], c["source_cm"]) == c["prior_source_delta_cm"] <= c["prior_source_equivalence_cm"] == .001
            assert prior_case["standing"] == c["standing"]
frames = [s["world_frame_seconds"] for c in cases for s in c.get("samples", [])]
assert not frames or max(frames) <= .1
log = root / "tmp/pure-map-survey-v1" / (args.identity + ".log")
log_errors = len(re.findall(pattern, log.read_text(encoding="utf-8", errors="replace")))
assert log_errors == exit_receipt["strict_log_errors"] == 0
assert exit_receipt["exit_code"] == 0 and (not report["errors"] or clean_cache_interruption(args.identity, report)) and report["protected_bytes_unchanged"]
guards = guard_rows()
assert len(guards) == 703 and guards_match(guards)
chain = []
batch_report, batch_graph, batch_identity = report, graph, args.identity
seen = set()
while True:
    assert batch_identity not in seen, "Cyclic resume chain"
    seen.add(batch_identity)
    chain.append(verify_batch(batch_identity, batch_report, batch_graph))
    previous = batch_report.get("previous_identity")
    if not previous: break
    previous_dir = evidence_root / previous
    previous_report = read(previous_dir / "survey.json")
    previous_graph = read(previous_dir / "graph.json")
    assert previous_report["status"] == "partial_finite_clean_survey_batch" or clean_cache_interruption(previous, previous_report) or remote_prefix_stop(previous, previous_report)
    assert batch_report["previous_receipt_sha256"] == digest(previous_dir / "survey.json")
    prefix_count = remote_checked.get(previous, len(previous_report["cases"]))
    assert batch_report["cases"][:prefix_count] == previous_report["cases"][:prefix_count], "Historical case altered on resume"
    if previous in remote_checked:
        prefix_path = root / "Docs/Development/MissionLoopV1/VEHICLE_REMOTE_PREFIX_RECEIPT_20261007.json"
        assert batch_report["remote_prefix_retained_count"] == prefix_count and batch_report["remote_prefix_admission_sha256"] == digest(prefix_path)
    def graph_signature(g):
        return (g["summary"], [(r["id"], r["tile"], r["point_cm"], r["raw_center_cm"], r["area_cm2"], r["z_range_cm"]) for r in g["regions"]],
            {(e["from"], e["to"], e["narrow"], e["vertical"]) for e in g["directed_edges"]},
            [{k: c[k] for k in ("id", "from", "to", "source_cm", "goal_cm", "kind", "tree_edge", "narrow", "vertical")} for c in g["cases"]])
    assert graph_signature(batch_graph) == graph_signature(previous_graph), "Resume geometry/topology/schedule drift"
    for k in ("profile", "inventory_sha256", "helper_sha256", "normal_time_reference_sha256", "recoil_local_binary_authority_sha256"):
        if previous in remote_checked and k == "normal_time_reference_sha256":
            assert batch_report["historical_normal_time_reference_sha256"] == previous_report[k]
            continue
        assert batch_report[k] == previous_report[k], "Resume authority/profile drift: " + k
    batch_identity, batch_report, batch_graph = previous, previous_report, previous_graph
chain.reverse()
assert report.get("prior_batches", []) == [c["identity"] for c in chain[:-1]]
assert len({c["graph_builder_sha256"] for c in chain}) == 1
source_hashes = {c["source_sha256"] for c in chain}
if len(source_hashes) > 1:
    revision = read(root / "Docs/Development/MissionLoopV1/SOURCE_CACHE_CORRECTION_RECEIPT_V2_20261007.json")
    static_revision_path = root / "Docs/Development/MissionLoopV1" / ("STATIC_VEHICLE_SOURCE_RECEIPT_V3_20261007.json" if args.identity == "fixed_static_vehicle_v18_20261007" else "STATIC_VEHICLE_SOURCE_RECEIPT_V5_20261007.json")
    static_revision = read(static_revision_path) if report.get("environment_fixture_version") else None
    expected_sources = {revision["old_source_sha256"], revision["new_source_sha256"]}
    if static_revision: expected_sources.add(static_revision["source_sha256"])
    static_admission = read(root / "Docs/Development/MissionLoopV1/STATIC_VEHICLE_SOURCE_RECEIPT_V3_20261007.json") if static_revision else None
    if static_admission: expected_sources.add(static_admission["source_sha256"])
    assert source_hashes == expected_sources
    assert chain[0]["identity"] == revision["clean_interrupted_identity"] == "fixed_surface_v10_20261007"
    assert chain[0]["source_sha256"] == revision["old_source_sha256"]
    assert all(c["source_sha256"] == (revision["new_source_sha256"] if c["identity"] == "fixed_surface_v12_20261007" or not static_revision else static_admission["source_sha256"] if c["identity"] == "fixed_static_vehicle_v18_20261007" else static_revision["source_sha256"]) for c in chain[1:])
if report["execution_profile"] == "FixedSurvey":
    normal = evidence_root / ("early_static_vehicle_v17_20261007" if report.get("environment_fixture_version") else "early_surface_v9_20261007")
    assert report["normal_time_reference_sha256"] == digest(normal / "survey.json")
    normal_report = read(normal / "survey.json")
    assert normal_report["status"] == "bounded_normal_time_probe_lifecycle_pass" and len(normal_report["cases"]) == 2
    assert normal_report["surface_sampling_gate"] == "pass_known_exact_poly_standing"
    assert len(normal_report["surface_controls"]) == 1 and normal_report["surface_controls"][0]["status"] == "standing_passed"
    assert normal_report["surface_sampling_version"] == report["surface_sampling_version"] == native["sampling_version"]
    assert read(normal / "exit.json")["exit_code"] == read(normal / "exit.json")["strict_log_errors"] == 0
    for c in normal_report["cases"]: accepted_move(c)
    if report.get("environment_fixture_version"):
        assert normal_report["vehicle_control_gate"] == "pass_native_near_vehicle" and len(normal_report["vehicle_controls"]) == 1
        for c in normal_report["vehicle_controls"]: accepted_move(c)
    authority = root / "Docs/Development/RecoilV1/AUTHORIZED_LOCAL_BINARIES_20261007.json"
    assert report["recoil_local_binary_authority_sha256"] == digest(authority)
    authority_data = read(authority)
    assert digest(root / authority_data["proof"]) == authority_data["proof_sha256"]
else:
    assert report["surface_sampling_gate"] == "pass_known_exact_poly_standing"
    calibration = report["surface_controls"]
    assert len(calibration) == 1 and calibration[0]["status"] == "standing_passed"
    assert calibration[0]["not_a_connectivity_edge"] and calibration[0]["standing"]["native_floor"]["walkable_floor"]
    assert calibration[0]["standing"]["xy_cm"] <= 35 and calibration[0]["standing"]["foot_error_cm"] <= 35
    assert not calibration[0]["standing"]["blockers"] and not calibration[0]["samples"]
template = evidence_root / "template_defaults_v1_20261007"
manifest_files = list(template.glob("*manifest*.json"))
# The template manifest format is kept as authored; exact mounted-file receipts are independent.
template_files = list((template / "Content/Characters").rglob("*"))
template_files = [p for p in template_files if p.is_file()]
assert len(template_files) == 128 and sum(p.stat().st_size for p in template_files) == 131381051
source_template = Path("C:/Program Files/Epic Games/UE_5.8/Templates/TemplateResources/High/Characters/Content")
assert all(digest(p) == digest(source_template / p.relative_to(template / "Content/Characters")) for p in template_files)
surface_actors = Counter(s.get("native_floor", {}).get("actor_class", "unobserved")
                         for c in cases for s in c.get("samples", []))
measured_nodes = {n for c in passed for n in (c["from"], c["to"])}
adjacency = {n: set() for n in sorted(measured_nodes)}
for c in passed: adjacency[c["from"]].add(c["to"])
physical_groups = components(adjacency)
assert report["physical_components"] == physical_groups
assert report["coverage"]["regions_on_passed_edges"] == len(measured_nodes)
assert report["coverage"]["unmeasured_cases"] == len(schedule)-len(cases)
assert report["coverage"]["regions_without_passed_edge_evidence"] == len(graph["regions"])-len(measured_nodes)
mode_counts = Counter(s["mode"] for c in cases for s in c.get("samples", []))
feet = [s["foot_z_cm"] for c in passed for s in c.get("samples", [])]
feet += [c["final_body_cm"][2]-report["profile"]["half_height_cm"] for c in passed]
inventory = read(evidence_root / "inventory_v4_20261007/inventory.json")
assert report["inventory_sha256"] == digest(evidence_root / "inventory_v4_20261007/inventory.json")
blocker_index = {b["component"]: b for b in inventory["blockers"]}
support_counts = Counter()
support_details = {}
for c in cases:
    observations = [s["native_floor"] for s in c.get("samples", [])]
    if c.get("standing"): observations.append(c["standing"]["native_floor"])
    if c.get("final_native_floor"): observations.append(c["final_native_floor"])
    for f in observations:
        component = re.sub(r"UEDPIE_\d+_", "", f.get("component", ""))
        key = component or "no_support"
        support_counts[key] += 1
        if key not in support_details:
            b = blocker_index.get(component, {})
            support_details[key] = {"component": component, "actor_class": f.get("actor_class"),
                "label": b.get("label"), "mesh": b.get("mesh"), "matched_inventory": bool(b),
                "engine_test_geometry": str(b.get("mesh", "")).startswith("/Engine/BasicShapes/")}
categories = {}
for key in ("vertical", "narrow", "tree_edge"):
    selected = [c for c in cases if c.get(key)]
    categories[key] = {"scheduled": sum(bool(c.get(key)) for c in graph["cases"]), "completed": len(selected),
        "passed": sum(c["status"] == "passed" for c in selected), "failed": sum(c["status"] == "failed" for c in selected)}
region_index = {r["id"]: r for r in graph["regions"]}
physical_summary = []
for group in physical_groups[:12]:
    points = [region_index[n]["point_cm"] for n in group]
    physical_summary.append({"regions": len(group), "sample_min_cm": [min(p[i] for p in points) for i in range(3)],
        "sample_max_cm": [max(p[i] for p in points) for i in range(3)], "first_region": group[0]})
height_examples = []
for c in sorted(passed, key=lambda c: abs(c["final_body_cm"][2]-report["profile"]["half_height_cm"]-c["standing"]["foot_z_cm"]), reverse=True)[:12]:
    height_examples.append({"case": c["id"], "from": c["from"], "to": c["to"], "source_feet_cm": c["standing"]["foot_z_cm"],
        "final_feet_cm": c["final_body_cm"][2]-report["profile"]["half_height_cm"], "source_support": c["standing"]["native_floor"]["component"],
        "final_support": c["final_native_floor"]["component"], "native_success": True})
result = {"identity": args.identity, "status": "pass_receipt_audit", "not_full_map_acceptance": True,
    "protected_rows": len(guards), "protected_bytes_exact": True, "exit": exit_receipt,
    "native_summary": {k: native[k] for k in ("active_tiles", "exported_tiles", "capacity_slots", "vacant_slots", "invalid_records")},
    "graph_summary": graph["summary"], "completed_cases": len(cases), "passed_edges": len(passed),
    "standing_only_passes": sum(c["status"] == "standing_passed" for c in cases),
    "failure_reasons": dict(Counter(c.get("reason", c["status"]) for c in cases if c["status"] not in ("passed", "standing_passed"))),
    "unmeasured_cases": len(schedule)-len(cases), "regions_on_passed_edges": len(measured_nodes),
    "full_finite_case_coverage": len(schedule) == len(cases),
    "frame_range_seconds": [min(frames), max(frames)] if frames else None,
    "batch_chain": chain, "physical_component_sizes": [len(g) for g in physical_groups],
    "largest_physical_evidence_groups": physical_summary, "largest_accepted_height_changes": height_examples,
    "case_categories": categories, "sampled_movement_modes": dict(mode_counts),
    "sampling_version": native["sampling_version"], "surface_calibration_controls": report["surface_controls"],
    "surface_vs_center_z_range_cm": [min(p["surface_minus_center_z_cm"] for p in native["polygons"]), max(p["surface_minus_center_z_cm"] for p in native["polygons"])],
    "passed_movement_feet_z_range_cm": [min(feet), max(feet)] if feet else None,
    "support_components": [{**support_details[k], "observations": n} for k, n in support_counts.most_common()],
    "sampled_support_actor_classes": dict(surface_actors),
    "template": {"files": len(template_files), "bytes": sum(p.stat().st_size for p in template_files), "installed_source_exact": True},
    "input_hashes": {p.name: digest(p) for p in directory.iterdir() if p.is_file() and p.suffix in (".json", ".py")},
    "helper_sha256": digest(root / "Unreal/ParisStreetCombat/Plugins/ParisMapSurveyV1/Binaries/Win64/UnrealEditor-ParisMapSurveyV1.dll"),
    "completion_ids": "Native integer request ID and bound controller matched per accepted movement/control case"}
args.output.parent.mkdir(parents=True, exist_ok=True)
assert not args.output.exists(), "Unique audit receipt required"
args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in ("status", "completed_cases", "passed_edges", "standing_only_passes", "failure_reasons", "unmeasured_cases", "frame_range_seconds")}, indent=2))
