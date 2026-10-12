"""Pin native action identities and package-local mesh choices for lazy conversion."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];STATE=ROOT/'Assets/LocalWorking/AssetWorkbench';BASE=STATE/'native-covers-v1';OUT=STATE/'animation-viewer-v1'
defaults={j['asset_id']:j for j in json.loads((OUT/'defaults.json').read_text())};packs={}
expected={}
for manifest in sorted(BASE.glob('batch-*/jobs.json'))+[BASE/'repair-movement/jobs.json']:
 content=manifest.parent/'Project/Content'
 for job in json.loads(manifest.read_text()):
  for item in job.get('package_mappings',[]):expected[str(content/(item['package'][6:]+'.uasset'))]=item['sha256']
def digest(p):
 # These are extraction-time hashes of the same private copies; runtime verifies selected inputs before load.
 return expected[str(p)] if str(p) in expected else hashlib.sha256(p.read_bytes()).hexdigest()
for file in sorted(BASE.glob('batch-*/animation-directory-v1.json'))+[BASE/'repair-movement/animation-directory-v1.json']:
 for row in json.loads(file.read_text()):
  if row['id']=='anim-movement-animset-pro' and file.parent.name!='repair-movement':continue
  job=defaults[row['id']];source=job['source'];content=Path(row['project']).parent/'Content'
  def native(path):return content/(path.split('.')[0][6:]+'.uasset')
  clips=[]
  for c in sorted(row['clips'],key=lambda c:(c['name'].casefold(),c['path'])):
   p=native(c['path']);assert p.is_file(),p
   clips.append(dict(c,id=hashlib.sha256((row['id']+'|'+c['path']).encode()).hexdigest()[:24],source_path=p.relative_to(ROOT).as_posix(),sha256=digest(p)))
  preferred=source['mesh'];meshes=list(dict.fromkeys([preferred]+row['meshes']))
  mesh_files=[dict(path=m,source_path=native(m).relative_to(ROOT).as_posix(),sha256=digest(native(m))) for m in meshes]
  assert any(c['id']==job['id'] for c in clips),(row['id'],'default absent')
  packs[row['id']]=dict(id=row['id'],project=Path(row['project']).relative_to(ROOT).as_posix(),source_sha256=source['source_sha256'],default_clip=job['id'],preferred_mesh=preferred,meshes=mesh_files,clips=clips,external_mannequin=bool(source.get('preview_dependency')))
assert len(packs)==125
dest=STATE/'private-records/animation-packs.json';dest.write_text(json.dumps({'version':1,'packs':packs},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'packs':len(packs),'clips':sum(len(p['clips']) for p in packs.values())}))
