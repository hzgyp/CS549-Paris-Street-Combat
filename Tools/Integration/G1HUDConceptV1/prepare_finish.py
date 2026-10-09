"""Freeze viewed V2; replace only Circle/Soldier drawing helpers for V3."""
import json,shutil,sys
from pathlib import Path
from prepare import ROOT,HERE,BASE,CPP,once
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source

def part(text,start,end):return text[text.index(start):text.index(end,text.index(start))]

def main():
    old=BASE/'hud_v2';out=BASE/'hud_v3';assert not out.exists()
    p=json.loads((old/'prepare_revision.json').read_text());b=json.loads((old/'build_revision.json').read_text(encoding='utf-8-sig'))
    project=Path(p['project']);frozen=old/'FrozenSource';assert not frozen.exists()
    assert verify_source()['source_files']==758
    g=guard_rows();assert len(g)==703 and guards_match(g)
    for r in p['private_source_files']:assert digest(project/r['path'])==r['sha256']
    assert digest(project/'WW2FranceLiberation.uproject')==p['descriptor_sha256']
    source=(project/CPP).read_text(encoding='utf-8');start=source.index('void AParisBridgeHUD::DrawHUD()\n');end=source.index('\nnamespace ParisPronePrediction\n',start)
    oldhud=source[start:end].rstrip();newhud=(HERE/'HUD.inc').read_text(encoding='utf-8').rstrip();admitted=oldhud
    for begin,finish in [('    auto Circle=','    auto Diamond='),('        auto Soldier=','        Soldier(55')]:
        admitted=once(admitted,part(oldhud,begin,finish),part(newhud,begin,finish))
    assert admitted==newhud,'No other UI/layout/font/resource change admitted'
    archive=old/'Archive';archive_rows=[dict(path=f.relative_to(archive).as_posix(),size_bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(archive.rglob('*')) if f.is_file()]
    assert len(archive_rows)==47 and digest(archive/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==b['game_sha256']
    for r in p['private_source_files']:
        dst=frozen/r['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(project/r['path'],dst)
    shutil.copyfile(project/'WW2FranceLiberation.uproject',frozen/'WW2FranceLiberation.uproject')
    (project/CPP).write_text(source[:start]+newhud+'\n'+source[end:],encoding='utf-8')
    changed=[Path(r['path']).as_posix() for r in p['private_source_files'] if digest(project/r['path'])!=r['sha256']];assert changed==[CPP]
    out.mkdir();shutil.copytree(old/'UI',out/'UI')
    result=dict(p,identity='hud_v3',reuse_archive=str(archive),archive_files=archive_rows,v3_game_sha256=b['game_sha256'],
        reuse_scope='Only Circle/Soldier primitive drawing helpers change from viewed V2; exact other HUD/layout/font/marker/resource/nonrender/input/save/schema/config/observer/cooked content.',
        private_source_files=[dict(r,sha256=digest(project/r['path'])) for r in p['private_source_files']],protected_files=g)
    (out/'prepare_revision.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(identity='hud_v3',admitted_helpers=['Circle','Soldier'],changed=changed),indent=2))
if __name__=='__main__':main()
