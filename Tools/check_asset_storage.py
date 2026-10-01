"""Check selected asset manifests and prevent asset bytes returning to Git."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ASSET_SUFFIX = re.compile(r"\.(uasset|umap|blend|fbx|obj|wav|exr|zip|7z|rar|pdf|docx|pptx|png|jpg|jpeg|webp|gif|mp4|glb|gltf|bin|tga|tif|tiff|psd)$", re.I)
RAW_PREFIX = "HistoricalReference/NormandyContext/archive/"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def safe_path(base: Path, relative: str) -> Path:
    p = PurePosixPath(relative)
    if not relative or p.is_absolute() or ".." in p.parts or "\\" in relative or ":" in relative:
        raise ValueError(f"Unsafe relative path: {relative}")
    target = (base / Path(*p.parts)).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f"Path escapes root: {relative}")
    return target


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def verify_file(path: Path, item: dict) -> None:
    if not path.is_file() or path.stat().st_size != item["size_bytes"] or sha256(path) != item["sha256"]:
        raise ValueError(f"Missing or mismatched asset: {item['path']}")


def check_manifests(local: bool, server: Path | None, selected: list[str]) -> int:
    catalog = json.loads((ROOT / "Assets/Sync/CATALOG.json").read_text(encoding="utf-8-sig"))
    seen: set[str] = set()
    count = 0
    found: set[str] = set()
    for release in catalog["active_manifests"]:
        manifest_path = safe_path(ROOT, release["path"])
        if sha256(manifest_path) != release["sha256"]:
            raise ValueError(f"Catalog hash mismatch: {release['path']}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if manifest["asset_id"] != release["asset_id"] or manifest["asset_version"] != release["asset_version"]:
            raise ValueError(f"Catalog identity mismatch: {release['path']}")
        if manifest["file_count"] != len(manifest["files"]):
            raise ValueError(f"Manifest count mismatch: {release['path']}")
        if manifest["size_bytes"] != sum(f["size_bytes"] for f in manifest["files"]):
            raise ValueError(f"Manifest byte total mismatch: {release['path']}")
        if manifest["file_count"] != release["file_count"] or manifest["size_bytes"] != release["size_bytes"]:
            raise ValueError(f"Catalog totals mismatch: {release['path']}")
        found.add(manifest["asset_id"])
        for item in manifest["files"]:
            target = safe_path(ROOT, item["path"])
            if item["path"] in seen:
                raise ValueError(f"Two active owners for path: {item['path']}")
            seen.add(item["path"])
            if item["storage"] != "sftp" or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
                raise ValueError(f"Invalid active storage/hash: {item['path']}")
            remote = item["remote_path"]
            if not remote.startswith(("/objects/sha256/", "/baselines/")):
                raise ValueError(f"Not an immutable asset location: {item['path']}")
            safe_path(ROOT, remote.lstrip("/"))
            if remote.startswith("/objects/sha256/") and remote != f"/objects/sha256/{item['sha256'][:2]}/{item['sha256']}":
                raise ValueError(f"Hash object location mismatch: {item['path']}")
            if selected and manifest["asset_id"] not in selected:
                continue
            if local:
                verify_file(target, item)
            if server:
                verify_file(safe_path(server, remote.lstrip("/")), item)
            count += 1
    if set(selected) - found:
        raise ValueError(f"Unknown asset selection: {sorted(set(selected) - found)}")
    return count


def code_allowlist() -> set[str]:
    data = json.loads((ROOT / "Assets/Sync/GIT_CODE_ALLOWLIST.json").read_text(encoding="utf-8-sig"))
    result = set()
    for entry in data["files"]:
        path = entry["path"]
        safe_path(ROOT, path)
        if not path.startswith("Unreal/ParisStreetCombat/Content/ParisCombat/") or not path.endswith(".uasset") or entry["kind"] != "team_blueprint_code":
            raise ValueError(f"Invalid binary code exception: {path}")
        result.add(path)
    return result


def check_git(history: bool, staged: bool) -> None:
    allowed = code_allowlist()
    current = [p.decode("utf-8") for p in git("ls-files", "-z").split(b"\0") if p]
    paths = set(current)
    if history:
        for line in git("rev-list", "--objects", "--all").decode("utf-8").splitlines():
            if " " in line:
                paths.add(line.split(" ", 1)[1])
    rejected = sorted(p for p in paths if (ASSET_SUFFIX.search(p) and p not in allowed) or p.startswith(RAW_PREFIX))
    if rejected:
        raise ValueError("Asset bytes/raw archives must stay outside Git:\n" + "\n".join(rejected))
    if staged:
        catalog = json.loads(git("show", ":Assets/Sync/CATALOG.json"))
        for release in catalog["active_manifests"]:
            blob = git("show", ":" + release["path"])
            if hashlib.sha256(blob).hexdigest() != release["sha256"]:
                raise ValueError(f"Staged manifest bytes differ from verified catalog: {release['path']}")
        changed = [p.decode("utf-8") for p in git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split(b"\0") if p]
        for p in changed:
            blob = git("show", ":" + p)
            if p in allowed:
                if len(blob) > 10 * 1024 * 1024:
                    raise ValueError(f"Approved Blueprint code exceeds 10 MiB: {p}")
            elif b"\0" in blob or len(blob) > 25 * 1024 * 1024:
                raise ValueError(f"Unclassified binary/oversized source: {p}")
            if blob.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
                raise ValueError(f"LFS pointer prohibited in source release: {p}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", action="store_true", help="Hash actual restored local assets")
    parser.add_argument("--sftp-root", type=Path, help="Administrator-only server filesystem verification")
    parser.add_argument("--asset-id", action="append", default=[])
    parser.add_argument("--git", action="store_true", help="Check tracked source paths")
    parser.add_argument("--history", action="store_true", help="Also check all reachable Git object paths")
    parser.add_argument("--staged", action="store_true", help="Check staged source bytes")
    args = parser.parse_args()
    count = check_manifests(args.local, args.sftp_root, args.asset_id)
    if args.git or args.history or args.staged:
        check_git(args.history, args.staged)
    print(f"Verified manifest metadata for {count} selected files; local/server hashes checked only when requested.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc))
