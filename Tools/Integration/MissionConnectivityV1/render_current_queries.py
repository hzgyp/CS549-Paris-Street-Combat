"""Render current query coverage, all-pairs matrix and stacked-surface example."""
import argparse
import hashlib
import json
import subprocess
from collections import defaultdict
from html import escape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/"Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity',required=True)
    args=parser.parse_args()
    assert args.identity.replace('_','').isalnum()
    source=STORE/'Evidence/MissionConnectivityV1/current_query_v1_20261007/query.json'
    data=json.loads(source.read_text())
    assert not data['errors'] and data['protected_bytes_unchanged']
    out=STORE/'Evidence/MissionConnectivityV1'/args.identity
    svg=ROOT/'Docs/Development/MissionLoopV1/Visuals'/(args.identity+'.svg')
    assert not out.exists() and not svg.exists(),'Preserve prior output'
    elements=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="850" viewBox="0 0 1280 850" role="img" aria-labelledby="title desc">',
              '<title id="title">Current Paris navigation query connectivity</title>',
              '<desc id="desc">All thirty directed six-actor queries complete. 449 of 1854 sampled nodes have complete outward and return paths. Stacked surfaces retain separate height and connectivity. Query evidence, not physical walking or confirmed floors.</desc>',
              '<rect width="1280" height="850" fill="#fff"/>']
    def text(x,y,value,size=17,color='#22323e',anchor='start'):
        elements.append(f'<text x="{x}" y="{y}" font-family="Microsoft YaHei, sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>')
    def line(x1,y1,x2,y2,color='#d9e0e5',width=1,dash=''):
        elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')
    def dot(x,y,r,color,stroke='none'):
        elements.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{color}" stroke="{stroke}"/>')
    origin=data['actors'][0]['projected_cm'];scale=560/440
    def xy(point):return 70+((point[0]-origin[0])/100+220)*scale,742-((point[1]-origin[1])/100+200)*scale
    text(640,35,'当前地图：先验证连通，再选择任务地点',27,anchor='middle')
    text(640,66,'2026-10-07 · 地图 9ff18c13… · 保留 XYZ，不能直接压平上下表面',17,anchor='middle')
    text(350,105,'导航点采样与往返连接',22,anchor='middle')
    text(350,135,'绿色：449 个往返完整 · 灰色：1,405 个未与起点互通',16,anchor='middle')
    text(350,163,'橙圈：43 处同 XY 高差 ≥ 1.93 m 的上下样本',16,anchor='middle')
    for value in (-200,-100,0,100,200):
        gx=70+(value+220)*scale;gy=742-(value+200)*scale
        line(gx,182,gx,742);line(70,gy,630,gy)
        text(gx,764,str(value),14,anchor='middle');text(58,gy+5,str(value),14,anchor='end')
    elements.append('<rect x="70" y="182" width="560" height="560" fill="none" stroke="#71838f"/>')
    for state,color in ((False,'#aeb7be'),(True,'#167b55')):
        for n in data['nodes']:
            if n['mutual_query_complete']==state:
                dot(*xy(n['projected_cm']),2.2 if not state else 2.8,color)
    buckets=defaultdict(list)
    for n in data['nodes']:
        p=n['projected_cm'];buckets[(round(p[0]),round(p[1]))].append(n)
    stacked=[]
    for ns in buckets.values():
        lo=min(ns,key=lambda n:n['projected_cm'][2]);hi=max(ns,key=lambda n:n['projected_cm'][2])
        if hi['projected_cm'][2]-lo['projected_cm'][2]>=193:
            stacked.append({'lower':lo,'upper':hi});dot(*xy(hi['projected_cm']),5.2,'none','#bb6d16')
    highest=max((n for n in data['nodes'] if n['mutual_query_complete']),key=lambda n:n['projected_cm'][2])
    path=highest['outward']['points_cm']
    elements.append('<polyline points="'+' '.join('%.2f,%.2f'%xy(p) for p in path)+'" fill="none" stroke="#3757ac" stroke-width="2.3"/>')
    dot(*xy(origin),6,'#3757ac')
    text(350,795,'X / Y 为相对玩家起点的米；点采样不是道路或面积底图',15,anchor='middle')
    text(970,105,'六个现有角色位置：30 / 30 有向路径完整',21,anchor='middle')
    names=('玩家','友1','友2','敌1','敌2','敌3');ids=[a['id'] for a in data['actors']]
    pairs={(p['from'],p['to']):p['path'] for p in data['directed_pairs']}
    for i,name in enumerate(names):
        text(860+i*48,144,name,17,anchor='middle');text(816,178+i*42,name,17,anchor='end')
    for i,source_id in enumerate(ids):
        for j,target_id in enumerate(ids):
            x=860+j*48;y=172+i*42
            if i==j:text(x,y+6,'—',17,'#667780','middle')
            else:
                p=pairs[(source_id,target_id)];passed=p['valid'] and not p['partial']
                dot(x,y,13,'#e3f3eb' if passed else '#fae5df')
                text(x,y+6,'✓' if passed else '×',18,'#167b55' if passed else '#b3452f','middle')
    text(970,438,'行 → 列；查询通过，实际通行另验',16,anchor='middle')
    example=next(s for s in stacked if s['upper']['projected_cm'][:2]==[-4000.0,6000.0])
    low=example['lower'];high=example['upper']
    text(970,490,'同一 XY，两个不同高度的导航面',21,anchor='middle')
    text(970,520,'世界 X=-40 m，Y=60 m',16,anchor='middle')
    line(1008,567,1008,719,'#c3cdd3',2,'5 5')
    dot(1008,567,7,'#167b55');text(1031,573,f"Z={high['projected_cm'][2]/100:.2f} m",18)
    text(1031,603,'往返查询完整',16,'#167b55')
    dot(1008,719,7,'#8a959d');text(1031,725,f"Z={low['projected_cm'][2]/100:.2f} m",18)
    text(1031,755,'未连到玩家区域',16,'#667780')
    dot(763,646,6,'#3757ac');text(735,679,'玩家起点',16)
    line(775,640,993,573,'#167b55',2)
    line(775,653,993,714,'#8a959d',1.5,'5 5')
    text(970,797,'同 XY 不等于同地点；仍未证明楼梯／真实楼层',15,anchor='middle')
    text(640,831,'当前结果仅为 NavMesh 查询；高处结构、身体净空、原角色实走仍须验证',17,anchor='middle')
    elements.append('</svg>')
    out.mkdir(parents=True);svg.parent.mkdir(parents=True,exist_ok=True)
    svg.write_text('\n'.join(elements)+'\n',encoding='utf-8')
    deps=Path('C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/node')
    png=out/'current-connectivity.png'
    subprocess.run([str(deps/'bin/node.exe'),'-e',
       'require(process.argv[1])(process.argv[2]).png().toFile(process.argv[3]).catch(e=>{console.error(e);process.exitCode=1});',
       str(deps/'node_modules/sharp'),str(svg),str(png)],check=True)
    analysis={'query_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'same_xy_key_precision_cm':1,'candidate_vertical_gap_cm':193,'stacked_candidates':len(stacked),
        'stacked_both_mutual':sum(s['lower']['mutual_query_complete'] and s['upper']['mutual_query_complete'] for s in stacked),
        'stacked_touching_mutual':sum(s['lower']['mutual_query_complete'] or s['upper']['mutual_query_complete'] for s in stacked),
        'examples':[{k:{'id':n['id'],'projected_cm':n['projected_cm'],'mutual_query':n['mutual_query_complete']} for k,n in s.items()} for s in stacked],
        'visuals':[{'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (svg,png)]}
    (out/'analysis.json').write_text(json.dumps(analysis,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'stacked_candidates':len(stacked),'stacked_both_mutual':analysis['stacked_both_mutual'],'png':str(png)}))


if __name__=='__main__':main()
