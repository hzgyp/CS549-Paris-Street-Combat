"""Real branch execution, movement failures, bounded memory and historical traces."""
import copy
from npc_policy_evidence import policy_evidence
import json
import pytest
from app.npc_behavior_tree import definitions, tick_tree
from app.npc_engine import CFG
from npc_quiet_fixture import World
from app.npc_oracle import Observation
from app.npc_raster import RasterGeometry
from test_npc_simulation import advance, clients


def status(w, aid, node):
    return w.behavior_trees[aid]['nodes'][node]['status']


def test_follow_and_support_are_executed_branches_with_actual_arrival():
    w = World('follow')
    assert status(w, 'A1', 'travel.move') == 'Running'
    assert status(w, 'A1', 'role.reserve') == 'Skipped'
    advance(w, 4)
    assert status(w, 'A1', 'travel.move') == 'Success'
    assert w.moves['A1'].result == 'Arrived'
    w = World('support')
    assert status(w, 'A1', 'role.reserve') == 'Success'
    assert status(w, 'A2', 'role.reserve') == 'Success'
    assert w.behavior_trees['A2']['nodes']['role.reserve']['detail']['role'] == 'Overwatch'
    assert status(w, 'A1', 'follow.compute') == 'Skipped'


def test_failed_move_does_not_claim_arrival_or_select_another_role():
    w = World('support')
    # Preserve the assigned intent while its already-issued movement fails.
    w.moves['A1'].result = 'Unreachable'
    w._decide()
    assert status(w, 'A1', 'travel.move') == 'Failure'
    assert status(w, 'A1', 'travel.intent') == 'Success'
    assert status(w, 'A1', 'follow.compute') == 'Skipped'
    assert w.moves['A1'].result != 'Arrived'
    w.moves['A1'].exhausted = True
    w.moves['A1'].result = 'WaitingBudgetExhausted'
    w._decide()
    assert status(w, 'A1', 'budget.wait') == 'Running'
    assert status(w, 'A1', 'travel') == 'Skipped'


def test_no_formation_path_waits_and_cancels_stale_movement():
    w = World('follow')
    w.geo.path = lambda start, goal: {'status': 'Unreachable', 'length': 0, 'points': []}
    w._decide()
    assert status(w, 'A1', 'travel.goal') == 'Failure'
    assert status(w, 'A1', 'follow.wait') == 'Running'
    assert w.moves['A1'].goal is None and not w.moves['A1'].points


def test_german_actual_sight_grace_search_and_return_branches():
    w = World('search')
    assert status(w, 'G1', 'alert.update') == 'Success'
    advance(w, 1)
    assert status(w, 'G1', 'engage') == 'Success'
    w.command('place', 'P', [13, 10])
    assert status(w, 'G1', 'grace.update') == 'Success'
    advance(w, 1)
    assert status(w, 'G1', 'memory.update') == 'Success'
    assert status(w, 'G1', 'travel.move') == 'Running'
    advance(w, 3)
    assert w.minds['G1'].state == 'Search'
    advance(w, 8)
    assert status(w, 'G1', 'return') == 'Success'
    assert status(w, 'G1', 'guard.restore') == 'Running'
    assert w.minds['G1'].state == 'Guard'


def test_hearing_dwell_is_a_real_separate_branch():
    w = World('follow')
    m = w.minds['G2']
    m.memory = Observation('P', (24, 3), w.at, 'hearing')
    m.transition('Alert', w.at, 'test noise')
    w._decide()
    assert status(w, 'G2', 'hearing.update') == 'Success'
    assert status(w, 'G2', 'sight') == 'Skipped'
    assert not m.live_visible


def test_history_is_frozen_and_hidden_player_counterfactual_preserves_trace():
    a, b = World('search'), World('search')
    advance(a, 1); advance(b, 1)
    old = a.frame(); original = copy.deepcopy(old)
    a.command('place', 'P', [13, 10]); b.command('place', 'P', [11, 10])
    for _ in range(12):
        fa, fb = a.step(), b.step()
        for gid in ('G1', 'G2', 'G3'):
            assert policy_evidence(fa['behavior_trees'][gid]) == policy_evidence(fb['behavior_trees'][gid])
            assert fa['minds'][gid] == fb['minds'][gid] and fa['moves'][gid] == fb['moves'][gid]
            assert 'player_position' not in fa['behavior_trees'][gid]['blackboard']
    assert old == original
    json.dumps(a.frame())


def test_raster_search_projection_records_real_bounded_candidates():
    w = World('search', geometry=RasterGeometry(dict(CFG, path_node_budget=12000)))
    advance(w, 1); w.command('place', 'P', [92.125, 95.125]); advance(w, 4)
    assert status(w, 'G1', 'search.project') == 'Success'
    detail = w.behavior_trees['G1']['nodes']['search.project']['detail']
    assert detail['candidate_limit'] == 25
    assert w.minds['G1'].search_origin == (106.125, 99.125)
    assert detail['deadline'] == w.minds['G1'].search_deadline


def test_definitions_are_finite_unique_and_execution_is_bounded():
    trees = definitions()
    for faction, tree in trees.items():
        ids = [n['id'] for n in tree['nodes']]
        assert len(ids) == len(set(ids)) == tree['max_node_visits'] < 60
        assert all(c in ids for n in tree['nodes'] for c in n['children'])
        trace = tick_tree(faction, 0, lambda op: (False, {}), lambda op: ('Running', {}))
        assert len(trace['visited']) == len(set(trace['visited'])) <= len(ids)
    trees['allied']['nodes'].clear()
    assert definitions()['allied']['nodes']


def test_old_arrival_is_not_success_for_a_new_deferred_goal():
    w = World('follow'); advance(w, 4)
    w.moves['A1'].last_attempt = w.at
    w.actors['P'].position = (11, 11)
    w._decide()
    assert w.moves['A1'].result == 'Arrived'
    assert status(w, 'A1', 'travel.move') == 'Running'


def test_api_serves_the_executed_definitions_and_historical_traces(clients):
    c, h = clients[0]
    assert c.get('/api/v1/npc-simulation').json()['behavior_tree_definitions'] == definitions()
    data = c.post('/api/v1/npc-simulation/sessions', json={'scene': 'exercise'}, headers=h).json()
    url = '/api/v1/npc-simulation/sessions/'+data['session_id']
    prior = copy.deepcopy(data['frame']['behavior_trees'])
    reply = c.post(url, json={'revision': 0, 'request_id': 'tree_http_test', 'operation': 'step', 'seconds': .1}, headers=h).json()
    assert reply['frame']['at'] == .1
    assert reply['frame']['behavior_trees'] == prior
    assert c.get(url).json()['history'][0]['behavior_trees'] == prior
