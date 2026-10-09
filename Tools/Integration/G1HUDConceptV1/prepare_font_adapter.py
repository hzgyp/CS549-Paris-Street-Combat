"""Stop V1 visual failure and admit the bounded Canvas runtime-UFont adapter."""
import json,shutil,sys
from pathlib import Path
from prepare import ROOT,HERE,BASE,STORE,CPP,once
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source

def main():
    old=BASE/'hud_v1';out=BASE/'hud_v2';assert not out.exists()
    previous=json.loads((old/'prepare_revision.json').read_text())
    built=json.loads((old/'build_revision.json').read_text(encoding='utf-8-sig'))
    project=Path(previous['project']);frozen=old/'FrozenSource';assert not frozen.exists()
    assert verify_source()['source_files']==758
    guards=guard_rows();assert len(guards)==703 and guards_match(guards)
    for r in previous['private_source_files']:assert digest(project/r['path'])==r['sha256']
    assert digest(project/'WW2FranceLiberation.uproject')==previous['descriptor_sha256']
    archive=old/'Archive';archive_rows=[]
    for f in sorted(archive.rglob('*')):
        if f.is_file():archive_rows.append(dict(path=f.relative_to(archive).as_posix(),size_bytes=f.stat().st_size,sha256=digest(f)))
    assert len(archive_rows)==47 and digest(archive/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==built['game_sha256']
    for r in previous['private_source_files']:
        dst=frozen/r['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(project/r['path'],dst)
    shutil.copyfile(project/'WW2FranceLiberation.uproject',frozen/'WW2FranceLiberation.uproject')
    failed=STORE/'Evidence/Failures/MI013/hud_v1_missing_text';failed.mkdir(parents=True,exist_ok=False)
    for name in ['launch.json','game.log','read_only_audit.json','ready.png']:shutil.copyfile(BASE/'hud_plain_v1'/name,failed/name)
    shutil.copyfile(frozen/CPP,failed/'ParisBridgeMission.cpp')
    manifest=[dict(path=f.name,size_bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(failed.iterdir())]
    (failed/'MANIFEST.json').write_text(json.dumps(dict(status='stopped_visual_failure_missing_all_text',numeric_audit='Identity/startup only, not visual acceptance',files=manifest),indent=2)+'\n')
    source=(frozen/CPP).read_text(encoding='utf-8');start=source.index('void AParisBridgeHUD::DrawHUD()\n');end=source.index('\nnamespace ParisPronePrediction\n',start)
    new=source[:start]+(HERE/'HUD.inc').read_text(encoding='utf-8').rstrip()+'\n'+source[end:]
    new=once(new,'#include "GlobalRenderResources.h"\n','#include "GlobalRenderResources.h"\n#include "Engine/Font.h"\n#include "UObject/StrongObjectPtr.h"\n')
    (project/CPP).write_text(new,encoding='utf-8')
    changed=[Path(r['path']).as_posix() for r in previous['private_source_files'] if digest(project/r['path'])!=r['sha256']]
    assert changed==[CPP]
    # Everything outside the draw function and these two type headers is identical.
    assert new[new.index('\nnamespace ParisPronePrediction\n'):]==source[end:]
    head=new[:new.index('void AParisBridgeHUD::DrawHUD()\n')].replace('#include "Engine/Font.h"\n#include "UObject/StrongObjectPtr.h"\n','')
    assert head==source[:start]
    out.mkdir();shutil.copytree(old/'UI',out/'UI')
    receipt=dict(previous,identity='hud_v2',reuse_archive=str(archive),archive_files=archive_rows,v3_game_sha256=built['game_sha256'],
        reuse_scope='Bounded transient runtime UFont adapter plus actual glyph-draw assertion inside the HUD function; two required type headers. All layout/font bytes/nonrender/save/input/cook policy exact.',
        private_source_files=[dict(r,sha256=digest(project/r['path'])) for r in previous['private_source_files']],protected_files=guards)
    (out/'prepare_revision.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(identity='hud_v2',changed=changed,nonrender_policy_exact=True),indent=2))
if __name__=='__main__':main()
