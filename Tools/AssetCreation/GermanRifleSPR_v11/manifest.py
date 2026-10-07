"""Private weathering draft metadata, not a shared release or restore catalog."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-weather-v11'
NAME = 'GermanRifle_SPR_Weathered_V11'


def record(p):
    return {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


audit = json.loads((BASE / 'audit_v1/audit.json').read_text())
repeat = json.loads((BASE / 'repeat_audit_v1/audit.json').read_text())
build = json.loads((BASE / 'finish_v1/build_report.json').read_text())
assert audit['passed'] and repeat['passed'] and repeat['cross_export_images_identical']
assert build['geometry_exact']
for path, digest in build['baseline_files'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
data = {'date': '2026-10-04', 'scope': 'private texture-only draft, not SFTP/production/restore authority',
        'candidate': record(BASE / 'finish_v1' / (NAME + '.glb')),
        'blend': record(BASE / 'finish_v1' / (NAME + '.blend')),
        'baseline_form_user_approved': True, 'weathering_user_approved': False,
        'historical_approval': False, 'runtime_approval': False,
        'rights_status': 'MW2 project-use/derivative-sharing confirmation pending; local-only',
        'geometry_raw_fingerprint_exact': True, 'protected_v10_hashes_match': True,
        'metrics': {k: audit[k] for k in ['triangles', 'dimensions_m', 'embedded_images']},
        'repeat_embedded_images_identical': True,
        'repeat_attributes_passed': True, 'repeat_byte_identical': repeat['cross_export_byte_identical'],
        'inspected_evidence': ['preview_v1/' + p + '_' + v + '.png' for p in ['before', 'pbr'] for v in ['quarter', 'receiver']]
        + [folder + '/' + prefix + '_' + v + '.png'
           for folder, prefix in [('finish_v1', 'pbr'), ('audit_v1', 'fresh_pbr')]
           for v in ['right', 'left', 'quarter', 'top', 'underside', 'receiver']],
        'private_files': [record(p) for p in sorted(BASE.rglob('*')) if p.is_file() and '__pycache__' not in str(p)],
        'source_files': [record(p) for p in sorted(Path(__file__).parent.iterdir()) if p.is_file()]
        + [record(ROOT / 'Tools/AssetCreation/GermanRifleSPR_v10' / f) for f in ['main.py', 'audit.py']]}
target = ROOT / 'Assets/Integration/GERMAN_RIFLE_WEATHERING_DRAFT_INVENTORY_20261004.json'
assert not target.exists(), 'Preserve existing manifest identity'
target.write_text(json.dumps(data, indent=2), encoding='utf-8')
print(json.dumps({'private_files': len(data['private_files']), 'source_files': len(data['source_files']),
                  'candidate': data['candidate'], 'repeat_byte_identical': data['repeat_byte_identical']}))
