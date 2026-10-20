"""Executable candidate rule oracle. No UE imports, world/Actor transform access or damage.

Functions receive immutable observations and explicit navigation results. The
replay does not reimplement these rules. Blueprint ports must match oracle vectors.
"""
from dataclasses import dataclass, field, asdict
import math


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


@dataclass(frozen=True)
class Observation:
    actor_id: str
    position: tuple
    at: float
    sense: str = "sight"
    uncertainty: float = 0.0
    source: str = "self"


@dataclass
class Mind:
    actor_id: str
    faction: str
    home: tuple
    state: str = "Guard"
    state_since: float = 0
    reason: str = "initial role"
    memory: Observation | None = None
    live_visible: bool = False
    last_sight: float = -100
    consumed_observation: float = -100
    search_deadline: float = -1
    search_started: float = -1
    search_index: int = 0
    search_goal: tuple | None = None
    search_origin: tuple | None = None
    generation: int = 1
    target_scores: list = field(default_factory=list)
    transitions: list = field(default_factory=list)
    knowledge: Observation | None = None

    def transition(self, state, at, reason):
        if self.state != state:
            self.transitions.append({"at": round(at, 3), "from": self.state,
                                     "to": state, "reason": reason})
            self.state_since = at
        self.state, self.reason = state, reason

    def invalidate(self, actor_id, at):
        if self.memory and self.memory.actor_id == actor_id:
            self.memory = None
            self.live_visible = False
            self.search_deadline = -1
            self.search_origin = None
            self.transition("Return" if self.faction == "german" else "Follow",
                            at, "registered target invalid; release intent")

    def receive(self, sightings, noises, at, own_position, cfg):
        """Only sensor outputs enter memory; noises cannot create visible targets."""
        scores = [{"id": x.actor_id, "position": x.position,
                   "score": round(1 - distance(own_position, x.position) / cfg['sight_range'], 6),
                   "reason": "live hostile + FOV + unoccluded sight"} for x in sightings]
        scores.sort(key=lambda x: (-x['score'], x['id']))
        self.target_scores = scores
        self.live_visible = bool(scores)
        if scores:
            best = scores[0]
            incumbent = next((x for x in scores if self.memory and x['id'] == self.memory.actor_id), None)
            if incumbent and best['score'] - incumbent['score'] < cfg['target_switch_margin']:
                best = incumbent
            self.memory = next(x for x in sightings if x.actor_id == best['id'])
            self.last_sight = at
            self.search_deadline = -1
            self.search_origin = None
        elif noises and (not self.memory or self.memory.sense != 'sight' or at - self.last_sight > cfg['memory_age']):
            noise = sorted(noises, key=lambda x: (-x.at, x.actor_id))[0]
            # An active episode has a frozen origin/deadline; repeated noises do
            # not move its search goal or reset its lifetime.
            if self.search_deadline < 0:
                self.memory = noise
                if self.state in ('Guard', 'Return'):
                    self.transition('Alert', at, 'audible event with uncertainty; no live lock')

    def enemy_intent(self, at, position, cfg):
        if self.memory and self.memory.sense == 'hearing' and self.state == 'Alert' and at-self.state_since < cfg['alert_dwell']-1e-8:
            return None
        if self.live_visible and self.memory:
            if self.state in ('Guard', 'Return'):
                self.transition('Alert', at, 'fresh hostile sight; alert dwell')
            if self.state == 'Alert' and at - self.state_since < cfg['alert_dwell'] - 1e-8:
                return None
            self.transition('Engage', at, 'current sight; original action adapter required')
            return None  # Standing combat intent; no new fire/ammo implementation.
        if self.memory and self.memory.sense == 'sight' and at - self.last_sight < cfg['loss_grace'] - 1e-8:
            self.reason = 'sight loss grace; no fire permission'
            return None
        if self.memory and self.memory.at > self.consumed_observation:
            if self.search_deadline < 0:
                self.search_started = at
                self.search_deadline = at + cfg['search_duration']
                self.search_index = 0
                self.search_origin = self.memory.position
                self.search_goal = self.search_origin
                self.transition('Investigate', at, 'frozen observed/event location; finite episode')
            if at >= self.search_deadline - 1e-8 or self.search_index >= cfg['search_points']:
                self.consumed_observation = self.memory.at
                self.search_deadline = -1
                self.transition('Return', at, 'fixed deadline or finite points exhausted')
                return self.home
            if self.state == 'Investigate':
                if distance(position, self.search_origin) <= cfg['arrival_radius'] or at - self.search_started >= 2:
                    self.transition('Search', at, 'check finite offsets around frozen origin')
                else:
                    return self.search_origin
            if self.state == 'Search':
                offsets = ((0, 1.5), (1.5, 0), (0, -1.5), (-1.5, 0))
                dx, dy = offsets[self.search_index]
                self.search_goal = (self.search_origin[0] + dx, self.search_origin[1] + dy)
                if distance(position, self.search_goal) <= cfg['arrival_radius']:
                    self.search_index += 1
                return self.search_goal
        if self.memory and at - self.memory.at > cfg['memory_age']:
            self.memory = None
        if distance(position, self.home) <= cfg['arrival_radius']:
            self.transition('Guard', at, 'home reached; no valid current observation')
            return None
        self.transition('Return', at, 'memory/search expired; return measured role anchor')
        return self.home


def cover_score(role, position, player, observed_threat, path_length, blocks_threat, cfg):
    """Features use observed threat position only. Navigation gates are separate."""
    features = {'cover': float(blocks_threat), 'lane': float(not blocks_threat),
                'range': max(0, 1 - abs(distance(position, observed_threat) - 7) / 14),
                'travel': max(0, 1 - path_length / 30),
                'player': max(0, 1 - distance(position, player) / cfg['ally_player_envelope'])}
    weights = cfg['support_weights' if role == 'Support' else 'overwatch_weights']
    contributions = {k: round(v * features[k], 6) for k, v in weights.items()}
    return sum(contributions.values()), features, contributions


def joint_assignment(rows_by_agent, current, at, last_assignment, cfg):
    """Bounded two-NPC pair comparison, deterministic tie and incumbent hysteresis."""
    ids = sorted(rows_by_agent)
    if len(ids) != 2:
        return {}, 'no two live eligible allies', 0
    a, b = ids
    pairs = []
    comparisons = 0
    for x in rows_by_agent[a][:cfg['candidate_limit']]:
        for y in rows_by_agent[b][:cfg['candidate_limit']]:
            comparisons += 1
            if x['valid'] and y['valid'] and distance(x['position'], y['position']) >= cfg['reservation_separation']:
                pairs.append((x['score'] + y['score'], x['id'], y['id'], {a: x, b: y}))
    if not pairs:
        return {}, 'no complete reachable separated pair; wait', comparisons
    pairs.sort(key=lambda p: (-p[0], p[1], p[2]))
    best = pairs[0]
    incumbent = next((p for p in pairs if all(current.get(k) == v['id'] for k, v in p[3].items())), None)
    if incumbent and (at - last_assignment < cfg['assignment_dwell'] or best[0] - incumbent[0] < cfg['goal_switch_margin']):
        return incumbent[3], 'retain valid occupied reservation: dwell/score margin', comparisons
    return best[3], 'maximum gated two-role utility; stable ID tie break', comparisons


def callback_matches(generation, request_id, current_generation, current_request_id):
    return generation == current_generation and request_id == current_request_id


def serialized_mind(mind):
    row = asdict(mind)
    row.pop('transitions')
    return row
