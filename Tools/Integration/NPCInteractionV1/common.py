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


def guard_rows():
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
