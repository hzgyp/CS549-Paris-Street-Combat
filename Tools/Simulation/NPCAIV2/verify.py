"""Black-box finite invariants/counterfactuals; independent of replay code."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import statistics
import time
from simulate import run_scenario, SCENARIOS, CFG, Move
from geometry import Geometry
from policy import callback_matches, distance


def verify(out):
    checks = []
    def check(name, condition, evidence):
        checks.append({'name': name, 'pass': bool(condition), 'evidence': evidence})
    runs = {s['id']:run_scenario(s) for s in SCENARIOS}
    for sid, run in runs.items():
        metric = run['metrics']
        check(sid+': hidden transforms excluded', metric['hidden_coordinate_reads']==0, metric['hidden_coordinate_reads'])
        check(sid+': swept geometry admission', metric['penetrations']==0, metric['penetrations'])
        check(sid+': request and query budgets', max(metric['npc_attempts'].values()) <= CFG['attempts_per_run'] and
              metric['max_query_expansions']<=CFG['path_node_budget'] and metric['pair_comparisons_max']<=64,
              {'attempts':metric['npc_attempts'], 'nodes':metric['max_query_expansions'], 'pairs':metric['pair_comparisons_max']})
        check(sid+': fixed search deadline', metric['overdue_search_frames']==0, metric['overdue_search_frames'])
        check(sid+': finite roster', metric['spawned_npcs']==0 and len(run['frames'][-1]['minds'])==metric['initial_npcs'], metric['initial_npcs'])
    r = runs['occlusion_reacquire']
    states = [x['to'] for x in r['metrics']['transitions']['G1']]
    check('occlusion: investigate/search/return/reacquire', all(s in states for s in ('Alert','Engage','Investigate','Search','Return')) and states.count('Engage')==2, states)
    hidden = [f for f in r['frames'] if 4<=f['at']<=9]
    check('occlusion: last seen frozen despite hidden movement', len({tuple(f['minds']['G1']['memory']['position']) for f in hidden if f['minds']['G1']['memory']})==1,
          [f['minds']['G1']['memory']['position'] for f in hidden[:1]])
    spec = copy.deepcopy(next(s for s in SCENARIOS if s['id']=='occlusion_reacquire'))
    spec['events'][0]['position']=[29,20]
    alternate=run_scenario(spec)
    def decisions(run):
        return [{'at':f['at'],'mind':f['minds']['G1'],'move':f['moves']['G1']} for f in run['frames'] if 3.2<=f['at']<14]
    check('occlusion: counterfactual hidden target cannot steer AI', decisions(r)==decisions(alternate), 'two different hidden trajectories, same mind and movement trace')
    r=runs['hearing_only']; senses=[f['minds']['G1']['memory']['sense'] for f in r['frames'] if f['minds']['G1']['memory']]
    check('hearing: no visible lock behind wall', 'sight' not in senses and all(not f['minds']['G1']['live_visible'] for f in r['frames']), sorted(set(senses)))
    deadlines={f['minds']['G1']['search_deadline'] for f in r['frames'] if f['minds']['G1']['search_deadline']>=0}
    check('hearing: repeated noise does not extend search', len(deadlines)==1, sorted(deadlines))
    r=runs['target_invalid']; later=[f for f in r['frames'] if f['at']>=4]
    check('death: memory cleared and corpse remains dead', all(f['minds']['G1']['memory'] is None and not f['actors']['P']['alive'] and f['minds']['G1']['state']!='Engage' for f in later), len(later))
    for sid in ('unreachable','stuck'):
        metric=runs[sid]['metrics']
        check(sid+': real failure resolves to Waiting', metric['final_results']['A1'].startswith('Waiting:') and metric['npc_attempts']['A1']==3,
              {'result':metric['final_results']['A1'],'attempts':metric['npc_attempts']['A1'],'goal_error':metric['actual_goal_errors']['A1']})
        check(sid+': no reservation after exhaustion', 'A1' not in runs[sid]['frames'][-1]['reservations'], list(runs[sid]['frames'][-1]['reservations']))
        exhausted=[f for f in runs[sid]['frames'] if f['moves']['A1']['result'].startswith('Waiting:')]
        check(sid+': exhausted waiting stays stable', bool(exhausted) and all(f['minds']['A1']['state']=='Waiting' for f in exhausted), len(exhausted))
    events=runs['unreachable']['metrics']['move_events']['A1']
    check('unreachable: disconnected free endpoints exhaust finite graph',any(e['result']=='Unreachable' for e in events),[e['result'] for e in events])
    for sid in ('squad_cover','bottleneck'):
        r=runs[sid]; metric=r['metrics']
        check(sid+': separated goals and bodies', metric['same_goal_frames']==0 and metric['min_ally_separation']>=2*CFG['capsule_radius']-1e-6,
              {'shared_goal_frames':metric['same_goal_frames'],'min_separation':metric['min_ally_separation']})
    r=runs['squad_cover']
    after_death=[f for f in r['frames'] if f['at']>=10]
    check('squad: dead threat cannot survive in report knowledge',all(not f['actors']['G1']['alive'] and all(m['knowledge'] is None or m['knowledge']['actor_id']!='G1' for m in f['minds'].values()) for f in after_death),len(after_death))
    check('squad: support and overwatch both chosen', any(f['minds']['A1']['state']=='Support' and f['minds']['A2']['state']=='Overwatch' for f in r['frames']),
          {k:[x['to'] for x in r['metrics']['transitions'][k]] for k in ('A1','A2')})
    retained=[f for f in r['frames'] if f['moves']['A1']['result']=='Arrived' and f['minds']['A1']['state']=='Support']
    check('squad: occupied arrival keeps reservation', bool(retained) and all('A1' in f['reservations'] for f in retained), len(retained))
    r=runs['bottleneck']
    check('bottleneck: both bodies actually arrive', all(v=='Arrived' for v in r['metrics']['final_results'].values()) and all(v<=CFG['arrival_radius'] for v in r['metrics']['actual_goal_errors'].values()),
          {'results':r['metrics']['final_results'],'errors':r['metrics']['actual_goal_errors'],'queue_wait_ticks':r['metrics']['gate_wait_frames']})
    r=runs['threshold_jitter']; n=len(r['metrics']['transitions']['G1'])
    check('jitter: loss grace prevents repeated state flips', n<=3, r['metrics']['transitions']['G1'])
    r=runs['private_memory']; initial=[f for f in r['frames'] if 1<=f['at']<=3]
    check('private memory: unseen NPC does not inherit another target', all(f['minds']['G1']['memory'] and f['minds']['G2']['memory'] is None for f in initial), len(initial))
    move=Move(goal=(8,10),points=[(8,10)],request_id=4,generation=2,result='Moving')
    stale=[move.completed(1,4,1,(8,10),CFG),move.completed(2,3,2,(8,10),CFG)]
    fake=move.completed(2,4,3,(4,10),CFG);unchanged=move.result=='Moving' and bool(move.points)
    real=move.completed(2,4,4,(8,10),CFG)
    check('lifecycle: stale/false arrival callbacks cannot change current move',not any(stale) and not fake and unchanged and real and move.result=='Arrived',move.events)
    # Low-node-budget control: exhaustion cannot be mislabeled an obstacle.
    low=dict(CFG);low['path_node_budget']=2
    geo=Geometry([[10,0,1,22]],low);res=geo.path((4,8),(12,8))
    check('navigation: budget exhaustion stays Unknown',res['status']=='BudgetExceeded',res)
    cfg=dict(CFG);cfg['path_node_budget']=700
    geo=Geometry([[10,0,1,22]],cfg);wall=geo.path((4,8),(10.2,8))
    check('navigation: blocked endpoint rejected before path claim',wall['status']=='InvalidEndpoint',wall)
    check('perception: FOV rejects a hostile behind observer',not Geometry([],CFG).see((5,10),0,(3,10)),{'observer':[5,10],'target':[3,10],'heading':0})
    fps={fps:run_scenario(next(s for s in SCENARIOS if s['id']=='squad_cover'),render_fps=fps)['trace_sha256'] for fps in (4,30,60,120)}
    check('frame scheduling: 4/30/60/120 FPS same fixed-step trace',len(set(fps.values()))==1,fps)
    repeat=run_scenario(SCENARIOS[0])
    check('repeatability: same seed/config identical full trace',repeat['trace_sha256']==runs[SCENARIOS[0]['id']]['trace_sha256'],repeat['trace_sha256'])
    refs={sid:run_scenario(next(s for s in SCENARIOS if s['id']==sid),reference=True) for sid in ('occlusion_reacquire','squad_cover','bottleneck')}
    check('comparison: direct chase exposes hidden reads',refs['occlusion_reacquire']['metrics']['hidden_coordinate_reads']>0 and runs['occlusion_reacquire']['metrics']['hidden_coordinate_reads']==0,
          {'reference':refs['occlusion_reacquire']['metrics']['hidden_coordinate_reads'],'candidate':0})
    check('comparison: independent same-goal reference is crowded',refs['squad_cover']['metrics']['same_goal_frames']>0 and runs['squad_cover']['metrics']['same_goal_frames']==0,
          {'reference_same_goal_frames':refs['squad_cover']['metrics']['same_goal_frames'],'candidate':0})
    durations=[x['metrics']['wall_seconds'] for x in list(runs.values())+list(refs.values())]
    vectors=[]
    for sid in ('occlusion_reacquire','hearing_only','target_invalid','squad_cover','stuck'):
        for f in runs[sid]['view_frames']:
            for aid,m in f['minds'].items():
                vectors.append({'scenario':sid,'at':f['at'],'npc':aid,'input_observation':m['memory'], 'live_visible':m['live_visible'],
                                'private_generation':m['generation'],'expected_state':m['state'],'expected_reason':m['reason'],
                                'expected_move':f['moves'][aid],'expected_reservation':f['reservations'].get(aid),
                                'expected_scores':f['scores'].get(aid,[])})
    receipt={'scope':'finite_synthetic_oracle_invariants_not_UE_acceptance','checks':checks,
             'passed':sum(x['pass'] for x in checks),'total':len(checks), 'status':'pass' if all(x['pass'] for x in checks) else 'failed_preserve_candidate',
             'host_python_seconds':{'median_run':statistics.median(durations),'max_run':max(durations),'claim_UE_FPS':False},
             'comparison':{sid:{'candidate':{k:runs[sid]['metrics'][k] for k in ('hidden_coordinate_reads','same_goal_frames','collision_blocks','min_ally_separation')},
                                'reference':{k:refs[sid]['metrics'][k] for k in ('hidden_coordinate_reads','same_goal_frames','collision_blocks','min_ally_separation')}} for sid in refs}}
    (out/'VERIFY.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    (out/'UE_ORACLE_TRACE_VECTORS.json').write_text(json.dumps({'scope':'sequential trace expectations; consume entire scenario, not stateless unit inputs','policy_sha256':hashlib.sha256(Path(__file__).with_name('policy.json').read_bytes()).hexdigest(),'vectors':vectors},indent=2),encoding='utf-8')
    print(json.dumps({'status':receipt['status'],'passed':receipt['passed'],'total':len(checks),
                      'failures':[x for x in checks if not x['pass']], 'median_host_seconds':receipt['host_python_seconds']['median_run']},ensure_ascii=False))
    return all(x['pass'] for x in checks)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args();out=Path(args.out).resolve()
    if not out.is_dir() or (out/'VERIFY.json').exists():
        raise SystemExit('Use existing unique generated run directory without a VERIFY receipt')
    raise SystemExit(0 if verify(out) else 1)
