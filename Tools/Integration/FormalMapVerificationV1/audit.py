"""Audit original receipts, not outcome labels; keep negatives as negatives."""
import json,math,re,sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
identity=sys.argv[1];base=STORE/'Evidence/FormalMapVerificationV1'/identity
report=json.loads((base/'result.json').read_text())
exit=json.loads((base/'exit.json').read_text(encoding='utf-8-sig'))
assert not report['errors'] and report['protected_bytes_unchanged']
assert exit['exit_code']==exit['strict_log_errors']==0
assert report['status']=='complete_bounded_formal_verification_with_negatives_retained'
assert report['current_guards']==703 and len(guard_rows())==703 and guards_match(guard_rows())
assert report['nav_rebuilt']==report['map_saved']==report['final_layout_selected']==False
assert report['original_player_possession_preserved']
assert report['native_bootstrap_gate']=='pass_original_six_bodies_five_brains_selected_bindings_resources'
assert report['vehicle_max_drift_cm']==0
assert report['bank_sha256']==digest(STORE/'Evidence/FormalMapVerificationV1/case_bank_v3_20261007/cases.json')
assert report['helper_sha256']==digest(ROOT/'Unreal/ParisStreetCombat/Plugins/ParisFormalSurveyV1/Binaries/Win64/UnrealEditor-ParisFormalSurveyV1.dll')
assert report['pure_helper_sha256']==digest(ROOT/'Unreal/ParisStreetCombat/Plugins/ParisMapSurveyV1/Binaries/Win64/UnrealEditor-ParisMapSurveyV1.dll')
assert len(report['formal_profiles'])==6 and len(report['equipment'])==5
cases=report['cases'];assert len({c['id'] for c in cases})==len(cases)
expected={'Early':6,'Solo':36,'Squad':14,'Encounter':1}[report['stage']]
assert report['planned_cases']==len(cases)==expected and report['summary']['unmeasured']==0
for c in cases:
    assert c['status'] in ('passed','negative')
    if c['status']=='negative':assert c['reason'];continue
    if c['kind']=='encounter':
        assert report['global_policies']['unique_coordinator'] and report['global_policies']['friendly_fire_off']
        assert set(c['seen_factions'])==set(c['real_opponent_shot_factions'])=={0,1} and c['enemy_health_loss']
        assert set(e['team'] for e in c['shot_events'] if e['delta']>0 and e['native_los'])=={0,1}
        assert any(e['outcome']=='Hostile hit' and e['target_health_after']<e['target_health_before'] for e in c['shot_events'])
        for e in c['shot_events']:
            assert e['new_shot_and_same_interval_only'] and e['shooter'] in range(1,6) and e['target'] in range(1,6)
            assert (e['shooter']<3)!=(e['target']<3)
        assert all(m['initial_standing']['standing_pass'] for m in c['members'])
        assert c['ended_game_seconds']-c['started_game_seconds']>=30
        for sample in c['samples']:
            for row in sample['members']:
                health,loaded,reserve,shots,dead=row['resources'];assert loaded+reserve+shots==18
                assert row['outcome']!='Friendly hit'
        for dead in c['dead_observations'].values():
            assert dead['settled_checks']==0 or dead['last_stop_pass']
        continue
    for m in c['members']:
        assert m['standing']['standing_pass']
        assert not m['standing']['blockers'] and m['standing']['movement_mode']==1 and m['standing']['walkable_floor']
        final=m['final'];assert final['walkable_floor'] and final['movement_mode']==1
        assert final['resources']==report['startup_resources'][m['index']]
        if c['kind']=='allied_follow':
            assert 'raw_leader_slot_body_cm' in final
            assert final['reservation']>0 and final['slot'] in (0,1)
            assert math.dist(final['body_cm'],final['held_goal_cm'])<=55
            assert math.dist(m['standing']['body_cm'],final['body_cm'])>=100
        else:
            request=m['request'];event=m['completion'];assert request['started'] and event['result_code']==0
            assert event['request_id']==request['request_id'] and event['controller']==request['controller']
            assert final['controller']['status_code']==0
            assert math.dist(final['feet_cm'][:2],m['goal_cm'][:2])<=35
            assert abs(final['feet_cm'][2]-m['goal_cm'][2])<=35
            assert event['game_seconds']>=c['started_game_seconds']
    if c['kind']=='allied_follow':
        assert len({m['final']['slot'] for m in c['members']})==2
        assert len({m['final']['reservation'] for m in c['members']})==2
log=ROOT/'tmp/formal-map-v1'/(identity+'.log')
assert not re.search(r'Error:|Fatal:|Fatal error:|Ensure condition failed|Assertion failed:|Accessed None|BOOTSTRAP_FAILED',log.read_text(encoding='utf-8',errors='replace'))
result={'identity':identity,'status':'pass_independent_formal_receipt_audit','stage':report['stage'],'recorded':len(cases),
    'passed':sum(c['status']=='passed' for c in cases),'negative':sum(c['status']=='negative' for c in cases),
    'negative_reasons':dict(Counter(c['reason'] for c in cases if c['status']=='negative')),
    'completed_finite_scope_only':True,'not_whole_map_or_final_layout_acceptance':True,'protected_rows':703,'exit':exit,
    'inputs':{p.name:digest(p) for p in [base/'result.json',base/'ue_verify.py',base/'guards_before.json',base/'entry.json',base/'exit.json',log]},
    'captures_present':[x['file'] for x in report['captures'] if (base/x['file']).is_file()]}
target=base/'audit_v1.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('status','stage','recorded','passed','negative','negative_reasons')},indent=2))
