"""Regression checks for explicitly reviewed public course PDFs."""
import hashlib
import json
import unittest
from unittest.mock import patch

import check_asset_storage as guard


class CourseDocumentStorageTests(unittest.TestCase):
    def setUp(self):
        self.path = "Docs/Assignments/Assignment3/test.pdf"
        self.blob = b"%PDF-1.4\nunit-test fixture\n%%EOF\n"
        self.entry = {
            "path": self.path, "kind": "project_course_report",
            "public_review": "approved", "provenance": "Own course report",
            "reviewed_by": "Test", "documents": ["Docs/test.md"],
            "approved_versions": [{"size_bytes": len(self.blob),
                "sha256": hashlib.sha256(self.blob).hexdigest()}],
        }

    def staged_policy(self, **changes):
        entry = dict(self.entry, **changes)
        payload = json.dumps({"schema_version": 1, "files": [entry]}).encode()

        def fake_git(*args):
            if args == ("ls-files", "--", guard.COURSE_DOCUMENT_LIST):
                return guard.COURSE_DOCUMENT_LIST.encode()
            if args == ("show", ":" + guard.COURSE_DOCUMENT_LIST):
                return payload
            if args == ("show", ":Docs/test.md"):
                return ("[Report](" + guard.posixpath.relpath(entry["path"], "Docs") + ")").encode()
            raise AssertionError(args)

        return patch.object(guard, "git", fake_git)

    def test_approved_exact_pdf(self):
        guard.verify_course_document(self.path, self.blob, self.entry)

    def test_modified_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            guard.verify_course_document(self.path, self.blob.replace(b"fixture", b"changed"), self.entry)

    def test_false_pdf_and_truncated_pdf_rejected_even_with_matching_hash(self):
        for blob in (b"private zip disguised as PDF", b"%PDF-1.4\ntruncated"):
            entry = dict(self.entry, approved_versions=[{
                "size_bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}])
            with self.assertRaisesRegex(ValueError, "Invalid"):
                guard.verify_course_document(self.path, blob, entry)

    def test_oversized_pdf_rejected(self):
        blob = b"%PDF-1.4\n" + b"x" * guard.COURSE_DOCUMENT_LIMIT + b"\n%%EOF"
        with self.assertRaisesRegex(ValueError, "oversized"):
            guard.verify_course_document(self.path, blob, self.entry)

    def test_staged_approval_and_link(self):
        with self.staged_policy():
            self.assertIn(self.path, guard.course_document_allowlist(staged=True))

    def test_private_vendor_and_non_pdf_paths_not_eligible(self):
        for path in ("Assets/LocalShared/private.pdf", "Docs/Submission/LocalEvidence/email.pdf",
                     "Docs/Assignments/model.fbx", "Docs/Assignments/report.docx"):
            with self.staged_policy(path=path):
                with self.assertRaisesRegex(ValueError, "Invalid course document exception"):
                    guard.course_document_allowlist(staged=True)

    def test_existing_proposal_path_supported_when_explicitly_approved(self):
        path = "Docs/Proposal/CS549_Assignment1_Proposal.pdf"
        with self.staged_policy(path=path):
            self.assertIn(path, guard.course_document_allowlist(staged=True))

    def test_vendor_document_kind_is_not_course_approval(self):
        with self.staged_policy(path="Docs/Proposal/vendor.pdf", kind="vendor_document"):
            with self.assertRaisesRegex(ValueError, "Invalid course document exception"):
                guard.course_document_allowlist(staged=True)

    def test_missing_public_review_rejected(self):
        with self.staged_policy(public_review="pending"):
            with self.assertRaisesRegex(ValueError, "Invalid"):
                guard.course_document_allowlist(staged=True)

    def test_oversized_approval_rejected(self):
        with self.staged_policy(approved_versions=[{
                "size_bytes": guard.COURSE_DOCUMENT_LIMIT + 1, "sha256": "0" * 64}]):
            with self.assertRaisesRegex(ValueError, "byte approval"):
                guard.course_document_allowlist(staged=True)

    def test_unstaged_policy_cannot_admit_staged_pdf(self):
        with patch.object(guard, "git", return_value=b""):
            self.assertEqual(guard.course_document_allowlist(staged=True), {})

    def test_unlisted_pdf_and_asset_bytes_remain_rejected(self):
        for path in ("Docs/Assignments/unlisted.pdf", "Assets/LocalShared/access.zip", "Assets/model.fbx"):
            with patch.object(guard, "code_allowlist", return_value=set()), \
                 patch.object(guard, "document_image_allowlist", return_value={}), \
                 patch.object(guard, "course_document_allowlist", return_value={}), \
                 patch.object(guard, "git", return_value=path.encode() + b"\0"):
                with self.assertRaisesRegex(ValueError, "Asset bytes"):
                    guard.check_git(False, False)

    def test_unapproved_outgoing_pdf_history_rejected(self):
        revision = "a" * 40

        def fake_git(*args):
            if args == ("ls-files", "-z"):
                return b""
            if args == ("rev-parse", revision + "^{commit}"):
                return revision.encode()
            if args == ("rev-list", "--objects", revision):
                return ("b" * 40 + " " + self.path).encode()
            if args == ("cat-file", "blob", "b" * 40):
                return self.blob.replace(b"fixture", b"changed")
            raise AssertionError(args)

        with patch.object(guard, "code_allowlist", return_value=set()), \
             patch.object(guard, "document_image_allowlist", return_value={}), \
             patch.object(guard, "course_document_allowlist", return_value={self.path: self.entry}), \
             patch.object(guard, "git", fake_git):
            with self.assertRaisesRegex(ValueError, "Unapproved"):
                guard.check_git(False, False, [revision])

    def test_real_reports_match_approvals(self):
        documents = guard.course_document_allowlist()
        expected = {
            "Docs/Proposal/CS549_Assignment1_Proposal.pdf",
            "Docs/Proposal/CS549_Assignment2_Proposal.pdf",
            "Docs/Assignments/Assignment3/Paris_Street_Combat_Assignment3_20261010_EN.pdf",
        }
        self.assertTrue(expected.issubset(documents))
        for path, entry in documents.items():
            guard.verify_course_document(path, (guard.ROOT / path).read_bytes(), entry)


if __name__ == "__main__":
    unittest.main()
