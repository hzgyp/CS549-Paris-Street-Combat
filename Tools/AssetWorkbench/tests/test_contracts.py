import json
import hashlib
import time
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.catalog import Importer, refresh, result_state
from app.main import create_app, ROOT
from app.security import WorkbenchError, safe_path, read_file
from app.store import Store


@pytest.fixture(autouse=True)
def protect_live_navigation_outputs(monkeypatch):
    """Live-source checks must not rewrite the owner's active navigation index.

    Real publication/rollback contracts are tested on isolated fixture roots.
    Live checks still validate source fingerprints and use temporary databases.
    """
    import asset_index
    original = asset_index.publish

    @contextmanager
    def isolated_publication(root, data, cancelled=lambda: False):
        if Path(root).resolve() != ROOT.resolve():
            with original(root, data, cancelled) as result:
                yield result
            return
        asset_index.validate_sources(root, data)
        assert not cancelled(), 'Live-source check was cancelled'
        yield {'status': 'test_read_only', 'asset_count': data['asset_count'],
               'member_count': data['member_count'], 'files': []}
        asset_index.validate_sources(root, data)

    monkeypatch.setattr(asset_index, 'publish', isolated_publication)


def put(root,path,data):
    p=root/path;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data),encoding='utf-8')
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture
def fixture(tmp_path):
    root=tmp_path/'project';root.mkdir()
    manifest={'schema_version':1,'asset_id':'test-bundle','asset_version':'v1','files':[{'path':'Assets/example.bin','sha256':'a'*64,'size_bytes':5,'storage':'sftp'}],'dependencies':[]}
    manifest_hash=put(root,'Assets/Sync/manifests/test.json',manifest)
    put(root,'Assets/Sync/CATALOG.json',{'schema_version':1,'active_manifests':[{'asset_id':'test-bundle','asset_version':'v1','path':'Assets/Sync/manifests/test.json','sha256':manifest_hash}]})
    put(root,'Assets/Registry/assets/pilots.json',{'assets':[{'id':'example','name':'测试资产','name_en':'Example','category':'道具','origin':'team_created','lifecycle':'candidate','owner':'test','bundles':['test-bundle'],'documents':[]}]})
    put(root,'Assets/Registry/mappings/history.json',{'revisions':[]})
    put(root,'Assets/Registry/templates/requirements.json',{'templates':[{'id':'prop','text':'template','version':'1'}]})
    put(root,'Assets/Registry/registry.json',{'schema_version':1,'catalog':'Assets/Sync/CATALOG.json','assets':'Assets/Registry/assets/pilots.json','history':'Assets/Registry/mappings/history.json','templates':'Assets/Registry/templates/requirements.json','selectors':[]})
    store=Store(tmp_path/'state/cache/index.sqlite3')
    return root,store


def test_hash_mismatch_preserves_snapshot(fixture):
    root,store=fixture
    original=refresh(root,store)
    p=root/'Assets/Sync/manifests/test.json';p.write_text(p.read_text()+' ')
    with pytest.raises(WorkbenchError,match='哈希不匹配'):refresh(root,store)
    assert store.active()==original['id']


def test_inventory_coverage_members_and_precise_usage(tmp_path):
    store=Store(tmp_path/'inventory.sqlite3');snap=refresh(ROOT,store)['id']
    assets=store.list(snap,'assets');by_id={a['id']:a for a in assets}
    assert len(assets)==229 and len(by_id)==229
    assert sum(a.get('parent_id')=='ue4-animation-collection' for a in assets)==125
    assert sum(a.get('parent_id')=='mw2-library' for a in assets)==53
    assert all(a['preview_id'] and a['revisions'] for a in assets)
    media=store.list(snap,'media')
    assert not any(m.get('kind')=='supplier thumbnail' for m in media)
    animation_ids={a['id'] for a in assets if a.get('parent_id')=='ue4-animation-collection'}
    covers=[m for m in media if m.get('native_cover')]
    assert {m['asset_id'] for m in covers}==animation_ids|{'ue4-animation-collection'}
    assert all(sum(m['asset_id']==asset_id for m in covers)==2 for asset_id in animation_ids)
    assert all(m['provenance']['capture_sha256']==m['sha256'] and m['provenance']['animation'] for m in covers)
    assert by_id['paris-city']['member_count']==15850
    assert by_id['rifle-animation']['member_count']==298
    assert by_id['frag-grenade']['usage_status']=='formal'
    assert 'formal' in by_id['ammo-box']['build_ids']
    assert by_id['ammo-box']['usage_status']=='formal'
    assert 'formal' in by_id['muzzle-flash']['build_ids']
    assert by_id['mw2-sp-r-208']['usage_status']=='source_only'
    assert by_id['mw2-library']['usage_status']=='source_only'
    assert by_id['anim-rifle-animset-pro']['usage_status']=='unregistered'
    assert by_id['anim-superhero-flight-animations-426']['usage_status']=='unregistered'
    assert any(r['id']=='rifle-animation-duplicate-delivery-20261004' for r in store.list(snap,'revisions'))
    for m in store.list(snap,'media'):
        assert hashlib.sha256(read_file(ROOT,m['path'])).hexdigest()==m['sha256']
    assert all(u.get('source_sha256') and u.get('matches') for u in store.list(snap,'usage') if u['basis']=='pinned_source_reference')


def test_animation_pack_default_coverage_and_source_identity(tmp_path):
    from app.animations import AnimationLibrary
    store=Store(tmp_path/'animation.sqlite3');snap=refresh(ROOT,store)['id']
    packs={a['id'] for a in store.list(snap,'assets') if a.get('parent_id')=='ue4-animation-collection'}
    models=[m for m in store.list(snap,'models') if m.get('animation_pack_id')]
    assert len(models)==125 and {m['animation_pack_id'] for m in models}==packs
    library=AnimationLibrary(ROOT,ROOT/'Assets/LocalWorking/AssetWorkbench')
    count=0
    for pid in packs:
        directory=library.directory(pid);count+=len(directory['clips'])
        assert library.status(pid,directory['default_clip'])['status']=='ready'
        raw,_=library.file(pid,directory['default_clip']);assert len(raw)>10000
    assert count>=25000


def test_members_search_paging_and_pinned_source_tamper(fixture):
    root,store=fixture
    data={'assets':[],'members':{'example':[{'name':f'clip-{i}','path':f'clip-{i}','kind':'AnimSequence'} for i in range(125)]},'usage_rules':[{'asset_id':'example','filename':'Use.cpp','needle':'/Game/Example','label':'source reference'}]}
    put(root,'Assets/Registry/assets/inventory.json',data)
    code='Unreal/Variants/Test/Project/Use.cpp';p=root/code;p.parent.mkdir(parents=True);p.write_text('/Game/Example')
    manifest=put(root,'Unreal/Variants/Test/SOURCE_MANIFEST.json',{'files':[{'path':'Use.cpp','size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}]})
    put(root,'Docs/Development/selector.json',{'source_manifest':'Unreal/Variants/Test/SOURCE_MANIFEST.json','source_manifest_sha256':manifest,'game_sha256':'a'*64,'source_snapshot':'Unreal/Variants/Test/Project','status':'candidate'})
    registry=json.loads((root/'Assets/Registry/registry.json').read_text());registry['inventory']='Assets/Registry/assets/inventory.json';registry['selectors']=[dict(id='ui-review',path='Docs/Development/selector.json',assets=[],channel='candidate',title='Test')]
    put(root,'Assets/Registry/registry.json',registry)
    client,app,_=make_client(fixture)
    first=client.get('/api/v1/assets/example/members?limit=50').json()['data']
    assert first['total']==125 and len(first['items'])==50
    second=client.get('/api/v1/assets/example/members',params={'limit':50,'cursor':first['next_cursor']}).json()['data']
    assert second['items'][0]['name']=='clip-50'
    assert client.get('/api/v1/assets/example/members',params={'q':'clip-1','cursor':first['next_cursor']}).status_code==422
    found=client.get('/api/v1/assets?q=clip-124').json()['data']
    assert found['total']==1 and 'members' not in found['items'][0]
    before=app.state.store.active();p.write_text('/Game/Changed')
    with pytest.raises(WorkbenchError,match='源码哈希'):refresh(root,app.state.store)
    assert app.state.store.active()==before


def test_unknown_schema_preserves_snapshot(fixture):
    root,store=fixture;original=refresh(root,store)
    p=root/'Assets/Registry/registry.json';d=json.loads(p.read_text());d['schema_version']=99;put(root,str(p.relative_to(root)),d)
    with pytest.raises(WorkbenchError):refresh(root,store)
    assert store.active()==original['id']


def test_partial_and_fixture_results_never_pass():
    assert result_state({'exit_code':0})=='incomplete'
    assert result_state({'status':'pass'})=='incomplete'
    assert result_state({'status':'failed_restore_v16_equipment','reason':'unknown_check_mode'})=='fixture_error'
    assert result_state({'status':'pass_case','reason':'done','mode':'wrong'},'expected')=='fixture_error'
    assert result_state({'status':'pass_case','reason':'complete','scope':'only this case'})=='pass'


def test_missing_historical_document_is_unassessed(fixture):
    root,store=fixture
    put(root,'Assets/Registry/mappings/history.json',{'revisions':[{'id':'old','asset_id':'example','title':'Historical','kind':'integration_revision','document':'Docs/Development/missing.md','result':'pass','summary':'old claim','scope':'past only','media_ids':[]}]})
    snap=refresh(root,store)
    revision=store.get(snap['id'],'revisions','old')
    assert revision['result']=='unassessed' and revision['recorded_result']=='pass'


def test_inherited_flag_cannot_override_failed_or_wrong_game(fixture):
    root,store=fixture
    manifest=put(root,'Unreal/Variants/Test/SOURCE_MANIFEST.json',{'files':[]})
    result_path='tmp/g1-test/checks/test/RESULT.json'
    put(root,result_path,{'status':'fail_case','reason':'actually failed'})
    put(root,'Docs/Development/selector.json',{'source_manifest':'Unreal/Variants/Test/SOURCE_MANIFEST.json','source_manifest_sha256':manifest,'game_sha256':'a'*64,'source_snapshot':'Unreal/Variants/Test/Project','status':'candidate','checks':[{'result':result_path,'inherited_unchanged_scope':True}]})
    importer=Importer(root,store);importer.build({'id':'test','path':'Docs/Development/selector.json','assets':['example'],'channel':'candidate','title':'Test'})
    assert importer.entities['evidence'][0]['result']=='fail'
    put(root,result_path,{'status':'pass_case','reason':'complete','game_sha256':'b'*64})
    importer=Importer(root,store);importer.build({'id':'test','path':'Docs/Development/selector.json','assets':['example'],'channel':'candidate','title':'Test'})
    assert importer.entities['evidence'][0]['result']=='unassessed'


def test_metadata_only_and_duplicate_accounting(fixture):
    root,store=fixture
    p=root/'Assets/Sync/manifests/test.json';m=json.loads(p.read_text());m['files'].append(dict(m['files'][0],path='Assets/copy.bin'))
    newhash=put(root,str(p.relative_to(root)),m)
    p=root/'Assets/Sync/CATALOG.json';c=json.loads(p.read_text());c['active_manifests'][0]['sha256']=newhash;put(root,str(p.relative_to(root)),c)
    snap=refresh(root,store)
    assert snap['stats']['file_count']==2 and snap['stats']['unique_blobs']==1
    assert store.list(snap['id'],'assets')[0]['availability']=='metadata_only'
    assert len(store.files(snap['id'])[0])==2


def test_rebuild_semantics_and_cancel(fixture):
    root,store=fixture;s1=refresh(root,store);r1=store.list(s1['id'],'revisions')
    with pytest.raises(WorkbenchError):refresh(root,store,lambda:True)
    assert store.active()==s1['id']
    s2=refresh(root,store)
    assert s1['digest']==s2['digest'] and r1==store.list(s2['id'],'revisions')


@pytest.mark.parametrize('path',['../private.json','/etc/passwd','C:/secret','Assets/x:stream','//server/a','Assets/../secret','Assets//secret'])
def test_path_rejection(fixture,path):
    root,_=fixture
    with pytest.raises(WorkbenchError):safe_path(root,path)


def test_metadata_reference_cannot_read_credentials(fixture):
    root,store=fixture;put(root,'Assets/LocalWorking/access/secret.json',{'private':'never expose'})
    with pytest.raises(WorkbenchError):Importer(root,store).read('Assets/LocalWorking/access/secret.json')


def make_client(fixture):
    root,store=fixture;refresh(root,store)
    app=create_app(root=root,state_dir=store.path.parent.parent,token='t'*32)
    client=TestClient(app,base_url='http://127.0.0.1:8765')
    response=client.post('/api/v1/session',json={'token':'t'*32},headers={'origin':'http://127.0.0.1:8765'})
    assert response.status_code==200
    return client,app,response.json()['csrf']


def test_registered_glb_auth_identity_and_external_resources(fixture):
    import struct
    from app.models import validate_glb
    def glb(doc):
        chunk=json.dumps(doc).encode();chunk+=b' '*((-len(chunk))%4)
        return struct.pack('<IIIII',0x46546c67,2,20+len(chunk),len(chunk),0x4e4f534a)+chunk
    root,store=fixture
    raw=glb({'asset':{'version':'2.0'},'scenes':[{}]})
    path='Assets/LocalWorking/AssetWorkbench/3d/test.glb'
    p=root/path;p.parent.mkdir(parents=True);p.write_bytes(raw)
    record=dict(id='model',asset_ids=['example'],path=path,sha256=hashlib.sha256(raw).hexdigest(),audience='local_owner')
    put(root,'Assets/LocalWorking/AssetWorkbench/private-records/models.json',{'models':[record]})
    client,app,_=make_client(fixture)
    response=client.get('/api/v1/models/model/file')
    assert response.status_code==200 and response.content==raw
    assert response.headers['content-type']=='model/gltf-binary'
    metadata=client.get('/api/v1/assets/example').json()['data']['models'][0]
    assert 'path' not in metadata and 'audience' not in metadata
    assert client.get('/api/v1/models/unregistered/file').status_code==404
    assert client.get('/api/v1/models/model/file',headers={'origin':'http://external.invalid'}).status_code==403
    p.write_bytes(raw+b'changed')
    assert client.get('/api/v1/models/model/file').status_code==409
    client.cookies.clear()
    assert client.get('/api/v1/models/model/file').status_code==401
    for doc in [{'asset':{'version':'2.0'},'images':[{'uri':'https://external.invalid/image.png'}]},
                {'asset':{'version':'2.0'},'buffers':[{'uri':'file:///private','byteLength':1}]},
                {'asset':{'version':'2.0'},'bufferViews':[{'byteLength':4}]},
                {'asset':{'version':'2.0'},'accessors':[{'count':10000001}]},[],{'asset':[]}]:
        with pytest.raises(WorkbenchError):validate_glb(glb(doc))
    with pytest.raises(WorkbenchError):validate_glb(raw+b'x')


def test_supplier_images_are_retired_even_in_historical_snapshots(fixture):
    root,store=fixture
    item=dict(id='supplier',asset_id='example',path='Assets/old.png',sha256='a'*64,audience='local_owner',kind='supplier thumbnail',mime='image/png')
    put(root,'Assets/LocalWorking/AssetWorkbench/private-records/media.json',{'files':[item]})
    client,app,_=make_client(fixture);snapshot=store.active()
    assert store.list(snapshot,'media')==[]
    assert client.get('/api/v1/assets/example').json()['data']['preview_id'] is None
    # Simulate an old, previously published snapshot containing the retired record.
    with store.connect() as db:db.execute('INSERT INTO entities VALUES(?,?,?,?)',(snapshot,'media','supplier',json.dumps(item)))
    response=client.get('/api/v1/media/supplier',params={'snapshot_id':snapshot})
    assert response.status_code==410 and response.json()['code']=='MEDIA_RETIRED'


def test_auth_origin_cursor_and_source_clone(fixture):
    client,app,csrf=make_client(fixture)
    assert client.get('/api/v1/assets?q=测试').json()['data']['total']==1
    assert client.get('/api/v1/assets?q=EXAMPLE').json()['data']['total']==1
    assert client.get('/api/v1/assets?limit=201').status_code==422
    assert client.get('/api/v1/assets?cursor=wrong').status_code==422
    assert client.get('/api/v1/assets',headers={'origin':'http://evil.example'}).status_code==403
    assert client.get('/api/v1/assets',headers={'host':'evil.example'}).status_code==403
    assert client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'}).status_code==403
    assert client.post('/api/v1/assets/example',json={}).status_code==403
    assert client.get('/api/v1/media/not-registered').status_code==404
    client.cookies.clear()
    assert client.get('/api/v1/assets').status_code==401


def test_spa_asset_deep_link(fixture):
    client,app,csrf=make_client(fixture)
    response=client.get('/assets/recorded-audio')
    assert response.status_code==200
    assert '<html' in response.text
    assert client.get('/assets/nonexistent.js').status_code==404


def test_source_changes_before_activation(fixture,monkeypatch):
    root,store=fixture;original=refresh(root,store)
    import app.catalog as catalog
    real=catalog.read_file;calls=0
    def changing(r,p,*args,**kwargs):
        nonlocal calls
        data=real(r,p,*args,**kwargs)
        if p=='Assets/Sync/CATALOG.json':
            calls+=1
            if calls%2==0:return data+b' '
        return data
    monkeypatch.setattr(catalog,'read_file',changing)
    with pytest.raises(WorkbenchError):refresh(root,store)
    assert store.active()==original['id']


def test_media_identity_and_mime(fixture):
    root,store=fixture
    from PIL import Image
    p=root/'Assets/test.png';p.parent.mkdir(exist_ok=True);Image.new('RGB',(4,4),'red').save(p)
    raw=p.read_bytes()
    put(root,'Assets/LocalWorking/AssetWorkbench/private-records/media.json',{'files':[{'id':'image','asset_id':'example','audience':'local_owner','path':'Assets/test.png','sha256':hashlib.sha256(raw).hexdigest(),'mime':'image/png','label':'test','size_bytes':len(raw)}]})
    client,app,csrf=make_client(fixture)
    assert client.get('/api/v1/media/image').status_code==200
    assert client.get('/api/v1/media/image',headers={'range':'bytes=0-3'}).status_code==206
    p.write_bytes(b'changed')
    assert client.get('/api/v1/media/image').status_code==409


def test_real_channel_and_mine_scope(tmp_path):
    store=Store(tmp_path/'actual.sqlite3');snap=refresh(ROOT,store)
    builds={b['id']:b for b in store.list(snap['id'],'builds')}
    # Roles remain distinct even after the same reviewed Game is adopted/published.
    assert len({builds[k]['source_id'] for k in ('formal','ui-review','published')})==3
    registry=json.loads((ROOT/'Assets/Registry/registry.json').read_text())
    for role in ('formal','ui-review'):
        selector=next(s for s in registry['selectors'] if s['id']==role)
        expected=json.loads((ROOT/selector['path']).read_text())
        assert builds[role]['game_sha256']==expected['game_sha256']
        assert builds[role]['source_manifest_sha256']==expected['source_manifest_sha256']
    catalog=json.loads((ROOT/'Assets/Sync/CATALOG.json').read_text())
    release=next(m for m in catalog['active_manifests'] if m['asset_id']=='paris-g1-packaged-playtest')
    published=json.loads((ROOT/release['path']).read_text())
    assert builds['published']['game_sha256']==published['game_sha256']
    assert builds['ui-review']['revision']==json.loads((ROOT/'Docs/Development/CURRENT_UI_REVIEW.json').read_text())['revision']
    l=store.get(snap['id'],'revisions','mine-ue-v1');r=store.get(snap['id'],'revisions','mine-ue-v2')
    assert l['model_identity']==r['model_identity']
    assert l['result']=='fail' and r['result']=='pass'
    assert store.get(snap['id'],'revisions','german-v14-selected')['result']=='accepted_with_limits'
    assert store.get(snap['id'],'revisions','animation-repeat')['result']=='recorded'


def test_20000_file_query_budget(fixture):
    root,store=fixture
    m={'schema_version':1,'asset_id':'test-bundle','asset_version':'v1','files':[{'path':f'Assets/fixture/{n:05d}.bin','sha256':f'{n:064x}','size_bytes':1,'storage':'sftp'} for n in range(20000)]}
    digest=put(root,'Assets/Sync/manifests/test.json',m)
    c=json.loads((root/'Assets/Sync/CATALOG.json').read_text());c['active_manifests'][0]['sha256']=digest;put(root,'Assets/Sync/CATALOG.json',c)
    s=refresh(root,store);assert s['stats']['file_count']==20000
    timings=[]
    for n in range(30):
        start=time.perf_counter();rows,total=store.files(s['id'],q='fixture',offset=n*50);timings.append((time.perf_counter()-start)*1000)
        assert len(rows)==50 and total==20000
    p95=sorted(timings)[28]
    print(f'20k file metadata query p95={p95:.2f}ms')
    assert p95<500


def test_process_crash_retains_previous_snapshot(fixture):
    import subprocess,sys
    root,store=fixture;first=refresh(root,store)
    script="""import sqlite3,sys,os
c=sqlite3.connect(sys.argv[1]);c.execute('BEGIN IMMEDIATE')
c.execute("UPDATE state SET value='partial' WHERE key='active'")
os._exit(7)
"""
    run=subprocess.run([sys.executable,'-c',script,str(store.path)],capture_output=True)
    assert run.returncode==7
    restored=Store(store.path)
    assert restored.active()==first['id']
    rebuilt=refresh(root,Store(store.path.parent/'recreated.sqlite3'))
    assert rebuilt['digest']==first['digest']
    store.job({'id':'interrupted','status':'running'})
    assert Store(store.path).jobs()[0]['status']=='failed'


def test_windows_junction_and_read_limit(fixture,tmp_path):
    import subprocess,os
    root,store=fixture;outside=tmp_path/'outside';outside.mkdir();(outside/'hidden.bin').write_bytes(b'private')
    link=root/'junction'
    subprocess.run(['powershell','-NoProfile','-Command',"$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path $env:AW_TEST_LINK -Target $env:AW_TEST_TARGET | Out-Null"],env={**os.environ,'AW_TEST_LINK':str(link),'AW_TEST_TARGET':str(outside)},check=True,capture_output=True)
    try:
        with pytest.raises(WorkbenchError):read_file(root,'junction/hidden.bin')
    finally:
        os.rmdir(link)
    (root/'large.bin').write_bytes(b'12345')
    with pytest.raises(WorkbenchError):read_file(root,'large.bin',4)


@pytest.mark.parametrize('audience,mime,exists,expected',[('local_owner','image/png',True,422),('not_approved','image/png',True,404),('local_owner','image/png',False,404)])
def test_media_negative_cases(fixture,audience,mime,exists,expected):
    root,store=fixture;raw=b'not an image'
    if exists:(root/'Assets/bad.bin').write_bytes(raw)
    put(root,'Assets/LocalWorking/AssetWorkbench/private-records/media.json',{'files':[{'id':'bad','asset_id':'example','audience':audience,'path':'Assets/bad.bin','sha256':hashlib.sha256(raw).hexdigest(),'mime':mime,'label':'test','size_bytes':len(raw)}]})
    client,app,csrf=make_client(fixture)
    assert client.get('/api/v1/media/bad').status_code==expected
    if audience!='local_owner':
        assert any(i['code']=='RIGHTS_NOT_ESTABLISHED' for i in app.state.store.list(app.state.store.active(),'issues'))


def test_job_idempotency_cancel_and_no_write_api(fixture,monkeypatch):
    import threading
    import app.main as main
    client,app,csrf=make_client(fixture);entered=threading.Event();release=threading.Event()
    real=main.refresh
    def blocked(*args,**kwargs):
        entered.set();release.wait(5);return real(*args,**kwargs)
    monkeypatch.setattr(main,'refresh',blocked)
    headers={'origin':'http://127.0.0.1:8765','x-csrf-token':csrf,'idempotency-key':'job-1'}
    try:
        first=client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers=headers)
        assert first.status_code==200 and entered.wait(3)
        same=client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers=headers)
        assert same.json()['id']==first.json()['id']
        assert client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers=dict(headers,**{'idempotency-key':'job-2'})).status_code==409
        assert client.post('/api/v1/assets/example',json={},headers=headers).status_code==405
        assert client.post('/api/v1/index/jobs/'+first.json()['id']+'/cancel',headers=headers).status_code==200
    finally:
        release.set();app.state.pool.shutdown(wait=True)
    assert app.state.store.jobs()[0]['status']=='cancelled'


def wait_job(client, job_id):
    deadline=time.monotonic()+10
    while time.monotonic()<deadline:
        job=client.get('/api/v1/index/jobs/'+job_id).json()
        if job['status'] not in ('queued','running'):return job
        time.sleep(.02)
    pytest.fail('Refresh job did not finish')


def navigation_bytes(root):
    return {p:(root/p).read_bytes() for p in ('Assets/Registry/asset-index.json','Assets/Registry/ASSET_DIRECTORY.md')}


def test_refresh_api_add_and_edit_automatically_syncs_navigation(fixture):
    root,_=fixture;client,app,csrf=make_client(fixture)
    headers={'origin':'http://127.0.0.1:8765','x-csrf-token':csrf,'idempotency-key':'navigation-add'}
    path='Assets/Registry/assets/pilots.json';data=json.loads((root/path).read_text())
    added=dict(data['assets'][0],id='new-prop',name='新增道具',name_en='New prop',bundles=[])
    data['assets'].append(added);put(root,path,data)
    try:
        job=wait_job(client,client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers=headers).json()['id'])
        assert job['status']=='succeeded' and job['navigation_index']['status']=='synced'
        index=json.loads((root/'Assets/Registry/asset-index.json').read_text(encoding='utf-8'))
        assert index['asset_count']==2 and any(a['id']=='new-prop' for a in index['assets'])
        assert '新增道具' in (root/'Assets/Registry/ASSET_DIRECTORY.md').read_text(encoding='utf-8')
        data['assets'][1]['name']='已修改道具';put(root,path,data)
        headers['idempotency-key']='navigation-edit'
        job=wait_job(client,client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers=headers).json()['id'])
        assert job['status']=='succeeded'
        assert app.state.store.get(job['snapshot_id'],'assets','new-prop')['name']=='已修改道具'
        assert '已修改道具' in (root/'Assets/Registry/ASSET_DIRECTORY.md').read_text(encoding='utf-8')
        assert json.loads((root/'Assets/Registry/asset-index.json').read_text(encoding='utf-8'))['assets'][1]['name']=='已修改道具'
        for file in job['navigation_index']['files']:
            assert hashlib.sha256((root/file['path']).read_bytes()).hexdigest()==file['sha256']
    finally:app.state.pool.shutdown(wait=True)


def test_directory_write_failure_rolls_back_documents_and_snapshot(fixture,monkeypatch):
    import asset_index
    root,_=fixture;client,app,csrf=make_client(fixture)
    previous=app.state.store.active();old=navigation_bytes(root)
    path='Assets/Registry/assets/pilots.json';data=json.loads((root/path).read_text());data['assets'][0]['name']='Changed';put(root,path,data)
    real=asset_index.atomic_write
    def broken(path,raw):
        if path.name=='ASSET_DIRECTORY.md':raise OSError('test directory write denied')
        return real(path,raw)
    monkeypatch.setattr(asset_index,'atomic_write',broken)
    try:
        response=client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers={'origin':'http://127.0.0.1:8765','x-csrf-token':csrf,'idempotency-key':'write-failure'})
        job=wait_job(client,response.json()['id'])
        assert job['status']=='failed' and job['code']=='NAVIGATION_INDEX_FAILED'
        assert 'test directory write denied' in job['error']
        assert app.state.store.active()==previous and navigation_bytes(root)==old
    finally:app.state.pool.shutdown(wait=True)


def test_database_failure_rolls_back_navigation(fixture,monkeypatch):
    root,store=fixture;previous=refresh(root,store);old=navigation_bytes(root)
    path='Assets/Registry/assets/pilots.json';data=json.loads((root/path).read_text());data['assets'][0]['name']='Changed';put(root,path,data)
    def broken(*args,**kwargs):raise OSError('database publication failed')
    monkeypatch.setattr(store,'publish',broken)
    with pytest.raises(WorkbenchError,match='database publication failed'):refresh(root,store)
    assert store.active()==previous['id'] and navigation_bytes(root)==old


def test_cancel_after_document_write_rolls_back_navigation(fixture,monkeypatch):
    import asset_index
    root,store=fixture;previous=refresh(root,store);old=navigation_bytes(root)
    path='Assets/Registry/assets/pilots.json';data=json.loads((root/path).read_text());data['assets'][0]['name']='Changed';put(root,path,data)
    cancelled=False;real=asset_index.atomic_write
    def cancel_on_write(path,raw):
        nonlocal cancelled
        real(path,raw);cancelled=True
    monkeypatch.setattr(asset_index,'atomic_write',cancel_on_write)
    with pytest.raises(WorkbenchError) as failure:refresh(root,store,lambda:cancelled)
    assert failure.value.code=='CANCELLED'
    assert store.active()==previous['id'] and navigation_bytes(root)==old


def test_source_drift_during_navigation_publication_rolls_back(fixture):
    import asset_index
    root,store=fixture;previous=refresh(root,store);old=navigation_bytes(root)
    data=asset_index.build(root)
    path=root/'Assets/Registry/assets/pilots.json';path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(WorkbenchError) as failure:
        with asset_index.publish(root,data):pytest.fail('Changed source was published')
    assert failure.value.code=='SOURCE_CHANGED_DURING_SCAN'
    assert store.active()==previous['id'] and navigation_bytes(root)==old


def test_shared_selector_manifest_deduplicates_file_records(fixture):
    root,store=fixture
    code=root/'Unreal/Variants/Test/Project/Use.cpp';code.parent.mkdir(parents=True);code.write_text('body')
    manifest=put(root,'Unreal/Variants/Test/SOURCE_MANIFEST.json',{'files':[{'path':'Use.cpp','size_bytes':4,'sha256':hashlib.sha256(code.read_bytes()).hexdigest()}]})
    selector='Docs/Development/selector.json'
    put(root,selector,{'source_manifest':'Unreal/Variants/Test/SOURCE_MANIFEST.json','source_manifest_sha256':manifest,'game_sha256':'a'*64,'source_snapshot':'Unreal/Variants/Test/Project','status':'candidate'})
    path='Assets/Registry/registry.json';registry=json.loads((root/path).read_text())
    registry['selectors']=[{'id':i,'path':selector,'assets':['example'],'channel':'candidate','title':i} for i in ('ui-review','equipment-review')];put(root,path,registry)
    snapshot=refresh(root,store)
    assert len(store.list(snapshot['id'],'builds'))==2
    assert snapshot['stats']['file_count']==2  # one Catalog row plus one shared source row
    importer=Importer(root,store)
    row={'path':'same.bin','size_bytes':1,'sha256':'a'*64}
    importer.file_rows('same',[row])
    with pytest.raises(WorkbenchError,match='冲突'):importer.file_rows('same',[dict(row,sha256='b'*64)])


def test_grenade_model_versions_and_current_formal_usage(tmp_path):
    from app.models import validate_glb
    store=Store(tmp_path/'grenades.sqlite3');snapshot=refresh(ROOT,store)
    app=create_app(root=ROOT,state_dir=tmp_path/'web',token='g'*32)
    refresh(ROOT,app.state.store)
    client=TestClient(app,base_url='http://127.0.0.1:8765')
    client.post('/api/v1/session',json={'token':'g'*32},headers={'origin':'http://127.0.0.1:8765'}).raise_for_status()
    for aid,triangles in [('frag-grenade',2733),('smoke-grenade',7562)]:
        asset=client.get('/api/v1/assets/'+aid).json()['data']
        assert asset['usage_status']=='formal' and len(asset['models'])==1
        assert asset['preview_id']==aid+'-model-v1-browser-front'
        model=asset['models'][0]
        response=client.get('/api/v1/models/'+model['id']+'/file')
        assert response.status_code==200 and hashlib.sha256(response.content).hexdigest()==model['sha256']
        doc=validate_glb(response.content)
        assert not doc.get('animations') and len(doc['images'])>=3
        assert sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])==triangles
        revisions=client.get('/api/v1/assets/'+aid+'/revisions').json()['data']
        original=next(r for r in revisions if r['id']==model['id'])
        current=next(r for r in revisions if r['id']==aid+'-wheel-integration-v4-20261011')
        assert current['parent_ids']==[original['id']]
        assert current['model_identity']==original['model_identity']==model['sha256']
        usage=next(u for u in asset['usage'] if u['build_id']=='equipment-input-review')
        selected=json.loads((ROOT/'Docs/Development/CURRENT_EQUIPMENT_INPUT_REVIEW.json').read_text())
        assert usage['build_revision']==selected['revision'] and usage['game_sha256']==selected['game_sha256']
        formal=json.loads((ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json').read_text())
        assert any(u['build_id']=='formal' and u['game_sha256']==formal['game_sha256'] for u in asset['usage'])
        # This older wheel revision is historical evidence, not the current selector.
        assert current['metrics']['game_sha256']=='332756d091f64678de7b124e4e216571211bead31c42e6226edc686a14b15695'
        comparison=client.get('/api/v1/comparisons',params={'left':original['id'],'right':current['id']}).json()['data']
        assert comparison['same_model']
    index=json.loads((ROOT/'Assets/Registry/asset-index.json').read_text(encoding='utf-8'))
    assert index['asset_count']==snapshot['stats']['asset_count']==229


def test_shared_host_authentication_origin_and_csrf(fixture):
    root,store=fixture
    app=create_app(root=root,state_dir=store.path.parent.parent,token='n'*32,allowed_hosts=['127.0.0.1','192.168.1.75','asset-pc'],shared=True)
    refresh(root,app.state.store)
    client=TestClient(app,base_url='http://192.168.1.75:8765')
    origin='http://192.168.1.75:8765'
    assert client.get('/').status_code==200
    assert client.get('/api/v1/assets').status_code==401
    assert client.post('/api/v1/session',json={'token':'n'*32},headers={'origin':'http://evil.example'}).status_code==403
    login=client.post('/api/v1/session',json={'token':'n'*32},headers={'origin':origin});assert login.status_code==200
    assert client.get('/api/v1/assets').status_code==200
    assert client.get('/api/v1/health').json()['mode']=='shared_read_only'
    assert client.get('/api/v1/assets',headers={'host':'unknown.example:8765'}).status_code==403
    assert client.get('/api/v1/assets',headers={'origin':'http://127.0.0.1:8765'}).status_code==403
    headers={'origin':origin,'idempotency-key':'shared-refresh'}
    assert client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers=headers).status_code==403
    headers['x-csrf-token']=login.json()['csrf']
    job=client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers=headers);assert job.status_code==200
    assert wait_job(client,job.json()['id'])['status']=='succeeded'
    app.state.pool.shutdown(wait=True)


def test_local_network_authorities_are_bounded(monkeypatch):
    import app.network as network
    ips,hosts=network.addresses(False)
    assert ips==['127.0.0.1'] and '192.168.1.75' not in hosts
    monkeypatch.setattr(network.socket,'gethostname',lambda:'asset-pc')
    monkeypatch.setattr(network.socket,'getaddrinfo',lambda *args:[(None,None,None,None,('192.168.1.75',0)),(None,None,None,None,('169.254.1.1',0))])
    class Route:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def connect(self,*args):pass
        def getsockname(self):return ('192.168.1.75',0)
    monkeypatch.setattr(network.socket,'socket',lambda *args:Route())
    ips,hosts=network.addresses(True)
    assert ips==['192.168.1.75'] and 'asset-pc' in hosts and '169.254.1.1' not in hosts


@pytest.mark.parametrize('origin',['http://203.0.113.7:8766','http://203.0.113.7:18766','http://assets.example.test'])
def test_public_forward_preserves_authentication_and_exact_authority(fixture,origin):
    root,store=fixture
    app=create_app(root=root,state_dir=store.path.parent.parent,token='p'*32,port=8766,shared=True,external_url=origin)
    refresh(root,app.state.store)
    client=TestClient(app,base_url=origin)
    assert client.get('/').status_code==200
    assert client.get('/api/v1/assets').status_code==401
    assert client.post('/api/v1/session',json={'token':'x'*32},headers={'origin':origin}).status_code==401
    login=client.post('/api/v1/session',json={'token':'p'*32},headers={'origin':origin})
    assert login.status_code==200
    assert client.get('/api/v1/assets').status_code==200
    assert client.get('/api/v1/assets',headers={'host':'203.0.113.8:8766'}).status_code==403
    assert client.get('/api/v1/assets',headers={'host':'203.0.113.7:9876'}).status_code==403
    assert client.get('/api/v1/assets',headers={'origin':'http://127.0.0.1:8766'}).status_code==403
    assert client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers={'origin':origin}).status_code==403
    headers={'origin':origin,'x-csrf-token':login.json()['csrf'],'idempotency-key':'public-refresh'}
    job=client.post('/api/v1/index/jobs',json={'kind':'refresh_metadata'},headers=headers)
    assert job.status_code==200 and wait_job(client,job.json()['id'])['status']=='succeeded'
    assert client.get('http://127.0.0.1:8766/').status_code==200
    app.state.pool.shutdown(wait=True)
    local=create_app(root=root,state_dir=store.path.parent.parent,port=8766,external_url=origin)
    assert TestClient(local,base_url=origin).get('/').status_code==403
    local.state.pool.shutdown(wait=True)


def test_external_url_validation():
    from app.network import external_origin
    assert external_origin('http://ASSETS.example.test:80/',True)=='http://assets.example.test'
    assert external_origin('http://203.0.113.7:18766',True)=='http://203.0.113.7:18766'
    assert external_origin('http://203.0.113.7:8766',False) is None
    assert external_origin(None,True) is None
    for value in ('*','http://*.example.test:8766','https://203.0.113.7:8766','http://u:p@assets.test',
                  'http://assets.test/path','http://assets.test?token=x','http://assets.test/#token=x',
                  'http://assets.test:65536','http://assets.test:0','http://[::1]:8766','http://assets.test\n',123):
        with pytest.raises(ValueError):external_origin(value,True)


def test_city_map_registration_and_authenticated_real_previews(tmp_path):
    app=create_app(root=ROOT,state_dir=tmp_path/'city-web',token='c'*32)
    refresh(ROOT,app.state.store)
    client=TestClient(app,base_url='http://127.0.0.1:8765')
    assert client.get('/api/v1/assets/paris-city').status_code==401
    client.post('/api/v1/session',json={'token':'c'*32},headers={'origin':'http://127.0.0.1:8765'}).raise_for_status()
    asset=client.get('/api/v1/assets/paris-city').json()['data']
    assert asset['category']=='地图' and asset['member_count']==15850
    assert asset['map_details']['level_count']==69 and asset['map_details']['size_bytes']==28421951358
    assert asset['preview_id']=='paris-map-game-bridge'
    for media in asset['media']:
        if not media['id'].startswith('paris-map-'):continue
        assert media['actual_capture'] and media['source_map']=='/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1'
        response=client.get('/api/v1/media/'+media['id'])
        assert response.status_code==200 and response.content.startswith(b'\x89PNG\r\n\x1a\n')
        assert hashlib.sha256(response.content).hexdigest()==media['sha256']
    levels=client.get('/api/v1/assets/paris-city/members',params={'q':'.umap','limit':100}).json()['data']
    assert levels['total']==69
    assert any(x['name']=='LV_Paris_WW2.umap' for x in levels['items'])
    current=next(u for u in asset['usage'] if u['build_id']=='formal' and u['basis']=='pinned_source_reference' and u['label']=='当前游戏默认地图')
    assert any(asset['map_details']['game_map'] in x['text'] for x in current['matches'])
    assert any(r['title']=='G1 原生派生地图' for r in client.get('/api/v1/assets/paris-city/revisions').json()['data'])
    app.state.pool.shutdown(wait=True)
