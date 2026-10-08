"""Plot a review-only mission layout over immutable measured Paris survey cells."""
import hashlib,json,math,re,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
E=STORE/'Evidence';F=E/'FineMapGridV1/expanded_v2_20261007'
OUT=E/'MissionLayoutV1/layout_v2_20261008'
FONT='C:/Windows/Fonts/msyh.ttc'
BLUE='#248fe6';GOLD='#f9b332';RED='#f35365';GREEN='#30d68a'

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def font(n):return ImageFont.truetype(FONT,n)
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def selected_nodes(path,ids):
    """Read selected flat node records without loading the 596 MB array into memory."""
    needles={i:('"id":'+str(i)+',').encode() for i in ids};found={};tail=b'';h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):
            h.update(block);chunk=tail+block
            for i,needle in needles.items():
                if i in found:continue
                k=chunk.find(needle)
                if k>=0:
                    a=chunk.rfind(b'{"c":',0,k);b=chunk.find(b'}',k)
                    if a>=0 and b>=0:found[i]=json.loads(chunk[a:b+1])
            tail=chunk[-8192:]
    assert set(found)==set(ids)
    return found,h.hexdigest()

def make():
    assert not OUT.exists(),'Frozen layout identity already exists'
    bank=json.loads((E/'UEStandardNavigationV1/bank_v1_20261007/bank.json').read_text())
    assert all(digest(F/n)==h for n,h in bank['source_sha256'].items())
    spec=json.loads((F/'grid_spec.json').read_text());assert spec==bank['grid_spec']
    z=np.load(F/'derived/full_filters.npz');x=spec['xmin_cm']+(z['c']+.5)*25;y=spec['ymax_cm']-(z['r']+.5)*25
    base=z['base']&(z['layer']==0)&~z['quarantine'];chosen={}
    requests=[('S',[-3162.5,-25937.5],'spawn','盟军集结／玩家'),
        ('A1',[-3312.5,-26087.5],'ally','盟军1'),('A2',[-3012.5,-26087.5],'ally','盟军2'),
        ('T1',[5850,-20250],'task','目标1／抵达对岸'),('G1',[7100,-20300],'guard','德军1／桥头守卫'),
        ('T2',[12087.5,-12087.5],'task','目标2／进城路口'),('G2',[12100,-11000],'guard','德军2／路口守卫或巡逻'),
        ('T3',[5500,-3600],'task','目标3／市中心据点'),('G3',[6400,-3500],'guard','德军3／据点守军')]
    points=[]
    for key,target,mode,label in requests:
        use=base.copy()
        if mode=='spawn':use&=z['count3']>=3
        if mode=='task':use&=z['task']
        if mode=='ally':
            si=chosen['S'];use&=(z['group']==z['group'][si])&((x-x[si])**2+(y-y[si])**2<=300**2)
            for other in ('S','A1','A2'):
                if other in chosen:
                    j=chosen[other];use&=(x-x[j])**2+(y-y[j])**2>=150**2
        ids=np.flatnonzero(use);distance=(x[ids]-target[0])**2+(y[ids]-target[1])**2
        i=int(ids[np.argmin(distance)]);assert float(distance.min())<300**2
        chosen[key]=i;points.append({'id':key,'label_zh':label,'kind':mode,'node_id':i,
            'cell':[int(z['c'][i]),int(z['r'][i])],'group':int(z['group'][i]),'local_stack':0,
            'station_count_3m':int(z['count3'][i]),'task_filter':bool(z['task'][i]),
            'requested_xy_cm':target,'snap_distance_cm':math.sqrt(float(distance.min())),
            'status':'static_survey_candidate_not_mission_runtime_accepted'})
    nodes,node_hash=selected_nodes(F/'links/nodes.json',set(chosen.values()))
    manifest=json.loads((F/'derived/manifest.json').read_text())
    assert node_hash==manifest['scopes']['full']['source_nodes_sha256']
    original=Image.open(F/'derived/full_walk_L0.png');assert original.mode=='1'
    for p in points:
        n=nodes[p['node_id']];assert p['cell']==[n['c'],n['r']]
        p['feet_cm']=n['feet_cm'];p['nav_cm']=n['nav_cm'];p['support_component']=n['component'];p['support_mesh']=n['mesh']
        assert original.getpixel(tuple(p['cell'])) and not z['quarantine'][p['node_id']]
        xx=spec['xmin_cm']+(p['cell'][0]+.5)*25;yy=spec['ymax_cm']-(p['cell'][1]+.5)*25
        assert max(abs(xx-p['feet_cm'][0]),abs(yy-p['feet_cm'][1]))<1e-6
    by={p['id']:p for p in points}
    for a,b in (('S','A1'),('S','A2'),('A1','A2')):
        assert math.dist(by[a]['feet_cm'][:2],by[b]['feet_cm'][:2])>=150
    bridge_file=E/'BridgeConnectivityV1/runtime_reverse_v3_20261007/result.json'
    br=json.loads(bridge_file.read_text());case=next(c for c in br['cases'] if c['status']=='passed')
    m=case['members'][0];trace=[m['standing']['feet_cm']]+[s['members'][0]['feet_cm'] for s in case['samples']]+[m['final']['feet_cm']]
    diag_file=E/'UEStandardNavigationV1/diagnostic_expanded_v1_20261007/result.json'
    diag=json.loads(diag_file.read_text());q=next(c for c in diag['cases'] if c['origin_index']==49 and c['role']=='allied')['diagnostic_queries'][1]
    assert q['success'] and not q['partial'] and q['effective_max_search_nodes']==65536
    old=q['points_cm'];centre=by['T3']['feet_cm']
    # Clip the existing query polyline at its closest geometric projection to the draft objective.
    candidates=[]
    for k,(a,b) in enumerate(zip(old,old[1:])):
        v=np.array(b[:2])-a[:2];t=float(np.clip(np.dot(np.array(centre[:2])-a[:2],v)/np.dot(v,v),0,1))
        p=(np.array(a)+(np.array(b)-a)*t).tolist();candidates.append((math.dist(p[:2],centre[:2]),k,p))
    _,end,projection=min(candidates)
    after_bridge=old[6:end+1]+[projection,centre]
    # Include the approach objective explicitly; these joins have not been queried in UE.
    goal=by['T2']['feet_cm'];insert_at=min(range(len(after_bridge)-1),key=lambda k:
        math.dist(after_bridge[k][:2],goal[:2])+math.dist(goal[:2],after_bridge[k+1][:2])-
        math.dist(after_bridge[k][:2],after_bridge[k+1][:2]))+1
    after_bridge.insert(insert_at,goal)
    proposed=[by['S']['feet_cm'],[-1800,-24200],[0,-22500],[1950,-20650]]
    route=[p[:2] for p in proposed+list(reversed(trace))+[by['T1']['feet_cm']]+after_bridge]
    assert all(any(math.dist(p,by[key]['feet_cm'][:2])<1e-6 for p in route) for key in ('S','T1','T2','T3'))
    OUT.mkdir(parents=True)
    layout={'schema':'paris_mission_layout_draft_v1','date':'2026-10-08','grid_spec':spec,'points':points,
        'source_scope':'expanded_disposable_survey','local_stack_not_a_storey':True,
        'source_sha256':bank['source_sha256'],'source_nodes_sha256':node_hash,
        'bridge_player_trace_cm':trace,'bridge_trace_source':str(bridge_file.relative_to(STORE)),
        'bridge_trace_source_sha256':digest(bridge_file),'native_query_source_sha256':digest(diag_file),
        'native_query_origin_index':49,'native_query_budget':65536,'native_query_points_cm':old,
        'proposed_progression_xy_cm':route,'route_is_planning_annotation_not_a_new_native_query':True,
        'bridge_other_roles_or_squad_passed':False,'mission_route_physically_walked':False,
        'formal_placement_saved':False,'custom_pathfinder_used':False,
        'capture_zone_draft_xy_cm':[3900,-4200,7500,-3000],
        'source_immutable_hashes_verified':True,'coordinate_white_quarantine_separation_checks':True,
        'every_required_objective_explicitly_on_proposed_line':True,
        'retained_presentation_v1':'Evidence/MissionLayoutV1/layout_v1_20261008'}
    put(OUT/'layout.json',layout)
    plot(layout,original.convert('RGB'),'overview',OUT/'PARIS_MISSION_LAYOUT_20261008.png')
    plot(layout,original.convert('RGB'),'detail',OUT/'PARIS_MISSION_LAYOUT_DETAILS_20261008.png')
    write_review(layout)
    receipt={'status':'pass_static_annotation_checks','outputs':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in OUT.iterdir() if p.is_file()},
        'source_hashes_after':{n:digest(F/n) for n in bank['source_sha256']},'visual_review':'pending'}
    assert receipt['source_hashes_after']==bank['source_sha256'];put(OUT/'receipt.json',receipt)
    print(json.dumps({'folder':str(OUT),'points':{p['id']:p['feet_cm'] for p in points},'source_retained':True},ensure_ascii=False))

def dashed(d,pts,fill,width=5,dash=17,gap=12):
    phase=0
    for a,b in zip(pts,pts[1:]):
        v=np.array(b)-a;length=float(np.linalg.norm(v))
        if not length:continue
        u=v/length;t=0
        while t<length:
            on=phase<dash;n=min(length-t,(dash if on else dash+gap)-phase)
            if on:d.line([tuple(np.array(a)+u*t),tuple(np.array(a)+u*(t+n))],fill=fill,width=width)
            t+=n;phase=(phase+n)%(dash+gap)

def label(d,p,text,offset,color,size=27):
    x,y=p;tx,ty=x+offset[0],y+offset[1];f=font(size);box=d.multiline_textbbox((tx,ty),text,font=f,spacing=4)
    d.line((x,y,tx,ty+(box[3]-box[1])/2),fill=color,width=2)
    d.rounded_rectangle((box[0]-10,box[1]-6,box[2]+10,box[3]+8),radius=7,fill='#142230',outline=color,width=2)
    d.multiline_text((tx,ty),text,font=f,fill='#ffffff',spacing=4)

def panel(im,d,base,spec,box,area):
    x0,y0,x1,y1=box;left,top,w,h=area;scale=min(w/(x1-x0),h/(y1-y0))
    c0=round((x0-spec['xmin_cm'])/25);r0=round((spec['ymax_cm']-y1)/25)
    c1=round((x1-spec['xmin_cm'])/25);r1=round((spec['ymax_cm']-y0)/25)
    ww=round((x1-x0)*scale);hh=round((y1-y0)*scale);left+=round((w-ww)/2);top+=round((h-hh)/2)
    im.paste(base.crop((c0,r0,c1,r1)).resize((ww,hh),Image.Resampling.NEAREST),(left,top))
    def xy(p):return left+(p[0]-x0)*scale,top+(y1-p[1])*scale
    def inside(p):return x0<=p[0]<=x1 and y0<=p[1]<=y1
    for x in range(math.ceil(x0/5000)*5000,int(x1)+1,5000):
        a=xy([x,y0]);d.line((a[0],top,a[0],top+hh),fill='#303a45',width=1)
        d.text((a[0]+3,top+3),f'{x/100:g}',font=font(17),fill='#9eb4cc')
    for y in range(math.ceil(y0/5000)*5000,int(y1)+1,5000):
        a=xy([x0,y]);d.line((left,a[1],left+ww,a[1]),fill='#303a45',width=1)
        d.text((left+4,a[1]+3),f'{y/100:g}',font=font(17),fill='#9eb4cc')
    d.rectangle((left,top,left+ww,top+hh),outline='#8494a6',width=2)
    n=50 if box[2]-box[0]>20000 else 20;px=n*100*scale
    d.rectangle((left+20,top+hh-62,left+px+50,top+hh-15),fill='#122231')
    d.line((left+30,top+hh-30,left+30+px,top+hh-30),fill='white',width=6)
    d.text((left+30,top+hh-62),f'{n} m',font=font(22),fill='white')
    return xy,inside,(left,top,ww,hh)

def markers(d,layout,xy,inside,detail=False):
    for p in layout['points']:
        if not inside(p['feet_cm']):continue
        if not detail and p['id'] in ('A1','A2'):continue
        x,y=xy(p['feet_cm']);r=(5 if p['kind'] in ('spawn','ally') else 9) if detail else 10
        if p['kind']=='guard':d.polygon([(x,y-r-3),(x-r-2,y+r),(x+r+2,y+r)],fill=RED,outline='#ffffff',width=2)
        elif p['kind']=='task':d.rectangle((x-r,y-r,x+r,y+r),fill=GOLD,outline='#141a23',width=2)
        else:d.ellipse((x-r,y-r,x+r,y+r),fill=BLUE,outline='white',width=2)

def overlay(d,layout,xy,inside):
    route=layout['proposed_progression_xy_cm']
    for a,b in zip(route,route[1:]):
        if inside(a) and inside(b):dashed(d,[xy(a),xy(b)],GOLD,5)
    ps=layout['bridge_player_trace_cm']
    for a,b in zip(ps,ps[1:]):
        if inside(a) and inside(b):d.line([xy(a),xy(b)],fill=GREEN,width=6)
    zone=layout['capture_zone_draft_xy_cm'];corners=[[zone[0],zone[1]],[zone[2],zone[1]],[zone[2],zone[3]],[zone[0],zone[3]]]
    if all(inside(p) for p in corners):dashed(d,[xy(p) for p in corners+[corners[0]]],GOLD,3,9,8)

def plot(layout,base,kind,path):
    spec=layout['grid_spec'];by={p['id']:p for p in layout['points']}
    if kind=='overview':
        im=Image.new('RGB',(2200,1860),'#eef2f6');d=ImageDraw.Draw(im)
        d.text((65,35),'巴黎任务布局草案',font=font(53),fill='#152b40')
        d.text((65,112),'河对岸集结 → C桥 → 进城路口 → 市中心据点',font=font(31),fill='#375169')
        xy,inside,frame=panel(im,d,base,spec,[-28000,-32000,18000,24000],(60,205,1250,1510))
        overlay(d,layout,xy,inside);markers(d,layout,xy,inside)
        offsets={'S':(-225,45),'T1':(-300,-85),'G1':(50,55),'T2':(-260,35),'G2':(-260,-75),'T3':(-245,-100),'G3':(55,-20)}
        texts={'S':'S 盟军集结\n玩家＋2盟军','T1':'① 过桥抵达对岸','G1':'G1 桥头守卫','T2':'② 进城路口','G2':'G2 路口敌军','T3':'③ 市中心据点','G3':'G3 据点守军'}
        for key,off in offsets.items():label(d,xy(by[key]['feet_cm']),texts[key],off,RED if key.startswith('G') else BLUE if key=='S' else GOLD,26)
        label(d,xy([3955,-20837]),'C桥',(-100,-155),'#9dc9f1',23)
        left=1390;d.text((left,205),'位置与角色',font=font(34),fill='#152b40')
        yy=275
        for p in layout['points']:
            color=RED if p['kind']=='guard' else GOLD if p['kind']=='task' else BLUE
            d.rounded_rectangle((left,yy,left+680,yy+104),radius=11,fill='white')
            d.text((left+18,yy+9),p['id']+'  '+p['label_zh'],font=font(25),fill=color)
            d.text((left+18,yy+53),f"X {p['feet_cm'][0]/100:+.2f} m    Y {p['feet_cm'][1]/100:+.2f} m",font=font(23),fill='#34495f');yy+=116
        yy+=15
        for text,color in [('●  蓝色：盟军初始候选位置',BLUE),('■  黄色：任务目标候选位置','#aa7515'),('▲  红色：德军候选位置',RED),('—  绿色：已实走的玩家桥段','#168758'),('┄  橙虚线：待验证的推进走廊','#aa7515')]:
            d.text((left,yy),text,font=font(24),fill=color);yy+=43
        d.text((left,yy+15),'图上方＝UE +Y；右方＝UE +X\nX／Y等比例；坐标单位为米\n不是地理方位或历史街区认证',font=font(23),fill='#40566d',spacing=9)
        d.text((65,1760),'25厘米原底图保留｜黑：阻挡或未准入；白：静态通行候选｜位置均待UE任务验证',font=font(27),fill='#273d53')
        d.text((65,1810),'仅二维标注，尚未放入UE。C桥仅玩家已验证；整条走廊、小队及交火仍待验证。',font=font(25),fill='#40566d')
    else:
        im=Image.new('RGB',(2200,1320),'#eef2f6');d=ImageDraw.Draw(im)
        d.text((55,30),'任务位置放大图',font=font(49),fill='#152b40')
        d.text((55,101),'绿色＝玩家实走桥段；橙虚线＝布局参考；蓝／黄／红分别为盟军／任务／敌军',font=font(27),fill='#40566d')
        d.text((55,170),'过桥与起始小队',font=font(34),fill='#152b40')
        d.text((1160,170),'进城与最终据点',font=font(34),fill='#152b40')
        xy,inside,_=panel(im,d,base,spec,[-6000,-28000,9500,-18500],(55,245,1020,900))
        overlay(d,layout,xy,inside);markers(d,layout,xy,inside,True)
        labels={'S':((-145,-90),'S 玩家'),'A1':((-165,-15),'A1 盟军1'),'A2':((90,-15),'A2 盟军2'),
            'T1':((-5,-140),'T1 对岸目标'),'G1':((0,70),'G1 桥头守卫')}
        for key,(off,t) in labels.items():label(d,xy(by[key]['feet_cm']),t,off,RED if key=='G1' else GOLD if key=='T1' else BLUE,25)
        label(d,xy([1950,-20650]),'桥前入口',(-130,-160),'#9dc9f1',24)
        label(d,xy([3955,-20837]),'C桥',(-110,110),'#9dc9f1',25)
        xy,inside,_=panel(im,d,base,spec,[1000,-14000,15000,1000],(1160,245,985,900))
        overlay(d,layout,xy,inside);markers(d,layout,xy,inside,True)
        for key,off,text in [('T2',(-320,40),'T2 进城路口'),('G2',(-300,-90),'G2 路口敌军'),('T3',(-110,-160),'T3 占领据点'),('G3',(75,50),'G3 据点守军')]:
            label(d,xy(by[key]['feet_cm']),text,off,RED if key.startswith('G') else GOLD,27)
        d.text((55,1190),'初始6角色：玩家＋2盟军＋3德军。市中心虚框是占领范围候选，边界尚未实走验收。',font=font(27),fill='#273d53')
        d.text((55,1250),'保留每个点的实际源XYZ；L0表示局部堆叠次序，不等于已经确认的楼层。',font=font(25),fill='#40566d')
    im.save(path)

def write_review(layout):
    d=ROOT/'Docs/Development/MissionLoopV1';rows=[]
    english={'S':'Assembly / player','A1':'Ally 1','A2':'Ally 2','T1':'Far-bank objective','G1':'Bridge guard','T2':'City approach','G2':'Junction guard/patrol','T3':'City centre capture','G3':'Centre defender'}
    for p in layout['points']:
        x,y,z=p['feet_cm'];rows.append((p['id'],english[p['id']],p['label_zh'],f'{x/100:.3f}',f'{y/100:.3f}',f'{z/100:.5f}'))
    en='\n'.join('| '+' | '.join([r[0],r[1],*r[3:]])+' |' for r in rows)
    zh='\n'.join('| '+' | '.join([r[0],r[2],*r[3:]])+' |' for r in rows)
    pre='| ID | Position | X m | Y m | Survey feet Z m |\n| --- | --- | ---: | ---: | ---: |\n'
    content=f'''# Bridge mission map layout draft

8 October 2026. Candidate layout on the preserved 25 cm expanded static survey. [Chinese review](MISSION_LAYOUT_20261008_ZH.md). Follow [the annotation plan](MISSION_LAYOUT_ANNOTATION_PLAN_20261008.md) and [selected mission](BRIDGE_TO_CENTRE_MISSION_DESIGN_20261007.md).

{pre}{en}

All nine anchors are original admitted L0 cell centres outside quarantine; S/A1/A2 are at least 1.5 m apart in the same local group and within 3 m of S. Z is measured survey feet height, not capsule-centre spawn height or fresh formal-role standing acceptance. Preserve the full source node, local stack, native projection, support and coordinates in the private layout JSON. L0 does not establish a semantic floor.

Start west of lower C bridge, cross toward the right-bank city, advance along the outer street through T2 and turn toward T3. T3 is a gameplay city-centre candidate, distinct from the former hub; it is not an authenticated historical city centre. G1/G2 kills are optional; G3 is the initial sealed centre defender. The outlined capture boundary remains a proposal.

The green segment reproduces the audited original-player reverse bridge trace from 7 October. Its independent outward evidence also exists; Allies/squad are unmeasured there. The orange dashed corridor is a design annotation. Its city portion references the recorded origin49 cloned-filter UE query, clipped and joined to new anchors. New joins and S-to-bridge guidance have no new native query or physical traversal. No new A*, UE process, saved actor/navigation/config, model/finger/gun edit or publication is performed.

Black means blocked or not admitted by the conservative static mask, not universally proved physical obstruction. White means a static terrain candidate. Source masks remain byte-identical. ML014/015/020 inform quarantine, support identity and navigation-budget limitations. Before placement, verify this frozen corridor with the player and two Allies together, actual support, fresh original-character standing, selected native coverage/filter and contacts; preserve any failed result.

Private output: `Evidence/MissionLayoutV1/layout_v2_20261008/` contains layout.json, overview/detail PNGs and receipt.json. Source hashes, node authentication, white-cell/quarantine checks and coordinate round trips pass before delivery. Visual review is recorded separately after inspection. The earlier presentation remains in layout_v1_20261008. This is a review draft; mission route, combat and formal placement are not accepted by a rendered figure.
'''
    cn=f'''# 过桥任务二维布局草案

2026年10月8日。在保留的25厘米扩展静态测绘底图上标注候选位置。[英文原文](MISSION_LAYOUT_20261008.md)。遵循[标注流程](MISSION_LAYOUT_ANNOTATION_PLAN_20261008_ZH.md)及[选定任务设计](BRIDGE_TO_CENTRE_MISSION_DESIGN_20261007_ZH.md)。

| 编号 | 位置 | X米 | Y米 | 测绘脚底Z米 |
| --- | --- | ---: | ---: | ---: |
{zh}

9个锚点均为原测绘L0准入格心，位于隔离范围之外；S／A1／A2在同一个局部组内，彼此至少1.5米、距离S不超过3米。Z是测绘脚底高度，不是角色胶囊中心出生高度，也不代表已经重新验过正式角色站立。私有JSON保留完整源节点、局部堆叠、导航投影、支撑与坐标；L0不等于已确认楼层。

从下方C桥西侧集结，过桥进入图右岸城市，沿外侧街道经过T2，再转向T3。T3是游戏中的市中心据点候选，与原测试汇聚点不同，不是历史城市中心认证。G1／G2击杀可选，G3为初始登记据点守军。虚框占领边界仍为草案。

绿线复现10月7日已审计的原玩家反向过桥轨迹，独立去程证据也保留；这里还没有盟军／小队验证。橙色虚线仅表示规划走廊：市区段参考旧origin49复制过滤器UE查询形状，再截取、连接新锚点。新连接段及S至桥前的方向参考，没有新的原生查询或真实行走证据。本轮没有运行新A*、启动UE、保存角色／导航／配置、修改模型／手指／枪械或发布。

黑色表示保守静态筛选的阻挡或未准入，不等于全部已证明物理不通；白色表示静态地形候选。原底图字节不变。ML014／015／020分别约束隔离、支撑身份和导航预算解释。正式放置前，应以玩家和两盟军共同验证这份冻结走廊，检查真实支撑、原角色重新落地、选定原生导航覆盖／过滤器和接触点，保留任何失败。

私有产物：`Evidence/MissionLayoutV1/layout_v2_20261008/`中的layout.json、总览／放大PNG及receipt.json。交付前检查源哈希、节点身份、白格／隔离和坐标往返；图片目检另记回执。早期排版保留在layout_v1_20261008。本图供布局评审，不代表整条任务、交战或正式布局已验收。
'''
    for name,text in [('MISSION_LAYOUT_20261008.md',content),('MISSION_LAYOUT_20261008_ZH.md',cn)]:
        (d/name).write_text(text,encoding='utf-8',newline='\n')

if __name__=='__main__':make()
