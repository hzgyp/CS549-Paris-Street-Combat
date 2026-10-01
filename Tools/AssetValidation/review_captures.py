"""Diagnostic contact sheets. Original engine captures remain unchanged."""
from pathlib import Path
import os
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('CS549_CAPTURE_DIR', ROOT / 'Assets/LocalWorking/Validation/UE582/2026-09-30-v1/Evidence'))


def sheet(paths, name, columns=4):
    if not paths:
        return
    cell_w, cell_h = 270, 330
    output = Image.new('RGB', (columns * cell_w, ((len(paths) + columns - 1) // columns) * cell_h), '#333333')
    draw = ImageDraw.Draw(output)
    for index, path in enumerate(paths):
        im = Image.open(path).convert('RGB')
        im.thumbnail((cell_w, cell_h - 30))
        x, y = (index % columns) * cell_w, (index // columns) * cell_h
        output.paste(im, (x + (cell_w - im.width) // 2, y + 30))
        draw.text((x + 4, y + 5), path.stem, fill='white')
    output.save(OUT / name)


sheet([OUT / f'{label}_{view}.png' for label in ('german_A', 'german_B', 'allied_A', 'allied_B')
       for view in ('front', 'back', 'side', 'three_quarter') if (OUT / f'{label}_{view}.png').exists()], 'material_contact_sheet.jpg')
for label in ('german_A', 'german_B', 'allied_A', 'allied_B'):
    paths = [OUT / f'{label}_{action}_{index:02}_{view}.png'
             for action, index in [('idle', 2), ('walk', 6), ('walk', 18), ('run', 6), ('run', 18),
                                   ('reload', 1), ('reload', 3), ('hit', 2), ('death', 2), ('death', 4)]
             for view in ('front', 'side') if (OUT / f'{label}_{action}_{index:02}_{view}.png').exists()]
    sheet(paths, label + '_pose_contact_sheet.jpg')
if os.environ.get('CS549_CAPTURE_DIR'):
    for label in ('german_A', 'german_B', 'allied_A', 'allied_B'):
        paths = [OUT / f'{label}_{action}_{index:02}_{view}.png'
                 for action, index in [('idle', 0), ('walk', 0), ('walk', 12), ('run', 12),
                                       ('reload', 0), ('hit', 0), ('death', 0)]
                 for view in ('front', 'side') if (OUT / f'{label}_{action}_{index:02}_{view}.png').exists()]
        sheet(paths, label + '_repair_pose_sheet.jpg')
print('Capture contact sheets generated')
