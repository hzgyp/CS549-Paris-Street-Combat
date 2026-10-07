"""Label original textured full-arm/body native comparisons without retouch."""
import argparse
from PIL import Image,ImageDraw,ImageFont
from common import *
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');assert not n['errors']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
records=[]
for name,title,views in (
    ('comparison','盟军 NPC · 枪与双手作为整体降低枪口 · 两侧手臂联动',
     [('before_context','之前：仰角约 33°'),('after_context','当前：接近水平'),('after_reverse','当前：反侧')]),
    ('three_views','当前射击姿态 · 双手—枪械相对位置不变 · 原贴图三视图',
     [('after_front','正视'),('after_right','右侧'),('after_top','俯视')]),
    ('grip_details','握持关系保留 · 不再调整手指 · 原有扳机相交仍保留',
     [('after_trigger','右手'),('after_reverse_trigger','右手反側'),('after_support','左支撑手')]),
    ('body_shoulder','完整手臂与肩部检查 · 不拉长骨骼、不单独搬手掌',
     [('after_body_right','全身侧视'),('after_body_front','全身正视'),('after_shoulder','枪托与肩部')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),'本轮静态姿态对照 · 未替换正式 NPC 资产 / 未验证射击与移动',font=small,fill=(222,173,125))
    for i,(view,label) in enumerate(views):
        im=Image.open(out/(view+'.png')).convert('RGB');assert im.size==(1600,1000)
        canvas.paste(im.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    p=out/(name+'.png');assert not p.exists();canvas.save(p)
    records.append({'path':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size})
write(out/'presentation.json',{'images':records,'retouched':False,'comparison_only':True,'contact_accepted':False})
print(records)
