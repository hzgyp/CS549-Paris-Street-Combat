"""Label original native wrist/whole-body comparisons without retouch."""
import argparse
from PIL import Image,ImageDraw,ImageFont
from common import *
parser=argparse.ArgumentParser();parser.add_argument('identity');args=parser.parse_args()
out=BASE/args.identity;n=read(out/'result.json');assert not n['errors']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
records=[]
for name,title,views in (
    ('comparison','盟军 NPC · 参考已验收第一人称的右前臂—手掌关系',
     [('before_right','之前：右腕折角较大'),('after_right','当前：右肘弯曲方向调整'),('after_reverse','当前：反侧')]),
    ('three_views','原贴图三视图 · 枪 / 双手 / 手指位置全部保留',
     [('after_front','正视'),('after_right','右侧'),('after_top','俯视')]),
    ('wrist_details','右腕与肘部局部对照 · 未移动手掌 / 未修改手指',
     [('before_wrist','之前：前臂与手掌'),('after_wrist','当前：前臂与手掌'),('after_elbow','当前：右肘')]),
    ('body_shoulder','完整人物和肩部 · 原骨骼长度 / 原衣袖权重',
     [('after_body_right','全身侧视'),('after_body_front','全身正视'),('after_shoulder','肩部与枪托')])):
    canvas=Image.new('RGB',(2400,660),(29,34,41));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title,font=font,fill=(235,240,247))
    draw.text((20,53),'静态比较版本 · 不是完整握持 / 动作验收 · 未替换正式 NPC',font=small,fill=(222,173,125))
    for i,(view,label) in enumerate(views):
        im=Image.open(out/(view+'.png')).convert('RGB');assert im.size==(1600,1000)
        canvas.paste(im.resize((800,500),Image.Resampling.LANCZOS),(i*800,125))
        draw.text((i*800+20,92),str(i+1)+'  '+label,font=small,fill=(235,240,247))
    p=out/(name+'.png');assert not p.exists();canvas.save(p)
    records.append({'path':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size})
write(out/'presentation.json',{'images':records,'retouched':False,'comparison_only':True,'contact_accepted':False})
print(records)
