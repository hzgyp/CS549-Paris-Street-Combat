import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();dest=Path(a.output).resolve();assert not dest.exists()
checks=[]
for label in ('PILOT','REFINEMENT','PART_SPLIT','SURFACE','ALLIED_REFERENCE','JOINT'):
    d=json.loads((ROOT/f'Assets/Integration/GERMAN_RIFLE_{label}_INVENTORY_20261003.json').read_text(encoding='utf-8-sig'));bad=[]
    for r in d['files']+d['source_files']:
        f=ROOT/r['path']
        if not f.is_file() or f.stat().st_size!=r['size_bytes'] or sha(f)!=r['sha256']:bad.append(r['path'])
    checks.append({'name':label,'files':len(d['files']),'sources':len(d['source_files']),'mismatches':bad})
for name in ('CITY_CONTINUOUS_ARMS_NATIVE','PLAYER_ACTIONS_DRAFT'):
    d=json.loads((ROOT/f'Assets/Integration/{name}_INVENTORY_20261003.json').read_text(encoding='utf-8-sig'))
    bad=[r['path'] for r in d['files'] if not (ROOT/r['path']).is_file() or (ROOT/r['path']).stat().st_size!=r['size_bytes'] or sha(ROOT/r['path'])!=r['sha256']]
    checks.append({'name':name,'files':len(d['files']),'sources':0,'mismatches':bad})
ally=json.loads((ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-ally-reference-v5/inspection/ally_parameters.json').read_text())
refs=[{'path':ally['sourceBlend'],'sha256':ally['sourceBlendSha256']}]+[{'path':t['path'],'sha256':t['sha256']} for t in ally['textures']]
for r in refs:r['matches']=sha(ROOT/r['path'])==r['sha256']
result={'checks':checks,'M1':refs,'allPass':all(not r['mismatches'] for r in checks) and all(r['matches'] for r in refs)}
dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result));assert result['allPass']
