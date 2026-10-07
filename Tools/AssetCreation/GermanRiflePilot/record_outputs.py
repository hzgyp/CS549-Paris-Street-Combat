"""Non-secret pilot inventory: generated artifacts, references and source hashes."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[3]
store=root/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1'
dest=root/'Assets/Integration/GERMAN_RIFLE_PILOT_INVENTORY_20261003.json'
if dest.exists():raise RuntimeError('Preserve occupied manifest')
def entry(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return {'path':path.relative_to(root).as_posix(),'size_bytes':path.stat().st_size,'sha256':h.hexdigest()}
files=[]
for folder in ('references','incoming','blender','exports','evidence'):
    files.extend(entry(p) for p in sorted((store/folder).rglob('*')) if p.is_file())
sources=[entry(p) for p in sorted(Path(__file__).parent.glob('*.py'))]
a=store/'blender/adapt_v2/Kar98k_WorldCandidate_v2.glb';b=store/'exports/reproduced_v2/Kar98k_WorldCandidate_v2.glb'
data={'schema_version':1,'date':'2026-10-03','status':'local_pilot_production_gate_not_passed',
      'restoration_authority':'None; not Catalog, SFTP baseline, native import or automatic restore authority',
      'cloud_task':3919866,'base_calls':1,'gift_credit_debit':20,'gift_balance_after':240,
      'bounded_blender_repairs':2,'basic_export_checks_passed':14,'production_visual_pass':False,
      'reproduced_v2_glb_sha_identical':entry(a)['sha256']==entry(b)['sha256'],
      'limitations':['UV/color artifacts after reduction','Jagged incomplete handle cuts','Only exterior handle separated, not whole bolt','Soft receiver/sight and flawed front silhouette','Museum replacement sling retained','Welded topology risks remain','UE/history/rights for generated distribution not reviewed'],
      'sensitive_state_excluded':True,'files':files,'source_files':sources}
dest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'manifest':str(dest),'files':len(files),'sources':len(sources),'reproduction_sha_match':data['reproduced_v2_glb_sha_identical']}))
