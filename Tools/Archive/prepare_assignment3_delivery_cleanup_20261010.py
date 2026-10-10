"""Freeze this delivery-only cleanup and verify a recoverable private ZIP."""
from pathlib import Path
import hashlib
import json
import os
import stat
import zipfile
from datetime import datetime, timezone
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / 'Assets/LocalShared/Deliverables/Assignment3'
ARCHIVE = ROOT / 'Assets/LocalShared/Archives/Assignment3_20261010'
VIDEO = DELIVERY / 'DemoDraft04_20261010/Paris_G1_MVP_Draft_04_Live_Performance.mp4'
PDF = ROOT / 'output/pdf/Paris_Street_Combat_Assignment3_20261010_EN.pdf'
GAME = ROOT / 'tmp/Playtest-G1-Foley-V2-20261009/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
ACCESS = DELIVERY / 'SFTPAccess_20261010'
TOPS = {'DemoDraft02_20261009', 'DemoDraft03_20261009', 'DemoDraft04_20261010',
        'DemoDraft20261009', 'FailedReports', 'VoiceAudition20261009', 'SFTPAccess_20261010'}
ACCESS_NAMES = {'CONNECTION.json', 'cs549_sftp_ed25519', 'DOWNLOAD_GAME.cmd',
                'DOWNLOAD_GAME.ps1', 'README.md'}

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def check_path(path):
    absolute = path.absolute()
    absolute.relative_to(ROOT)
    for ancestor in (absolute, *absolute.parents):
        if ancestor.exists():
            assert not (ancestor.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT), str(ancestor)
        if ancestor == ROOT:
            break
    return absolute

def row(path):
    check_path(path)
    info = path.stat()
    return {'path': str(path), 'relative_path': path.relative_to(ROOT).as_posix(),
            'bytes': info.st_size, 'mtime_ns': info.st_mtime_ns, 'sha256': digest(path)}

def main():
    check_path(DELIVERY)
    check_path(ARCHIVE)
    assert not ARCHIVE.exists(), 'This archive identity already exists; do not overwrite'
    assert {p.name for p in DELIVERY.iterdir()} == TOPS
    assert {p.name for p in ACCESS.iterdir()} == ACCESS_NAMES
    assert all(p.is_file() for p in ACCESS.iterdir())
    assert digest(VIDEO) == '8048195262f6dd45cc583985b1297227065bb9b4b2454d16763037564d073be0'
    assert digest(PDF) == '6379243d8e003906362972533927f9f503971513836fb0556f191d4679cd8f6f'
    assert len(PdfReader(PDF).pages) == 2
    assert digest(GAME) == '53ab36d9da1975a2f8e1109fcf6745cc40e96d371fc89fbfa009139b91950aec'
    source = list((ROOT / 'Unreal/Variants/G1FootContactAudio20261009/Project').rglob('*'))
    source = sorted(p for p in source if p.is_file())
    assert len(source) == 42
    keep = {VIDEO, *ACCESS.iterdir()}
    originals = sorted(p for p in DELIVERY.rglob('*') if p.is_file())
    entries = [row(p) for p in originals if p not in keep]
    for entry in entries:
        path = Path(entry['path'])
        entry['archive_member'] = path.relative_to(DELIVERY).as_posix()
        assert not entry['archive_member'].startswith('SFTPAccess_20261010/')
    guards = [row(p) for p in sorted(keep)] + [row(PDF), row(GAME)] + [row(p) for p in source]
    manifest = {'date': datetime.now(timezone.utc).isoformat(),
                'authorization': 'User: inspect screenshot delivery directory and delete unused files',
                'workspace': str(ROOT), 'delivery_root': str(DELIVERY), 'archive_root': str(ARCHIVE),
                'entries': entries, 'guards': guards,
                'original_delivery_files': len(originals),
                'pdf_source': str(PDF), 'pdf_delivery': str(DELIVERY / PDF.name),
                'archive_members_prefix': 'Original relative paths under Assignment3'}
    ARCHIVE.mkdir(parents=True)
    target = ARCHIVE / 'production-evidence.zip'
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for entry in entries:
            path = Path(entry['path'])
            assert path.stat().st_mtime_ns == entry['mtime_ns']
            assert digest(path) == entry['sha256']
            z.write(path, entry['archive_member'])
        z.writestr('MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {e['archive_member'] for e in entries} | {'MANIFEST.json'}
        for entry in entries:
            member = z.getinfo(entry['archive_member'])
            assert member.file_size == entry['bytes']
            h = hashlib.sha256()
            with z.open(member) as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    h.update(chunk)
            assert h.hexdigest() == entry['sha256']
    manifest['archive_file'] = str(target)
    manifest['archive_bytes'] = target.stat().st_size
    manifest['archive_sha256'] = digest(target)
    manifest['archive_all_members_verified'] = True
    manifest['retired_original_bytes'] = sum(e['bytes'] for e in entries)
    manifest['projected_net_saving_bytes'] = manifest['retired_original_bytes'] - manifest['archive_bytes'] - PDF.stat().st_size
    assert manifest['projected_net_saving_bytes'] > 0
    (ARCHIVE / 'MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ('original_delivery_files', 'retired_original_bytes',
                                              'archive_bytes', 'projected_net_saving_bytes')}))
    print('Verified archived files:', len(entries), 'Protected files:', len(guards))

if __name__ == '__main__':
    main()
