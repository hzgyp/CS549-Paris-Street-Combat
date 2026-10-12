from pathlib import Path
import sys,os,shutil
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,sha,read,write,INNER
revision=sys.argv[1];parent=read(root/'tmp/g1-grenade-models-20261011/freeze.json')['parent'];build=read(OUT/revision/'build-game.json');assert build['exit_code']==0
target=OUT/revision/'Runtime';target.mkdir(exist_ok=False)
for p in (root/parent['playable_directory']/'Windows').rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(root/parent['playable_directory']);dst=target/rel
    if rel.as_posix()==INNER:continue
    dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
project=Path(read(OUT/revision/'prepare.json')['project'])
shutil.copyfile(project/'Binaries/Win64/WW2FranceLiberation.exe',target/INNER)
base=root/'Assets/LocalWorking/Experiments/GrenadeModels/20261011'
assets=[]
for kind,source,stem in [('Frag',base/'frag_finish_v1','frag'),('Smoke',base/'smoke/finish_v1','smoke')]:
    dest=target/'Windows/WW2FranceLiberation/Equipment/Grenades'/kind;dest.mkdir(parents=True)
    for name in [stem+'_geometry.json',stem+'_albedo.png',stem+'_orm.png',stem+'_normal.png']:
        p=source/name;d=dest/name;shutil.copyfile(p,d);assets.append(dict(path=d.relative_to(target).as_posix(),size_bytes=d.stat().st_size,sha256=sha(d)))
assert sha(target/INNER)==build['game_sha256']
write(OUT/revision/'runtime.json',dict(status='staged_grenade_visual_unverified',path=str(target),revision=revision,game_sha256=sha(target/INNER),assets=assets))
print(target)
