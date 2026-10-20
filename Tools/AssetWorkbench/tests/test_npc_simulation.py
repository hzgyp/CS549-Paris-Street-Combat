"""Real motion/perception and private HTTP worlds; no refresh or native writes."""
import copy
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import create_app, ROOT
from npc_quiet_fixture import World
from app.npc_oracle import distance

def advance(w, seconds):
    for _ in range(round(seconds/.5)):
        w.step(.5)
    return w.frame()

def test_walk_changes_real_separated_follow_positions():
    w=World('follow'); old=copy.deepcopy(w.frame())
    w.command('walk','P',[12,11]); f=advance(w,8)
    assert f['moves']['P']['result']=='Arrived'
    assert distance(f['actors']['P']['position'],[12,11])<=.45
    for aid in ['A1','A2']:
        assert f['minds'][aid]['state']=='Follow'
        assert distance(old['actors'][aid]['position'],f['actors'][aid]['position'])>2
        assert f['moves'][aid]['result']=='Arrived' and f['moves'][aid]['arrival_error']<=.45
        wanted=[f['actors']['P']['position'][0]-3,11+(-1.2 if aid=='A1' else 1.2)]
        assert distance(wanted,f['moves'][aid]['goal'])<=.45
    assert distance(f['reservations']['A1']['position'],f['reservations']['A2']['position'])>=1.6
    assert not f['metrics']['penetrations']

def test_support_roles_arrive_at_distinct_real_goals():
    w=World('support'); f=advance(w,5)
    assert [f['minds'][a]['state'] for a in ['A1','A2']]==['Support','Overwatch']
    assert f['reservations']['A1']['id']!=f['reservations']['A2']['id']
    for aid in ['A1','A2']:
        assert f['moves'][aid]['result']=='Arrived' and f['moves'][aid]['arrival_error']<=.45
    assert f['metrics']['pair_comparisons_max']<=36

def test_lost_sight_fixed_search_and_return():
    w=World('search'); advance(w,1)
    assert w.frame()['minds']['G1']['engage_permitted']
    w.command('place','P',[13,10])
    assert not w.frame()['minds']['G1']['engage_permitted']
    advance(w,1)
    mind=w.minds['G1']; origin=tuple(mind.search_origin); deadline=mind.search_deadline
    assert mind.state=='Investigate' and origin==(19,10)
    advance(w,3)
    assert mind.state=='Search' and tuple(mind.search_origin)==origin and mind.search_deadline==deadline
    advance(w,8)
    assert mind.state=='Guard' and mind.memory is None
    assert distance(w.actors['G1'].position,mind.home)<=.45
    states=[t['to'] for t in mind.transitions]
    assert all(s in states for s in ['Alert','Engage','Investigate','Search','Return','Guard'])

def test_hidden_player_counterfactual_does_not_move_search():
    a,b=World('search'),World('search'); advance(a,1); advance(b,1)
    a.command('place','P',[13,10]); b.command('place','P',[11,10])
    for _ in range(12):
        fa,fb=a.step(),b.step()
        for gid in ['G1','G2','G3']:
            assert fa['minds'][gid]==fb['minds'][gid]
            assert fa['actors'][gid]==fb['actors'][gid]
            assert fa['moves'][gid]==fb['moves'][gid]

@pytest.mark.parametrize('position',[[15.5,10],[5,9],[-1,11],[float('nan'),2]])
def test_rejected_placement_preserves_state(position):
    w=World(); before=w.frame()
    with pytest.raises(ValueError): w.command('place','P',position)
    assert w.frame()==before

def test_wall_detour_is_actual_swept_motion():
    w=World(); w.command('walk','P',[20,11]); f=advance(w,20)
    assert f['moves']['P']['result']=='Arrived' and f['moves']['P']['arrival_error']<=.45
    assert f['metrics']['max_query_nodes']<=700 and not f['metrics']['penetrations']
    assert w.moves['P'].travel>distance([8,11],[20,11])

def test_player_collision_stall_retries_are_finite_and_new_input_recovers():
    w=World(); w.command('walk','P',[13,11])
    # Controlled immobile obstacle: does not change canonical perception policy.
    w.actors['A1'].position=(10,11);w.actors['A1'].alive=False
    original=w._move
    def hold():
        w.actors['A1'].alive=True
        original()
        w.actors['A1'].alive=False
    w._move=hold
    advance(w,15)
    assert w.moves['P'].exhausted and w.moves['P'].retries==2
    requests=w.moves['P'].requests; advance(w,3)
    assert w.moves['P'].requests==requests
    w._move=original;w.actors['A1'].position=(5,9);w.actors['A1'].alive=True
    w.command('walk','P',[12,11]);advance(w,5)
    assert not w.moves['P'].exhausted and w.moves['P'].result=='Arrived'

def test_fixed_ticks_deterministic_and_history_immutable():
    a,b=World(),World()
    for w in [a,b]:w.command('walk','P',[12,11])
    saved=copy.deepcopy(a.step());b.step()
    advance(a,3);advance(b,3)
    assert a.frame()==b.frame() and a.history[0]==saved

def test_new_player_input_reopens_stalled_npc_plan_without_erasing_memory():
    w=World('search');advance(w,1);w.command('place','P',[13,10]);advance(w,1)
    observed=w.minds['G1'].memory;deadline=w.minds['G1'].search_deadline
    m=w.moves['G1'];m.exhausted=True;m.points=[];m.result='WaitingBudgetExhausted'
    w.command('place','P',[12,10])
    assert not m.exhausted and m.result=='Moving' and m.requests==1
    assert w.minds['G1'].memory==observed and w.minds['G1'].search_deadline==deadline

def test_episode_history_and_attempts_are_bounded():
    w=World('search');advance(w,121)
    assert w.at==120 and len(w.history)<=240
    assert all(m.requests<=32 and m.retries<=2 for m in w.moves.values())
    before=w.frame();w.step();assert w.frame()==before
    with pytest.raises(ValueError):w.command('place','P',[13,10])

@pytest.fixture
def clients(tmp_path):
    app=create_app(root=ROOT,state_dir=tmp_path/'state',token='x'*32)
    rows=[]
    for _ in range(2):
        c=TestClient(app,base_url='http://127.0.0.1:8765')
        r=c.post('/api/v1/session',json={'token':'x'*32},headers={'origin':'http://127.0.0.1:8765'})
        assert r.status_code==200
        rows.append((c,{'origin':'http://127.0.0.1:8765','x-csrf-token':r.json()['csrf']}))
    yield rows
    for c,_ in rows:c.close()
    app.state.pool.shutdown(wait=True)

def test_auth_owner_csrf_cas_and_idempotency(clients):
    (c,h),(other,oh)=clients
    guest=TestClient(c.app,base_url='http://127.0.0.1:8765')
    assert guest.get('/api/v1/npc-simulation').status_code==401
    assert c.post('/api/v1/npc-simulation/sessions',json={}).status_code==403
    r=c.post('/api/v1/npc-simulation/sessions',json={},headers=h).json();url='/api/v1/npc-simulation/sessions/'+r['session_id']
    assert other.get(url).status_code==404
    assert other.post(url,json={'revision':0,'request_id':'isolation1','operation':'step'},headers=oh).status_code==404
    payload={'revision':0,'request_id':'unique123','operation':'step','seconds':.5}
    first=c.post(url,json=payload,headers=h);assert first.status_code==200
    assert c.post(url,json=payload,headers=h).json()==first.json()
    assert c.get(url).json()['frame']['at']==.5
    assert c.post(url,json={**payload,'seconds':.4},headers=h).status_code==409
    assert c.post(url,json={**payload,'request_id':'stale123'},headers=h).status_code==409
    invalid={'revision':1,'request_id':'invalid123','operation':'place','position':[15.5,10]}
    assert c.post(url,json=invalid,headers=h).status_code==422
    assert c.get(url).json()['frame']['revision']==1
    guest.close()

def test_map_allowlist_exact_bytes_and_scope(clients):
    c,h=clients[0]
    assert not c.get('/api/v1/npc-simulation').json()['map']['reference_only']
    audit=json.loads((ROOT/'tmp/map-survey-overnight-20261013/collections/complete_v3/figures_v1/FIGURE_AUDIT.json').read_text())
    import hashlib
    for scope,n in [('saved',3),('bounded_expanded',5)]:
        for layer in range(n):
            for kind in ['candidate','status']:
                r=c.get(f'/api/v1/npc-simulation/maps/{scope}/{layer}/{kind}')
                assert r.status_code==200
                expected=audit['outputs'][f'{scope}\\L{layer}_{kind}_25cm.png']
                assert len(r.content)==expected['size_bytes'] and hashlib.sha256(r.content).hexdigest()==expected['sha256']
    assert c.get('/api/v1/npc-simulation/maps/saved/3/candidate').status_code==404
    assert c.get('/api/v1/npc-simulation/maps/unlisted/0/candidate').status_code==422

def test_invalid_layout_and_step_do_not_mutate(clients):
    c,h=clients[0]
    assert c.post('/api/v1/npc-simulation/sessions',json={'layout':{'P':[2,2]}},headers=h).status_code==422
    r=c.post('/api/v1/npc-simulation/sessions',json={},headers=h).json();url='/api/v1/npc-simulation/sessions/'+r['session_id']
    assert c.post(url,json={'revision':0,'request_id':'badstep123','operation':'step','seconds':.15},headers=h).status_code==422
    assert c.get(url).json()['frame']==r['frame']
