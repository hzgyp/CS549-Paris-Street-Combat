"""Verify an offline failure case's immutable byte mappings without restoring anything."""
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def safe(relative):
    p=(ROOT/relative).resolve()
    assert p.is_relative_to(ROOT.resolve()),relative
    return p
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',default='FP001-20261003-first-person-view')
    parser.add_argument('--protected',action='store_true',help='Also compare the dated protected baseline; later approved development may legitimately change it')
    args=parser.parse_args()
    manifest=json.loads(safe(f'Failures/{args.case}/MANIFEST.json').read_text(encoding='utf-8-sig'))
    errors=[]
    for entry in manifest['entries']:
        p=safe(entry['archive_path'])
        if not p.is_file() or p.stat().st_size!=entry['size_bytes'] or digest(p)!=entry['sha256']:errors.append(entry['archive_path'])
        if entry['action']=='move' and safe(entry['original_path']).is_file():errors.append('Retired exclusive file still active: '+entry['original_path'])
    if args.protected:
        for e in manifest['protected_files']:
            p=safe(e['path'])
            if not p.is_file() or p.stat().st_size!=e['size_bytes'] or digest(p)!=e['sha256']:errors.append('Protected mismatch: '+e['path'])
    result={'case_id':manifest['case_id'],'archive_entries_checked':len(manifest['entries']),
        'archive_bytes':sum(x['size_bytes'] for x in manifest['entries']),
        'protected_checked':len(manifest['protected_files']) if args.protected else 0,'errors':errors,'passed':not errors}
    print(json.dumps(result,indent=2))
    raise SystemExit(bool(errors))
if __name__=='__main__':main()
