"""Freeze V5, admit a distinct finite terrain/aim observer; assets remain exact."""
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source
BASE=ROOT/'tmp/g1-playtest-revision-20261008'

def main():
    old=BASE/'candidate_v5';out=BASE/'candidate_v6';assert not out.exists()
    prepared=json.loads((old/'prepare_revision.json').read_text())
    built=json.loads((old/'build_revision.json').read_text(encoding='utf-8-sig'))
    project=Path(prepared['project']);frozen=old/'SourceAtV5';assert not frozen.exists()
    assert verify_source()['source_files']==758
    rows=guard_rows();assert len(rows)==703 and guards_match(rows)
    for row in prepared['private_source_files']:
        source=project/row['path'];assert digest(source)==row['sha256']
        target=frozen/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    archive_rows=[]
    for row in prepared['archive_files']:
        path=old/'Archive'/row['path'];expected=built['game_sha256'] if Path(row['path']).as_posix().endswith('/Binaries/Win64/WW2FranceLiberation.exe') else row['sha256']
        assert digest(path)==expected,str(path)
        archive_rows.append(dict(row,size_bytes=path.stat().st_size,sha256=expected))
    assert len(archive_rows)==len([p for p in (old/'Archive').rglob('*') if p.is_file()])
    for row in prepared['cooked_files']:assert digest(project/'Saved/Cooked/Windows'/row['path'])==row['sha256']
    out.mkdir();shutil.copytree(old/'UI',out/'UI')
    negative=[]
    for identity in ['actions_v1','checkpoint_v1']:
        loc=BASE/identity;result=json.loads((loc/'result.json').read_text());launch=json.loads((loc/'launch.json').read_text(encoding='utf-8-sig'))
        assert launch['exit_code']==0 and result['status'].startswith('failed_')
        negative.append(dict(identity=identity,status=result['status'],files=[dict(path=str(f.relative_to(ROOT)),size_bytes=f.stat().st_size,sha256=digest(f)) for f in loc.glob('*') if f.is_file()]))
    (out/'retained_negatives.json').write_text(json.dumps(negative,indent=2)+'\n')
    module='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp'
    (project/module).write_text('#include "Modules/ModuleManager.h"\n'+(Path(__file__).parent/'RevisionTest.inc').read_text(),encoding='utf-8')
    changed=[Path(r['path']).as_posix() for r in prepared['private_source_files'] if digest(project/r['path'])!=r['sha256']]
    assert changed==[module]
    receipt=dict(prepared,identity='candidate_v6',reuse_archive=str(old/'Archive'),archive_files=archive_rows,
        v3_game_sha256=built['game_sha256'],changed_implementation_paths=changed,
        reuse_scope='V5 frozen source, only opt-in observer cpp changes; headers/defaults/config/native content exact. Preserve V5 terrain refusal and legitimate player death negatives. V6 does not alter product behavior.',
        private_source_files=[dict(r,sha256=digest(project/r['path'])) for r in prepared['private_source_files']],protected_files=rows)
    (out/'prepare_revision.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(identity='candidate_v6',changed=changed,retained_negatives=[r['status'] for r in negative]),indent=2))
if __name__=='__main__':main()
