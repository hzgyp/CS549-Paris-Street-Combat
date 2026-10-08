"""In-memory protection-allowlist tests, not native evidence."""
import copy
import hashlib
import json
import unittest
from types import SimpleNamespace

from guard_contract import apply_muzzle_descriptor_ledger, AUTHORITY, DESCRIPTOR


class MemoryPath:
    def __init__(self, fs, name=""):
        self.fs, self.name = fs, name

    def __truediv__(self, name):
        return MemoryPath(self.fs, self.name + ("/" if self.name else "") + name)

    def read_text(self, **kwargs):
        return self.fs[self.name].decode()

    def stat(self):
        return SimpleNamespace(st_size=len(self.fs[self.name]))

    def resolve(self):
        return self.fs.get("alias:" + self.name, self.name)


class DescriptorAllowlistTests(unittest.TestCase):
    def setUp(self):
        self.fs = {}
        self.root = MemoryPath(self.fs)
        self.digest = lambda p: hashlib.sha256(p.fs[p.name]).hexdigest()
        def put(name, value):
            self.fs[name] = json.dumps(value).encode() if isinstance(value, dict) else value
            return {"path": name, "size_bytes": len(self.fs[name]), "sha256": self.digest(self.root / name)}
        self.put = put
        before = {"FileVersion": 3, "Plugins": [{"Name": "Accepted", "Enabled": True}]}
        old = put("backup", before)
        old["path"] = DESCRIPTOR
        after = copy.deepcopy(before)
        after["Plugins"].append({"Name": "ParisMuzzleFlashV1", "Enabled": True})
        new = put(DESCRIPTOR, after)
        self.rows = [old] + [{"path": "guard/%d" % i, "sha256": str(i), "size_bytes": i, "package": "unchanged"} for i in range(702)]
        refs = {}
        for kind, value in {
            "result": {"mode": "Fresh", "status": "pass_real_transactions_native_visual_pending", "errors": [],
                       "private_configure_calls": 0, "checks": {"actual": True}, "native_profile_readback_exact": True},
            "log": {"strict_errors": 0, "exit_code": 0, "timed_out": False},
            "visual": {"candidate_runtime_visual_admitted": True, "all_originals_inspected": True}}.items():
            refs[kind] = put(kind, value)
        home = "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/"
        files = []
        destinations = [home + "MsvFx_MuzzleFlash_Pack/test%d.uasset" % i for i in range(25)]
        destinations.append(home + "ParisCombat/VFX/MuzzleFlashV1/DA_PC_MuzzleFlashV1.uasset")
        destinations.extend("Unreal/ParisStreetCombat/Plugins/ParisMuzzleFlashV1/Binaries/Win64/" + name
            for name in ("UnrealEditor-ParisMuzzleFlashV1.dll", "UnrealEditor-ParisMuzzleFlashV1.pdb", "UnrealEditor.modules"))
        for dest in destinations:
            file = put(dest, b"synthetic test, not a commercial/native asset")
            file["destination"] = file.pop("path")
            files.append(file)
        aliases = [
            {"path": "Unreal/ParisStreetCombat/Content/MsvFx_MuzzleFlash_Pack", "target": home + "MsvFx_MuzzleFlash_Pack"},
            {"path": "Unreal/ParisStreetCombat/Content/ParisCombat/VFX/MuzzleFlashV1", "target": home + "ParisCombat/VFX/MuzzleFlashV1"}]
        for alias in aliases:
            self.fs["alias:" + alias["path"]] = alias["target"]
        self.proof = {"authorization": AUTHORITY, "local_only": True,
            "status": "pass_local_muzzle_install_fresh_formal_runtime_unpassed", "original_guard_count": 703,
            "unchanged_other_guard_count": 702, "unchanged_other_guards": True, "original_row": old,
            "new_row": new, "backup": "backup", "candidate_receipts": refs, "files": files, "aliases": aliases}
        proofrow = put("proof", self.proof)
        self.ledger = {"authorization": AUTHORITY, "proof": "proof", "proof_sha256": proofrow["sha256"], "row": new}

    def apply(self):
        return apply_muzzle_descriptor_ledger(copy.deepcopy(self.rows), self.ledger, self.root, self.digest)

    def test_only_one_descriptor_row_advances(self):
        applied = self.apply()
        self.assertEqual(applied[0], self.ledger["row"])
        self.assertEqual(applied[1:], self.rows[1:])

    def test_missing_authority_fails_closed(self):
        self.ledger["authorization"] = "unapproved"
        with self.assertRaises(AssertionError):
            self.apply()

    def test_altered_receipt_fails_closed(self):
        self.fs["proof"] += b" "
        with self.assertRaises(AssertionError):
            self.apply()

    def test_other_descriptor_change_fails_closed(self):
        after = json.loads(self.fs[DESCRIPTOR])
        after["Description"] = "unrelated edit"
        self.put(DESCRIPTOR, after)
        with self.assertRaises(AssertionError):
            self.apply()

    def test_commercial_file_drift_fails_closed(self):
        self.fs[self.proof["files"][0]["destination"]] = b"changed"
        with self.assertRaises(AssertionError):
            self.apply()

    def test_wrong_prior_epoch_fails_closed(self):
        self.rows[0]["sha256"] = "wrong"
        with self.assertRaises(AssertionError):
            self.apply()


if __name__ == "__main__":
    unittest.main()
