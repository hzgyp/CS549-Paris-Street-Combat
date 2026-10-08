"""Independently derive native request/standing/arrival outcomes from immutable receipts."""
import argparse,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match

def grounded(x):
    return x['xy_error_cm']<=35 and x['feet_error_cm']<=35 and not x['terrain_blockers'] and x['movement_mode']==1 and x['walkable_floor']
def audit(entry):
    bank_path=STORE/'Evidence/NativeConvergenceV1/bank_v1_20261007/bank.json';bank=json.loads(bank_path.read_text())
    report=json.loads((entry/'result.json').read_text());ex=json.loads((entry/'exit.json').read_text(encoding='utf-8-sig'))
    assert not report['errors'] and ex['exit_code']==0 and ex['strict_log_errors']==0
    assert report['protected_bytes_unchanged'] and report['helpers_unchanged']
    assert guard_rows()==bank['protected_rows'] and guards_match(bank['protected_rows'])
    assert report['bank_sha256']==digest(bank_path)
    assert report['navigation_scope']=='saved' and report['source_white_scope']=='full' and not report['nav_rebuilt'] and not report['map_saved']
    assert report['time_dilation']==1 and report['terrain_phase_mutual_test_character_collision_ignored']
    if report['stage']=='Full':
        assert len(report['avoidance_group_isolation'])==6
        for i,x in enumerate(report['avoidance_group_isolation']):
            assert len(x['after'])==32 and not any(x['after']) and x['native_rvo_enabled']==report['profiles'][i]['rvo']
    assert len(report['bootstrap_latches'])==5 and all(all(x['flags'].values()) and x['resources']==[100,2,16,0,False] for x in report['bootstrap_latches'])
    assert all(grounded(x) for x in report['hub_standing'].values())
    frozen={s['id']:s for s in bank['cases']};early=set(bank['early_ids'])
    expected={k for k in frozen if (k in early)==(report['stage']=='Early')}
    seen=set();counts={role:{'passed':0,'negative':0} for role in ('allied','german')};hashes={}
    for s in report['cases']:
        f=frozen[s['id']];assert s['id'] in expected and s['id'] not in seen;seen.add(s['id'])
        for k in ('role','source_cm','source_node_id','c','r','layer','source_component'):assert s[k]==f[k],(s['id'],k)
        assert s['status'] in ('passed','negative');counts[s['role']][s['status']]+=1
        h=s['source_standing'];assert h['standing_pass']==grounded(h)
        if s['status']=='passed':
            assert grounded(h);q=s['request'];assert q['started'] and q['path_length_cm']>0 and q['path_cm'] and not q.get('rejection')
            assert q['goal_cm']==bank['hub']['feet_cm']
            assert s['completion']['controller']==q['controller'] and s['completion']['request_id']==q['request_id'] and s['completion']['result_code']==0
            assert grounded(s['arrival_standing']) and s['ended_game_seconds']-s['arrival_first_game_seconds']>=.6-1e-8
            samples=[json.loads(line) for line in (entry/s['samples_file']).open()]
            assert len(samples)==s['sample_count'] and samples and max(x['speed_cm_s'] for x in samples)>50
            assert samples[-1]['path_status']==0 and samples[-1]['completion']['result_code']==0
            assert math.dist(samples[-1]['feet_cm'][:2],bank['hub']['feet_cm'][:2])<=35
            assert abs(samples[-1]['feet_cm'][2]-bank['hub']['feet_cm'][2])<=35
            assert s['deadline_seconds']==max(12,q['path_length_cm']/report['profiles'][s['actor_index']]['max_speed_cm_s']*2+10)
            assert s['travel_seconds']<=s['deadline_seconds']+.5
            hashes[s['samples_file']]=digest(entry/s['samples_file'])
        else:
            reason=s['reason'];assert reason in ('source_standing_rejected','saved_navigation_complete_path_rejected','native_path_following_failed','endpoint_standing_rejected','distance_scaled_travel_deadline')
            if reason=='source_standing_rejected':assert not grounded(h)
            elif reason=='saved_navigation_complete_path_rejected':assert grounded(h) and (s['request'].get('rejection') or not s['request'].get('started'))
            elif reason=='endpoint_standing_rejected':assert not grounded(s['arrival_standing'])
            elif reason=='native_path_following_failed':assert s['completion']['result_code']!=0
            else:assert s['ended_game_seconds']-s['moving_started_game_seconds']>s['deadline_seconds']
            p=entry/s['samples_file']
            if p.exists():hashes[s['samples_file']]=digest(p)
    assert seen==expected and len(seen)==report['planned_cases'],'Finite bank not completed'
    early_pass=report['stage']=='Early' and all(counts[role]['passed']>=1 for role in counts)
    if report['stage']=='Early':assert early_pass and report['status']=='pass_early_native_convergence'
    out={'status':'pass_independent_convergence_audit','stage':report['stage'],'cases':len(seen),'role_counts':counts,'early_mechanism_pass':early_pass,
         'receipt_sha256':digest(entry/'result.json'),'exit_sha256':digest(entry/'exit.json'),'observer_sha256':digest(entry/'ue_convergence.py'),
         'bank_sha256':digest(bank_path),'protected_rows':703,'guards_exact':True,'sample_sha256':hashes,'negative_cases':[s['id'] for s in report['cases'] if s['status']=='negative'],
         'finite_sample_not_full_white_runtime':True,'crowd_acceptance':False,'final_layout_selected':False}
    target=entry/'audit.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('sample_sha256','negative_cases')}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);audit(p.parse_args().entry)
