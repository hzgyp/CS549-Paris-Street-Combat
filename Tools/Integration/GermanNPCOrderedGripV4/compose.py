"""Present actual native pixels and preserve diagnostic/acceptance distinctions."""
import sys,argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import *
p=argparse.ArgumentParser();p.add_argument('identity');args=p.parse_args()
out=STORE/'Evidence/GermanNPCOrderedGripV4'/args.identity
r=read(out/'result.json');assert not r['errors'] and r['guards_after']==618 and guards()==618
assert r['status']=='german_ordered_static_views_require_user_review' and r['inputs_unchanged']
for path,h in r['input_hashes'].items():assert sha(ROOT/path)==h
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
records=[]
for name,title,views in (
    ('steps','德军握枪 · 右握点校准 → 整体下压与左臂支撑', [('before_right','之前 5° / 78cm视野'),('first_right','枪单独再转 5° / 78cm视野'),('after_right','下压12°＋双臂联动 / 100cm视野')]),
    ('three_views','当前候选 · 原贴图三视图 / 尚未替换正式资产',[('after_front','正视'),('after_right','右侧'),('after_top','俯视')]),
    ('contacts','双手接触细节 · 保留未通过的穿模记录',[('after_trigger','扳机 / 右手'),('after_palm','右掌与枪托 / 俯视'),('after_support','左掌与前护木')]),
    ('context','整体姿态与背侧 · 原模型 / 原骨长 / 无新动作',[('after_reverse','反侧'),('after_context','肩肘腕整体'),('after_body','全身')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));d=ImageDraw.Draw(canvas)
    d.text((20,12),title,font=font,fill=(235,240,247))
    d.text((20,52),'原生 UE 静态展示 · 局部/完整动作未验收 · 相机宽度不同处已标注',font=small,fill=(170,187,203))
    for i,(file,label) in enumerate(views):
        image=Image.open(out/(file+'.png')).convert('RGB');assert image.size==(1600,1000)
        canvas.paste(image.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        d.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    dest=out/(name+'.png');assert not dest.exists();canvas.save(dest);records.append(row(dest))
write(out/'presentation.json',{'images':records,'native_originals':[row(out/c['file']) for c in r['captures']],
    'original_pixels_retouched':False,'guards':618,'motion_or_full_contact_accepted':False})
print([e['path'] for e in records])
