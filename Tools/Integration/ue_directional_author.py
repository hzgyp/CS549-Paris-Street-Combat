"""New-only German translation adaptation and two-axis native locomotion drafts."""
import hashlib
import json
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/P2/Retarget/directional_author_v1.json'
if OUT.exists():
    raise RuntimeError('Preserve prior authoring evidence; no automatic rerun')
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'assets': [], 'errors': []}
def checkpoint():
    OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
checkpoint()
try:
    compare = json.loads((OUT.parent / 'translation_compare_v1.json').read_text(encoding='utf-8'))
    assert compare['original_german_files_unchanged'] > 0
    for c in compare['cases']:
        if 'German' in c['mesh'] and c['clip'].endswith('Rifle_WalkFwdLoop'):
            assert max(s['mesh_min_z_cm'] for s in c['cases'][1]['samples']) < 1
    # Guard both namespaces before any authoring; do not save vendor objects.
    for path in ('/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1',
                 '/Game/ParisCombat/Animation/DirectionalDraft'):
        assert not unreal.EditorAssetLibrary.list_assets(path, recursive=True, include_folder=False), path
    german = json.loads(unreal.ParisBlueprintAuthoring.create_german_translation_draft())
    assert 'error' not in german, german
    for path in german['assets']:
        asset = unreal.load_asset(path)
        assert asset and unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False), path
        report['assets'].append(path)
    checkpoint()
    direction = json.loads(unreal.ParisBlueprintAuthoring.create_directional_draft())
    assert 'error' not in direction, direction
    report['compiler_messages'] = direction['compiler_messages']
    for path in direction['assets']:
        asset = unreal.load_asset(path)
        assert asset and unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False), path
        report['assets'].append(path)
    report['result'] = 'saved_new_drafts_pending_fresh_tests'
    report['files'] = []
    for p in report['assets']:
        relative = p.split('.')[0].removeprefix('/Game/') + '.uasset'
        f = STORE / 'Content' / relative
        report['files'].append({'path': relative, 'size': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()})
except Exception:
    report['errors'].append(traceback.format_exc())
    report['result'] = 'fail_preserve_partial_drafts'
checkpoint()
if report['errors']:
    raise RuntimeError(report['errors'][0])
unreal.log('CS549_DIRECTIONAL_AUTHOR_DONE')
