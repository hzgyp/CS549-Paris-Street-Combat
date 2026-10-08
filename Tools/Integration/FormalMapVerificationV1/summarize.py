"""Aggregate frozen private evidence; never upgrade a negative or choose layout."""
import hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
BASE=STORE/'Evidence/FormalMapVerificationV1';OUT=BASE/'final_summary_v1_20261007'
assert not OUT.exists() and len(guard_rows())==703 and guards_match(guard_rows())
identities=['early_v1_20261007','solo_v1_20261007','squad_v1_20261007',
 'encounter_flat_v1_20261007','encounter_turning_v1_20261007','encounter_height_v1_20261007','encounter_height_latch_v2_20261007']
reports={};inputs=[]
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)}
for identity in identities:
    base=BASE/identity;r=json.loads((base/'result.json').read_text());a=json.loads((base/'audit_v1.json').read_text())
    assert a['status']=='pass_independent_formal_receipt_audit' and a['inputs']['result.json']==digest(base/'result.json')
    assert r['protected_bytes_unchanged'] and r['summary']['unmeasured']==0
    assert r['nav_rebuilt']==r['map_saved']==r['final_layout_selected']==False
    reports[identity]=r
    files=[base/'result.json',base/'audit_v1.json',base/'ue_verify.py',base/'guards_before.json',base/'entry.json',base/'exit.json']
    if r['stage']=='Encounter':
        ia=json.loads((base/'interaction_audit_v1.json').read_text());assert ia['status']=='pass_independent_interaction_audit'
        files.append(base/'interaction_audit_v1.json')
    inputs.extend(row(p) for p in files)
solo=reports['solo_v1_20261007'];squad=reports['squad_v1_20261007'];groups={}
for kind in ('allied_follow','german_traffic','opposing'):
    cases=[c for c in squad['cases'] if c['kind']==kind]
    groups[kind]={'recorded':len(cases),'passed':sum(c['status']=='passed' for c in cases),
        'negative':[{'id':c['id'],'reason':c['reason'],'member_errors_cm':[m.get('body_goal_error_cm') for m in c['members']]} for c in cases if c['status']=='negative']}
encounters=[]
for identity in ('encounter_flat_v1_20261007','encounter_turning_v1_20261007','encounter_height_latch_v2_20261007'):
    r=reports[identity];c=r['cases'][0];ia=json.loads((BASE/identity/'interaction_audit_v1.json').read_text())
    final=c['samples'][-1]['members'];initial=c['samples'][0]['members'];raw_shots=[sum(row['resources'][3] for row in final if row['team']==t) for t in (0,1)]
    encounters.append({'identity':identity,'category':c['category'],'status':c['status'],
        'window_game_seconds':c['ended_game_seconds']-c['started_game_seconds'],
        'seen_factions':ia['seen_factions'],'opponent_shot_factions':ia['new_opponent_shot_factions'],
        'confirmed_shot_intervals':ia['opponent_shot_intervals'],'raw_shots_allied_german':raw_shots,
        'casualties_allied_german':[sum(row['resources'][4] for row in final if row['team']==t) for t in (0,1)],
        'dead_stop_checks':ia['dead_stop_checks'],'hostile_health_loss':c['enemy_health_loss'],
        'initial_native_los_true':sum(x['los'] for x in c['initial_los']),'initial_native_los_total':len(c['initial_los']),
        'initial_standing_max_xy_cm':max(m['initial_standing']['xy_error_cm'] for m in c['members']),
        'initial_standing_max_feet_cm':max(m['initial_standing']['feet_error_cm'] for m in c['members']),
        'max_individual_travel_cm':max(math.dist(row['position_cm'],next(x for x in initial if x['index']==row['index'])['position_cm']) for row in final)})
feet_errors=[m['feet_error_cm'] for c in solo['cases'] for m in c['members']]
xy_errors=[m['xy_error_cm'] for c in solo['cases'] for m in c['members']]
falling=sum(row['movement_mode']==3 for c in solo['cases'] for sample in c['samples'] for row in sample['members'])
result={'status':'completed_bounded_formal_verification_with_negatives','temporary_coordinates_only':True,
 'main_cases':53,'main_passed':solo['summary']['passed']+squad['summary']['passed']+sum(e['status']=='passed' for e in encounters),
 'main_negative':squad['summary']['negative']+sum(e['status']=='negative' for e in encounters),
 'early_controls':6,'solo':solo['summary'],'solo_max_xy_cm':max(xy_errors),'solo_max_feet_cm':max(feet_errors),
 'solo_falling_samples':falling,'groups':groups,'encounters':encounters,
 'height_v1_admission_failure_separate_not_combat':reports['encounter_height_v1_20261007']['cases'][0]['reason'],
 'protected_rows':703,'vehicle_max_drift_cm':max(r.get('vehicle_max_drift_cm',0) for r in reports.values()),
 'formal_profiles':solo['formal_profiles'],'map_sha256':digest(ROOT/'Unreal/ParisStreetCombat/Content/ParisCombat/Maps/LV_ParisStreetCombat_V1.umap'),
 'helper_sha256':solo['helper_sha256'],'pure_helper_sha256':solo['pure_helper_sha256'],
 'not_full_map_mutual_connectivity_or_german_follow_formation_or_visual_fps_mvp_acceptance':True,
 'inputs':inputs}
assert result['main_passed']+result['main_negative']==53
OUT.mkdir();(OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
failure=ROOT/'Failures/ML011-20261007-formal-encounter/MANIFEST.json';assert not failure.exists()
files=[BASE/identity/name for identity in identities if identity.startswith('encounter_') for name in ('result.json','audit_v1.json','interaction_audit_v1.json','ue_verify.py','exit.json')]
files.extend(p for identity in identities if identity.startswith('encounter_') for p in (BASE/identity).glob('*.png'))
failure.write_text(json.dumps({'failed_flat_not_rerun':True,'height_v1_kept_and_distinct_latch_v2':True,'inputs':[row(p) for p in files]},indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('main_cases','main_passed','main_negative','solo_max_xy_cm','solo_max_feet_cm','solo_falling_samples','groups','encounters')},indent=2))
