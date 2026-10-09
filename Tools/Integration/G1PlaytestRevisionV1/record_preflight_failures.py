"""Authenticate stopped preflight/compile evidence, never traverse Content links."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match

def main():
    out=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/Failures/MI012'
    target=out/'preflight_manifest_v1.json';assert not target.exists()
    rows=guard_rows();assert len(rows)==703 and guards_match(rows)
    failed=out/'candidate_v2'
    build=json.loads((failed/'build_revision.json').read_text(encoding='utf-8-sig'))
    assert build['status']=='editor_compile_failed' and build['editor_exit_code']!=0
    log=(failed/'editor_build.log').read_text(errors='replace');assert 'error C2181' in log
    assert not (failed/'uat.log').exists() and not (failed/'Archive').exists()
    prepared=json.loads((failed/'prepare_revision.json').read_text())
    source=[]
    for row in prepared['private_source_files']:
        f=failed/'Project'/row['path'];assert digest(f)==row['sha256'];source.append(row)
    receipt=dict(status='retained_preflight_negatives_no_native_save_or_runtime',
        candidate_v1='Stale 3 October V6 guard stops before wrapper/engine; current retained bytes authenticated by 4 October recovery and current epoch.',
        candidate_v2='C2181 unbraced UE_LOG else; compile stops before cook/runtime.',
        protected_files_unchanged=703,archived_path=str(failed.relative_to(ROOT)),source_files=source,
        receipts=[dict(path=str(f.relative_to(out)),sha256=digest(f)) for f in [failed/'editor_build.log',failed/'build_revision.json',failed/'prepare_revision.json']],
        scope='Source/receipt manifest only, not all intermediate compiler caches or linked original Content bytes')
    target.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
if __name__=='__main__':main()
