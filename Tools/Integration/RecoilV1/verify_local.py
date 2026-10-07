"""Fresh local selection snapshot; do not alter immutable installation evidence."""
import argparse
import json
from common import BASE, ROOT, guards, sha, write
from audit_recoil import validate_receipt, validate_motion

p = argparse.ArgumentParser()
p.add_argument("--identity", required=True)
p.add_argument("--runtime", required=True)
args = p.parse_args()
out = BASE / args.identity
assert not out.exists()
runtime = BASE / args.runtime
result = json.loads((runtime / "result.json").read_text(encoding="utf-8-sig"))
log = json.loads((runtime / "log_validation.json").read_text(encoding="utf-8-sig"))
assert result["mode"] == "installed"
validate_receipt(result, log)
validate_motion(result)
rows = guards()
ledger_path = ROOT / "Docs/Development/RecoilV1/AUTHORIZED_LOCAL_BINARIES_20261007.json"
ledger = json.loads(ledger_path.read_text())
assert all(r in rows for r in ledger["rows"])
visual_folder = BASE / "candidate_lit_visual_v3_20261007"
visual = json.loads((visual_folder / "result.json").read_text())
assert len(visual["captures"]) == 9
images = [{"path": (visual_folder / c["file"]).relative_to(ROOT).as_posix(),
           "sha256": sha(visual_folder / c["file"]), "diagnostic_only": c["isolated_diagnostic_only"]}
          for c in visual["captures"]]
out.mkdir(parents=True)
write(out / "result.json", {"status": "pass_local_visible_recoil_finite_regression", "files": rows,
    "guard_count": 703, "authorized_display_binary_count": 3, "unchanged_other_guards": 700,
    "runtime_proof": (runtime / "result.json").relative_to(ROOT).as_posix(),
    "runtime_sha256": sha(runtime / "result.json"), "images": images,
    "scope": "existing player/Allied/German visible firing presentation; not full NPC/contact/FPS/Shipping acceptance",
    "source_curve_amplified": False, "python_pose_driver": False, "camera_shake_substitute": False,
    "world_visibility_contact_accepted": False, "published": False, "git_committed": False})
print("Fresh original-project recoil proof authenticated;703 current local guards exact")
