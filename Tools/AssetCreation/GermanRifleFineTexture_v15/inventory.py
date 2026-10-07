"""Hash-only local diagnostic inventory; no release, selection or restore power."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRIVATE = ROOT / 'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-fine-texture-v15'
OUT = ROOT / 'Assets/Integration/GERMAN_RIFLE_FINE_TEXTURE_V15_INVENTORY_20261004.json'


def record(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


assert not OUT.exists(), 'Occupied diagnostic inventory'
assets = sorted(path for path in PRIVATE.rglob('*') if path.is_file())
paths = [path.relative_to(ROOT).as_posix() for path in assets]
# Binary NUL-delimited paths prevent Windows CRLF/quoted-path false failures.
ignored = subprocess.run(['git', 'check-ignore', '-z', '--stdin'],
                         input=('\0'.join(paths) + '\0').encode('utf-8'),
                         cwd=ROOT, capture_output=True, check=True)
assert set(ignored.stdout.decode('utf-8').rstrip('\0').split('\0')) == set(paths), 'Private file not ignored'
sources = sorted(path for path in Path(__file__).parent.rglob('*')
                 if path.is_file() and '__pycache__' not in path.parts)
sources += [ROOT / 'Tools/AssetCreation' / name for name in [
    'GermanRifleSPR_v10/main.py', 'GermanRifleSPR_v10/audit.py',
    'GermanRifleSPR_v11/main.py', 'GermanRifleM1Transfer_v12/main.py',
    'GermanRifleWoodWear_v13/main.py', 'GermanRifleWoodWear_v13/preflight.py',
    'GermanRifleWoodFinish_v14/main.py']]
sources += [ROOT / 'Tools/AssetValidation/blender_rifle_texture_compare.py']
sources += [ROOT / 'Docs/Development' / name for name in [
    'GERMAN_RIFLE_FINE_TEXTURE_V15_20261004.md',
    'GERMAN_RIFLE_FINE_TEXTURE_V15_20261004_ZH.md',
    'GERMAN_RIFLE_FINE_TEXTURE_RESULT_20261004.md',
    'GERMAN_RIFLE_FINE_TEXTURE_RESULT_20261004_ZH.md']]
report = {
    'date': '2026-10-04',
    'purpose': 'Private diagnostic metadata; NOT Catalog, release, production selection or teammate restore authority',
    'candidate': (PRIVATE / 'finish_v1/GermanRifle_FineWood_V15.glb').relative_to(ROOT).as_posix(),
    'prior_v14_user_feedback': 'Visibly much improved; not complete production acceptance',
    'v15_user_appearance_approved': False, 'shared': False, 'cloud_spend': 0,
    'final_authorized_polish_round_stopped': True, 'all_private_files_ignored': True,
    'private_files': [record(path) for path in assets],
    'source_files': [record(path) for path in sorted(set(sources))]}
OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'private_files': len(assets), 'source_files': len(set(sources)), 'all_ignored': True}))
