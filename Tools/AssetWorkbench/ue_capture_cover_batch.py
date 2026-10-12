import unreal,json,os,runpy,gc
from pathlib import Path
batch=Path(unreal.Paths.project_dir()).resolve().parent
jobs=json.loads((batch/'jobs.json').read_text())
script=Path(__file__).with_name('ue_capture_asset_cover.py')
for job in jobs:
 directory=Path(job['directory']);result=directory/'capture-v2/result.json'
 if result.exists():continue
 (directory/'allowed-packages.json').write_text(json.dumps(job['paths']))
 os.environ['COVER_JOB_DIR']=str(directory)
 runpy.run_path(str(script),run_name='__main__')
 unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
 gc.collect()
 if hasattr(unreal.SystemLibrary,'collect_garbage'):unreal.SystemLibrary.collect_garbage()
 unreal.log('COVER_BATCH_PROGRESS '+job['id'])
