"""Finite deterministic simulation; writes evidence only to an explicitly named run.

python Tools/Simulation/NPCAIV2/simulate.py --out tmp/npc-ai-v2-20261017/run_v1
No engine/build/Content/save/network operations exist in this module.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import time
from dataclasses import dataclass, field

from geometry import Geometry, intersects
from policy import Mind, Observation, callback_matches, cover_score, distance, joint_assignment, serialized_mind

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / 'policy.json').read_text(encoding='utf-8'))
SCENARIOS = json.loads((HERE / 'scenarios.json').read_text(encoding='utf-8'))['scenarios']


@dataclass
class Actor:
    id: str
    team: str
    position: tuple
    heading: float = 0
    alive: bool = True
    immobile_until: float = 0


@dataclass
class Move:
    goal: tuple | None = None
    points: list = field(default_factory=list)
    result: str = 'Idle'
    attempts: int = 0
    retries: int = 0
    request_id: int = 0
    generation: int = 1
    last_attempt: float = -100
    last_progress: float = 0
    progress_position: tuple = (0, 0)
    exhausted: bool = False
    needs_retry: bool = False
    travel: float = 0
    chase_travel: float = 0
    token: str = 'BT'
    events: list = field(default_factory=list)

    def completed(self, generation, request_id, at, actual_position, cfg):
        """A callback cannot fabricate arrival or supersede the current owner."""
        admitted = callback_matches(generation,request_id,self.generation,self.request_id)
        if not admitted:
            self.events.append({'at':at,'request':request_id,'generation':generation,'result':'StaleCallbackRejected','owner':self.token})
            return False
        if self.goal is None or distance(actual_position,self.goal)>cfg['arrival_radius']:
            self.events.append({'at':at,'request':request_id,'generation':generation,'result':'CallbackWithoutPhysicalArrival','owner':self.token})
            return False
        self.points=[]
        self.result='Arrived'
        return True

    def cancel(self, at, reason):
        if self.points:
            self.events.append({'at': round(at, 3), 'request': self.request_id, 'result': 'Cancelled', 'reason': reason, 'owner': self.token})
        self.points = []
        self.goal = None
        self.result = 'Idle'

    def request(self, goal, actor, geo, at, cfg):
        if self.exhausted:
            return
        changed = self.goal is None or distance(goal, self.goal) >= cfg['goal_change_distance']
        if not changed and not self.needs_retry:
            return
        if at - self.last_attempt < cfg['replan_interval'] - 1e-8:
            return
        if self.attempts >= cfg['attempts_per_run']:
            self.exhausted, self.result = True, 'Waiting:RunBudget'
            self.points = []
            self.events.append({'at': round(at, 3), 'request': self.request_id, 'result': self.result, 'reason': 'goal changes do not reset finite run budget', 'owner': self.token})
            return
        if changed:
            self.retries = 0
            self.goal = tuple(goal)
        elif self.retries >= cfg['move_retries']:
            self.exhausted, self.result = True, 'Waiting:RetryExhausted'
            self.points = []
            self.events.append({'at': round(at, 3), 'request': self.request_id, 'result': self.result, 'reason': 'same episode exhausted; requires explicit rearm', 'owner': self.token})
            return
        else:
            self.retries += 1
        self.attempts += 1
        self.request_id += 1
        self.last_attempt = at
        self.last_progress, self.progress_position = at, actor.position
        result = geo.path(actor.position, self.goal)
        self.points = result['points'][:]
        self.result = 'Moving' if result['status'] == 'Complete' else result['status']
        self.needs_retry = result['status'] != 'Complete'
        self.events.append({'at': round(at, 3), 'request': self.request_id, 'generation': self.generation,
                            'goal': self.goal, 'result': result['status'], 'reason': 'complete feet path admission' if not self.needs_retry else 'bounded retry; no fabricated arrival',
                            'expanded': result['expanded'], 'owner': self.token})


def run_scenario(spec, reference=False, render_fps=60, cfg=None):
    cfg = dict(CFG if cfg is None else cfg)
    rng = random.Random(cfg['seed'])
    geo = Geometry(spec['walls'], cfg)
    actors = {x['id']: Actor(x['id'], x['team'], tuple(x['position']), x.get('heading', 0),
                            immobile_until=x.get('immobile_until', 0)) for x in spec['agents']}
    actors['P'] = Actor('P', 'allied', tuple(spec['player']))
    minds = {k: Mind(k, a.team, a.position, state='Follow' if a.team == 'allied' else 'Guard') for k, a in actors.items() if k != 'P'}
    moves = {k: Move(progress_position=a.position) for k, a in actors.items() if k != 'P'}
    reservations, scores, assignment = {}, {}, {}
    assignment_reason, assigned_at, gate_owner = 'no tactical contact', -100, None
    reports = {}
    events = []
    frames, sample_frames = [], []
    metrics = {'hidden_coordinate_reads': 0, 'collision_blocks': 0, 'penetrations': 0,
               'min_ally_separation': 1e9, 'pair_comparisons_max': 0, 'assignment_switches': 0,
               'same_goal_frames': 0, 'max_tick_queries': 0, 'max_tick_expansions': 0,
               'overdue_search_frames': 0, 'gate_wait_frames': 0,
               'initial_npcs': len(minds), 'spawned_npcs': 0}
    seen_events = set()
    steps = round(min(spec['duration'], cfg['max_duration']) / cfg['fixed_dt'])
    # Display frame rate drives an accumulator, while the rule oracle uses fixed
    # integer simulation ticks. No frame-dependent randomness or wall-time input.
    due_steps, frame_no = [], 0
    while len(due_steps) <= steps:
        frame_no += 1
        due = min(steps + 1, int((frame_no / render_fps + 1e-9) / cfg['fixed_dt']) + 1)
        while len(due_steps) < due:
            due_steps.append(len(due_steps))
    sensor_ticks = round(cfg['sensor_period']/cfg['fixed_dt'])
    decision_ticks = round(cfg['decision_period']/cfg['fixed_dt'])
    start_wall = time.perf_counter()
    for step in due_steps:
        at = round(step * cfg['fixed_dt'], 6)
        query_before, exp_before = geo.query_count, geo.expansions
        noises = []
        for i, event in enumerate(spec['events']):
            if i not in seen_events and at + 1e-8 >= event['at']:
                seen_events.add(i)
                events.append(dict(event))
                if event['type'] == 'player_position':
                    actors['P'].position = tuple(event['position'])
                elif event['type'] == 'noise':
                    jitter = cfg['hearing_measurement_jitter_m']
                    measured = tuple(v+rng.uniform(-jitter,jitter) for v in event['position'])
                    noises.append(Observation(event['actor_id'], measured, at, 'hearing', event['uncertainty']))
                elif event['type'] == 'death':
                    dead = actors[event['actor_id']]
                    dead.alive = False
                    for mind in minds.values():
                        mind.invalidate(dead.id, at)
                    if dead.id in moves:
                        moves[dead.id].cancel(at, 'self dead; original registry event')
                        reservations.pop(dead.id, None)
                        minds[dead.id].transition('Dead', at, 'registered death; no ordinary revive')
                else:
                    raise ValueError(event)
        if spec.get('jitter'):
            actors['P'].position = (18.8 if (step // sensor_ticks) % 2 == 0 else 19.2, 10)
        if step % sensor_ticks == 0 or noises:
            for aid, mind in minds.items():
                actor = actors[aid]
                if not actor.alive:
                    continue
                hostile = [x for x in actors.values() if x.alive and x.team != actor.team]
                if len(hostile) > cfg['candidate_limit']:
                    raise ValueError('Fixture target budget exceeded; do not silently omit targets')
                sensed = [Observation(x.id, x.position, at) for x in hostile if geo.see(actor.position, actor.heading, x.position)]
                audible = [n for n in noises if distance(actor.position, n.position) <= cfg['hearing_range'] *
                           (cfg['wall_hearing_multiplier'] if geo.blocked(actor.position, n.position) else 1)]
                mind.receive(sensed, audible, at, actor.position, cfg)
                if actor.team == 'allied' and mind.live_visible:
                    reports[aid] = mind.memory
        ally_ids = sorted(k for k, a in actors.items() if k != 'P' and a.team == 'allied' and a.alive)
        if step % decision_ticks == 0:
            # Knowledge is each ally's own observation plus expiring immutable
            # teammate reports. Registry life filtering does not disclose location.
            for aid in ally_ids:
                mind = minds[aid]
                known = ([mind.memory] if mind.memory and at-mind.memory.at <= cfg['report_age'] and actors[mind.memory.actor_id].alive else [])
                known += [Observation(r.actor_id, r.position, r.at, 'report', r.uncertainty, owner)
                          for owner, r in reports.items() if owner != aid and at-r.at <= cfg['report_age'] and actors[r.actor_id].alive]
                mind.knowledge = sorted(known, key=lambda r: (-r.at, r.actor_id))[0] if known else None
            tactical = len(ally_ids) == 2 and actors['P'].alive and all(minds[k].knowledge for k in ally_ids)
            if tactical:
                scores = {}
                covers = spec.get('covers', [(actors['P'].position[0]-3, actors['P'].position[1]-2),
                                               (actors['P'].position[0]-3, actors['P'].position[1]+2)])
                if len(covers) > cfg['candidate_limit']:
                    raise ValueError('Candidate budget exceeded')
                for idx, aid in enumerate(ally_ids):
                    role = 'Support' if idx == 0 else 'Overwatch'
                    actor = actors[aid]
                    scores[aid] = []
                    for cid, p in enumerate(covers):
                        p = tuple(p)
                        route = geo.path(actor.position, p)
                        gates = []
                        if route['status'] != 'Complete':
                            gates.append(route['status'])
                        if distance(p, actors['P'].position) > cfg['ally_player_envelope']:
                            gates.append('PlayerEnvelope')
                        if moves[aid].chase_travel >= cfg['ally_chase_travel_budget']:
                            gates.append('ChaseTravelExhausted')
                        if moves[aid].exhausted:
                            gates.append('MoveEpisodeExhausted')
                        value, features, contributions = cover_score(role, p, actors['P'].position,
                            minds[aid].knowledge.position, route['length'], geo.blocked(p, minds[aid].knowledge.position), cfg)
                        scores[aid].append({'id': 'C'+str(cid+1), 'position': p, 'valid': not gates,
                                            'gates': gates, 'score': round(value, 6), 'features': features,
                                            'contributions': contributions, 'role': role,
                                            'observed_threat': minds[aid].knowledge.position})
                selected, assignment_reason, pair_count = joint_assignment(scores, assignment, at, assigned_at, cfg)
                metrics['pair_comparisons_max'] = max(metrics['pair_comparisons_max'], pair_count)
                if selected:
                    next_assignment = {aid: row['id'] for aid, row in selected.items()}
                    if next_assignment != assignment:
                        assignment, assigned_at = next_assignment, at
                        metrics['assignment_switches'] += 1
                    for aid, row in selected.items():
                        reservations[aid] = {'id': row['id'], 'position': row['position'], 'generation': minds[aid].generation,
                                             'since': assigned_at, 'reason': assignment_reason}
                        minds[aid].transition(row['role'], at, assignment_reason)
                else:
                    reservations.clear()
                    for aid in ally_ids:
                        if not moves[aid].exhausted:
                            minds[aid].transition('Regroup', at, assignment_reason)
            else:
                reservations.clear()
                assignment = {}
                scores = {}
                for idx, aid in enumerate(ally_ids):
                    mind = minds[aid]
                    if not actors['P'].alive:
                        mind.transition('Waiting', at, 'no living player; finite roster unchanged')
                        moves[aid].cancel(at, mind.reason)
                        continue
                    if moves[aid].exhausted:
                        mind.transition('Waiting', at, moves[aid].result+'; sensing remains active')
                        continue
                    mind.transition('Follow', at, 'no unexpired contact; distinct follow slots')
                    goal = (actors['P'].position[0]-cfg['follow_distance'], actors['P'].position[1]+(-1.2 if idx == 0 else 1.2))
                    reservations[aid] = {'id': 'F'+str(idx+1), 'position': goal, 'generation': mind.generation,
                                         'since': at, 'reason': mind.reason}
            # Reference intentionally bypasses perception for direct chase, and
            # bypasses coordination for same follow goal. It is never adoptable.
            for aid, mind in minds.items():
                actor = actors[aid]
                if not actor.alive:
                    continue
                if reference:
                    goal = actors['P'].position if actor.team == 'german' else (actors['P'].position[0]-3, actors['P'].position[1])
                    if actor.team == 'german' and not mind.live_visible:
                        metrics['hidden_coordinate_reads'] += 1
                    mind.transition('DirectChaseReference', at, 'deliberately unsafe comparison')
                elif actor.team == 'german':
                    goal = mind.enemy_intent(at, actor.position, cfg)
                    if mind.state == 'Guard':
                        actor.heading = next(x.get('heading',0) for x in spec['agents'] if x['id']==aid)
                else:
                    goal = reservations.get(aid, {}).get('position')
                move = moves[aid]
                if goal is None:
                    if not move.exhausted:
                        move.cancel(at, 'intent has no movement ownership')
                else:
                    move.request(goal, actor, geo, at, cfg)
                if move.exhausted and actor.team == 'allied':
                    reservations.pop(aid, None)
                    mind.transition('Waiting', at, move.result)
        # Actual finite toy motion: swept disc/rect checks and actor separation.
        for aid in sorted(minds):
            actor, mind, move = actors[aid], minds[aid], moves[aid]
            if not actor.alive or not move.points:
                continue
            while move.points and distance(actor.position, move.points[0]) < 0.08:
                move.points.pop(0)
            if not move.points:
                move.result = 'Arrived'
                continue
            point = move.points[0]
            d = distance(actor.position, point)
            stride = min(d, cfg['move_speed']*cfg['fixed_dt'])
            want = (actor.position[0]+(point[0]-actor.position[0])*stride/max(d, 1e-9),
                    actor.position[1]+(point[1]-actor.position[1])*stride/max(d, 1e-9))
            gate = spec.get('gate')
            gate_wait = False
            # Reserve before path convergence, not only when a disc finally
            # enters the throat. The entire remaining path predicts gate use.
            route_points = [actor.position]+move.points
            needs_gate = gate and actor.position[0] <= gate[0]+gate[2] and any(intersects(p,q,gate) for p,q in zip(route_points,route_points[1:]))
            if needs_gate:
                if gate_owner is None:
                    gate_owner = aid
                elif gate_owner != aid:
                    gate_wait = True
                    metrics['gate_wait_frames'] += 1
            dynamic_block = any(x.id != aid and x.alive and distance(want, x.position) < 2*cfg['capsule_radius']
                                for x in actors.values())
            blocked = at < actor.immobile_until or geo.blocked(actor.position, want, cfg['capsule_radius']) or dynamic_block or gate_wait
            if dynamic_block:
                metrics['collision_blocks'] += 1
            if not blocked:
                move.travel += distance(actor.position, want)
                if mind.state in ('Support', 'Overwatch'):
                    move.chase_travel += distance(actor.position, want)
                actor.position = want
                if mind.state in ('Investigate', 'Search', 'Return'):
                    actor.heading = math.atan2(point[1]-actor.position[1], point[0]-actor.position[0])
                if distance(actor.position, move.progress_position) > 0.1:
                    move.last_progress, move.progress_position = at, actor.position
            elif gate_wait:
                # Queue waiting is explicit, not a stuck-path retry. In these
                # finite fixtures gate owner exits or death releases the token.
                move.last_progress = at
            if at - move.last_progress >= cfg['stall_timeout'] - 1e-8 and move.goal:
                move.needs_retry = True
                move.points = []
                move.result = 'Stalled'
                move.events.append({'at': round(at, 3), 'request': move.request_id, 'result': 'Stalled',
                                    'reason': 'measured no progress; bounded recovery', 'owner': move.token})
            if move.goal and distance(actor.position, move.goal) <= cfg['arrival_radius']:
                move.completed(move.generation,move.request_id,at,actor.position,cfg)
        if gate_owner and (not actors[gate_owner].alive or not intersects(actors[gate_owner].position, actors[gate_owner].position, spec['gate'])):
            # Retain while approaching/intersecting a gate path, release only
            # after the owner has physically crossed the rectangle's far side.
            owner = actors[gate_owner]
            if not owner.alive or owner.position[0] > spec['gate'][0]+spec['gate'][2]:
                gate_owner = None
        if len(ally_ids) == 2:
            sep = distance(actors[ally_ids[0]].position, actors[ally_ids[1]].position)
            metrics['min_ally_separation'] = min(metrics['min_ally_separation'], sep)
            goals = [moves[x].goal for x in ally_ids]
            if all(goals) and distance(*goals) < cfg['reservation_separation']:
                metrics['same_goal_frames'] += 1
        for aid, mind in minds.items():
            if mind.state in ('Search', 'Investigate') and mind.search_deadline >= 0 and at > mind.search_deadline + cfg['decision_period'] + 1e-8:
                metrics['overdue_search_frames'] += 1
            if actors[aid].alive and not geo.free(actors[aid].position):
                metrics['penetrations'] += 1
        metrics['max_tick_queries'] = max(metrics['max_tick_queries'], geo.query_count-query_before)
        metrics['max_tick_expansions'] = max(metrics['max_tick_expansions'], geo.expansions-exp_before)
        frame = {'at': at, 'actors': {aid: {'team': x.team, 'position': [round(v, 4) for v in x.position],
                    'heading': round(x.heading, 4), 'alive': x.alive} for aid, x in actors.items()},
                 'minds': {aid: serialized_mind(m) for aid, m in minds.items()},
                 'moves': {aid: {'goal': m.goal, 'result': m.result, 'request': m.request_id, 'generation': m.generation,
                                'retries': m.retries, 'attempts': m.attempts, 'path': m.points, 'travel': round(m.travel, 4)} for aid, m in moves.items()},
                 'reservations': {aid: dict(x) for aid, x in reservations.items()},
                 'scores': {aid: list(x) for aid, x in scores.items()}, 'assignment_reason': assignment_reason,
                 'gate_owner': gate_owner}
        frames.append(frame)
        if step % decision_ticks == 0:
            sample_frames.append(frame)
    metrics.update({'path_queries': geo.query_count, 'path_expansions': geo.expansions,
                    'max_query_expansions': geo.max_expansions, 'query_budget_exceeded': geo.budget_failures,
                    'cache_hits': geo.cache_hits, 'wall_seconds': round(time.perf_counter()-start_wall, 6),
                    'npc_attempts': {aid: m.attempts for aid, m in moves.items()},
                    'npc_retries': {aid: m.retries for aid, m in moves.items()},
                    'actual_goal_errors': {aid: round(distance(actors[aid].position, m.goal), 4) if m.goal else None for aid, m in moves.items()},
                    'final_results': {aid: m.result for aid, m in moves.items()},
                    'transitions': {aid: m.transitions for aid, m in minds.items()},
                    'move_events': {aid: m.events for aid, m in moves.items()},
                    'frame_count': len(frames), 'render_fps_input': render_fps})
    if metrics['min_ally_separation'] == 1e9:
        metrics['min_ally_separation'] = None
    trace_json = json.dumps(frames, sort_keys=True, separators=(',', ':'))
    return {'id': spec['id'], 'spec': spec, 'reference': reference, 'metrics': metrics,
            'trace_sha256': hashlib.sha256(trace_json.encode()).hexdigest(), 'frames': frames, 'view_frames': sample_frames}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    if out.exists():
        raise SystemExit('Run identity already exists; choose a new --out to preserve prior evidence')
    out.mkdir(parents=True)
    snapshot = out/'source_snapshot'
    snapshot.mkdir()
    for source in HERE.iterdir():
        if source.is_file():
            (snapshot/source.name).write_bytes(source.read_bytes())
    results = [run_scenario(s) for s in SCENARIOS]
    reference_ids = {'occlusion_reacquire', 'squad_cover', 'bottleneck'}
    references = [run_scenario(s, reference=True) for s in SCENARIOS if s['id'] in reference_ids]
    for result in results+references:
        suffix = '_reference' if result['reference'] else ''
        with (out/(result['id']+suffix+'.ndjson')).open('w', encoding='utf-8', newline='\n') as stream:
            for frame in result['frames']:
                stream.write(json.dumps(frame, separators=(',', ':'))+'\n')
    summary = {'scope': 'finite_offline_synthetic_not_UE_or_Paris', 'seed': CFG['seed'],
               'config_sha256': hashlib.sha256((HERE/'policy.json').read_bytes()).hexdigest(),
               'scenarios': [{k:v for k,v in r.items() if k not in ('frames','view_frames')} for r in results],
               'references': [{k:v for k,v in r.items() if k not in ('frames','view_frames')} for r in references]}
    (out/'RESULT.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    view = {'config': CFG, 'runs': [{k:v for k,v in r.items() if k != 'frames'} for r in results+references]}
    template = (HERE/'replay.html').read_text(encoding='utf-8')
    (out/'replay.html').write_text(template.replace('/*__EVIDENCE__*/null', json.dumps(view, separators=(',', ':'))), encoding='utf-8')
    print(json.dumps({'status':'generated_finite_candidate', 'out':str(out), 'scenarios':len(results), 'references':len(references),
                      'replay_bytes':(out/'replay.html').stat().st_size, 'runtime_acceptance':False}))


if __name__ == '__main__':
    main()
