"""Label equally resized native images; no retouching."""
import argparse
from PIL import Image, ImageDraw, ImageFont
from common import BASE, read, write, sha
parser=argparse.ArgumentParser()
parser.add_argument('identity')
args=parser.parse_args()
out=BASE/args.identity
r=read(out/'result.json')
assert not r['errors'] and r['status']=='marked_web_v6_native_views_require_user_review'
assert r['guards_before']==r['guards_after']==611
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
records=[]
for sheet,title,views in (
    ('three_views','盟军 NPC · 标记处左下靠拢，再绕虎口转入左掌 · 双手不动',
        [('after_front','正视'),('after_right','右侧 / 扳机手'),('after_top','俯视')]),
    ('comparison','分步对照 · 原版 → 仅左下平移 → 再绕虎口旋转',
        [('before_right','上一版 V5'),('seated_right','第一步：左下平移'),('after_right','第二步：绕虎口旋转')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41))
    draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),'原生 UE 贴图 · 同姿态静止对照 · 完整接触待人工复核 · 未替换正式资产',font=small,fill=(170,187,203))
    for i,(name,label) in enumerate(views):
        img=Image.open(out/(name+'.png')).convert('RGB')
        assert img.size==(1600,1000)
        canvas.paste(img.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    dest=out/(sheet+'.png')
    assert not dest.exists()
    canvas.save(dest)
    records.append({'path':dest.name,'sha256':sha(dest),'size_bytes':dest.stat().st_size})
write(out/'presentation.json',{'images':records,'original_pixels_retouched':False})
print(records)
