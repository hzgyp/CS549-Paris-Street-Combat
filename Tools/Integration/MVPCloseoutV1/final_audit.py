"""Read-only closeout audit; write one private dated receipt, never adopt a release."""
import ast
import hashlib
import json
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1'
sys.path.insert(0, str(ROOT / 'Tools/Integration/NPCInteractionV1'))
from common import digest, guard_rows, guards_match
sys.path.insert(0, str(ROOT / 'Tools/Integration'))
from verify_team_source import verify_source


def main():
    out = STORE / 'final_audit_v1.json'
    assert not out.exists(), 'Preserve occupied audit identity'
    started = time.monotonic()
    source = verify_source()
    assert source['source_files'] == 758
    guards = guard_rows()
    assert len(guards) == 703 and guards_match(guards)
    checked = []
    all_paths = set()
    for name, count in [('france-liberation-content', 15850), ('paris-gameplay-native-playtest', 359)]:
        manifest_path = ROOT / 'Assets/Sync/manifests' / (name + '.json')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        assert len(manifest['files']) == count
        size = 0
        for row in manifest['files']:
            path = ROOT / row['path']
            assert path.resolve().is_relative_to(ROOT.resolve()), 'Asset path escapes workspace'
            assert row['path'] not in all_paths, 'Duplicate cross-manifest file'
            all_paths.add(row['path'])
            assert path.stat().st_size == row['size_bytes'] and digest(path) == row['sha256'], row['path']
            size += row['size_bytes']
        assert size == manifest['size_bytes']
        checked.append(dict(manifest=name, version=manifest['asset_version'],
                            files=count, size_bytes=size, manifest_sha256=digest(manifest_path)))
    delivery = STORE / 'delivery_v1'
    receipt = json.loads((delivery / 'delivery_receipt.json').read_text())
    assert receipt['status'] == 'private_review_bundle_prepared_not_selected'
    assert receipt['media_status'] == 'pending' and receipt['demo_binary_sha256'] is None
    archive = delivery / 'Paris_Street_Combat_G1_Private_Candidate_Win64.zip'
    assert archive.stat().st_size == receipt['zip_size_bytes']
    assert digest(archive) == receipt['zip_sha256']
    with zipfile.ZipFile(archive) as z:
        names = set(z.namelist())
        assert len(names) == len(z.namelist()), 'Duplicate ZIP entry'
        for row in receipt['source_patch_files']:
            relative = row['path'].replace('\\', '/')
            assert 'Content' not in Path(relative).parts
            assert digest(delivery / 'SourcePatch' / relative) == row['sha256']
            assert hashlib.sha256(z.read('SourcePatch/' + relative)).hexdigest() == row['sha256']
        for name in ['PLAY_G1_CANDIDATE.cmd', 'README_FIRST.txt', 'README_FIRST_ZH.txt',
                     'build_manifest.json', 'Prerequisites/vc_redist.x64.exe']:
            assert hashlib.sha256(z.read(name)).hexdigest() == digest(delivery / name)
    retained_count = 0
    for relative, expected in receipt['retained_receipt_hashes'].items():
        assert digest(delivery / 'Evidence' / relative) == expected
        retained_count += 1
    pdf = STORE / 'progress_v1/output/pdf/Paris_Street_Combat_Assignment3_Progress.pdf'
    reader = PdfReader(pdf)
    assert len(reader.pages) == 2
    links = []
    for page in reader.pages:
        assert page.extract_text().strip()
        for annotation in page.get('/Annots', []):
            action = annotation.get_object().get('/A', {})
            if '/URI' in action:
                links.append(str(action['/URI']))
    assert links == ['https://github.com/hzgyp/CS549-Paris-Street-Combat']
    tools = sorted((ROOT / 'Tools/Integration/MVPCloseoutV1').glob('*.py'))
    for tool in tools:
        ast.parse(tool.read_text(encoding='utf-8'), filename=str(tool))
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert head == receipt['baseline_git']
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True, capture_output=True)
    # A previous archive receipt proves full cooked-file ZIP readback. This audit
    # rehashes the immutable whole ZIP and independently checks all source entries.
    result = dict(status='pass_private_candidate_integrity_not_mvp_acceptance',
                  checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  elapsed_seconds=time.monotonic()-started, baseline_git=head,
                  canonical_source=source, canonical_protected_files=len(guards),
                  asset_manifests=checked, total_asset_files=len(all_paths),
                  total_asset_bytes=sum(r['size_bytes'] for r in checked),
                  zip_sha256=receipt['zip_sha256'], zip_size_bytes=receipt['zip_size_bytes'],
                  source_patch_files_verified=len(receipt['source_patch_files']),
                  retained_receipts_verified=retained_count,
                  earlier_cooked_zip_full_readback=receipt['zip_cooked_sha256_readback'],
                  pdf=dict(path=str(pdf.relative_to(ROOT)), sha256=digest(pdf), pages=2,
                           external_links=links, link_access='Prior source verification; no new access test'),
                  parsed_python_tools=len(tools), media_status='pending',
                  limits=receipt['limits'])
    out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['asset_manifests', 'pdf']}, indent=2))


if __name__ == '__main__':
    main()
