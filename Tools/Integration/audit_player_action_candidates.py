"""Read-only named candidates and local hashes, never native acceptance."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def checked(entry):
    path = ROOT / entry["path"]
    ok = path.is_file() and path.stat().st_size == entry["size_bytes"]
    ok = ok and digest(path) == entry["sha256"]
    return {"path": entry["path"], "size_bytes": entry["size_bytes"],
            "sha256": entry["sha256"], "local_match": bool(ok)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT) or output.exists():
        raise RuntimeError("Use a new workspace metadata path; preserve prior records")
    manifests = {}
    for entry in read("Assets/Sync/CATALOG.json")["active_manifests"]:
        if digest(ROOT / entry["path"]) != entry["sha256"]:
            raise RuntimeError("Catalog hash conflict: " + entry["path"])
        manifests[entry["asset_id"]] = read(entry["path"])["files"]
    character = manifests["character-ue582-integration-baseline"]
    city = manifests["france-liberation-content"]
    motion = manifests["rifle-pro-mocap-ue582-selected"]
    groups = {
        "hold_fire": "Rifle_Idle Rifle_ShootOnce",
        "run": "Rifle_RunFwdLoop Rifle_RunBwdLoop Rifle_StrafeRunLeftLoop Rifle_StrafeRunRightLoop Rifle_SprintStart Rifle_SprintLoop Rifle_SprintStop_LU Rifle_SprintStop_RU",
        "jump": "Rifle_Jump_Platformer_Start Rifle_Jump_Platformer_Fall Rifle_Jump_Platformer_Land Rifle_Jump_Idle_ALL Rifle_Jump_WalkFwdShort_ALL",
        "slow_walk_adaptation": "Rifle_WalkFwdLoop Rifle_WalkBwdLoop Rifle_StrafeLeftLoop Rifle_StrafeRightLoop",
        "crouch": "Rifle_Idle2Crouch Rifle_CrouchLoop Rifle_Crouch2Idle Rifle_Crouch_WalkFwd Rifle_Crouch_WalkBwd Rifle_Crouch2Prone Rifle_Prone2Crouch",
        "prone": "Rifle_Idle2Prone Rifle_Prone Rifle_Prone2Idle Rifle_Prone_WalkFwd Rifle_Prone_WalkBwd Rifle_Prone_WalkFwdStart",
    }
    selection = {}
    for name, names in groups.items():
        stems = set(names.split())
        found = [e for e in character if "/Animations/InPlace/" in e["path"] and Path(e["path"]).stem in stems]
        selection[name] = {"status": "source_candidates_not_runtime_acceptance",
                           "candidates": [checked(e) for e in found],
                           "names_not_found": sorted(stems - {Path(e["path"]).stem for e in found})}
    selection["feedback_textures_trails"] = {
        "status": "candidates_not_ready_flash_impact_or_decal_system",
        "candidates": [checked(e) for e in city if "/Texture/BulletHoles/" in e["path"] or "/Particle/BulletTrail/" in e["path"]]}
    selection["hold_fire_comparison"] = {
        "status": "accepted_source_motion_not_soldier_contact_acceptance",
        "candidates": [checked(e) for e in motion if Path(e["path"]).stem in {"W2_Stand_Aim_Idle_IP", "W2_Stand_Fire_Single_IP"}]}
    discovery = read("Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1/Evidence/ue_load_inventory.json")
    gaps = {}
    for key, terms in {"dedicated_muzzle_flash": ("muzzle", "gunflash"),
                       "dedicated_surface_impact": ("impact", "bullethit"),
                       "dedicated_sneak": ("sneak", "stealth")}.items():
        active = [e["path"] for e in character + city + motion if any(t in Path(e["path"]).stem.lower() for t in terms)]
        prior = [e["path"] for e in discovery["assets"] if any(t in e["path"].rsplit("/", 1)[-1].lower() for t in terms)]
        gaps[key] = {"active_named_matches": active, "prior_discovery_named_matches": prior,
                     "status": "named_candidates_require_inspection" if active or prior else "missing_in_inspected_named_sets",
                     "limit": "No exhaustive semantic or unopened-archive audit; differently named assets may exist"}
    guards = [checked(e) for name in ("CITY_NAVIGATION_DRAFT_INVENTORY_20261002", "RELOAD_DRAFT_SNAPSHOT_20261002")
              for e in read("Assets/Integration/" + name + ".json")["files"]]
    failures = [e["path"] for g in selection.values() for e in g["candidates"] if not e["local_match"]]
    failures += [e["path"] for e in guards if not e["local_match"]]
    result = {"schema_version": 1, "recorded_at": datetime.now(timezone.utc).isoformat(), "owner": "yg745",
              "scope": "Read-only named candidates and local size/SHA-256; not native load, deformation, gameplay, remote verification or restore authority",
              "native_changes": False, "catalog_changed": False, "selection": selection,
              "named_gap_screen": gaps, "guarded_drafts": guards, "verification_failures": failures}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(output), "guarded_drafts": len(guards),
                      "groups": {k: {"count": len(v["candidates"]), "names_not_found": v.get("names_not_found", [])} for k, v in selection.items()},
                      "named_gap_screen": gaps, "failures": failures}))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
