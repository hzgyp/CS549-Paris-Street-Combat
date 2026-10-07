"""Label matched renders in a contact sheet; no retouch or material/asset writes."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

p = argparse.ArgumentParser()
p.add_argument('--input', required=True)
p.add_argument('--out', required=True)
p.add_argument('--german-variant', default='german_v11')
p.add_argument('--german-title', default='German V11 - current exported candidate')
p.add_argument('--filename', default='m1_vs_v11.png')
a = p.parse_args()
source = Path(a.input).resolve()
out = Path(a.out).resolve()
assert not out.exists(), 'Preserve earlier presentation identity'
out.mkdir(parents=True)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 24)
small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
width, height = 900, 525
canvas = Image.new('RGB', (width * 2, (height + 35) * 3 + 70), '#24282c')
draw = ImageDraw.Draw(canvas)
draw.text((25, 16), 'Allied M1 - existing portable material', font=font, fill='white')
assert a.german_variant.startswith('german_') and a.german_variant.replace('_','').isalnum()
assert Path(a.filename).name == a.filename and a.filename.endswith('.png')
draw.text((width + 25, 16), a.german_title, font=font, fill='white')
paths = []
for row, (view, label) in enumerate([('whole', 'Whole rifle / same scale'), ('receiver', 'Receiver / steel and wood'), ('stock', 'Stock / wood surface')]):
    y = 70 + row * (height + 35)
    for col, variant in enumerate(['allied_m1', a.german_variant]):
        path = source / (variant + '_' + view + '.png')
        im = Image.open(path).convert('RGB')
        assert im.size == (1200, 700)
        im = im.resize((width, height), Image.Resampling.LANCZOS)
        draw.text((col * width + 20, y), label, font=small, fill='#d5dde5')
        canvas.paste(im, (col * width, y + 35))
        paths.append({'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
target = out / a.filename
canvas.save(target)
(out / 'presentation.json').write_text(json.dumps({'source_renders': paths,
    'operations': 'uniform downscale + labels only; no crop/retouch',
    'image': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}, indent=2), encoding='utf-8')
print(str(target))
