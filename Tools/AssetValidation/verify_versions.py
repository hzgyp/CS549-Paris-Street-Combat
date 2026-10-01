"""Verify originals and local resaved package headers; not a publication manifest."""
import hashlib
import json
import os
import re
import struct
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / 'Assets/LocalWorking/Validation/UE582/2026-09-30-v1'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    staging = json.loads((LAB / 'Evidence/staging.json').read_text(encoding='utf-8'))
    baseline = json.loads((ROOT / 'tmp/asset-intake-review/intake_static_inventory.json').read_text(encoding='utf-8'))
    changed_originals = []
    total = 0
    for asset in baseline['assets']:
        for entry in asset['files']:
            path = ROOT / 'Assets/LocalWorking/Intake/2026-09-30' / asset['asset_id'] / entry['path']
            total += 1
            if path.stat().st_size != entry['size_bytes'] or digest(path) != entry['sha256']:
                changed_originals.append(str(path))
    records = []
    entries = list(staging['copied_files'])
    if os.environ.get('CS549_REPAIR_VERSIONS') == '1':
        entries += [{'path': p.relative_to(LAB.resolve()).as_posix(), 'original_sha256': None}
                    for p in (LAB / 'Content/ParisCombat/Characters/Adaptation').resolve().rglob('*.uasset')]
    for entry in entries:
        path = LAB / entry['path']
        # Engine branch strings are in the serialized header, not the filename.
        data = path.read_bytes()[:65536]
        branches = sorted(set(m.decode('ascii') for m in re.findall(rb'\+\+UE[45]\+Release-[0-9.]+', data)))
        header_versions = []
        for match in re.finditer(rb'\+\+UE[45]\+Release-[0-9.]+', data):
            if match.start() >= 14:
                major, minor, patch, changelist = struct.unpack('<HHHI', data[match.start() - 14:match.start() - 4])
                if major in (4, 5) and minor < 100 and patch < 100:
                    header_versions.append({'version': f'{major}.{minor}.{patch}',
                                            'changelist': changelist & 0x7fffffff,
                                            'branch': match.group().decode('ascii')})
        checksum = digest(path)
        records.append({'path': entry['path'], 'size_bytes': path.stat().st_size,
                        'sha256': checksum, 'original_sha256': entry['original_sha256'],
                        'changed_from_original': checksum != entry['original_sha256'],
                        'header_engine_branches': branches,
                        'header_engine_versions': header_versions,
                        'has_UE582_header': any(v['version'] == '5.8.2' for v in header_versions),
                        'has_UE58_header': '++UE5+Release-5.8' in branches})
    report = {'checked_at': datetime.now().astimezone().isoformat(),
              'status': 'local-only diagnostic version inventory; not SFTP publication',
              'original_files_checked': total, 'changed_originals': changed_originals,
              'packages': records,
              'changed_packages': sum(r['changed_from_original'] for r in records),
              'UE582_header_packages': sum(r['has_UE582_header'] for r in records),
              'UE58_header_packages': sum(r['has_UE58_header'] for r in records)}
    report_path = LAB / ('Evidence/Repair20261001/repair_versions.json' if os.environ.get('CS549_REPAIR_VERSIONS') == '1' else 'Evidence/version_verification.json')
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'packages'}, indent=2))
    if changed_originals:
        raise SystemExit('Original preservation failed')


if __name__ == '__main__':
    main()
