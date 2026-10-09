"""Move explicit closed private trial identities, preserving raw paths and selected hashes."""
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures'

def main():
    p=argparse.ArgumentParser();p.add_argument('case');p.add_argument('identities',nargs='+');a=p.parse_args()
    case=(ROOT/'Failures'/a.case).resolve();assert case.parent==ROOT/'Failures' and case.is_dir()
    manifest=case/'MANIFEST.json';record=json.loads(manifest.read_text()) if manifest.exists() else {'archives':[]}
    for identity in a.identities:
        assert identity.replace('_','').replace('-','').isalnum()
        source=(ROOT/'tmp/mvp-closeout-20261008'/identity).resolve();dest=(STORE/identity).resolve()
        assert source.parent==(ROOT/'tmp/mvp-closeout-20261008').resolve() and source.is_dir()
        assert dest.parent==STORE.resolve() and not dest.exists() and source.drive==dest.drive
        selected=[]
        for relative in ['launch.json','game.log','result.json','capture_failure.json','capture_source.cpp','performance_summary.json','read_only_audit.json','finite_stress_result.json','instrument.json','prepare.json','native_candidate.json','agent_candidate.json',
            'instrument_build.log','Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp',
            'Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp',
            'Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Public/ParisBridgeMission.h']:
            path=source/relative
            if path.is_file():selected.append(dict(path=relative,size_bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        dest.parent.mkdir(parents=True,exist_ok=True);os.rename(source,dest)
        assert not source.exists() and all((dest/r['path']).stat().st_size==r['size_bytes'] and hashlib.sha256((dest/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in selected)
        record['archives'].append(dict(identity=identity,old_path=str(source),archive_path=str(dest),receipts=selected,
            scope='Whole directory retained by same-volume rename; selected receipt/source hashes checked, NOT a whole-bundle byte audit'))
        manifest.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'case':a.case,'moved':a.identities,'archives':len(record['archives'])}))

if __name__=='__main__':main()
