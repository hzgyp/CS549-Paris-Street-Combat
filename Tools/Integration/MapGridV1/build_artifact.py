"""Emit private black/white rasters and summary; no final gameplay layout."""
import argparse
import json
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont

from grid_core import digest
from planning_data import PlanningData


def build(entry):
    data=PlanningData(entry);dest=entry/'artifact_v3';dest.mkdir()
    manifest={'spec':data.spec,'sources':{},'filters':{},'formal_groups':data.groups(True),
              'survey_groups':data.groups(False),'layers':max(n['layer'] for n in data.nodes)+1,
              'white_meaning':'Measured cell-center geometry and native reciprocal connection candidates; not full gameplay acceptance',
              'final_layout_selected':False}
    for rel in ['result.json','saved/samples.jsonl','full/samples.jsonl','saved_links/samples.jsonl','links/samples.jsonl','sight/samples.jsonl','derived_v3/nodes.json','derived_v3/associations.json','runtime_admission.json']:
        manifest['sources'][rel]=digest(entry/rel)
    for current in (True,False):
        for layer in range(manifest['layers']):
            for mode in ('walk','spawn','task','encounter'):
                bitmap,meta,_=data.mask(mode,current,layer=layer)
                name=f'{"current" if current else "survey"}_{mode}_surface_{layer}'
                Image.fromarray(bitmap).convert('1').save(dest/(name+'.png'))
                manifest['filters'][name]={**meta,'png_sha256':digest(dest/(name+'.png'))}
    # Clear labeled overview of four measured candidate filters, keeping map pixels binary.
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    title=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',32)
    canvas=Image.new('RGB',(1600,1190),'white');draw=ImageDraw.Draw(canvas)
    draw.text((35,22),'巴黎地图黑白网格  每格1米  点选后导出真实XYZ',font=title,fill='black')
    draw.text((35,73),'黑：阻挡或未准入   白：格心满足当前筛选   同XY不同表面另存   当前显示正式导航范围',font=small,fill='black')
    walk,_,_=data.mask('walk',True,layer=0)
    ys,xs=walk.nonzero()
    bounds=[max(0,int(xs.min())-8),max(0,int(ys.min())-8),min(data.spec['columns'],int(xs.max())+9),min(data.spec['rows'],int(ys.max())+9)] if len(xs) else [0,0,data.spec['columns'],data.spec['rows']]
    labels={'walk':'通行候选  道路连接','spawn':'生成候选  至少3个独立站位','task':'任务候选  四向1米操作空间','encounter':'遭遇候选  接近空间与双向视线'}
    for i,mode in enumerate(labels):
        bitmap,meta,_=data.mask(mode,True,layer=0)
        x=35+(i%2)*780;y=125+(i//2)*475
        draw.text((x,y),labels[mode]+f"  {meta['white_cells']:,}白格",font=font,fill='black')
        im=Image.fromarray(bitmap).crop(tuple(bounds))
        factor=min(720/im.width,390/im.height)
        im=im.resize((int(im.width*factor),int(im.height*factor)),Image.Resampling.NEAREST).convert('RGB')
        draw.rectangle((x,y+43,x+730,y+443),fill='black')
        canvas.paste(im,(x+(730-im.width)//2,y+48+(390-im.height)//2))
    draw.text((35,1100),'用途白格表示几何候选；具体小队、任务交互与战斗仍按选定位置验证。视图裁切不是最终任务边界。',font=small,fill='black')
    draw.text((35,1134),'点击工具可查看黑格原因、各叠置表面、原生高度与正式导航证据；所有标记只导出为草案。',font=small,fill='black')
    canvas.save(dest/'PARIS_BLACK_WHITE_GRID_20261007.png')
    manifest['overview_sha256']=digest(dest/'PARIS_BLACK_WHITE_GRID_20261007.png')
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'layers':manifest['layers'],'formal_groups':len(manifest['formal_groups']),'survey_groups':len(manifest['survey_groups']),
                      'current_default':{k:v['white_cells'] for k,v in manifest['filters'].items() if k.startswith('current') and k.endswith('_0')}},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);build(p.parse_args().entry)
