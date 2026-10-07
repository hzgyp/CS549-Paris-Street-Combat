"""Non-release diagnostic hash manifest; invoke only after all jobs finish."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PRIVATE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-wear-v13'
TARGET=ROOT/'Assets/Integration/GERMAN_RIFLE_WOOD_WEAR_V13_INVENTORY_20261004.json'
assert not TARGET.exists(),'New diagnostic identity required'
def row(p):
    return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
audit=json.loads((PRIVATE/'audit_v1/audit.json').read_text())
details=json.loads((PRIVATE/'fresh_details_v1/details_audit.json').read_text())
repeat=json.loads((PRIVATE/'repeat_audit_v1/audit.json').read_text())
assert audit['passed'] and details['passed'] and repeat['passed'] and repeat['cross_export_images_identical']
files=[p for p in sorted(PRIVATE.rglob('*')) if p.is_file()]
for p in files:
    assert subprocess.run(['git','check-ignore','--quiet',str(p.relative_to(ROOT))],cwd=ROOT).returncode==0,p
source=[p for p in sorted(Path(__file__).parent.iterdir()) if p.is_file()]
source+=list(sorted((ROOT/'Docs/Development').glob('GERMAN_RIFLE_LOCALIZED_WOOD_WEAR_V13_20261004*.md')))
source+=list(sorted((ROOT/'Docs/Development').glob('GERMAN_RIFLE_WOOD_WEAR_RESULT_20261004*.md')))
data={'date':'2026-10-04','scope':'private V13 coordinated local material repair; not production/restore authority',
      'selected_review_candidate':'finish_v2/GermanRifle_CoordinatedWear_V13.glb','user_appearance_approved':False,
      'shared':False,'catalog_selected':False,'restore_authority':False,'cloud_spend':0,
      'fresh_audit_passed':True,'fresh_material_and_protected_png_audit_passed':True,
      'repeat_embedded_images_identical':True,'repeat_whole_glb_identical':repeat['cross_export_byte_identical'],
      'private_files':[row(p) for p in files],'source_files':[row(p) for p in source]}
TARGET.write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps({'private_files':len(files),'source_files':len(source),'manifest':str(TARGET)}))
