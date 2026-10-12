import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];STATE=ROOT/'Assets/LocalWorking/AssetWorkbench';OUT=STATE/'animation-viewer-v1';OUT.mkdir(exist_ok=True)
review=json.loads((STATE/'native-covers-v1/review/report.json').read_text());jobs=[]
for row in review['captured']:
 capture=ROOT/row['folder'];export=capture.parent/('export-v5' if capture.name=='capture-v9' else 'export-v4');source=json.loads((export/'result.json').read_text())
 cid=hashlib.sha256((row['id']+'|'+source['animation']).encode()).hexdigest()[:24]
 jobs.append({'id':cid,'asset_id':row['id'],'name':source['animation'].split('.')[-1],'fbx':str(export/'source-action.fbx'),'fbx_sha256':source['fbx_sha256'],'output':str(OUT/'cache'/cid),'source':source,'fps':row['import_fps']})
(OUT/'defaults.json').write_text(json.dumps(jobs,indent=2));print('Default conversion jobs',len(jobs))
