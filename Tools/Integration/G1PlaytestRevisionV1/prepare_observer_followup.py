"""Freeze an admitted private build and replace only its opt-in observer cpp."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source
BASE=ROOT/'tmp/g1-playtest-revision-20261008'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('previous');parser.add_argument('identity');parser.add_argument('--pending',action='store_true');args=parser.parse_args()
    assert all(x.replace('_','').isalnum() for x in [args.previous,args.identity])
    old=BASE/args.previous;out=BASE/args.identity;assert not out.exists()
    prepared=json.loads((old/'prepare_revision.json').read_text())
    if args.pending:
        assert not (old/'build_revision.json').exists(),'Pending-only admission must not hide a build'
        built=dict(game_sha256=prepared['v3_game_sha256']);archive=Path(prepared['reuse_archive'])
    else:
        built=json.loads((old/'build_revision.json').read_text(encoding='utf-8-sig'));archive=old/'Archive'
    project=Path(prepared['project']);frozen=old/'FrozenSource';assert not frozen.exists()
    assert verify_source()['source_files']==758
    rows=guard_rows();assert len(rows)==703 and guards_match(rows)
    descriptor=project/'WW2FranceLiberation.uproject'
    assert digest(descriptor)==digest(BASE/'candidate_v3/SourceAtV3/WW2FranceLiberation.uproject')
    for row in prepared['private_source_files']:
        source=project/row['path'];assert digest(source)==row['sha256']
        target=frozen/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    shutil.copyfile(descriptor,frozen/descriptor.name)
    archive_rows=[]
    for row in prepared['archive_files']:
        path=archive/row['path'];expected=built['game_sha256'] if Path(row['path']).as_posix().endswith('/Binaries/Win64/WW2FranceLiberation.exe') else row['sha256']
        if not args.pending or Path(row['path']).as_posix().endswith('/Binaries/Win64/WW2FranceLiberation.exe'):assert digest(path)==expected,str(path)
        archive_rows.append(dict(row,size_bytes=path.stat().st_size,sha256=expected))
    assert len(archive_rows)==len([p for p in archive.rglob('*') if p.is_file()])
    if not args.pending:
        for row in prepared['cooked_files']:assert digest(project/'Saved/Cooked/Windows'/row['path'])==row['sha256']
    else:
        (old/'superseded_before_build.json').write_text(json.dumps(dict(status='preserved_prepared_observer_superseded_before_build',next_identity=args.identity,recipe_sha256=digest(old/'prepare_revision.json'),frozen_source=str(frozen)),indent=2)+'\n')
    module='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp'
    (project/module).write_text('#include "Modules/ModuleManager.h"\n'+(Path(__file__).parent/'RevisionTest.inc').read_text(),encoding='utf-8')
    changed=[Path(r['path']).as_posix() for r in prepared['private_source_files'] if digest(project/r['path'])!=r['sha256']]
    assert changed==[module]
    out.mkdir();shutil.copytree(old/'UI',out/'UI')
    receipt=dict(prepared,identity=args.identity,observer_only_game_build=True,
        reuse_archive=str(archive),archive_files=archive_rows,v3_game_sha256=built['game_sha256'],changed_implementation_paths=changed,
        descriptor_sha256=digest(descriptor),
        reuse_scope='Only the explicit opt-in observer cpp changes. All frozen product sources/headers/defaults/config/cooked/native content exact. Game-only compile; no Editor/cook claim. See dated bounded plan and retained negatives.',
        private_source_files=[dict(r,sha256=digest(project/r['path'])) for r in prepared['private_source_files']],protected_files=rows)
    (out/'prepare_revision.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(identity=args.identity,changed=changed),indent=2))
if __name__=='__main__':main()
