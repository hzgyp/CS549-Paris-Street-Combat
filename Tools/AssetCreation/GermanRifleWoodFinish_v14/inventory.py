"""Diagnostic metadata only; cannot release, restore or publish private bytes."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PRIVATE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-finish-v14'
OUT=ROOT/'Assets/Integration/GERMAN_RIFLE_WOOD_FINISH_V14_INVENTORY_20261004.json'

def record(path):
    return {'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

assert not OUT.exists(),'Occupied diagnostic inventory'
assets=sorted(p for p in PRIVATE.rglob('*') if p.is_file())
paths=[p.relative_to(ROOT).as_posix() for p in assets]
ignored=subprocess.run(['git','check-ignore','-z','--stdin'],input=('\0'.join(paths)+'\0').encode('utf-8'),cwd=ROOT,capture_output=True,check=True)
assert set(ignored.stdout.decode('utf-8').rstrip('\0').split('\0'))==set(paths),'Private file not ignored'
sources=sorted(p for p in Path(__file__).parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
sources += [ROOT/'Tools/AssetCreation'/f for f in ['GermanRifleSPR_v10/main.py','GermanRifleSPR_v10/audit.py','GermanRifleSPR_v11/main.py','GermanRifleM1Transfer_v12/main.py','GermanRifleWoodWear_v13/main.py','GermanRifleWoodWear_v13/preflight.py']]
sources += [ROOT/'Tools/AssetValidation/blender_rifle_texture_compare.py']
sources += [ROOT/'Docs/Development'/f for f in ['GERMAN_RIFLE_WOOD_FINISH_V14_20261004.md','GERMAN_RIFLE_WOOD_FINISH_V14_20261004_ZH.md','GERMAN_RIFLE_WOOD_FINISH_RESULT_20261004.md','GERMAN_RIFLE_WOOD_FINISH_RESULT_20261004_ZH.md']]
report={'date':'2026-10-04','purpose':'Private diagnostic metadata; NOT Catalog, release, production selection or teammate restore authority',
    'candidate':'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-finish-v14/finish_v1/GermanRifle_DarkWood_V14.glb',
    'user_appearance_approved':False,'shared':False,'cloud_spend':0,'all_private_files_ignored':True,
    'private_files':[record(p) for p in assets],'source_files':[record(p) for p in sorted(set(sources))]}
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'private_files':len(assets),'source_files':len(set(sources)),'all_ignored':True}))
