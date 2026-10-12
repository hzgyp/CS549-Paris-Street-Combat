"""Read actual UE captures and make private QA contact sheets; never edits covers."""
import json,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageStat
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Assets/LocalWorking/AssetWorkbench/native-covers-v1';QA=OUT/'review';QA.mkdir(exist_ok=True)
rows=[];failures=[]
for p in sorted(OUT.glob('anim-*/prepare.json')):
 job=json.loads(p.read_text());folder=p.parent/('capture-v9' if job['id'] in ('anim-frank-rpg-archer-combo-set','anim-t-pose-zombie-2','anim-ghostsamurai-bundle') else 'capture-v8');result=folder/'result.json'
 if not result.exists():failures.append({'id':job['id'],'reason':'capture pending'});continue
 d=json.loads(result.read_text())
 if d['status']!='captured_pending_visual_review':failures.append({'id':job['id'],'reason':d['status'],'errors':d['errors']});continue
 for capture in d['captures']:
  img=folder/capture['file'];raw=img.read_bytes();assert hashlib.sha256(raw).hexdigest()==capture['sha256']
  with Image.open(img) as im:
   rgb=im.convert('RGB');assert im.size==(800,600)
   stat=ImageStat.Stat(rgb);background=rgb.getpixel((0,0));nonblack=sum(max(abs(px[i]-background[i]) for i in range(3))>25 for px in rgb.resize((160,120)).getdata())/(160*120)
   capture['pixel_check']={'stddev':stat.stddev,'visible_fraction':nonblack}
   assert max(stat.stddev)>5 and .003<nonblack<.98,(job['id'],'blank or full-frame capture',nonblack)
   capture['needs_close_review']=nonblack<.025
 rows.append({'id':job['id'],'title':job['title'],'source_sha256':job['source_sha256'],'folder':str(folder.relative_to(ROOT)),**d})
for page,start in enumerate(range(0,len(rows),20)):
 sheet=Image.new('RGB',(1200,1000),'#eceee8');draw=ImageDraw.Draw(sheet)
 for index,row in enumerate(rows[start:start+20]):
  x=(index%4)*300;y=(index//4)*200
  for ci,capture in enumerate(row['captures']):
   with Image.open(ROOT/row['folder']/capture['file']) as im:sheet.paste(im.convert('RGB').resize((140,105)),(x+10+ci*140,y+30))
  draw.text((x+6,y+179),row['id'].replace('anim-','')[:43],fill='black')
 sheet.save(QA/f'sheet-{page:02d}.png')
(QA/'report.json').write_text(json.dumps({'captured':rows,'pending_or_failed':failures},indent=2))
print(json.dumps({'captured':len(rows),'pending_or_failed':len(failures),'sheets':math.ceil(len(rows)/20)}))
