"""Private isolated copies for actual Unreal asset captures. No source writes."""
import json,re,subprocess,hashlib,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/'Assets/LocalWorking/AssetWorkbench'
OUT=STATE/'native-covers-v1'
BASE=ROOT/'Assets/LocalWorking/Intake/2026-10-01/03_UE4_Animation_Collection'
SEVEN=Path('C:/Program Files/NVIDIA Corporation/NVIDIA App/7z.exe')
facts=json.loads((ROOT/'Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog/catalog_facts.json').read_text(encoding='utf8'))
archives={p.name:p for p in BASE.rglob('*.7z')}
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def prepare(row):
 id='anim-'+re.sub('[^a-z0-9]+','-',Path(row['title']).stem.lower()).strip('-')
 dest=OUT/id;receipt=dest/'prepare.json'
 if receipt.exists():return json.loads(receipt.read_text())
 assert not row['unsafe_paths'] and row['expanded_bytes']<3*1024**3
 p=archives[row['title']];before=sha(p);password=None
 for parent in p.parents:
  match=re.search(r'(?:解压密码|密码|password|pwd)\s*[:：=]?\s*(.+)$',parent.name,re.I)
  if match:password=match.group(1).strip();break
  if parent==BASE:break
 dest.mkdir(parents=True,exist_ok=True);extract=dest/'extracted'
 args=[str(SEVEN),'x',str(p),'-o'+str(extract),'-y','-bso0','-bsp0']
 if password:args+=['-p'+password]
 with (dest/'extract.log').open('w') as log:
  result=subprocess.run(args,stdout=log,stderr=log,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW)
 assert result.returncode==0,(id,'extraction failed')
 native=list(extract.rglob('*.uasset'));assert native
 candidates=set()
 for f in native:
  candidates.update(parent for parent in f.parents if parent==extract or extract in parent.parents)
 scores={c:0 for c in candidates}
 # Original long package names embedded in package headers identify the Content root.
 for f in native[:180]:
  raw=f.read_bytes();names=set(x.decode('ascii',errors='ignore') for x in re.findall(rb'/Game/[A-Za-z0-9_ /\-]+',raw))
  for c in candidates:
   if c in f.parents:
    rel='/Game/'+f.relative_to(c).with_suffix('').as_posix()
    if rel in names:scores[c]+=1
 root=max(scores,key=scores.get)
 project=dest/'Project';project.mkdir(exist_ok=True);content=project/'Content'
 # Copies only into this isolated project. No junction to game/native originals.
 mappings=[];unresolved=[]
 content.mkdir(exist_ok=True)
 if True:
  for f in [x for x in extract.rglob('*') if x.suffix.lower() in ('.uasset','.umap')]:
   raw=f.read_bytes();names=set(x.decode('ascii',errors='ignore') for x in re.findall(rb'/Game/[A-Za-z0-9_ /\-]+',raw));own=[n for n in names if n.endswith('/'+f.stem)]
   if not own:own=[n for n in names if n.endswith('/'+re.sub(r'_\d+$','',f.stem))]
   if own:
    def suffix_score(n):
     count=0
     for a,b in zip(reversed(Path(n).parts),reversed(f.with_suffix('').parts)):
      if a.lower()!=b.lower():break
      count+=1
     return count
    own.sort(key=lambda n:(-suffix_score(n),len(n),n));rel=Path(own[0][6:]).parent/(f.stem+f.suffix)
   else:
    if scores[root]>0 and root in f.parents:rel=f.relative_to(root)
    else:
     unresolved.append(f.relative_to(extract).as_posix());rel=Path('__Unresolved')/f.relative_to(extract)
   target=content/rel;target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists():assert sha(target)==sha(f),(id,'package collision',str(rel))
   else:shutil.copyfile(f,target)
   for ext in ('.uexp','.ubulk'):
    side=f.with_suffix(ext)
    if side.exists():shutil.copyfile(side,target.with_suffix(ext))
   mappings.append({'source':f.relative_to(extract).as_posix(),'package':'/Game/'+rel.with_suffix('').as_posix(),'sha256':sha(f)})
 (project/'AssetCoverLab.uproject').write_text(json.dumps({'FileVersion':3,'EngineAssociation':'5.8','Plugins':[{'Name':'PythonScriptPlugin','Enabled':True},{'Name':'EditorScriptingUtilities','Enabled':True}]}))
 config=project/'Config';config.mkdir(exist_ok=True)
 (config/'DefaultEngine.ini').write_text('[/Script/Engine.RendererSettings]\nr.DefaultFeature.AutoExposure=False\nr.DefaultFeature.MotionBlur=False\nr.AllowStaticLighting=False\nr.Shadow.Virtual.Enable=0\nr.RayTracing=False\nr.DynamicGlobalIlluminationMethod=0\nr.ReflectionMethod=0\n[/Script/EngineSettings.GameMapsSettings]\nEditorStartupMap=/Engine/Maps/Entry\nGameDefaultMap=/Engine/Maps/Entry\n')
 with (config/'DefaultEngine.ini').open('a') as stream:stream.write('\n[/Script/WindowsTargetPlatform.WindowsTargetSettings]\nDefaultGraphicsRHI=DefaultGraphicsRHI_DX12\n-D3D12TargetedShaderFormats=PCD3D_SM5\n+D3D12TargetedShaderFormats=PCD3D_SM6\n')
 out=dict(id=id,title=row['title'],source=p.relative_to(ROOT).as_posix(),source_sha256=before,content_root=root.relative_to(dest).as_posix(),root_match_count=scores[root],package_mappings=mappings,unresolved_packages=unresolved,native_count=len(native),project=str(project/'AssetCoverLab.uproject'),inputs_unchanged=sha(p)==before)
 assert out['inputs_unchanged'];receipt.write_text(json.dumps(out,indent=2));print('PREPARED',id,len(native),flush=True);return out
if __name__=='__main__':
 for row in facts['archives']:
  if len(sys.argv)>1 and sys.argv[1] not in row['title']:continue
  try:prepare(row)
  except Exception as exc:print('PREPARE_FAILED',row['title'],str(exc),flush=True)
