"""Measured layer atlas and finite native convergence results, private outputs only."""
import argparse,json,sys
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest
SOURCE=STORE/'Evidence/FineMapGridV1/expanded_v2_20261007'
BANK=STORE/'Evidence/NativeConvergenceV1/bank_v1_20261007/bank.json'
FONT='C:/Windows/Fonts/msyh.ttc'

def font(n):return ImageFont.truetype(FONT,n)
def layers(out):
    out.mkdir(parents=True,exist_ok=True)
    f=np.load(SOURCE/'derived/full_filters.npz');c=f['c'];r=f['r'];l=f['layer'];b=f['base'];q=f['quarantine']
    crop=(int(c.min())-8,int(r.min())-8,int(c.max())+9,int(r.max())+9)
    crop=(max(0,crop[0]),max(0,crop[1]),min(4032,crop[2]),min(4032,crop[3]))
    im=Image.new('RGB',(1480,1860),'#eeeeee');d=ImageDraw.Draw(im)
    d.text((30,20),'巴黎地图：已测叠置表面 ≠ 已验证楼层通行',font=font(35),fill='black')
    d.text((30,70),'25厘米原比例格网；每一行共用同一世界范围。左：几何净空；右：道路连接准入。',font=font(21),fill='black')
    d.text((30,108),'序号是同一XY处按Z排序的局部表面，不能直接称为1楼／2楼。原黑白图保持不变。',font=font(21),fill='black')
    counts=[]
    for layer in range(int(l.max())+1):
        geom=(l==layer)&~q;road=(l==layer)&b
        for col,mask in enumerate((geom,road)):
            x=30+col*730;y=160+layer*330
            label='已测几何净空' if col==0 else '道路准入白格'
            d.text((x,y),f'叠置序号 {layer} · {label}：{int(mask.sum()):,}',font=font(22),fill='black')
            a=np.zeros((4032,4032),dtype=np.uint8);a[r[mask],c[mask]]=255
            tile=Image.fromarray(a).crop(crop);tile.thumbnail((690,270),Image.Resampling.NEAREST)
            canvas=Image.new('RGB',(690,270),'black');canvas.paste(tile,((690-tile.width)//2,(270-tile.height)//2));im.paste(canvas,(x,y+36))
        counts.append({'surface_order':layer,'geometric_clearance_nodes':int(geom.sum()),'road_admitted_white_nodes':int(road.sum())})
    d.text((30,1820),'高层几何虽有记录，但当前无道路连接白格；楼梯／坡道／桥上桥下的角色通行尚不能据此宣称完成。',font=font(19),fill='black')
    target=out/'PARIS_SURFACE_LAYERS_20261007.png';im.save(target)
    (out/'layer_atlas.json').write_text(json.dumps({'source':str(SOURCE),'counts':counts,'crop':crop,'semantic_floor_map':False,'layer_connectivity_verified':False,'sha256':digest(target)},indent=2)+'\n')
    print(json.dumps({'figure':str(target),'counts':counts}))

def results(out,entries):
    assert not out.exists(),'Preserve earlier artifact';out.mkdir(parents=True)
    bank=json.loads(BANK.read_text());reports=[json.loads((e/'result.json').read_text()) for e in entries]
    cases=[s for report in reports for s in report['cases']];byid={s['id']:s for s in cases};assert len(byid)==len(cases)
    f=np.load(SOURCE/'derived/full_filters.npz');base=f['base'];ly=f['layer'];cc=f['c'];rr=f['r']
    crops=[s['node'] for s in bank['origins']];c0=max(0,min(s['c'] for s in crops)-170);c1=min(4032,max(s['c'] for s in crops)+171)
    r0=max(0,min(s['r'] for s in crops)-170);r1=min(4032,max(s['r'] for s in crops)+171);crop=(c0,r0,c1,r1)
    im=Image.new('RGB',(1580,1170),'#eeeeee');d=ImageDraw.Draw(im)
    d.text((32,20),'正式NPC向中央点汇聚：均匀样本实走结果',font=font(36),fill='black')
    d.text((32,73),'保留原25厘米黑白图；50米分区各取一个白格。原生A*，原速300厘米/秒，地形阶段排除人物互堵。',font=font(20),fill='black')
    summary={}
    for column,role in enumerate(('allied','german')):
        rows=[s for s in cases if s['role']==role];neg=[s for s in rows if s['status']=='negative'];passed=[s for s in rows if s['status']=='passed']
        summary[role]={'passed':len(passed),'negative':len(neg),'unmeasured':69-len(rows),'reasons':dict(Counter(s['reason'] for s in neg))}
        for layer in range(int(ly.max())+1):
            a=np.zeros((4032,4032),dtype=np.uint8);use=base&(ly==layer);a[rr[use],cc[use]]=255
            for s in neg:
                if s['layer']==layer:a[s['r'],s['c']]=0
            target=out/f'{role}_hub_relative_L{layer}.png';Image.fromarray(a).convert('1').save(target)
            original=Image.open(SOURCE/'derived'/f'full_walk_L{layer}.png').convert('L')
            delta=np.argwhere(np.asarray(original)!=a)
            expected={(s['r'],s['c']) for s in neg if s['layer']==layer}
            assert {tuple(p) for p in delta.tolist()}==expected
        x=32+column*775;y=128
        title='盟军' if role=='allied' else '德军';d.text((x,y),f'{title}：到达 {len(passed)} / 负面 {len(neg)} / 未测 {69-len(rows)}',font=font(25),fill='black')
        tile=Image.open(out/f'{role}_hub_relative_L0.png').convert('RGB').crop(crop)
        scale=min(735/tile.width,795/tile.height);size=(int(tile.width*scale),int(tile.height*scale));tile=tile.resize(size,Image.Resampling.NEAREST)
        d2=ImageDraw.Draw(tile)
        def xy(c,r):return ((c-c0+.5)*scale,(r-r0+.5)*scale)
        for j,s in enumerate(bank['origins']):
            p=xy(s['node']['c'],s['node']['r']);rec=byid.get(f'origin_{j:03d}_{role}')
            color='#43cf7c' if rec and rec['status']=='passed' else '#ff634c' if rec else '#ffcb50'
            d2.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill=color,outline='black')
        hx,hy=xy(bank['hub']['c'],bank['hub']['r']);d2.line((hx-12,hy,hx+12,hy),fill='#47b9ff',width=4);d2.line((hx,hy-12,hx,hy+12),fill='#47b9ff',width=4)
        im.paste(tile,(x,y+48));d.rectangle((x,y+48,x+size[0],y+48+size[1]),outline='#777777')
    d.text((32,1010),'绿点：正式角色实走到达  ·  红点：起点／路径／运动／终点负面  ·  黄点：未测  ·  蓝十字：临时汇聚点',font=font(22),fill='black')
    d.text((32,1051),'白格仍是几何候选，只有绿点有本次实走证据；红点对应的25厘米起始格在派生图变黑，不涂黑整个50米区域。',font=font(20),fill='black')
    d.text((32,1090),'当前保存导航与扩展白图范围不同。负面表示当前角色到不了这个点，原因分别保留；不代表该位置永久不可用。',font=font(20),fill='black')
    d.text((32,1129),'此图不选择最终出生／任务／遭遇位置，也不建立多人汇聚、楼层切换或整片地图验收。',font=font(20),fill='black')
    figure=out/'PARIS_NATIVE_CONVERGENCE_20261007.png';im.save(figure)
    manifest={'status':'finite_convergence_derivatives','bank_sha256':digest(BANK),'role_counts':summary,'entries':[str(e) for e in entries],
              'black_scope':'exact rejected initial cell, role/current saved navigation/current hub only','unmeasured_geometry_white_retained':True,
              'original_map_overwritten':False,'final_layout_selected':False,'figure_sha256':digest(figure),
              'masks':{p.name:digest(p) for p in out.glob('*_hub_relative_*.png')}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['layers','results']);p.add_argument('out',type=Path);p.add_argument('entries',nargs='*',type=Path);a=p.parse_args()
    if a.mode=='layers':layers(a.out)
    else:results(a.out,a.entries)
