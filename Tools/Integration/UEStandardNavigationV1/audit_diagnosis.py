"""Audit query-only observations and characterize search-limit versus connectivity evidence."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
P=STORE/'Evidence/UEStandardNavigationV1'

def audit(entry):
    r=json.loads((entry/'result.json').read_text());ex=json.loads((entry/'exit.json').read_text(encoding='utf-8-sig'))
    b=json.loads((P/'bank_v1_20261007/bank.json').read_text());q=json.loads((P/'diagnostic_bank_v1_20261007.json').read_text())
    assert ex['exit_code']==0 and ex['strict_log_errors']==0 and not r['errors'] and r['protected_bytes_unchanged'] and r['helpers_unchanged']
    dll=ROOT/'Unreal/ParisStreetCombat/Plugins/ParisNavDiagnosticsV1/Binaries/Win64/UnrealEditor-ParisNavDiagnosticsV1.dll'
    assert r['diagnostic_helper_unchanged'] and r['diagnostic_helper_sha256']==digest(dll)
    assert guard_rows()==b['protected_rows'] and guards_match(b['protected_rows'])
    assert r['queries_only'] and r['query_diagnosis_plan_sha256']==q['plan_sha256'] and r['bank_sha256']==q['parent_bank_sha256']
    assert len(r['cases'])==12 and {s['id'] for s in r['cases']}==set(q['case_ids'])
    observations=[]
    for s in r['cases']:
        assert s['status']=='query_observed' and s['reason']=='no_movement_submitted' and s['sample_count']==0
        h=s['source_standing'];assert h['standing_pass'] and h['walkable_floor'] and h['movement_mode']==1 and not h['terrain_blockers'] and h['xy_error_cm']<=35 and h['feet_error_cm']<=35
        aa=s['diagnostic_queries'];assert len(aa)==2
        for i,a in enumerate(aa):
            assert not a.get('error') and a['movement_submitted'] is False and a['budget_override']==q['budgets'][i]
            assert a['effective_max_search_nodes']==(65536 if i else a['original_max_search_nodes'])
            assert a['goal_projected'] and a['source_cm']==h['feet_cm']
        complete=lambda x:x['success'] and x['path_valid'] and not x['partial']
        if s['origin_index']==0:assert all(complete(a) for a in aa)
        observations.append({'id':s['id'],'scope':r['navigation_scope'],'original_budget':aa[0]['original_max_search_nodes'],
            'original_complete':complete(aa[0]),'original_partial':aa[0].get('partial'),
            'original_search_reached_limit':aa[0].get('search_reached_limit'),
            'higher_budget_complete':complete(aa[1]),'higher_budget_search_reached_limit':aa[1].get('search_reached_limit'),
            'higher_budget_length_cm':aa[1].get('length_cm'),
            'search_budget_contribution_observed':bool(aa[0].get('search_reached_limit') and not complete(aa[0]) and complete(aa[1]))})
    out={'status':'pass_independent_query_diagnosis_audit','observations':observations,'native_queries':24,'physical_moves':0,
        'receipt_sha256':digest(entry/'result.json'),'observer_sha256':digest(entry/'ue_diagnosis.py'),'exit_sha256':digest(entry/'exit.json'),'703_exact':True}
    file=entry/'audit.json';assert not file.exists();file.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(out))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);audit(p.parse_args().entry)
