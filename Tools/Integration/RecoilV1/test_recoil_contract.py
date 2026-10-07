import unittest
from pathlib import Path
from recoil_contract import RecoilObserver


class RecoilContractTests(unittest.TestCase):
    def fresh(self):
        observer = RecoilObserver()
        self.assertFalse(observer.update(0, 0, True, False, 0, 0))
        return observer

    def test_one_committed_sequence_starts_once(self):
        observer = self.fresh()
        self.assertTrue(observer.update(1, 0, True, False, .05, .25))
        self.assertTrue(observer.update(1, 0, True, False, .1, .25))
        self.assertEqual(observer.starts, 1)

    def test_denied_request_does_not_start(self):
        observer = self.fresh()
        self.assertFalse(observer.update(0, 0, True, False, .2, 0))
        self.assertEqual(observer.starts, 0)

    def test_no_historical_replay(self):
        observer = RecoilObserver()
        self.assertFalse(observer.update(8, 3, True, False, 4, 4.25))
        self.assertEqual(observer.starts, 0)

    def test_repeat_committed_shot_restarts_existing_source(self):
        observer = self.fresh()
        observer.update(1, 0, True, False, .05, .25)
        self.assertTrue(observer.update(2, 0, True, False, .3, .5))
        self.assertEqual(observer.starts, 2)
        self.assertEqual(observer.started_at, .25)

    def test_duration_uses_authoritative_commit_time(self):
        observer = self.fresh()
        self.assertTrue(observer.update(1, 0, True, False, .3, .25))
        self.assertFalse(observer.update(1, 0, True, False, .8, .25))

    def test_death_cancels(self):
        observer = self.fresh()
        observer.update(1, 0, True, False, .05, .25)
        self.assertFalse(observer.update(1, 0, True, True, .1, .25))

    def test_reload_and_return_do_not_replay(self):
        observer = self.fresh()
        observer.update(1, 0, True, False, .05, .25)
        self.assertFalse(observer.update(1, 0, False, False, .1, .25))
        self.assertFalse(observer.update(1, 0, True, False, .5, .25))

    def test_reset_then_new_shot(self):
        observer = self.fresh()
        observer.update(1, 0, True, False, .05, .25)
        self.assertFalse(observer.update(1, 1, True, False, .1, .25))
        self.assertTrue(observer.update(2, 1, True, False, .3, .55))
        self.assertEqual(observer.starts, 2)

    def test_backwards_counter_does_not_replay(self):
        observer = RecoilObserver()
        observer.update(9, 0, True, False, 0, 0)
        self.assertFalse(observer.update(0, 0, True, False, 1, 1))

    def test_skipped_commits_fail_closed(self):
        observer = self.fresh()
        self.assertFalse(observer.update(2, 0, True, False, 1, 1.25))
        self.assertTrue(observer.error)

    def test_runtime_helpers_remain_identical(self):
        root = Path(__file__).resolve().parents[3]
        plugins = root / "Unreal/ParisStreetCombat/Plugins"
        a = plugins / "ParisGripBindingV18/Source/ParisGripBindingV18/Public/ParisExistingRecoil.h"
        b = plugins / "ParisNPCGripV15/Source/ParisNPCGripV15/Public/ParisExistingRecoil.h"
        self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
