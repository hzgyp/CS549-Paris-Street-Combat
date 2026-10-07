"""Local unfinished-work hashes. Not SFTP production/restore authority."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8'
DEST=ROOT/'Assets/Integration/GERMAN_RIFLE_TOPOLOGY_INVENTORY_20261003.json'
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args()
if a.verify:
    d=json.loads(DEST.read_text());bad=[r['path'] for r in d['files']+d['source_files'] if not (ROOT/r['path']).is_file() or row(ROOT/r['path'])!=r]
    print(json.dumps({'files':len(d['files']),'sources':len(d['source_files']),'mismatches':bad}));assert not bad
else:
    assert not DEST.exists()
    d={'date':'2026-10-03','status':'partial_standalone_mechanical_candidate_not_integrated_not_selected',
       'purpose':'Private failure evidence and analytical parts; NOT Catalog/production/teammate restore authority',
       'parts':24,'triangles':10104,'cloud_calls':0,'credit_spend':0,'ue_or_original_rifle_changes':False,
       'source_input':'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7/normals_v1/Kar98k_Normals_V7.blend',
       'evidence_png_count':37,'evidence_pngs_actually_inspected':37,
       'result':'Docs/Development/GERMAN_RIFLE_TOPOLOGY_RESULT_20261003.md',
       'files':[row(f) for f in sorted(BASE.rglob('*')) if f.is_file() and '__pycache__' not in f.parts],
       'source_files':[row(f) for f in sorted(Path(__file__).resolve().parent.iterdir()) if f.is_file()]}
    assert sum(r['path'].endswith('.png') for r in d['files'])==37
    DEST.write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps({'files':len(d['files']),'sources':len(d['source_files']),'pngs':37}))
