"""Independently derive interaction gates, including negatives and casualties."""
import json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest
identity=sys.argv[1];base=STORE/'Evidence/FormalMapVerificationV1'/identity
r=json.loads((base/'result.json').read_text());basic=json.loads((base/'audit_v1.json').read_text())
assert basic['status']=='pass_independent_formal_receipt_audit' and r['stage']=='Encounter'
assert basic['inputs']['result.json']==digest(base/'result.json') and not r['errors']
assert r['global_policies']['unique_coordinator'] and r['global_policies']['friendly_fire_off']
c=r['cases'][0];samples=c['samples'];standing=[m['initial_standing'] for m in c['members']]
for s in standing:
    derived=s['xy_error_cm']<=35 and s['feet_error_cm']<=35 and not s['blockers'] and s['movement_mode']==1 and s['walkable_floor']
    assert s['standing_pass']==derived
if not all(s['standing_pass'] for s in standing):
    assert c['reason']=='encounter_initial_standing_rejected' and not samples and not c['shot_events']
    derived_status='not_admitted_no_combat_or_visibility_measurement';seen=set();shot_teams=set();dead={};events=[]
else:
    assert samples and c['ended_game_seconds']-c['started_game_seconds']>=30
    seen=set();shot_teams=set();dead={};events=[];previous={};last_time=-1
    for sample in samples:
        now=sample['game_seconds'];assert now>last_time;last_time=now
        current={row['index']:row for row in sample['members']};assert set(current)=={1,2,3,4,5}
        for i,row in current.items():
            team=0 if i<3 else 1;assert row['team']==team
            hp,loaded,reserve,shots,isdead=row['resources'];assert loaded+reserve+shots==18 and hp>=0
            assert row['outcome']!='Friendly hit'
            valid=bool(row['target'] and ('BP_PCGermanFormalCombatV1_C_' if team==0 else 'BP_PCAlliedFormalCombatV1_C_') in row['target'])
            assert row['opponent_is_active_npc']==valid
            if row['visible'] and valid and row['los_to_target']:seen.add(team)
            before=previous[i]['resources'] if i in previous else c['initial_resources'][i]
            delta=shots-before[3];assert delta>=0 and hp<=before[0]
            if delta>0 and valid and row['los_to_target']:
                shot_teams.add(team);events.append((now,i,team,delta))
            if isdead:
                if i not in dead:dead[i]={'seconds':now,'position':row['position_cm'],'shots':shots,'generation':row['generation'],'checks':0}
                d=dead[i]
                if now-d['seconds']>=.75:
                    assert row['speed_cm_s']<=1 and math.dist(row['position_cm'],d['position'])<=1
                    assert shots==d['shots'] and row['generation']==d['generation'] and row['reservation']==0
                    d['checks']+=1
            else:assert i not in dead,'Casualty restored'
        previous=current
    serialized=[(e['game_seconds'],e['shooter'],e['team'],e['delta']) for e in c['shot_events']]
    assert serialized==events and set(c['seen_factions'])==seen and set(c['real_opponent_shot_factions'])==shot_teams
    damage=False
    for e in c['shot_events']:
        assert (e['shooter']<3)!=(e['target']<3) and e['native_los'] and e['new_shot_and_same_interval_only']
        match=next(s for s in samples if s['game_seconds']==e['game_seconds'])
        target=next(row for row in match['members'] if row['index']==e['target'])
        assert target['resources'][0]==e['target_health_after']
        damage=damage or (e['outcome']=='Hostile hit' and e['target_health_after']<e['target_health_before'])
    assert c['enemy_health_loss']==damage
    passed=seen==shot_teams=={0,1} and damage
    assert c['status']==('passed' if passed else 'negative')
    derived_status='two_sided_native_interaction_pass' if passed else 'admitted_interaction_negative'
if r.get('pre_admission_latch_enabled'):
    latches=r['bootstrap_latches'];assert len(latches)==5 and len({x['label'] for x in latches})==5
    assert all(all(x['enabled_flags'].values()) and x['resources']==[100,2,16,0,False] for x in latches)
out={'identity':identity,'status':'pass_independent_interaction_audit','classification':derived_status,
 'seen_factions':sorted(seen),'new_opponent_shot_factions':sorted(shot_teams),'opponent_shot_intervals':len(events),
 'dead_count':len(dead),'dead_stop_checks':sum(x['checks'] for x in dead.values()),
 'sample_interval_health_association_not_per_bullet_hit_log':True,
 'inputs':{p.name:digest(p) for p in (base/'result.json',base/'audit_v1.json',Path(__file__).resolve())}}
target=base/'interaction_audit_v1.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
