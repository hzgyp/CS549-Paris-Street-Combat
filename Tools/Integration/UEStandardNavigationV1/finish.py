"""Close completed native controls; generate measured comparisons without altering old maps."""
import ast,collections,json,math,shutil,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
P=STORE/'Evidence/UEStandardNavigationV1';D=ROOT/'Docs/Development/MissionLoopV1'
FONT='C:/Windows/Fonts/msyh.ttc'

def put(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8',newline='\n')
def font(size):return ImageFont.truetype(FONT,size)

def main():
    b=json.loads((P/'bank_v1_20261007/bank.json').read_text());assert guard_rows()==b['protected_rows'] and guards_match(b['protected_rows'])
    es=['saved_probe_v1_20261007','early_v2_20261007','full_v1_20261007']
    reports={e:json.loads((P/e/'result.json').read_text()) for e in es}
    audits={e:json.loads((P/e/'audit.json').read_text()) for e in es}
    assert all(a['status']=='pass_independent_standard_navigation_audit' for a in audits.values())
    saved={s['id']:s for s in reports[es[0]]['cases']}
    actual={s['id']:s for e in es[1:] for s in reports[e]['cases']};assert len(saved)==len(actual)==138
    counts={role:dict(collections.Counter(s['status'] for s in actual.values() if s['role']==role)) for role in ('allied','german')}
    requests={role:sum(s['status']=='request_admitted' for s in saved.values() if s['role']==role) for role in counts}
    reasons={role:dict(collections.Counter(s['reason'] for s in actual.values() if s['role']==role and s['status']=='negative')) for role in counts}
    gains={role:[s['origin_index'] for s in actual.values() if s['role']==role and s['status']=='passed' and saved[s['id']]['status']=='negative'] for role in counts}
    art=P/'artifact_v1_20261007';assert not art.exists();art.mkdir()
    im=Image.new('RGB',(1550,1220),'#f3f5f7');draw=ImageDraw.Draw(im)
    draw.text((35,24),'UE标准导航 · 保存覆盖与完整覆盖对照',font=font(34),fill='#18222e')
    draw.text((35,79),'相同69个起点和中心；图中绿色/红色来自正式角色实际移动，未测白色仍只是地形候选',font=font(18),fill='#445160')
    source=STORE/b['source']
    assert all(digest(source/n)==h for n,h in b['source_sha256'].items())
    assert all(digest(ROOT/f'Unreal/ParisStreetCombat/Plugins/{n}/Binaries/Win64/UnrealEditor-{n}.dll')==h for n,h in b['helpers'].items())
    base=Image.open(source/'derived/full_walk_L0.png').convert('RGB')
    spec=b['grid_spec'];orig=b['origins'];xs=[s['node']['feet_cm'][0] for s in orig];ys=[s['node']['feet_cm'][1] for s in orig]
    lo=[min(xs)-1800,min(ys)-1800];hi=[max(xs)+1800,max(ys)+1800]
    xmin=spec.get('xmin_cm',-50400);ymax=spec.get('ymax_cm',50400)
    crop=[max(0,int((lo[0]-xmin)/25)),max(0,int((ymax-hi[1])/25)),min(4032,int((hi[0]-xmin)/25)+1),min(4032,int((ymax-lo[1])/25)+1)]
    panel=base.crop(crop);scale=min(690/panel.width,800/panel.height);wh=(int(panel.width*scale),int(panel.height*scale));panel=panel.resize(wh,Image.Resampling.NEAREST)
    for col,role in enumerate(counts):
        left=35+col*775;top=183;draw.text((left,125),('盟军' if role=='allied' else '德军')+f"：实际到达{counts[role].get('passed',0)}/69",font=font(27),fill='#172c44')
        im.paste(panel,(left,top))
        def pos(p):return (left+((p[0]-xmin)/25-crop[0])*scale,top+((ymax-p[1])/25-crop[1])*scale)
        for s in actual.values():
            if s['role']!=role:continue
            x,y=pos(s['source_cm']);color='#169447' if s['status']=='passed' else '#d63d34'
            draw.ellipse((x-5,y-5,x+5,y+5),fill=color,outline='#061421',width=1)
            if s['origin_index'] in gains[role]:draw.ellipse((x-9,y-9,x+9,y+9),outline='#247bc2',width=2)
        x,y=pos(b['hub']['feet_cm']);draw.rectangle((x-7,y-7,x+7,y+7),fill='#9855d3',outline='white',width=1)
        # Selected successful west/south native request routes are annotations, not painted walkable cells.
        for index in (7,49):
            s=actual[f'origin_{index:03d}_{role}']
            if s['status']=='passed':draw.line([pos(p) for p in s['request']['path_cm']],fill='#e09016',width=2)
        y=top+wh[1]+20
        draw.text((left,y),f"原保存导航标准请求准入 {requests[role]}/69；未保存重建后到达 {counts[role].get('passed',0)}/69",font=font(17),fill='#233444')
        draw.text((left,y+30),f"蓝圈：原请求拒绝、覆盖对照后真实到达（{len(gains[role])}点）",font=font(17),fill='#247bc2')
        draw.text((left,y+60),'绿：真实到达  红：保留负结果  紫：临时中心  橙：示例UE原生路径',font=font(16),fill='#354657')
    draw.text((35,1160),'25厘米原黑白图保留；导航重建未保存；不代表最终出生/任务/遭遇点或完整小队互达验收',font=font(19),fill='#334155')
    image=art/'PARIS_UE_STANDARD_NAVIGATION_20261007.png';im.save(image)
    ff=np.load(source/'derived/full_filters.npz');source_masks={}
    for role in counts:
        mask=np.zeros((4032,4032),dtype=bool);ids=np.flatnonzero(ff['base']&(ff['layer']==0));mask[ff['r'][ids],ff['c'][ids]]=True
        negatives=[s for s in actual.values() if s['role']==role and s['status']=='negative']
        for s in negatives:assert s['layer']==0 and mask[s['r'],s['c']];mask[s['r'],s['c']]=False
        file=art/(role+'_expanded_hub_relative_L0.png');Image.fromarray(mask).save(file)
        assert Image.open(file).mode=='1'
        source_masks[role]={'file':file.name,'sha256':digest(file),'additional_black_centres':len(negatives),'unmeasured_white_not_certified':True}
    archive=P/'failed_runtime_v1_20261007';assert not archive.exists();archive.mkdir();copies=[]
    for e in es:
        for name in ('result.json','entry.json','exit.json','audit.json','ue_standard.py','guards_before.json'):
            src=P/e/name;dest=archive/e/name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(src,dest);assert digest(src)==digest(dest);copies.append({'source':src.relative_to(STORE).as_posix(),'copy':dest.relative_to(STORE).as_posix(),'sha256':digest(src)})
        for s in reports[e]['cases']:
            if s['status']=='negative' and (P/e/s['samples_file']).exists():
                src=P/e/s['samples_file'];dest=archive/e/src.name;shutil.copyfile(src,dest);assert digest(src)==digest(dest);copies.append({'source':src.relative_to(STORE).as_posix(),'copy':dest.relative_to(STORE).as_posix(),'sha256':digest(src)})
        src=ROOT/f'tmp/ue-standard-navigation-v1/{e}.log';dest=archive/e/'engine.log';shutil.copyfile(src,dest);assert digest(src)==digest(dest);copies.append({'source':src.relative_to(ROOT).as_posix(),'copy':dest.relative_to(STORE).as_posix(),'sha256':digest(src)})
    closure={'status':'complete_finite_standard_navigation_control','cases_per_role':69,'expanded_actual_counts':counts,'saved_standard_request_admission':requests,
        'expanded_negative_reasons':reasons,'new_actual_arrivals_from_saved_rejections':gains,'bank_sha256':digest(P/'bank_v1_20261007/bank.json'),
        'entry_audits':{e:digest(P/e/'audit.json') for e in es},'source_masks':source_masks,'figure':image.relative_to(STORE).as_posix(),'figure_sha256':digest(image),
        '703_guards_exact':True,'formal_navigation_saved':False,'original_maps_retained':True,'all_pairs_or_return_certified':False,'semantic_floors_certified':False,'crowd_acceptance':False,'final_layout_selected':False,'engine_slot_released':True}
    put(art/'closure.json',json.dumps(closure,indent=2)+'\n');put(P/'closure_v1_20261007.json',json.dumps(closure,indent=2)+'\n')
    put(archive/'manifest.json',json.dumps({'copies':copies,'originals_retained':True},indent=2)+'\n')
    sr=dict(reports[es[0]]['pie_navigation']);fr=dict(reports[es[2]]['pie_navigation'])
    # Native GetNumActiveTiles is zero in these PIE duplicates despite real exported tiles.
    # Preserve that raw counter; report the independently enumerated occupied export count.
    for info,e in ((sr,es[0]),(fr,es[2])):
        mesh=json.loads((P/e/info['export_file']).read_text())
        info['occupied_export_tiles']=mesh['exported_tiles']
    lines=['| Profile | Saved standard requests admitted (not arrivals) | Expanded actual arrivals | Expanded negatives |','|---|---:|---:|---|']
    for role in counts:lines.append(f"| {role} | {requests[role]}/69 | {counts[role].get('passed',0)}/69 | {json.dumps(reasons[role])} |")
    table='\n'.join(lines)
    diagnosis=json.loads((P/'query_diagnosis_v1_20261007.json').read_text())
    assert diagnosis['status']=='complete_native_query_diagnosis' and diagnosis['native_queries']==48 and diagnosis['physical_movements']==0
    budget_cases=diagnosis['search_budget_contribution_cases']
    closure['query_diagnosis_sha256']=digest(P/'query_diagnosis_v1_20261007.json')
    closure['search_budget_contribution_combinations']=len(budget_cases)
    put(art/'closure.json',json.dumps(closure,indent=2)+'\n');put(P/'closure_v1_20261007.json',json.dumps(closure,indent=2)+'\n')
    coverage_en=('New complete coverage supports a saved coverage/build contribution at the actually restored sites.' if any(gains.values()) else 'The expanded export alone does NOT establish that coverage caused the original rejections: no previously rejected saved request has yet gained physical arrival under the standard default query budget.')
    coverage_zh=('实际恢复的点证明保存导航覆盖/构建有影响。' if any(gains.values()) else '扩大后的导出本身不能证明覆盖是旧拒绝的原因：在UE标准默认查询预算下，旧保存请求拒绝点没有新增真实到达。')
    budget_en=f'Native diagnosis observes {len(budget_cases)} site/role/scope combinations where the original query exhausts its search-node budget and one cloned65536-budget query finds a complete route. See UE_STANDARD_NAV_QUERY_RESULT. These are query-only observations, not higher-budget physical arrivals, an optimal production budget or all69 cases verified at higher budget. No default filter/config is changed.'
    budget_zh=f'原生诊断观察到{len(budget_cases)}个点/阵营/范围组合：原查询耗尽搜索节点预算，复制过滤器的65536查询获得完整路径。见UE_STANDARD_NAV_QUERY_RESULT。这只是查询，不是高预算实际到达、正式最优预算或69点全量高预算验收；未改默认过滤器/配置。'
    en=f'''# Standard Unreal navigation result

7 October 2026. The explicitly authorized paired control is complete. Read its implementation and ML013/14/17/18/19; all original convergence/fine-grid records and maps remain immutable.

{table}

The previous implementation already used UE Recast/Detour, but submitted manually queried paths to PathFollowing. This control uses the original AIController's standard MoveToLocation with pathfinding, native goal projection and complete paths. The saved stage issues and intentionally cancels requests before a movement tick; it does not repeat/claim physical arrivals. The expanded stage uses original accepted formal Allied/German bodies, native PathFollowing/CharacterMovement, original300cm/s and actual matching success/standing/overlap/dwell gates. Four early actual cases are counted once with134 further cases:138 total, zero bank cases unmeasured. These are69 origins, not all733900 source white centres.

Saved native coverage: {sr['occupied_export_tiles']} enumerated occupied tiles/{sr['polygon_count']} polygons; bounds centre{sr['bounds_center_cm']}, extent{sr['bounds_extent_cm']}cm. Unsaved expanded coverage: {fr['occupied_export_tiles']} tiles/{fr['polygon_count']} polygons; centre{fr['bounds_center_cm']}, extent{fr['bounds_extent_cm']}cm. Both retain radius34/height193/slope45/tile1000, unchanged source terrain/collision and formal movement profiles. Expanding/rebuilding navigation changes the tested coverage and may change tessellation; it does not repair/adopt the saved production map. {coverage_en} It never establishes that all earlier negatives were physical terrain obstacles. New actual arrivals from previously rejected saved requests: Allied{len(gains['allied'])}, German{len(gains['german'])}. Remaining negatives need their own route/collision diagnosis; no offsets, speed/threshold changes or failed travel retries occurred.

{budget_en}

Source maps and old conditional black masks remain retained; new per-role expanded/hub-relative1bit masks remove only newly observed negative25cm starts, never neighbours or whole tiles. The figure shows actual sampled arrival outcomes and two successful native request routes when available. Native request routes are distinct from ground-truth body trajectory; every actual travel retains its real samples/supports/events. Global floor identity, bridge-specific visual review, return/all-pairs/squad/crowd/combat/FPS/MVP and final mission sites remain unpassed.

The three admitted entries normally exit0/strict log0; independent audits pass. Failed early_v1 also exits0/strict log0 but has zero movement: editor-body collision remained disabled into PIE, causing all initial bodies to fall. ML021 retains its authenticated evidence; early_v2 restores exact original editor flags before PIE and admits original grounded profiles without changing any geometry or movement gate. Current703, all three old helpers, fine source files, equipment/resources/player possession and original models/fingers/weapon logic remain exact. No map/package/navigation/config save, asset fitting, commit, push or publication. Private selected evidence: Evidence/UEStandardNavigationV1/artifact_v1_20261007; runtime negatives and authenticated source/receipt/log copies: failed_runtime_v1_20261007. Read ML020/21 before subsequent map work. Raw PIE GetNumActiveTiles counters are0 although2274/11828 occupied tiles are actually enumerated; the coverage counts above use native exported occupied tiles, and preserve the raw counters. Native slot released; check actual process before another writer.
'''
    zh=f'''# UE标准导航对照结果

2026年10月7日。用户授权的新对照已完成。已读本次实施文档、ML013/014/017/018/019；原汇聚/精细绘图记录与所有原地图保留。

{table}

上一轮实际也是UE原生导航，但手工查路径后直接提交。此次使用原控制器标准MoveToLocation：UE寻路、目标投影、完整路径。保存导航阶段只发请求、下一移动帧前主动取消，不能算实际到达；完整覆盖阶段正式盟军/德军模型实际走，使用原生跟路/角色移动、原速300厘米/秒以及对应成功事件、严格站立/误差/重叠/持续0.6秒标准。4项早期加134项，共138项，各一次；银行无未测。这仍仅69个起点，不是全部733900白格都走过。

原保存导航：{sr['occupied_export_tiles']}瓦片/{sr['polygon_count']}多边形，边界中心{sr['bounds_center_cm']}、半范围{sr['bounds_extent_cm']}厘米。临时完整导航：{fr['occupied_export_tiles']}瓦片/{fr['polygon_count']}多边形，中心{fr['bounds_center_cm']}、半范围{fr['bounds_extent_cm']}厘米。半径34/高度193/坡度45/瓦片1000及原碰撞/地形/正式移动参数相同。临时扩大重建改变覆盖及可能的剖分，不是已修复并采用正式保存地图。{coverage_zh} 不能把旧失败都当作地形实质障碍。原保存请求拒绝、完整覆盖后真实到达：盟军{len(gains['allied'])}点、德军{len(gains['german'])}点。余下失败保留，未换点、改速/阈值、重试失败移动。

{budget_zh}

原黑白图和旧条件黑图保留；新各阵营“临时完整导航—本中心”1位黑白图只扣真实负结果的25厘米初始格，不扩大到邻格/瓦片。对照图点色为实际移动结论，示例线为UE请求路径，实际身体轨迹/地面/事件另有完整原始记录。完整楼层、桥专项视觉、返程/全点互达、小队/人群/交火/FPS/MVP及最终任务地点仍未验收。

三个通过准入的入口正常退出0、严格日志0、独立审计通过。失败early_v1同样退出0/日志0但移动0项：编辑器角色碰撞被错误关闭并继承到PIE，全部初始角色下落。ML021保留认证原始证据；新early_v2在PIE前精确恢复六个原开关并验证初始站地，未改几何或移动标准。703项、三个原辅助库、原精细数据、装备/资源/玩家控制及原模型/手指/枪械逻辑保持；未保存地图/包/导航/配置，未拟合资产、提交或发布。私有交付Evidence/UEStandardNavigationV1/artifact_v1_20261007；真实负结果及认证脚本/回执/日志副本在failed_runtime_v1_20261007。后续读ML020/021；资源释放，下次先查实际进程。PIE中GetNumActiveTiles原始计数为0，但实际导出2274/11828个有数据瓦片；上面按原生实际导出计数，原始0计数保留。
'''
    put(D/'UE_STANDARD_NAV_RESULT_20261007.md',en);put(D/'UE_STANDARD_NAV_RESULT_20261007_ZH.md',zh)
    failure=ROOT/'Failures/ML020-20261007-saved-nav-coverage'
    analysis=f'''# Saved navigation coverage versus physical connectivity

7 October2026. Read ML013/14/17/18/19 and UE_STANDARD_NAV_IMPLEMENTATION. Original V1 was native Recast/Detour, not custom bitmap A*. Its42 saved complete-path rejections per role did not establish physical obstruction. New standard AIController requests admit{requests['allied']}/69 Allied and{requests['german']}/69 German in saved scope, without actual travel.

The distinct user-authorized unsaved coverage control keeps the original hub/sources/roles/agent/collision/profile/gates and performs138 standard native physical cases: {json.dumps(counts)}. It observes {json.dumps(reasons)} negatives. Gains from saved rejected requests are {len(gains['allied'])}/{len(gains['german'])}. {coverage_en} {budget_en} It does not isolate which individual missing tile/link or rebuild tessellation change caused each rejection. Never label all rejected native requests universal terrain blockage or merge navigation scopes in a black map.

Actual source/path/travel/arrival negatives retain original native events/ground/support/trajectory. Detailed obstacle causes remain unisolated unless a subsequent bounded diagnosis establishes them. No automatic collision deletion, origin shifts, goal substitution, threshold changes or retries. Old derivatives remain historical hub/saved-scope records; new derivatives mark only current exact role/hub/expanded-scope negative25cm cells. White neighbours remain unmeasured.

Private immutable originals and authenticated copies: Evidence/UEStandardNavigationV1/failed_runtime_v1_20261007. All703/helpers/sources exact; owned exits0/strict log0. Navigation expansion/rebuild is unsaved and unselected, not production repair/adoption; models/fingers/weapons/AI assets untouched. Next production navigation increment requires a distinct documented budget/coverage choice, save/fresh-load and physical control. Never treat node-budget exhaustion as a measured terrain obstacle. No final-site/squad/whole-map/MVP acceptance.
'''
    put(failure/'ANALYSIS.md',analysis);put(failure/'manifest.json',json.dumps({'private_archive':'Evidence/UEStandardNavigationV1/failed_runtime_v1_20261007','manifest_sha256':digest(archive/'manifest.json'),'closure_sha256':digest(P/'closure_v1_20261007.json'),'commercial_bytes_public':False},indent=2)+'\n')
    index=ROOT/'Failures/README.md';text=index.read_text();heading='# 失败案例索引 / Failure case index\n\n';assert text.startswith(heading)
    put(index,text.replace(heading,heading+'7 October standard UE navigation control: [ML020](ML020-20261007-saved-nav-coverage/ANALYSIS.md).\nSaved navigation admission differs from unsaved expanded physical traversal; preserve all raw negatives/scopes.\n\n',1))
    handoff=ROOT/'HANDOFF.md';text=handoff.read_text();head='# Paris Street Combat - new-session handoff\n\n';assert text.startswith(head)
    status=f'''**UEStandardNavigationV1 COMPLETE / native slot RELEASED — 7 October:**
User explicitly authorizes standardUE control of original69 sites/hub. Read
UE_STANDARD_NAV_IMPLEMENTATION/RESULT withZH andML020. Saved standard request-only
admission Allied{requests['allied']}/69/German{requests['german']}/69 (intentionally cancelled, not arrivals).
Unsaved expanded original-model actual138 cases: {json.dumps(counts)};
negative reasons{json.dumps(reasons)}. Four early actual receipts counted once; zero bank unmeasured.
Saved{sr['occupied_export_tiles']}tiles/{sr['polygon_count']}polygons versus expanded{fr['occupied_export_tiles']}/{fr['polygon_count']}.
UseAIController.MoveToLocation, native projection/filter/path/300cm/s/strict35cm+overlap+dwell.
Original blackwhite/old derivatives/evidence retained. New derivatives conditional on expanded/hub/role;
do not infer physical blockage from old saved path negatives or adopt unsaved nav automatically.
703/currenthelpers/finesources/models/fingers/weapons exact; normal exits0/strict log0/audits pass.
No formal save/config/adoption/commit/publication/final mission sites; no return/allpairs/floors/crowd/MVP pass.
Selected private Evidence/UEStandardNavigationV1/artifact_v1_20261007; ML020 authenticates negatives.
All owned engines closed; verify actual process before a writer. Old completed launchers remain locked.

'''
    put(handoff,text.replace(head,head+status,1))
    print(json.dumps({'counts':counts,'saved_requests':requests,'reasons':reasons,'gains':{k:len(v) for k,v in gains.items()},'figure':str(image),'closure_sha256':digest(P/'closure_v1_20261007.json')}))

if __name__=='__main__':main()
