"""New-only per-sample stride-calibrated native BlendSpaces and AnimBPs."""
import hashlib
import json
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
DEST=STORE/'Evidence/P2/Retarget/stride_author_v1.json'
if DEST.exists():
    raise RuntimeError('Refusing existing stride authoring evidence')
report=json.loads(unreal.ParisBlueprintAuthoring.create_stride_draft())
assert 'error' not in report,report
report['files']=[]
for p in report['assets']:
    asset=unreal.load_asset(p)
    assert unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False),p
    relative=p.split('.')[0].removeprefix('/Game/')+'.uasset'
    f=STORE/'Content'/relative
    report['files'].append({'path':relative,'size':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
report['engine']=unreal.SystemLibrary.get_engine_version()
report['result']='saved_new_stride_drafts_pending_tests'
DEST.write_text(json.dumps(report,indent=2),encoding='utf-8')
unreal.log('CS549_STRIDE_AUTHOR_DONE')
