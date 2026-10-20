import copy
import json
from types import SimpleNamespace

import pytest
from app.library_scope import collect, validate
from app.security import WorkbenchError
from test_contracts import ROOT, fixture, put, protect_live_navigation_outputs
from test_research import registered
from app.research import build
from app.catalog import refresh
from app.store import Store


@pytest.mark.parametrize('keys',[['absent'],['photo.jpg','photo.jpg'],[{}],[],42])
def test_research_exact_selection_rejects_invalid_keys(fixture,keys):
    root,_=fixture;cfg=registered(fixture)
    cfg['registers'][0]['include_keys']=keys
    with pytest.raises(WorkbenchError):build(root,cfg)


def test_scoped_curation_and_failed_refresh_preserve_previous_snapshot(fixture):
    root,store=fixture;cfg=registered(fixture)
    cfg['registers'][0]['include_keys']=['photo.jpg']
    cfg['allowed_scopes']=['paris','equipment']
    put(root,'Assets/Registry/research/library.json',cfg)
    snap=refresh(root,store)
    rows=store.list(snap['id'],'research');assert len(rows)==2
    assert sum(r['kind']=='image' and r['media_id'] is not None for r in rows)==1
    cfg['registers'][0]['scope']='background'
    put(root,'Assets/Registry/research/library.json',cfg)
    with pytest.raises(WorkbenchError):refresh(root,store)
    assert store.active()==snap['id']


def scope_importer():
    data={'schema_version':1,'retired_files':[dict(bundle='legacy',path='Reference/old.png',sha256='a'*64,reason='Retired scenario')]}
    rows=[dict(bundle='legacy',path='Reference/old.png',sha256='a'*64,size_bytes=10),dict(bundle='legacy',path='Reference/rifle.blend',sha256='b'*64,size_bytes=20)]
    importer=SimpleNamespace(doc=lambda p:data,files=rows,research_paths=set(),code_paths={},entities={'bundles':[dict(id='legacy',file_count=2,size_bytes=30)],'assets':[],'research':[]})
    return importer,data


def test_retirement_changes_membership_preserves_source_identity_and_reuse():
    importer,data=scope_importer();before=copy.deepcopy(data)
    collect(importer,'scope.json')
    assert data==before
    assert [r['path'] for r in importer.files]==['Reference/rifle.blend']
    b=importer.entities['bundles'][0]
    assert (b['file_count'],b['catalog_file_count'],b['retired_file_count'],b['size_bytes'])==(1,2,1,20)


@pytest.mark.parametrize('change',['hash','unknown','research','asset','model','source','duplicate'])
def test_retirement_rejects_stale_or_in_use_identity(change):
    importer,data=scope_importer()
    if change=='hash':data['retired_files'][0]['sha256']='c'*64
    if change=='unknown':data['retired_files'][0]['path']='Reference/unknown.png'
    if change=='research':importer.entities['research']=[{'local_files':[{'path':'Reference/old.png'}]}]
    if change=='asset':importer.entities['assets']=[{'bundles':['legacy']}]
    if change=='model':importer.entities['models']=[{'path':'Reference/old.png'}]
    if change=='source':importer.code_paths={'Reference/old.png':'a'*64}
    if change=='duplicate':data['retired_files']*=2
    with pytest.raises(WorkbenchError):collect(importer,'scope.json')


def test_current_equipment_history_and_paris_preservation(tmp_path):
    store=Store(tmp_path/'scope.sqlite3');s=refresh(ROOT,store)['id']
    assets=store.list(s,'assets');assert len(assets)==231
    ids={a['id'] for a in assets};assert {'frag-grenade','smoke-grenade','ammo-box','paris-city'}<=ids
    research=store.list(s,'research');assert len(research)==67
    assert {'S20','S22','E03'}<={r['key'] for r in research if r['kind']=='source'}
    assert {r['scope'] for r in research}=={'paris','equipment'}
    assert not any(r['kind'] in ('motion','weather') for r in research)
    for target in ('frag-grenade','smoke-grenade','ammo-box'):
        refs=[r for r in research if target in r['asset_ids']]
        assert len(refs)==3
        assert any(r['kind']=='note' and r['body'] for r in refs)
        assert any(r['kind']=='image' and r['media_id'] for r in refs)
        assert all(r['links'] and r['asset_links'] and r['gameplay_links'] for r in refs)
    scope=json.loads((ROOT/'Assets/Registry/library-scope.json').read_text(encoding='utf-8'))
    for r in scope['retired_files']:
        rows,_=store.files(s,r['bundle'],limit=100000)
        assert r['path'] not in {f['path'] for f in rows}
    assert not any('Normandy/' in f['path'] or 'BrowserPrototype/' in f['path'] for f in store.files(s,'gunplay-reference-assets',limit=100000)[0])
    assert len(store.files(s,'gunplay-reference-assets',limit=100000)[0])==5
