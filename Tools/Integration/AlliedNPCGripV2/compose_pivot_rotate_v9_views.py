"""Label matched native V7/V9 images, no retouching."""
import argparse
from PIL import Image,ImageDraw,ImageFont
from common import *
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;r=read(out/'result.json')
assert not r['errors'] and r['status']=='pivot_rotate_v9_native_views_require_user_review'
assert r['guards_before']==r['guards_after']==611
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
records=[]
for name,title,views in (
    ('three_views','盟军 NPC · 围绕原握点继续上仰2° · 没有整体平移',
     [('after_front','正视'),('after_right','右侧 / 扳机手'),('after_top','俯视')]),
    ('comparison','V7 → V9 · 右手和手指不变 · 左臂随枪旋转',
     [('before_right','之前：V7'),('after_right','本轮：额外上仰2°'),('after_trigger','本轮：扳机局部')]),
    ('arm_context','原握点固定 · 左肩固定，整条左臂联动 · 原骨段长度保持',
     [('before_context','之前：全臂'),('after_context','本轮：全臂'),('after_reverse','本轮：背侧')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),'原生 UE 贴图 · 静止对照 · 局部交叉仍需复核 · 未替换正式资产',font=small,fill=(170,187,203))
    for i,(view,label) in enumerate(views):
        image=Image.open(out/(view+'.png')).convert('RGB');assert image.size==(1600,1000)
        canvas.paste(image.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    path=out/(name+'.png');assert not path.exists();canvas.save(path)
    records.append({'path':path.name,'sha256':sha(path),'size_bytes':path.stat().st_size})
write(out/'presentation.json',{'images':records,'retouched':False,'diagnostic_not_gameplay':True})
print(records)
