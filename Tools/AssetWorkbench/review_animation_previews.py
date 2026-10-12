"""Audit real browser captures and create private QA sheets, without editing previews."""
import json,sys
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
folder=ROOT/'Assets/LocalWorking/AssetWorkbench/runs'/sys.argv[1]
rows=[]
for path in sorted(folder.glob('anim-*.png')):
 with Image.open(path) as im:
  rgb=im.convert('RGB').crop((2,2,im.width-2,im.height-2))
  diff=ImageChops.difference(rgb,Image.new('RGB',rgb.size,rgb.getpixel((0,0))))
  mask=diff.convert('L').point(lambda x:255 if x>18 else 0)
  fraction=mask.histogram()[255]/(mask.width*mask.height)
  box=mask.getbbox()
  rows.append({'id':path.stem,'visible_fraction':fraction,'bounds':box,'size':rgb.size})
for page,start in enumerate(range(0,len(rows),20)):
 sheet=Image.new('RGB',(1400,1000),'#eceee8');draw=ImageDraw.Draw(sheet)
 for i,row in enumerate(rows[start:start+20]):
  x=i%4*350;y=i//4*200
  with Image.open(folder/(row['id']+'.png')) as im:
   im.thumbnail((340,165));sheet.paste(im,(x+(350-im.width)//2,y+5))
  draw.text((x+5,y+180),row['id'].replace('anim-','')[:48],fill='black')
 sheet.save(folder/f'webgl-review-{page:02d}.png')
bad=[r for r in rows if not .0002<r['visible_fraction']<.95]
clipped=[r for r in rows if r['bounds'] and (r['bounds'][0]==0 or r['bounds'][1]==0 or r['bounds'][2]==r['size'][0] or r['bounds'][3]==r['size'][1])]
(folder/'pixel-review.json').write_text(json.dumps({'count':len(rows),'blank_or_full':bad,'edge_contacts':clipped,'images':rows},indent=2))
print(json.dumps({'count':len(rows),'blank_or_full':bad,'edge_contacts':clipped}))
assert len(rows)==125 and not bad and not clipped
