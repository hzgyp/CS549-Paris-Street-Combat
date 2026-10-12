"""Stage immutable original assets and new Game without altering the parent trial."""
from pathlib import Path
import argparse,sys,os,shutil
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,sha,INNER
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
freeze=read(ROOT/'tmp/g1-combat-ui-20261011/freeze.json')
parent=ROOT/freeze['parent']['playable_directory']
build=read(OUT/a.revision/'build-game.json');assert build['exit_code']==0
target=OUT/a.revision/'Runtime';assert not target.exists();target.mkdir()
for src in parent.rglob('*'):
    if not src.is_file():continue
    rel=src.relative_to(parent)
    if rel.as_posix()==INNER or rel.parts[0].startswith('PLAY_') or len(rel.parts)==1:continue
    dst=target/rel;dst.parent.mkdir(parents=True,exist_ok=True)
    if src.suffix.lower() in {'.ini','.json','.md','.txt','.cmd','.ps1','.log'}:shutil.copyfile(src,dst)
    else:os.link(src,dst)
src=OUT/a.revision/'Project/Binaries/Win64/WW2FranceLiberation.exe'
assert sha(src)==build['game_sha256'];shutil.copyfile(src,target/INNER)
write(OUT/a.revision/'runtime.json',dict(status='staged_ui_unverified',path=str(target),game_sha256=sha(target/INNER),revision=a.revision))
print(target)
