from prepare import ROOT,OUT,read,write,sha,rows
from pathlib import Path
import json
d=read(OUT/'DELIVERY.json');p=read(OUT/'checks/performance_v16_early/PERFORMANCE_SUMMARY.json')
write(ROOT/'Docs/Development/CURRENT_EQUIPMENT_REVIEW.json',{k:v for k,v in d.items() if k!='normal_files'}|dict(implementation='Docs/Development/MissionLoopV1/TACTICAL_EQUIPMENT_IMPLEMENTATION_20261010_ZH.md',result='Docs/Development/MissionLoopV1/TACTICAL_EQUIPMENT_RESULT_20261011_ZH.md',manual_review='pending',formal_baseline_unchanged=True,editor_pid=50836,editor_project='tmp/g1-tactical-equipment-20261010/candidate_full_v16/Project/WW2FranceLiberation.uproject',explosion_source='https://freesound.org/people/qubodup/sounds/162363/',explosion_sha256=sha(OUT/'intake-explosion/explosion.wav')))
text=f'''# 战术装备统一试玩结果

2026-10-11。本机功能候选已完成，等待用户统一人工试玩；正式 enemy-clear v3 和其用户存档继续保留。本轮按实施文档顺序集成手榴弹、烟雾弹、预设敌方陷阱、弹药补给，没有增加NPC或新任务阶段。

## 入口与身份

- 根入口 `PLAY_TACTICAL_EQUIPMENT.cmd`；正常目录 `{d['playable_directory']}`。Enter开始任务。
- Game SHA-256 `{d['game_sha256']}`。
- {d['source_files']}文件独立源 `{d['source_snapshot']}`；manifest `{d['source_manifest_sha256']}`。
- 配套 authoring/Editor：`tmp/g1-tactical-equipment-20261010/candidate_full_v16/Project`。
- 独立UserDir `G1TacticalEquipment20261010`，prefix `ParisEquipmentV1`，不移入原正常用户档。
- 正常入口没有观察器、诊断摆位、自动输入、solo或AI hold。画质2/1080p/原D3D12，启动通过官方DPCVars提前应用同一配置；正常入口不限制最高帧数。

## 四种机制

| 项目 | 本轮实现与操作 |
|---|---|
| 手榴弹 | 开局2颗；按住G准备，松开投掷，提交前Esc取消不扣库存。现有兼容投掷动画、唯一释放、UE实际碰撞sweep、3.5秒释放后引信；6米爆炸范围，伤害衰减与三条实际遮挡采样；玩家和盟军可受伤。NPC可见危险后走有正式胶囊净空的原生路径，有限间隔后恢复原行为。 |
| 烟雾弹 | 开局2颗；Q准备/松开投掷。2秒展开、18秒有限寿命，后段消散；同一浓度控制视觉、双方感知与敌军雷达过滤。保留最后所见记忆；原子弹仍可穿烟命中；消散后原生感知重新发现。复用已有烟图集/已cook输入和transient材质，中央目标的头/上身细节被浓烟遮住，边缘可能有低对比轮廓。 |
| 敌方陷阱 | 固定2处，在侧路；观察发现、可绕过，近距离瞄准后按住E两秒拆除。松开/移动/Esc取消保持武装；玩家或盟军真实接触只触发一次。German不触发自己的装置；装置不加入敌军名册，不额外锁保存。 |
| 弹药箱 | 现有弹药箱资产，固定2处各16发；近距离瞄准按E只增加备用弹药。保持当前装填、射击次数和原换弹事务；箱耗尽后重复E不给资源，备用容量64。 |

两处补给位于起始岸路边和桥后路边。精确原生世界厘米坐标：Supply1=(1812.5,-21162.5)，Supply2=(6062.5,-20462.5)；Trap1=(6637.5,-20137.5)，Trap2=(7637.5,-20487.5)。它们只取自25cm规划后实际simple地面、正式胶囊与完整UE路径验收，不沿用1米粗图。原生G1完整路线与两处陷阱有至少100cm距离，装置不在存档圈内，也没有改变地图或NavMesh。

手榴弹/烟罐/陷阱首轮使用简单临时几何，保留人物、手指与步枪；不是新精细美术资产通过。爆炸声采用[qubodup的CC0录制](https://freesound.org/people/qubodup/sounds/162363/)官方预览适配，48kHz单声道PCM，SHA `{sha(OUT/'intake-explosion/explosion.wav')}`；不标成精确二战手榴弹录音。既有33音效与M1/K98原逻辑保持。

## 验收边界与原证据

v15_early 真实原生运行通过10项未改机制：投掷/取消/恢复持枪、真实引信/自伤、墙体遮挡、NPC避险、盟军触发陷阱、拆除/补给、设施通路、菜单、清场保存/真实写盘失败重试/F9/F6、原弹药与雷达。避险实际位移336.345cm，结束恢复原Brain；装填8/备用10/总量18保持，有限补给后8/26/总量34，额外一发严格拒绝。已检查准备与取消后实际画面；持枪finger error约0.000003415度、HoldingAlpha1。未扩大为全部近墙动作/全手部接触美术验收。

v16只把烟实例材质Opacity1改为3，其他60源文件逐字一致；不能把旧检查改称新Game实跑。受这行影响的5项在v16_early再次实际运行：浓烟/双向感知/记忆/原射击伤害/消散，实际保存活弹体与烟幕，跨进程F9，原V5复制档兼容，当前人数组合性能。保留每项Game/结果SHA与承接标记，见CURRENT_EQUIPMENT_REVIEW.json。135粒子/6x6图集/alpha约0.595/材质Opacity3及实际烟幕图已复看；不以粒子计数代替外观。

原敌军完全消灭是唯一任务/存档解锁条件；原圈内主动E、成功窗口、双槽序号、schema、checksum、实际写盘和readback保持。装备状态在同一校验载荷：库存/提交次数、箱库存与有限增量、稳定陷阱身份、活弹体位置速度/年龄剩余引信、烟位置剩余寿命。旧档只复制到隔离测试目录；旧档不给免费新装备/弹药。严格负向拒绝额外弹药、库存不守恒、错误配置、错误引信、重复弹体、错误陷阱ID及移除扩展后额外资源。新进程恢复不重置引信/烟寿命、不返还投掷物、不重领箱、不重放尸体死亡动作。

最终保护通过：1,754 native文件、原52源、原Game、Catalog及原正常用户4文件逐字不变；既有UPROPERTY/UFUNCTION布局保持，新增独立感知桥类；持枪/手指/动作/声音及原资源、存档写盘、任务门槛保持。旧小队路径算法逐字保留，仅有限装备导航所有权期间让桥接hook让出控制；结束恢复。没有修改原BT/导航/碰撞资产。

## 当前人数性能

i9-12900F / RTX3080 / 32GB。本轮原六角色、普通AI、真实G/Q输入，未摆位/暂停AI/新增NPC。1080p画质2、诊断上限60FPS，Editor保持开启；16游戏秒流程在1秒后采890点，其中552点有烟。平均59.96FPS，墙钟帧平均16.68ms/P95 18.65ms，GPU平均8.64ms；有烟阶段平均59.95FPS/GPU8.61ms。GPU和Game/Draw是UE全局导出计数，不能按当帧壁钟一一对应或当作CPU利用率。

Game计数包含260.09ms最大值，保留，没有筛掉；加载与Editor启动会影响这段短测。不是完整自然遭遇、大量NPC/第二台机器或长期稳定性通过。性能原始工况以PERFORMANCE.json.scope为准；RESULT共用scope字符串误写隔离流程，另附SCOPE_CORRECTION，原件不改。

## 失败与引擎状态

MI024–MI028均保留：早于正式第一人称Initialized的无效画面、点位复杂碰撞误当实际支撑、诊断相机/AI/数组构造错误、烟图集/材质倍率和序列化限制、小队路径被停止、原启动首帧质量3以及未确定根因的GPU hang。DPCVars修正后完成本轮真实检查，不能宣称GPU挂起已根治；旧dump和失败结果保持。

匹配v16 Editor构建通过，PID50836已加载Engine Entry并初始化，保持开启；原PID51148仍保持，原Zen等待状态未自动终止。只读素材审计commandlet正常自行退出；独立Game探针正常自行结束，以便验证真正的新进程恢复。本轮没有PIE或native保存/recook；既有AV的Editor音频路径仍需后续独立入口适配，不能拿打包Game音频通过冒称PIE通过。

用户人工试玩后才选新正式基线。本轮未commit/push、SFTP同步或清理失败/历史文件。
'''
(ROOT/'Docs/Development/MissionLoopV1/TACTICAL_EQUIPMENT_RESULT_20261011_ZH.md').write_text(text,encoding='utf-8')
(ROOT/'Docs/Development/CURRENT_EQUIPMENT_REVIEW.md').write_text('''# 当前战术装备试玩候选

2026-10-11，统一功能候选，等待人工试玩。入口 `PLAY_TACTICAL_EQUIPMENT.cmd`。

G/Q按住准备、松开投掷；提交前Esc取消。地面敌方陷阱瞄准后按住E两秒拆除；弹药箱近距离瞄准按E领取。原三个德军全灭解锁圈内E保存、F9/F6保留。

对应身份见 CURRENT_EQUIPMENT_REVIEW.json；详细结果见 [实施结果](MissionLoopV1/TACTICAL_EQUIPMENT_RESULT_20261011_ZH.md)。正式基线仍为 enemy-clear v3，原正常存档没有迁入或覆盖。匹配Editor保持开启；无自动发布/清理。
''',encoding='utf-8')
for identity in ['performance_v15_early','performance_v16_early']:
    write(OUT/'checks'/identity/'SCOPE_CORRECTION.json',dict(mode='performance',scope='normal AI/current six actors/no relocation or brain hold/real G-Q input; authoritative PERFORMANCE.json.scope',reason='Generic FinishCheck RESULT.scope string describes other fixtures and is inaccurate for this distinct branch; original result kept',result_sha256=sha(OUT/'checks'/identity/'RESULT.json')))
print('Review identity and Chinese result documented; original performance receipt kept with explicit scope correction')
