"""Real audited-raster behaviour gates; no UE or live index writes."""
import copy
import hashlib
import math
import pytest
from app.npc_engine import CFG
from npc_quiet_fixture import World
from app.npc_raster import RasterGeometry, FIGURES
from test_npc_simulation import advance, clients


def world(preset='follow'):
    return World(preset, geometry=RasterGeometry(dict(CFG, path_node_budget=12000)))


def test_exact_identity_coordinates_and_conservative_footprint():
    w = world(); g = w.geo
    raw = (FIGURES/'bounded_expanded/L0_candidate_25cm.png').read_bytes()
    assert g.description()['sha256'] == hashlib.sha256(raw).hexdigest()
    assert w.frame()['bounds'] == [180,240] and w.walls == []
    # Pixel centre299,827 maps to UE CP1(70.875,-202.875).
    local = ((299+.5)*.25,(827+.5)*.25)
    assert (local[0]-4,4-local[1]) == (70.875,-202.875)
    assert not g.free((-1,50)) and not g.free((180,240))
    edges = [i for i,v in enumerate(g.data['sight']) if v and not g.data['nav'][i]]
    assert edges and not g.free(((edges[0]%720+.5)*.25,(edges[0]//720+.5)*.25))


def test_real_building_detour_has_checked_continuous_segments():
    g=world('search').geo; a,b=(106.125,99.125),(92.125,95.125)
    assert g.blocked(a,b)
    route=g.path(a,b)
    assert route['status']=='Complete' and 0<route['expanded']<=12000
    assert route['length']>math.dist(a,b)
    assert all(not g.blocked(x,y,.35) for x,y in zip([a]+route['points'],route['points']))
    assert g.path(a,b)['expanded']==0 and g.cache_hits>=1


def test_disconnected_and_budget_failure_remain_distinct():
    g=world().geo; a=(101.125,99.125)
    component=g.data['components'][g._index(a)]
    other=next(i for i,v in enumerate(g.data['nav']) if v and g.data['components'][i]!=component)
    b=((other%720+.5)*.25,(other//720+.5)*.25)
    assert g.path(a,b)['status']=='Unreachable'
    limited=RasterGeometry(dict(CFG,path_node_budget=5))
    route=limited.path((106.125,99.125),(92.125,95.125))
    assert route['status']=='BudgetExceeded' and route['expanded']==5
    assert limited.path(a,(-1,2))['status']=='InvalidEndpoint'


def test_both_allies_actually_follow_a_player_walk_on_the_raster():
    w=world(); before=copy.deepcopy(w.frame()); w.command('walk','P',(97.125,99.125))
    for _ in range(20):
        f=w.step(.5)
        assert all(w.geo.free(a.position) for a in w.actors.values())
        assert all(math.dist(a.position,b.position)>=.7-1e-8 for i,a in enumerate(w.actors.values()) for b in list(w.actors.values())[i+1:])
    assert f['moves']['P']['result']=='Arrived'
    for aid in ('A1','A2'):
        assert f['minds'][aid]['state']=='Follow'
        assert f['moves'][aid]['result']=='Arrived' and f['moves'][aid]['arrival_error']<=.45
        assert math.dist(before['actors'][aid]['position'],f['actors'][aid]['position'])>2
    assert not f['metrics']['penetrations']


def test_support_overwatch_reach_distinct_reserved_positions():
    w=world('support'); f=advance(w,10)
    assert [f['minds'][k]['state'] for k in ('A1','A2')]==['Support','Overwatch']
    assert f['reservations']['A1']['id']!=f['reservations']['A2']['id']
    assert math.dist(f['reservations']['A1']['position'],f['reservations']['A2']['position'])>=1.6
    for aid in ('A1','A2'):
        assert f['moves'][aid]['result']=='Arrived' and f['moves'][aid]['arrival_error']<=.45
    assert f['metrics']['pair_comparisons_max']<=36


def test_building_occlusion_frozen_search_and_actual_home_return():
    w=world('search'); advance(w,1)
    assert w.frame()['minds']['G1']['engage_permitted']
    observed=copy.deepcopy(w.minds['G1'].memory)
    assert observed.actor_id=='P' and w.geo.blocked(w.actors['G1'].position,(92.125,95.125))
    w.command('place','P',(92.125,95.125))
    assert not w.frame()['minds']['G1']['engage_permitted']
    advance(w,1); origin=w.minds['G1'].search_origin; deadline=w.minds['G1'].search_deadline
    assert origin==observed.position and deadline>0
    for _ in range(10):
        w.step(.5)
        m=w.minds['G1']
        assert m.search_origin==origin and m.search_deadline==deadline
        if m.search_goal is not None:
            assert w.geo.free(m.search_goal)
    f=advance(w,8); m=w.minds['G1']
    assert m.state=='Guard' and m.memory is None
    assert math.dist(w.actors['G1'].position,m.home)<=.45
    assert all(s in [r['to'] for r in m.transitions] for s in ('Alert','Engage','Investigate','Search','Return','Guard'))
    assert not f['metrics']['penetrations']


def test_hidden_player_counterfactual_preserves_all_enemy_decisions():
    a,b=world('search'),world('search');advance(a,1);advance(b,1)
    a.command('place','P',(85.125,99.125));b.command('place','P',(81.125,98.125))
    for _ in range(24):
        fa,fb=a.step(),b.step()
        for gid in ('G1','G2','G3'):
            assert fa['minds'][gid]==fb['minds'][gid]
            assert fa['actors'][gid]==fb['actors'][gid]
            assert fa['moves'][gid]==fb['moves'][gid]


@pytest.mark.parametrize('actor',['P','A1','A2','G1','G2','G3'])
def test_every_member_can_be_placed_and_rotated_without_moving_others(actor):
    w=world(); before=w.frame(); p=w.actors[actor].position
    target=next(q for q in ((p[0]+.25,p[1]),(p[0]-.25,p[1]),(p[0],p[1]+.25),(p[0],p[1]-.25))
                if w.geo.free(q) and all(math.dist(q,a.position)>=.7 for k,a in w.actors.items() if k!=actor))
    w.command('place',actor,target)
    assert w.actors[actor].position==target
    for k,a in w.actors.items():
        if k!=actor: assert list(a.position)==before['actors'][k]['position']
    w.command('rotate',actor,heading=math.pi/2)
    assert w.actors[actor].heading==math.pi/2


def test_map_api_default_mask_identity_roundtrip_and_rejected_mutations(clients):
    c,h=clients[0];prefix='/api/v1/npc-simulation'
    r=c.post(prefix+'/sessions',json={'preset':'support'},headers=h).json()
    assert r['frame']['scene']['kind']=='paris_raster_2d'
    scene=r['layout']['scene'];mask=c.get(prefix+'/masks/bounded_expanded/0')
    assert mask.status_code==200 and len(mask.content)==720*960
    assert mask.headers['x-map-sha256']==scene['sha256']
    layout=r['layout'];again=c.post(prefix+'/sessions',json={'preset':layout['preset'],'layout':layout['positions'],'headings':layout['headings'],'expected_map_sha256':scene['sha256']},headers=h)
    assert again.status_code==200 and again.json()['layout']==layout
    bad=c.post(prefix+'/sessions',json={'expected_map_sha256':'wrong'},headers=h)
    assert bad.status_code==422
    url=prefix+'/sessions/'+r['session_id']
    for i,p in enumerate(([0,0],r['frame']['actors']['A1']['position'])):
        response=c.post(url,json={'revision':0,'request_id':'rejected_'+str(i),'operation':'place','position':p},headers=h)
        assert response.status_code==422 and c.get(url).json()['frame']==r['frame']
    assert c.post(prefix+'/sessions',json={'layer':4},headers=h).status_code==422


def test_episode_and_replanning_still_finite_on_full_map():
    w=world('search');advance(w,1);w.command('place','P',(85.125,99.125));f=advance(w,120)
    assert f['at']==120 and f['finished'] and len(w.history)<=240
    assert f['metrics']['max_query_nodes']<=12000 and not f['metrics']['hidden_target_reads']
    assert all(m.requests<=32 and m.retries<=2 for m in w.moves.values())
