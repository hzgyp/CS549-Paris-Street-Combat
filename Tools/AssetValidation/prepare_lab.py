"""Stage vendor copies in an ignored lab; never overwrite originals or main Content."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTAKE = ROOT / 'Assets/LocalWorking/Intake/2026-09-30'
LAB = ROOT / 'Assets/LocalWorking/Validation/UE582/2026-09-30-v1'
BASELINE = ROOT / 'tmp/asset-intake-review/intake_static_inventory.json'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    baseline = json.loads(BASELINE.read_text(encoding='utf-8'))
    checked = 0
    for asset in baseline['assets']:
        for entry in asset['files']:
            path = INTAKE / asset['asset_id'] / entry['path']
            if path.stat().st_size != entry['size_bytes'] or digest(path) != entry['sha256']:
                raise RuntimeError(f'Original changed since static intake: {path}')
            checked += 1
    sources = {
        'GermanSoldier': INTAKE / 'CHAR-G-GermanSoldierWWII/Original',
        'USParatrooper': INTAKE / 'CHAR-A-USSoldier/Original/USParatrooper/Content/USParatrooper',
        'RifleAnimsetPro': INTAKE / 'ANI-TP-RifleAnimsetPro/Original/Content/RifleAnimsetPro',
    }
    records = []
    for mount, source in sources.items():
        for original in sorted(source.rglob('*')):
            if not original.is_file() or original.suffix.lower() not in ('.uasset', '.umap', '.uexp', '.ubulk'):
                continue
            relative = original.relative_to(source)
            target = LAB / 'Content' / mount / relative
            original_hash = digest(original)
            if target.exists():
                if digest(target) != original_hash:
                    raise RuntimeError(f'Lab contains an edited file; refusing overwrite: {target}')
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, target)
            if digest(target) != original_hash:
                raise RuntimeError(f'Copy hash mismatch: {target}')
            records.append({'source': original.relative_to(ROOT).as_posix(),
                            'path': target.relative_to(LAB).as_posix(),
                            'size_bytes': target.stat().st_size, 'original_sha256': original_hash})
    (LAB / 'Evidence').mkdir(parents=True, exist_ok=True)
    (LAB / 'Evidence/staging.json').write_text(json.dumps({
        'owner': 'Yupu Guo integration lab', 'engine_target': '5.8.2',
        'status': 'local-only, rights unresolved, not a published asset manifest',
        'original_files_verified': checked, 'copied_files': records,
    }, indent=2), encoding='utf-8')
    print(json.dumps({'original_files_verified': checked, 'copied_files': len(records),
                      'lab': str(LAB)}, indent=2))


if __name__ == '__main__':
    main()
