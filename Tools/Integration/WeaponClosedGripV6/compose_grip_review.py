"""Derived QA sheets/comparison from frozen diagnostic PNGs; no asset image edits."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];E=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponClosedGripV6';OUT=E/'image_review_v8';assert not OUT.exists();OUT.mkdir(parents=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for folder in ('envelope_fit_v7','chain_seat_v8b'):
    data=json.loads((E/folder/'result.json').read_text());files=[x['file'] for x in data['views']];w,h=360,315;sheet=Image.new('RGB',(w*6,h*((len(files)+5)//6)),(32,32,32));draw=ImageDraw.Draw(sheet)
    for i,name in enumerate(files):
        im=Image.open(E/folder/name).convert('RGB');im.thumbnail((360,288));x=(i%6)*w;y=(i//6)*h;sheet.paste(im,(x,y));draw.text((x+4,y+291),name.replace('_',' ')[:42],font=font,fill='white')
    sheet.save(OUT/(folder+'_sheet.jpg'),quality=92)
comparison=Image.new('RGB',(2000,840),(32,32,32));draw=ImageDraw.Draw(comparison)
for i,(folder,name,label) in enumerate([('envelope_fit_v7','0.0_envelope_v7_plain_oblique.png','V7: before chain seating'),('chain_seat_v8b','0.0_v8_chain_seated_plain_oblique.png','V8: pinky closer; ring gap remains')]):
    comparison.paste(Image.open(E/folder/name).convert('RGB'),(i*1000,40));draw.text((i*1000+12,10),label,font=font,fill='white')
comparison.save(OUT/'before_after.png');print(str(OUT))
