"""Freeze and verify the bounded static-fixture source revision."""
import ast
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parents[3]
evidence = root / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1"
old = evidence / "fixed_surface_v12_20261007/ue_pure_map_survey.py"
new = Path(__file__).with_name("ue_pure_map_survey.py")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(p): return ast.parse(p.read_text(encoding="utf-8"))
before, after = parse(old), parse(new)
def function(tree, name): return ast.dump(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name), include_attributes=False)
protected = ("spawn_probe", "standing", "teardown_probe", "live_nav", "clean_cache_interruption", "checkpoint", "isolate", "finish")
assert all(function(before, n) == function(after, n) for n in protected)
def profile(tree):
    report = next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "report" for t in n.targets))
    return ast.literal_eval(next(v for k, v in zip(report.keys, report.values) if isinstance(k, ast.Constant) and k.value == "profile"))
assert profile(before) == profile(after)
receipt = {"status": "reviewed_static_fixture_revision", "old_source_sha256": sha(old), "source_sha256": sha(new),
    "unchanged_function_ast": {n: hashlib.sha256(function(after, n).encode()).hexdigest() for n in protected},
    "native_profile_exact": profile(after),
    "changes": ["vehicle ticks/simulation stopped with collision geometry parity", "near-car control separate from denominator",
        "authenticated conservative remote prefix only", "new normal-time static fixture reference"],
    "plan_sha256": sha(root / "Docs/Development/MissionLoopV1/PURE_MAP_STATIC_VEHICLE_PLAN_20261007.md"),
    "prefix_receipt_sha256": sha(root / "Docs/Development/MissionLoopV1/VEHICLE_REMOTE_PREFIX_RECEIPT_20261007.json")}
output = root / "Docs/Development/MissionLoopV1/STATIC_VEHICLE_SOURCE_RECEIPT_V5_20261007.json"
assert not output.exists()
output.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
print(receipt["source_sha256"])
