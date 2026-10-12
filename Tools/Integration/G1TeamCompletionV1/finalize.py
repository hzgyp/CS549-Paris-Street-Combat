"""Write one unselected human-review handoff after verified native runs."""
import json,math
from pathlib import Path
from prepare import ROOT,OUT,SOURCE,load,sha

def main():
    r=load(OUT/'RUNTIME.json');v=load(OUT/'verification.json')
    assert r['revision']=='candidate_v9' and v['status']=='pass_fixed_layout_and_p0_p1_native_checks_pending_manual_review'
    assert r['game_sha256']==v['game_sha256'] and r['source_manifest_sha256']==v['source_manifest_sha256']
    route=load(OUT/'checks/route_v4/result.json');actions=load(OUT/'checks/actions_v1/result.json')
    stats={}
    for step,expected in [('walk',220),('run',450),('slow',65)]:
        samples=[s for s in actions['samples'] if s['step']==step]
        steady=[s for s in samples if abs(s['speed']-expected)<2]
        assert steady and abs(samples[-1]['speed']-expected)<2
        assert all(abs(s['animation_rate']-(1.5 if step=='run' else 1))<.03 for s in steady)
        stats[step]=dict(target_cm_s=expected,steady_samples=len(steady),steady_peak_cm_s=max(s['speed'] for s in steady))
    docdir=ROOT/'Docs/Development';report=docdir/'G1_TEAM_FEEDBACK_COMPLETION_RESULT_20261010_ZH.md'
    manifest=SOURCE.parent/'SOURCE_MANIFEST.json';entry=Path(r['path'])/'PLAY_G1_REVISION.cmd'
    source_rel=SOURCE.relative_to(ROOT).as_posix();entry_rel=entry.relative_to(ROOT).as_posix()
    review=dict(schema_version=1,date='2026-10-10',review_id='g1-team-feedback-completion-v9-20261010',status=v['status'],selection='Unselected single human-review candidate; selected audio V2 retained',parent_review='CURRENT_TEAM_FEEDBACK_P1_REVIEW.json',selected_baseline='CURRENT_DEVELOPMENT_BASELINE.json',plan='G1_TEAM_FEEDBACK_COMPLETION_IMPLEMENTATION_20261010_ZH.md',result=report.name,compatibility='G1_TEAM_FEEDBACK_P2_COMPATIBILITY_20261010_ZH.md',source_snapshot=source_rel,source_files=52,source_manifest=manifest.relative_to(ROOT).as_posix(),source_manifest_sha256=r['source_manifest_sha256'],active_authoring_project='tmp/g1-team-completion-20261010/candidate_v9/Project/WW2FranceLiberation.uproject',playable_directory=Path(r['path']).relative_to(ROOT).as_posix(),playable_entry=entry_rel,game_sha256=r['game_sha256'],save_directory='%LOCALAPPDATA%/ParisStreetCombat/'+r['user_directory'],save_prefix='ParisG1PlaytestV5',speed_preset_m_s=dict(walk=2.2,run=4.5,slow=.65),fresh_ammo=dict(loaded=8,reserve=10,total=18),verified_runs=v['verified_runs'],actual_speed=stats,actual_initial_actor_locations=v['actual_initial_actor_locations'],won_allies_actual_locations=v['won_allies_actual_locations'],private_verification='tmp/g1-team-completion-20261010/verification.json',native_guards=1754,failures='Failures/MI021-20261010-full-space-completion/FAILURE_ANALYSIS.md',remaining=['ADS and M1 en-bloc/mechanism/remaining reload sleeve visuals not implemented; compatible assets/adaptation decision required','Positive 200cm prone crawl not accepted; original road support edge refused, thresholds/world collision preserved','Physical mouse/keyboard, HUD, foot/audio cadence, Lost/Error/Exit and second-machine follow-up'],test_scope='Opt-in simulated UE inputs and actual native navigation/physical movement/visible original weapon fire. Covering route is explicit, not natural tactical encounter or human acceptance.',publication='No baseline adoption, Git/SFTP/video/PDF publication or cleanup in this round')
    (docdir/'CURRENT_TEAM_FEEDBACK_REVIEW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    evidence='\n'.join(f"| {key} | {val['checks']} | {val['scope']} |" for key,val in v['verified_runs'].items())
    waypoints=[e['event'] for e in route['events'] if e['event'].startswith('search_waypoint_')]
    result=f'''# 组员反馈整合候选与一次性复检

2026-10-10。本轮可在保护约束内实施的P0/P1已经整合并通过本机原生Game回归，
候选v9等待用户一次性人工复验；没有选择为正式开发基线。已选audio V2和P0/P1
父候选、原模型/手指/枪械逻辑、原存档保持。不能将此文读成八项表现全部完成。

依据与变化见[实施文档](G1_TEAM_FEEDBACK_COMPLETION_IMPLEMENTATION_20261010_ZH.md)。
已读AGENTS/HANDOFF/当前selectors、Jingdi八项及Failures/README，MI005/006/
014/015/016/019/020/021和AN003/AN005；本次先完整测空间，再固定布局、实际通行。
早期门槛是全五角色胶囊/地面/完整路径/间距和原落地装备；任何guard/资源/
模型/导航退化停止，未放宽阈值或自动换点。失败收据均保留在MI021所列私有路径。

## 与八项反馈对应

| Jingdi项 | 本轮整合状态 |
|---|---|
| 1 满装M1 | 新任务/F6为8+10，总量18；旧档恢复保存值，不补弹 |
| 2 菜单选择 | 鼠标、上下/Tab/Enter、禁用原因、进入后无菜单误射，原P0实现保留 |
| 3 玩家中心雷达 | 地图滚动、同一比例/朝向、已测绘边缘与圈外方向，原P1实现保留 |
| 4 步行/跑步 | 用户选择2.2/4.5米每秒，静步0.65；本机实际运动与稳态倍率通过 |
| 5 准星/ADS | 绿色黑描边准星已做；ADS未实施，不能以缩FOV冒充 |
| 6 M1换弹 | 既有事务/动作保持；八发弹夹、机件、剩余衣袖遮挡未修，见兼容性文档 |
| 7 E存档 | 取消/圈外/移动/不安全原因、明确确认、写盘/readback、F9/旧V5恢复通过 |
| 8 NPC分散/盟军 | 四个已测新点+原A2；真实清除三守军、两活盟军过桥与原到达旗标通过；编号/距离/圈外提示保留 |

## 实际空间和任务证据

固定测量2205个NPC格及289条匍匐走廊。A1/D1/D2/D3完整准入341/169/94/88；
A2新区域为0，匍匐有46条静态全足迹通过但到起点路径均不完整，保持不准入。
独立paths_v1证实原A2->FarBank/原A1完整，新A2/首匍匐格为partial，投影后仍失败。

新布局A1(1512.5,-21462.5)、原A2(1487.5,-20837.5)、D1(6612.5,-20662.5)、
D2(7387.5,-19937.5)、D3(7738.631,-21337.367)，XY单位cm；Z仍由原Nav/真实地面/
胶囊高度决定。入场后两盟军间约625.50cm，玩家到两盟军约894.43/459.62cm，
守军最小间距约1061.25cm。五点通过才移动四人，A2原变换保持；原role配置函数
同步新准备期位置，原AI/目标跟随算法不变，原落地/EquipmentReady再次通过才Ready。
ParisLoad完全跳过新布局，恢复旧保存的位置；F6从同一新配置开始。

route_v4正确执行原UE路线+掩体后搜索，共{len(route['samples'])}个实际样本、47事件。
已真实击杀三守军，存档只在原bridge_transit_complete及两活盟军过桥后开放。
Won两盟军实际Actor X为{v['won_allies_actual_locations']['Ally1'][0]:.3f}/
{v['won_allies_actual_locations']['Ally2'][0]:.3f}cm，均>=5600；原HeldGoal/55cm/
SquadFailed和完成旗标保留。掩体后实际搜索使用完整原玩家agent路径，原eye/
muzzle/barrel/camera判定和射击输入；三守军清除后返回G1。搜索前用原R正常换弹，
没有传送、自动伤害、血量/弹药/AI改写，所有样本Loaded+Reserve+Shots=18。
这些是指定路线可完成证明，不是自然战术遭遇或人工试玩结论。

E取消/离圈不保存，移动确认拒绝，站稳后一次明确确认写盘；F9新地图首帧和
之后3秒三尸体保持终态，F6复位任务/资源。旧V5副本的E负例/磁盘失败重试/
再次保存28项、新进程恢复19项通过，六角色class/血量/死亡/弹药/射击计数相同、
位置误差<0.001cm，serial2。诊断使用独立UserDir/前缀，旧正常用户文件未改。

| 证据身份 | 检查/事件数 | 身份范围 |
|---|---|---|
{evidence}

v6菜单/弹药证据明确承接；v6->v9只有显式诊断module发生变化，全部生产文件、
菜单/雷达/动作/音频/配置源码精确相同，没有把旧Game收据改标v9重跑。
v9动作实际稳态为walk220/run450/slow65cm每秒；walk倍率1、run1.5，跳跃落地/
蹲伏/按键释放及原地形拒绝通过。具体稳态样本计数在review JSON。

保护审计通过：1,754 native行、三个父源码/Game、Catalog、三个原正常存档目录
精确；六个原资源/存档/启动/导航/AI区段和现有UPROPERTY/UFUNCTION schema精确。
NPC握持/原模型/骨架/权重/动作/材质/枪械native文件和对应源模块均未改变。
普通入口没有自动输入、survey/cause/probe或审计参数，所有诊断进程正常退出，
v7断言失败单独保留，不冒充通过。Development Game-only，没有Editor/recook。

## 明确未完成与失败经验

匍匐prone_cause_v3只完成原因观察：控制点前进1.568893cm后BP拒绝，盒子清空、
不是自身枪体；道路中心支撑normalZ0.141258，不满足原>=0.97，前后支撑通过。
这是同位置事后重查，与原拒绝相符；保留原碰撞/支撑阈值，停止该控制点。
正向200cm爬行仍未验收，需要新的完整可达足迹走廊，不能改阈值或循环挪锚点。

ADS、M1 en-bloc弹夹/机件与衣袖表现仍未做。[P2兼容性记录](G1_TEAM_FEEDBACK_P2_COMPATIBILITY_20261010_ZH.md)
清点590供应商文件，现有通用动作/单骨骼刚体枪没有已验证的兼容组合。保留
AN003/AN005停止决定，不重启手指/权重/绑定失败路线，不自动采购或改正式模型。
后续需要选择许可兼容资产或专业有限适配；当前实现不能说成真实M1换弹/ADS。

旧直线route_v1到G1但未绕掩体找第三人，240秒失败；v7漏注册诊断白名单而
启动断言退出3；v8漏preload分派而走入步行、真实被杀；都保留原结果。
v9逐项核对所有模式分支后，使用新route_v4通过，点位/普通玩法没有为测试挪动。
见[MI021](../../Failures/MI021-20261010-full-space-completion/FAILURE_ANALYSIS.md)。

## 一次性人工复检入口

双击 `{entry_rel}`。独立存档 `%LOCALAPPDATA%/ParisStreetCombat/{r['user_directory']}`，
前缀仍为ParisG1PlaytestV5，正常入口不会把测试副本或老存档搬过来。

1. 鼠标/上下/Tab/Enter选菜单并开始，检查进入后鼠标、准星、弹药8+10。
2. WASD、Shift、Alt、Space、Ctrl/Z、R，检查速度手感、脚步对应与HUD/雷达方向。
3. 找到并清除三守军；第三人可能在掩体后，雷达可看现有敌军标记。检查盟军
   分散/编号/圈外方向和真实过桥，不只看玩家到达。
4. G1 secured后进入金圈，站立停稳按E；核对拒绝原因/确认/成功，再F9看原状态
   与静止尸体、F6看新任务8+10。Lost/Error/Exit的实体输入也留给本次统一复验。

本机实体输入、声音/步伐观感、HUD、自然交战和第二台电脑尚未宣称通过。
本轮不改变已选基线、视频、Assignment PDF、SFTP或Git发布状态，也未清理失败证据。

源快照 `{source_rel}`，52文件；authoring为candidate_v9/Project。
Game SHA256 `{r['game_sha256']}`。
Manifest SHA256 `{r['source_manifest_sha256']}`。
当前统一索引[CURRENT_TEAM_FEEDBACK_REVIEW.json](CURRENT_TEAM_FEEDBACK_REVIEW.json)；
私有原始记录`tmp/g1-team-completion-20261010`，verification.json记录保护与当前Game收据。
'''
    report.write_text(result,encoding='utf-8')
    quick=f'''# 当前统一人工复检候选

2026-10-10，G1 team-feedback completion v9，**等待人工复验，未选择为正式基线**。

入口：`{entry_rel}`。独立存档：`%LOCALAPPDATA%/ParisStreetCombat/{r['user_directory']}`。

已整合菜单/E、8+10装载、2.2/4.5米每秒、玩家中心雷达/盟军方向/准星，以及
四个新NPC位置+原A2。实际清场三守军、两盟军过桥、E/F9/F6和旧V5跨进程恢复
通过本机有限原生检查。保护审计1754行/父源码与存档/原反射和事务通过。

ADS/M1弹夹机件/剩余衣袖与200cm正向匍匐没有验收完成；实体输入/HUD/音频/
自然交战及第二台电脑待复验。详见[统一结果与检查步骤]({report.name})、
[实施文档](G1_TEAM_FEEDBACK_COMPLETION_IMPLEMENTATION_20261010_ZH.md)与
[机器索引](CURRENT_TEAM_FEEDBACK_REVIEW.json)。

旧P0/P1索引和正式audio V2是保护父项；本候选是本轮一次性人工检查入口。
不把本地诊断通过当成人工接受/完整性能/全接触/课程再验收，也不自动发布或清理。
'''
    (docdir/'CURRENT_TEAM_FEEDBACK_REVIEW.md').write_text(quick,encoding='utf-8')
    (Path(r['path'])/'README_TEAM_FEEDBACK.md').write_text(quick.replace(f'({report.name})',f'({report.as_posix()})'),encoding='utf-8')
    (Path(r['path'])/'README_P1.md').write_text('''# Unified review entry

This directory is G1 completion candidate_v9, not the old P1 candidate_v9.
Read README_TEAM_FEEDBACK.md for the current roster, checks and known gaps.
PLAY_G1_REVISION.cmd has only normal user controls and an independent save root.
''',encoding='utf-8')
    handoff=ROOT/'HANDOFF.md';prefix=f'''## 2026-10-10：组员反馈统一候选收尾（未正式选定）

用户要求按文档实施，完成后一次性人工检查。最新统一候选是
`{entry_rel}`，Game `{r['game_sha256']}`；52文件快照
`{source_rel}`，manifest `{r['source_manifest_sha256']}`，authoring
`tmp/g1-team-completion-20261010/candidate_v9/Project`。
先读`Docs/Development/CURRENT_TEAM_FEEDBACK_REVIEW.json/.md`、completion实施/结果、
P2兼容性与MI021，再读下方历史。P0/P1、四个测量点+原A2已整合，本机真实清场/
两活盟军过桥/E/F9/F6/旧V5跨进程和速度动作通过；1754native/全部父源/Game/
原存档与反射/原资源保存AI导航区段保护通过。菜单/弹药v6明确承接，其他v9原生运行。

ADS/M1弹夹机件/剩余衣袖仍是资产适配缺口；正向200cm匍匐未通过，控制点道路
支撑normal0.141258合法拒绝，原阈值和碰撞保持。实体输入、HUD/脚步音频观感、
自然交战/终态菜单/第二台电脑待本轮人工复验。失败identity保留，禁止循环旧锚点/
扩大豁免/恢复AN003/AN005或详细人物路线。选定audio V2仍不变，不自动发布或清理。
所有诊断引擎已退出；后续启动/写入前仍检查实际进程，保护用户接管的预览。

'''
    assert prefix.splitlines()[0] not in handoff.read_text(encoding='utf-8-sig')
    handoff.write_text(prefix+handoff.read_text(encoding='utf-8-sig'),encoding='utf-8')
    baseline=docdir/'CURRENT_DEVELOPMENT_BASELINE.md';note='''## 2026-10-10 统一人工复检候选（不改变selected JSON）

本轮最新未选定入口见[CURRENT_TEAM_FEEDBACK_REVIEW](CURRENT_TEAM_FEEDBACK_REVIEW.md)，
G1TeamCompletion candidate_v9；P0/P1、新布局与实际清场/小队/存档回归通过。
ADS/M1换弹资产与正向匍匐仍未完成，人工复验待完成。selected audio V2仍是正式
保护父项，旧P0/P1候选资料保留。实施/保护/停止条件和MI021均需先读，不能以
旧P1索引代替此次统一候选，也不能自动adopt/publish/cleanup。

'''
    baseline.write_text(note+baseline.read_text(encoding='utf-8-sig'),encoding='utf-8')
    print(json.dumps(dict(status='single_unselected_review_handoff_written',entry=entry_rel,report=report.relative_to(ROOT).as_posix(),game_sha256=r['game_sha256'],source_manifest_sha256=r['source_manifest_sha256'],speed=stats),ensure_ascii=False))

if __name__=='__main__':main()
