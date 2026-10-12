"""Register verified local viewing copies, without modifying Catalog/game assets."""
import hashlib,json,sys
from pathlib import Path
from app.models import validate_glb,MAX_MODEL_BYTES
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'Assets/LocalWorking/AssetWorkbench/3d/export-v3'
report=json.loads((out/'export-report.json').read_text())
verification=json.loads((out/'fresh-import-validation.json').read_text())
assert verification['passed'] and report['inputs_unchanged'] and not report['errors']
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in report['inputs'].items())
models=[]
def add(id,assets,path,label,en,revision,scope,scope_en,sources):
    raw=(ROOT/path).read_bytes();doc=validate_glb(raw)
    models.append(dict(id=id,asset_ids=assets,path=path,sha256=hashlib.sha256(raw).hexdigest(),size_bytes=len(raw),audience='local_owner',label=label,label_en=en,revision=revision,scope=scope,scope_en=scope_en,source_files=sources,clips=[a['name'] for a in doc.get('animations',[])]))
names={'german-soldier':('德军源模型','German source mesh','varA / source clips'), 'allied-soldier':('盟军源模型','Allied source mesh','US Paratrooper / source clips'), 'first-person':('第一人称手臂','First-person arms','SleeveWeightsV5 / source clips'),'m1-garand':('M1 来源模型','M1 source mesh','M1 exchange')}
for row in sorted(report['models'],key=lambda r:r['id']=='m1-garand'):
    id=row['id'];label,en,revision=names[id]
    assets=[id] if id!='m1-garand' else ['allied-soldier','first-person']
    if id=='allied-soldier':assets+=['rifle-animation']
    scope='源模型与源动作；不含游戏握姿、挂枪、状态切换及 UE 服装迷彩/染色。预览贴图 ≤1024。' if row['clips'] else 'M1 来源外观；独立查看，不含游戏挂接。预览贴图 ≤1024。'
    scope_en='Source mesh and clips; excludes game grip, weapon attachment, transitions and UE clothing camouflage/tint. Preview textures ≤1024.' if row['clips'] else 'M1 source appearance; viewed separately from game attachment. Preview textures ≤1024.'
    add(id+'-browser-v3',assets,row['path'],label,en,revision,scope,scope_en,[dict(path=row['source'],sha256=row['source_sha256'])])
for id,assets,path,label,en,revision,scope,scope_en in [
 ('finewood-v15',['german-rifle'],'Assets/LocalShared/SFTP/workspaces/yg745/german-rifle-model-v1/Model/GermanRifle_FineWood_V15.glb','FineWood V15','FineWood V15','FineWoodV15','当前德军步枪模型；无内嵌动画。','Current German rifle model; no embedded animation.'),
 ('pressure-mine-v2',['pressure-mine'],'Assets/LocalWorking/Experiments/PressureMine/20261011-v1/finish_v2/PressureMine.glb','压力地雷 v2','Pressure mine v2','finish_v2','当前候选地雷模型；无内嵌动画。','Current candidate mine model; no embedded animation.')]:
    add(id,assets,path,label,en,revision,scope,scope_en,[dict(path=path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest())])
dest=ROOT/'Assets/LocalWorking/AssetWorkbench/private-records/models.json'
if dest.exists():
    generated_ids={m['id'] for m in models}
    models.extend(m for m in json.loads(dest.read_text(encoding='utf-8'))['models'] if m['id'] not in generated_ids)
dest.write_text(json.dumps({'models':models},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'models':len(models),'assets':sorted(set(a for m in models for a in m['asset_ids']))}))
