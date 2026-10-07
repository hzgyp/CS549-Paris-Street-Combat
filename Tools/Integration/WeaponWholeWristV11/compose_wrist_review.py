"""Fixed-camera contact sheets from actual before/after diagnostic renders."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponWholeWristV11/small_approach_v1'
OUT = SOURCE.parent / 'image_review_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 32)
small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 24)
views = ['right', 'opposite', 'top', 'bottom', 'oblique', 'whole_oblique', 'whole_reverse']
sheet = Image.new('RGB', (1600, len(views) * 640 + 80), '#202730')
draw = ImageDraw.Draw(sheet)
draw.text((25, 15), '左：原握姿  |  右：整手靠近7.5毫米（指节角度、枪位不变）', font=font, fill='white')
for row, view in enumerate(views):
    y = 80 + row * 640
    draw.text((25, y), view + '  /  固定同机位', font=small, fill='white')
    for col, prefix in enumerate(('before', 'whole_wrist_7p5mm')):
        im = Image.open(SOURCE / (prefix + '_' + view + '.png')).convert('RGB')
        sheet.paste(im.resize((800, 600), Image.Resampling.LANCZOS), (col * 800, y + 35))
sheet.save(OUT / 'all_views.jpg', quality=94)
hero = Image.new('RGB', (2400, 1990), '#202730')
draw = ImageDraw.Draw(hero)
draw.text((25, 10), '整手位置试验：左为原版，右为靠近7.5毫米。未改指节／枪位，仍有穿模，未选入游戏。', font=font, fill='white')
for row, view in enumerate(('oblique', 'bottom')):
    y = 80 + row * 955
    for col, prefix in enumerate(('before', 'whole_wrist_7p5mm')):
        draw.text((col * 1200 + 25, y), ('原握姿' if col == 0 else '整手靠近7.5毫米') + ' / ' + view, font=small, fill='white')
        hero.paste(Image.open(SOURCE / (prefix + '_' + view + '.png')).convert('RGB'), (col * 1200, y + 35))
hero.save(OUT / 'before_after.jpg', quality=95)
(OUT / 'result.json').write_text(json.dumps({'status': 'composed_from_fixed_actual_views', 'views': views,
                                            'candidate_authored': False, 'native_authored': False}, indent=2) + '\n')
print(str(OUT))
