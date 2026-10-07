"""Layout native pixels for human markup; never retouch meshes or images."""
import argparse
from PIL import Image, ImageDraw, ImageFont
from common import BASE, write, read, sha

parser = argparse.ArgumentParser()
parser.add_argument('identity')
args = parser.parse_args()
assert args.identity.replace('_', '').isalnum()
out = BASE / args.identity
result = read(out / 'result.json')
assert not result['errors']
font_path = 'C:/Windows/Fonts/msyh.ttc'
font = ImageFont.truetype(font_path, 30)
small = ImageFont.truetype(font_path, 23)
records = []
for faction, title in [('allied','盟军 NPC · M1 Garand'),('german','德军 NPC · 现有德军步枪候选')]:
    # PNG sources remain intact; contact sheets use lossless same-scale tiles.
    for sheet, views in [('three_views', [('front','正视 / 人物前方'),('right','右侧 / 扳机手'),('top','俯视 / 上方')]),
                         ('details', [('right_grip','右手握持近景'),('left_support','左手扶枪近景'),('context','完整肩肘腕关系')])]:
        canvas = Image.new('RGB',(2400,660),(29,34,41))
        d = ImageDraw.Draw(canvas)
        d.text((20,12),title,fill=(235,240,247),font=font)
        note = '当前待机原姿态，未做修复' if faction == 'allied' else '临时内存装备：未保存正式地图，未做修复'
        d.text((20,53),note,fill=(170,187,203),font=small)
        for i,(view,label) in enumerate(views):
            image = Image.open(out/f'{faction}_{view}.png').convert('RGB')
            assert image.size == (1600,1000)
            image = image.resize((800,500),Image.Resampling.LANCZOS)
            canvas.paste(image,(i*800,125))
            d.text((i*800+20,92),f'{i+1}  {label}',fill=(235,240,247),font=small)
        path = out/f'{faction}_{sheet}.png'
        assert not path.exists(), 'Preserve existing presentation'
        canvas.save(path)
        records.append({'path':path.name,'sha256':sha(path),'size_bytes':path.stat().st_size})
write(out/'presentation.json',{'images':records,'original_pixels_retouched':False,
    'native_source':'original UE scene captures; only layout and labels added'})
print('\n'.join(x['path'] for x in records))
