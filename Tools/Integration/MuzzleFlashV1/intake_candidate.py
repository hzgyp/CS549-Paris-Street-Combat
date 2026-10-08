"""Hash original delivery and find preliminary purchased-effect references."""
import argparse
import json
import re
from pathlib import Path
from common import ROOT, BASE, INTAKE, PACKAGE_ROOT, guards, intake_rows, sha, write


def candidate_closure(rows, native_seeds=()):
    packages = {PACKAGE_ROOT + "/" + (ROOT / r["path"]).relative_to(INTAKE).with_suffix("").as_posix(): r for r in rows}
    candidates = [PACKAGE_ROOT + "/Prefabs/Niagara_Riffle_MuzzleFlash_0" + str(i) for i in range(1, 5)]
    references = {}
    for package, row in packages.items():
        payload = (ROOT / row["path"]).read_bytes()
        ascii_refs = re.findall(rb"/(?:Game|Engine|Niagara)/[A-Za-z0-9_./-]+", payload)
        # Old package strings may use either UTF-8 or UTF-16LE.
        wide = payload.decode("utf-16-le", errors="ignore")
        refs = {p.decode("ascii").split(".", 1)[0] for p in ascii_refs}
        refs |= {p.split(".", 1)[0] for p in re.findall(r"/(?:Game|Engine|Niagara)/[A-Za-z0-9_./-]+", wide)}
        references[package] = sorted(refs)
    selected, pending, engine, unresolved = set(), list(candidates) + list(native_seeds), set(), set()
    while pending:
        package = pending.pop()
        if package in selected:
            continue
        assert package in packages, "Missing preliminary game dependency: " + package
        selected.add(package)
        for dependency in references[package]:
            if dependency.startswith("/Game/"):
                if dependency not in packages:
                    unresolved.add(dependency)
                elif dependency not in selected:
                    pending.append(dependency)
            else:
                engine.add(dependency)
    forbidden = ("/Blueprints/", "/Maps/", "/Guns/", "/Skeleton_Mesh/", "/Animation/", "HiveShot", "Shotgun")
    assert not any(any(term in package for term in forbidden) for package in selected), "Unexpected example gun/shell dependency"
    return candidates, [{"package": p, **packages[p], "references": references[p]} for p in sorted(selected)], sorted(engine), sorted(unresolved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity", required=True)
    parser.add_argument("--native-reference-identity")
    args = parser.parse_args()
    assert args.identity.replace("_", "").isalnum()
    out = BASE / args.identity
    assert not out.exists(), "Preserve occupied evidence"
    protected = guards()
    rows = intake_rows()
    native_seeds = []
    native_receipt = None
    if args.native_reference_identity:
        assert args.native_reference_identity.replace("_", "").isalnum()
        native_receipt = BASE / args.native_reference_identity / "result.json"
        native_data = json.loads(native_receipt.read_text())
        assert native_data["status"] == "failed_purchased_asset_gate_preserve"
        native_seeds = sorted({p for d in native_data["dependencies"]
                               for p in d["hard"] if p.startswith(PACKAGE_ROOT + "/")})
    candidates, closure, engine, unresolved = candidate_closure(rows, native_seeds)
    out.mkdir(parents=True)
    write(out / "preflight.json", {"guard_count": len(protected), "guards": protected, "source_files": rows})
    write(out / "intake.json", {"status": "pass_hashes_preliminary_reference_closure_native_unpassed",
        "identity": args.identity, "candidates": candidates, "closure": closure,
        "engine_reference_hints": engine, "unresolved_game_reference_hints": unresolved,
        "hard_dependency_classification": "native_gate_pending", "source_count": len(rows), "copied_count": len(closure),
        "native_reference_receipt": str(native_receipt.relative_to(ROOT)) if native_receipt else None,
        "native_reference_receipt_sha256": sha(native_receipt) if native_receipt else None,
        "native_reference_seeds": native_seeds,
        "source_bytes": sum(r["size_bytes"] for r in rows), "candidate_bytes": sum(r["size_bytes"] for r in closure),
        "native_runtime_passed": False, "package_root": PACKAGE_ROOT, "guard_count": len(protected)})
    print(json.dumps({"source_count": len(rows), "candidate_count": len(closure),
                      "candidate_bytes": sum(r["size_bytes"] for r in closure), "guard_count": len(protected)}))
