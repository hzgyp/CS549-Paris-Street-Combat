"""Labeled fixed-phase sheets; do not edit source assets or overwrite evidence."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--identity', default='compare_v4')
args = parser.parse_args()
assert args.identity.replace('_', '').isalnum()
out = ROOT/'Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload'/args.identity
report = json.loads((out/'result.json').read_text(encoding='utf-8'))
assert report['status'] == 'captured_source_comparison_pending_image_review'
assert len(report['clips']) == 3 and len(report['images']) == 42 and len(report['samples']) == 21
for clip in report['clips']:
    dest = out/(clip['label']+'_review_sheet_v2.png')
    assert not dest.exists(), 'Preserve existing evidence'
    sheet = Image.new('RGB', (2016, 960), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 8), clip['label']+' | '+clip['clip'].split('/')[-1]+' | source / target diagnostic, no weapon contact test', fill='white')
    for i, entry in enumerate(x for x in report['images'] if x['label'] == clip['label']):
        source_path = out/entry['file']
        with Image.open(source_path) as source:
            assert source.size == (720, 800)
            thumb = source.convert('RGB').resize((288, 320))
        x = (i//2)*288
        y = 45+(i%2)*450
        view_name = '-Y rear' if entry['view'] == 'front' else '+X side'
        draw.text((x+8, y), f"{view_name}  {entry['fraction']*100:.1f}%  {entry['time_s']:.3f}s", fill='white')
        sheet.paste(thumb, (x, y+28))
    sheet.save(dest)
    print(str(dest))
