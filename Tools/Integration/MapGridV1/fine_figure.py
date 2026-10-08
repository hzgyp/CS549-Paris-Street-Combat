"""Equal-world-scale comparison of measured 1 m and 25 cm masks, plus C bridge trace."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from grid_core import digest

def build(entry):
    evidence=entry.parent.parent;old=evidence/'MapGridV1/full_v1_20261007';s=json.loads((entry/'grid_spec.json').read_text())
    coarse=Image.open(old/'artifact_v3/survey_walk_surface_0.png').convert('RGB')
    fine=Image.open(entry/'derived/full_walk_L0.png').convert('RGB')
    runtime=json.loads((evidence/'BridgeConnectivityV1/runtime_reverse_v3_20261007/result.json').read_text())
    summary=json.loads((entry/'derived/manifest.json').read_text());same=summary['scopes']['full']['C_fine_graph_same_group']
    out=Image.new('RGB',(1600,1370),'white');d=ImageDraw.Draw(out)
    title=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    d.text((30,20),'巴黎地图细化：1米 → 25厘米',font=title,fill='black')
    d.text((30,66),'相同世界范围 · 原生重新测地面／胶囊／四向连接 · 人物宽度仍68厘米 · 黑：阻挡或未准入',font=small,fill='black')
    d.text((30,98),'4032×4032格；每像素25厘米；密度提高16倍。比较临时扩展测绘的最低城市表面，未保存正式导航。',font=small,fill='black')
    for j,(label,image,cell) in enumerate((('原版：每格1米',coarse,100),('新版：每格25厘米',fine,25))):
        for i,box in enumerate(([-24000,-29000,15000,24000],[900,-23500,6900,-17500])):
            left=30+j*790;top=160+i*550;d.text((left,top),label+(' · 城市概览' if i==0 else ' · C桥区域'),font=font,fill='black')
            c0=(box[0]-s['xmin_cm'])/cell;r0=(s['ymax_cm']-box[3])/cell;c1=(box[2]-s['xmin_cm'])/cell;r1=(s['ymax_cm']-box[1])/cell
            crop=image.crop((round(c0),round(r0),round(c1),round(r1)));scale=min(730/crop.width,470/crop.height);w,h=round(crop.width*scale),round(crop.height*scale)
            x=left+(730-w)//2;y=top+43;out.paste(crop.resize((w,h),Image.Resampling.NEAREST),(x,y))
            def xy(p):return (x+((p[0]-s['xmin_cm'])/cell-c0)*scale,y+((s['ymax_cm']-p[1])/cell-r0)*scale)
            if i==1:
                for case in runtime['cases']:
                    if case['status']!='passed':continue
                    m=case['members'][0];ps=[m['standing']['feet_cm']]+[a['members'][0]['feet_cm'] for a in case['samples']]+[m['final']['feet_cm']]
                    d.line([xy(p) for p in ps],fill='#3deb85',width=3)
                d.text((left,top+521),'绿线：此前已验证的真实玩家路径，未把黑格涂白。',font=small,fill='black')
    d.text((30,1270),'C桥两岸局部：扩展测绘细格'+('同组；当前保存导航筛选仍分组。' if same else '仍未合为同组；实际角色双向走通证据独立保留。'),font=font,fill='black')
    d.text((30,1314),'A/B桥、小队通行、细格遭遇视线仍未验收。旧1米失败范围继续隔离，所有位置均为测试／草案。',font=small,fill='black')
    path=entry/'artifact/PARIS_FINE_GRID_COMPARISON_20261007.png';assert not path.exists();out.save(path)
    (entry/'artifact/figure_receipt.json').write_text(json.dumps({'path':str(path),'sha256':digest(path),'equal_world_scale':True,'coarse_cell_cm':100,'fine_cell_cm':25,'scope':'full_disposable_survey','C_full_fine_same_group':same,'C_saved_fine_same_group':summary['scopes']['saved']['C_fine_graph_same_group']},indent=2)+'\n');print(path)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);build(p.parse_args().entry)
