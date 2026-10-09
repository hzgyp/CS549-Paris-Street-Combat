"""Bounded private native future-floor guard, no reflected/cooked schema changes."""
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source
from revise_source import replace_once
BASE=ROOT/'tmp/g1-playtest-revision-20261008'
def main():
    old=BASE/'candidate_v8';out=BASE/'candidate_v9';assert not out.exists()
    prepared=json.loads((old/'prepare_revision.json').read_text());built=json.loads((old/'build_revision.json').read_text(encoding='utf-8-sig'))
    project=Path(prepared['project']);frozen=old/'FrozenSource';assert not frozen.exists()
    assert verify_source()['source_files']==758
    rows=guard_rows();assert len(rows)==703 and guards_match(rows)
    descriptor=project/'WW2FranceLiberation.uproject';assert digest(descriptor)==prepared['descriptor_sha256']
    for row in prepared['private_source_files']:
        src=project/row['path'];assert digest(src)==row['sha256'];dst=frozen/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    shutil.copyfile(descriptor,frozen/descriptor.name)
    base='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/'
    header=base+'Public/ParisBridgeMission.h';cpp=base+'Private/ParisBridgeMission.cpp';module=base+'Private/ParisBridgeMissionV1.cpp'
    prior=(project/header).read_text(encoding='utf-8');new=replace_once(prior,'    virtual bool InputKey(const FInputKeyEventArgs& Params) override;',
        '    virtual bool InputKey(const FInputKeyEventArgs& Params) override;\n    virtual void PostProcessInput(const float DeltaTime,const bool bGamePaused) override;')
    reflected=lambda s:[line for line in s.splitlines() if any(k in line for k in ['UCLASS','UPROPERTY','UFUNCTION','GENERATED_BODY'])]
    assert reflected(new)==reflected(prior)
    (project/header).write_text(new,encoding='utf-8')
    with (project/cpp).open('a',encoding='utf-8') as f:f.write('\n'+(HERE/'ProneFutureGuard.inc').read_text(encoding='utf-8'))
    (project/module).write_text('#include "Modules/ModuleManager.h"\n'+(HERE/'RevisionTest.inc').read_text(encoding='utf-8'),encoding='utf-8')
    changed=[Path(r['path']).as_posix() for r in prepared['private_source_files'] if digest(project/r['path'])!=r['sha256']]
    assert set(changed)=={header,cpp,module}
    assert digest(descriptor)==prepared['descriptor_sha256']
    out.mkdir();shutil.copytree(old/'UI',out/'UI')
    archive_rows=[dict(r,sha256=built['game_sha256'],size_bytes=(old/'Archive'/r['path']).stat().st_size) if Path(r['path']).as_posix().endswith('/Binaries/Win64/WW2FranceLiberation.exe') else r for r in prepared['archive_files']]
    assert digest(old/'Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==built['game_sha256']
    receipt=dict(prepared,identity='candidate_v9',observer_only_game_build=False,private_method_only_game_build=True,
        reuse_archive=str(old/'Archive'),archive_files=archive_rows,v3_game_sha256=built['game_sha256'],changed_implementation_paths=changed,
        reuse_scope='Private controller PostProcessInput non-reflected virtual override plus implementation and finite observer. Exact reflected declarations/defaults/config/assets/cook dependencies preserved. No model/pose/camera/gun transaction changes.',
        reflected_header_contract_exact=True,
        private_source_files=[dict(r,sha256=digest(project/r['path'])) for r in prepared['private_source_files']],protected_files=rows)
    (out/'prepare_revision.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(identity='candidate_v9',changed=changed,reflected_contract_exact=True),indent=2))
if __name__=='__main__':main()
