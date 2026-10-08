"""Read-only preparation checks, not native firing/lifecycle acceptance."""
import json
import unittest

from common import BASE, INTAKE, ROOT, guards, intake_rows, sha
from intake_candidate import candidate_closure
from asset_gate_contract import classify_systems
from effect_gate_contract import select_effect_candidates
from rate_pulse_contract import RATE, WINDOW, CAP, MAX_CAPTURES, select_rate_candidate
from geometry_mounts import measured_profiles, terminal_ring
from scale_contract import IDENTITY, INSTANCE_SCALE, scaled_profiles
from formal_contract import approved_profiles, BUILD_ID
from runtime_audit import transaction_receipt


class MuzzlePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = intake_rows()
        cls.candidates, cls.closure, cls.engine, cls.unresolved = candidate_closure(cls.rows)
        cls.receipt = json.loads((BASE / "intake_v2_20261007/intake.json").read_text())
        cls.plugin = ROOT / "Unreal/ParisStreetCombat/Plugins/ParisMuzzleFlashV1"

    def test_exact_supplier_inventory(self):
        self.assertEqual(len(self.rows), 68)
        self.assertEqual(sum(row["size_bytes"] for row in self.rows), 78239739)

    def test_four_present_rifle_systems(self):
        self.assertEqual(len(self.candidates), 4)
        packages = {row["package"] for row in self.closure}
        self.assertTrue(set(self.candidates) <= packages)
        self.assertEqual(len(packages), 24)

    def test_preliminary_receipt_reproduces(self):
        self.assertEqual(self.receipt["closure"], self.closure)
        self.assertEqual(self.receipt["unresolved_game_reference_hints"], self.unresolved)
        self.assertEqual(self.receipt["engine_reference_hints"], self.engine)
        self.assertFalse(self.receipt["native_runtime_passed"])

    def test_unknown_names_remain_unclassified(self):
        self.assertEqual(self.receipt["hard_dependency_classification"], "native_gate_pending")
        self.assertEqual(len(self.unresolved), 2)

    def test_private_copy_is_exact(self):
        candidate = ROOT / "tmp/muzzle-flash-v1/Candidate_intake_v2_20261007/Content"
        for row in self.closure:
            with self.subTest(package=row["package"]):
                relative = (ROOT / row["path"]).relative_to(INTAKE)
                self.assertEqual(sha(candidate / "MsvFx_MuzzleFlash_Pack" / relative), row["sha256"])

    def test_plugin_only_enabled_by_exact_local_authority(self):
        descriptor = json.loads((self.plugin / "ParisMuzzleFlashV1.uplugin").read_text())
        self.assertFalse(descriptor["EnabledByDefault"])
        formal = json.loads((ROOT / "Unreal/ParisStreetCombat/WW2FranceLiberation.uproject").read_text())
        ledger = ROOT / "Docs/Development/MuzzleFlashV1/AUTHORIZED_LOCAL_DESCRIPTOR_20261008.json"
        enabled = [p for p in formal["Plugins"] if p["Name"] == "ParisMuzzleFlashV1"]
        if ledger.exists():
            from guard_contract import apply_muzzle_descriptor_ledger, DESCRIPTOR
            authority = json.loads(ledger.read_text())
            proof = json.loads((ROOT / authority["proof"]).read_text())
            plan = json.loads((ROOT / authority["proof"]).with_name("install_plan.json").read_text())
            applied = apply_muzzle_descriptor_ledger(plan["original_guards"], authority, ROOT, sha)
            self.assertEqual(enabled, [{"Name": "ParisMuzzleFlashV1", "Enabled": True}])
            self.assertEqual(next(r for r in applied if r["path"] == DESCRIPTOR), proof["new_row"])
            self.assertEqual(applied, guards())
        else:
            self.assertFalse(enabled, "No enable row before exact local installation authority")

    def test_build_source_matches_current(self):
        built = ROOT / ("tmp/muzzle-flash-v1/Build_" + BUILD_ID + "/ParisMuzzleFlashV1")
        for directory in ("Source", "Config"):
            for source in (self.plugin / directory).rglob("*"):
                if source.is_file():
                    relative = source.relative_to(self.plugin)
                    with self.subTest(source=str(relative)):
                        self.assertEqual(sha(source), sha(built / relative))

    def test_later_human_size_approval_preserves_old_receipts(self):
        approved = approved_profiles()
        self.assertTrue(approved["human_scale_accepted"])
        self.assertEqual([p["scale"] for p in approved["profiles"]], [[.25]*3]*2)

    def test_failed_transaction_fixture_is_never_admitted(self):
        for identity in ("transactions_v1_20261008", "transactions_v2_20261008", "transactions_v3_20261008", "transactions_v5_20261008"):
            with self.subTest(identity=identity), self.assertRaises(AssertionError):
                transaction_receipt(identity, require_visual=False)

    def test_failed_teardown_observers_are_never_admitted(self):
        for identity in ("api_smoke_v1_20261008", "api_smoke_v2_20261008"):
            with self.subTest(identity=identity), self.assertRaises(AssertionError):
                transaction_receipt(identity, require_visual=False)

    def test_v4_native_success_does_not_waive_failed_fp_visual_review(self):
        result, _ = transaction_receipt("transactions_v4_20261008", require_visual=False)
        self.assertEqual(result["mode"], "Transient")
        review = json.loads((BASE / "transactions_v4_20261008/visual_review.json").read_text())
        self.assertFalse(review["candidate_runtime_visual_admitted"])
        self.assertTrue(review["all_originals_inspected"])
        self.assertEqual(review["unreadable_roles"], ["PC_City_Player"])
        self.assertEqual(len(review["images"]), 39)
        with self.assertRaises(AssertionError):
            transaction_receipt("transactions_v4_20261008")

    def test_v6_actual_transactions_and_original_visual_review_authenticate(self):
        result, refs = transaction_receipt("transactions_v6_20261008")
        self.assertEqual(result["mode"], "Transient")
        self.assertEqual(set(refs), {"result", "log", "visual"})

    def test_saved_fresh_native_success_does_not_waive_fp_visual_rejection(self):
        result, _ = transaction_receipt("fresh_profile_v1_20261008", require_visual=False)
        self.assertEqual(result["mode"], "Fresh")
        self.assertEqual(result["private_configure_calls"], 0)
        with self.assertRaises(AssertionError):
            transaction_receipt("fresh_profile_v1_20261008")

    def test_v13_deferred_capture_is_diagnostic_and_bounded(self):
        source = (self.plugin / "Source/ParisMuzzleFlashV1/Private/ParisMuzzleFlashV1.cpp").read_text()
        capture = source.split("bool UParisMuzzleReviewCapture::ArmDeferredReview", 1)[1].split("bool UParisMuzzleFlashSubsystem::DoesSupportWorldType", 1)[0]
        self.assertIn("Targets.Num() != 12", capture)
        self.assertIn("OnWorldPostActorTick.AddUObject", capture)
        self.assertIn("CaptureSceneDeferred()", capture)
        self.assertIn("CaptureRecords.Num() == 12", capture)
        self.assertNotIn("ProcessEvent", capture)
        self.assertNotIn("SpawnPulse", capture)
        self.assertNotIn("AdvanceSimulation", capture)
        self.assertIn("OnWorldPostActorTick.Remove", capture)

    def test_v12_diagnostic_dispatch_does_not_change_runtime_stale_guard(self):
        source = (self.plugin / "Source/ParisMuzzleFlashV1/Private/ParisMuzzleFlashV1.cpp").read_text()
        self.assertIn("FWorldDelegates::OnWorldPreActorTick.AddUObject", source)
        self.assertIn("FStructOnScope Parameters(Function)", source)
        self.assertIn("Actor->ProcessEvent(Function, Parameters.GetStructMemory())", source)
        dispatch = source.split("void UParisMuzzleReviewFireBatch::Dispatch", 1)[1].split("void UParisMuzzleReviewFireBatch::BeginDestroy", 1)[0]
        self.assertLess(dispatch.index("OnWorldPreActorTick.Remove"), dispatch.index("Actor->ProcessEvent"))
        self.assertNotIn("SpawnPulse", dispatch)
        self.assertNotIn("SetPropertyValue", dispatch)
        self.assertIn("Now - Commit > .25", source)
        fixture = (ROOT / "Tools/Integration/MuzzleFlashV1/ue_transactions.py").read_text()
        self.assertIn("yield .5, lambda: prop(batch, \"executed\")", fixture)
        self.assertNotIn('pawn.call_method("PC_RequestFire"', fixture)

    def test_uat_descriptor_transform_is_explicit(self):
        original = json.loads((self.plugin / "ParisMuzzleFlashV1.uplugin").read_text())
        built = ROOT / "tmp/muzzle-flash-v1/Build_native_v2_20261007/ParisMuzzleFlashV1/ParisMuzzleFlashV1.uplugin"
        packaged = json.loads(built.read_text())
        self.assertFalse(original.pop("EnabledByDefault"))
        additions = {key: packaged[key] for key in packaged.keys() - original.keys()}
        self.assertEqual(additions, {"CreatedBy": "", "CreatedByURL": "", "DocsURL": "",
                         "MarketplaceURL": "", "SupportURL": "", "EngineVersion": "5.8.0", "Installed": True})
        self.assertEqual({key: packaged[key] for key in original}, original)

    def test_current_selected_guards_unchanged(self):
        self.assertEqual(len(guards()), 703)

    def test_native_missing_candidate_file_is_existing_supplier_original(self):
        native = json.loads((BASE / "native_assets_v1_20261007/result.json").read_text())
        missing = {p for d in native["dependencies"] for p in d["missing_hard"]}
        self.assertEqual(missing, {"/Game/MsvFx_MuzzleFlash_Pack/Sources/Meshes/Sm_Root_Muzzle_Flash_0"})
        candidates, closure, _, _ = candidate_closure(self.rows, missing)
        self.assertEqual(candidates, self.candidates)
        self.assertEqual(len(closure), 25)
        self.assertTrue(missing <= {r["package"] for r in closure})

    def test_compiling_invalid_is_pending_not_success(self):
        row = {"loaded": True, "emitters": [1], "valid": False, "ready": False, "compiling": True}
        self.assertEqual(classify_systems([row]), "compiling")

    def test_finished_invalid_still_fails_even_when_another_compiles(self):
        row = {"loaded": True, "emitters": [1], "valid": False, "ready": False, "compiling": False}
        with self.assertRaises(AssertionError):
            classify_systems([row, dict(row, compiling=True)])

    def test_ready_requires_final_validity_and_readiness(self):
        row = {"loaded": True, "emitters": [1], "valid": True, "ready": False, "compiling": False}
        self.assertEqual(classify_systems([row]), "waiting_readiness")
        self.assertEqual(classify_systems([dict(row, ready=True)]), "ready")
        with self.assertRaises(AssertionError):
            classify_systems([dict(row, loaded=False)])

    def test_remaining_variants_never_replay_failed_rifle01(self):
        prior = json.loads((BASE / "effect_pulse_v1_20261007/result.json").read_text())
        selected = select_effect_candidates(self.candidates, "RemainingPulse", prior)
        self.assertEqual(selected, self.candidates[1:])
        self.assertNotIn(self.candidates[0], selected)
        with self.assertRaises(AssertionError):
            select_effect_candidates(self.candidates, "RemainingPulse", dict(prior, status="pass_"))
        with self.assertRaises(AssertionError):
            select_effect_candidates(self.candidates, "RemainingPulse", None)

    def test_one_new_instance_rate_candidate_only(self):
        reviews = [json.loads((BASE / identity / "visual_review.json").read_text()) for identity in
                   ("effect_pulse_v1_20261007", "remaining_pulse_v1_20261007")]
        self.assertEqual(select_rate_candidate(self.candidates, reviews), self.candidates[0])
        self.assertEqual((RATE, WINDOW, CAP, MAX_CAPTURES), (20., .10, 8., 12))
        with self.assertRaises(AssertionError):
            select_rate_candidate(self.candidates, [])
        with self.assertRaises(AssertionError):
            select_rate_candidate(self.candidates, [dict(reviews[0], candidate_admitted=True), reviews[1]])

    def test_terminal_profiles_require_saved_native_success(self):
        measured = measured_profiles()
        self.assertEqual(len(measured["profiles"]), 2)
        self.assertFalse(measured["ballistic_logic_changed"])
        for row in measured["profiles"]:
            self.assertEqual(row["terminal_unique_vertices"], 32)
            self.assertEqual(row["outward_axis_local"], [0, 1, 0])
            self.assertEqual(row["scale"], [1, 1, 1])

    def test_unknown_terminal_geometry_fails_closed(self):
        source = json.loads((BASE / "rifle_geometry_v1_20261008/result.json").read_text())["rifles"][0]
        with self.assertRaises(AssertionError):
            terminal_ring(dict(source, sockets=[{"name": "unreviewed"}]))
        with self.assertRaises(AssertionError):
            terminal_ring(dict(source, vertices=source["vertices"][:10]))

    def test_native_mount_success_does_not_admit_unaccepted_scale(self):
        directory = BASE / "mount_named_rotation_v2_20261008"
        native = json.loads((directory / "result.json").read_text())
        review = json.loads((directory / "visual_review.json").read_text())
        self.assertTrue(native["status"].startswith("pass_"))
        self.assertEqual(review["native_result_sha256"], sha(directory / "result.json"))
        self.assertEqual(len(review["images"]), 26)
        self.assertFalse(review["scale_accepted"])
        self.assertFalse(review["candidate_admitted"])
        self.assertFalse(review["human_approved"])
        for row in review["images"]:
            self.assertEqual(row["sha256"], sha(directory / row["file"]))

    def test_single_scale_comparison_changes_only_instance_scale(self):
        original = measured_profiles()
        adapted = scaled_profiles(original)
        self.assertEqual(INSTANCE_SCALE, .25)
        self.assertEqual(IDENTITY, "mount_scale_v3_20261008")
        self.assertFalse(adapted["human_scale_accepted"])
        for before, after in zip(original["profiles"], adapted["profiles"]):
            self.assertEqual(before["scale"], [1, 1, 1])
            self.assertEqual(after["scale"], [.25] * 3)
            self.assertEqual({k: v for k, v in before.items() if k != "scale"},
                             {k: v for k, v in after.items() if k != "scale"})
        with self.assertRaises(AssertionError):
            scaled_profiles(adapted)

    def test_latest_private_closure_still_exact(self):
        intake = json.loads((BASE / "intake_transaction_v1_20261008/intake.json").read_text())
        candidate = ROOT / "tmp/muzzle-flash-v1/Candidate_intake_transaction_v1_20261008/Content/MsvFx_MuzzleFlash_Pack"
        self.assertEqual(len(intake["closure"]), 25)
        for row in intake["closure"]:
            file = candidate / (ROOT / row["path"]).relative_to(INTAKE)
            self.assertEqual(file.stat().st_size, row["size_bytes"])
            self.assertEqual(sha(file), row["sha256"])

    def test_quarter_scale_native_and_review_are_not_formal_admission(self):
        directory = BASE / IDENTITY
        native = json.loads((directory / "result.json").read_text())
        review = json.loads((directory / "visual_review.json").read_text())
        self.assertEqual(native["activation_count"], 2)
        self.assertEqual(native["instance_scale"], .25)
        self.assertFalse(native["errors"])
        self.assertEqual(review["native_result_sha256"], sha(directory / "result.json"))
        self.assertTrue(review["visible_flame_smaller_than_unit_baseline"])
        self.assertEqual(len(review["images"]), 26)
        self.assertFalse(review["human_approved"])
        self.assertFalse(review["scale_accepted"])
        self.assertFalse(review["candidate_admitted"])
        for row in native["completions"]:
            self.assertTrue(row["component_valid"] and row["complete"])
            self.assertFalse(row["active"])
            self.assertLessEqual(row["age"], 8)
            self.assertEqual(row["relative_scale"], [.25] * 3)
        for row in review["images"]:
            self.assertEqual(row["sha256"], sha(directory / row["file"]))


if __name__ == "__main__":
    unittest.main()
