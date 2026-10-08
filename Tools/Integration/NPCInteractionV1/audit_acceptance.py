"""Read-only cross-check of bounded receipts, strict logs, exits and protection."""
import argparse
import hashlib
import json
import re
from math import dist
from common import ROOT, STORE, guard_rows, guards_match


def audit(identity):
    folder=STORE/"Evidence/NPCInteractionV1"/identity
    receipt=json.loads((folder/"acceptance.json").read_text())
    log=json.loads((folder/"log_validation.json").read_text())
    exited=json.loads((ROOT/"tmp/npc-interaction-v1"/(identity+".log.exit.json")).read_text())
    assert receipt["identity"]==log["identity"]==exited["identity"]==identity
    assert receipt["status"].startswith("pass_") and not receipt["errors"]
    assert receipt["protected_count"]==703 and receipt["protected_guards_unchanged"]
    assert log["matched_error_count"]==0 and exited["exit_code"]==log["exit_code"]==0
    assert receipt["checks"] and all(receipt["checks"].values())
    assert receipt["samples"] and not receipt["map_saved"] and not receipt["python_ai_decision_or_pose_driver"]
    items=[x for s in receipt["samples"] for x in s["roster"]]
    assert all(x["loaded"]+x["reserve"]+x["shots"]==18 for x in items)
    chasing=[x for x in items if x["squad_mode"]=="Chase" and x["chase"]]
    maximum={"travel_cm":max((x["travel"] for x in items),default=0),
             "player_radius_while_chasing_cm":max((x["player_distance"] for x in chasing),default=0)}
    if receipt["scenario"] in ("travel","radius"):
        assert maximum["travel_cm"]<=1000 and maximum["player_radius_while_chasing_cm"]<=1000
        assert all(receipt["checks"].get("actual_cutoff_and_physical_regroup_ally"+str(i)) for i in (0,1))
        parks=[s for s in receipt.get("stimuli",[]) if s["name"]=="park_finite_hostiles_after_individual_cutoff"]
        retained=[0,0]
        for sample in receipt["samples"]:
            if sample.get("phase")!="regroup":
                continue
            prior=[s for s in parks if s["game_time"]<=sample["game_time"]]
            assert prior,"Regroup sample lacks its declared individual cutoff"
            ally=max(prior,key=lambda s:s["game_time"])["ally"]
            body=sample["roster"][ally]
            if dist(body["position"],body["goal"])>55:
                assert body["chase"] and body["travel"]>=receipt["summary"]["cutoffs"][str(ally)]["travel"],"Budget reset before actual regroup arrival"
                retained[ally]+=1
        assert all(retained),"Both original bodies require observed in-progress regroup retention"
        maximum["retained_regroup_samples_by_ally"]=retained
    summary=dict(receipt["summary"])
    if "cutoffs" in summary:
        summary["cutoffs"]={key:{field:row[field] for field in
            ("npc","episode","travel","player_distance","position","goal")}
            for key,row in summary["cutoffs"].items()}
    return {"identity":identity,"scenario":receipt["scenario"],"checks":receipt["checks"],
            "summary":summary,"observed_maxima":maximum,
            "samples":len(receipt["samples"]),"receipt_sha256":hashlib.sha256((folder/"acceptance.json").read_bytes()).hexdigest()}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("identities",nargs="+")
    parser.add_argument("--report-identity",help="Write generated audit inside an existing unique preflight evidence folder")
    args=parser.parse_args()
    rows=guard_rows()
    assert len(rows)==703 and guards_match(rows)
    payload={"current_protected_count":len(rows),"current_protection_exact":True,
             "scope":"Explicit listed clean functional entries only; not full motion/FPS/whole-city/MVP acceptance",
             "entries":[audit(identity) for identity in args.identities]}
    if args.report_identity:
        assert re.fullmatch(r"[A-Za-z0-9_]+",args.report_identity)
        folder=STORE/"Evidence/NPCInteractionV1"/args.report_identity
        target=folder/"acceptance_audit.json"
        assert folder.is_dir() and not target.exists(),"Require unique existing preflight folder; preserve occupied report"
        target.write_text(json.dumps(payload,indent=2)+"\n")
    print(json.dumps(payload,indent=2))


if __name__=="__main__":
    main()
