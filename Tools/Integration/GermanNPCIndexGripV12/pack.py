"""Label/combine existing original views for review; no image retouch."""
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha
BASE=STORE/'Evidence/GermanNPCIndexGripV12';VIEWS=BASE/'final_views_v1'
OUT=BASE/'review_sheets_v1';assert not OUT.exists();OUT.mkdir(parents=True)
record=read(VIEWS/'result.json');assert not record['errors'] and len(record['images'])==12
for e in record['images']:assert sha(ROOT/e['path'])==e['sha256']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
outputs=[]
for name,views in [('three_views',[('right','侧面'),('reverse','反侧'),('top','俯视')]),('arm_context',[('support','左手支撑'),('context','完整手臂')]),('under_detail',[('under','下方；部分接触被手和枪遮挡')])]:
    sheet=Image.new('RGB',(1600,110+len(views)*600),(28,32,38));draw=ImageDraw.Draw(sheet)
    draw.text((20,10),'德军食指 V12：局部改善，扳机重叠仍在；未正式采用',font=font,fill='white')
    draw.text((20,47),'蓝色：食指；橙色：已认可拇指；金色：已认可三指。灰模仅作接触检查。',font=small,fill=(215,220,226))
    for j,(view,label) in enumerate(views):
        y=110+j*600
        for col,stage in enumerate(('before','after')):
            draw.text((col*800+12,y),('原版 / ' if stage=='before' else '局部试验 / ')+label,font=font,fill='white')
            im=Image.open(VIEWS/(stage+'_'+view+'.png')).convert('RGB');im.thumbnail((800,566))
            sheet.paste(im,(col*800,y+34))
    dest=OUT/(name+'.jpg');sheet.save(dest,quality=93);outputs.append(row(dest))
write(OUT/'result.json',{'status':'labeled_partial_comparison_not_contact_acceptance','images':outputs,'inputs':record['images']+[row(VIEWS/'result.json'),row(Path(__file__))],'formal_selected':False})
print(outputs)
