import copy
import hashlib
import json

import pytest
from app.version_reviews import merge, review_state
from app.catalog import Importer, refresh
from app.security import WorkbenchError
from app.store import Store
from test_contracts import ROOT, fixture, put, protect_live_navigation_outputs


def test_annotations_cannot_silently_promote_or_retarget_a_version():
    rows=[dict(id='old',result='fail',asset_id='a')]
    for patch in ({'result':'pass'},{'asset_id':'other'}):
        with pytest.raises(ValueError):merge(rows,{'annotations':{'old':patch}})
    with pytest.raises(ValueError):merge(rows,{'annotations':{'missing':{}}})
    with pytest.raises(ValueError):merge(rows,{'revisions':copy.deepcopy(rows)})
    assert rows[0]['result']=='fail'


def test_adoption_requires_exact_same_asset_ids_and_does_not_promote_technical_checks():
    rows=[dict(id='accepted',asset_id='a',result='pass'),dict(id='prior',asset_id='a',result='fail'),dict(id='other',asset_id='b',result='pass')]
    selection=dict(asset_id='a',current_id='accepted',previous_id='prior',authority='Docs/accepted.json',scope={'zh':'模型','en':'Model'})
    merged=merge(rows,{'selections':[selection]})
    assert merged[0]['adoption']['previous_id']=='prior'
    assert merged[0]['adoption']['primary'] is True
    assert merged[0]['review_state']=='pending'  # Technical pass alone never enters Human approved.
    assert merged[1]['review_state']=='not_passed'
    assert 'adoption' not in rows[0]
    assert review_state(dict(result='accepted_with_limits',review={'basis':'human'}))=='human_approved'
    for patch in [dict(current_id='missing'),dict(current_id='prior'),dict(previous_id='other'),dict(previous_id='accepted'),dict(authority=''),dict(asset_id='b')]:
        with pytest.raises(ValueError):merge(rows,{'selections':[{**selection,**patch}]})
    with pytest.raises(ValueError):merge(rows,{'selections':[selection,selection]})


def test_bad_adoption_preserves_previous_snapshot_and_navigation(fixture):
    root,store=fixture;before=refresh(root,store);index=(root/'Assets/Registry/asset-index.json').read_bytes()
    reg=json.loads((root/'Assets/Registry/registry.json').read_text());reg['version_reviews']='Assets/Registry/mappings/version-reviews.json';put(root,'Assets/Registry/registry.json',reg)
    put(root,reg['version_reviews'],{'selections':[dict(asset_id='example',current_id='missing',previous_id=None,authority='Docs/accepted.json',scope={'zh':'模型','en':'Model'})]})
    with pytest.raises(WorkbenchError):refresh(root,store)
    assert store.active()==before['id']
    assert (root/'Assets/Registry/asset-index.json').read_bytes()==index


def test_bad_version_evidence_preserves_snapshot_and_index(fixture):
    root,store=fixture;before=refresh(root,store);index=(root/'Assets/Registry/asset-index.json').read_bytes()
    reg=json.loads((root/'Assets/Registry/registry.json').read_text());reg['version_reviews']='Assets/Registry/mappings/version-reviews.json';put(root,'Assets/Registry/registry.json',reg)
    text={'zh':'记录','en':'Recorded'}
    row=dict(id='failed',asset_id='example',title='Failed',kind='integration_revision',document='Docs/Development/check.md',summary='Failed',scope='Local',result='fail',media_ids=['not-registered'],review=dict(basis='technical',problem=text,changes=text,decision=text))
    put(root,reg['version_reviews'],{'revisions':[row]})
    with pytest.raises(WorkbenchError):refresh(root,store)
    assert store.active()==before['id']
    assert (root/'Assets/Registry/asset-index.json').read_bytes()==index


def test_viewpoints_require_registered_images_unique_identity_and_safe_provenance():
    rows=[dict(id='v',asset_id='a',media_ids=['one','two'])]
    view=dict(key='a:front',label={'zh':'正面','en':'Front'},basis='capture_recipe',source='Tools/Modeling/Test/render.py')
    assert merge(rows,{'image_views':{'one':view}})[0]['image_views']['one']==view
    assert 'image_views' not in rows[0]
    for views in ({'unknown':view},{'one':view,'two':view},{'one':{**view,'source':'../../private.json'}},{'one':{**view,'source':'Assets/private.json'}},{'one':{**view,'label':{'zh':'正面'}}}):
        with pytest.raises(ValueError):merge(rows,{'image_views':views})


def test_view_source_is_not_an_unrestricted_file_reader(fixture):
    root,store=fixture
    importer=Importer(root,store)
    with pytest.raises(WorkbenchError,match='登记来源'):importer.read('Tools/Modeling/Test/render.py')
    assert not importer.sources


def test_current_trial_selector_schema_preserves_pending_review_and_no_invented_checks(fixture):
    root,store=fixture
    manifest='Unreal/Variants/Audio/SOURCE_MANIFEST.json'
    digest=put(root,manifest,dict(files=[dict(path='Source/test.cpp',sha256='a'*64,size_bytes=12)]))
    path='Docs/Development/CURRENT_AUDIO.json'
    put(root,path,dict(source_project='Unreal/Variants/Audio/Project',source_manifest=manifest,source_manifest_sha256=digest,game_sha256='b'*64,status='local_playtest_delivered_human_review_pending',selected_build='game_v5',human_review='pending',checks='tmp/g1-audio/CHECKS.json'))
    importer=Importer(root,store);importer.build(dict(id='trial',channel='diagnostic',title='Trial',path=path,assets=[]))
    build=importer.entities['builds'][0]
    assert build['source_snapshot']=='Unreal/Variants/Audio/Project'
    assert build['revision']=='game_v5' and build['human_review']=='pending'
    assert build['checks_record']=='tmp/g1-audio/CHECKS.json'
    assert not importer.entities['evidence']


def test_invalid_view_annotation_preserves_snapshot_and_navigation(fixture):
    root,store=fixture;before=refresh(root,store);index=(root/'Assets/Registry/asset-index.json').read_bytes()
    reg=json.loads((root/'Assets/Registry/registry.json').read_text());reg['version_reviews']='Assets/Registry/mappings/version-reviews.json';put(root,'Assets/Registry/registry.json',reg)
    put(root,reg['version_reviews'],{'image_views':{'not-registered':dict(key='a:front',label={'zh':'正面','en':'Front'},basis='capture_recipe',source='Tools/Modeling/Test/render.py')}})
    with pytest.raises(WorkbenchError):refresh(root,store)
    assert store.active()==before['id']
    assert (root/'Assets/Registry/asset-index.json').read_bytes()==index


def test_medical_history_and_known_rejections_are_indexed_without_runtime_promotion(tmp_path):
    store=Store(tmp_path/'versions.sqlite3');s=refresh(ROOT,store)['id']
    versions=store.list(s,'revisions');medical=[v for v in versions if v['asset_id']=='medical-pouch']
    stages=[v for v in medical if v['id'].startswith('medical-pouch-') and 'review' in v]
    assert len(stages)==13
    assert all(v['media_ids'] and v['review']['decision']['en'] for v in stages)
    failed=next(v for v in medical if v['id']=='medical-pouch-finish-v2-20261017')
    assert failed['result']=='fail' and '136' in failed['review']['problem']['en']
    accepted=next(v for v in medical if v['id']=='medical-pouch-stain-v2-20261017')
    assert accepted['review']['basis']=='human'
    current=next(v for v in medical if v.get('adoption',{}).get('primary'))
    assert current['id']=='medical-pouch-human-accepted-20261017'
    assert current['adoption']['previous_id']=='medical-pouch-stain-v1-20261017'
    assert len(current['image_views'])==7
    previous=next(v for v in medical if v['id']==current['adoption']['previous_id'])
    assert {v['key'] for v in previous['image_views'].values()}=={'medkit:hero','medkit:detail'}
    assert {v['camera_group'] for v in current['image_views'].values()}=={'medkit-imported-v1'}
    assert all(v['source_id'] for v in current['image_views'].values())
    assert not accepted.get('adoption')  # Duplicate appearance record is not a second adopted model.
    asset=store.get(s,'assets','medical-pouch');assert len(asset['models'])==1
    design=store.get(s,'gameplay','medical-kits');assert design['implementation']['state']=='diagnostic'
    assert design['validation']['state']=='scoped_verified'
    assert design['asset_ids']==['medical-pouch']
    rejected=next(v for v in versions if v['id']=='frag-grenade-thumb-opposition-rejected-20261016')
    assert rejected['result']=='human_rejected' and len(rejected['media_ids'])>1
    assert rejected['review']['basis']=='human'
    # Every registered historical image has an exact surviving original, not an inferred cover.
    media={m['id']:m for m in store.list(s,'media')}
    reviewed=[v for v in versions if v.get('review')]
    for ident in {i for v in reviewed for i in v['media_ids']}:
        m=media[ident];raw=(ROOT/m['path']).read_bytes()
        assert len(raw)==m['size_bytes'] and hashlib.sha256(raw).hexdigest()==m['sha256']
