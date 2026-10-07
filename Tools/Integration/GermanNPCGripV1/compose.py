"""Label and lay out original native captures; never retouch source pixels."""
import argparse
from PIL import Image,ImageDraw,ImageFont
from common import *
p=argparse.ArgumentParser();p.add_argument('identity');args=p.parse_args()
assert args.identity.replace('_','').isalnum()
out=BASE/args.identity;r=read(out/'result.json')
assert not r['errors'] and r['status']=='translated_native_views_require_user_review'
assert r['guards_before']==r['guards_after']==618 and r['all_bones_exact']
assert r['before']['bones']==r['after']['bones'] and r['before']['gun_world']['q']==r['after']['gun_world']['q']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
records=[]
for sheet,title,views in (
    ('three_views','德军 NPC · 枪械仅平移 / 双手、手臂与枪角度不变',[('after_front','正视'),('after_right','右侧 / 扳机手'),('after_top','俯视')]),
    ('comparison','德军扳机对食指 · 单次粗定位，不代表完整握持验收',[('before_right','平移前'),('after_right','平移后'),('after_trigger','扳机位置近景')]),
    ('context','固定双手的局限也保留 · 未修左手 / 未替换正式资产',[('after_reverse','反侧 / 左手支撑'),('after_context','完整肩肘腕'),('after_trigger','右手对位')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),'原生 UE 贴图 · 临时内存装配 · 未保存正式地图',font=small,fill=(170,187,203))
    for i,(name,label) in enumerate(views):
        source=out/(name+'.png');img=Image.open(source).convert('RGB');assert img.size==(1600,1000)
        canvas.paste(img.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    dest=out/(sheet+'.png');assert not dest.exists();canvas.save(dest)
    records.append({'path':dest.name,'sha256':sha(dest),'size_bytes':dest.stat().st_size})
write(out/'presentation.json',{'images':records,'original_pixels_retouched':False,'native_originals':[row(out/c['file']) for c in r['captures']]})
print([f['path'] for f in records])
