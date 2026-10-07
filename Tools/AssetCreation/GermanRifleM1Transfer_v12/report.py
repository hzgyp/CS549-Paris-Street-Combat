"""Build labeled evidence and non-release hash inventory; no asset retouch."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-m1-texture-v12'
OUT = BASE/'presentation_v1'
assert not OUT.exists(), 'Preserve occupied output identities'
OUT.mkdir(parents=True)
old = ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-weather-v11/audit_v1'
new = BASE/'audit_v1'
canvas = Image.new('RGB', (1800, 1232), '#24282c')
draw = ImageDraw.Draw(canvas)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 25)
draw.text((20,15), 'Before: V11 procedural finish', fill='white', font=font)
draw.text((920,15), 'After: V12 existing M1 texture transfer', fill='white', font=font)
inputs = []
for row, view in enumerate(['quarter','receiver']):
    y = 70+row*581
    for col, source in enumerate([old,new]):
        path = source/('fresh_pbr_'+view+'.png')
        im = Image.open(path).convert('RGB')
        assert im.size == (1400,850), im.size
        draw.text((col*900+20,y), view, fill='#d5dde5', font=font)
        canvas.paste(im.resize((900,546),Image.Resampling.LANCZOS), (col*900,y+35))
        inputs.append({'path':path.relative_to(ROOT).as_posix(),
                       'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
canvas.save(OUT/'v11_vs_v12.png')
(OUT/'presentation.json').write_text(json.dumps({'inputs':inputs,
    'operations':'uniform resize and labels only; same fixed camera/light/AgX; no crop or retouch'},indent=2))

def row(path):
    return {'path':path.relative_to(ROOT).as_posix(),'size':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

audit = json.loads((new/'audit.json').read_text())
repeat = json.loads((BASE/'repeat_audit_v1/audit.json').read_text())
build = json.loads((BASE/'finish_v1/build_report.json').read_text())
assert audit['passed'] and repeat['passed'] and build['geometry_exact']
assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
           for path,digest in build['baseline_files'].items())
files = [row(p) for p in sorted(BASE.rglob('*')) if p.is_file()]
sources = [row(p) for p in sorted(Path(__file__).parent.glob('*.py'))]
sources += [row(ROOT/'Tools/AssetCreation/GermanRifleSPR_v10/main.py'),
            row(ROOT/'Tools/AssetCreation/GermanRifleSPR_v10/audit.py'),
            row(ROOT/'Tools/AssetCreation/GermanRifleSPR_v11/main.py')]
inventory = {'schema':'private-modeling-draft-v1','date':'2026-10-04',
    'purpose':'V12 M1 surface-transfer evidence only; NOT CATALOG/release/restore authority',
    'user_visual_approval':False,'shared':False,'historical_approval':False,'runtime_approval':False,
    'files':files,'sources':sources,'protected_files_rechecked':build['baseline_files'],
    'metrics':{k:audit[k] for k in ['triangles','dimensions_m','embedded_images']},
    'rerun_images_equal':repeat['cross_export_images_identical'],
    'rerun_whole_glb_equal':repeat['cross_export_byte_identical']}
manifest = ROOT/'Assets/Integration/GERMAN_RIFLE_M1_TEXTURE_V12_INVENTORY_20261004.json'
assert not manifest.exists(), 'Preserve prior inventory'
manifest.write_text(json.dumps(inventory,indent=2),encoding='utf-8')
print(json.dumps({'files':len(files),'sources':len(sources),
    'glb':row(BASE/'finish_v1/GermanRifle_M1Texture_V12.glb'),
    'blend':row(BASE/'finish_v1/GermanRifle_M1Texture_V12.blend'),
    'max_normal_deg':max(r['normal_max_degrees'] for r in audit['comparison']),
    'baseline_max_normal_deg':max(r['normal_max_degrees'] for r in audit['baseline_geometry_comparison']),
    'rerun_glb_equal':inventory['rerun_whole_glb_equal']}))
