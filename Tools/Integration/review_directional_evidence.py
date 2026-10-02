"""QA derived sheets/range summaries from immutable per-case diagnostic evidence."""
import hashlib
import json
import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2/Movement'
parser=argparse.ArgumentParser()
parser.add_argument('--version',choices=('v5','v6'),default='v5')
args=parser.parse_args()
version=args.version
DEST=OUT/('directional_'+version+'_review.json')
if DEST.exists():
    raise RuntimeError('Refusing existing review')
variants=('Allied_A','Allied_B','German_A','German_B')
reports=[json.loads((OUT/('movement_probe_%s_%s_%d.json'%(version,v,f))).read_text(encoding='utf-8')) for v in variants for f in (30,60,120)]
assert all(r.get('result')=='pass_numeric_directional_only' and len(r['cases'])==1 for r in reports)
review={'cases':[],'images':[],'scope':'Derived QA; numeric tests do not pass contact/stride. Image generation is not visual acceptance.'}
for r in reports:
    c=r['cases'][0]
    review['cases'].append({'variant':c['variant'],'fps':c['fps'],'criteria':c['criteria'],
        'pose_samples':sum(len(p['pose_samples']) for p in c['phases']),
        'phases':[{k:p[k] for k in ('phase','contact_range_cm','lower_foot_low_vertical_motion_drift_cm_s')} for p in c['phases']]})
phases=('settle','walk_forward','walk_right','walk_backward','walk_left','walk_diagonal','run_left','run_backward')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for view in ('front','side'):
    sheet=Image.new('RGB',(8*280,4*310),'#eeeeee')
    draw=ImageDraw.Draw(sheet)
    for row,v in enumerate(variants):
        c=next(r['cases'][0] for r in reports if r['cases'][0]['variant']==v and r['cases'][0]['fps']==60)
        for col,phase in enumerate(phases):
            capture=next(x for x in c['captures'] if x['file'].endswith('_'+phase+'_'+view+'.png'))
            p=Path(capture['directory'])/capture['file']
            assert p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
            with Image.open(p) as im:
                assert im.size==(1000,1000)
                sheet.paste(im.convert('RGB').resize((270,270)),(col*280+5,row*310+35))
            draw.text((col*280+5,row*310+5),v+' / '+phase,fill='black',font=font)
            review['images'].append({'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    sheet.save(OUT/('directional_'+version+'_'+view+'_sheet.jpg'),quality=92)
review['numeric_cases_passed']=len(reports)
review['pose_samples']=sum(c['pose_samples'] for c in review['cases'])
DEST.write_text(json.dumps(review,indent=2),encoding='utf-8')
print('Reviewed headers/sizes for',len(review['images']),'selected PNGs;',review['pose_samples'],'pose samples; visual review pending')
