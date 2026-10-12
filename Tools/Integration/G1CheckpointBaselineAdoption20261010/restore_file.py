"""Exact recovery of a retired file; also resolves earlier audio recovery references."""
import argparse
import hashlib
import shutil
import zipfile
from manage import ROOT, proof, safe, verify


def recover_retired(path, expected=None, output=None):
    _, _, mapping = proof()
    matches = [r for r in mapping['files'] if r['path'] == path]
    assert len(matches) == 1, 'No exact retired-file recovery: ' + path
    item = matches[0]
    if expected is not None:
        assert (item['size_bytes'], item['sha256']) == (expected['size_bytes'], expected['sha256'])
    dest = safe(output) if output else None
    if dest:
        assert not dest.exists(), 'Preserve occupied restore destination'
    rec = item['recovery']
    if rec['kind'] == 'retained_file':
        source = safe(rec['path'])
        verify(source, item)
        if dest:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with source.open('rb') as src, dest.open('xb') as dst:
                shutil.copyfileobj(src, dst)
    elif rec['kind'] == 'zip_entry':
        archive = safe(rec['archive_path'])
        verify(archive, mapping['recovery_zip'])
        with zipfile.ZipFile(archive) as z:
            assert z.getinfo(rec['entry']).file_size == item['size_bytes']
            with z.open(rec['entry']) as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == item['sha256']
            if dest:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with z.open(rec['entry']) as src, dest.open('xb') as dst:
                    shutil.copyfileobj(src, dst)
    else:
        raise AssertionError('Unknown recovery kind')
    if dest:
        verify(dest, item)
    return item


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path')
    parser.add_argument('--output', help='Optional unoccupied workspace-relative destination; otherwise verify only')
    args = parser.parse_args()
    recover_retired(args.path, output=args.output)
    print('PASS exact retired-file ' + ('restore' if args.output else 'verification') + ': ' + args.path)
