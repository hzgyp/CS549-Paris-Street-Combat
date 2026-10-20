"""Direct local entry without weakening shared auth or per-browser NPC ownership."""
import time

import pytest
from fastapi.testclient import TestClient

from app.main import create_app, ROOT


@pytest.fixture
def app(tmp_path):
    application=create_app(root=ROOT,state_dir=tmp_path/'state',token='t'*32)
    yield application
    application.state.pool.shutdown(wait=True)


@pytest.mark.parametrize('host',['127.0.0.1','localhost'])
def test_plain_local_entry_reuses_cookie_and_refreshes_expired_session(app,host):
    client=TestClient(app,base_url=f'http://{host}:8765')
    assert client.get('/npc-simulation').status_code==200
    login=client.get('/api/v1/session')
    assert login.status_code==200
    assert 'HttpOnly' in login.headers['set-cookie'] and 'SameSite=strict' in login.headers['set-cookie']
    cookie=client.cookies.get('aw_session');csrf=login.json()['csrf']
    assert client.get('/api/v1/npc-simulation').status_code==200
    again=client.get('/api/v1/session')
    assert again.json()['csrf']==csrf and client.cookies.get('aw_session')==cookie
    assert 'set-cookie' not in again.headers
    app.state.sessions[cookie]['expires']=time.time()-1
    assert client.get('/api/v1/npc-simulation').status_code==401
    renewed=client.get('/api/v1/session')
    assert renewed.status_code==200 and renewed.json()['csrf']!=csrf
    assert client.cookies.get('aw_session')!=cookie


def test_local_stale_bootstrap_link_and_invalid_cookie_recover(app):
    client=TestClient(app,base_url='http://127.0.0.1:8765')
    assert client.post('/api/v1/session',json={'token':'old-link'*5},
                       headers={'origin':'http://127.0.0.1:8765'}).status_code==200
    client.cookies.clear();client.cookies.set('aw_session','unknown')
    assert client.get('/api/v1/session').status_code==200
    assert client.cookies.get('aw_session',domain='127.0.0.1',path='/') in app.state.sessions


def test_local_auto_session_keeps_origin_host_csrf_and_world_ownership(app):
    origin='http://127.0.0.1:8765'
    first=TestClient(app,base_url=origin);second=TestClient(app,base_url=origin)
    assert first.get('/api/v1/session',headers={'origin':'http://evil.example'}).status_code==403
    assert first.get('/api/v1/session',headers={'host':'evil.example:8765'}).status_code==403
    assert first.post('/api/v1/session',json={'token':'old-link'*5}).status_code==403
    csrf=first.get('/api/v1/session').json()['csrf']
    assert second.get('/api/v1/session').json()['csrf']!=csrf
    route='/api/v1/npc-simulation/sessions'
    assert first.post(route,json={}).status_code==403
    assert first.post(route,json={},headers={'origin':origin,'x-csrf-token':'wrong'}).status_code==403
    created=first.post(route,json={},headers={'origin':origin,'x-csrf-token':csrf})
    assert created.status_code==200
    world=route+'/'+created.json()['session_id']
    assert first.get('/api/v1/session').json()['csrf']==csrf
    assert first.get(world).status_code==200
    assert second.get(world).status_code==404


@pytest.mark.parametrize('shared,host',[(True,'127.0.0.1'),(True,'192.168.1.75'),(False,'192.168.1.75')])
def test_shared_and_non_loopback_authorities_still_require_token(tmp_path,shared,host):
    app=create_app(root=ROOT,state_dir=tmp_path/'state',token='t'*32,
                   shared=shared,allowed_hosts=['127.0.0.1','192.168.1.75'])
    try:
        origin=f'http://{host}:8765';client=TestClient(app,base_url=origin)
        assert client.get('/api/v1/session').status_code==401
        assert client.post('/api/v1/session',json={'token':'x'*32},headers={'origin':origin}).status_code==401
        login=client.post('/api/v1/session',json={'token':'t'*32},headers={'origin':origin})
        assert login.status_code==200
        assert client.get('/api/v1/session').json()['csrf']==login.json()['csrf']
    finally:
        app.state.pool.shutdown(wait=True)
