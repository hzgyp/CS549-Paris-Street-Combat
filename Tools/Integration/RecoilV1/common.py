"""Current immutable protection for the new presentation-only recoil work."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(os.environ["CS549_RECOIL_ROOT"]) if "CS549_RECOIL_ROOT" in os.environ else Path(__file__).resolve().parents[3]
STORE = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1"
BASE = STORE / "Evidence/RecoilV1"
CLIP = "/Game/RifleAnimsetPro/Animations/InPlace/Rifle_ShootOnce"
MAP = "/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1"


def guards():
    spec = importlib.util.spec_from_file_location("recoil_current_npc_guards", ROOT / "Tools/Integration/NPCInteractionV1/common.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.guard_rows()
    assert len(rows) == 703, "Adopt a changed epoch explicitly, not automatically"
    assert module.guards_match(rows), "Current protected assets differ"
    return rows


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity", required=True)
    args = parser.parse_args()
    assert args.identity.replace("_", "").isalnum()
    out = BASE / args.identity
    assert not out.exists(), "Preserve occupied evidence"
    rows = guards()
    out.mkdir(parents=True)
    write(out / "preflight.json", {"identity": args.identity, "guards": rows, "guard_count": len(rows),
        "scope": "new read-only firing/source diagnosis; no save or publication"})
    print("Current guard preflight:", len(rows), "exact")
