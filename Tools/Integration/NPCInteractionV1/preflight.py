"""Lane B offline guard and interface audit. No Unreal launch or native write."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from common import guard_rows

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--identity", required=True)
args = parser.parse_args()
assert re.fullmatch(r"[A-Za-z0-9_]+", args.identity)
out = STORE / "Evidence/NPCInteractionV1" / args.identity
assert not out.exists(), "Preserve occupied evidence identity"
out.mkdir(parents=True)

rows = guard_rows()
mismatches = []
for row in rows:
    path = ROOT / row["path"]
    if not path.is_file() or path.stat().st_size != row["size_bytes"] or sha(path) != row["sha256"]:
        mismatches.append(row["path"])

setup = (ROOT / "Tools/Integration/ue_paris_city_setup.py").read_text()
combat = (ROOT / "Tools/Integration/ue_paris_combat_author.py").read_text()
required = ["PC_RequestFire", "PC_RequestReload", "PC_ApplyDamage", "PC_ResetLifecycle"]
report = {
    "status": "pass_offline_contract_guard" if not mismatches else "blocked_native_guard_conflict",
    "protected_count": len(rows),
    "mismatches": mismatches,
    "actual_contract": {
        "base": "/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2",
        "player": "/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1",
        "allied": "/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisAlliedNPCV1",
        "german": "/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisGermanNPCV1",
        "team_ids": {"Allied": 0, "German": 1},
        "roles": ["Player", "Ally", "Enemy"],
        "entries": required,
        "source_checks": {
            "roster_and_team_defaults": all(token in setup for token in ("TeamId", "RoleId", "BP_PCParisAlliedNPCV1", "BP_PCParisGermanNPCV1")),
            "fire_origin_direction": all(token in combat for token in ("AimOrigin", "AimDirection", "PC_RequestFire")),
            "historical_source_friendly_off_blocks_without_damage": "Friendly blocked" in combat,
        },
    },
    "scope": "offline read-only; not Behavior Tree, movement, perception, combat or city acceptance",
    "shared_ff_authorization_ledger_present": (ROOT / "Docs/Development/NPCInteractionV1/AUTHORIZED_SHARED_MUTATIONS_20261005.json").exists(),
}
(out / "source.py").write_bytes(Path(__file__).read_bytes())
(out / "result.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
if mismatches:
    raise SystemExit(2)
