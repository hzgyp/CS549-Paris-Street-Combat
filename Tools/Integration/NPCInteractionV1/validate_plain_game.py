"""Read-only ordinary game log/guard checks; no behavior script in that process."""
import argparse
import json
import re
from pathlib import Path
from common import STORE, guard_rows, guards_match

p = argparse.ArgumentParser()
p.add_argument("--identity", required=True)
p.add_argument("--log", required=True)
p.add_argument("--exit-code", required=True, type=int)
args = p.parse_args()
out = STORE / "Evidence/NPCInteractionV1" / args.identity
log = Path(args.log).read_text(errors="replace")
rows = guard_rows()
names = re.findall(r"PARIS_NPC_COMBAT_READY (\S+)", log)
allied = re.findall(r"PARIS_ALLIED_GRIP_READY (\S+)", log)
german = re.findall(r"PARIS_GERMAN_GRIP_READY (\S+)", log)
errors = [line for line in log.splitlines() if re.search(r"Error:|Fatal error:|Assertion failed:|Ensure condition failed:|BOOTSTRAP_FAILED|Accessed None", line)]
checks = {"normal_exit": args.exit_code == 0, "five_unique_native_combat_ready": len(names) == len(set(names)) == 5,
          "two_allied_three_german_native_bindings": len(allied) == 2 and len(german) == 3,
          "python_interpreter_explicitly_disabled": "Python disabled via command-line flag '-DisablePython'" in log
              and not re.search(r"LogPython:.*(?:Python enabled|Using Python|Running start-up script)", log),
          "editor_bridge_not_mounted_or_loaded": not re.search(r"Mounting.*ParisEditorBridge|InternalLoadLibrary: 'ParisEditorBridge'", log),
          "no_runtime_errors": not errors, "all_current_guards_exact": guards_match(rows)}
report = {"identity": args.identity, "status": "pass_ordinary_saved_game_native_bootstrap" if all(checks.values()) else "failed_ordinary_game_preserve",
          "checks": checks, "ready_names": names, "binding_names": {"Allied": allied, "German": german},
          "errors": errors, "protected_count": len(rows), "protected_guards_unchanged": checks["all_current_guards_exact"],
          "scope": "saved map -game Python interpreter explicitly disabled, bridge absent; module mounting is distinct; no physical-input/full-motion/FPS/Shipping acceptance"}
assert not (out / "validator_source.py").exists(), "Preserve prior validator receipt"
(out / "validator_source.py").write_bytes(Path(__file__).read_bytes())
(out / "plain_game.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
raise SystemExit(0 if all(checks.values()) else 2)
