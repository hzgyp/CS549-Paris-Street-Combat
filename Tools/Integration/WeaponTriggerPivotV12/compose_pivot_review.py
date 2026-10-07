"""Label actual fixed-camera V12 renders; no repainting or defect concealment."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponTriggerPivotV12'
SOURCE = BASE / 'pivot_10deg_v1'
OUT = BASE / 'image_review_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 30)
small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 24)
views = ['right', 'opposite', 'top', 'bottom', 'oblique', 'whole_rifle', 'left_support', 'whole_oblique', 'whole_reverse']
sheet = Image.new('RGB', (1600, 80 + len(views) * 640), '#202730')
draw = ImageDraw.Draw(sheet)
draw.text((25, 12), '左：原版  |  右：右手不动，枪绕扳机转10°，左臂跟随（未选入游戏）', font=font, fill='white')
for row, view in enumerate(views):
    y = 80 + row * 640
    draw.text((25, y), view + ' / 同机位', font=small, fill='white')
    for col, prefix in enumerate(('before', 'pivot_10deg')):
        im = Image.open(SOURCE / (prefix + '_' + view + '.png')).convert('RGB')
        sheet.paste(im.resize((800, 600), Image.Resampling.LANCZOS), (col * 800, y + 35))
sheet.save(OUT / 'all_views.jpg', quality=94)
hero = Image.new('RGB', (2400, 1990), '#202730')
draw = ImageDraw.Draw(hero)
draw.text((25, 10), '扳机支点试验：右手／指节不动，枪旋转10°，左臂随枪。诊断对比，未替换正式版。', font=font, fill='white')
for row, view in enumerate(('oblique', 'bottom')):
    y = 80 + row * 955
    for col, prefix in enumerate(('before', 'pivot_10deg')):
        draw.text((col * 1200 + 25, y), ('原版' if col == 0 else '枪旋转10°') + ' / ' + view, font=small, fill='white')
        hero.paste(Image.open(SOURCE / (prefix + '_' + view + '.png')).convert('RGB'), (col * 1200, y + 35))
hero.save(OUT / 'before_after.jpg', quality=95)
(OUT / 'result.json').write_text(json.dumps({'status': 'composed_from_actual_fixed_views',
                                            'views': views, 'native_authored': False}, indent=2) + '\n')
print(str(OUT))
