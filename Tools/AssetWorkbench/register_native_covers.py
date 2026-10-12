"""Publish only reviewed genuine UE capture files into the local catalog."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];STATE=ROOT/'Assets/LocalWorking/AssetWorkbench';OUT=STATE/'native-covers-v1'
review=json.loads((OUT/'review/report.json').read_text());approval=json.loads((OUT/'review/visual-review.json').read_text())
assert not review['pending_or_failed'] and len(review['captured'])==125
approved=set(approval['approved_asset_ids']);assert len(approved)==125
path=STATE/'private-records/media.json';media=json.loads(path.read_text(encoding='utf8'))
media['files']=[m for m in media['files'] if m.get('kind')!='supplier thumbnail' and not m.get('native_cover')]
for row in review['captured']:
 assert row['id'] in approved
 for i,capture in enumerate(row['captures']):
  file=ROOT/row['folder']/capture['file'];h=hashlib.sha256(file.read_bytes()).hexdigest();assert h==capture['sha256']
  media['files'].append(dict(id=f"native-cover-{row['id']}-{i}",asset_id=row['id'],path=file.relative_to(ROOT).as_posix(),sha256=h,size_bytes=file.stat().st_size,mime='image/png',audience='local_owner',rights_basis='Actual local UE source opening and Blender FBX capture; internal viewing only',label=('原始动作预览（外部预览人偶、中性材质） · ' if row.get('preview_dependency') else '原生动作预览（中性材质） · ')+row['animation'].split('/')[-1].split('.')[0]+f" · {capture['fraction']:.0%}",kind='Native action capture',native_cover=True,provenance={'source_sha256':row['source_sha256'],'engine':row['engine'],'renderer':row['renderer'],'mesh':row['mesh'],'skeleton':row['skeleton'],'animation':row['animation'],'time_s':capture['time'],'capture_sha256':h,'neutral_material':row.get('neutral_material',False),'preview_dependency':row.get('preview_dependency'),'fraction':capture['fraction'],'native_duration_s':row['duration'],'export_duration_s':row.get('export_duration_s'),'binding':row.get('binding','validated matching bind poses')}))
sample=next(m for m in media['files'] if m['asset_id']=='anim-rifle-animset-pro' and m.get('native_cover'))
media['files'].append(dict(sample,id='native-cover-animation-collection',asset_id='ue4-animation-collection',label='原生动作预览（中性材质） · Rifle Animset Pro'))
path.write_text(json.dumps(media,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'supplier_images':0,'native_covers':251,'covered_entries':126,'total_media':len(media['files'])}))
