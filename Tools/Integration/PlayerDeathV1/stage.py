"""Reuse immutable parent runtime files, replacing only the candidate Game."""
from pathlib import Path
import sys,os,shutil,argparse
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,sha,INNER
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
parent=read(ROOT/'tmp/g1-player-death-20261011/freeze.json')['parent']
build=read(OUT/a.revision/'build-game.json');assert build['exit_code']==0
target=OUT/a.revision/'Runtime';assert not target.exists();target.mkdir()
for src in (ROOT/parent['playable_directory']/'Windows').rglob('*'):
    if not src.is_file():continue
    rel=src.relative_to(ROOT/parent['playable_directory']);dst=target/rel
    if rel.as_posix()==INNER:continue
    dst.parent.mkdir(parents=True,exist_ok=True)
    if src.suffix.lower() in {'.cmd','.ps1','.md','.txt','.json','.ini','.log'}:shutil.copyfile(src,dst)
    else:os.link(src,dst)
source=OUT/a.revision/'Project/Binaries/Win64/WW2FranceLiberation.exe';assert sha(source)==build['game_sha256'];shutil.copyfile(source,target/INNER)
write(OUT/a.revision/'runtime.json',dict(status='staged_death_unverified',path=str(target),revision=a.revision,game_sha256=sha(target/INNER)))
print(target)
