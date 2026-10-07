"""Labels and uniform resizing only; no retouch or contrast change."""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[3]
OLD=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-texture-comparison/m1_v12_v1'
p=argparse.ArgumentParser();p.add_argument('--comparison',required=True);p.add_argument('--out',required=True)
a=p.parse_args();new=Path(a.comparison).resolve();out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True)
canvas=Image.new('RGB',(2400,1560),(30,34,37));draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27)
titles=['Allied M1 reference','German V12 - before','German V13 - localized wear']
views=['whole','stock','receiver'];rows=[]
for col,title in enumerate(titles):draw.text((col*800+15,16),title,font=font,fill=(235,235,235))
for row,view in enumerate(views):
    for col in range(3):
        path=(new/('allied_m1_'+view+'.png')) if col==0 else (OLD/('german_v12_'+view+'.png')) if col==1 else (new/('german_v13_'+view+'.png'))
        im=Image.open(path).convert('RGB');assert im.size==(1200,700)
        y=60+row*500;draw.text((col*800+15,y),view.capitalize()+' / same camera and scale',font=font,fill=(200,207,210))
        canvas.paste(im.resize((800,467),Image.Resampling.LANCZOS),(col*800,y+33))
        rows.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_size':list(im.size)})
canvas.save(out/'m1_v12_v13.png')
(out/'presentation.json').write_text(json.dumps({'method':'labels, uniform Lanczos resize, no crop/retouch','inputs':rows},indent=2),encoding='utf-8')
print(out/'m1_v12_v13.png')
