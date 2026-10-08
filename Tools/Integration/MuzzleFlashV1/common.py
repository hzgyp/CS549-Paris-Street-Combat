"""Private muzzle effect evidence and existing 703-path protection."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("CS549_MUZZLE_ROOT", Path(__file__).resolve().parents[3]))
STORE = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1"
BASE = STORE / "Evidence/MuzzleFlashV1"
INTAKE = ROOT / "Assets/LocalWorking/Intake/2026-10-04/01_Muzzle_Flash_VFX"
PACKAGE_ROOT = "/Game/MsvFx_MuzzleFlash_Pack"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def guards():
    file = ROOT / "Tools/Integration/NPCInteractionV1/common.py"
    spec = importlib.util.spec_from_file_location("muzzle_selected_guards", file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.guard_rows()
    assert len(rows) == 703 and module.guards_match(rows), "Preserve selected 703 paths"
    return rows


def intake_rows():
    data = json.loads((ROOT / "Assets/Integration/XIAN_YU_INTAKE_AUDIT_20261004.json").read_text())["vfx"]
    assert len(data["files"]) == data["file_count"] == 68
    assert sum(r["size_bytes"] for r in data["files"]) == data["size_bytes"] == 78239739
    for row in data["files"]:
        file = ROOT / row["path"]
        assert file.stat().st_size == row["size_bytes"] and sha(file) == row["sha256"], "Intake changed: " + row["path"]
    return data["files"]
