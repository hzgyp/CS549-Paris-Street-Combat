"""Group only byte-identical shared package paths; conflicting deliveries stay isolated."""
from prepare_native_covers import *
import os
groups=[];jobs=[]
for receipt in sorted(OUT.glob('*/prepare.json')):
 job=json.loads(receipt.read_text());content=receipt.parent/'Project/Content'
 recorded={m['package'][6:]+Path(m['source']).suffix:m['sha256'] for m in job.get('package_mappings',[])}
 files={}
 for p in content.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.uasset','.umap','.ubulk','.uexp'):
   key=p.relative_to(content).as_posix();files[key]=recorded[key] if key in recorded else sha(p)
 job['paths']=['/Game/'+str(Path(p).with_suffix('')).replace('\\','/') for p in files if p.endswith('.uasset')];job['directory']=str(receipt.parent)
 selected=next((g for g in groups if len(g['jobs'])<24 and not any(p in g['files'] and g['files'][p]!=h for p,h in files.items())),None)
 if selected is None:selected={'jobs':[],'files':{},'sources':{}};groups.append(selected)
 selected['jobs'].append(job)
 for p,h in files.items():selected['files'][p]=h;selected['sources'][p]=content/p
for i,g in enumerate(groups):
 dest=OUT/f'batch-{i:02d}';project=dest/'Project';content=project/'Content';content.mkdir(parents=True,exist_ok=True)
 for rel,p in g['sources'].items():
  target=content/rel;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():assert sha(target)==g['files'][rel]
  else:os.link(p,target)
 first=Path(g['jobs'][0]['project']).parent
 shutil.copyfile(first/'AssetCoverLab.uproject',project/'AssetCoverLab.uproject')
 shutil.copytree(first/'Config',project/'Config',dirs_exist_ok=True)
 cfg=project/'Config/DefaultEngine.ini'
 if 'D3D12TargetedShaderFormats=PCD3D_SM6' not in cfg.read_text():
  with cfg.open('a') as stream:stream.write('\n[/Script/WindowsTargetPlatform.WindowsTargetSettings]\nDefaultGraphicsRHI=DefaultGraphicsRHI_DX12\n-D3D12TargetedShaderFormats=PCD3D_SM5\n+D3D12TargetedShaderFormats=PCD3D_SM6\n')
 (dest/'jobs.json').write_text(json.dumps(g['jobs'],indent=2))
 print('BATCH',i,len(g['jobs']),len(g['files']),flush=True)
