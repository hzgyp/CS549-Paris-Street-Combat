from pathlib import Path
import sys,os,shutil
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,sha,read,write,INNER
rev=sys.argv[1];parent=read(root/'tmp/g1-grenade-equip-20261011/freeze.json')['parent'];build=read(OUT/rev/'build-game.json');assert build['exit_code']==0
target=OUT/rev/'Runtime';target.mkdir(exist_ok=False)
for p in (root/parent['playable_directory']/'Windows').rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(root/parent['playable_directory']);dst=target/rel
    if rel.as_posix()==INNER:continue
    dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
project=Path(read(OUT/rev/'prepare.json')['project']);shutil.copyfile(project/'Binaries/Win64/WW2FranceLiberation.exe',target/INNER)
assert sha(target/INNER)==build['game_sha256']
write(OUT/rev/'runtime.json',dict(status='staged_grenade_equip_unverified',path=str(target),revision=rev,game_sha256=sha(target/INNER),assets=parent['assets']))
print(target)
