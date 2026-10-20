"""Live effects, retained history and transactional parameter boundaries."""
import copy
from npc_policy_evidence import policy_evidence
import math
import pytest
from app.npc_engine import CFG
from npc_quiet_fixture import World
from app.npc_geometry import Geometry
from app.npc_raster import RasterGeometry
from app.npc_parameters import normalize, parameter_schema
from app.npc_behavior_tree import definitions
from app.npc_oracle import distance
from test_npc_simulation import advance, clients


def test_follow_distance_changes_actual_path_and_arrival_without_teleport():
    w = World(); advance(w, 4)
    before = w.frame(); budget = w.moves['A1'].requests
    w.configure({'follow_distance': 6})
    assert w.at == before['at'] and w.frame()['actors'] == before['actors']
    assert w.moves['A1'].requests >= budget
    assert w.metrics['player_commands'] == before['metrics']['player_commands']
    f = advance(w, 5)
    for aid, y in [('A1', 9.8), ('A2', 12.2)]:
        assert distance(w.actors[aid].position, (2, y)) <= CFG['arrival_radius']
        assert f['moves'][aid]['result'] == 'Arrived'
        assert f['behavior_trees'][aid]['nodes']['follow.compute']['detail']['follow_distance'] == 6


def test_german_range_changes_sight_immediately_allied_sensors_unchanged():
    w = World('support'); before = [w.minds[a].live_visible for a in ('A1', 'A2')]
    w.configure({'german_sight_range': 2})
    assert not w.minds['G1'].live_visible
    assert [w.minds[a].live_visible for a in ('A1', 'A2')] == before
    w.configure({'german_sight_range': 14})
    assert w.minds['G1'].live_visible
    assert w.minds['G1'].memory.sense == 'sight'


def test_german_fov_changes_actual_condition_not_just_overlay():
    layout = {'P': (8, 7), 'A1': (25, 7), 'A2': (25, 13), 'G1': (13, 11), 'G2': (28, 3), 'G3': (28, 19)}
    w = World(layout=layout, parameters={'german_sight_fov_degrees': 30})
    assert not w.minds['G1'].live_visible
    w.configure({'german_sight_fov_degrees': 120})
    assert w.minds['G1'].live_visible and w.minds['G1'].memory.actor_id == 'P'
    assert w.behavior_trees['G1']['nodes']['sight.check']['status'] == 'Success'


@pytest.mark.parametrize('raster', [False, True])
def test_wider_vision_still_respects_actual_obstruction(raster):
    if raster:
        geo = RasterGeometry(dict(CFG, path_node_budget=12000))
        # Existing measured fixture across a blocked patch, found by the preset.
        w = World('search', geometry=geo)
        origin = w.actors['G1'].position
        targets = [(origin[0]+dx, origin[1]+dy) for dx in range(-10, 11, 2) for dy in range(-10, 11, 2)]
        target = next(p for p in targets if distance(p, origin)>1 and geo.blocked(origin, p))
    else:
        geo = Geometry([[15, 6, 1, 10]], CFG); origin, target = (21, 10), (13, 10)
    heading = math.atan2(target[1]-origin[1], target[0]-origin[0])
    assert not geo.see(origin, heading, target, {**CFG, 'sight_range': 40, 'sight_fov_degrees': 180})


def searching():
    w = World('search'); advance(w, 1); w.command('place', 'P', [13, 10]); advance(w, 2)
    assert w.minds['G1'].search_deadline >= 0
    return w


def test_active_search_duration_uses_original_start_and_retains_memory():
    w = searching(); m = w.minds['G1']; origin, started, memory = m.search_origin, m.search_started, m.memory
    at, positions = w.at, w.frame()['actors']
    w.configure({'search_duration': 20})
    assert m.search_deadline == started + 20 and m.search_started == started
    assert m.memory == memory and m.search_origin == origin and w.at == at
    assert w.frame()['actors'] == positions
    advance(w, 1)
    w.configure({'search_duration': 20})
    assert m.search_deadline == started + 20
    w.configure({'search_duration': 1})
    assert m.state == 'Return' and m.search_deadline == -1
    assert m.consumed_observation == memory.at and m.search_origin == origin
    w.configure({'search_duration': 30})
    assert m.search_deadline == -1  # Consumed episodes cannot be resurrected by tuning.


def test_grace_is_executed_threshold_and_hidden_coordinates_remain_private():
    a, b = World('search'), World('search')
    for w, pos in [(a, [13, 10]), (b, [11, 10])]:
        advance(w, 1); w.command('place', 'P', pos)
        w.configure({'loss_grace': 0, 'search_duration': 12})
        assert w.minds['G1'].state == 'Investigate'
    for _ in range(8):
        a.step(); b.step()
        assert policy_evidence(a.behavior_trees['G1']) == policy_evidence(b.behavior_trees['G1'])
        assert a.minds['G1'] == b.minds['G1'] and a.moves['G1'] == b.moves['G1']
        assert a.actors['G1'] == b.actors['G1']


def test_history_and_layout_settings_are_independent_snapshots():
    w = searching(); saved = copy.deepcopy(w.step()); layout = w.layout()
    w.configure({'search_duration': 15, 'follow_distance': 5})
    assert w.history[-1] == saved and saved['parameters']['search_duration'] == 6
    assert saved['behavior_trees']['G1']['parameters']['search_duration'] == 6
    assert layout['parameters']['follow_distance'] == 3
    restored = World(layout=layout['positions'], headings=layout['headings'], parameters=layout['parameters'])
    assert restored.parameters == saved['parameters']
    from app.npc_engine import World as DefaultWorld
    assert DefaultWorld().parameters == normalize()  # Old layouts need no new key.


@pytest.mark.parametrize('patch', [{'follow_distance': 0}, {'german_sight_range': 41}, {'german_sight_fov_degrees': 181},
                                  {'search_duration': float('nan')}, {'loss_grace': True}, {'search_duration': '9'}, {'unknown': 1}])
def test_invalid_patch_preserves_entire_world(patch):
    w = searching(); before = copy.deepcopy(w.__dict__)
    with pytest.raises(ValueError): w.configure(patch)
    assert w.frame() == WorldFrame(before)
    assert w.history == before['history'] and w.parameters == before['parameters']


def WorldFrame(state):
    w = object.__new__(World); w.__dict__ = state
    return w.frame()


def test_tuning_cannot_rearm_exhausted_budgets():
    w = World(); w.moves['A1'].exhausted = True; w.moves['A1'].requests = w.request_budget
    w.configure({'follow_distance': 7})
    assert w.moves['A1'].exhausted and w.moves['A1'].requests == w.request_budget
    assert w.behavior_trees['A1']['nodes']['budget.wait']['status'] == 'Running'


def test_api_parameter_patch_cas_owner_history_and_idempotency(clients):
    (c, h), (other, oh) = clients
    descriptor = c.get('/api/v1/npc-simulation').json()
    assert descriptor['parameter_schema'] == parameter_schema()
    r = c.post('/api/v1/npc-simulation/sessions', json={'scene': 'exercise', 'parameters': {'follow_distance': 4}}, headers=h).json()
    url = '/api/v1/npc-simulation/sessions/' + r['session_id']
    payload = {'operation': 'configure', 'revision': 0, 'request_id': 'parameters_123', 'parameters': {'search_duration': 12}}
    assert other.post(url, json=payload, headers=oh).status_code == 404
    assert c.post(url, json=payload).status_code == 403
    result = c.post(url, json=payload, headers=h)
    assert result.status_code == 200
    f = result.json()['frame']; assert f['parameters']['follow_distance'] == 4 and f['parameters']['search_duration'] == 12
    assert f['at'] == 0 and f['actors'] == r['frame']['actors'] and f['revision'] == 1
    assert c.post(url, json=payload, headers=h).json() == result.json()
    assert c.get(url).json()['history'][-1] == f
    assert c.post(url, json={**payload, 'request_id': 'stale_parameter'}, headers=h).status_code == 409
    for p in ({'search_duration': 31}, {'unknown': 1}, {'follow_distance': True}, {'follow_distance': '5'}):
        bad = {**payload, 'revision': 1, 'request_id': 'bad_parameter', 'parameters': p}
        assert c.post(url, json=bad, headers=h).status_code == 422
        assert c.get(url).json()['frame'] == f
    assert c.post(url, json={**payload, 'parameters': {'search_duration': 13}}, headers=h).status_code == 409
    assert c.post('/api/v1/npc-simulation/sessions', json={'parameters': {'search_duration': 31}}, headers=h).status_code == 422


def test_node_parameter_bindings_are_real_known_thresholds():
    keys = {f['key'] for f in parameter_schema()}
    bound = {k for tree in definitions().values() for node in tree['nodes'] for k in node['parameters']}
    assert bound == keys


def test_initial_tuning_controls_new_search_and_finished_episode_stays_finite():
    w = World('search', parameters={'search_duration': 12, 'loss_grace': 0})
    advance(w, 1); w.command('place', 'P', [13, 10])
    mind = w.minds['G1']
    assert mind.search_deadline == mind.search_started + 12
    advance(w, 120); before = copy.deepcopy(w.frame())
    with pytest.raises(ValueError): w.configure({'search_duration': 6})
    assert w.frame() == before and w.at == 120
