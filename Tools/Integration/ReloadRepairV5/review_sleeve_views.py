"""Compose fixed existing diagnostic views; no source/model editing."""
from PIL import Image,ImageDraw
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadRepairV5/sleeve_weights_validate_v1'
OUT=BASE/'review_sheets_v1';assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
report=json.loads((BASE/'result.json').read_text());assert report['fresh_import_pass'] and not report['errors']
phases=['neutral','reload_0','reload_0.4','reload_1.2','reload_2.2','reload_3.4','reload_3.98','actual_2_20']
for angle in ('front','profile'):
    sheet=Image.new('RGB',(900,8*350),(35,35,35));draw=ImageDraw.Draw(sheet)
    for row,phase in enumerate(phases):
        for col,version in enumerate(('before','after')):
            src=Image.open(BASE/(phase+'_'+angle+'_'+version+'.png')).convert('RGB');src.thumbnail((450,325))
            sheet.paste(src,(col*450,row*350+25));draw.text((col*450+10,row*350+7),phase+' '+version,fill=(240,240,240))
    sheet.save(OUT/(angle+'_all_phases.png'))
sheet=Image.new('RGB',(1800,690),(35,35,35));draw=ImageDraw.Draw(sheet)
for col,version in enumerate(('before','after')):
    sheet.paste(Image.open(BASE/('actual_2_20_profile_'+version+'.png')),(col*900,40))
    draw.text((col*900+20,15),'Native recorded 2.20s - '+version,fill=(240,240,240))
sheet.save(OUT/'actual_2_20_comparison.png')
sheet=Image.new('RGB',(900,1400),(35,35,35));draw=ImageDraw.Draw(sheet)
for row,angle in enumerate(('front','back','profile','three_quarter')):
    for col,version in enumerate(('before','after')):
        src=Image.open(BASE/('neutral_'+angle+'_'+version+'.png')).convert('RGB');src.thumbnail((450,325))
        sheet.paste(src,(col*450,row*350+25));draw.text((col*450+10,row*350+7),'neutral '+angle+' '+version,fill=(240,240,240))
sheet.save(OUT/'neutral_four_views.png')
print(OUT)
