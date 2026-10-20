"""Physical cover/bound/contact outcomes; no per-frame pose driver."""
from copy import deepcopy
import math
import pytest
from app.npc_engine import World, CFG
from app.npc_geometry import Geometry
from app.npc_raster import RasterGeometry
from app.npc_oracle import distance


def bound_world():
    geo=Geometry([[12.5,6,1,4],[15,12,1,4],[18.5,7,1,3]],dict(CFG),width=60,height=30)
    positions={'P':(10,11),'A1':(8,9),'A2':(8,13),'G1':(50,2),'G2':(50,11),'G3':(50,20)}
    return World('follow',layout=positions,geometry=geo,parameters={'combat_damage':0,'search_duration':30})


def squad_world():
    w=World('squad',parameters={'combat_damage':0,'search_duration':30})
    for a in w.actors.values():a.ammo=0
    return w


def test_cover_admission_proves_real_obstruction_peek_and_capsule_connector():
    w=bound_world()
    assert not w.bound['failed']
    for aid,pair in w.bound['legs'].items():
        assert w.geo.blocked(pair['hide'],pair['threat'])
        assert not w.geo.blocked(pair['peek'],pair['threat'])
        assert not w.geo.blocked(pair['hide'],pair['peek'],CFG['capsule_radius'])
        assert w.geo.free(pair['hide']) and w.geo.free(pair['peek'])
        assert w.geo.path(w.actors[aid].position,pair['hide'])['status']=='Complete'
        assert pair['blocker']['blocked'] and pair['blocker']['wall_index'] in (0,1,2)
        assert pair['path_limit']==6 and pair['candidate_limit']==49


@pytest.mark.parametrize('walls', [[],[[15,0,1,30]]])
def test_open_ground_or_sealed_wall_cannot_claim_corner_cover(walls):
    w=bound_world();w.geo=Geometry(walls,dict(CFG),width=60,height=30)
    pair,rows=w._cover_pair('A1',(14,11),(25,11))
    assert pair is None and not any(r['valid'] for r in rows)
    assert all(r['gates'] for r in rows)


def test_cover_paths_have_a_finite_query_budget_and_never_relabel_failure():
    w=bound_world();count=w.geo.query_count
    original=w.geo.path;w.geo.path=lambda *a:{'status':'BudgetExceeded','length':0}
    pair,rows=w._cover_pair('A1',(15,8),(20,11))
    assert pair is None and any('BudgetExceeded' in r['gates'] for r in rows)
    assert sum('BudgetExceeded' in r['gates'] for r in rows)<=6
    w.geo.path=original
    assert w.geo.query_count==count


def test_mover_waits_until_partner_physically_enters_cover_and_reaches_peek():
    w=bound_world();start=w.actors['A1'].position
    assert w.maneuvers['A1']['role']=='WaitCover'
    for _ in range(12):
        before=deepcopy(w.maneuvers['A1']);old=w.actors['A1'].position
        w.step()
        if not before['holder_ready'] and not w.maneuvers['A1']['holder_ready']:
            assert w.actors['A1'].position==old
        if w.maneuvers['A1']['holder_ready']:break
    assert w.maneuvers['A1']['holder_ready']
    pair=w.bound['legs']['A2']
    assert pair['arrived_hide'] and distance(w.actors['A2'].position,pair['peek'])<=.08
    actor=w.actors['A2']
    assert w.geo.see(actor.position,actor.heading,pair['threat'],w._vision('allied'))
    assert start==(8,9)


def test_two_alternating_bounds_swap_only_after_actual_distinct_cover_arrivals():
    w=bound_world();seen=[]
    for _ in range(44):
        mover=w.bound['mover'];phase=w.bound['phase'];pair=deepcopy(w.bound['legs'].get(mover))
        w.step()
        if w.bound['phase']>phase:
            arrived=w.bound['last_swap']
            assert arrived['arrived_actor']==mover and arrived['hide']==pair['hide']
            assert distance(arrived['position'],pair['hide'])<=CFG['arrival_radius']
            assert w.bound['holder']==mover
            seen.append(mover)
        if len(seen)==2:break
    assert seen==['A1','A2']
    assert w.maneuvers['A1']['last_swap']['arrived_actor']=='A2'
    assert not w.metrics['penetrations']


@pytest.mark.parametrize('cause',['ammunition','budget'])
def test_missing_watch_ammo_or_move_budget_prevents_advance(cause):
    w=bound_world();start=w.actors['A1'].position
    if cause=='ammunition':w.actors['A2'].ammo=0
    else:w.moves['A1'].exhausted=True
    for _ in range(20):w.step()
    assert w.actors['A1'].position==start and not any(e['kind']=='BoundSwap' for e in w.events)


def test_old_frames_and_cover_evidence_are_immutable_across_real_phase_swaps():
    w=bound_world();frame=w.frame();frozen=deepcopy(frame)
    for _ in range(32):w.step()
    assert frame==frozen and w.bound['phase']>=3


def test_casualty_releases_two_person_bound_and_survivor_keeps_an_independent_plan():
    w=bound_world();w.actors['A2'].alive=False;w.actors['A2'].health=0;w._cancel('A2');w._decide()
    assert w.bound is None and w.maneuvers['A1']['role']=='Solo'
    assert w.plans['A1']['goal'] and w.behavior_trees['A2']['nodes']['dead.hold']['status']=='Running'


def test_german_own_observer_assigns_two_opposite_complete_flank_routes():
    w=squad_world();assert w.maneuvers['G1']['role']=='ContactWatch'
    left,right=w.maneuvers['G2'],w.maneuvers['G3']
    assert (left['role'],right['role'])==('FlankLeft','FlankRight')
    assert not w.minds['G2'].live_visible and not w.minds['G3'].live_visible
    assert distance(left['goal'],right['goal'])>=2*CFG['reservation_separation']
    assert left['leg']['side']==-right['leg']['side']
    for aid in ('G2','G3'):
        assert w.geo.path(w.actors[aid].position,w.maneuvers[aid]['goal'])['status']=='Complete'
        assert not w._fire_check(aid)['permitted']
    old={a:w.actors[a].position for a in ('G2','G3')}
    for _ in range(4):w.step()
    assert all(distance(old[a],w.actors[a].position)>.5 for a in old)


def test_flank_projection_cannot_merge_sides_or_call_failed_paths_complete():
    w=squad_world();w.flank_legs={};w.geo.path=lambda *a:{'status':'Unreachable','length':0}
    w._coordinate_germans()
    for aid in ('G2','G3'):
        assert w.maneuvers[aid]['goal'] is None
        assert w.maneuvers[aid]['leg']['path_status']=='NoAdmittedFlank'


def test_losing_own_observer_stops_flank_authority_and_starts_finite_separate_searches():
    w=squad_world();w.command('place','P',(9,11))
    for _ in range(3):w.step()
    assert all(p.get('role') not in ('ContactWatch','FlankLeft','FlankRight') for p in w.maneuvers.values() if p)
    points=[w.minds[a].search_goal for a in ('G1','G2','G3')]
    assert all(points) and len(set(points))==3
    assert all(w.minds[a].search_deadline>=0 for a in ('G1','G2','G3'))


def test_hidden_player_counterfactual_does_not_change_reports_searches_or_motion():
    w=squad_world();w.command('place','P',(9,11));w.step();w.step()
    other=deepcopy(w);other.command('place','P',(8,10))
    for _ in range(5):
        w.step();other.step()
        for aid in ('G1','G2','G3'):
            assert w.minds[aid].search_origin==other.minds[aid].search_origin
            assert w.minds[aid].search_deadline==other.minds[aid].search_deadline
            assert w.moves[aid].goal==other.moves[aid].goal
            assert w.actors[aid].position==other.actors[aid].position


def test_flank_leg_has_a_fixed_deadline_and_same_contact_does_not_rearm_it():
    w=squad_world();end=w.flank_legs['G2']['expires']
    for _ in range(28):w.step()
    assert w.flank_legs['G2']['expires']==end
    if w.maneuvers.get('G2',{}).get('role')=='FlankLeft':assert w.maneuvers['G2']['goal'] is None


def test_actual_paris_raster_admits_only_real_cover_and_records_blocking_cells():
    w=World('follow',geometry=RasterGeometry(dict(CFG,path_node_budget=12000)),parameters={'combat_damage':0})
    assert not w.bound['failed']
    for pair in w.bound['legs'].values():
        assert pair['blocker']['cell'] and pair['blocker']['point']
        assert w.geo.sight_ray(pair['hide'],pair['threat'])['blocked']
        assert not w.geo.sight_ray(pair['peek'],pair['threat'])['blocked']
        assert not w.geo.blocked(pair['hide'],pair['peek'],.35)
    assert w.behavior_trees['A1']['nodes']['bound.geometry']['status']=='Success'


def test_disabled_coordination_keeps_legacy_roles_and_invalid_tuning_is_atomic():
    w=bound_world();w.configure({'tactical_coordination':0})
    assert w.bound is None and not w.maneuvers
    before=deepcopy(w.frame())
    with pytest.raises(ValueError):w.configure({'tactical_coordination':2})
    assert w.frame()==before


def test_live_distance_tuning_invalidates_even_a_failed_cached_bound():
    w=bound_world();previous=w.bound
    previous['failed']=True
    w.configure({'follow_distance':4,'scout_distance':7})
    assert w.bound is not previous and w.parameters['scout_distance']==7
    assert w.bound['created']==w.at and not w.bound['failed']


def test_clear_peek_beyond_watch_range_is_rejected_instead_of_waiting_forever():
    w=bound_world()
    pair,rows=w._cover_pair('A1',(14,11),(40,11))
    assert pair is None and not any(row['valid'] for row in rows)


def test_actual_raster_flanks_have_final_lanes_and_both_physically_depart():
    w=World('squad',geometry=RasterGeometry(dict(CFG,path_node_budget=12000)),parameters={'combat_damage':0})
    starts={a:w.actors[a].position for a in ('G2','G3')}
    assert distance(*starts.values())>=2.5
    for aid in starts:
        m=w.maneuvers[aid]
        assert m['leg']['candidate_limit']==49 and m['leg']['expires']<=18
        assert not w.geo.blocked(m['goal'],m['contact']['position'])
        assert not w._fire_check(aid)['permitted']
    for _ in range(8):w.step()
    assert all(distance(starts[a],w.actors[a].position)>2 for a in starts)
    assert not w.metrics['penetrations']
