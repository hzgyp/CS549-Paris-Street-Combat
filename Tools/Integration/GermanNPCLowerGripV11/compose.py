"""Original-pixel contact comparison only; never retouch finger/wood geometry."""
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,guards
BASE=STORE/'Evidence/GermanNPCLowerGripV11';OUT=BASE/'frame_failure_views_v1'
r=read(OUT/'result.json');assert not r['errors'] and len(r['images'])==12
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
def sheet(folder,rows,name,heading):
    im=Image.new('RGB',(1800,180+len(rows)*690),'#20252b');draw=ImageDraw.Draw(im)
    draw.text((18,12),heading,font=font,fill='#efb67b')
    draw.text((18,55),'黄：中指 / 紫：无名指 / 绿：小指；拇指、食指和枪不动。仍有局部相交，未正式采用。',font=small,fill='#d2d8df')
    draw.text((18,108),'修改前（已认可 V10 拇指）',font=font,fill='white')
    draw.text((918,108),'局部试验（未通过完整接触检查）',font=font,fill='white')
    for i,(view,label) in enumerate(rows):
        y=180+i*690
        for j,stage in enumerate(('before','after')):
            original=Image.open(folder/(stage+'_'+view+'.png')).convert('RGB')
            im.paste(original.resize((900,638),Image.Resampling.LANCZOS),(j*900,y+42))
            draw.text((j*900+18,y+3),label,font=font,fill='#d2d8df')
    dest=folder/name;assert not dest.exists();im.save(dest);return row(dest)
images=[sheet(OUT,[('right','右侧 · 三指与掌心'),('reverse','反侧 · 枪托下缘'),('underside','仰视 · 指腹包握')],'finger_contact.png','德军 V11 · 三指贴合局部试验 / 保留拇指、食指、枪位'),
        sheet(OUT,[('top','俯视 · 已认可拇指保持'),('context','完整双臂 · 骨骼与枪保持原位')],'context.png','德军 V11 · 上方与双臂对照 / 静态诊断，不是游戏动作验收'),
        sheet(BASE/'failure_views_v1',[('right','右侧 · 现成换弹握姿仍虚握'),('underside','仰视 · 现成握姿对照')],'source_failure.png','德军 V11 · 完整现成握姿直接复用未通过 / 保留失败对照')]
write(OUT/'presentation.json',{'status':'retained_failed_grip_comparison_not_accepted','images':images,
    'inputs':r['images']+read(BASE/'failure_views_v1/result.json')['images']+[row(Path(__file__))],
    'formal_selected':False,'native_tested':False,'guards':guards(),'opened_originals':24,
    'occluded_oblique_views_retained_not_contact_proof':True})
print('\n'.join(str(ROOT/e['path']) for e in images))
