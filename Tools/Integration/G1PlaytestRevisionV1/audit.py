"""Read completed UX integration evidence; no engine/source writes."""
import argparse,json,re,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source

def main():
    p=argparse.ArgumentParser();p.add_argument('identity');p.add_argument('--retain-negative',action='store_true');a=p.parse_args()
    out=ROOT/'tmp/g1-playtest-revision-20261008'/a.identity
    target=out/'read_only_audit.json';assert not target.exists()
    launch=json.loads((out/'launch.json').read_text(encoding='utf-8-sig'))
    log=(out/'game.log').read_text(errors='replace')
    issues=re.findall(r'^.*(?:Error:|Fatal error:|Assertion failed:|Ensure condition failed:|EXCEPTION_ACCESS_VIOLATION).*$',log,re.M|re.I)
    assert launch['exit_code']==0 and not launch.get('deadline_terminated') and not issues,issues[:10]
    assert '-DisablePython' in launch['arguments'] and 'ParisEditorBridge' not in log
    actions=re.findall(r'PARIS_UX_ACTION_PLAYER old=(\S+) new=(\S+) original_gun=(\S+) mesh_material_resources_exact=1',log)
    assert actions and all('BP_PCParisPlayerV1_C' in r[0] and 'BP_PCParisPlayerActionsV6_C' in r[1] for r in actions)
    assert 'PARIS_UX_HUD_READY minimap=1024x1024' in log
    assert 'Paris approved first-person native binding ready; original gameplay retained' in log
    assert 'PARIS_G1_PHASE Ready' in log
    native=re.findall(r'PARIS_G1_NATIVE_BRIDGE_CONSTRAINT node=(\d+) vertices=(\d+) area_before=(\d+) area_after=(\d+)',log)
    assert native and all(r==('2441688907787','5','63','0') for r in native)
    assert 'PARIS_G1_AGENT_PLAN_BIND replacements=1' in log
    assert verify_source()['source_files']==758
    rows=guard_rows();assert len(rows)==703 and guards_match(rows)
    receipt=dict(status='pass_integrity_numeric_visual_review_separate',identity=a.identity,
        strict_issues=issues,normal_exit=True,source_contract_files=758,protected_files=703,
        ordinary_first_person_initialized=True,native_worlds=len(native),action_integrations=len(actions),
        files=[dict(path=f.name,size_bytes=f.stat().st_size,sha256=digest(f)) for f in [out/'launch.json',out/'game.log']],
        images=[])
    for f in sorted(out.glob('*.png')):
        dimensions=(launch.get('width',1920),launch.get('height',1080))
        assert Image.open(f).size==dimensions
        receipt['images'].append(dict(path=f.name,sha256=digest(f),dimensions=list(dimensions)))
    assert receipt['images'],'Actual SHOWUI screenshot required'
    if (out/'result.json').exists():
        r=json.loads((out/'result.json').read_text())
        assert r['status'].startswith('failed_' if a.retain_negative else 'pass_'),r['status']
        receipt['numeric_status']=r['status'];receipt['result_sha256']=digest(out/'result.json')
        if a.retain_negative:
            receipt['status']='stopped_negative_retained_integrity_only'
        elif r['mode']=='actions':
            assert r['stationary_min_player_ally_cm']>=250 and r['stationary_max_ally_travel_cm']<80
            assert len({s['posture'] for s in r['samples']})==3
        else:
            assert 'PARIS_UX_CHECKPOINT_CONFIRMED serial=1' in log
            assert 'PARIS_UX_CHECKPOINT_DECLINED serial=0' in log
            assert len(actions)==len(native)==3
    else:
        assert 'PARIS_UX_TEST' not in log
        receipt['numeric_status']='ordinary_ready_only_no_action_or_checkpoint_claim'
    target.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['files','images']},indent=2))
if __name__=='__main__':main()
