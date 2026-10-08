"""Independently audit finite original-role outcomes; preserve first negative."""
import argparse,json,math,re,sys
from pathlib import Path
from grid_core import digest,world_cell

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import guard_rows,guards_match

def audit(entry,runtime):
    entry=entry.resolve();runtime=runtime.resolve()
    r=json.loads((runtime/'result.json').read_text());end=json.loads((runtime/'exit.json').read_text(encoding='utf-8-sig'))
    bank=entry/'roundtrip_bank/cases.json';log=ROOT/'tmp/map-grid-v1'/(runtime.name+'.log')
    assert end['exit_code']==end['strict_log_errors']==0
    assert r['protected_bytes_unchanged'] and r['current_guards']==703 and len(guard_rows())==703 and guards_match(guard_rows())
    assert r['nav_rebuilt']==r['map_saved']==r['final_layout_selected']==False and r['original_player_possession_preserved']
    assert r['vehicle_max_drift_cm']==0 and r['bank_sha256']==digest(bank)
    assert r['native_bootstrap_gate']=='pass_original_six_bodies_five_brains_selected_bindings_resources'
    for key,plugin in [('helper_sha256','ParisFormalSurveyV1'),('pure_helper_sha256','ParisMapSurveyV1')]:
        assert r[key]==digest(ROOT/f'Unreal/ParisStreetCombat/Plugins/{plugin}/Binaries/Win64/UnrealEditor-{plugin}.dll')
    assert not re.search(r'Error:|Fatal:|Fatal error:|Ensure condition failed|Assertion failed:|Accessed None|BOOTSTRAP_FAILED',log.read_text(encoding='utf-8',errors='replace'))
    passed=[];negative=[];max_xy=max_z=0
    for c in r['cases']:
        if c['status']=='negative':
            assert c['reason']=='source_standing_rejected' and c['members'][0]['standing']['blockers']
            assert not c['members'][0]['standing']['standing_pass'] and not c['samples']
            negative.append(c);continue
        assert c['status']=='passed'
        for m in c['members']:
            s=m['standing'];f=m['final'];q=m['request'];e=m['completion']
            assert s['standing_pass'] and not s['blockers'] and s['movement_mode']==1 and s['walkable_floor']
            assert f['walkable_floor'] and f['movement_mode']==1 and f['resources']==r['startup_resources'][m['index']]
            assert q['started'] and e['result_code']==0 and e['request_id']==q['request_id'] and e['controller']==q['controller']
            assert f['controller']['status_code']==0
            xy=math.dist(f['feet_cm'][:2],m['goal_cm'][:2]);z=abs(f['feet_cm'][2]-m['goal_cm'][2])
            assert xy<=35 and z<=35;max_xy=max(max_xy,xy);max_z=max(max_z,z)
            if c['direction']=='back':assert not m['source_placement']
        passed.append(c['id'])
    assert len(passed)==7 and len(negative)==1 and r['cases'][-1] is negative[0]
    assert r['summary']=={'planned':18,'recorded':8,'passed':7,'negative':1,'unmeasured':10}
    spec=json.loads((entry/'grid_spec.json').read_text());c=negative[0];m=c['members'][0]
    col,row=world_cell(spec,*m['source_cm'][:2]);assert (col,row)==world_cell(spec,*m['standing']['feet_cm'][:2])
    result={'status':'audited_finite_negative_no_retry','summary':r['summary'],'passed_cases':passed,'max_passed_xy_cm':max_xy,'max_passed_feet_cm':max_z,
            'quarantined_cells':[{'c':col,'r':row,'all_scopes_and_surfaces':True,'reason':'runtime_return_standing_capsule_overlap',
            'case':c['id'],'requested_feet_cm':m['source_cm'],'observed_feet_cm':m['standing']['feet_cm'],'blockers':m['standing']['blockers']}],
            'exit':end,'protected_rows':703,'raw_sources':{str(p.relative_to(ROOT)):digest(p) for p in [runtime/'result.json',runtime/'ue_grid_roundtrip.py',runtime/'exit.json',bank,log]},
            'captures_present':[],'not_whole_map_runtime_acceptance':True}
    for capture in r['captures']:
        p=runtime/capture['file'];assert p.is_file();result['captures_present'].append({'file':str(p.relative_to(ROOT)),'sha256':digest(p)})
    target=entry/'runtime_admission.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','summary','max_passed_xy_cm','max_passed_feet_cm','quarantined_cells']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);p.add_argument('runtime',type=Path);a=p.parse_args();audit(a.entry,a.runtime)
