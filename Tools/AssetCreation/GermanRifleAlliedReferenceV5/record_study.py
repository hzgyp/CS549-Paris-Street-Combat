"""Protect existing rifle/native/M1 reference bytes and record private reference study."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-ally-reference-v5'
DEST=ROOT/'Assets/Integration/GERMAN_RIFLE_ALLIED_REFERENCE_INVENTORY_20261003.json'
assert not DEST.exists(),'Preserve occupied inventory'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)}
prior=[]
for label in ('PILOT','REFINEMENT','PART_SPLIT','SURFACE'):
    name=f'GERMAN_RIFLE_{label}_INVENTORY_20261003.json';d=json.loads((ROOT/'Assets/Integration'/name).read_text(encoding='utf-8-sig'));bad=[]
    for r in d['files']+d['source_files']:
        p=ROOT/r['path']
        if not p.is_file() or p.stat().st_size!=r['size_bytes'] or sha(p)!=r['sha256']:bad.append(r['path'])
    prior.append({'manifest':name,'private_files':len(d['files']),'source_files':len(d['source_files']),'mismatches':bad})
ally=json.loads((BASE/'inspection/ally_parameters.json').read_text());m1=[{'path':ally['sourceBlend'],'sha256':ally['sourceBlendSha256']}]+[{'path':t['path'],'sha256':t['sha256']} for t in ally['textures']]
for r in m1:r['matches']=sha(ROOT/r['path'])==r['sha256']
native=json.loads((BASE/'protected_after.json').read_text());reopen=json.loads((BASE/'reopen_verification.json').read_text())
assert not any(r['mismatches'] for r in prior) and all(r['matches'] for r in m1) and native['all_pass'] and reopen['geometryUvExactBetweenVariants'] and reopen['ownSourceAtlasBytesExact']
result={'schema_version':1,'date':'2026-10-03','owner':'yg745','status':'reference_study_complete_response_trial_not_selected',
        'restoration_authority':'None; render-only LocalWorking study, not Catalog/usable asset/native restore',
        'allied_exchange_triangles':3923,'kar_triangles_with_sling':299479,'images_generated_and_inspected':9,
        'geometry_uv_source_atlas_unchanged':True,'useful_repair_accepted':False,'german_production_accepted':False,
        'glb_exported':False,'native_runtime_tested':False,'cloud_calls':0,'credit_debit':0,
        'prior_checks':prior,'m1_reference_checks':m1,'native_checks':native,
        'files':[row(p) for p in sorted(BASE.rglob('*')) if p.is_file()],
        'source_files':[row(p) for p in sorted((ROOT/'Tools/AssetCreation/GermanRifleAlliedReferenceV5').iterdir()) if p.is_file()]}
DEST.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'inventory':DEST.relative_to(ROOT).as_posix(),'private_files':len(result['files']),'source_files':len(result['source_files']),
                  'prior_checks':prior,'m1_reference_files_unchanged':all(r['matches'] for r in m1),'native50_unchanged':native['all_pass'],'selected_improved_asset':False}))
