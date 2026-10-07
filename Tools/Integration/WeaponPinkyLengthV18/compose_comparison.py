"""Unretouched two-view before/after sheet for the local length correction."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponPinkyLengthV18/distal_v1'
OUT=SOURCE/'before_after.jpg'
assert not OUT.exists()
canvas=Image.new('RGB',(2400,1810),(30,33,37))
draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25)
draw.text((24,12),'调整前 · 原D059小拇指',font=font,fill=(239,241,245))
draw.text((1224,12),'调整后 · 指根不动，后两节缩短10%',font=font,fill=(239,241,245))
for j,view in enumerate(['front_trigger_side','top']):
    for i,condition in enumerate(['before','shorter']):
        image=Image.open(SOURCE/(condition+'_'+view+'.png')).convert('RGB')
        image=image.resize((1180,1011),Image.Resampling.LANCZOS)
        # Same fixed crop on both sides; no texture/contact retouching.
        image=image.crop((0,160,1180,995))
        canvas.paste(image,(10+i*1200,60+j*855))
draw.text((24,1773),'左前右后｜食指、枪位、UV与权重不动｜原肩/拇指/护圈问题仍未关闭｜未替换游戏',font=small,fill=(222,226,232))
canvas.save(OUT,quality=95,subsampling=0)
print(OUT)
