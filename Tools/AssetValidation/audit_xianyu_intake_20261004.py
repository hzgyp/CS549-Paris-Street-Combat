"""Read-only receipt/hash comparison and bounded ZIP audit; no supplied code runs."""
import collections
import hashlib
import json
import re
import struct
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalWorking/Validation/2026-10-04-xianyu-intake-v1/Audit'
assert not OUT.exists(), 'Preserve occupied evidence'
sys.path.insert(0, str(ROOT / 'Tools/Integration'))
from german_rifle_ue_common import guard


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    before = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'Source changed during read'
    return h.hexdigest()


def header(path):
    with path.open('rb') as stream:
        data = stream.read(65536)
    versions = []
    for match in re.finditer(rb'\+\+UE[45]\+Release-[0-9.]+', data):
        if match.start() >= 14:
            major, minor, patch, cl = struct.unpack('<HHHI', data[match.start()-14:match.start()-4])
            if major in (4, 5) and minor < 100 and patch < 100:
                versions.append({'version': f'{major}.{minor}.{patch}', 'cl': cl & 0x7fffffff,
                                 'branch': match.group().decode('ascii')})
    refs = sorted({m.decode('ascii') for m in re.findall(rb'/Game/[A-Za-z0-9_./-]+', data)})
    hints = [s for s in ('NiagaraSystem', 'NiagaraEmitter', 'ParticleSystem', 'Blueprint',
             'StaticMesh', 'SkeletalMesh', 'MaterialInstanceConstant', 'Texture2D', 'AnimSequence', 'Skeleton')
             if s.encode() + b'\x00' in data]
    return {'ue_package_tag': data[:4] == b'\xc1\x83\x2a\x9e', 'engine_version_clues': versions,
            'header_class_string_hints_not_registry_classes': hints, 'header_game_references_not_complete_dependencies': refs}


def scan(base):
    records = []
    for path in sorted(base.rglob('*')):
        if not path.is_file():
            continue
        assert not path.is_symlink(), 'Unexpected receipt symlink'
        record = {'relative_path': path.relative_to(base).as_posix(), 'size_bytes': path.stat().st_size,
                  'sha256': digest(path)}
        if path.suffix.lower() in ('.uasset', '.umap'):
            record.update(header(path))
            assert record['ue_package_tag'], 'Invalid package header'
        records.append(record)
    return records


before_guard = guard()
OUT.mkdir(parents=True)
base = ROOT / 'Assets/LocalWorking/Intake/2026-10-04'
vfx_base = base / '01_Muzzle_Flash_VFX'
anim_base = base / '02_Firearm_Animations'
vfx, animation = scan(vfx_base), scan(anim_base)
old_manifest_path = ROOT / 'Assets/Sync/manifests/rifle-animset-pro-original.json'
old_manifest = load(old_manifest_path)
old_rows = old_manifest['files']
assert len(old_rows) == 300
old_checked = []
for row in old_rows:
    path = ROOT / row['path']
    actual = digest(path)
    assert actual == row['sha256'] and path.stat().st_size == row['size_bytes'], 'Existing original differs from manifest'
    old_checked.append({'path': row['path'], 'size_bytes': row['size_bytes'], 'sha256': actual})

old_native = {}
for row in old_rows:
    if Path(row['path']).suffix.lower() in ('.uasset', '.umap'):
        key = 'RifleAnimsetPro/' + row['path'].split('/Content/RifleAnimsetPro/', 1)[1]
        assert key not in old_native
        old_native[key] = row
new_native = {r['relative_path']: r for r in animation if Path(r['relative_path']).suffix.lower() in ('.uasset', '.umap')}
shared = sorted(old_native.keys() & new_native.keys())
exact = [key for key in shared if old_native[key]['sha256'] == new_native[key]['sha256'] and old_native[key]['size_bytes'] == new_native[key]['size_bytes']]
different = [key for key in shared if key not in exact]
old_hashes = collections.defaultdict(list)
for row in old_rows:
    old_hashes[(row['sha256'], row['size_bytes'])].append(row['path'])
other_matches = [{'new_relative_path': r['relative_path'], 'old_paths': old_hashes[(r['sha256'], r['size_bytes'])]}
                 for r in animation if Path(r['relative_path']).suffix.lower() not in ('.uasset', '.umap')
                 and (r['sha256'], r['size_bytes']) in old_hashes]

zip_reports = []
for row in animation:
    if Path(row['relative_path']).suffix.lower() != '.zip':
        continue
    path = anim_base / row['relative_path']
    with zipfile.ZipFile(path) as archive:
        members = [i for i in archive.infolist() if not i.is_dir()]
        unsafe = [i.filename for i in members if '..' in PurePosixPath(i.filename.replace('\\', '/')).parts
                  or i.filename.startswith(('/', '\\')) or ':' in i.filename
                  or ((i.external_attr >> 16) & 0o170000) == 0o120000]
        expanded = sum(i.file_size for i in members)
        assert not unsafe and expanded <= 4 * 1024**3 and all(i.file_size <= 512 * 1024**2 for i in members), 'Unsafe/oversized archive'
        assert all(not i.flag_bits & 1 for i in members), 'Encrypted archive requires separate private handling'
        assert archive.testzip() is None, 'ZIP CRC failed'
        zip_reports.append({'relative_path': row['relative_path'], 'sha256': row['sha256'],
                            'members': len(members), 'expanded_bytes': expanded, 'crc_passed': True,
                            'extensions': dict(collections.Counter(Path(i.filename).suffix.lower() for i in members)),
                            'member_names': [i.filename for i in members], 'unsafe_paths': unsafe, 'extracted': False})

prior_path = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/FinalInventory/ue_load_inventory.json'
prior_assets = [r for r in load(prior_path)['assets'] if r['path'].startswith('/Game/RifleAnimsetPro/')]
prior_clips = [r for r in prior_assets if r.get('class') == 'AnimSequence']
assert len(prior_clips) == 277
clip_inventory = [{'path': r['path'], 'sequence_length': r.get('sequence_length'), 'frames': r.get('frames'),
                   'skeleton': r.get('skeleton'), 'root_motion': r.get('root_motion')}
                  for r in prior_clips if ('RifleAnimsetPro/' + r['path'].split('/Game/RifleAnimsetPro/', 1)[1] + '.uasset') in exact]

def group(records):
    return {'files': len(records), 'bytes': sum(r['size_bytes'] for r in records),
            'extensions': dict(collections.Counter(Path(r['relative_path']).suffix.lower() for r in records)),
            'engine_version_clues': dict(collections.Counter(v['version'] for r in records for v in r.get('engine_version_clues', []))),
            'records': records}

report = {'date': '2026-10-04', 'scope': 'Read-only file/header/SHA/original/ZIP inspection; no fresh UE load or visual acceptance',
          'vfx': group(vfx), 'animation': group(animation),
          'duplicate': {'old_manifest': old_manifest_path.relative_to(ROOT).as_posix(), 'old_manifest_sha256': digest(old_manifest_path),
                        'old_files_rehashed': len(old_checked), 'old_original_records': old_checked,
                        'new_native': len(new_native), 'old_native': len(old_native), 'exact_native': len(exact),
                        'different_native': different, 'new_only_native': sorted(new_native.keys() - old_native.keys()),
                        'old_only_native': sorted(old_native.keys() - new_native.keys()), 'non_native_exact_matches': other_matches,
                        'fully_duplicate_native': len(exact) == len(new_native) == len(old_native)},
          'zip': zip_reports, 'motion_inventory': clip_inventory,
          'prior_motion_basis': {'path': prior_path.relative_to(ROOT).as_posix(), 'sha256': digest(prior_path),
                                'note': 'Prior dated actual UE load; inherited only for SHA-exact original files, not fresh target playback'},
          'guard_before': before_guard, 'guard_after': guard(), 'new_sharing_rights': 'unconfirmed',
          'originals_changed': False, 'deleted': [], 'engine_launched': False, 'sftp_published': False}
assert report['guard_before'] == report['guard_after'] == 412
# Recheck receipt stability/bytes after analysis and ZIP decompression.
for directory, records in ((vfx_base, vfx), (anim_base, animation)):
    for row in records:
        p = directory / row['relative_path']
        assert p.stat().st_size == row['size_bytes'] and digest(p) == row['sha256'], 'Receipt changed during audit'
(OUT / 'intake_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
summary = {k: v for k, v in report['duplicate'].items() if k not in ('old_original_records', 'non_native_exact_matches')}
summary['non_native_exact_match_names'] = [r['new_relative_path'] for r in other_matches]
print(json.dumps({'vfx': {k: v for k, v in report['vfx'].items() if k != 'records'},
                  'animation': {k: v for k, v in report['animation'].items() if k != 'records'},
                  'duplicate': summary, 'zip': [{k: v for k, v in r.items() if k != 'member_names'} for r in zip_reports],
                  'prior_exact_motion_clips': len(clip_inventory), 'guard': report['guard_after']}, ensure_ascii=True, indent=2))
