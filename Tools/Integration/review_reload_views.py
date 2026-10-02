"""Assemble fixed-view QA sheets from preserved UE captures, no source edits."""
import json
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--version',choices=('Views_v1','Views_v2'),default='Views_v2');args=parser.parse_args()
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P4/SimplifiedReload20261002'/args.version
report=json.loads((OUT/'pose_views.json').read_text())
assert report['status']=='complete_static_pose_views_pending_visual_review'
assert len(report['captures'])==20 and len(report['joints'])==150
for name in ('BP_PCPlayerReloadV1','BP_PCNPCReloadV1'):
    dest=OUT/(name+'_sheet.png')
    assert not dest.exists(), 'Preserve sheets'
    sheet=Image.new('RGB',(2000,1060),(24,24,28));draw=ImageDraw.Draw(sheet)
    for index,e in enumerate([e for e in report['captures'] if e['class']==name]):
        with Image.open(OUT/e['file']) as source:
            assert source.size==(800,1000)
            thumb=source.convert('RGB').resize((400,500))
        # Stored order is frame-front, frame-side; front row / side row.
        x=(index//2)*400;y=(index%2)*530
        sheet.paste(thumb,(x,y+30))
        draw.text((x+8,y+8),f"{e['view']}  {e['time_s']:.3f}s",fill='white')
    sheet.save(dest)
    print(dest)
