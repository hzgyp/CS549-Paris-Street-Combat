"""Verify or restore one retired file using the frozen exact recovery map."""
import argparse
import hashlib
import shutil
import zipfile
from manage import ROOT, proof, safe, verify

def recover(path, output=None):
    _, _, mapping = proof()
    matches = [r for r in mapping['files'] if r['path'] == path]
    assert len(matches) == 1, 'Specify an exact recoverable path from the map'
    item = matches[0]
    dest = safe(output) if output else None
    if dest:
        assert not dest.exists(), 'Preserve occupied destination'
    rec = item['recovery']
    if rec['kind'] == 'retained_file':
        source = safe(rec['path'])
        verify(source, item)
        if dest:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with source.open('rb') as s, dest.open('xb') as d:
                shutil.copyfileobj(s, d)
    else:
        archive = safe(rec['archive_path'])
        verify(archive, mapping['recovery_zip'])
        with zipfile.ZipFile(archive) as z:
            assert z.getinfo(rec['entry']).file_size == item['size_bytes']
            with z.open(rec['entry']) as s:
                assert hashlib.file_digest(s, 'sha256').hexdigest() == item['sha256']
            if dest:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with z.open(rec['entry']) as s, dest.open('xb') as d:
                    shutil.copyfileobj(s, d)
    if dest:
        verify(dest, item)
    return item

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('path')
    p.add_argument('--output')
    args = p.parse_args()
    recover(args.path, args.output)
    print('PASS exact retired-file '+('restore' if args.output else 'verification'))
