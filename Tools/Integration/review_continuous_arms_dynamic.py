"""Summarize a closed motion run and make diagnostic sheets/pose-series GIF; no asset edits."""
import argparse
import json
import math
from pathlib import Path
from PIL import Image,ImageDraw

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('identity')
parser.add_argument('--partial',action='store_true',help='Review completed images only in an explicitly failed run')
args = parser.parse_args()
assert args.identity.replace('_','').isalnum()
out = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3'/args.identity
data = json.loads((out/'result.json').read_text())
assert data.get('status') and (not data['errors'] or args.partial) and data['protected_42_unchanged']
assert not (out/'summary.json').exists(), 'Preserve review identity'
summary = {'scope':'Numerical/PNG completeness check, not visual or human acceptance',
           'whole_run_pass':not data['errors'],'partial_review':args.partial,
           'capture_count':len(data['captures']), 'frame_count':len(data['frames']), 'checks':data['checks'],
           'max_finger_local_delta':max(f['finger_local_delta'] for f in data['frames']),
           'max_alive_right_anchor_cm':max(f['right_anchor_cm'] for f in data['frames'] if f['state']['IsDead'] == 'False'),
           'max_speed_cm_s':max(math.sqrt(sum(v*v for v in f['velocity_cm_s'])) for f in data['frames']),
           'reload_frames':sum(f['state']['ActionState'] == 'Reloading' for f in data['frames']),
           'moving_reload_frames':sum(f['state']['ActionState'] == 'Reloading' and math.sqrt(sum(v*v for v in f['velocity_cm_s'])) > 100 for f in data['frames']),
           'captures':[]}
tiles = []
walk = []
for capture in data['captures']:
    p = out/capture['file']
    with Image.open(p) as im:
        assert im.format == 'PNG' and im.size == (1014,550)
        summary['captures'].append({'phase':capture['phase'],'size':list(im.size),'action':capture['state']['ActionState'],
                                    'speed_cm_s':math.sqrt(sum(v*v for v in capture['velocity_cm_s']))})
        tile = Image.new('RGB',(360,226),'#18212b')
        resized = im.convert('RGB').resize((360,195))
        tile.paste(resized,(0,31))
        ImageDraw.Draw(tile).text((6,7),capture['phase'],fill='white')
        tiles.append(tile)
        if capture['phase'].startswith('walk_cycle_'):
            frame = im.convert('RGB').copy()
            ImageDraw.Draw(frame).text((10,10),'Sampled walk pose series, not real-time recording',fill='white',stroke_width=1,stroke_fill='black')
            walk.append(frame)
sheet = Image.new('RGB',(360*4,226*math.ceil(len(tiles)/4)),'#18212b')
for i,t in enumerate(tiles):
    sheet.paste(t,((i%4)*360,(i//4)*226))
sheet.save(out/'phase_sheet.png')
if walk:
    walk[0].save(out/'sampled_walk.gif',save_all=True,append_images=walk[1:],duration=120,loop=0)
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k != 'captures'},indent=2))
