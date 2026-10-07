"""Label real UE originals; retain blade-contact failure, no retouch."""
import argparse
from PIL import Image,ImageDraw,ImageFont
from common import *
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');assert not n['errors']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
records=[]
for name,title,views in (
    ('three_views','盟军 NPC · 枪沿箭头后移 0.4cm · 现成动作食指末节轻弯 7°',
     [('after_front','正视'),('after_right','右侧'),('after_top','俯视')]),
    ('trigger_details','食指局部 · 右腕、食指根部和其他手指不变',
     [('after_trigger','右侧'),('after_reverse_trigger','反侧'),('after_under_trigger','底部')]),
    ('comparison','之前 V10 → 当前 V11 · UE 原贴图对照',
     [('before_trigger','之前：直食指'),('after_trigger','当前：轻弯指尖'),('after_reverse_trigger','当前：反侧')]),
    ('arm_context','枪后移 · 全左臂保持原骨段长度联动 · 静态对照',
     [('before_context','之前全臂'),('after_context','当前全臂'),('after_reverse','当前背侧')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),'扳机薄片仍有相交 · 比较版，未采用为正式资产 · 动作未验',font=small,fill=(222,173,125))
    for i,(view,label) in enumerate(views):
        im=Image.open(out/(view+'.png')).convert('RGB');assert im.size==(1600,1000)
        canvas.paste(im.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    path=out/(name+'.png');assert not path.exists();canvas.save(path)
    records.append({'path':path.name,'sha256':sha(path),'size_bytes':path.stat().st_size})
write(out/'presentation.json',{'images':records,'retouched':False,'comparison_contact_failed':True})
print(records)
