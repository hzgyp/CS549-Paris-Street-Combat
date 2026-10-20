"""Observable tactical outcomes, occluded reports and finite 2D combat."""
import copy
import math
import pytest
from app.npc_engine import World as CoverWorld, CFG
from app.npc_geometry import Geometry
from app.npc_oracle import distance
from app.npc_behavior_tree import definitions


class World(CoverWorld):
    """Isolate the retained hit/fire/basic-role contract from cover coordination."""
    def __init__(self, *args, parameters=None, **kwargs):
        super().__init__(*args, parameters={'tactical_coordination': 0, **(parameters or {})}, **kwargs)


def advance(w, seconds):
    for _ in range(round(seconds/.5)):
        w.step()
    return w.frame()


def ambush(damage=20):
    w = World('follow', layout={'P': (20, 11), 'A1': (3, 3), 'A2': (3, 19),
                               'G1': (24, 11), 'G2': (12, 8), 'G3': (12, 14)},
              headings={'P': 0, 'A1': 0, 'A2': 0, 'G1': math.pi, 'G2': 0, 'G3': 0},
              parameters={'search_duration': 30, 'combat_damage': damage})
    for aid in w.actors:
        if aid != 'P':
            w.actors[aid].ammo = 0  # isolate report/navigation from follow-on combat
    return w


def test_paused_placement_and_parameter_edits_do_not_apply_autofire():
    w = World('support')
    w.configure({'scout_distance': 6})
    w.command('rotate', 'P', heading=.1)
    assert not w.shots and all(a.health == 100 and a.ammo == 30 for a in w.actors.values())
    w.step()
    assert any(s['shooter'].startswith('A') and s['damage_applied'] > 0 for s in w.shots)


@pytest.mark.parametrize('mode,roles', [(0, ('Follow', 'Follow')), (1, ('Cover', 'Cover')), (2, ('Scout', 'Cover'))])
def test_follow_cover_and_scout_admit_distinct_real_goals(mode, roles):
    w = World('follow', parameters={'allied_mode': mode, 'combat_damage': 0})
    assert tuple(w.minds[a].state for a in ('A1', 'A2')) == roles
    goals = [w.reservations[a]['position'] for a in ('A1', 'A2')]
    assert distance(*goals) >= CFG['reservation_separation']
    assert all(w.geo.free(p) for p in goals)
    if mode == 2:
        assert goals[0][0] > w.actors['P'].position[0]
    if mode == 1:
        assert goals[0][1] < 11 < goals[1][1]
    old = w.actors['A1'].position
    advance(w, 2)
    assert distance(old, w.actors['A1'].position) > .1
    assert not w.metrics['penetrations']


def test_scout_reorients_with_friendly_player_order_and_is_leashed():
    w = World('follow', parameters={'combat_damage': 0})
    w.command('rotate', 'P', heading=math.pi/2)
    goal = w.plans['A1']['desired_slot']
    assert goal[1] > w.actors['P'].position[1]
    assert distance(w.reservations['A1']['position'], w.actors['P'].position) <= 9


def test_single_survivor_still_repositions_and_fires_while_moving():
    w = World('support')
    w.actors['A2'].alive = False
    w.actors['A2'].health = 0
    w._decide()
    assert w.minds['A1'].state == 'Support'
    assert w.behavior_trees['A1']['nodes']['role.reserve']['status'] == 'Success'
    w.step()
    assert any(s['shooter'] == 'A1' for s in w.shots)
    assert w.actors['G1'].health < 100
    assert w.moves['A2'].points == [] and w.minds['A2'].state == 'Dead'


def test_hit_report_crosses_wall_without_visual_lock_and_spreads_approaches():
    w = ambush()
    assert not w.minds['G2'].live_visible and not w.minds['G3'].live_visible
    before = {g: w.actors[g].position for g in ('G2', 'G3')}
    w.command('fire', 'G1')
    goals = []
    for gid in ('G2', 'G3'):
        tree = w.behavior_trees[gid]
        assert tree['nodes']['squad.check']['status'] == 'Success'
        assert tree['nodes']['squad.update']['status'] == 'Success'
        assert w.minds[gid].state == 'Investigate' and not w.minds[gid].live_visible
        assert tree['blackboard']['observation']['sense'] == 'report'
        assert tree['blackboard']['squad_report']['victim'] == 'G1'
        assert not w._fire_check(gid)['permitted']
        goals.append(w.moves[gid].goal)
    assert distance(*goals) >= 1.6
    advance(w, 1)
    assert all(distance(w.actors[g].position, before[g]) > .5 for g in before)
    assert not w.metrics['penetrations']


def test_casualty_notifies_living_teammates_and_dead_actor_cannot_move_or_fire():
    w = ambush(50)
    w.command('fire', 'G1')
    advance(w, 1.5)
    w.command('fire', 'G1')
    assert not w.actors['G1'].alive and w.actors['G1'].health == 0
    assert all(w.squad_alerts[g]['kind'] == 'casualty' for g in ('G2', 'G3'))
    assert not w.moves['G1'].points and w.moves['G1'].result == 'Dead'
    old = w.actors['G1'].position
    advance(w, 1)
    assert w.actors['G1'].position == old and w.minds['G1'].state == 'Dead'
    with pytest.raises(ValueError, match='casualty'):
        w.command('place', 'G1', (25, 11))


def test_occluded_counterfactual_does_not_follow_hidden_updated_player():
    a, b = ambush(), ambush()
    for w in (a, b):
        w.command('fire', 'G1')
    a.command('place', 'P', (20, 10))
    b.command('place', 'P', (22, 10))
    for _ in range(3):
        a.step(); b.step()
        for gid in ('G2', 'G3'):
            assert not a.minds[gid].live_visible and not b.minds[gid].live_visible
            assert a.minds[gid].memory == b.minds[gid].memory
            assert a.moves[gid].goal == b.moves[gid].goal
            assert a.actors[gid].position == b.actors[gid].position
            assert a.minds[gid].search_deadline == b.minds[gid].search_deadline


def test_repeated_hits_and_casualty_do_not_extend_current_search_deadline():
    w = ambush(50)
    w.command('fire', 'G1')
    deadline = w.minds['G2'].search_deadline
    advance(w, 1.5); w.command('fire', 'G1')
    assert w.minds['G2'].search_deadline == deadline
    assert w.minds['G2'].search_started == 0


def test_unseen_source_is_coarse_event_estimate_not_identified_target():
    w = ambush()
    w.command('rotate', 'G1', heading=0)
    w.command('fire', 'G1')
    notice = w.squad_alerts['G2']
    assert notice['basis'] == 'coarse_gunfire_bearing' and notice['target_id'] == 'unknown'
    assert notice['uncertainty'] == 1.5
    origin = tuple(notice['position'])
    w.command('place', 'P', (20, 12))
    assert tuple(w.minds['G2'].search_origin) == origin


def test_report_search_expires_even_with_repeated_old_reports():
    w = ambush()
    w.configure({'search_duration': 2})
    w.command('fire', 'G1')
    for aid in ('A1', 'A2'):
        w.actors[aid].alive = False
    w.command('place', 'P', (30, 11))
    advance(w, 3)
    assert w.minds['G2'].search_deadline < 0 and w.minds['G2'].state in ('Return', 'Guard')
    assert w.minds['G2'].consumed_observation == 0


@pytest.mark.parametrize('gate', ['wall', 'range', 'body', 'cooldown', 'ammo'])
def test_rejected_shots_do_not_change_health_or_ammo(gate):
    w = ambush()
    if gate == 'wall':
        w.command('place', 'P', (12, 11))
    elif gate == 'range':
        w.command('place', 'P', (2, 11))
    elif gate == 'body':
        w.command('place', 'A1', (22, 11))
    elif gate == 'cooldown':
        w.command('fire', 'G1')
    else:
        w.actors['P'].ammo = 0
    before = (w.actors['P'].ammo, w.actors['G1'].health)
    w.command('fire', 'G1')
    assert (w.actors['P'].ammo, w.actors['G1'].health) == before
    assert not w.combat_checks['P']['permitted']


def test_own_reacquisition_overrides_report_and_can_engage():
    w = ambush()
    w.command('fire', 'G1')
    w.command('place', 'P', (12, 3))
    w.command('rotate', 'G2', heading=-math.pi/2)
    advance(w, 1)
    assert w.minds['G2'].live_visible and w.minds['G2'].state == 'Engage'
    assert w.minds['G2'].search_deadline < 0
    assert w.behavior_trees['G2']['nodes']['squad.check']['status'] == 'Skipped'


def test_frames_do_not_mutate_and_tree_has_no_unreachable_decoration_nodes():
    w = ambush(); w.command('fire', 'G1')
    old = w.frame(); frozen = copy.deepcopy(old)
    advance(w, 3)
    assert old == frozen
    for tree in definitions().values():
        by_id = {n['id']: n for n in tree['nodes']}
        def reach(nid):
            return {nid}.union(*(reach(c) for c in by_id[nid]['children']))
        assert len(by_id) == len(tree['nodes'])
        assert reach(tree['root']) == set(by_id)


def test_raster_squad_preset_exposes_two_occluded_living_squadmates():
    from app.npc_raster import RasterGeometry
    w = World('squad', geometry=RasterGeometry(dict(CFG, path_node_budget=12000)))
    assert all(w.perception[g]['failure'] == 'Occlusion' for g in ('G2', 'G3'))
    w.command('fire', 'G1')
    assert all(w.behavior_trees[g]['nodes']['squad.update']['status'] == 'Success' for g in ('G2', 'G3'))


def test_sector_search_physically_advances_points_and_preserves_deadline():
    w = ambush()
    w.command('fire', 'G1')
    deadline = w.minds['G2'].search_deadline
    for aid in ('P', 'A1', 'A2'):
        w.actors[aid].alive = False  # no new sensory contacts during finite search
    observed = set()
    for _ in range(40):
        w.step()
        mind = w.minds['G2']
        if mind.state == 'Search':
            observed.add(mind.search_index)
            assert mind.search_deadline == deadline
    assert len(observed) >= 2


def test_npc_casualty_tree_updates_in_the_same_frame_as_later_enemy_shot():
    w = World('support', parameters={'combat_damage': 50})
    w.actors['A1'].health = 1
    w.step()
    assert not w.actors['A1'].alive
    assert w.behavior_trees['A1']['nodes']['dead.hold']['status'] == 'Running'
    assert not w.behavior_trees['A1']['blackboard']['combat']['permitted']
