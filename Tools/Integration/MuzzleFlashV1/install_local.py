"""Exact local install planning/proof; authored enable row is a separate patch."""
import argparse
import json
from pathlib import Path

from common import BASE, ROOT, STORE, INTAKE, guards, intake_rows, sha, write
from formal_contract import AUTHORITY, BUILD_ID, INTAKE_ID, PROFILE_PACKAGE, approved_profiles
from runtime_audit import transaction_receipt

DESCRIPTOR = "Unreal/ParisStreetCombat/WW2FranceLiberation.uproject"
PLUGIN = "Unreal/ParisStreetCombat/Plugins/ParisMuzzleFlashV1"


def row(path):
    return {"path": path.relative_to(ROOT).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha(path)}


def prepare(identity, verified):
    out = BASE / identity
    assert not out.exists(), "Preserve occupied local installation"
    protected = guards()
    intake_rows()
    approved_profiles()
    result, refs = transaction_receipt(verified)
    assert result["mode"] == "Fresh", "A fresh private process must load the saved profile"
    candidate = ROOT / ("tmp/muzzle-flash-v1/Candidate_" + INTAKE_ID)
    intake = json.loads((BASE / INTAKE_ID / "intake.json").read_text())
    assert len(intake["closure"]) == 25
    files = []
    for asset in intake["closure"]:
        relative = asset["package"].removeprefix("/Game/") + ".uasset"
        source = candidate / "Content" / relative
        assert source.stat().st_size == asset["size_bytes"] and sha(source) == asset["sha256"]
        assert sha(ROOT / asset["path"]) == asset["sha256"]
        files.append({"source": source.relative_to(ROOT).as_posix(),
            "destination": (STORE / "Content" / relative).relative_to(ROOT).as_posix(),
            "size_bytes": asset["size_bytes"], "sha256": asset["sha256"]})
    source = candidate / "Content" / (PROFILE_PACKAGE.removeprefix("/Game/") + ".uasset")
    assert source.is_file()
    files.append({"source": source.relative_to(ROOT).as_posix(),
        "destination": (STORE / "Content" / source.relative_to(candidate / "Content")).relative_to(ROOT).as_posix(),
        "size_bytes": source.stat().st_size, "sha256": sha(source)})
    build = ROOT / ("tmp/muzzle-flash-v1/Build_" + BUILD_ID + "/ParisMuzzleFlashV1")
    for source in sorted((build / "Binaries/Win64").iterdir()):
        assert source.name in ("UnrealEditor-ParisMuzzleFlashV1.dll", "UnrealEditor-ParisMuzzleFlashV1.pdb", "UnrealEditor.modules")
        files.append({"source": source.relative_to(ROOT).as_posix(),
            "destination": PLUGIN + "/Binaries/Win64/" + source.name,
            "size_bytes": source.stat().st_size, "sha256": sha(source)})
    assert len(files) == 29
    for entry in files:
        assert not (ROOT / entry["destination"]).exists(), "Preserve occupied formal file: " + entry["destination"]
    aliases = [
        {"path": "Unreal/ParisStreetCombat/Content/MsvFx_MuzzleFlash_Pack",
         "target": (STORE / "Content/MsvFx_MuzzleFlash_Pack").relative_to(ROOT).as_posix()},
        {"path": "Unreal/ParisStreetCombat/Content/ParisCombat/VFX/MuzzleFlashV1",
         "target": (STORE / "Content/ParisCombat/VFX/MuzzleFlashV1").relative_to(ROOT).as_posix()}]
    for alias in aliases:
        assert not (ROOT / alias["path"]).exists(), "Preserve occupied formal content binding"
    descriptor = json.loads((ROOT / DESCRIPTOR).read_text())
    assert not any(p["Name"] == "ParisMuzzleFlashV1" for p in descriptor["Plugins"])
    old = next(r for r in protected if r["path"] == DESCRIPTOR)
    out.mkdir()
    write(out / "install_plan.json", {"authorization": AUTHORITY, "local_only": True,
        "original_guards": protected, "original_row": old, "files": files, "aliases": aliases,
        "candidate_receipts": {k: {"path": Path(v["path"]).relative_to(ROOT).as_posix(),
            "sha256": v["sha256"]} for k, v in refs.items()}, "private_identity": verified})
    print("Exact29-file local plan prepared; formal writes have not started")


def finalize(identity):
    out = BASE / identity
    plan = json.loads((out / "install_plan.json").read_text())
    assert plan["authorization"] == AUTHORITY
    proof = out / "result.json"
    assert not proof.exists(), "Preserve occupied installation proof"
    original = json.loads((out / "descriptor.original").read_text())
    assert sha(out / "descriptor.original") == plan["original_row"]["sha256"]
    current = json.loads((ROOT / DESCRIPTOR).read_text())
    expected = json.loads(json.dumps(original))
    expected["Plugins"].append({"Name": "ParisMuzzleFlashV1", "Enabled": True})
    assert current == expected, "Only one enabled plugin row is authorized"
    for source in plan["original_guards"]:
        if source["path"] != DESCRIPTOR:
            actual = row(ROOT / source["path"])
            assert all(actual[k] == source[k] for k in actual), "Preserve the other702 guards"
    for entry in plan["files"]:
        selected = ROOT / entry["destination"]
        assert selected.stat().st_size == entry["size_bytes"] and sha(selected) == entry["sha256"]
        assert sha(ROOT / entry["source"]) == entry["sha256"]
    for alias in plan["aliases"]:
        assert (ROOT / alias["path"]).resolve() == (ROOT / alias["target"]).resolve()
    for receipt in plan["candidate_receipts"].values():
        assert sha(ROOT / receipt["path"]) == receipt["sha256"]
    write(proof, {"authorization": AUTHORITY, "status": "pass_local_muzzle_install_fresh_formal_runtime_unpassed",
        "local_only": True, "original_guard_count": 703, "unchanged_other_guard_count": 702,
        "unchanged_other_guards": True, "original_row": plan["original_row"], "new_row": row(ROOT / DESCRIPTOR),
        "backup": (out / "descriptor.original").relative_to(ROOT).as_posix(),
        "candidate_receipts": plan["candidate_receipts"], "files": plan["files"], "aliases": plan["aliases"],
        "private_identity": plan["private_identity"], "fresh_formal_runtime_passed": False})
    print(json.dumps({"proof": proof.relative_to(ROOT).as_posix(), "proof_sha256": sha(proof), "row": row(ROOT / DESCRIPTOR)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("identity")
    parser.add_argument("--verified")
    parser.add_argument("--finalize", action="store_true")
    args = parser.parse_args()
    finalize(args.identity) if args.finalize else prepare(args.identity, args.verified)
