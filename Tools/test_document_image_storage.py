"""Regression checks for the narrow public document-image exception."""
import hashlib
import unittest
from unittest.mock import patch

import check_asset_storage as guard


class DocumentImageStorageTests(unittest.TestCase):
    def setUp(self):
        self.path = "Docs/Images/test.png"
        self.blob = b"\x89PNG\r\n\x1a\n" + b"test illustration"
        self.entry = {"approved_versions": [{
            "size_bytes": len(self.blob),
            "sha256": hashlib.sha256(self.blob).hexdigest(),
        }]}

    def test_approved_png(self):
        guard.verify_document_image(self.path, self.blob, self.entry)

    def test_changed_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            guard.verify_document_image(self.path, self.blob + b"changed", self.entry)

    def test_non_image_with_approved_hash_rejected(self):
        blob = b"private data disguised as PNG"
        entry = {"approved_versions": [{"size_bytes": len(blob),
                  "sha256": hashlib.sha256(blob).hexdigest()}]}
        with self.assertRaisesRegex(ValueError, "Invalid"):
            guard.verify_document_image(self.path, blob, entry)

    def test_oversize_rejected(self):
        blob = self.blob + b"x" * guard.DOCUMENT_IMAGE_LIMIT
        with self.assertRaisesRegex(ValueError, "oversized"):
            guard.verify_document_image(self.path, blob, self.entry)

    def test_historical_approved_version_allowed(self):
        entry = {"approved_versions": [self.entry["approved_versions"][0], {
            "size_bytes": len(self.blob) + 1, "sha256": "0" * 64}]}
        guard.verify_document_image(self.path, self.blob, entry)

    def test_current_reviewed_figures_and_links(self):
        images = guard.document_image_allowlist()
        self.assertGreaterEqual(len(images), 4)
        self.assertIn("Docs/Images/MissionLoopV1/PARIS_GRID_25CM_EXPANDED_L0_20261007.png", images)
        self.assertIn("Docs/Images/MissionLoopV1/PARIS_GRID_25CM_SAVED_L0_20261007.png", images)
        for path, entry in images.items():
            guard.verify_document_image(path, (guard.ROOT / path).read_bytes(), entry)

    def test_unannotated_maps_retain_full_25cm_raster(self):
        for scope in ("EXPANDED", "SAVED"):
            path = guard.ROOT / f"Docs/Images/MissionLoopV1/PARIS_GRID_25CM_{scope}_L0_20261007.png"
            blob = path.read_bytes()
            self.assertEqual(int.from_bytes(blob[16:20], "big"), 4032)
            self.assertEqual(int.from_bytes(blob[20:24], "big"), 4032)
            self.assertEqual(blob[24:26], b"\x01\x00")  # Original 1-bit grayscale.

    def staged_list(self, path=None, size=None, document_text=None):
        import json
        entry = dict(self.entry, path=path or self.path,
                     kind="project_document_illustration", public_review="approved",
                     provenance="Project-authored diagram", reviewed_by="Test",
                     documents=["Docs/test.md"])
        if size is not None:
            entry["approved_versions"] = [{"size_bytes": size, "sha256": "0" * 64}]
        payload = json.dumps({"schema_version": 1, "files": [entry]}).encode()

        def fake_git(*args):
            if args == ("ls-files", "--", guard.DOCUMENT_IMAGE_LIST):
                return guard.DOCUMENT_IMAGE_LIST.encode()
            if args == ("show", ":" + guard.DOCUMENT_IMAGE_LIST):
                return payload
            if args == ("show", ":Docs/test.md"):
                return (document_text if document_text is not None
                        else "![diagram](Images/test.png)").encode()
            raise AssertionError(args)

        return patch.object(guard, "git", fake_git)

    def test_staged_approval_read_from_index(self):
        with self.staged_list():
            self.assertIn(self.path, guard.document_image_allowlist(staged=True))

    def test_private_tree_exception_rejected(self):
        with self.staged_list(path="Assets/LocalShared/private.png"):
            with self.assertRaisesRegex(ValueError, "Invalid document image exception"):
                guard.document_image_allowlist(staged=True)

    def test_production_asset_exception_rejected(self):
        with self.staged_list(path="Docs/Images/model.fbx"):
            with self.assertRaisesRegex(ValueError, "Invalid document image exception"):
                guard.document_image_allowlist(staged=True)

    def test_missing_link_rejected(self):
        with self.staged_list(document_text="# No figure linked"):
            with self.assertRaisesRegex(ValueError, "does not link"):
                guard.document_image_allowlist(staged=True)

    def test_oversize_approval_rejected(self):
        with self.staged_list(size=guard.DOCUMENT_IMAGE_LIMIT + 1):
            with self.assertRaisesRegex(ValueError, "byte approval"):
                guard.document_image_allowlist(staged=True)

    def test_unlisted_tracked_image_rejected(self):
        with patch.object(guard, "code_allowlist", return_value=set()), \
             patch.object(guard, "document_image_allowlist", return_value={}), \
             patch.object(guard, "git", return_value=b"Docs/Images/unlisted.png\0"):
            with self.assertRaisesRegex(ValueError, "Asset bytes"):
                guard.check_git(False, False)

    def test_unapproved_outgoing_image_history_rejected(self):
        revision = "a" * 40

        def fake_git(*args):
            if args == ("ls-files", "-z"):
                return b""
            if args == ("rev-parse", revision + "^{commit}"):
                return revision.encode()
            if args == ("rev-list", "--objects", revision):
                return ("b" * 40 + " " + self.path).encode()
            if args == ("cat-file", "blob", "b" * 40):
                return self.blob + b"unapproved history"
            raise AssertionError(args)

        with patch.object(guard, "code_allowlist", return_value=set()), \
             patch.object(guard, "document_image_allowlist", return_value={self.path: self.entry}), \
             patch.object(guard, "git", fake_git):
            with self.assertRaisesRegex(ValueError, "Unapproved"):
                guard.check_git(False, False, [revision])


if __name__ == "__main__":
    unittest.main()
