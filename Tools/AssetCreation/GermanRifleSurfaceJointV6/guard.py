"""Read-only old manifest/reference/native protection and result inventory."""
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)}
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
dest=Path(a.output).resolve();assert not dest.exists()
checks=[]
for label in ('PILOT','REFINEMENT','PART_SPLIT','SURFACE','ALLIED_REFERENCE'):
    name=f'GERMAN_RIFLE_{label}_INVENTORY_20261003.json'
    d=json.loads((ROOT/'Assets/Integration'/name).read_text(encoding='utf-8-sig'));bad=[]
    for r in d['files']+d['source_files']:
        f=ROOT/r['path']
        if not f.is_file() or f.stat().st_size!=r['size_bytes'] or sha(f)!=r['sha256']:bad.append(r['path'])
    checks.append({'manifest':name,'private_files':len(d['files']),'source_files':len(d['source_files']),'mismatches':bad})
ally=json.loads((ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-ally-reference-v5/inspection/ally_parameters.json').read_text())
refs=[{'path':ally['sourceBlend'],'sha256':ally['sourceBlendSha256']}]+[{'path':t['path'],'sha256':t['sha256']} for t in ally['textures']]
for r in refs:r['matches']=sha(ROOT/r['path'])==r['sha256']
result={'old_rifle_records':checks,'m1_reference':refs,'all_pass':not any(c['mismatches'] for c in checks) and all(r['matches'] for r in refs)}
dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'all_pass':result['all_pass'],'old_rifle_private':sum(c['private_files'] for c in checks),'old_rifle_sources':sum(c['source_files'] for c in checks),'M1_files':len(refs)}))
raise SystemExit(0 if result['all_pass'] else 1)
