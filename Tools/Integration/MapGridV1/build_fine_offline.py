"""Lazy private tiled selection tool; no server or entire-map raw-data decode."""
import argparse,base64,gzip,json,gc
from collections import defaultdict
from pathlib import Path
import numpy as np
from grid_core import digest,PROFILE
from prepare_links import city
from planning_data import REASONS

def build(entry):
    spec=json.loads((entry/'grid_spec.json').read_text());summary=json.loads((entry/'derived/manifest.json').read_text())
    pool=[];index={};tiles={};images={}
    def intern(text):
        if text not in index:index[text]=len(pool);pool.append(text)
        return index[text]
    for name,folder in (('saved','saved_links'),('full','links')):
        print('Preparing tile data '+name,flush=True)
        with np.load(entry/'derived'/f'{name}_filters.npz') as archive:d={k:archive[k] for k in archive.files}
        records=defaultdict(lambda:{'nodes':[],'raw':[]})
        nodes=json.loads((entry/folder/'nodes.json').read_text())
        for n in nodes:
            i=n['id'];key=f"{name}:{n['r']//128}:{n['c']//128}"
            records[key]['nodes'].append([i,n['c'],n['r'],n['layer'],n['nav_cm'][2],n['feet_cm'][2],int(d['group'][i]),
                                        intern(n['component']),intern(n['mesh']),[intern(p) for p in n['polys']],n['sample_ids'],
                                        int(d['count2'][i]),int(d['count3'][i]),int(d['task'][i]),int(d['base'][i]),int(d['quarantine'][i])])
        del nodes;gc.collect()
        for line in (entry/name/'samples.jsonl').open(encoding='utf-8'):
            r=json.loads(line);reason=r['reason'] if not r['admitted'] else 'city_geometry_clear' if city(r) else 'non_city_or_unclassified_support'
            key=f"{name}:{r['r']//128}:{r['c']//128}"
            records[key]['raw'].append([(r['r']%128)*128+r['c']%128,r['nav_cm'][2],r['feet_cm'][2],intern(REASONS.get(reason,reason)),
                                        intern(r['component']),intern(r['mesh']),[intern(b) for b in r['blockers']],r['id'],intern(r['p'])])
        for key,value in records.items():tiles[key]=base64.b64encode(gzip.compress(json.dumps(value,separators=(',',':'),ensure_ascii=False).encode(),compresslevel=6)).decode()
        del records,d;gc.collect()
    for p in sorted((entry/'derived').glob('*.png')):images[p.stem]=base64.b64encode(p.read_bytes()).decode()
    config={'spec':spec,'profile':PROFILE,'layers':max(s['layers'] for s in summary['scopes'].values()),'identity':entry.name,
            'current_groups':summary['scopes']['saved']['road_groups'],'survey_groups':summary['scopes']['full']['road_groups'],
            'final_layout_selected':False,'encounter_visibility_fine_unmeasured':True}
    bridge=entry.parent.parent/'BridgeConnectivityV1/runtime_reverse_v3_20261007'
    proof=json.loads((bridge/'audit_v1.json').read_text());assert proof['confirmed_two_way_roles']==[0]
    runtime=json.loads((bridge/'result.json').read_text())
    case=next(c for c in runtime['cases'] if c['status']=='passed');member=case['members'][0]
    config['player_bridge_trace']=[member['standing']['feet_cm']]+[x['members'][0]['feet_cm'] for x in case['samples']]+[member['final']['feet_cm']]
    config['player_bridge_trace_source_sha256']=digest(bridge/'audit_v1.json')
    payload={'config':config,'pool':pool,'tiles':tiles,'images':images}
    here=Path(__file__).parent;template=(here/'viewer.html').read_text(encoding='utf-8')
    template=template.replace('每格1米','每格25厘米').replace("view.scale.toFixed(1)+'屏幕像素/米'","(view.scale*4).toFixed(1)+'屏幕像素/米'")
    # Longer exact substitution: the scale suffix continues after the unit.
    template=template.replace("view.scale.toFixed(1)+'屏幕像素/米 ·", "(view.scale*4).toFixed(1)+'屏幕像素/米 ·")
    template=template.replace('完整临时测绘','临时测绘城市包络')
    template=template.replace('<option value="1">当前正式导航</option><option value="0">临时测绘城市包络</option>', '<option value="0">临时测绘城市包络</option><option value="1">当前正式导航</option>')
    template=template.replace(";if(gs.length)$('group').value=String(gs[0].id)",";$('group').value='-1'")
    template=template.replace('<button id="fit">','<label style="flex-direction:row;align-items:center"><input type="checkbox" id="bridgeTrace">已实测C桥玩家路线（绿线）</label><button id="fit">')
    template=template.replace("for(const d of drafts)if", "if($('bridgeTrace').checked&&Number($('layer').value)===0&&$('current').value==='1'){ctx.strokeStyle='#3deb85';ctx.lineWidth=2;ctx.beginPath();config.player_bridge_trace.forEach((p,i)=>{const x=view.x+(p[0]-config.spec.xmin_cm)/25*view.scale,y=view.y+(config.spec.ymax_cm-p[1])/25*view.scale;i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke()}for(const d of drafts)if")
    template=template.replace("$('fit').onclick=", "$('bridgeTrace').onchange=async()=>{if($('bridgeTrace').checked){$('current').value='1';$('layer').value='0';groups();$('group').value='-1';await load();const cs=config.player_bridge_trace.map(p=>(p[0]-config.spec.xmin_cm)/25),rs=config.player_bridge_trace.map(p=>(config.spec.ymax_cm-p[1])/25);fit([Math.min(...cs)-40,Math.min(...rs)-40,Math.max(...cs)+40,Math.max(...rs)+40])}else draw()};$('fit').onclick=")
    template=template.replace('loadSeq=0,drag=null','loadSeq=0,inspectSeq=0,drag=null')
    template=template.replace("const seq=++loadSeq,p=params();", "const seq=++loadSeq,p=params();$('add').disabled=true;if(selected)selected.node=null;")
    template=template.replace('async function inspect(c,r){selected={c,r};','async function inspect(c,r){const seq=++inspectSeq,selection=String(params());selected={c,r};')
    template=template.replace("const d=await getJSON('/api/point?'+p);pointData=d;", "const d=await getJSON('/api/point?'+p);if(seq!==inspectSeq||selection!==String(params()))return;pointData=d;")
    template=template.replace('正式角色抽测：7段通过、1段失败、10段未测；失败格已隔离。白格尚未逐格进行角色行走验证。','本版是25厘米原生静态查询。旧1米失败范围继续隔离；C桥区域玩家两向已验证，A/B桥及正式小队尚未通过。可勾选C桥绿线查看独立实走证据，绿线不涂白细格、不准入其他角色或用途。细格未逐格实走，细格遭遇端点视线尚未复测。')
    template=template.replace("encounter:'两处候选各有至少3个局部站位，可在同一连通组接近；140厘米高度的原生双向视线通过，候选距离5至20米。此项不代表AI或开枪验收。'", "encounter:'25厘米细格端点视线尚未复测，此用途暂全黑。旧1米视线记录保留在旧工具，不能直接继承到新端点。'")
    old="async function getJSON(url){const r=await fetch(url);if(!r.ok)throw Error('数据读取失败 '+r.status);return r.json()}"
    assert template.count(old)==1;template=template.replace(old,'async function getJSON(url){return fineJSON(url)}')
    assert template.count("im.src='/map.png?'+p")==1
    template=template.replace('await new Promise((resolve,reject)=>{im.onload=resolve;im.onerror=reject;im.src=\'/map.png?\'+p})',"await new Promise(async(resolve,reject)=>{im.onload=resolve;im.onerror=reject;try{im.src=await fineMaskURL(p)}catch(e){reject(e)}})")
    adapter=(here/'fine_offline_api.js').read_text(encoding='utf-8')
    assert template.count('<script>')==1
    dataset=json.dumps(payload,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')
    template=template.replace('<script>','<script type="application/json" id="fineDataset">'+dataset+'</script>\n<script>'+adapter+'</script>\n<script>')
    out=entry/'artifact';out.mkdir(exist_ok=True);path=out/'PARIS_FINE_GRID_TOOL_20261007.html';assert not path.exists();path.write_text(template,encoding='utf-8')
    receipt={'file':str(path),'bytes':path.stat().st_size,'sha256':digest(path),'tiles':len(tiles),'png_layers':len(images),
             'no_external_requests':True,'only_selected_tiles_decoded':True,'tile_cache_limit':4,'mask_cache_limit':2,
             'cell_cm':25,'formal_map_or_navigation_saved':False,'manual_browser_tablet_qa':False}
    (out/'offline_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);build(p.parse_args().entry)
