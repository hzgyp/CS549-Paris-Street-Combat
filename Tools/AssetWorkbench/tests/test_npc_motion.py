"""Motion sampling is observational: existing AI/collision outcomes stay identical."""
import copy
import pytest
from fastapi.testclient import TestClient
from app.main import create_app, ROOT
from app.npc_engine import World, CFG
from app.npc_raster import RasterGeometry


@pytest.mark.parametrize('preset',['follow','support','search'])
def test_sample_capture_preserves_actual_raster_world_and_swept_segments(preset):
    worlds=[World(preset,geometry=RasterGeometry(dict(CFG,path_node_budget=12000),'bounded_expanded',0)) for _ in range(2)]
    sampled,plain=worlds
    if preset=='follow':
        for w in worlds:w.command('walk','P',(92.125,95.125))
    for _ in range(20):
        samples=[sampled.motion_sample()]
        sampled.step(.5,samples);plain.step(.5)
        assert sampled.frame()==plain.frame()
        assert len(samples)==6
        assert samples[-1]['actors']==sampled.frame()['actors']
        for a,b in zip(samples,samples[1:]):
            assert abs(b['at']-a['at']-.1)<1e-6
            for aid in a['actors']:
                assert not sampled.geo.blocked(a['actors'][aid]['position'],b['actors'][aid]['position'],.35)
        frozen=copy.deepcopy(samples);sampled.motion_sample();assert samples==frozen


def test_samples_stop_at_finite_episode_end():
    w=World();w.ticks=1198;samples=[w.motion_sample()];w.step(.5,samples)
    assert [s['at'] for s in samples]==[119.8,119.9,120]
    w.step(.5,samples);assert len(samples)==3 and w.frame()['finished']


def test_opt_in_motion_samples_keep_revision_csrf_and_idempotency(tmp_path):
    app=create_app(root=ROOT,state_dir=tmp_path/'state')
    try:
        origin='http://127.0.0.1:8765';c=TestClient(app,base_url=origin)
        csrf=c.get('/api/v1/session').json()['csrf'];headers={'origin':origin,'x-csrf-token':csrf}
        world=c.post('/api/v1/npc-simulation/sessions',json={'scene':'exercise'},headers=headers).json()
        url='/api/v1/npc-simulation/sessions/'+world['session_id']
        payload={'revision':0,'request_id':'sample_0001','operation':'step','motion_samples':True}
        assert c.post(url,json=payload).status_code==403
        response=c.post(url,json=payload,headers=headers);assert response.status_code==200
        data=response.json();assert len(data['motion_samples'])==6
        assert data['motion_samples'][0]['actors']==world['frame']['actors']
        assert data['motion_samples'][-1]['actors']==data['frame']['actors']
        assert c.post(url,json=payload,headers=headers).json()==data
        assert c.post(url,json={**payload,'motion_samples':False},headers=headers).status_code==409
        normal=c.post(url,json={'revision':1,'request_id':'normal_0002','operation':'step'},headers=headers).json()
        assert 'motion_samples' not in normal and normal['frame']['revision']==2
    finally:app.state.pool.shutdown(wait=True)
