"""Small-angle correction evidence; rejected V2 remains explicitly labeled."""
import sys,argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import *
p=argparse.ArgumentParser();p.add_argument('identity');args=p.parse_args()
assert args.identity.replace('_','').isalnum()
out=STORE/'Evidence/GermanNPCSmallPivotV3'/args.identity;r=read(out/'result.json')
proof=read(out.parent/'marked_rotation_v1/result.json')
assert not r['errors'] and r['status']=='rotated_native_views_require_user_review'
assert r['guards_before']==r['guards_after']==618 and r['all_bones_exact']
assert r['before']['bones']==r['after']['bones'] and r['pivot_residual_cm']<.01
assert abs(r['actual_rotation_deg']-5)<.01 and guards()==618
for e in (proof['v1_result'],proof['v1_landmarks'],proof['model'],proof['renderer_template'],proof['v2_rejected_result'],proof['v2_marking_proof']):
    assert sha(ROOT/e['path'])==e['sha256']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
old=STORE/'Evidence/GermanNPCTriggerPivotV2/native_rotation_v1/after_top.png'
records=[]
for name,title,views in (
    ('angle_comparison','角度纠正 · 大角度版拒绝 / 当前只从平移版转 5°',[(out/'before_top.png','平移后 / 本轮旋转前'),(old,'上一轮 37.6° · 已拒绝 / 旧截图'),(out/'after_top.png','本轮 5° · 双手不动')]),
    ('three_views','德军 NPC · 单次小角度 / 扳机支点固定',[(out/'after_front.png','正视'),(out/'after_right.png','右侧'),(out/'after_top.png','俯视')]),
    ('trigger_context','保持支点与双手 · 左手未调 / 尚非完整握持',[(out/'after_trigger.png','扳机近景'),(out/'after_reverse.png','反侧'),(out/'after_context.png','完整肩肘腕')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),'原生 UE 贴图 · 未保存地图 / 未替换正式资产',font=small,fill=(170,187,203))
    for i,(file,label) in enumerate(views):
        img=Image.open(file).convert('RGB');assert img.size==(1600,1000)
        canvas.paste(img.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    dest=out/(name+'.png');assert not dest.exists();canvas.save(dest)
    records.append({'path':dest.name,'sha256':sha(dest),'size_bytes':dest.stat().st_size})
write(out/'presentation.json',{'images':records,'original_pixels_retouched':False,
    'native_originals':[row(out/c['file']) for c in r['captures']],'rejected_v2_original':row(old),
    'retained_inputs_exact':True,'guards':618})
print([e['path'] for e in records])
