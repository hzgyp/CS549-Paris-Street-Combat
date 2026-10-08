"""Record explicit original-image inspection separately from native completion."""
import argparse
import json
import struct
from common import BASE, guards, intake_rows, sha, write

parser = argparse.ArgumentParser()
parser.add_argument("--identity", choices=("effect_pulse_v1_20261007", "remaining_pulse_v1_20261007"), required=True)
parser.add_argument("--all-originals-inspected", action="store_true", required=True)
parser.add_argument("--no-visible-flame", action="store_true", required=True)
args = parser.parse_args()
out = BASE / args.identity
destination = out / "visual_review.json"
assert not destination.exists(), "Preserve occupied review"
native = json.loads((out / "result.json").read_text())
rows = []
for capture in native["captures"]:
    file = out / capture["file"]
    with file.open("rb") as stream:
        header = stream.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    dimensions = struct.unpack(">II", header[16:24])
    assert dimensions == (1600, 900)
    rows.append({"file": file.name, "sha256": sha(file), "bytes": file.stat().st_size,
                 "dimensions": dimensions, "requested_age": capture["requested_sample"]["age"],
                 "original_inspected": True, "visible_flame": False})
assert len(rows) == (3 if args.identity == "effect_pulse_v1_20261007" else 9)
receipt = {"identity": args.identity, "native_result_sha256": sha(out / "result.json"),
           "review_basis": "assistant inspected every unedited original with view_image original",
           "status": "failed_visible_pulse_preserve", "candidate_admitted": False,
           "images": rows, "guard_count": len(guards()), "original_intake_count": len(intake_rows()),
           "runtime_enabled": False, "commercial_parameters_modified": False}
write(destination, receipt)
print(json.dumps({"identity": args.identity, "status": receipt["status"], "images": len(rows),
                  "guard_count": receipt["guard_count"], "original_intake_count": receipt["original_intake_count"]}))
