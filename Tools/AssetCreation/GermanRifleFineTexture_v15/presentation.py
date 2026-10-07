"""Fixed matched source images, uniform scaling/labels only."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
OLD=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-finish-v14/comparison_v1'
p=argparse.ArgumentParser();p.add_argument('--comparison',required=True);p.add_argument('--out',required=True)
a=p.parse_args();new=Path(a.comparison).resolve();out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True)
canvas=Image.new('RGB',(2400,1560),(30,34,37));draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27)
titles=['Allied M1 reference','German V14 - before','German V15 - native grain detail'];rows=[]
for col,title in enumerate(titles):draw.text((col*800+15,16),title,font=font,fill=(235,235,235))
for row,view in enumerate(['whole','stock','receiver']):
    for col in range(3):
        path=(new/('allied_m1_'+view+'.png')) if col==0 else (OLD/('german_v14_'+view+'.png')) if col==1 else (new/('german_v15_'+view+'.png'))
        im=Image.open(path).convert('RGB');assert im.size==(1200,700)
        y=60+row*500;draw.text((col*800+15,y),view.capitalize()+' / same camera, light and scale',font=font,fill=(200,207,210))
        canvas.paste(im.resize((800,467),Image.Resampling.LANCZOS),(col*800,y+33))
        rows.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_size':list(im.size)})
canvas.save(out/'m1_v14_v15.png')
# Additional1:1 crop comparison: same rectangle and native pixels, explicitly
# labeled. This supplements, never replaces, uncropped original evidence.
close=Image.new('RGB',(1600,640),(30,34,37));d=ImageDraw.Draw(close)
for col,variant in enumerate(['german_v14','german_v15']):
    path=(OLD if col==0 else new)/(variant+'_stock.png');im=Image.open(path).convert('RGB')
    box=(130,160,910,690);crop=im.crop(box);close.paste(crop,(col*800+10,80))
    d.text((col*800+15,16),variant+' / same stock crop at 1:1 pixels',font=font,fill=(235,235,235))
close.save(out/'v14_v15_stock_native.png')
(out/'presentation.json').write_text(json.dumps({'method':'Main sheet labels/uniform Lanczos resize; native sheet identical explicit crop only, no colour retouch/sharpening',
  'native_crop_box':[130,160,910,690],'inputs':rows},indent=2),encoding='utf-8')
print(out/'m1_v14_v15.png')
