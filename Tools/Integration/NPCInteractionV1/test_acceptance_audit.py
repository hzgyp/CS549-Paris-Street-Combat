"""Synthetic validator tests, never native acceptance evidence or asset writes."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from audit_acceptance import audit


class AcceptanceReceiptTest(unittest.TestCase):
    def setUp(self):
        self.receipt={"identity":"synthetic","scenario":"travel","status":"pass_synthetic",
                      "errors":[],"protected_count":703,"protected_guards_unchanged":True,
                      "checks":{"actual_cutoff_and_physical_regroup_ally0":True,
                                "actual_cutoff_and_physical_regroup_ally1":True},
                      "samples":[{"roster":[{"loaded":2,"reserve":16,"shots":0,
                                              "squad_mode":"Chase","chase":True,
                                              "travel":900,"player_distance":700}]}],
                      "map_saved":False,"python_ai_decision_or_pose_driver":False,
                      "summary":{"cutoffs":{"0":{"npc":0,"episode":1,"travel":900,"player_distance":700,"position":[0,0,0],"goal":[100,0,0]},
                                             "1":{"npc":1,"episode":1,"travel":900,"player_distance":700,"position":[0,0,0],"goal":[100,0,0]}}},
                      "stimuli":[{"name":"park_finite_hostiles_after_individual_cutoff","game_time":10,"ally":0},
                                 {"name":"park_finite_hostiles_after_individual_cutoff","game_time":20,"ally":1}]}
        body=copy.deepcopy(self.receipt["samples"][0]["roster"][0])
        body.update(position=[0,0,0],goal=[100,0,0],squad_mode="Regroup")
        for when in (11,21):
            self.receipt["samples"].append({"phase":"regroup","game_time":when,"roster":[copy.deepcopy(body),copy.deepcopy(body)]})
        self.log={"identity":"synthetic","matched_error_count":0,"exit_code":0}
        self.exited={"identity":"synthetic","exit_code":0}

    def run_audit(self):
        records={"acceptance.json":self.receipt,"log_validation.json":self.log,
                 "synthetic.log.exit.json":self.exited}
        def text(path,*args,**kwargs):
            return json.dumps(records[path.name])
        with patch.object(Path,"read_text",text),patch.object(Path,"read_bytes",return_value=b"synthetic"):
            return audit("synthetic")

    def test_scoped_consistent_receipt(self):
        self.assertEqual(self.run_audit()["observed_maxima"]["travel_cm"],900)

    def test_functional_pass_with_ensure_is_rejected(self):
        self.log["matched_error_count"]=35
        with self.assertRaises(AssertionError):
            self.run_audit()

    def test_bad_exit_is_rejected(self):
        self.exited["exit_code"]=-1
        with self.assertRaises(AssertionError):
            self.run_audit()

    def test_overshoot_is_rejected(self):
        self.receipt=copy.deepcopy(self.receipt)
        self.receipt["samples"][0]["roster"][0]["travel"]=1001
        with self.assertRaises(AssertionError):
            self.run_audit()

    def test_budget_reset_before_body_arrival_is_rejected(self):
        self.receipt["samples"][1]["roster"][0]["travel"]=0
        self.receipt["samples"][1]["roster"][0]["chase"]=False
        with self.assertRaises(AssertionError):
            self.run_audit()

    def test_missing_individual_regroup_samples_is_rejected(self):
        self.receipt["samples"]=self.receipt["samples"][:1]
        with self.assertRaises(AssertionError):
            self.run_audit()


if __name__=="__main__":
    unittest.main()
