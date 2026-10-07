"""Hash private failed drafts and verify all earlier rifle records, no publication."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-surface-v4'
DEST=ROOT/'Assets/Integration/GERMAN_RIFLE_SURFACE_INVENTORY_20261003.json'
assert not DEST.exists(),'Preserve occupied inventory'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def entry(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)}
prior=[]
for name in ('GERMAN_RIFLE_PILOT_INVENTORY_20261003.json','GERMAN_RIFLE_REFINEMENT_INVENTORY_20261003.json','GERMAN_RIFLE_PART_SPLIT_INVENTORY_20261003.json'):
    d=json.loads((ROOT/'Assets/Integration'/name).read_text(encoding='utf-8-sig'));bad=[]
    for e in d['files']+d['source_files']:
        p=ROOT/e['path']
        if not p.is_file() or p.stat().st_size!=e['size_bytes'] or sha(p)!=e['sha256']:bad.append(e['path'])
    prior.append({'manifest':name,'files':len(d['files']),'source_files':len(d['source_files']),'mismatches':bad})
native=json.loads((BASE/'protected_after.json').read_text())
audit=json.loads((BASE/'independent_audit_v2.json').read_text())
assert native['all_pass'] and audit['allSourceGeometryAndUvPreserved'] and not any(x['mismatches'] for x in prior)
result={'schema_version':1,'date':'2026-10-03','owner':'yg745','status':'early_surface_label_visual_gate_failed',
        'restoration_authority':'None; LocalWorking failed diagnostics, not Catalog/SFTP/native restore',
        'geometry_refinement_executed':False,'selected_improved_asset':False,'cloud_calls':0,'credit_debit':0,
        'triangles':299479,'fresh_import_meshes':2,'generated_images':18,'actually_inspected_images':11,
        'source_geometry_uv_exact':True,'visual_pass':False,'production_pass':False,
        'failed_identities':['interface_v1 export API','interface_v1b rectangular labels','contour_v1 labels','independent_audit first float32 path'],
        'prior_checks':prior,'native_checks':native,
        'files':[entry(p) for p in sorted(BASE.rglob('*')) if p.is_file()],
        'source_files':[entry(p) for p in sorted((ROOT/'Tools/AssetCreation/GermanRifleSurfaceV4').iterdir()) if p.is_file()]}
DEST.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'manifest':DEST.relative_to(ROOT).as_posix(),'private_files':len(result['files']),'source_files':len(result['source_files']),
                  'prior_checks':prior,'native50_unchanged':native['all_pass'],'visual_pass':False}))
