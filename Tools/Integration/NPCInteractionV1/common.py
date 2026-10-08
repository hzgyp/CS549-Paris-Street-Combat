import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1"
DEST = "/Game/ParisCombat/AI/NPCInteractionV1"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def apply_recoil_binary_ledger(rows, ledger):
    """Only three locally repaired display DLLs; immutable source epoch stays."""
    expected = {
        "Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18/Binaries/Win64/UnrealEditor-ParisGripBindingV18.dll",
        "Unreal/ParisStreetCombat/Plugins/ParisNPCGripV15/Binaries/Win64/UnrealEditor-ParisNPCGripV15.dll",
        "Unreal/ParisStreetCombat/Plugins/ParisNPCGripV15/Binaries/Win64/UnrealEditor-ParisNPCGripV15Editor.dll",
    }
    authority = "2026-10-07 user requests visible firing recoil repair for character presentation"
    assert ledger["authorization"] == authority
    proof_path = ROOT / ledger["proof"]
    assert digest(proof_path) == ledger["proof_sha256"], "Recoil installation receipt changed"
    proof = json.loads(proof_path.read_text(encoding="utf-8-sig"))
    assert proof["authorization"] == authority and proof["local_only"]
    assert proof["status"] == "pass_local_recoil_display_binaries_installed_runtime_unpassed"
    assert proof["original_guard_count"] == 703 and proof["unchanged_other_guard_count"] == 700 and proof["unchanged_other_guards"]
    assert digest(ROOT / proof["candidate_audit"]) == proof["candidate_audit_sha256"]
    audit = json.loads((ROOT / proof["candidate_audit"]).read_text())
    assert audit["status"] == "pass_finite_candidate_receipts_visual_review_separate"
    assert set(audit["receipts"]) == {"source", "motion", "contract", "visual"}
    for receipt in audit["receipts"].values():
        assert digest(ROOT / receipt["path"]) == receipt["sha256"], "Candidate recoil evidence changed"
    assert len(ledger["rows"]) == len(proof["new_rows"]) == len(proof["original_rows"]) == 3
    assert ledger["rows"] == proof["new_rows"]
    old = {r["path"]: r for r in proof["original_rows"]}
    new = {r["path"]: r for r in ledger["rows"]}
    assert set(old) == set(new) == expected
    assert expected.issubset({r["path"] for r in rows}), "Display paths missing from source epoch"
    assert len(proof["backups"]) == 3
    for original, backup in zip(proof["original_rows"], proof["backups"]):
        assert digest(ROOT / backup) == original["sha256"], "Original display DLL backup changed"
    for i, row in enumerate(rows):
        if row["path"] in expected:
            assert all(row[k] == old[row["path"]][k] for k in ("path", "size_bytes", "sha256")), "Recoil allowlist does not match original epoch"
            rows[i] = dict(new[row["path"]])
    return rows


def _base_guard_rows():
    epoch_path = ROOT / "Docs/Development/NPCInteractionV1/GUARD_EPOCH_20261006.json"
    if epoch_path.exists():
        epoch = json.loads(epoch_path.read_text())
        snapshot = ROOT / epoch["snapshot"]
        assert digest(snapshot) == epoch["sha256"], "Selected immutable epoch changed"
        proof = json.loads(snapshot.read_text())
        assert proof["status"] == epoch["status"] and proof["release"] == epoch["release"]
        rows = proof["files"]
        assert len(rows) == epoch["count"] == 678
        approved = {r["path"]: r for r in rows}
        assert len(approved) == len(rows), "Duplicate selected guard path"
        inventory = json.loads((ROOT / "Docs/Development/NPCInteractionV1/NPC_INTERACTION_V1_DRAFT_INVENTORY_20261004.json").read_text())
        for row in inventory["files"]:
            if row["path"] in approved:
                assert all(row[k] == approved[row["path"]][k] for k in ("size_bytes", "sha256")), "B package conflicts with selected epoch"
            else:
                rows.append(row)
                approved[row["path"]] = row
        assert len(rows) == inventory["combined_protected_count"], "Register explicit epoch and added B packages"
        # The 7 October human authorization covers ONE local map increment,
        # not a Catalog/release rebase. Preserve A's immutable snapshot and
        # authenticate the exact author receipt before replacing its two aliases.
        map_ledger_path = ROOT / "Docs/Development/NPCInteractionV1/AUTHORIZED_FORMAL_MAP_20261007.json"
        if map_ledger_path.exists():
            ledger = json.loads(map_ledger_path.read_text())
            assert ledger["authorization"] == "2026-10-07 user explicitly permits formal map NPC AI integration and play regression"
            proof_path = ROOT / ledger["proof"]
            assert digest(proof_path) == ledger["proof_sha256"], "Formal map receipt changed"
            proof = json.loads(proof_path.read_text())
            assert proof["authorization"] == ledger["authorization"]
            assert proof["status"] == "pass_formal_combat_map_saved_fresh_runtime_unpassed"
            assert proof["authorized_map_mutation_verified"] and proof["protected_guards_unchanged_except_authorized_map"]
            expected = {
                "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap",
                "Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap",
            }
            assert {r["path"] for r in ledger["rows"]} == expected
            assert ledger["rows"] == proof["new_map_rows"]
            old = {r["path"]: r for r in proof["original_map_rows"]}
            new = {r["path"]: r for r in ledger["rows"]}
            assert set(old) == expected and len({r["sha256"] for r in new.values()}) == 1
            for i, row in enumerate(rows):
                if row["path"] in expected:
                    assert all(row[k] == old[row["path"]][k] for k in ("path", "size_bytes", "sha256"))
                    rows[i] = dict(new[row["path"]])
        return rows
    snapshot = ROOT / "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FirstPersonFormalV21/selected_v1/result.json"
    rows = json.loads(snapshot.read_text())["files"]
    # A human explicitly authorized the shared FF change on 5 October. Preserve
    # the immutable FP epoch; only this exact, evidence-backed allowlist advances.
    ledger_path = ROOT / "Docs/Development/NPCInteractionV1/AUTHORIZED_SHARED_MUTATIONS_20261005.json"
    if ledger_path.exists():
        ledger = json.loads(ledger_path.read_text())
        assert ledger["authorization"] == "2026-10-05 user explicitly permits shared friendly-fire integration and regression"
        expected = {
            "Unreal/ParisStreetCombat/Content/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2.uasset",
            "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2.uasset",
        }
        assert {r["path"] for r in ledger["rows"]} == expected
        mutations = {r["path"]: r for r in ledger["rows"]}
        proof = json.loads((STORE / "Evidence/NPCInteractionV1" / ledger["author_identity"] / "friendly_fire_author.json").read_text())
        assert proof["status"].startswith("pass_") and proof["authorized_shared_mutations_verified"]
        assert proof["protected_guards_unchanged_except_authorized_mutations"]
        proved = {r["path"]: r for r in proof["new_shared_rows"]}
        for i, row in enumerate(rows):
            if row["path"] in mutations:
                mutation = mutations[row["path"]]
                assert row["sha256"] == mutation["original_sha256"]
                assert row["size_bytes"] == mutation["original_size_bytes"]
                assert all(mutation[k] == proved[row["path"]][k] for k in ("size_bytes", "sha256"))
                rows[i] = {"path": row["path"], "size_bytes": mutation["size_bytes"], "sha256": mutation["sha256"]}
    known = {row["path"] for row in rows}
    inventory = json.loads((ROOT / "Docs/Development/NPCInteractionV1/NPC_INTERACTION_V1_DRAFT_INVENTORY_20261004.json").read_text())
    assert len(rows) == 555, "Unexpected approved epoch; explicitly reconcile, never silently rebase"
    approved = {row["path"]: row for row in rows}
    for row in inventory["files"]:
        if row["path"] in approved:
            assert all(row[field] == approved[row["path"]][field]
                       for field in ("size_bytes", "sha256")), "Lane B conflicts with approved epoch"
        else:
            assert row["path"] not in known, "Duplicate inventory path"
            rows.append(row)
            known.add(row["path"])
    assert len(rows) == inventory["combined_protected_count"]
    return rows


def guard_rows():
    # Presentation-only increment is independent of pending AI/map epoch work.
    # An incompatible or missing prerequisite fails closed in the exact ledger.
    rows = _base_guard_rows()
    recoil_ledger = ROOT / "Docs/Development/RecoilV1/AUTHORIZED_LOCAL_BINARIES_20261007.json"
    if recoil_ledger.exists():
        rows = apply_recoil_binary_ledger(rows, json.loads(recoil_ledger.read_text()))
    return rows


def guards_match(rows):
    return all(
        (ROOT / row["path"]).is_file()
        and (ROOT / row["path"]).stat().st_size == row["size_bytes"]
        and digest(ROOT / row["path"]) == row["sha256"]
        for row in rows
    )


def package_file(package):
    suffix = ".umap" if "/Maps/" in package else ".uasset"
    return STORE / "Content" / (package.removeprefix("/Game/") + suffix)
