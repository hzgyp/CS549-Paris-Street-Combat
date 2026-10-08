"""Read-only guard/receipt authentication tests for the local formal increment."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import common

LEDGER = common.ROOT / "Docs/Development/NPCInteractionV1/AUTHORIZED_FORMAL_MAP_20261007.json"


@unittest.skipUnless(LEDGER.exists(), "Formal map has not been adopted locally")
class FormalMapGuardTest(unittest.TestCase):
    def tampered(self, change):
        ledger = json.loads(LEDGER.read_text())
        change(ledger)
        original = Path.read_text

        def read(path, *args, **kwargs):
            return json.dumps(ledger) if path == LEDGER else original(path, *args, **kwargs)

        with patch.object(Path, "read_text", read):
            with self.assertRaises(AssertionError):
                common.guard_rows()

    def test_current_rows_and_immutable_a_epoch(self):
        rows = common.guard_rows()
        self.assertEqual(len(rows), 703)
        self.assertTrue(common.guards_match(rows))
        epoch = json.loads((common.ROOT / "Docs/Development/NPCInteractionV1/GUARD_EPOCH_20261006.json").read_text())
        self.assertEqual(common.digest(common.ROOT / epoch["snapshot"]), epoch["sha256"])
        proof = json.loads((common.ROOT / epoch["snapshot"]).read_text())
        self.assertEqual(len(proof["files"]), 678)
        old = [r for r in proof["files"] if r["path"].endswith("Maps/LV_ParisStreetCombat_V1.umap")]
        self.assertEqual(len(old), 2)
        self.assertEqual({r["sha256"] for r in old}, {"70df2be5458961341a8ca47b473d1e89bb1a68276c4395941a8000532053f5b6"})

    def test_receipt_checksum_tamper_is_rejected(self):
        self.tampered(lambda ledger: ledger.update(proof_sha256="0" * 64))

    def test_new_map_row_tamper_is_rejected(self):
        self.tampered(lambda ledger: ledger["rows"][0].update(sha256="0" * 64))

    def test_other_asset_authority_is_rejected(self):
        self.tampered(lambda ledger: ledger["rows"][0].update(path="Unreal/ParisStreetCombat/WW2FranceLiberation.uproject"))


if __name__ == "__main__":
    unittest.main()
