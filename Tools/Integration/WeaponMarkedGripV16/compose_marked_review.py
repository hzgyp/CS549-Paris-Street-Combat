"""Label unchanged actual same-camera images, including the marked-pivot result."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponMarkedGripV16'
SOURCE = BASE/'marked_raise_v1'
OUT = BASE/'image_review_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30)
small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
views = ['right','opposite','top','bottom','oblique','left_support','whole_arms']
sheet = Image.new('RGB',(1600,90+len(views)*640),'#202730')
draw = ImageDraw.Draw(sheet)
draw.text((25,10),'左：V14，右：红箭头处固定支点上抬16.16°；手不动，尚有局部相交。',font=font,fill='white')
for row,view in enumerate(views):
    y = 90+row*640
    draw.text((25,y),view+' / 黄拇指，橙食指，蓝左支撑',font=small,fill='white')
    for col,prefix in enumerate(('seated_v14','raised_v16')):
        im = Image.open(SOURCE/(prefix+'_'+view+'.png')).convert('RGB')
        sheet.paste(im.resize((800,600),Image.Resampling.LANCZOS),(col*800,y+35))
sheet.save(OUT/'all_views.jpg',quality=94)
hero = Image.new('RGB',(2400,1990),'#202730')
draw = ImageDraw.Draw(hero)
draw.text((25,10),'左调整前，右按箭头支点上抬；食指接近扳机，原手姿不改。未替换游戏。',font=font,fill='white')
for row,view in enumerate(('right','oblique')):
    y = 80+row*955
    for col,prefix in enumerate(('seated_v14','raised_v16')):
        draw.text((col*1200+25,y),('调整前' if col==0 else '上抬16.16°')+' / '+view,font=small,fill='white')
        hero.paste(Image.open(SOURCE/(prefix+'_'+view+'.png')).convert('RGB'),(col*1200,y+35))
hero.save(OUT/'before_after.jpg',quality=95)
(OUT/'result.json').write_text(json.dumps({'status':'actual_fixed_camera_comparison_composed','views':views},indent=2)+'\n',encoding='utf-8')
print(OUT)
