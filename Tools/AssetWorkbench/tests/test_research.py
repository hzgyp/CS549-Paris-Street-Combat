import csv
import hashlib
import json

import pytest
from PIL import Image
from app.catalog import refresh
from app.research import build
from app.security import WorkbenchError
from test_contracts import fixture, make_client, put


def registered(fixture):
    root,store=fixture
    note=root/'HistoricalReference/Paris1944/CONTEXT.md'
    note.parent.mkdir(parents=True)
    note.write_text('# Paris research\nBarricades 街垒 — https://example.org/source\n',encoding='utf-8')
    photo=root/'HistoricalReference/Paris1944/photo.jpg'
    Image.new('RGB',(1800,1000),(80,90,60)).save(photo)
    csv_path=root/'HistoricalReference/Paris1944/images.csv'
    with csv_path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['file','source','title','date','scope','rights','note','locator','sha256'])
        writer.writeheader()
        for name,file,rights in [('Photo','photo.jpg','U.S. government work'),('Restricted','restricted.jpg','Copyright reserved'),('Missing','missing.jpg','public domain')]:
            writer.writerow(dict(file=file,source='https://example.org',title=name,date='1944',scope='Paris',rights=rights,note='No unit identification',locator='Plate 1',sha256=hashlib.sha256(photo.read_bytes()).hexdigest()))
    cfg=dict(schema_version=1,notes=[dict(directory='HistoricalReference/Paris1944',scope='paris',asset_ids=['example'])],registers=[dict(path='HistoricalReference/Paris1944/images.csv',adapter='images',scope='paris')])
    # Images adapter resolves relative to catalog's parent, mirroring the original register layout.
    catalog=root/'HistoricalReference/Paris1944/catalog';catalog.mkdir()
    csv_path.rename(catalog/'images.csv');cfg['registers'][0]['path']='HistoricalReference/Paris1944/catalog/images.csv'
    put(root,'Assets/Registry/research/library.json',cfg)
    path='Assets/Registry/registry.json';reg=json.loads((root/path).read_text());reg['research']='Assets/Registry/research/library.json';put(root,path,reg)
    return cfg


def test_authenticated_text_images_rights_and_index_refresh(fixture):
    root,store=fixture;registered(fixture)
    client,app,_=make_client(fixture)
    rows=client.get('/api/v1/research').json()['data'];assert rows['total']==4
    notes=client.get('/api/v1/research?q=街垒&kind=note&scope=paris').json()['data']['items'];assert len(notes)==1
    note=client.get('/api/v1/research/'+notes[0]['id']).json()['data'];assert 'Barricades' in note['body']
    assert note['assets'][0]['id']=='example'
    assert client.get('/api/v1/assets/example').json()['data']['historical_references'][0]['id']==note['id']
    photo=next(r for r in rows['items'] if r['title']=='Photo')
    image=client.get('/api/v1/media/'+photo['media_id']);assert image.status_code==200
    import io
    assert Image.open(io.BytesIO(image.content)).size==(1600,889)
    assert client.get('/api/v1/media/'+photo['media_id']+'?original=true').content==(root/photo['image_path']).read_bytes()
    assert next(r for r in rows['items'] if r['title']=='Restricted')['image_access']=='rights_link_only'
    assert next(r for r in rows['items'] if r['title']=='Missing')['image_access']=='missing'
    outputs=['asset-index.json','ASSET_DIRECTORY.md','HISTORICAL_DIRECTORY.md']
    index=json.loads((root/'Assets/Registry/asset-index.json').read_text());assert index['research_count']==4
    # Registered folders are enumerated on every refresh, including new research notes.
    (root/'HistoricalReference/Paris1944/NEW.md').write_text('# Added source\nNew evidence',encoding='utf-8')
    snap=refresh(root,store);assert snap['stats']['research_count']==5
    valid={p:(root/'Assets/Registry'/p).read_bytes() for p in outputs}
    # Tampered image fails refresh and media read; database and all index outputs stay intact.
    Image.new('RGB',(20,20),'red').save(root/photo['image_path'])
    assert client.get('/api/v1/media/'+photo['media_id']).status_code==409
    with pytest.raises(WorkbenchError,match='哈希'):refresh(root,store)
    assert store.active()==snap['id']
    assert valid=={p:(root/'Assets/Registry'/p).read_bytes() for p in outputs}
    client.cookies.clear()
    assert client.get('/api/v1/research').status_code==401
    assert client.get('/api/v1/media/'+photo['media_id']).status_code==401


@pytest.mark.parametrize('change', ['escape','url','scope','duplicate'])
def test_research_registration_rejects_unsafe_inputs(fixture,change):
    root,_=fixture;cfg=registered(fixture)
    if change=='escape':cfg['notes']=[{'path':'../outside.md','scope':'paris'}]
    if change=='scope':cfg['registers'][0]['scope']='adopted'
    if change=='duplicate':cfg['notes']*=2
    if change=='url':
        p=root/'HistoricalReference/Paris1944/catalog/images.csv';p.write_text(p.read_text().replace('https://example.org','javascript:alert(1)'),encoding='utf-8')
    with pytest.raises(WorkbenchError):build(root,cfg)


def test_database_failure_rolls_back_research_navigation(fixture,monkeypatch):
    root,store=fixture;registered(fixture);snap=refresh(root,store)
    outputs=['asset-index.json','ASSET_DIRECTORY.md','HISTORICAL_DIRECTORY.md']
    before={p:(root/'Assets/Registry'/p).read_bytes() for p in outputs}
    (root/'HistoricalReference/Paris1944/CONTEXT.md').write_text('# Changed\nNew text',encoding='utf-8')
    def fail(*args,**kwargs):raise RuntimeError('simulated database failure')
    monkeypatch.setattr(store,'publish',fail)
    with pytest.raises(WorkbenchError):refresh(root,store)
    assert store.active()==snap['id']
    assert before=={p:(root/'Assets/Registry'/p).read_bytes() for p in outputs}


def test_supplemental_source_sections_and_chinese_keywords(fixture):
    root,_=fixture;cfg=registered(fixture)
    p=root/'HistoricalReference/NormandyContext/SOURCES.md';p.parent.mkdir()
    p.write_text('# Sources\n## S27 — Archive photograph\n\nNational Archives\n\nhttps://example.org/a\n## S28 — Another source\n\nMuseum\n\nhttps://example.org/b\n',encoding='utf-8')
    cfg['notes'].append({'path':'HistoricalReference/NormandyContext/SOURCES.md','scope':'background'})
    entries,_,_=build(root,cfg)
    assert {r['key'] for r in entries if r['kind']=='source'}=={'S27','S28'}
    assert '街垒' in next(r for r in entries if r['key']=='document' and r['scope']=='paris')['search_text']
