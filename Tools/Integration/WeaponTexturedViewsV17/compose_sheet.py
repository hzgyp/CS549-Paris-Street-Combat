"""Arrange unedited rendered pixels into a Chinese-labeled three-view sheet."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponTexturedViewsV17/presentation_v2'
OUT = SOURCE/'three_views.jpg'
assert not OUT.exists()
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',32)
small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',26)
canvas = Image.new('RGB',(3000,960),(30,33,37))
draw = ImageDraw.Draw(canvas)
rows = [('front_trigger_side.png','正视 · +X'),('side_stock_end.png','侧视 · 枪托端 −Y'),('top.png','俯视 · +Z')]
for i,(file,label) in enumerate(rows):
    image = Image.open(SOURCE/file).convert('RGB')
    image = image.resize((980,840),Image.Resampling.LANCZOS)
    canvas.paste(image,(10+i*1000,60))
    draw.text((28+i*1000,10),label,font=font,fill=(238,240,244))
draw.text((28,917),'原始贴图｜V16枪位与手势未改｜仅静态近景展示，完整手臂另有总览｜未替换游戏版',font=small,fill=(220,224,230))
canvas.save(OUT,quality=95,subsampling=0)
print(OUT)
