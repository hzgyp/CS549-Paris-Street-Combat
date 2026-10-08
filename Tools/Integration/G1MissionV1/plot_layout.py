"""Exact25cm planning figure, rendered with the available NumPy/Pillow runtime."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest
config_file=STORE/'Evidence/G1MissionV1/staging_config_v2_20261008/config.json';config=json.loads(config_file.read_text())
proof_file=STORE/'Evidence/G1MissionV1/travel_v4_20261008/result.json';proof=json.loads(proof_file.read_text())
assert proof['status']=='pass_travel_native_mission' and proof['protected_unchanged']
author=STORE/'Evidence/G1MissionV1/staging_author_v2_20261008/result.json';a=json.loads(author.read_text())
assert a['status'].startswith('pass_') and a['config_sha256']==digest(config_file)
out=STORE/'Evidence/G1MissionV1/staging_layout_v2_20261008';assert not out.exists();out.mkdir()
f=STORE/'Evidence/FineMapGridV1/expanded_v2_20261007';z=np.load(f/'derived/full_filters.npz');s=json.loads((f/'grid_spec.json').read_text())
width=round((s['xmax_cm']-s['xmin_cm'])/25);height=round((s['ymax_cm']-s['ymin_cm'])/25)
mask=np.zeros((height,width),np.uint8);b=z['base']&(z['layer']==0)&~z['quarantine'];mask[z['r'][b],z['c'][b]]=255
canvas=Image.new('RGB',(2250,1350),'#f2f4f7');draw=ImageDraw.Draw(canvas)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def text(xy,label,size=28,color='#26394b',bg=False):
 box=draw.textbbox(xy,label,font=font(size))
 if bg:draw.rectangle((box[0]-5,box[1]-3,box[2]+5,box[3]+3),fill='white')
 draw.text(xy,label,font=font(size),fill=color)
def panel(box,left,top,scale,title):
 x0,x1,y0,y1=box;c0=round((x0-s['xmin_cm'])/25);c1=round((x1-s['xmin_cm'])/25)
 r0=round((s['ymax_cm']-y1)/25);r1=round((s['ymax_cm']-y0)/25)
 w=round((x1-x0)/100*scale);h=round((y1-y0)/100*scale)
 tile=Image.fromarray(mask[r0:r1,c0:c1]).resize((w,h),Image.Resampling.NEAREST).convert('RGB');canvas.paste(tile,(left,top))
 draw.rectangle((left-1,top-1,left+w,top+h),outline='#78889a',width=2);text((left,top-55),title,30)
 def xy(p):return (round(left+(p[0]-x0)/100*scale),round(top+(y1-p[1])/100*scale))
 return {'box':box,'xy':xy,'rect':(left,top,left+w,top+h),'scale':scale}
main=panel((-4500,8500,-27500,-18500),100,235,10,'近岸集结 → C桥 → 攻占G1')
bank=panel((1150,2500,-21500,-20000),1680,235,29,'近岸集结（同比例坐标）')
guard=panel((5500,8000,-21500,-19000),1620,760,18,'远岸任务与三名守卫')
def point(pane,feet,label,color,offset=(15,-40),cross=False):
 x,y=pane['xy'](feet);rect=pane['rect']
 if not rect[0]<=x<=rect[2] or not rect[1]<=y<=rect[3]:return
 if cross:
  draw.line((x-12,y-12,x+12,y+12),fill=color,width=6);draw.line((x-12,y+12,x+12,y-12),fill=color,width=6)
 else:draw.ellipse((x-9,y-9,x+9,y+9),fill=color,outline='white',width=2)
 text((x+offset[0],y+offset[1]),label,25,color,True)
old=json.loads((STORE/'Evidence/G1MissionV1/config_v1_20261008/config.json').read_text())
point(main,old['roster'][0]['feet_cm'],'旧S：出生视图不合格','#b52c39',(20,10),True)
trace=[sample['actors'][0]['location_cm'][:2] for sample in proof['samples']]
for pane in (main,bank,guard):
 pts=[pane['xy'](p) for p in trace if pane['box'][0]<=p[0]<=pane['box'][1] and pane['box'][2]<=p[1]<=pane['box'][3]]
 if len(pts)>1:draw.line(pts,fill='#13bd79',width=5)
for pane in (main,bank):
 for p,label,color,offset in zip(config['roster'][:3],('S 玩家','A1 盟军','A2 盟军'),('#067c57','#006da8','#006da8'),((15,-40),(15,12),(-125,-40))):
  point(pane,p['feet_cm'],label,color,offset)
for pane in (main,guard):
 point(pane,[5837.5,-20237.5],'T1','#a45e00',(-45,-45))
 point(pane,config['roster'][3]['feet_cm'],'G1 / D1','#b52c39',(12,8))
 if pane is guard:
  point(pane,config['roster'][4]['feet_cm'],'D2','#b52c39',(10,-35));point(pane,config['roster'][5]['feet_cm'],'D3','#b52c39',(12,8))
text(main['xy']([3450,-21900]),'C桥：绿色为本次实体轨迹',25,'#067c57',True)
for xm in (-25,0,25,50,75):
 x,y=main['xy']([xm*100,-27500]);draw.line((x,y,x,y+8),fill='#536579',width=2);text((x-20,y+15),str(xm),22)
text((715,1190),'X（米）',25)
for ym in (-275,-250,-225,-200):
 x,y=main['xy']([-4500,ym*100]);text((10,y-15),str(ym),22)
text((15,200),'Y 米',22)
x,y=main['xy']([-3800,-26800]);draw.line((x,y,x+100,y),fill='#27717d',width=6);text((x+15,y-38),'10米',24,'#27717d',True)
text((100,35),'G1 期中 MVP 点位图',56)
text((100,115),'保留原巴黎城市与碰撞；旧集结方案排除，任务止于桥头守卫。',30,'#435166')
text((100,1255),'黑：阻挡／未准入　白：25厘米测量候选格心　绿线：玩家实走；两名盟军已实际过桥。',26,'#435166')
text((100,1300),'白格不自动代表可出生，仍须站立与视图验收。原始黑白测量数据未覆盖。',26,'#435166')
image_file=out/'G1_MVP_LAYOUT_20261008.png';canvas.save(image_file)
record={'config_sha256':digest(config_file),'native_trace_sha256':digest(proof_file),'owned_adoption_sha256':digest(author),
 'image_sha256':digest(image_file),'excluded_staging':old['roster'][:3],'current_roster':config['roster'],
 'pixel_centres_cm':25,'world_axes_units':'metres','raw_grid_unchanged':True,'not_all_white_cells_spawn_eligible':True}
(out/'layout.json').write_text(json.dumps(record,indent=2)+'\n');print(image_file)
