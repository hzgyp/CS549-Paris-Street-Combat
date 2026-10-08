"""Independently check standard controller admission, actual travel and frozen protections."""
import argparse,collections,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
P=STORE/'Evidence/UEStandardNavigationV1'

def grounded(x):
    return x['xy_error_cm']<=35 and x['feet_error_cm']<=35 and not x['terrain_blockers'] and x['movement_mode']==1 and x['walkable_floor']

def audit(entry):
    bp=P/'bank_v1_20261007/bank.json';b=json.loads(bp.read_text())
    r=json.loads((entry/'result.json').read_text());ex=json.loads((entry/'exit.json').read_text(encoding='utf-8-sig'))
    assert ex['exit_code']==0 and ex['strict_log_errors']==0 and not r['errors'],r['errors']
    assert r['protected_bytes_unchanged'] and r['helpers_unchanged'] and guard_rows()==b['protected_rows'] and guards_match(b['protected_rows'])
    assert r['bank_sha256']==digest(bp) and r['time_dilation']==1 and not r['map_saved'] and r['terrain_phase_mutual_test_character_collision_ignored']
    saved=r['stage']=='SavedProbe';assert r['navigation_scope']==('saved' if saved else 'expanded_unsaved') and r['nav_rebuilt']==(not saved)
    if not saved:
        assert len(r['editor_collision_restore'])==6 and all(x['original']==x['restored'] for x in r['editor_collision_restore'])
        assert r['fixture_addendum_sha256']==digest(ROOT/'Docs/Development/MissionLoopV1/UE_STANDARD_NAV_FIXTURE_ADDENDUM_20261007.md')
        assert all(x['walkable_floor'] and x['movement_mode']==1 for x in r['profiles'])
    for info in [r['editor_navigation'],r['pie_navigation']]:
        assert digest(entry/info['export_file'])==info['export_sha256']
        mesh=json.loads((entry/info['export_file']).read_text());assert len(mesh['polygons'])==info['polygon_count'] and info['active_tiles']==mesh['active_tiles']
        assert not mesh['invalid_records']
    assert all(grounded(x) for x in r['hub_standing'].values())
    assert len(r['bootstrap_latches'])==5 and all(all(x['flags'].values()) and x['resources']==[100,2,16,0,False] for x in r['bootstrap_latches'])
    assert len(r['avoidance_group_isolation'])==6
    for i,x in enumerate(r['avoidance_group_isolation']):assert len(x['after'])==32 and not any(x['after']) and x['native_rvo_enabled']==r['profiles'][i]['rvo']
    frozen={s['id']:s for s in b['cases']};early=set(b['early_ids'])
    expected=set(frozen) if saved else {k for k in frozen if (k in early)==(r['stage']=='Early')}
    seen=set();counts={role:collections.Counter() for role in ('allied','german')};sample_hashes={}
    for s in r['cases']:
        assert s['id'] in expected and s['id'] not in seen;seen.add(s['id']);f=frozen[s['id']]
        for k in ('role','source_cm','source_node_id','source_component','c','r','layer','previous_status','previous_reason'):assert s[k]==f[k]
        assert s['source_standing']['standing_pass']==grounded(s['source_standing'])
        counts[s['role']][s['status']]+=1
        q=s.get('request')
        if q:
            assert q['api']=='AAIController.MoveToLocation' and q['use_pathfinding'] and q['project_destination'] and not q['allow_partial_paths'] and not q['stop_on_overlap'] and q['acceptance_cm']==30
            assert q['goal_cm']==b['hub']['feet_cm'] and q['actual_source_feet_cm']==s['source_standing']['feet_cm']
        if s['status'] in ('passed','request_admitted'):
            assert grounded(s['source_standing']) and q['started'] and q['request_id']>=0 and not q['partial'] and len(q['path_cm'])>=2
            assert abs(q['path_length_cm']-sum(math.dist(a,b) for a,b in zip(q['path_cm'],q['path_cm'][1:])))<1e-7
            assert q['goal_projection_cm'] is not None and math.dist(q['goal_projection_cm'][:2],b['hub']['feet_cm'][:2])<=35
            if saved:
                assert s['status']=='request_admitted' and s['reason']=='intentional_cancel_before_travel' and s['sample_count']==0
            else:
                assert s['status']=='passed' and grounded(s['arrival_standing'])
                ev=s['completion'];assert ev['result_code']==0 and ev['controller']==q['controller'] and ev['request_id']==q['request_id']
                assert s['ended_game_seconds']-s['arrival_first_game_seconds']>=.6-1e-8
                samples=[json.loads(line) for line in (entry/s['samples_file']).open()]
                assert len(samples)==s['sample_count'] and samples[-1]['path_status']==0 and samples[-1]['completion']==ev
                assert max(x['speed_cm_s'] for x in samples)>50
                assert s['deadline_seconds']==max(12,q['path_length_cm']/r['profiles'][s['actor_index']]['max_speed_cm_s']*2+10)
                assert s['travel_seconds']<=s['deadline_seconds']+.5
        else:
            assert s['status']=='negative'
            why=s['reason']
            if why=='source_standing_rejected':assert not grounded(s['source_standing'])
            elif why=='standard_navigation_request_rejected':assert grounded(s['source_standing']) and q and not q['started']
            elif why=='native_path_following_failed':assert s['completion']['result_code']!=0
            elif why=='endpoint_standing_rejected':assert not grounded(s['arrival_standing'])
            elif why=='distance_scaled_travel_deadline':assert s['ended_game_seconds']-s['moving_started_game_seconds']>s['deadline_seconds']
            else:raise AssertionError(why)
        sp=entry/s['samples_file']
        if sp.exists():sample_hashes[sp.name]=digest(sp)
    assert seen==expected and len(seen)==r['planned_cases'] and r['summary']['unmeasured']==0
    early_pass=r['stage']=='Early' and all(counts[role]['passed']>=1 for role in counts)
    if r['stage']=='Early':assert early_pass
    out={'status':'pass_independent_standard_navigation_audit','stage':r['stage'],'cases':len(seen),'role_counts':{k:dict(v) for k,v in counts.items()},
        'early_mechanism_pass':early_pass,'receipt_sha256':digest(entry/'result.json'),'exit_sha256':digest(entry/'exit.json'),
        'observer_sha256':digest(entry/'ue_standard.py'),'bank_sha256':digest(bp),'samples_sha256':sample_hashes,
        'protected_rows':703,'guards_exact':True,'saved_stage_is_request_only':saved,'formal_nav_selected':False}
    target=entry/'audit.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in out.items() if k!='samples_sha256'}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);audit(p.parse_args().entry)
