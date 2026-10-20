import copy
import hashlib
import json

import pytest

from app.catalog import refresh
from app.gameplay import validate
from app.security import WorkbenchError
from test_contracts import fixture, make_client, put


def registered(fixture):
    root, store = fixture
    doc = root/'Docs/Development/design.md'
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text('Reviewed gameplay rules', encoding='utf-8')
    text = lambda zh, en: {'zh': zh, 'en': en}
    row = dict(id='tutorial', kind='mission', design_state='review',
               title=text('教程方案', 'Tutorial proposal'), summary=text('待实现', 'Not implemented'),
               implementation={'state': 'unimplemented', 'note': text('尚未实现', 'No implementation')},
               validation={'state': 'pending', 'note': text('待验证', 'Pending validation')},
               asset_ids=['example'], rules=[text('有限资源', 'Finite resources')],
               documents=[{'path': 'Docs/Development/design.md', 'title': text('设计原文', 'Design source'),
                           'registered_sha256': hashlib.sha256(doc.read_bytes()).hexdigest()}])
    put(root, 'Assets/Registry/gameplay/designs.json', {'schema_version': 1, 'entries': [row]})
    path = 'Assets/Registry/registry.json'
    reg = json.loads((root/path).read_text())
    reg['gameplay'] = 'Assets/Registry/gameplay/designs.json'
    put(root, path, reg)
    return row


def test_authenticated_navigation_reverse_links_and_atomic_refresh(fixture):
    root, store = fixture
    registered(fixture)
    client, app, _ = make_client(fixture)
    data = client.get('/api/v1/gameplay?q=有限').json()['data']
    assert data['total'] == 1
    assert client.get('/api/v1/gameplay?implementation=formal').json()['data']['total'] == 0
    entry = client.get('/api/v1/gameplay/tutorial').json()['data']
    assert entry['assets'][0]['id'] == 'example' and not entry['source_changed']
    assert client.get('/api/v1/assets/example').json()['data']['gameplay'][0]['id'] == 'tutorial'
    source = client.get('/api/v1/sources/'+entry['documents'][0]['source_id']+'/excerpt')
    assert source.status_code == 200
    outputs = ['asset-index.json', 'ASSET_DIRECTORY.md', 'GAMEPLAY_DIRECTORY.md']
    before = {p: (root/'Assets/Registry'/p).read_bytes() for p in outputs}
    (root/'Docs/Development/design.md').write_text('Revised gameplay rules', encoding='utf-8')
    snap = refresh(root, app.state.store)
    revised = app.state.store.get(snap['id'], 'gameplay', 'tutorial')
    assert revised['source_changed']
    assert revised['documents'][0]['sha256'] == hashlib.sha256(b'Revised gameplay rules').hexdigest()
    index = json.loads((root/'Assets/Registry/asset-index.json').read_text())
    assert index['gameplay_count'] == 1
    assert index['assets'][0]['gameplay_references'][0]['id'] == 'tutorial'
    # A failed subsequent import must retain the complete previous publication.
    valid = {p: (root/'Assets/Registry'/p).read_bytes() for p in outputs}
    bad = json.loads((root/'Assets/Registry/gameplay/designs.json').read_text())
    bad['entries'][0]['asset_ids'] = ['missing']
    put(root, 'Assets/Registry/gameplay/designs.json', bad)
    with pytest.raises(WorkbenchError): refresh(root, app.state.store)
    assert app.state.store.active() == snap['id']
    assert valid == {p: (root/'Assets/Registry'/p).read_bytes() for p in outputs}
    assert before['asset-index.json'] != valid['asset-index.json']
    client.cookies.clear()
    assert client.get('/api/v1/gameplay').status_code == 401
    assert client.get('/api/v1/gameplay/tutorial').status_code == 401


@pytest.mark.parametrize('change', [
    lambda r: r.update(asset_ids=[{}]),
    lambda r: r.update(media_ids='invalid'),
    lambda r: r.update(related_ids=[{}]),
    lambda r: r.update(title={'zh': '仅中文'}),
    lambda r: r['validation'].update(state='passed'),
    lambda r: r['documents'][0].update(path='Assets/LocalWorking/access/secret.md'),
    lambda r: r.update(locations=[{'foot_xyz_m': [float('nan'), 0, 0]}]),
])
def test_invalid_design_registration_is_rejected(fixture, change):
    row = copy.deepcopy(registered(fixture))
    change(row)
    with pytest.raises(WorkbenchError): validate({'schema_version': 1, 'entries': [row]}, {'example'})


def test_formal_design_requires_formal_build(fixture):
    root, store = fixture
    row = registered(fixture)
    row['implementation']['state'] = 'formal'
    put(root, 'Assets/Registry/gameplay/designs.json', {'schema_version': 1, 'entries': [row]})
    with pytest.raises(WorkbenchError, match='构建依据'): refresh(root, store)


def test_duplicate_design_id_is_rejected(fixture):
    row = registered(fixture)
    with pytest.raises(WorkbenchError, match='重复'):
        validate({'schema_version': 1, 'entries': [row, row]}, {'example'})


def test_gameplay_directory_failure_rolls_back_all_outputs(fixture, monkeypatch):
    import asset_index
    root, store = fixture
    registered(fixture)
    original = refresh(root, store)
    paths = [root/'Assets/Registry'/p for p in ('asset-index.json', 'ASSET_DIRECTORY.md', 'GAMEPLAY_DIRECTORY.md')]
    before = {p: p.read_bytes() for p in paths}
    (root/'Docs/Development/design.md').write_text('Updated design', encoding='utf-8')
    real = asset_index.atomic_write
    def fail_once(path, raw):
        if path.name == 'GAMEPLAY_DIRECTORY.md' and raw != before[path]:
            raise OSError('gameplay directory unavailable')
        return real(path, raw)
    # Change a title so the third output must change as well.
    path = 'Assets/Registry/gameplay/designs.json'
    data = json.loads((root/path).read_text())
    data['entries'][0]['title']['en'] = 'Updated tutorial'
    put(root, path, data)
    monkeypatch.setattr(asset_index, 'atomic_write', fail_once)
    with pytest.raises(WorkbenchError, match='gameplay directory unavailable'): refresh(root, store)
    assert store.active() == original['id']
    assert before == {p: p.read_bytes() for p in paths}
