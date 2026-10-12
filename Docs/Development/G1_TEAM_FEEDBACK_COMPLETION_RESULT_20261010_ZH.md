# 组员反馈整合候选与一次性复检

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

route_v4正确执行原UE路线+掩体后搜索，共813个实际样本、47事件。
已真实击杀三守军，存档只在原bridge_transit_complete及两活盟军过桥后开放。
Won两盟军实际Actor X为5842.396/
5701.124cm，均>=5600；原HeldGoal/55cm/
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
| menu_v1 | 25 | v6 production exact; carried receipt, not v9 rerun |
| ammo_v1 | 22 | v6 production exact; carried receipt, not v9 rerun |
| actions_v1 | 25 | current v9 Game native run |
| route_v4 | 47 | current v9 Game native run |
| checkpoint_v1 | 28 | current v9 Game native run |
| restore_v1 | 19 | current v9 Game native run |

v6菜单/弹药证据明确承接；v6->v9只有显式诊断module发生变化，全部生产文件、
菜单/雷达/动作/音频/配置源码精确相同，没有把旧Game收据改标v9重跑。
v9动作实际稳态为walk220/run450/slow65cm每秒；walk倍率1、run1.5，跳跃落地/
蹲伏/按键释放及原地形拒绝通过。具体稳态样本计数在review JSON。

保护审计通过：1,754 native行、三个父源码/Game、Catalog、三个原正常存档目录
精确；六个原资源/存档/启动/导航/AI区段和现有UPROPERTY/UFUNCTION schema精确。
NPC握持/原模型/骨架/权重/动作/材质/枪械native文件和对应源模块均未改变。
普通入口没有自动输入、survey/cause/probe或审计参数，所有诊断进程正常退出，
v7断言失败单独保留，不冒充通过。Development Game-only，没有Editor/recook。
当前验证入口是Game；若之后要进入Editor，须先从本52文件源快照重建Editor。

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

双击 `tmp/Playtest-G1-Completion-candidate_v9-20261010/PLAY_G1_REVISION.cmd`。独立存档 `%LOCALAPPDATA%/ParisStreetCombat/G1Completionv920261010`，
前缀仍为ParisG1PlaytestV5，正常入口不会把测试副本或老存档搬过来。

1. 鼠标/上下/Tab/Enter选菜单并开始，检查进入后鼠标、准星、弹药8+10。
2. WASD、Shift、Alt、Space、Ctrl/Z、R，检查速度手感、脚步对应与HUD/雷达方向。
3. 找到并清除三守军；第三人可能在掩体后，雷达可看现有敌军标记。检查盟军
   分散/编号/圈外方向和真实过桥，不只看玩家到达。
4. G1 secured后进入金圈，站立停稳按E；核对拒绝原因/确认/成功，再F9看原状态
   与静止尸体、F6看新任务8+10。Lost/Error/Exit的实体输入也留给本次统一复验。

本机实体输入、声音/步伐观感、HUD、自然交战和第二台电脑尚未宣称通过。
本轮不改变已选基线、视频、Assignment PDF、SFTP或Git发布状态，也未清理失败证据。

源快照 `Unreal/Variants/G1TeamCompletion20261010/Project`，52文件；authoring为candidate_v9/Project。
Game SHA256 `8e4088d757811446dd923898fd8215194afbccc75f30ee102a19bb5ff77324b4`。
Manifest SHA256 `22bae077bbbcd5809ff9c278e95f5b38284b57463a1b3e1db293208fe3ca1170`。
当前统一索引[CURRENT_TEAM_FEEDBACK_REVIEW.json](CURRENT_TEAM_FEEDBACK_REVIEW.json)；
私有原始记录`tmp/g1-team-completion-20261010`，verification.json记录保护与当前Game收据。
