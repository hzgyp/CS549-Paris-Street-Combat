"""Label/lay out original diagnostic pixels only, never retouch contact geometry."""
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,guards
OUT=STORE/'Evidence/GermanNPCTriggerLowerV7/review_v1'
r=read(OUT/'result.json');assert not r['errors'] and len(r['images'])==10
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
def sheet(rows,name):
    im=Image.new('RGB',(1800,170+len(rows)*690),'#20252b');draw=ImageDraw.Draw(im)
    draw.text((18,12),'德军 V7 · 保留抬起的拇指 / 扳机支点 / 枪托下压 8°',font=font,fill='#efb67b')
    draw.text((18,55),'橙色：右拇指，蓝色：食指；左手整臂随枪转动。灰模诊断，仍有接触问题，未正式采用。',font=small,fill='#d2d8df')
    draw.text((18,103),'修改前（已抬拇指）',font=font,fill='white');draw.text((918,103),'修改后（枪托下压）',font=font,fill='white')
    for i,(view,label) in enumerate(rows):
        y=170+i*690
        for j,stage in enumerate(('before','after')):
            source=Image.open(OUT/(stage+'_'+view+'.png')).convert('RGB')
            source=source.resize((900,638),Image.Resampling.LANCZOS);im.paste(source,(j*900,y+42))
            draw.text((j*900+18,y+3),label,font=font,fill='#d2d8df')
    dest=OUT/name;assert not dest.exists();im.save(dest);return row(dest)
rows=[sheet([('reverse','反侧 · 拇指与枪托'),('right','右侧 · 扳机手'),('top','俯视 · 枪托与虎口')],'three_views.png'),
      sheet([('support','左手扶枪随动'),('context','完整双臂姿态')],'context.png')]
write(OUT/'presentation.json',{'status':'labeled_directional_comparison_not_full_contact_acceptance','images':rows,
    'formal_selected':False,'native_tested':False,'guards':guards(),'viewed_originals':10})
print('\n'.join(str(ROOT/r['path']) for r in rows))
