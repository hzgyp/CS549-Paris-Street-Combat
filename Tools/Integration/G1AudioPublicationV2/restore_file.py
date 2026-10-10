"""Verify or restore one retired file without overwriting an occupied path."""
import argparse
import hashlib
import shutil
import zipfile
from publish import ROOT, PROOF, read, safe, verify, row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',help='Exact workspace-relative retired path from RECOVERY_MAP')
    parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--output',help='Optional unoccupied workspace-relative test destination')
    args=parser.parse_args()
    authority=read(PROOF/'RETIREMENT_INVENTORY_20261009.json')
    metadata=PROOF/'RECOVERY_MAP_20261009.json'
    assert row(metadata)['sha256']==authority['recovery_map_sha256']
    mapped=read(metadata)
    matches=[r for r in mapped['files'] if r['path']==args.path]
    assert len(matches)==1,'Choose exactly one recorded file'
    item=matches[0];rec=item['recovery']
    target=safe(args.output or args.path)
    if not args.verify_only:assert not target.exists(),'Preserve occupied restore destination'
    if rec['kind']=='retained_file':
        source=safe(rec['path']);verify(source,item)
        if not args.verify_only:
            target.parent.mkdir(parents=True,exist_ok=True)
            with source.open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
    elif rec['kind']=='zip_entry':
        archive_path=safe(rec['archive_path']);verify(archive_path,mapped['recovery_zip'])
        with zipfile.ZipFile(archive_path) as archive:
            with archive.open(rec['entry']) as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==item['sha256']
            assert archive.getinfo(rec['entry']).file_size==item['size_bytes']
            if not args.verify_only:
                target.parent.mkdir(parents=True,exist_ok=True)
                with archive.open(rec['entry']) as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
    else:raise AssertionError('Unknown recovery type')
    if not args.verify_only:verify(target,item)
    print('Exact retired file '+('verified: ' if args.verify_only else 'restored: ')+args.path)


if __name__=='__main__':main()
