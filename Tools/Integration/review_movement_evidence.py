"""Inventory local draft bytes and assemble a QA contact sheet, without UE edits."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/P2/Movement'
probe = json.loads((OUT / 'movement_probe_v3.json').read_text(encoding='utf-8'))
author = json.loads((OUT / 'authoring.json').read_text(encoding='utf-8'))
cases = [c for c in probe['cases'] if c['fps'] == 60]
assert len(cases) == 4 and sum(len(c['captures']) for c in cases) == 24
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
sheet = Image.new('RGB', (6 * 340, 4 * 380), '#eeeeee')
draw = ImageDraw.Draw(sheet)
images = []
for row, case in enumerate(cases):
    for col, capture in enumerate(case['captures']):
        path = OUT / 'Captures_v3' / capture['file']
        data = path.read_bytes()
        assert data.startswith(b'\x89PNG\r\n\x1a\n'), 'Capture is not a PNG: ' + path.name
        with Image.open(path) as im:
            assert im.size == (1000, 1000)
            sheet.paste(im.convert('RGB').resize((330, 330)), (col * 340 + 5, row * 380 + 40))
        label = case['variant'] + ' / ' + capture['file'].split('_v1_')[1].removesuffix('.png')
        draw.text((col * 340 + 5, row * 380 + 5), label, fill='black', font=font)
        images.append({'file': path.relative_to(STORE).as_posix(), 'bytes': len(data),
                       'sha256': hashlib.sha256(data).hexdigest()})
sheet.save(OUT / 'movement_v3_contact_sheet.jpg', quality=92)
drafts = []
for package in author['bridge']['assets'] + [author['map']]:
    suffix = '.umap' if package == author['map'] else '.uasset'
    relative = 'Content/' + package.removeprefix('/Game/') + suffix
    path = STORE / relative
    data = path.read_bytes()
    drafts.append({'package': package, 'local_path': relative, 'bytes': len(data),
                   'sha256': hashlib.sha256(data).hexdigest(), 'owner': 'yg745',
                   'status': 'local_unpublished_draft', 'immutable_sftp_object': None})
report = {'schema_version': 1, 'status': 'draft_inventory_not_release_manifest',
          'source_revision': '37de53688530d379d73115a22604bd7ee02c03c9',
          'drafts': drafts, 'captures': images, 'visual_review': 'pending_human_or_agent_inspection',
          'limitations': 'Phase-end renders, controlled lights; not a full gait, city, weapon or packaging pass'}
(OUT / 'draft_inventory.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('Inventoried', len(drafts), 'draft packages and', len(images), 'valid PNG captures; contact sheet ready')
