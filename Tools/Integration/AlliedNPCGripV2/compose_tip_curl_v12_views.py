"""Label actual original UE views; no image/material retouch."""
import argparse
from PIL import Image,ImageDraw,ImageFont
from common import *
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');t=read(BASE/'tip_curl_v12/result.json');assert not n['errors']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
records=[]
for name,title,views in (
    ('comparison','仅食指末节再向内弯 3.5° · 总计约 10.5° · 枪位和其他关节不变',
     [('before_trigger','之前：7°'),('after_trigger','当前：10.5°'),('after_reverse_trigger','当前：反侧')]),
    ('three_views','盟军 NPC · 仅食指末节增加弯曲 · 原贴图三视图',
     [('after_front','正视'),('after_right','右侧'),('after_top','俯视')]),
    ('trigger_details','食指指尖局部 · 现成 D059 姿态复用 · 其他关节不动',
     [('after_trigger','右侧'),('after_reverse_trigger','反侧'),('after_under_trigger','底部')]),
    ('arm_context','只改食指末节 · 右腕、枪和整条左臂保持当前姿态',
     [('before_context','之前：全臂'),('after_context','当前：全臂'),('after_reverse','当前：背侧')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),'扳机薄片相交仍未解决 · 本轮局部比较，未替换正式资产',font=small,fill=(222,173,125))
    for i,(view,label) in enumerate(views):
        im=Image.open(out/(view+'.png')).convert('RGB');assert im.size==(1600,1000)
        canvas.paste(im.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    p=out/(name+'.png');assert not p.exists();canvas.save(p)
    records.append({'path':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size})
write(out/'presentation.json',{'images':records,'retouched':False,'comparison_only':True,'contact_accepted':False})
print(records)
