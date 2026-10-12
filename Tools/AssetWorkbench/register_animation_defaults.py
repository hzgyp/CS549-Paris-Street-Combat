import json,hashlib
from pathlib import Path
from app.models import validate_glb
ROOT=Path(__file__).resolve().parents[2];STATE=ROOT/'Assets/LocalWorking/AssetWorkbench';BASE=STATE/'animation-viewer-v1'
directory=json.loads((STATE/'private-records/animation-packs.json').read_text())['packs'];defaults=json.loads((BASE/'defaults.json').read_text());path=STATE/'private-records/models.json';models=json.loads(path.read_text(encoding='utf8'))['models'];models=[m for m in models if not m.get('animation_pack_id')]
for job in defaults:
 pack=directory[job['asset_id']];clip=next(c for c in pack['clips'] if c['id']==job['id']);assert pack['source_sha256']==job['source']['source_sha256']
 receipt=Path(job['output'])/'fresh-validation-v3.json';r=json.loads(receipt.read_text());assert r['status']=='ready',(job['asset_id'],r)
 raw=Path(r['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['sha256'];doc=validate_glb(raw);assert doc.get('animations')
 r['source_sha256']=clip['sha256'];r['source_path']=clip['path'];receipt.write_text(json.dumps(r,indent=2))
 (Path(job['output'])/'current.json').write_text(json.dumps({'receipt':receipt.relative_to(ROOT).as_posix()}))
 models.append(dict(id='animation-'+job['id'],asset_ids=[job['asset_id']],path=Path(r['path']).relative_to(ROOT).as_posix(),sha256=r['sha256'],size_bytes=len(raw),audience='local_owner',label=job['name'],label_en=job['name'],revision='source animation',scope='原始动作 · 中性材质',scope_en='Source animation · Neutral material',source_files=[{'path':clip['source_path'],'sha256':clip['sha256']}],clips=[a['name'] for a in doc['animations']],animation_pack_id=job['asset_id']))
path.write_text(json.dumps({'models':models},ensure_ascii=False,indent=2),encoding='utf8');print('Registered animated packs:',len(defaults),'total model records:',len(models))
