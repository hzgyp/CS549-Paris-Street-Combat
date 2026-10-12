"""Register existing grenade previews and verified integration metadata; never alter models."""
import hashlib
import json
from pathlib import Path
from app.models import validate_glb
from asset_index import atomic_write

ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/'Assets/LocalWorking/AssetWorkbench'
SHOTS=STATE/'runs/grenade-models-capture-v1'
OUT=STATE/'runs/grenade-models-registration-v1'
OUT.mkdir(parents=True,exist_ok=True)

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def relative(path):return path.relative_to(ROOT).as_posix()
def save(path,data):atomic_write(ROOT/path,(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

paths={
 'models':'Assets/LocalWorking/AssetWorkbench/private-records/models.json',
 'media':'Assets/LocalWorking/AssetWorkbench/private-records/media.json',
 'inventory':'Assets/Registry/assets/inventory.json',
 'history':'Assets/Registry/mappings/inventory-history.json'
}
data={key:load(path) for key,path in paths.items()}
original={key:digest(ROOT/path) for key,path in paths.items()}
current=load('Docs/Development/CURRENT_UI_REVIEW.json')
parent=load('Docs/Development/CURRENT_GRENADE_MODEL_REVIEW.json')
input_review=load('Docs/Development/CURRENT_EQUIPMENT_INPUT_REVIEW.json')
assert current['game_sha256']==input_review['game_sha256'],'Current input/UI identity differs'
assert current['source_snapshot']=='Unreal/Variants/G1EquipmentWheel20261011/Project','Review latest source before registering another candidate'
protected={}
runtime=[]
checks=[]
for check in current['checks']:
 raw=(ROOT/check['result']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==check['sha256'],'Existing Game result changed'
 assert json.loads(raw)['status']==check['status'] and check['status'].startswith('pass'),'Existing Game result not passed'
 checks.append({k:check[k] for k in ('mode','result','status','sha256')})
for selector in (current,parent):
 manifest=ROOT/selector['source_manifest'];assert digest(manifest)==selector['source_manifest_sha256'],'Source manifest changed'
 protected[relative(manifest)]=digest(manifest)
 for f in selector['assets']:
  path=ROOT/selector['playable_directory']/f['path']
  assert path.stat().st_size==f['size_bytes'] and digest(path)==f['sha256'],('Runtime input changed',relative(path))
  protected[relative(path)]=f['sha256'];runtime.append({'path':relative(path),**{k:f[k] for k in ('sha256','size_bytes')}})
game=ROOT/current['playable_directory']/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
assert digest(game)==current['game_sha256'],'Current Game changed'
protected[relative(game)]=current['game_sha256']
rows=[]
for aid,label,en,report_path in [
 ('frag-grenade','Mk II 手雷模型 v1','Mk II grenade model v1','Assets/LocalWorking/Experiments/GrenadeModels/20261011/frag_finish_v1/REPORT.json'),
 ('smoke-grenade','AN-M8 烟雾弹模型 v1','AN-M8 smoke grenade model v1','Assets/LocalWorking/Experiments/GrenadeModels/20261011/smoke/finish_v1/REPORT.json')]:
 model=next(m for m in data['models']['models'] if m['id']==aid+'-model-v1-20261011')
 path=ROOT/model['path'];raw=path.read_bytes();assert digest(path)==model['sha256'],'Model changed'
 doc=validate_glb(raw);assert not doc.get('animations'),'Expected static prop'
 triangles=sum(doc['accessors'][p['indices']]['count']//3 for mesh in doc['meshes'] for p in mesh['primitives'])
 report=load(report_path);assert triangles==report['triangles'],'Model triangle count differs'
 protected[model['path']]=model['sha256']
 for source in model['source_files']:
  assert digest(ROOT/source['path'])==source['sha256'],'Authoring source changed'
  protected[source['path']]=source['sha256']
 model.update(label=label,label_en=en,scope='模型 v1 · 原始PBR · 静态外观',scope_en='Model v1 · Source PBR · Static exterior')
 media_ids=[]
 for angle,zh,english in [('front','正面','Front'),('side','侧面','Side')]:
  shot=SHOTS/(aid+'-'+angle+'.png');assert shot.is_file(),'Actual browser capture required'
  mid=aid+'-model-v1-browser-'+angle;media_ids.append(mid)
  record={'id':mid,'asset_id':aid,'path':relative(shot),'sha256':digest(shot),'size_bytes':shot.stat().st_size,'mime':'image/png',
          'label':label+' · '+zh,'label_en':en+' · '+english,'kind':'模型3D实图','audience':'local_owner',
          'rights_basis':'User-authorized local internal preview of the registered model; source rights unchanged',
          'model_id':model['id'],'model_sha256':model['sha256'],'actual_capture':True}
  data['media']['files']=[m for m in data['media']['files'] if m['id']!=mid];data['media']['files'].insert(0,record)
 asset=next(a for a in data['inventory']['assets'] if a['id']==aid)
 docpath='Docs/Development/MissionLoopV1/EQUIPMENT_WHEEL_INPUT_RESULT_20261011_ZH.md'
 asset['documents']=list(dict.fromkeys(asset['documents']+[docpath]))
 asset['validation']='源GLB与当前候选运行文件已核对；人工复验待定'
 if aid=='frag-grenade':asset['description']='Mk II 手雷；从现有盟军装备提取，保留几何与PBR。当前装备切换候选使用模型 v1。'
 else:asset['description']='AN-M8 风格烟雾弹；自建灰罐黄标外壳与PBR。当前装备切换候选使用模型 v1。'
 for member in data['inventory']['members'][aid]:
  if member['kind'] in ('RuntimeGeometry','Texture2DPNG'):
   old_prefix=parent['playable_directory']+'/'
   assert member['path'].startswith((old_prefix,current['playable_directory']+'/'))
   member['path']=member['path'].replace(old_prefix,current['playable_directory']+'/',1)
 for rule in data['inventory']['usage_rules']:
  if rule['asset_id']==aid and rule['filename']=='ParisTacticalEquipment.cpp':rule['label']='装备类型与显示入口：'+('手雷' if aid=='frag-grenade' else '烟雾弹')
 revision=next(r for r in data['history']['revisions'] if r['id']==model['id'])
 revision.update(title=label,model_identity=model['sha256'],media_ids=media_ids,parent_ids=[aid+'-equipment-v16-20261011'])
 revision['metrics'].update(model_glb_sha256=model['sha256'],dimensions_cm=[round(x*100,3) for x in report['dimensions_m']])
 old_revision=next(r for r in data['history']['revisions'] if r['id']==aid+'-equipment-v16-20261011')
 old_revision['media_ids']=['inv-'+aid+'-0']
 rid=aid+'-wheel-integration-v4-20261011'
 new={'id':rid,'asset_id':aid,'title':'滚轮装备整合 v4 (2026-10-11)','kind':'integration_revision','result':'local_verified_manual_review_pending',
      'parent_ids':[revision['id']],'model_identity':model['sha256'],'summary':'模型 v1 字节沿用；滚轮选择、左键准备/松开投掷，当前统一候选待人工复验。',
      'scope':'读取已有14项最终Game记录；本次只核对文件与平台预览，没有重新运行游戏验收。',
      'document':docpath,'metrics':{'model_glb_sha256':model['sha256'],'game_sha256':current['game_sha256'],'source_manifest_sha256':current['source_manifest_sha256']},'media_ids':media_ids}
 data['history']['revisions']=[r for r in data['history']['revisions'] if r['id']!=rid]+[new]
 rows.append({'asset_id':aid,'model_id':model['id'],'model_sha256':model['sha256'],'triangles':triangles,'media_ids':media_ids,'integration_revision':rid})
by_id={m['id']:m for m in data['media']['files']}
fronts=[by_id[row['media_ids'][0]] for row in rows]
data['media']['files']=fronts+[m for m in data['media']['files'] if m['id'] not in {x['id'] for x in fronts}]
assert all(digest(ROOT/p)==h for p,h in protected.items()),'Protected input changed'
for key,path in paths.items():
 assert digest(ROOT/path)==original[key],('Registration changed during update',path)
 backup=OUT/(key+'-before.json')
 if not backup.exists():backup.write_bytes((ROOT/path).read_bytes())
 save(path,data[key])
assert all(digest(ROOT/p)==h for p,h in protected.items()),'Protected input changed'
save(relative(OUT/'registration.json'),{'status':'registered_pending_platform_refresh','models':rows,'current_selector':'Docs/Development/CURRENT_UI_REVIEW.json',
 'game_sha256':current['game_sha256'],'runtime_files':runtime,'existing_checks_read':checks,'protected_inputs':protected,'protected_inputs_unchanged':True})
print('Registered 2 source models, 4 actual captures and 2 current integration records; protected inputs unchanged.')
