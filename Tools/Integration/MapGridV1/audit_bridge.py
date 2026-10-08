"""Audit raw role movement/support before stating that a bridge is usable."""
import argparse,json,math,re,sys
from pathlib import Path
from grid_core import digest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import guard_rows,guards_match

def audit(runtime,bank):
    runtime=runtime.resolve();bank=bank.resolve();r=json.loads((runtime/'result.json').read_text());b=json.loads((bank/'cases.json').read_text())
    end=json.loads((runtime/'exit.json').read_text(encoding='utf-8-sig'));log=ROOT/'tmp/bridge-connectivity-v1'/(runtime.name+'.log')
    assert end['exit_code']==end['strict_log_errors']==0
    assert r['protected_bytes_unchanged'] and len(guard_rows())==r['current_guards']==703 and guards_match(guard_rows())
    assert r['map_saved']==r['nav_rebuilt']==r['final_layout_selected']==False and r['original_player_possession_preserved']
    assert r['bank_sha256']==digest(bank/'cases.json') and r['vehicle_max_drift_cm']==0
    assert r['native_bootstrap_gate']=='pass_original_six_bodies_five_brains_selected_bindings_resources'
    for field,plugin in [('helper_sha256','ParisFormalSurveyV1'),('pure_helper_sha256','ParisMapSurveyV1')]:
        assert r[field]==digest(ROOT/f'Unreal/ParisStreetCombat/Plugins/{plugin}/Binaries/Win64/UnrealEditor-{plugin}.dll')
    assert not re.search(r'Error:|Fatal:|Fatal error:|Ensure condition failed|Assertion failed:|Accessed None|BOOTSTRAP_FAILED',log.read_text(errors='replace'))
    route=b['routes'][0];component=route['bridge_component'];x,y,_=route['bridge_origin_cm'];normal=route['bank_normal_xy']
    assert sum((route['source_cm'][j]-route['bridge_origin_cm'][j])*normal[j] for j in [0,1])<-900
    assert sum((route['goal_cm'][j]-route['bridge_origin_cm'][j])*normal[j] for j in [0,1])>900
    checked=[];maxxy=maxz=0
    for c in r['cases']:
        row={'case':c['id'],'status':c['status'],'reason':c.get('reason')}
        if c['status']=='passed':
            assert c['kind']=='solo' and c['actual_bridge_floor_samples']>0
            m=c['members'][0];s=m['standing'];f=m['final'];q=m['request'];e=m['completion']
            assert s['standing_pass'] and not s['blockers'] and s['walkable_floor'] and s['movement_mode']==1
            assert q['started'] and e['result_code']==0 and e['request_id']==q['request_id'] and e['controller']==q['controller']
            assert f['controller']['status_code']==0 and f['walkable_floor'] and f['movement_mode']==1
            assert f['resources']==r['startup_resources'][m['index']]
            xy=math.dist(f['feet_cm'][:2],m['goal_cm'][:2]);z=abs(f['feet_cm'][2]-m['goal_cm'][2]);assert xy<=35 and z<=35
            maxxy=max(maxxy,xy);maxz=max(maxz,z)
            for p in q['path_cm']:assert abs(p[0]-x)<=3500 and abs(p[1]-y)<=3500
            bridge_samples=[]
            for sample in c['samples']:
                for n in sample['members']:
                    assert n['resources']==r['startup_resources'][n['index']]
                    assert n['walkable_floor'] and n['movement_mode']==1 and n['feet_cm'][2]>40
                    assert abs(n['feet_cm'][0]-x)<=3500 and abs(n['feet_cm'][1]-y)<=3500
                    if re.sub(r'UEDPIE_[0-9]+_','',n['floor_component'])==component:bridge_samples.append(n['feet_cm'])
            assert len(bridge_samples)==c['actual_bridge_floor_samples']
            if c['direction']=='back':assert not m['source_placement']
            row.update({'role_index':m['index'],'direction':c['direction'],'bridge_samples':len(bridge_samples),
                        'xy_error_cm':xy,'feet_error_cm':z,'native_path_length_cm':q['path_length_cm']})
        else:assert c['status']=='negative' and c['reason']
        checked.append(row)
    passed=[c for c in checked if c['status']=='passed'];neg=[c for c in checked if c['status']=='negative']
    if neg:assert r['cases'][-1]['status']=='negative' and r['summary']['unmeasured']==6-len(checked)
    else:assert len(checked)==6 and {(c['role_index'],c['direction']) for c in passed}=={(i,d) for i in [0,1,3] for d in ['out','back']}
    two_way_roles=[i for i in [0,1,3] if {(c['direction']) for c in passed if c['role_index']==i}=={'out','back'}]
    captures=[]
    for cap in r['captures']:
        p=runtime/cap['file'];assert p.is_file();captures.append({'file':p.name,'sha256':digest(p)})
    result={'status':'audited_bridge_roles_with_negatives' if neg else 'pass_three_original_roles_two_way_bridge',
        'bridge_id':route['bridge_id'],'summary':r['summary'],'confirmed_two_way_roles':two_way_roles,'cases':checked,
        'max_passed_xy_cm':maxxy,'max_passed_feet_cm':maxz,'exit':end,'captures':captures,'protected_rows':703,
        'sources':{p.relative_to(ROOT).as_posix():digest(p) for p in [runtime/'result.json',runtime/'ue_bridge_verify.py',runtime/'exit.json',bank/'cases.json',bank/'discovery.json',bank/'adaptation.json',log]},
        'not_whole_map_or_other_bridges_admission':True,'formal_map_unchanged':True}
    target=runtime/'audit_v1.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runtime',type=Path);p.add_argument('bank',type=Path);a=p.parse_args();audit(a.runtime,a.bank)
