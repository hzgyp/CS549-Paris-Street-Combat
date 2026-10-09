"""Read-only, bounded audit of completed native closeout receipts and strict logs."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('identity');p.add_argument('--native-candidate',action='store_true');p.add_argument('--agent-feet',action='store_true');a=p.parse_args()
    assert not a.agent_feet or a.native_candidate
    out=ROOT/'tmp/mvp-closeout-20261008'/a.identity;target=out/'read_only_audit.json'
    assert not target.exists(), 'Preserve audit identity'
    launch=json.loads((out/'launch.json').read_text());log=(out/'game.log').read_text(errors='replace')
    issues=re.findall(r'^.*(?:Error:|Fatal error:|Assertion failed:|Ensure condition failed:|EXCEPTION_ACCESS_VIOLATION).*$',log,re.M|re.I)
    assert launch['exit_code']==0 and not issues, issues[:10]
    assert '-DisablePython' in launch['arguments'] and 'ParisEditorBridge' not in log
    native=re.findall(r'PARIS_G1_NATIVE_BRIDGE_CONSTRAINT node=(\d+) vertices=(\d+) area_before=(\d+) area_after=(\d+) hit_cm=([\d.]+) projection_cm=([\d.]+)',log)
    if a.native_candidate:
        assert native and all(x[:4]==('2441688907787','5','63','0') for x in native)
        assert all(float(x[4])<.11 and float(x[5])<6.8 for x in native)
    plan=re.findall(r'PARIS_G1_AGENT_PLAN_BIND replacements=(\d+) nodes=(\d+) services=(\d+) other_classes_exact=(\d+) blackboard_exact=(\d+)',log)
    if a.agent_feet:
        assert len(plan)==len(native) and plan and len(set(plan))==1
        assert all(x[0]=='1' and x[3:]==('1','1') and int(x[1])>1 for x in plan)
    record=dict(identity=a.identity,normal_exit=True,strict_issues=issues,python_disabled_argument=True,
        editor_bridge_absent=True,native_constraint_observations=len(native),agent_plan_observations=len(plan),
        hashes={name:sha(out/name) for name in ['launch.json','game.log']})
    if (out/'result.json').exists():
        r=json.loads((out/'result.json').read_text());record['status']=r['status'];record['hashes']['result.json']=sha(out/'result.json')
        rounds=int(r.get('requested_rounds',3));assert rounds in (1,3)
        assert r['status']==('pass_three_scripted_integrated_rounds_human_gate_pending' if rounds==3 else 'pass_one_scripted_integrated_round_human_gate_pending'),r['status']
        counts={name:sum(e.get('event')==name for e in r['events']) for name in [
            'both_allies_original_55cm_25sec_far_bank_gate_pass','native_won',
            'won_checkpoint_saved_original_resources','fresh_world_won_resource_restore_verified',
            'original_fresh_roster_resources_verified']}
        assert list(counts.values())==[rounds,rounds,rounds,rounds,rounds-1],counts
        assert len(r['rounds'])==rounds
        assert all(s['viewport_width']==1920 and s['viewport_height']==1080 for s in r['samples'])
        assert all(len(s['actors'])==6 and s['phase']=='Won' for s in r['rounds'])
        if a.native_candidate:
            assert len(native)==rounds*2, 'Each initial/load/restart world must validate independently'
            assert not any(e.get('event')=='single_collision_witness_polygon_exclusion' for e in r['events']), 'Observer must not apply policy'
            suffix='_BridgeConstraintV2FeetPlan' if a.agent_feet else '_BridgeConstraintV1Nearbank'
            assert all(s['config'].endswith(suffix) for s in r['rounds'])
            paths=[s['bridge_centreline'] for s in r['samples'] if len(s.get('bridge_centreline',[]))>1]
            assert paths and all(abs(v[0][0]-1912.5)<.01 and abs(v[0][1]+20662.5)<.01 for v in paths)
        old_config=[e for e in r['events'] if e.get('event')=='newer_old_config_correct_checksum_rejected_good_fallback_live_state_exact']
        if '-ParisVerifyOldCheckpoint' in launch['arguments']:
            assert len(old_config)==rounds
            for e in old_config:
                path=Path(e['retained_file']);assert path.is_file();record['hashes'][path.name]=sha(path)
        record.update(counts=counts,rounds=rounds,old_configuration_rejections=len(old_config),actual_viewport=[1920,1080],
            scope=f'Scripted original player/squad/capture/save/load and {rounds-1} full restarts; not human/natural encounter/MVP/performance acceptance')
    else:
        assert 'CLOSEOUT_MODULE_ACTIVATED' not in log and 'PARIS_G1_PHASE Ready' in log
        from PIL import Image
        assert Image.open(out/'ready.png').size==(1920,1080)
        record.update(status='pass_observer_disabled_native_ready_only',actual_viewport=[1920,1080])
    target.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

if __name__=='__main__':main()
