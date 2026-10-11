"""Check selected asset manifests and prevent asset bytes returning to Git."""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ASSET_SUFFIX = re.compile(r"\.(uasset|umap|blend|fbx|obj|wav|exr|zip|7z|rar|pdf|docx|pptx|png|jpg|jpeg|webp|gif|mp4|glb|gltf|bin|tga|tif|tiff|psd)$", re.I)
RAW_PREFIX = "HistoricalReference/NormandyContext/archive/"
DOCUMENT_IMAGE_LIST = "Assets/Sync/GIT_DOCUMENT_IMAGE_ALLOWLIST.json"
DOCUMENT_IMAGE_LIMIT = 5 * 1024 * 1024
DOCUMENT_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
COURSE_DOCUMENT_LIST = "Assets/Sync/GIT_COURSE_DOCUMENT_ALLOWLIST.json"
COURSE_DOCUMENT_LIMIT = 5 * 1024 * 1024


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


def document_image_allowlist(staged: bool = False) -> dict[str, dict]:
    return reviewed_document_allowlist(
        staged, DOCUMENT_IMAGE_LIST, "Docs/Images/", DOCUMENT_IMAGE_SUFFIXES,
        "project_document_illustration", DOCUMENT_IMAGE_LIMIT, "document image")


def course_document_allowlist(staged: bool = False) -> dict[str, dict]:
    return reviewed_document_allowlist(
        staged, COURSE_DOCUMENT_LIST, ("Docs/Assignments/", "Docs/Proposal/"), {".pdf"},
        "project_course_report", COURSE_DOCUMENT_LIMIT, "course document")


def reviewed_document_allowlist(staged: bool, list_path: str, prefix: str | tuple[str, ...],
                               suffixes: set[str], kind: str, limit: int,
                               label: str) -> dict[str, dict]:
    # Use the staged policy at commit time, never an unstaged approval.
    if staged:
        if not git("ls-files", "--", list_path).strip():
            return {}
        data = json.loads(git("show", ":" + list_path))
    else:
        path = ROOT / list_path
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("schema_version") != 1:
        raise ValueError(f"Invalid {label} allowlist schema")
    result = {}
    for entry in data["files"]:
        path = entry["path"]
        safe_path(ROOT, path)
        if (not path.startswith(prefix)
                or PurePosixPath(path).suffix.lower() not in suffixes
                or path in result or entry.get("kind") != kind
                or entry.get("public_review") != "approved"
                or not entry.get("provenance") or not entry.get("reviewed_by")
                or not entry.get("documents") or not entry.get("approved_versions")):
            raise ValueError(f"Invalid {label} exception: {path}")
        for version in entry["approved_versions"]:
            if (not isinstance(version["size_bytes"], int)
                    or not 0 < version["size_bytes"] <= limit
                    or not re.fullmatch(r"[0-9a-f]{64}", version["sha256"])):
                raise ValueError(f"Invalid {label} byte approval: {path}")
        for doc in entry["documents"]:
            target = safe_path(ROOT, doc)
            if not doc.startswith("Docs/") or not doc.endswith(".md"):
                raise ValueError(f"Invalid linked document: {doc}")
            content = (git("show", ":" + doc).decode("utf-8-sig") if staged
                       else target.read_text(encoding="utf-8-sig"))
            relative = posixpath.relpath(path, posixpath.dirname(doc))
            if "](" + relative + ")" not in content:
                raise ValueError(f"Document does not link approved {label}: {doc}: {path}")
        result[path] = entry
    return result


def verify_document_image(path: str, blob: bytes, entry: dict) -> None:
    suffix = PurePosixPath(path).suffix.lower()
    signatures = {
        ".png": blob.startswith(b"\x89PNG\r\n\x1a\n"),
        ".jpg": blob.startswith(b"\xff\xd8\xff"),
        ".jpeg": blob.startswith(b"\xff\xd8\xff"),
        ".gif": blob.startswith((b"GIF87a", b"GIF89a")),
        ".webp": blob.startswith(b"RIFF") and blob[8:12] == b"WEBP",
    }
    if not signatures.get(suffix) or not 0 < len(blob) <= DOCUMENT_IMAGE_LIMIT:
        raise ValueError(f"Invalid or oversized document image: {path}")
    digest = hashlib.sha256(blob).hexdigest()
    if not any(v["size_bytes"] == len(blob) and v["sha256"] == digest
               for v in entry["approved_versions"]):
        raise ValueError(f"Unapproved document image bytes: {path}")


def verify_course_document(path: str, blob: bytes, entry: dict) -> None:
    # Full content/privacy review precedes registering these exact bytes.
    if (PurePosixPath(path).suffix.lower() != ".pdf"
            or not blob.startswith(b"%PDF-") or not blob.rstrip().endswith(b"%%EOF")
            or not 0 < len(blob) <= COURSE_DOCUMENT_LIMIT):
        raise ValueError(f"Invalid or oversized course PDF: {path}")
    digest = hashlib.sha256(blob).hexdigest()
    if not any(v["size_bytes"] == len(blob) and v["sha256"] == digest
               for v in entry["approved_versions"]):
        raise ValueError(f"Unapproved course PDF bytes: {path}")


def check_git(history: bool, staged: bool, publish_refs: list[str] | None = None) -> None:
    allowed = code_allowlist()
    images = document_image_allowlist(staged)
    course_documents = course_document_allowlist(staged)
    documents = images | course_documents

    def verify_document(path: str, blob: bytes) -> None:
        verifier = verify_course_document if path in course_documents else verify_document_image
        verifier(path, blob, documents[path])

    current = [p.decode("utf-8") for p in git("ls-files", "-z").split(b"\0") if p]
    paths = set(current)
    historical_images = set()
    if history:
        for line in git("rev-list", "--objects", "--all").decode("utf-8").splitlines():
            if " " in line:
                oid, path = line.split(" ", 1)
                paths.add(path)
                if path in documents:
                    historical_images.add((oid, path))
    for revision in publish_refs or []:
        if not re.fullmatch(r"[0-9a-f]{40,64}", revision):
            raise ValueError("Publication revision must be a complete Git object ID")
        # Reject a blob/tree tag: assets could otherwise have no path to classify.
        commit = git("rev-parse", revision + "^{commit}").decode().strip()
        for line in git("rev-list", "--objects", commit).decode("utf-8").splitlines():
            if " " in line:
                oid, path = line.split(" ", 1)
                paths.add(path)
                if path in documents:
                    historical_images.add((oid, path))
    rejected = sorted(p for p in paths if (ASSET_SUFFIX.search(p) and p not in allowed and p not in documents) or p.startswith(RAW_PREFIX))
    if rejected:
        raise ValueError("Asset bytes/raw archives must stay outside Git:\n" + "\n".join(rejected))
    for path in set(current) & documents.keys():
        verify_document(path, git("show", ":" + path))
    for oid, path in historical_images:
        verify_document(path, git("cat-file", "blob", oid))
    if staged:
        catalog = json.loads(git("show", ":Assets/Sync/CATALOG.json"))
        for release in catalog["active_manifests"]:
            blob = git("show", ":" + release["path"])
            if hashlib.sha256(blob).hexdigest() != release["sha256"]:
                raise ValueError(f"Staged manifest bytes differ from verified catalog: {release['path']}")
        changed = [p.decode("utf-8") for p in git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split(b"\0") if p]
        for p in changed:
            blob = git("show", ":" + p)
            if p in documents:
                verify_document(p, blob)
            elif p in allowed:
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
    parser.add_argument("--publish-ref", action="append", default=[],
                        help="Check full ancestry of each exact outgoing commit; private recovery refs are not outgoing")
    args = parser.parse_args()
    count = check_manifests(args.local, args.sftp_root, args.asset_id)
    if args.git or args.history or args.staged or args.publish_ref:
        check_git(args.history, args.staged, args.publish_ref)
    print(f"Verified manifest metadata for {count} selected files; local/server hashes checked only when requested.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc))
