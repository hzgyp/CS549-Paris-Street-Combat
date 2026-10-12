"""Private contact sheets for human visual inspection; never substitutes for approval."""
from pathlib import Path
import argparse
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('identity');a=ap.parse_args()
base=ROOT/'tmp/g1-combat-ui-20261011/checks'/a.identity
paths=sorted(base.glob('*.png'))
assert paths
canvas=Image.new('RGB',(1920,570*((len(paths)+1)//2)),(12,20,16))
draw=ImageDraw.Draw(canvas)
for i,p in enumerate(paths):
    source=Image.open(p); source.thumbnail((960,540))
    x=(i%2)*960;y=(i//2)*570
    draw.text((x+8,y+5),p.name,fill=(245,230,192))
    canvas.paste(source,(x,y+30))
dest=ROOT/'tmp/g1-combat-ui-20261011'/('QA_'+a.identity+'.jpg')
canvas.save(dest,quality=93)
print(dest)
