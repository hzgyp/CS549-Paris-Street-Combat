"""Record the partial normal candidate and failed surface gate, no publication."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7'
DEST=ROOT/'Assets/Integration/GERMAN_RIFLE_FINISH_INVENTORY_20261003.json'
assert not DEST.exists()
def row(p):
    return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
audit=json.loads((BASE/'independent_audit_v3.json').read_text());guard=json.loads((BASE/'protected_after.json').read_text())
assert audit['allPass'] and audit['glbBytesReproduced'] and guard['allPass']
pngs=sorted(BASE.rglob('*.png'));inspected=[p for p in pngs if 'normals_rerun' not in p.parts]
assert len(pngs)==70 and len(inspected)==56
record={'schema_version':1,'date':'2026-10-03','owner':'yg745','status':'local_partial_normals_repair_surface_gate_failed',
        'restoration_authority':'None; LocalWorking candidate, no Catalog/native/SFTP selection',
        'whole_rifle_finished':False,'german_production_accepted':False,'triangles':299479,'meshes':2,
        'geometry_uv_image_material_changes':False,'rifle_corner_normals_changed':True,'metal_selection_accepted':False,
        'images_generated':len(pngs),'images_actually_inspected':[p.relative_to(ROOT).as_posix() for p in inspected],
        'cloud_calls':0,'credit_debit':0,'audit':audit,'protected_after':guard,
        'files':[row(p) for p in sorted(BASE.rglob('*')) if p.is_file()],
        'source_files':[row(p) for p in sorted(Path(__file__).parent.iterdir()) if p.is_file() and p.suffix in ('.py','.md')]}
DEST.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'inventory':str(DEST),'private_files':len(record['files']),'source_files':len(record['source_files']),
                  'generated_pngs':len(pngs),'inspected_pngs':len(inspected),'glb_sha256':audit['glbSha256']}))
