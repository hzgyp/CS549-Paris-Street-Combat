"""Inventory new partial local repair without selecting/publishing asset bytes."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6'
DEST=ROOT/'Assets/Integration/GERMAN_RIFLE_JOINT_INVENTORY_20261003.json'
assert not DEST.exists()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)}
audit=json.loads((BASE/'independent_audit.json').read_text());prior=json.loads((BASE/'prior_after.json').read_text());native=json.loads((BASE/'native_after.json').read_text())
assert audit['allPass'] and audit['glbBytesReproduced'] and prior['all_pass'] and native['all_pass']
pngs=list(BASE.rglob('*.png'));assert len(pngs)==22
r={'schema_version':1,'date':'2026-10-03','owner':'yg745','status':'local_partial_ball_repair_root_proof_failed',
   'restoration_authority':'None; LocalWorking partial repair, no Catalog/native selection',
   'german_production_accepted':False,'local_ball_visual_improvement':'modest; inspected fixed clay/PBR views',
   'root_joint_selected':False,'whole_rifle_finished':False,'material_changes':False,
   'triangles':299479,'selected_faces':1918,'changed_vertices':1129,'max_displacement_m':audit['maxDisplacementM'],
   'images_generated_and_inspected':len(pngs),'cloud_calls':0,'credit_debit':0,'native_runtime_tested':False,
   'audit':audit,'prior_checks':prior,'native_checks':native,
   'files':[row(p) for p in sorted(BASE.rglob('*')) if p.is_file()],
   'source_files':[row(p) for p in sorted(Path(__file__).parent.iterdir()) if p.is_file() and p.suffix in ('.py','.md')]}
DEST.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps({'inventory':str(DEST),'private_files':len(r['files']),'source_files':len(r['source_files']),'pngs':len(pngs),'all_guards':True}))
