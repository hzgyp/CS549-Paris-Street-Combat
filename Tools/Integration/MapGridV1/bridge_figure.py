"""Private measured diagnostic: binary grid background with labeled bridge evidence."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

def build(root,runtime,bank):
    r=json.loads((runtime/'result.json').read_text());a=json.loads((runtime/'audit_v1.json').read_text());discovery=json.loads((runtime.parent/'bank_v1_20261007/discovery.json').read_text())
    e=root/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence';grid=e/'MapGridV1/full_v1_20261007'
    bitmap=Image.open(grid/'artifact_v3/current_walk_surface_0.png').convert('RGB');spec=json.loads((grid/'grid_spec.json').read_text())
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18);title=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30)
    out=Image.new('RGB',(1600,1300),'white');draw=ImageDraw.Draw(out)
    confirmed=bool(a['confirmed_two_way_roles']);draw.text((30,20),'巴黎两岸与桥梁专项核对',font=title,fill='black')
    draw.text((30,68),'底图：既有正式导航1米黑白图；蓝框：原桥包围盒；绿线：实际角色移动（不涂白水面）',font=small,fill='black')
    summary='下方C桥区域：原玩家两方向走通（独立入口）' if confirmed else 'C桥实际移动尚未双向通过'
    draw.text((30,100),summary+'；A/B尚未确认可通行，不能据黑图断言所有两岸不通。',font=small,fill='black')
    full_bounds=[220,220,800,830]
    items=[('整体位置',None)]+[(b['id']+'桥',b) for b in discovery['bridges']]
    for i,(label,b) in enumerate(items):
        x=30+(i%2)*790;y=155+(i//2)*530;draw.text((x,y),label,font=font,fill='black')
        if b:
            bx,by,_=b['origin_cm'];c=(bx-spec['xmin_cm'])/100;row=(spec['ymax_cm']-by)/100;bounds=[int(c)-35,int(row)-35,int(c)+35,int(row)+35]
            state=b['scopes']['current'];text='实际往返已确认' if b['id']=='C' and confirmed else '本次未确认通行'
            draw.text((x+110,y+3),text,font=small,fill='black')
        else:bounds=full_bounds
        crop=bitmap.crop(tuple(bounds));scale=min(710/crop.width,430/crop.height);w,h=int(crop.width*scale),int(crop.height*scale)
        left=x+(730-w)//2;top=y+44;out.paste(crop.resize((w,h),Image.Resampling.NEAREST),(left,top))
        def xy(p):return (left+((p[0]-spec['xmin_cm'])/100-bounds[0])*scale,top+((spec['ymax_cm']-p[1])/100-bounds[1])*scale)
        for bridge in discovery['bridges'] if b is None else [b]:
            ox,oy,_=bridge['origin_cm'];ex,ey,_=bridge['extent_cm'];p1=xy([ox-ex,oy+ey]);p2=xy([ox+ex,oy-ey]);draw.rectangle((*p1,*p2),outline='#5b9aff',width=3)
            mid=xy([ox,oy]);draw.text((mid[0]+7,mid[1]-18),bridge['id'],font=font,fill='#5b9aff',stroke_width=1,stroke_fill='black')
        if b is None or b['id']=='C':
            for case in r['cases']:
                if case['status']!='passed':continue
                m=case['members'][0];points=[m['standing']['feet_cm']]+[s['members'][0]['feet_cm'] for s in case['samples']]+[m['final']['feet_cm']]
                draw.line([xy(p) for p in points],fill='#3deb85',width=3)
        if b:
            count=b['scopes']['current']['clear_deck_nodes'];draw.text((x,y+483),f'桥面净空格心 {count}；旧网格道路连接 0。',font=small,fill='black')
    draw.text((30,1220),'角色往返结论来自原生站立、实际桥区域原始支撑、匹配SUCCESS与终点检查；不是只看路径线。',font=small,fill='black')
    draw.text((30,1254),'全部坐标为临时测试。原始网格未重写，其他桥与桥面任意位置未获验收。',font=small,fill='black')
    target=runtime/'PARIS_BRIDGES_REVIEW_20261007.png';assert not target.exists();out.save(target);print(str(target))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runtime',type=Path);p.add_argument('bank',type=Path);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3]);a=p.parse_args();build(a.root,a.runtime,a.bank)
