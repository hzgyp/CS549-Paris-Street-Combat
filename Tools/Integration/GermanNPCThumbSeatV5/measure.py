"""Cached geometry inspection only; no source/fitting mutations."""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT, STORE, GLB, read, write, row, guards, tm

BASE=STORE/'Evidence/GermanNPCThumbSeatV5'
OUT=BASE/'measure_v1'; assert not OUT.exists(); OUT.mkdir(parents=True)
PREV=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/result.json'
DATA=PREV.parent/'geometry.npz'
old=read(PREV); assert not old['errors'] and guards()==618
for e in old['inputs']: assert row(ROOT/e['path'])['sha256']==e['sha256']
d=np.load(DATA); skin=d['skin']; names=old['bone_names']; w=d['weights']
g=old['after_gun_world']; gp=d['gun_local_cm']
world=np.array([tm.point(g,p.tolist()) for p in gp])
hand=np.array(old['after_bones']['hand_r']['t'])
idx=[j for j,n in enumerate(names) if n.startswith('thumb_') and n.endswith('_r')]
mask=w[:,idx].sum(1)>0
dominant=w[:,idx].sum(1)>.5
records={'guards':618,'inputs':[row(p) for p in (PREV,DATA,GLB,Path(__file__))],
    'bones':{n:old['after_bones'][n] for n in names if n.startswith(('thumb_', 'index_')) and n.endswith('_r')},
    'thumb_any_vertices':int(mask.sum()),'thumb_dominant_vertices':int(dominant.sum()),
    'thumb_dominant_bounds_cm':[skin[dominant].min(0).tolist(),skin[dominant].max(0).tolist()],
    'pivot_gun_cm':old['trigger_pivot_gun_cm'],'stock_marker_gun_cm':old['stock_pivot_gun_cm'],
    'source_modified':False}
canvas=Image.new('RGB',(2400,850),(32,37,45)); draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for panel,(coords,title) in enumerate(zip([(0,1),(0,2),(1,2)],['World XY / top','World XZ / side','World YZ / end'])):
    a,b=coords; p=world-hand; s=skin-hand
    region=np.linalg.norm(p,axis=1)<22
    def dots(points,color):
        for point in points:
            x=panel*800+400+point[a]*24;y=440-point[b]*24
            if panel*800<x<(panel+1)*800 and 70<y<800:
                draw.ellipse((x-1,y-1,x+1,y+1),fill=color)
    dots(p[region],'#a68352')
    for digit,col in [('index','#4c9dec'),('middle','#aaa'),('ring','#ccc'),('pinky','#ddd')]:
        ids=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_r')]
        m=w[:,ids].sum(1)>0
        dots(s[m],col)
    dots(s[mask],'#f06f55')
    pivot=np.array(tm.point(g,old['trigger_pivot_gun_cm']))-hand
    x=panel*800+400+pivot[a]*24;y=440-pivot[b]*24
    draw.line((x-8,y-8,x+8,y+8),fill='white',width=2);draw.line((x-8,y+8,x+8,y-8),fill='white',width=2)
    draw.text((panel*800+20,20),title,font=font,fill='white')
    draw.text((panel*800+20,800),'Orange thumb / blue index / tan rifle / white trigger',font=font,fill='white')
canvas.save(OUT/'landmarks.png')
write(OUT/'result.json',records)
print(json.dumps(records,indent=2))
