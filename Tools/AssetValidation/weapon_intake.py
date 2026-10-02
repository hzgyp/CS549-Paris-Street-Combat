"""Selective local intake discovery/staging. Never print extraction passwords."""
import argparse
import hashlib
import json
import re
import shutil
import sys
import zlib
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
INTAKE = ROOT / 'Assets/LocalWorking/Intake/2026-10-01'
LAB = ROOT / 'Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1'
OUT = ROOT / 'tmp/weapon-intake-20261001'
OUT.mkdir(parents=True, exist_ok=True)
NATIVE = {'.uasset', '.umap', '.uexp', '.ubulk'}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def inventory():
    if (OUT / 'original_inventory.json').exists():
        raise RuntimeError('Inventory exists; preserve the first baseline instead of replacing it')
    report = {'time': datetime.now().astimezone().isoformat(), 'assets': []}
    for folder in sorted(INTAKE.iterdir()):
        if not folder.is_dir():
            continue
        entries = []
        for path in sorted(folder.rglob('*')):
            if path.is_symlink() or path.is_junction():
                raise RuntimeError('Unexpected alias in new intake')
            if not path.is_file():
                continue
            before = path.stat()
            checksum = digest(path)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise RuntimeError('A file changed while hashing; wait for downloads to finish')
            entries.append({'path': path.relative_to(folder).as_posix(),
                            'size_bytes': after.st_size, 'sha256': checksum})
        report['assets'].append({'asset_id': folder.name, 'files': entries})
        write('original_inventory.json.partial', report)
        print(json.dumps({'asset': folder.name, 'files': len(entries),
                          'bytes': sum(e['size_bytes'] for e in entries)}), flush=True)
    write('original_inventory.json', report)


def verify():
    report = json.loads((OUT / 'original_inventory.json').read_text(encoding='utf-8'))
    checked, changed, added = 0, 0, 0
    for asset in report['assets']:
        root = INTAKE / asset['asset_id']
        # This delivery was hash-verified and relocated once, not duplicated.
        # Keep the original immutable inventory as the verification authority.
        if asset['asset_id'] == '02_Rifle_Pro_MoCap_Pack_D059' and not root.exists():
            root = ROOT / 'Assets/LocalShared/SFTP/baselines/rifle-pro-mocap-original/rifle-motion-20261002-v1'
        expected = {entry['path'] for entry in asset['files']}
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        added += len(actual - expected)
        for entry in asset['files']:
            path = root / entry['path']
            checked += 1
            if not path.is_file() or path.stat().st_size != entry['size_bytes'] or digest(path) != entry['sha256']:
                changed += 1
    result = {'original_files_checked': checked, 'changed_or_missing': changed, 'added_files': added,
              'verified_at': datetime.now().astimezone().isoformat()}
    write('original_preservation.json', result)
    print(json.dumps(result))
    if changed or added:
        raise RuntimeError('Intake differs from baseline; preserve all files for review')


def password_for(path):
    for parent in path.parents:
        match = re.search(r'(?:解压密码|密码|password|pwd)\s*[:：=]?\s*(.+)$', parent.name, re.I)
        if match:
            return match.group(1).strip()
        if parent == INTAKE:
            break
    return None


def archives():
    sys.path.insert(0, str(OUT / 'pydeps'))
    import py7zr
    selected = {'Rifle Animset Pro.7z', 'Rifle Basic MoCap Pack.7z',
                'Rifle Pro - MoCap Pack.7z', 'Animated Modern Civilian Hands Pack.7z'}
    reports = []
    for path in sorted((INTAKE / '03_UE4_Animation_Collection').rglob('*.7z')):
        if path.name not in selected:
            continue
        try:
            with py7zr.SevenZipFile(path, mode='r', password=password_for(path)) as archive:
                infos = archive.list()
                names = [i.filename for i in infos]
                unsafe = [name for name in names if PurePosixPath(name.replace('\\', '/')).is_absolute()
                          or '..' in PurePosixPath(name.replace('\\', '/')).parts or ':' in name]
                item = {'archive': path.name, 'files': len(infos),
                        'expanded_bytes': sum(i.uncompressed or 0 for i in infos),
                        'unsafe_paths': bool(unsafe), 'members': names,
                        'encrypted': archive.needs_password()}
                item['native_crc_entries'] = [{'path': i.filename, 'size_bytes': i.uncompressed,
                    'crc32': i.crc32} for i in infos if Path(i.filename).suffix.lower() in NATIVE]
                reports.append(item)
                print(json.dumps({k: v for k, v in item.items()
                    if k not in ('members', 'native_crc_entries')}), flush=True)
        except Exception as exc:
            # Exception strings can include sensitive archive parents; publish type only.
            reports.append({'archive': path.name, 'error_type': type(exc).__name__})
            print(json.dumps(reports[-1]), flush=True)
    write('selected_archive_catalogs.json', reports)


def compare():
    catalogs = json.loads((OUT / 'selected_archive_catalogs.json').read_text(encoding='utf-8'))
    roots = {'Rifle_01': INTAKE / '02_Rifle_Pro_MoCap_Pack_D059/Rifle Pro - MoCap Pack/Content/Rifle_01',
             'RifleAnimsetPro': ROOT / 'Assets/LocalWorking/Intake/2026-09-30/ANI-TP-RifleAnimsetPro/Original/Content/RifleAnimsetPro'}
    cache, reports = {}, []
    for item in catalogs:
        entries = item.get('native_crc_entries', [])
        matching, different, missing = 0, 0, 0
        for entry in entries:
            parts = PurePosixPath(entry['path']).parts
            mount = next((m for m in roots if m in parts), None)
            if not mount:
                continue
            path = roots[mount] / Path(*parts[parts.index(mount) + 1:])
            if not path.is_file():
                missing += 1
                continue
            if path not in cache:
                value = 0
                with path.open('rb') as stream:
                    for data in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                        value = zlib.crc32(data, value)
                cache[path] = (path.stat().st_size, value & 0xffffffff)
            if cache[path] == (entry['size_bytes'], entry['crc32']):
                matching += 1
            else:
                different += 1
        reports.append({'archive': item['archive'], 'size_crc_matches': matching,
                        'different': different, 'missing': missing,
                        'limit': 'CRC/size screening only, not cryptographic extraction equivalence'})
    write('archive_duplicate_screen.json', reports)
    print(json.dumps(reports, indent=2))


def stage():
    if LAB.exists():
        raise RuntimeError('Lab already exists; refusing to overwrite or restage')
    baseline = json.loads((OUT / 'original_inventory.json').read_text(encoding='utf-8'))
    index = {(asset['asset_id'], e['path']): e for asset in baseline['assets'] for e in asset['files']}
    sources = [('01_ShooterStarter_FPS_Arm_A', 'ShooterStarter'),
               ('02_Rifle_Pro_MoCap_Pack_D059', 'Rifle_01')]
    candidates = []
    for asset_id, mount in sources:
        roots = [p for p in (INTAKE / asset_id).rglob(mount)
                 if p.is_dir() and p.parent.name == 'Content']
        if len(roots) != 1:
            raise RuntimeError('Missing or ambiguous native content root')
        source = roots[0]
        for path in sorted(source.rglob('*')):
            if path.is_file() and path.suffix.lower() in NATIVE:
                entry = index[(asset_id, path.relative_to(INTAKE / asset_id).as_posix())]
                if path.stat().st_size != entry['size_bytes'] or digest(path) != entry['sha256']:
                    raise RuntimeError('Original source differs from intake baseline')
                candidates.append((path, Path('Content') / mount / path.relative_to(source), entry))
    (LAB / 'Config').mkdir(parents=True)
    shutil.copy2(ROOT / 'Tools/AssetValidation/lab_template.uproject', LAB / 'WeaponCompatibilityLab.uproject')
    shutil.copy2(ROOT / 'Tools/AssetValidation/lab_DefaultEngine.ini', LAB / 'Config/DefaultEngine.ini')
    records = []
    for source, relative, entry in candidates:
        target = LAB / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if target.stat().st_size != entry['size_bytes'] or digest(target) != entry['sha256']:
            raise RuntimeError('Staged copy verification failed')
        records.append({'path': relative.as_posix(), 'size_bytes': entry['size_bytes'],
                        'original_sha256': entry['sha256']})
    (LAB / 'Evidence').mkdir()
    (LAB / 'Evidence/staging.json').write_text(json.dumps({'status': 'local selective discovery lab, unpublished',
        'files': records, 'excluded': 'StarterContent, vendor configuration, caches, collection and FBX wrappers'}, indent=2), encoding='utf-8')
    print(json.dumps({'staged_files': len(records), 'staged_bytes': sum(e['size_bytes'] for e in records),
                      'mounts': dict(Counter(Path(e['path']).parts[1] for e in records))}), flush=True)


def summarize():
    """Publish hash-only diagnostic metadata, never private delivery wrapper names."""
    original = json.loads((OUT / 'original_inventory.json').read_text(encoding='utf-8'))
    staging = json.loads((LAB / 'Evidence/staging.json').read_text(encoding='utf-8'))
    inventory = json.loads((LAB / 'Evidence/ue_load_inventory.json').read_text(encoding='utf-8'))
    probe = json.loads((LAB / 'Evidence/CandidateProbe_v2/candidate_probe.json').read_text(encoding='utf-8'))
    audit = json.loads((LAB / 'Evidence/CandidateProbe/blender_export_audit.json').read_text(encoding='utf-8'))
    preservation = json.loads((OUT / 'original_preservation.json').read_text(encoding='utf-8'))
    draft = json.loads((ROOT / 'Assets/Integration/LOCAL_DRAFT_INVENTORY_20261001.json').read_text(encoding='utf-8'))
    draft_bad = [e['package'] for e in draft['files']
        if digest(ROOT / draft['canonical_workspace'] / e['workspace_path']) != e['sha256']]
    paths = {a['path']: a for a in inventory['assets']}
    timing = []
    for a in audit['animations']:
        native = next(v for k,v in paths.items() if k.endswith('/' + Path(a['file']).stem))
        duration = (a['actions'][0]['frame_range'][1] - a['actions'][0]['frame_range'][0]) / a['fps']
        timing.append({'file': a['file'], 'native_seconds': native['sequence_length'],
            'imported_action_span_seconds': duration, 'span_difference_seconds': duration-native['sequence_length'],
            'status': 'diagnostic only; scene rate/export endpoint convention not normalized'})
    selected_names = {'Rifle Animset Pro.7z', 'Rifle Basic MoCap Pack.7z',
                      'Rifle Pro - MoCap Pack.7z', 'Animated Modern Civilian Hands Pack.7z'}
    archive_hashes = [{'archive': Path(e['path']).name, 'size_bytes': e['size_bytes'], 'sha256': e['sha256']}
        for a in original['assets'] if a['asset_id'] == '03_UE4_Animation_Collection'
        for e in a['files'] if Path(e['path']).name in selected_names]
    data = {'schema_version': 1, 'status': 'LOCAL_DIAGNOSTICS_NOT_A_RELEASE', 'owner': 'yg745',
        'catalog_selected': False, 'restore_authority': False, 'remote_immutable_path': None,
        'sharing': 'owner attests private three-member original and derivative sharing; public distribution unconfirmed',
        'engine': inventory['engine'], 'blender': audit['blender'],
        'intake': [{'asset_id': a['asset_id'], 'file_count': len(a['files']),
            'size_bytes': sum(e['size_bytes'] for e in a['files'])} for a in original['assets']],
        'original_preservation': preservation, 'existing_drafts_checked': len(draft['files']), 'existing_draft_mismatches': draft_bad,
        'staged_files': staging['files'], 'archive_hashes': archive_hashes,
        'archive_duplicate_screen': json.loads((OUT / 'archive_duplicate_screen.json').read_text(encoding='utf-8')),
        'native_loaded_count': inventory['loaded_count'], 'native_errors': len(inventory['errors']),
        'v2_samples': len(probe['samples']), 'v2_captures': len(probe['captures']), 'v2_errors': len(probe['errors']),
        'reference_pose_differences': probe['reference_pose_differences'], 'exchange_timing': timing,
        'mesh_metrics': [{k:v for k,v in m.items() if k != 'bones'} for m in audit['models']],
        'decision': 'Do not release this direct-animation FP configuration. WWII rifle kit, matched reload, evaluated retarget and historical sleeves/gloves remain open.'}
    target = ROOT / 'Assets/Integration/WEAPON_INTAKE_DIAGNOSTICS_20261001.json'
    target.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(json.dumps({'report': target.relative_to(ROOT).as_posix(), 'staged_hash_records': len(staging['files']),
        'draft_mismatches': len(draft_bad), 'status': data['status']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['inventory', 'archives', 'compare', 'stage', 'verify', 'summarize'])
    args = parser.parse_args()
    globals()[args.command]()
