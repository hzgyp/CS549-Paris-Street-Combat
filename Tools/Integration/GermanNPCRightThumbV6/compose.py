"""Label the retained failed diagnostic; never present it as a usable asset."""
import sys,ast
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards
BASE=STORE/'Evidence/GermanNPCRightThumbV6';OUT=BASE/'failure_views_v2'
r=read(OUT/'result.json');assert not r['errors'] and r['diagnostic_failed_pose_only']
assert guards()==r['guards_after']==618 and len(r['images'])==8
for e in r['images']+r['inputs']:assert sha(ROOT/e['path'])==e['sha256']
for p in Path(__file__).parent.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
canvas=Image.new('RGB',(2400,1880),(30,35,42));d=ImageDraw.Draw(canvas)
d.text((24,15),'右拇指局部适配对照 · 未通过 / 未采用',font=font,fill=(255,178,102))
d.text((24,55),'橙色＝右拇指，蓝色＝保留的食指；灰模诊断，不是游戏贴图 / 枪、左手和食指不动',font=font,fill=(225,234,241))
for col,(prefix,label) in enumerate([('before','修改前'),('after_failed','仅抬拇指根部 · 失败对照')]):
    d.text((col*1200+24,100),label,font=font,fill='white')
    for rownum,view in enumerate(['reverse','top']):
        im=Image.open(OUT/(prefix+'_'+view+'.png'));assert im.size==(1200,850)
        canvas.paste(im,(col*1200,150+rownum*850))
dest=OUT/'thumb_comparison.png';assert not dest.exists();canvas.save(dest)
write(OUT/'presentation.json',{'status':'failed_pose_labeled_for_user_marking','images':[row(dest)],
    'native_tested':False,'full_grasp_accepted':False,'formal_selected':False,'guards':618,
    'sources_exact':True,'source_model_weights_actions_modified':False})
print(dest)
