"""Actual sensor gates, first-hit parity, immutable decision evidence and no policy change."""
import copy
import math
import random
import pytest
from app.npc_engine import CFG, World
from app.npc_geometry import Geometry
from app.npc_raster import RasterGeometry
from app.npc_sight import evaluate_sight, rectangle_ray


def sample(target, heading=0, **cfg):
    calls = []
    def ray(a, b):
        calls.append((a, b))
        return {'blocked': False, 'point': None, 'cell': None}
    report = evaluate_sight((0, 0), heading, target, dict(sight_range=14, sight_fov_degrees=120, **cfg), ray)
    return report, calls


def test_ordered_gates_do_not_claim_untested_occlusion():
    far, calls = sample((15, 0))
    assert far['failure'] == 'Distance' and not calls and far['ray'] is None
    assert far['gates'] == dict(distance='Failure', angle='Skipped', occlusion='Skipped')
    behind, calls = sample((-2, 0))
    assert behind['failure'] == 'Angle' and not calls
    assert behind['gates'] == dict(distance='Success', angle='Failure', occlusion='Skipped')
    clear, calls = sample((14, 0))
    assert clear['visible'] and len(calls) == 1


def test_fixture_first_hit_is_nearest_not_wall_order():
    ray = rectangle_ray((0, 1), (12, 1), [(8, 0, 1, 2), (3, 0, 1, 2)])
    assert ray['point'] == [3, 1] and ray['wall_index'] == 1
    assert rectangle_ray((0, 3), (12, 3), [(3, 0, 1, 2)])['blocked'] is False


@pytest.mark.parametrize('target,heading', [((14, 0), 0), ((0, 0), 0), ((0, 2), math.pi/6), ((-2, 0), math.pi), ((2, 2), 0)])
def test_exact_geometric_threshold_matches_existing_see(target, heading):
    geo = Geometry([], CFG)
    assert geo.sight_evidence((0, 0), heading, target)['visible'] == geo.see((0, 0), heading, target)


def fake_raster():
    geo = RasterGeometry.__new__(RasterGeometry)
    geo.data = {'sight': bytearray([1])*(720*960)}
    return geo


@pytest.mark.parametrize('a,b,blocked,point', [
    ((.125, .125), (1.125, .125), (2, 0), (.5, .125)),
    ((1.125, .125), (.125, .125), (2, 0), (.75, .125)),
    ((.125, .125), (.125, 1.125), (0, 2), (.125, .5)),
    ((.125, 1.125), (.125, .125), (0, 2), (.125, .75)),
    ((.125, .125), (.625, .625), (1, 0), (.25, .25)),
    ((.125, .125), (.625, .625), (0, 1), (.25, .25)),
])
def test_exact_first_cell_and_entry_including_supercover_corner(a, b, blocked, point):
    geo = fake_raster(); x, y = blocked; geo.data['sight'][y*720+x] = 0
    hit = geo.sight_ray(a, b)
    assert hit['blocked'] == geo.blocked(a, b) is True
    assert hit['cell'] == list(blocked) and hit['point'] == list(point)


def test_raster_random_and_boundary_parity():
    geo = fake_raster(); rng = random.Random(20261018)
    for _ in range(2500):
        geo.data['sight'][rng.randrange(720*960)] = 0
    rays = [((0, 0), (0, 0)), ((180, 1), (2, 1)), ((-.1, 0), (0, 0)),
            ((.25, .25), (.75, .75)), ((.75, .75), (.25, .25))]
    rays += [((rng.random()*180, rng.random()*240), (rng.random()*180, rng.random()*240)) for _ in range(600)]
    for a, b in rays:
        assert geo.sight_ray(a, b)['blocked'] == geo.blocked(a, b)


def test_actual_map_sensor_parity():
    geo = RasterGeometry(CFG); rng = random.Random(18)
    for _ in range(500):
        a, b = (rng.uniform(85, 120), rng.uniform(80, 110)), (rng.uniform(85, 120), rng.uniform(80, 110))
        heading = rng.uniform(-math.pi, math.pi)
        assert geo.sight_evidence(a, heading, b)['visible'] == geo.see(a, heading, b)
        assert geo.sight_ray(a, b)['blocked'] == geo.blocked(a, b)


def test_failed_player_sight_never_supplies_private_memory_and_any_hostile_still_passes():
    w = World('search'); w.actors['P'].position = (13, 10)
    w.actors['A1'].position = (19, 10); w._sense(); w._decide()
    sight = w.perception['G1']
    assert not sight['visible'] and sight['failure'] == 'Occlusion'
    assert 'P' not in sight['visible_hostiles'] and 'A1' in sight['visible_hostiles']
    assert w.minds['G1'].memory.actor_id == 'A1'
    trace = w.frame()['behavior_trees']['G1']
    visible = next(n for n in trace['nodes'].values() if n['detail'].get('player_sight'))
    assert visible['status'] == 'Success' and visible['detail']['player_sight'] == sight


def test_decision_sample_is_immutable_and_precedes_motion():
    w = World('search'); before = w.frame(); frozen = copy.deepcopy(before)
    w.command('walk', 'P', (23, 12)); w.step(.5)
    assert before == frozen
    trace = w.behavior_trees['G1']; sight = trace['blackboard']['player_sight']
    assert sight['at'] <= trace['at'] <= w.at
    assert sight['origin'] != list(w.actors['G1'].position) or sight['target_position'] != list(w.actors['P'].position)
    w.actors['P'].alive = False; w._sense(); w._decide()
    assert not w.perception and w.behavior_trees['G1']['blackboard']['player_sight'] is None

