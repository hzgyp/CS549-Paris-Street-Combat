from prepare import ROOT, OUT, write, sha
from stage import main
import argparse, shutil
a=argparse.ArgumentParser();a.add_argument('revision');a=a.parse_args()
main(a.revision)
src=ROOT/'Assets/LocalWorking/Experiments/PressureMine/20261011-v1/finish_v2'
dst=OUT/a.revision/'Runtime/Windows/WW2FranceLiberation/Equipment/Mine'
dst.mkdir(parents=True)
rows=[]
for name in ['mine_geometry.json','mine_albedo.png','mine_orm.png','mine_normal.png']:
    shutil.copyfile(src/name,dst/name)
    assert sha(src/name)==sha(dst/name)
    rows.append(dict(name=name,bytes=(dst/name).stat().st_size,sha256=sha(dst/name)))
write(OUT/a.revision/'mine-assets.json',dict(model_source=str(src),files=rows,native_writes=False))
