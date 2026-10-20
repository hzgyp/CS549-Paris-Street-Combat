import copy
import json
import pytest
from app.catalog import refresh
from app.research_links import associate
from app.security import WorkbenchError
from test_contracts import fixture, make_client, put
from test_research import registered as research_registered
from test_gameplay import registered as gameplay_registered


def registration(fixture):
    root,_=fixture
    cfg=research_registered(fixture)
    gameplay_registered(fixture)
    cfg['associations']='Assets/Registry/research/associations.json'
    put(root,'Assets/Registry/research/library.json',cfg)
    group=dict(id='context',references=[dict(register='HistoricalReference/Paris1944/CONTEXT.md',key='document')],asset_ids=['example'],gameplay_ids=['tutorial'],relation='context',note=dict(zh='仅街垒背景，不证明关卡地形。',en='Barricade context only; not proof of level geometry.'))
    data=dict(schema_version=1,groups=[group])
    put(root,cfg['associations'],data)
    return data


def test_inline_references_reverse_navigation_and_snapshot_refresh(fixture):
    root,store=fixture;data=registration(fixture)
    client,app,_=make_client(fixture)
    first=store.active()
    asset=client.get('/api/v1/assets/example').json()['data']
    ref=asset['historical_references'][0]
    assert 'Barricades' in ref['excerpt'] and ref['links'][0]['url']=='https://example.org/source'
    assert ref['association']['note']['en'].startswith('Barricade context')
    game=client.get('/api/v1/gameplay/tutorial').json()['data']
    assert game['historical_references'][0]['id']==ref['id']
    reverse=client.get('/api/v1/research/'+ref['id']).json()['data']
    assert reverse['assets'][0]['id']=='example' and reverse['gameplay'][0]['id']=='tutorial'
    index=json.loads((root/'Assets/Registry/asset-index.json').read_text())
    assert index['gameplay'][0]['historical_references'][0]['id']==ref['id']
    assert index['assets'][0]['historical_references'][0]['association']==ref['association']
    assert any(f['path'].endswith('associations.json') for f in index['source_fingerprints'])
    data['groups'][0]['gameplay_ids']=[]
    put(root,'Assets/Registry/research/associations.json',data)
    refresh(root,store)
    assert client.get('/api/v1/gameplay/tutorial').json()['data']['historical_references']==[]
    assert client.get('/api/v1/gameplay/tutorial?snapshot_id='+first).json()['data']['historical_references'][0]['id']==ref['id']
    before={p:(root/'Assets/Registry'/p).read_bytes() for p in ['asset-index.json','ASSET_DIRECTORY.md','GAMEPLAY_DIRECTORY.md','HISTORICAL_DIRECTORY.md']}
    current=store.active()
    data['groups'][0]['asset_ids']=['missing']
    put(root,'Assets/Registry/research/associations.json',data)
    with pytest.raises(WorkbenchError):refresh(root,store)
    assert store.active()==current
    assert all((root/'Assets/Registry'/p).read_bytes()==b for p,b in before.items())


@pytest.mark.parametrize('change',['missing_reference','unknown_asset','unknown_gameplay','duplicate','missing_language','unknown_relation','duplicate_selector'])
def test_invalid_associations_fail_before_publish(fixture,change):
    root,store=fixture;data=registration(fixture)
    g=data['groups'][0]
    if change=='missing_reference':g['references'][0]['key']='not-registered'
    if change=='unknown_asset':g['asset_ids']=['missing']
    if change=='unknown_gameplay':g['gameplay_ids']=['missing']
    if change=='duplicate':data['groups'].append(dict(copy.deepcopy(g),id='duplicate'))
    if change=='missing_language':g['note'].pop('en')
    if change=='unknown_relation':g['relation']='historically_proven'
    if change=='duplicate_selector':g['references']*=2
    put(root,'Assets/Registry/research/associations.json',data)
    with pytest.raises(WorkbenchError):refresh(root,store)
