from prepare import ROOT,OUT,INNER,read,write,sha
import argparse,os,shutil
def main(revision):
    frozen=read(OUT/'freeze.json');build=read(OUT/revision/'build-game.json')
    assert build['exit_code']==0
    target=OUT/revision/'Runtime';assert not target.exists()
    parent=ROOT/frozen['parent']['playable_directory'];target.mkdir()
    for src in parent.rglob('*'):
        if not src.is_file():continue
        rel=src.relative_to(parent);dst=target/rel;dst.parent.mkdir(parents=True,exist_ok=True)
        if rel.as_posix()==INNER:continue
        if src.suffix.lower() in {'.cmd','.ps1','.md','.txt','.json','.ini','.log'}:shutil.copyfile(src,dst)
        else:os.link(src,dst)
    src=OUT/revision/'Project/Binaries/Win64/WW2FranceLiberation.exe'
    assert sha(src)==build['game_sha256'];shutil.copyfile(src,target/INNER)
    explosion=OUT/'intake-explosion/explosion.wav'
    if explosion.exists():
        shutil.copyfile(explosion,target/'Windows/WW2FranceLiberation/Audio/equipment_explosion.wav')
    write(OUT/revision/'runtime.json',dict(path=str(target),game_sha256=sha(target/INNER),revision=revision,status='staged_unverified'))
    print(str(target/INNER))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('revision');main(ap.parse_args().revision)
