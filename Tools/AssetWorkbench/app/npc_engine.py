"""Interactive, finite 2D world. No UE/process/file/network or original asset writes."""
from dataclasses import dataclass, field
from copy import deepcopy
import json
import math
from pathlib import Path
from .npc_geometry import Geometry
from .npc_oracle import Mind, Observation, cover_score, distance, joint_assignment, serialized_mind
from .npc_behavior_tree import tick_tree
from .npc_parameters import normalize
from .npc_tactics import TacticalWorld

ROOT = Path(__file__).resolve().parents[3]
CFG = json.loads((ROOT/'Tools/Simulation/NPCAIV2/policy.json').read_text(encoding='utf-8'))
PRESETS = {
    'follow': {'P': (8, 11), 'A1': (5, 9), 'A2': (5, 13), 'G1': (23, 10), 'G2': (28, 3), 'G3': (28, 19)},
    'support': {'P': (18, 10), 'A1': (17.5, 7), 'A2': (17.5, 13), 'G1': (24, 10), 'G2': (28, 3), 'G3': (28, 19)},
    'search': {'P': (19, 10), 'A1': (5, 9), 'A2': (5, 13), 'G1': (21, 10), 'G2': (28, 3), 'G3': (28, 19)},
    'squad': {'P': (20, 11), 'A1': (3, 3), 'A2': (3, 19), 'G1': (24, 11), 'G2': (12, 8), 'G3': (12, 14)},
}


@dataclass
class Unit:
    id: str
    position: tuple
    team: str
    heading: float
    alive: bool = True
    health: float = 100
    ammo: int = 30
    last_fire: float = -100


@dataclass
class Movement:
    goal: tuple | None = None
    points: list = field(default_factory=list)
    result: str = 'Idle'
    requests: int = 0
    retries: int = 0
    generation: int = 1
    last_attempt: float = -100
    last_progress: float = 0
    progress_position: tuple = (0, 0)
    exhausted: bool = False
    retry: bool = False
    travel: float = 0
    chase: float = 0


class World(TacticalWorld):
    duration = 120
    request_budget = 32

    def __init__(self, preset='follow', layout=None, geometry=None, headings=None, parameters=None):
        if preset not in PRESETS:
            raise ValueError('Unknown preset')
        self.preset = preset
        self.cfg = dict(CFG)
        self.parameters = normalize(parameters)
        self.cfg.update({k: self.parameters[k] for k in ('follow_distance', 'loss_grace', 'search_duration')})
        self.walls = [] if geometry else [[15, 6, 1, 10]]
        if geometry:
            self.cfg['path_node_budget'] = geometry.cfg['path_node_budget']
        self.geo = geometry or Geometry(self.walls, self.cfg)
        positions = geometry.preset_positions(preset) if geometry and layout is None else PRESETS[preset]
        if layout is not None:
            if set(layout) != set(positions):
                raise ValueError('Layout must contain P, A1/A2 and G1/G2/G3 exactly')
            positions = {k: tuple(v) for k, v in layout.items()}
        self.actors = {k: Unit(k, tuple(p), 'german' if k.startswith('G') else 'allied', math.pi if k.startswith('G') else 0) for k, p in positions.items()}
        if preset == 'squad' and geometry is None:
            self.actors['G2'].heading = self.actors['G3'].heading = 0
        if headings is not None:
            if set(headings) != set(self.actors) or not all(math.isfinite(v) for v in headings.values()):
                raise ValueError('All six finite headings are required')
            for k, angle in headings.items():
                self.actors[k].heading = angle % (2*math.pi)
        for k, unit in self.actors.items():
            self.validate_position(k, unit.position)
        self.minds = {k: Mind(k, a.team, a.position) for k, a in self.actors.items() if k != 'P'}
        self.moves = {k: Movement(progress_position=a.position) for k, a in self.actors.items()}
        self.home_headings = {k: a.heading for k, a in self.actors.items()}
        self.ticks = 0
        self.revision = 0
        self.reports = {}
        self.reservations = {}
        self.assignment = {}
        self.assigned_at = -100
        self.scores = {}
        self.events = []
        self.history = []
        self.behavior_trees = {}
        self.perception = {}
        self.metrics = {'penetrations': 0, 'collision_waits': 0, 'player_commands': 0, 'hidden_target_reads': 0, 'pair_comparisons_max': 0}
        self._init_tactics()
        self._allow_fire = False
        self._sense()
        self._decide()

    @property
    def at(self):
        return round(self.ticks * .1, 6)

    def validate_position(self, aid, position):
        if aid not in self.actors or len(position) != 2 or not all(isinstance(x, (float, int)) and math.isfinite(x) for x in position):
            raise ValueError('Invalid member/position')
        if not self.geo.free(position):
            raise ValueError('位置落在黑色/未知区域、边缘净空不足，或超出场景范围 / Position is blocked or lacks footprint clearance')
        if any(k != aid and a.alive and distance(position, a.position) < 2*self.cfg['capsule_radius'] for k, a in self.actors.items()):
            raise ValueError('Position overlaps another member')

    def event(self, aid, kind, reason):
        self.events.append({'at': self.at, 'actor_id': aid, 'kind': kind, 'reason': reason})
        self.events = self.events[-100:]

    def new_player_order(self):
        self.metrics['player_commands'] += 1
        for aid, m in self.moves.items():
            m.requests = m.retries = 0
            m.exhausted = m.retry = False
            m.chase = 0
            m.generation += 1
            m.goal, m.points, m.result = None, [], 'Idle'
            m.last_attempt, m.last_progress = -100, self.at
            m.progress_position = self.actors[aid].position
        self.moves['P'].goal = None
        self.moves['P'].points = []
        self.moves['P'].last_attempt = -100
        self.event('P', 'NewOrder', 'accepted human input starts a new finite planning budget; memories retained')

    def command(self, kind, actor_id='P', position=None, heading=None):
        if self.at >= self.duration:
            raise ValueError('Episode finished; reset to start a new finite episode')
        if kind not in ('place', 'walk', 'rotate', 'fire') or actor_id not in self.actors:
            raise ValueError('Invalid command')
        if kind == 'fire':
            if self.actors[actor_id].team != 'german':
                raise ValueError('Select a German target for the player shot')
            self._fire('P', actor_id, manual=True)
            self._sense()
            self._decide()
            return
        if not self.actors[actor_id].alive:
            raise ValueError('This member is a casualty; reset to start a new episode')
        if kind == 'rotate':
            if heading is None or not math.isfinite(heading):
                raise ValueError('A finite heading is required')
            self.actors[actor_id].heading = heading % (2*math.pi)
            self.home_headings[actor_id] = heading % (2*math.pi)
            if actor_id == 'P':
                self.new_player_order()
            self.event(actor_id, 'Heading', 'explicit authored heading; private memories retained')
            self._sense()
            self._decide()
            return
        position = tuple(position or ())
        self.validate_position(actor_id, position)
        if kind == 'walk' and actor_id != 'P':
            raise ValueError('Walking input belongs to the player; NPC orders come from policy')
        if kind == 'walk':
            route = self.geo.path(self.actors['P'].position, position)
            if route['status'] != 'Complete':
                raise ValueError('Player path: '+route['status'])
            self.new_player_order()
            self._request('P', position)
        else:
            self.actors[actor_id].position = position
            self.moves[actor_id] = Movement(generation=self.moves[actor_id].generation+1, progress_position=position)
            if actor_id == 'P':
                self.new_player_order()
            else:
                # Re-authoring an NPC changes its own anchor, not other NPC memories.
                generation = self.minds[actor_id].generation+1
                self.minds[actor_id] = Mind(actor_id, self.actors[actor_id].team, position, generation=generation)
                self.reports.pop(actor_id, None)
                self.reservations.pop(actor_id, None)
                self.squad_alerts.pop(actor_id, None)
            self.event(actor_id, 'Placement', 'validated authored position')
        self._sense()
        self._decide()

    def configure(self, parameters):
        # Validate the entire patch before changing any live state.
        updated = normalize(parameters, self.parameters)
        if self.at >= self.duration:
            raise ValueError('Episode finished; reset before tuning')
        changed = {k: v for k, v in updated.items() if v != self.parameters[k]}
        if not changed:
            return
        self.parameters = updated
        self.cfg.update({k: updated[k] for k in ('follow_distance', 'loss_grace', 'search_duration')})
        if {'follow_distance', 'scout_distance', 'tactical_coordination', 'allied_mode'} & changed.keys():
            self.bound = None
        if 'search_duration' in changed:
            for mind in self.minds.values():
                if mind.faction == 'german' and mind.search_deadline >= 0:
                    mind.search_deadline = mind.search_started + updated['search_duration']
        if 'follow_distance' in changed:
            for aid in ('A1', 'A2'):
                if self.minds[aid].state in ('Follow', 'Regroup'):
                    self._cancel(aid)
        self.event('P', 'Parameters', json.dumps(changed, sort_keys=True))
        self._sense()
        self._decide()

    def _vision(self, team):
        return ({**self.cfg, 'sight_range': self.parameters['german_sight_range'],
                 'sight_fov_degrees': self.parameters['german_sight_fov_degrees']}
                if team == 'german' else self.cfg)

    def _sense(self):
        # Replace, never mutate a previous sample retained by a tree/history frame.
        self.perception = {}
        for aid, actor in self.actors.items():
            if not actor.alive:
                continue
            vision = self._vision(actor.team)
            sightings = []
            for target in self.actors.values():
                if not target.alive or target.team == actor.team:
                    continue
                if actor.team == 'german' and target.id == 'P':
                    evidence = self.geo.sight_evidence(actor.position, actor.heading, target.position, vision)
                    evidence.update({'at': self.at, 'observer': aid, 'target': 'P',
                                     'map_sha256': getattr(self.geo, 'data', {}).get('sha256')})
                    self.perception[aid] = evidence
                    visible = evidence['visible']
                else:
                    visible = self.geo.see(actor.position, actor.heading, target.position, vision)
                if visible:
                    sightings.append(Observation(target.id, target.position, self.at))
            if aid in self.perception:
                self.perception[aid]['visible_hostiles'] = [x.actor_id for x in sightings]
            if aid != 'P':
                self.minds[aid].receive(sightings, [], self.at, actor.position, vision)
            if actor.team == 'allied' and sightings:
                self.reports[aid] = min(sightings, key=lambda x: (distance(actor.position, x.position), x.actor_id))
        self.reports = {k: r for k, r in self.reports.items() if self.at-r.at <= self.cfg['report_age']}

    def _cancel(self, aid):
        m = self.moves[aid]
        m.points = []
        if not self.actors[aid].alive:
            m.goal, m.result = None, 'Dead'
            return
        if not m.exhausted:
            m.goal, m.result = None, 'Idle'

    def _request(self, aid, goal):
        m, actor = self.moves[aid], self.actors[aid]
        if m.exhausted:
            return
        changed = (m.goal is None or distance(goal, m.goal) >= self.cfg['goal_change_distance']
                   or m.result == 'Arrived' and distance(goal, m.goal) >= self.cfg['arrival_radius'])
        if not changed and not m.retry:
            return
        if self.at-m.last_attempt < self.cfg['replan_interval']-1e-8:
            return
        if m.requests >= self.request_budget or m.retry and m.retries >= self.cfg['move_retries']:
            m.exhausted, m.points, m.result = True, [], 'WaitingBudgetExhausted'
            self.event(aid, m.result, 'finite planning/recovery budget; new human order or reset required')
            return
        if m.retry:
            m.retries += 1
        m.requests += 1
        m.last_attempt = self.at
        m.retry = False
        m.goal = tuple(goal)
        route = self.geo.path(actor.position, m.goal)
        m.points = list(route['points'])
        m.result = 'Moving' if route['status'] == 'Complete' else route['status']
        m.last_progress, m.progress_position = self.at, actor.position
        if route['status'] != 'Complete':
            m.retry = True
            self.event(aid, m.result, 'explicit finite path result; not an actual arrival')

    def _follow_goal(self, aid, wanted):
        candidates = [wanted]
        candidates += [(wanted[0]+r*math.cos(a*math.pi/4), wanted[1]+r*math.sin(a*math.pi/4)) for r in (.75, 1.5, 2) for a in range(8)]
        # Reservations are friendly coordination data, never hostile intel.
        occupied = [r['position'] for k, r in self.reservations.items()
                    if k != aid and self.actors[k].team == self.actors[aid].team]
        for p in candidates:
            if self.geo.free(p) and all(distance(p, q) >= self.cfg['reservation_separation'] for q in occupied):
                if self.geo.path(self.actors[aid].position, p)['status'] == 'Complete':
                    return p
        return None

    def _decide(self):
        player = self.actors['P']
        if self.moves['P'].retry and self.moves['P'].goal:
            self._request('P', self.moves['P'].goal)
        allies = ['A1', 'A2']
        selected = self._plan_allies()
        reason = 'independent reachable tactical roles; one living ally remains functional'
        self.reservations = {}
        self.behavior_trees = {}
        for i, aid in enumerate(allies):
            self._tick_behavior(aid, {'index': i, 'selected': selected, 'reason': reason, 'goal': None})
        self._coordinate_germans()
        for aid in ['G1', 'G2', 'G3']:
            if self.actors[aid].alive:
                self._accept_report(aid)
            self._tick_behavior(aid, {'goal': None})
        for m in self.minds.values():
            m.transitions = m.transitions[-80:]
        if len(self.geo.cache) > 1024:
            self.geo.cache.clear()

    def _tick_behavior(self, aid, context):
        mind, actor, movement = self.minds[aid], self.actors[aid], self.moves[aid]

        def condition(op):
            if op in ('bound_plan', 'cover_geometry', 'bound_holder', 'bound_ready', 'squad_maneuver'):
                detail = deepcopy(self.maneuvers.get(aid, {'active': False, 'reason': 'coordination disabled or no admitted maneuver'}))
                if op == 'squad_maneuver':
                    detail['player_sight'] = self.perception.get(aid)
                cover = detail.get('cover') or {}
                passed = {'bound_plan': detail.get('active',False),
                          'cover_geometry': all(cover.get(k) for k in ('hide_blocked','peek_clear','connector_clear')) and cover.get('path_status')=='Complete',
                          'bound_holder': detail.get('holder')==aid,
                          'bound_ready': detail.get('holder_ready',False),
                          'squad_maneuver': detail.get('active',False)}[op]
                return passed, detail
            if op == 'dead':
                return not actor.alive, {'alive': actor.alive, 'health': actor.health}
            if op == 'fire_ready':
                detail = self._fire_check(aid)
                self.combat_checks[aid] = detail
                return detail['permitted'], detail
            if op == 'squad_report':
                notice = self.squad_alerts.get(aid)
                return bool(notice and not mind.live_visible and mind.memory and mind.memory.sense == 'report'
                            and mind.memory.at > mind.consumed_observation), {'report': notice, 'live_visible': mind.live_visible}
            if op in ('tactical_contact', 'scouting', 'covering'):
                plan = self.plans[aid]
                passed = plan['contact'] if op == 'tactical_contact' else not plan['contact'] and plan['role'] == ('Scout' if op == 'scouting' else 'Cover')
                return passed, dict(plan)
            if op == 'budget':
                return movement.exhausted, {'requests': movement.requests, 'limit': self.request_budget, 'result': movement.result}
            if op == 'assigned':
                row = context['selected'].get(aid)
                return bool(row), {'assignment': row['id'] if row else None, 'role': row['role'] if row else None,
                                   'reason': context['reason']}
            if op == 'contact':
                return bool(mind.knowledge), {'observation': self._tree_observation(mind.knowledge)}
            if op == 'goal':
                return context['goal'] is not None, {'goal': list(context['goal']) if context['goal'] is not None else None}
            if op == 'visible':
                return bool(mind.live_visible and mind.memory), {'live_visible': mind.live_visible, 'observation': self._tree_observation(mind.memory),
                    'german_sight_range': self.parameters['german_sight_range'], 'german_sight_fov_degrees': self.parameters['german_sight_fov_degrees'],
                    'player_sight': self.perception.get(aid)}
            if op == 'alert':
                elapsed = self.at-mind.state_since
                return mind.state in ('Guard', 'Return') or mind.state == 'Alert' and elapsed < self.cfg['alert_dwell']-1e-8, {
                    'state': mind.state, 'elapsed': round(elapsed, 6), 'dwell': self.cfg['alert_dwell']}
            if op == 'hearing':
                return bool(mind.memory and mind.memory.sense == 'hearing' and mind.state == 'Alert'
                            and self.at-mind.state_since < self.cfg['alert_dwell']-1e-8), {
                    'sense': mind.memory.sense if mind.memory else None, 'state': mind.state}
            if op == 'grace':
                elapsed = self.at-mind.last_sight
                return bool(mind.memory and mind.memory.sense == 'sight' and elapsed < self.cfg['loss_grace']-1e-8), {
                    'since_last_sight': round(elapsed, 6), 'grace': self.cfg['loss_grace']}
            if op == 'memory':
                return bool(mind.memory and mind.memory.at > mind.consumed_observation), {
                    'observation': self._tree_observation(mind.memory), 'consumed_at': mind.consumed_observation}
            if op == 'search':
                return bool(context['goal'] and mind.state == 'Search' and hasattr(self.geo, 'description')), {
                    'state': mind.state, 'raster': hasattr(self.geo, 'description')}
            if op == 'guard':
                return mind.state == 'Guard', {'state': mind.state}
            raise RuntimeError('Unknown tree condition: '+op)

        def action(op):
            if op == 'dead_hold':
                self._cancel(aid)
                mind.transition('Dead', self.at, '2D casualty; reset required')
                return 'Running', {'health': actor.health, 'reason': 'casualty_no_navigation_or_fire'}
            if op == 'fire':
                return 'Success', self._fire(aid)
            if op == 'fire_hold':
                return 'Success', self.combat_checks.get(aid, {})
            if op == 'tactical_plan':
                plan = self.plans[aid]
                context['goal'] = tuple(plan['goal']) if plan['goal'] else None
                mind.transition(plan['role'] if context['goal'] else 'Waiting', self.at, plan['reason'])
                if context['goal']:
                    self.reservations[aid] = {'id': plan['slot'], 'position': context['goal'], 'role': plan['role']}
                return 'Success', dict(plan)
            if op == 'wait_budget':
                mind.transition('Waiting', self.at, movement.result)
                return 'Running', {'result': movement.result, 'requires_new_order': True}
            if op == 'reserve_role':
                row = context['selected'][aid]
                context['goal'] = tuple(row['position'])
                mind.transition(row['role'], self.at, context['reason'])
                self.reservations[aid] = {'id': row['id'], 'position': context['goal']}
                return 'Success', {'slot': row['id'], 'role': row['role'], 'goal': list(context['goal'])}
            if op == 'formation':
                # Player position is friendly information, never a German target fallback.
                player = self.actors['P']
                forward = (math.cos(player.heading), math.sin(player.heading))
                side = (-forward[1], forward[0])
                wanted = (player.position[0]-self.cfg['follow_distance']*forward[0]+(-1.2 if context['index'] == 0 else 1.2)*side[0],
                          player.position[1]-self.cfg['follow_distance']*forward[1]+(-1.2 if context['index'] == 0 else 1.2)*side[1])
                context['goal'] = self._follow_goal(aid, wanted)
                state = 'Regroup' if mind.knowledge else 'Follow'
                mind.transition(state if context['goal'] else 'Waiting', self.at,
                                context['reason'] if context['goal'] else 'no complete separated formation path')
                return 'Success', {'follow_distance': self.cfg['follow_distance'], 'desired_slot': list(wanted), 'goal': list(context['goal']) if context['goal'] else None}
            if op == 'reserve_formation':
                slot = 'F'+str(context['index']+1)
                self.reservations[aid] = {'id': slot, 'position': context['goal']}
                return 'Success', {'slot': slot, 'goal': list(context['goal'])}
            if op == 'enemy_policy':
                context['goal'] = self._maneuver_enemy_intent(aid)
                if context['goal']:
                    self.reservations[aid] = {'id': aid+'.sector', 'position': context['goal'], 'role': self.maneuvers.get(aid,{}).get('role',mind.state)}
                return 'Success', {'state': mind.state, 'reason': mind.reason, 'search_duration': self.cfg['search_duration'],
                                   'search_started': mind.search_started, 'deadline': mind.search_deadline,
                                   'report': self.squad_alerts.get(aid), 'sector': int(aid[-1])-1,
                                   'maneuver': deepcopy(self.maneuvers.get(aid)),
                                   'goal': list(context['goal']) if context['goal'] else None}
            if op == 'project_search':
                goal = context['goal']
                candidates = [goal]+[(goal[0]+r*math.cos(i*math.pi/4), goal[1]+r*math.sin(i*math.pi/4))
                                     for r in (.5, 1, 1.5) for i in range(8)]
                projected = next((p for p in candidates if self.geo.free(p) and self.geo.path(actor.position,p)['status']=='Complete'), None)
                if projected is None:
                    mind.search_index += 1
                    mind.search_goal = None
                    self.event(aid, 'SearchPointSkipped', 'no complete bounded raster candidate around frozen offset')
                else:
                    mind.search_goal = projected
                context['goal'] = projected
                return 'Success', {'requested_offset': list(goal), 'projected': list(projected) if projected else None,
                                   'candidate_limit': len(candidates), 'deadline': mind.search_deadline}
            if op == 'move':
                self._request(aid, context['goal'])
                arrived = movement.result == 'Arrived' and distance(actor.position, context['goal']) <= self._arrival_tolerance(aid)
                status = ('Success' if arrived else 'Running' if movement.result in ('Moving', 'Idle', 'Arrived') else 'Failure')
                return status, {'result': movement.result, 'goal': list(movement.goal) if movement.goal else None,
                                'requested_goal': list(context['goal']), 'requests': movement.requests,
                                'retries': movement.retries, 'arrival_error': distance(actor.position, movement.goal) if movement.goal else None}
            if op == 'guard_hold':
                actor.heading = self.home_headings[aid]
            if op in ('guard_hold', 'cancel', 'wait_no_path'):
                self._cancel(aid)
                return 'Running', {'state': mind.state, 'result': movement.result, 'reason': mind.reason}
            raise RuntimeError('Unknown tree action: '+op)

        trace = tick_tree(actor.team, self.at, condition, action)
        trace['parameters'] = dict(self.parameters)
        trace['blackboard'] = {'state': mind.state, 'live_visible': mind.live_visible,
            'observation': self._tree_observation(mind.memory), 'home': list(mind.home),
            'search_origin': list(mind.search_origin) if mind.search_origin else None,
            'search_started': mind.search_started, 'search_deadline': mind.search_deadline, 'search_index': mind.search_index,
            'move_goal': list(movement.goal) if movement.goal else None, 'move_result': movement.result,
            'requests': movement.requests, 'request_limit': self.request_budget, 'retries': movement.retries,
            'reservation': dict(self.reservations[aid]) if aid in self.reservations else None}
        trace['blackboard'].update({'squad_report': self.squad_alerts.get(aid), 'combat': self.combat_checks.get(aid),
                                    'health': actor.health, 'ammo': actor.ammo, 'maneuver': deepcopy(self.maneuvers.get(aid))})
        if actor.team == 'allied':
            trace['blackboard'].update({'player_position': list(self.actors['P'].position),
                                        'squad_observation': self._tree_observation(mind.knowledge)})
        else:
            trace['blackboard']['player_sight'] = self.perception.get(aid)
        self.behavior_trees[aid] = trace

    @staticmethod
    def _tree_observation(observation):
        return ({'actor_id': observation.actor_id, 'position': list(observation.position),
                 'at': observation.at, 'sense': observation.sense, 'source': observation.source} if observation else None)

    def _move(self):
        for aid in ['P', 'A1', 'A2', 'G1', 'G2', 'G3']:
            a, m = self.actors[aid], self.moves[aid]
            if not a.alive:
                continue
            if not m.points:
                continue
            while m.points and distance(a.position, m.points[0]) < .05:
                m.points.pop(0)
            if not m.points:
                continue
            target = m.points[0]
            delta = (target[0]-a.position[0], target[1]-a.position[1])
            length = max(distance(a.position, target), 1e-9)
            step = min(length, (2.6 if aid == 'P' else self.cfg['move_speed'])*.1)
            wanted = (a.position[0]+step*delta[0]/length, a.position[1]+step*delta[1]/length)
            dynamic = any(k != aid and x.alive and distance(wanted, x.position) < 2*self.cfg['capsule_radius'] for k, x in self.actors.items())
            if dynamic and hasattr(self.geo, 'description'):
                # Bounded local steering around actual nearby discs. No warping,
                # collision bypass or use of hidden enemy coordinates in policy.
                direction = math.atan2(delta[1], delta[0])
                candidates = []
                for offset in (math.pi/6, -math.pi/6, math.pi/3, -math.pi/3, math.pi/2, -math.pi/2):
                    point = (a.position[0]+step*math.cos(direction+offset), a.position[1]+step*math.sin(direction+offset))
                    if self.geo.blocked(a.position, point, self.cfg['capsule_radius']):
                        continue
                    def overlaps(other):
                        vx, vy = point[0]-a.position[0], point[1]-a.position[1]
                        t = max(0, min(1, ((other.position[0]-a.position[0])*vx+(other.position[1]-a.position[1])*vy)/max(step*step, 1e-9)))
                        closest = (a.position[0]+t*vx, a.position[1]+t*vy)
                        return distance(closest, other.position) < 2*self.cfg['capsule_radius']
                    if not any(k != aid and x.alive and overlaps(x) for k, x in self.actors.items()):
                        candidates.append(point)
                if candidates:
                    wanted = min(candidates, key=lambda p: distance(p, target))
                    dynamic = False
                    delta = (wanted[0]-a.position[0], wanted[1]-a.position[1])
            if not dynamic and not self.geo.blocked(a.position, wanted, self.cfg['capsule_radius']):
                a.position = wanted
                a.heading = math.atan2(delta[1], delta[0])
                m.travel += step
                if aid != 'P' and self.minds[aid].state in ('Support', 'Overwatch') and self.minds[aid].knowledge:
                    m.chase += step
                if distance(a.position, m.progress_position) > .1:
                    m.last_progress, m.progress_position = self.at, a.position
            elif dynamic:
                self.metrics['collision_waits'] += 1
            if self.at-m.last_progress >= self.cfg['stall_timeout'] and m.goal:
                m.points, m.retry, m.result = [], True, 'Stalled'
                self.event(aid, 'Stalled', 'actual no-progress timer; bounded retry')
            if m.goal and distance(a.position, m.goal) <= self._arrival_tolerance(aid):
                m.points, m.result = [], 'Arrived'
        for aid, m in self.minds.items():
            if not self.actors[aid].alive:
                continue
            if m.live_visible and m.memory and m.state in ('Engage', 'Support', 'Overwatch'):
                a = self.actors[aid]
                a.heading = math.atan2(m.memory.position[1]-a.position[1], m.memory.position[0]-a.position[0])
            elif m.state == 'Search' and not self.moves[aid].points:
                self.actors[aid].heading = (self.actors[aid].heading+.25) % (2*math.pi)
            elif not self.moves[aid].points and self.maneuvers.get(aid,{}).get('contact'):
                point = self.maneuvers[aid]['contact']['position']
                self.actors[aid].heading = math.atan2(point[1]-self.actors[aid].position[1],point[0]-self.actors[aid].position[0])
        for a in self.actors.values():
            if not self.geo.free(a.position):
                self.metrics['penetrations'] += 1

    def _actor_frame(self):
        return {k: {'position': list(a.position), 'heading': a.heading, 'team': a.team, 'alive': a.alive,
                    'health': a.health, 'ammo': a.ammo, 'squad': 'GER-1' if a.team == 'german' else 'ALLIED-1'}
                for k, a in self.actors.items()}

    def motion_sample(self):
        return {'at': self.at, 'actors': self._actor_frame()}

    def step(self, seconds=.5, motion_samples=None):
        count = round(seconds/.1)
        if not 1 <= count <= 5 or abs(count*.1-seconds) > 1e-6:
            raise ValueError('Step must be 0.1..0.5s in fixed 0.1s increments')
        for _ in range(count):
            if self.at >= self.duration:
                break
            self.ticks += 1
            if self.ticks % 2 == 0:
                self._sense()
            if self.ticks % 5 == 0:
                self._allow_fire = True
                try:
                    self._decide()
                finally:
                    self._allow_fire = False
            self._move()
            if motion_samples is not None:
                motion_samples.append(self.motion_sample())
        result = self.frame()
        self.history.append(result)
        self.history = self.history[-240:]
        return result

    def frame(self):
        return {'at': self.at, 'tick': self.ticks, 'revision': self.revision, 'duration': self.duration, 'preset': self.preset,
                'actors': self._actor_frame(),
                'minds': {k: {**serialized_mind(m), 'engage_permitted': self.actors[k].alive and m.live_visible and m.state in ('Engage', 'Support', 'Overwatch')} for k, m in self.minds.items()},
                'moves': {k: {'goal': m.goal, 'path': list(m.points), 'result': m.result, 'requests': m.requests, 'retries': m.retries, 'generation': m.generation,
                              'arrival_error': distance(self.actors[k].position, m.goal) if m.goal else None} for k, m in self.moves.items()},
                'reservations': self.reservations, 'scores': self.scores, 'events': self.events[-25:],
                'behavior_trees': self.behavior_trees, 'perception': self.perception, 'parameters': dict(self.parameters),
                'combat': {'shots': self.shots[-20:], 'incidents': self.incidents[-12:], 'checks': dict(self.combat_checks)},
                'maneuvers': deepcopy(self.maneuvers),
                'transitions': {k: m.transitions[-12:] for k, m in self.minds.items()},
                'metrics': {**self.metrics, 'path_queries': self.geo.query_count, 'max_query_nodes': self.geo.max_expansions},
                'finished': self.at >= self.duration, 'walls': self.walls, 'bounds': [self.geo.width, self.geo.height],
                'scene': self.geo.description() if hasattr(self.geo, 'description') else {'kind': 'exercise'}}

    def layout(self):
        return {'schema': 'paris.npc.live-layout.v2', 'preset': self.preset,
                'parameters': dict(self.parameters),
                'positions': {k: list(a.position) for k, a in self.actors.items()},
                'headings': {k: a.heading for k, a in self.actors.items()},
                'scene': self.geo.description() if hasattr(self.geo, 'description') else {'kind': 'exercise'}}
