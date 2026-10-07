"""Hash current private experiment and source; no asset relocation or publication."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-v10'
SOURCE=ROOT/'Assets/LocalWorking/Intake/2026-10-03/01_MW2_Guns_Asset_Library/MW2_Guns_Asset_Library.blend'
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while data:=f.read(4*1024*1024):h.update(data)
    return h.hexdigest()
source_hash=digest(SOURCE);assert source_hash=='9e5e1a18b1608f2359e9087834cf553621759e22d67ca343ec5182159f4b3a11'
audit=json.loads((BASE/'audit_v2/audit.json').read_text());repeat=json.loads((BASE/'repeat_audit_v1/audit.json').read_text())
assert audit['passed'] and repeat['passed'] and repeat['cross_export_images_identical']
def record(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)}
obj={'date':'2026-10-04','scope':'private local SP-R donor adaptation, not production/restore authority',
     'original_source':record(SOURCE),'candidate':record(BASE/'finish_v3/GermanRifle_SPR_V10.glb'),
     'historical_approval':False,'user_visual_approval':False,'ue_runtime_approval':False,
     'rights_status':'MW2 project-use/derivative-sharing confirmation pending; no publication',
     'metrics':{k:audit[k] for k in ['triangles','dimensions_m','embedded_images']},
     'repeat_byte_identical':repeat['cross_export_byte_identical'],'repeat_geometry_uv_normal_checks_passed':True,
     'repeat_embedded_images_identical':True,
     'private_files':[record(p) for p in sorted(BASE.rglob('*')) if p.is_file()],
     'source_files':[record(p) for p in sorted(Path(__file__).parent.rglob('*')) if p.is_file() and '__pycache__' not in str(p)]}
target=ROOT/'Assets/Integration/GERMAN_RIFLE_SPR_DRAFT_INVENTORY_20261004.json'
target.write_text(json.dumps(obj,indent=2),encoding='utf-8')
print(json.dumps({'private_files':len(obj['private_files']),'source_files':len(obj['source_files']),'source_unchanged':True,'candidate_sha256':obj['candidate']['sha256']}))
