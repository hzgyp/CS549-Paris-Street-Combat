"""One descriptor increment only; immutable character/map/recoil epochs remain."""
import json

AUTHORITY = "2026-10-08 user approves smaller muzzle images and requests formal local asset integration"
DESCRIPTOR = "Unreal/ParisStreetCombat/WW2FranceLiberation.uproject"


def apply_muzzle_descriptor_ledger(rows, ledger, root, digest):
    assert ledger["authorization"] == AUTHORITY
    file = root / ledger["proof"]
    assert digest(file) == ledger["proof_sha256"], "Muzzle installation proof changed"
    proof = json.loads(file.read_text(encoding="utf-8-sig"))
    assert proof["authorization"] == AUTHORITY and proof["local_only"]
    assert proof["status"] == "pass_local_muzzle_install_fresh_formal_runtime_unpassed"
    assert proof["original_guard_count"] == 703 and proof["unchanged_other_guard_count"] == 702
    assert proof["unchanged_other_guards"]
    original, new = proof["original_row"], proof["new_row"]
    assert original["path"] == new["path"] == DESCRIPTOR
    assert ledger["row"] == new
    oldfile = root / proof["backup"]
    assert oldfile.stat().st_size == original["size_bytes"] and digest(oldfile) == original["sha256"]
    before = json.loads(oldfile.read_text())
    after = json.loads((root / DESCRIPTOR).read_text())
    assert not any(p["Name"] == "ParisMuzzleFlashV1" for p in before["Plugins"])
    before["Plugins"].append({"Name": "ParisMuzzleFlashV1", "Enabled": True})
    assert after == before, "Only the muzzle enable row may change"
    assert set(proof["candidate_receipts"]) == {"result", "log", "visual"}
    for kind, ref in proof["candidate_receipts"].items():
        assert digest(root / ref["path"]) == ref["sha256"], "Private firing evidence changed"
        data = json.loads((root / ref["path"]).read_text(encoding="utf-8-sig"))
        if kind == "result":
            assert data["mode"] == "Fresh" and data["status"] == "pass_real_transactions_native_visual_pending"
            assert not data["errors"] and data["private_configure_calls"] == 0
            assert all(data["checks"].values()) and data["native_profile_readback_exact"]
        elif kind == "log":
            assert data == {"strict_errors": 0, "exit_code": 0, "timed_out": False}
        else:
            assert data["candidate_runtime_visual_admitted"] and data["all_originals_inspected"]
    assert len(proof["files"]) == 29
    allowed_roots = (
        "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/MsvFx_MuzzleFlash_Pack/",
        "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/VFX/MuzzleFlashV1/",
        "Unreal/ParisStreetCombat/Plugins/ParisMuzzleFlashV1/Binaries/Win64/")
    assert len({r["destination"] for r in proof["files"]}) == 29
    destinations = {r["destination"] for r in proof["files"]}
    assert sum(p.startswith(allowed_roots[0]) for p in destinations) == 25
    assert {p for p in destinations if p.startswith(allowed_roots[1])} == {
        allowed_roots[1] + "DA_PC_MuzzleFlashV1.uasset"}
    assert {p for p in destinations if p.startswith(allowed_roots[2])} == {
        allowed_roots[2] + name for name in ("UnrealEditor-ParisMuzzleFlashV1.dll", "UnrealEditor-ParisMuzzleFlashV1.pdb", "UnrealEditor.modules")}
    for entry in proof["files"]:
        assert entry["destination"].startswith(allowed_roots)
        selected = root / entry["destination"]
        assert selected.stat().st_size == entry["size_bytes"] and digest(selected) == entry["sha256"]
    assert len(proof["aliases"]) == 2
    assert {r["path"]: r["target"] for r in proof["aliases"]} == {
        "Unreal/ParisStreetCombat/Content/MsvFx_MuzzleFlash_Pack":
            "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/MsvFx_MuzzleFlash_Pack",
        "Unreal/ParisStreetCombat/Content/ParisCombat/VFX/MuzzleFlashV1":
            "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/VFX/MuzzleFlashV1"}
    for alias in proof["aliases"]:
        assert (root / alias["path"]).resolve() == (root / alias["target"]).resolve()
    selected_rows = [i for i, r in enumerate(rows) if r["path"] == DESCRIPTOR]
    assert len(rows) == 703 and len(selected_rows) == 1
    index = selected_rows[0]
    assert rows[index] == original, "Descriptor allowlist does not match current prior epoch"
    rows[index] = dict(new)
    return rows
