"""Homepage classification, current-release identity and failed-refresh preservation."""
import copy
import hashlib
import json

import pytest

from app.catalog import refresh
from app.homepage import assemble, collect
from app.security import WorkbenchError
from app.store import Store
from test_contracts import ROOT, fixture, put, protect_live_navigation_outputs


def sample():
    bi=lambda value:dict(zh=value,en=value)
    entities=dict(assets=[dict(id='actor',category='人物',models=[]),dict(id='map',category='地图',models=[])],
        revisions=[dict(id='accepted-action',asset_id='actor',adoption={'previous_id':'old-action'})],
        builds=[dict(id='formal',channel='formal',title='Release',revision='1.0',game_sha256='current',assets=['actor','map']),
                dict(id='old-formal',channel='formal',title='Old',revision='86',game_sha256='old',assets=['actor'])],
        media=[dict(id='release-image',asset_id='map',actual_capture=True,game_sha256='current',sha256='image'),
               dict(id='action-image',asset_id='actor',sha256='action')],gameplay=[dict(id='teaching')])
    config=dict(schema_version=1,release=dict(build_id='formal',gameplay_id='teaching',cover_id='release-image',title=bi('Teaching 1.0'),summary=bi('Current gameplay')),
        modules=[dict(id='actions',title=bi('Actions'),description=bi('Adopted actions'),category='人物',cards=[dict(id='hold',asset_id='actor',revision_id='accepted-action',cover_id='action-image',title=bi('Holding'),description=bi('Accepted holding'),image_label=bi('Runtime'))])])
    return config,entities


def test_current_release_and_scoped_action_links():
    config,entities=sample();home=assemble(config,entities)
    assert home['release']['build_id']=='formal' and home['release']['version']=='1.0'
    card=home['modules'][0]['cards'][0]
    assert card['status']=='adopted' and 'right=accepted-action' in card['href']
    assert 'left=old-action' in card['href']
    entities['revisions'][0]['adoption']={}
    # An empty acceptance object is not a recorded adoption.
    with pytest.raises(WorkbenchError):assemble(config,entities)


def test_later_release_never_reuses_previous_release_capture():
    config,entities=sample();entities['builds'][0]['game_sha256']='next-game'
    home=assemble(config,entities)
    assert home['release']['cover_id'] is None
    assert home['release']['cover_state']=='not_registered'
    assert home['release']['summary']['en']=='The current release preview is not registered.'


@pytest.mark.parametrize('fault',['missing_record','different_game','different_original'])
def test_formal_image_requires_matching_capture_provenance(fault):
    from types import SimpleNamespace
    config,entities=sample();cover=entities['media'][0]
    cover.update(size_bytes=100,source_record='tmp/g1-home/VISUAL_REVIEW.json')
    record=dict(game_sha256='current',frames=[dict(sha256='image',size_bytes=100)])
    if fault=='missing_record':cover.pop('source_record')
    elif fault=='different_game':record['game_sha256']='other'
    else:record['frames'][0]['sha256']='different'
    importer=SimpleNamespace(entities=entities,view_paths=set(),sources={},doc=lambda path:config if path=='config' else record)
    with pytest.raises(WorkbenchError):collect(importer,'config')


@pytest.mark.parametrize('invalid',['old_release','wrong_cover','model_in_actions','unaccepted_action','duplicate_module','duplicate_card'])
def test_reject_misleading_module_references(invalid):
    config,entities=sample()
    if invalid=='old_release':config['release']['build_id']='old-formal'
    elif invalid=='wrong_cover':entities['media'][1]['asset_id']='map'
    elif invalid=='model_in_actions':entities['assets'][0]['category']='道具'
    elif invalid=='unaccepted_action':config['modules'][0]['cards'][0].pop('revision_id')
    elif invalid=='duplicate_module':config['modules'].append(copy.deepcopy(config['modules'][0]))
    elif invalid=='duplicate_card':config['modules'][0]['cards'].append(copy.deepcopy(config['modules'][0]['cards'][0]))
    with pytest.raises(WorkbenchError):assemble(config,entities)


def test_invalid_homepage_refresh_retains_active_snapshot_and_index(fixture):
    root,store=fixture;original=refresh(root,store)['id']
    paths=['Assets/Registry/asset-index.json','Assets/Registry/ASSET_DIRECTORY.md']
    before={p:(root/p).read_bytes() for p in paths}
    registry=json.loads((root/'Assets/Registry/registry.json').read_text())
    registry['homepage']='Assets/Registry/mappings/homepage.json';put(root,'Assets/Registry/registry.json',registry)
    config,_=sample();put(root,registry['homepage'],config)
    with pytest.raises(WorkbenchError):refresh(root,store)
    assert store.active()==original
    assert all((root/p).read_bytes()==raw for p,raw in before.items())


def test_live_registered_modules_and_original_identity(tmp_path):
    store=Store(tmp_path/'home.sqlite3');snap=refresh(ROOT,store)['id']
    home=store.list(snap,'homepage')[0]
    assert [(m['id'],len(m['cards'])) for m in home['modules']]==[('actions',2),('characters',2),('scenes',1),('props',5)]
    builds={b['id']:b for b in store.list(snap,'builds')}
    assert home['release']['game_sha256']==builds['formal']['game_sha256']
    assert home['release']['source_id']
    media={m['id']:m for m in store.list(snap,'media')}
    ids=[home['release']['cover_id']]+[c['cover_id'] for m in home['modules'] for c in m['cards']]
    assert len(ids)==11 and len(set(ids))==11
    for ident in ids:
        record=media[ident];raw=(ROOT/record['path']).read_bytes()
        assert len(raw)==record['size_bytes'] and hashlib.sha256(raw).hexdigest()==record['sha256']
    assert len(store.list(snap,'assets'))==231
    assert len(store.list(snap,'gameplay'))==18
    # Props without scoped adoption records cannot inherit action acceptance.
    props=next(m for m in home['modules'] if m['id']=='props')['cards']
    assert next(c for c in props if c['asset_id']=='frag-grenade')['status']!='adopted'
