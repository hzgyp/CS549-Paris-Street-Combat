"""Authenticate ML007 raw failure and derive remote prefix without editing it."""
import json
import sys
from pathlib import Path
from vehicle_prefix import read, digest, digest_bytes, near_case, verify

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / "Tools/Integration/NPCInteractionV1"))
from common import guard_rows, guards_match
evidence = root / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1"
directory = evidence / "fixed_surface_v12_20261007"
report = read(directory / "survey.json")
guards = guard_rows()
assert len(guards) == 703 and guards_match(guards) and guards == read(directory / "guards_before.json")
inventory = read(evidence / "inventory_v4_20261007/inventory.json")
car = next(b for b in inventory["blockers"] if b["class"].endswith("BP_Car_02a_C"))
bounds = [car["origin_cm"][i]-car["extent_cm"][i]-300 for i in range(2)] + [car["origin_cm"][i]+car["extent_cm"][i]+300 for i in range(2)]
first = next(i for i, c in enumerate(report["cases"]) if near_case(c, bounds))
receipt = {"identity": directory.name, "status": "remote_prefix_only_not_clean_batch",
    "input_sha256": {p.name: digest(p) for p in directory.iterdir() if p.is_file() and p.suffix in (".json", ".py")},
    "inventory_sha256": digest(evidence / "inventory_v4_20261007/inventory.json"),
    "exclusion_margin_cm": 300, "exclusion_xy_cm": bounds, "height_ignored_conservatively": True,
    "retained_count": first, "retained_cases_sha256": digest_bytes(report["cases"][:first]),
    "quarantined_cases": [c["id"] for c in report["cases"][first:]],
    "ungraded_initializations": [i["case"] for i in report["initializations"] if i["case"] not in {c["id"] for c in report["cases"]+report["control_cases"]}],
    "native_positive_criteria_unchanged": True, "protected_rows": 703}
log = root / "tmp/pure-map-survey-v1/fixed_surface_v12_20261007.log"
receipt["log_sha256"] = digest(log)
verify(evidence, receipt)
output = root / "Docs/Development/MissionLoopV1/VEHICLE_REMOTE_PREFIX_RECEIPT_20261007.json"
assert not output.exists()
output.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
files = [p for p in directory.iterdir() if p.is_file()] + [log]
manifest = {"case": "ML007", "shared_evidence_retained_in_place": True,
    "files": [{"path": str(p.relative_to(root)).replace("\\", "/"), "bytes": p.stat().st_size, "sha256": digest(p)} for p in files]}
target = root / "Failures/ML007-20261007-pure-map-vehicle-motion/MANIFEST.json"
assert not target.exists()
target.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
print(json.dumps({k: receipt[k] for k in ("retained_count", "quarantined_cases", "ungraded_initializations", "exclusion_xy_cm")}))
