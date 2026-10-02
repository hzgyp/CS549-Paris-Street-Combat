"""Derived diagnostic sheets; numerical/format checks are not visual acceptance."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1/Evidence/Baseline20261002'
report=json.loads((OUT/'inspect.json').read_text(encoding='utf-8'))
assert len(report['clips'])==15 and len(report['poses'])==465 and not report['errors']
assert all(p['finite'] for p in report['poses'])
clips=[x['package'].split('/')[-1] for x in report['clips']]
for group in range(3):
    sheet=Image.new('RGB',(1800,1800),(35,35,35))
    draw=ImageDraw.Draw(sheet)
    for row,clip in enumerate(clips[group*5:group*5+5]):
        draw.text((8,row*360+3),clip,fill='white')
        for col,(sample,view) in enumerate((s,v) for s in (0,15,30) for v in ('front','side')):
            file=OUT/f'{clip}_{sample:02d}_{view}.png'
            with Image.open(file) as img:
                assert img.format=='PNG' and img.size==(900,1000)
                pic=img.convert('RGB');pic.thumbnail((300,330))
                sheet.paste(pic,(col*300,row*360+26))
            draw.text((col*300+8,row*360+14),f'{sample}/30 {view}',fill='white')
    file=OUT/f'source_motion_sheet_{group+1}.png'
    if file.exists():raise RuntimeError('Preserve prior derived review')
    sheet.save(file)
print('465 finite sampled poses; 90 valid PNG captures; three derived sheets created, review still required')
