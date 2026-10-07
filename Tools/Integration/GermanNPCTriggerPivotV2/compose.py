"""Present unretouched native before/after pixels with explicit fixed-pivot scope."""
import sys,argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import *
p=argparse.ArgumentParser();p.add_argument('identity');args=p.parse_args()
assert args.identity.replace('_','').isalnum()
out=STORE/'Evidence/GermanNPCTriggerPivotV2'/args.identity;r=read(out/'result.json')
assert not r['errors'] and r['status']=='rotated_native_views_require_user_review'
assert r['guards_before']==r['guards_after']==618 and r['all_bones_exact']
assert r['before']['bones']==r['after']['bones'] and r['pivot_residual_cm']<.01
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
records=[]
for name,title,views in (
    ('three_views','德军 NPC · 扳机支点固定 / 枪托向右手旋转',[('after_front','正视'),('after_right','右侧 / 扳机手'),('after_top','俯视')]),
    ('top_comparison','俯视前后对照 · 双手、手臂与手指姿态不变',[('before_top','旋转前'),('after_top','旋转后'),('after_palm_top','右手掌近景')]),
    ('grip_context','支点保持 / 左手未调 / 仅静态候选，未替换正式资产',[('after_trigger','扳机近景'),('after_palm_reverse','右手握持反侧'),('after_context','完整肩肘腕')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),f'原生 UE 贴图 · 单次旋转 {abs(r["actual_rotation_deg"]):.1f}° · 非完整握持验收',font=small,fill=(170,187,203))
    for i,(file,label) in enumerate(views):
        img=Image.open(out/(file+'.png')).convert('RGB');assert img.size==(1600,1000)
        canvas.paste(img.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    target=out/(name+'.png');assert not target.exists();canvas.save(target)
    records.append({'path':target.name,'sha256':sha(target),'size_bytes':target.stat().st_size})
write(out/'presentation.json',{'images':records,'original_pixels_retouched':False,'native_originals':[row(out/c['file']) for c in r['captures']]})
print([e['path'] for e in records])
