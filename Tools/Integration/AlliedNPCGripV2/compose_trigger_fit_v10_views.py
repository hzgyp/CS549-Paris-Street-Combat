"""Label actual V10 UE originals equally; no material retouching."""
import argparse
from PIL import Image,ImageDraw,ImageFont
from common import *
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');t=read(BASE/'trigger_pad_v10d/result.json')
assert not n['errors'] and n['status']=='trigger_fit_v10_native_views_require_user_review'
assert t['contact_gate_passed'] and guards()==611
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
records=[]
for name,title,views in (
    ('three_views','盟军 NPC · 右手和手指不变 · 枪位校准，左臂联动',
     [('after_front','正视'),('after_right','右侧 / 扳机手'),('after_top','俯视')]),
    ('trigger_details','食指/扳机局部 · 指腹距离 1mm · 食指交叉面 0',
     [('after_trigger','右侧'),('after_reverse_trigger','反侧'),('after_under_trigger','底部')]),
    ('comparison','之前 V9 → 当前 V10 · 原生 UE 贴图静止对照',
     [('before_right','之前：V9'),('after_right','当前：V10'),('after_trigger','当前：扳机局部')]),
    ('arm_context','原右手保持 · 左臂原骨段长度联动 · 静态检查，不是动作验收',
     [('before_context','之前：全臂'),('after_context','当前：全臂'),('after_reverse','当前：背侧')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),'局部食指几何检查通过 · 其他握持仍有残留 · 未替换正式资产',font=small,fill=(170,187,203))
    for i,(view,label) in enumerate(views):
        im=Image.open(out/(view+'.png')).convert('RGB');assert im.size==(1600,1000)
        canvas.paste(im.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    path=out/(name+'.png');assert not path.exists();canvas.save(path)
    records.append({'path':path.name,'sha256':sha(path),'size_bytes':path.stat().st_size})
write(out/'presentation.json',{'images':records,'retouched':False,'diagnostic_not_gameplay':True})
print(records)
