# NPC Interaction V1 — B窗口检查点

## 最新验证：2026-10-05，本轮持续修复

用户明确允许目标内中间错误继续修复；旧文中的单次失败/作者API失败即暂停规则不再
作为整轮终点。下方为保留的历史，不覆盖本节的新验证。

- `sight_causal_v1`实测原场景LOS首先被与观察者重叠的`PC_City_Ally1`阻挡；清理测试
  遮挡后，同一SightV4资产原生事件/BB获取敌军、丢视线记忆不变。此前“Controller归属
  导致失败”的判断无证据，UE源码支持Controller/Pawn两种归属，予以纠正。
- `sight_verified_v1`新进程、不挂Python监听：友军单独0.75秒不获取；敌军真实LOS获取；
  两个BB实例独立；移走70.71米后1.25秒visible=false/记忆变化0cm。558项精确。
- `behavior_runtime_v3`实测原生BT守卫/完整路径巡逻往返/有限重规划/死亡恢复：守卫
  全程漂移0cm，回家XY误差23.7030cm（≤50），最大步行300cm/s；不可达目标RetryCount
  封顶2/PathExhausted，等待时不再请求；原PC_ApplyDamage死亡→Move idle/RequestID0/
  清目标/漂移0cm；原PC_ResetLifecycle→generation1/旧请求0/漂移0cm。571项精确。
- 10项离线合同测试通过，新增BT换TaskID预算不重置与恢复清感知/追击两反例。
- `search_runtime_v2`三德军实际城市非战斗通过：各自抵达5个点，开始3.8587s、结束
  17.3305s、固定deadline18.8215s；隐藏目标移动后记忆不变，两个守卫回家误差
  38.0049/32.7434cm，第三名恢复RolePatrol；无枪原开火请求不耗弹/不伤目标。581项精确。

- `squad_runtime_v5`实际双盟军：身体到点误差45.6189/31.0632cm，预约点间距372.1346cm；
  待机和原换弹期间不释放，弹药守恒；真实换敌保持同episode及累计距离，目击敌军死亡
  清目标/记忆，实际归队后死亡释放自己的槽且存活者槽/RID不变，原恢复生成新预约。
  追击样本峰值267.8745/262.3908cm，所有样本满足10m约束；没有跑到预算极限，不能
  当作极限压力证据。固定同两人/起点/点池/RVO对照：协作1.812s、独立1.687s，独立
  0失败；协作并未更快，不能声称协作优越或拥挤全城通过。606项精确/进程exit0。
- `combat_regression_v5`真实城市1玩家+2盟军+3德军，21次原接口射击：每类射手两模式
  中，活友军始终挡住后方敌军，OFF不扣血/ON正常35扣一次；敌军35，墙挡不伤任何人；
  原冷却拒绝即时重复，原换弹后Loaded+Reserve+ShotSequence=18，死亡胶囊NoCollision/
  不再次死亡。桥接建图插件通过命令行关闭并反射确认，原FP runtime模块不关。606项
  精确/进程exit0。这是直接事务回归，不是NPC自主战斗或接触验收。
- `action_gate_runtime_v1`使用ActionGateV4、桥接插件关闭：旧generation/Task/Request、
  无枪/未验/等待握枪人审请求均拒绝且不耗弹；实际移动后Stop的16个连续样本漂移0cm。
  相同请求不重启、同身份不同动作拒绝、插入忙请求的拒绝后完成反馈仍带原身份；原
  死亡/恢复/原生树重评估产生的真实Task变更取消旧请求。五项检查通过，611项精确/
  exit0。Fire/Reload合法分支没有启用或通过装备人审，不把停止接口通过当完整B4。

父类骨骼/模型/枪/AnimBP/玩家/正式地图/Catalog不改；共享友伤修改得到用户明确授权，
只有一个共享Combatant文件通过两个路径别名变化，原始300043bytes/
`892836f8a7f39a3a4bc23ce799cd6b9c89c1a7ccdbe5f409927fd98100b142de`，当前327903bytes/
`dc2f8fc2da7653bc4eaa53015c96e1bbab24aa4dd6afbc77cc2a398a8c824f5d`。
备份和[明确授权变更账本](AUTHORIZED_SHARED_MUTATIONS_20261005.json)保留；其余553个
批准旧行精确，555快照不重写、不回滚A采用；67个B包包含旧11个已在555行的包、
早期失败/未选择包。最终保护为611行（555+56），`final_20261005_v1`全部精确；
67个本地包全部登记，没有未登记文件。10项单测、Python全目录编译、PS解析通过；
本窗口47个代码/文档文件独立空白检查通过。全仓检查发现其他窗口/既有
DefaultEditor.ini末尾空行，未修改，不把全仓检查报成通过。

所有任务自有UE进程已正常关闭、实际UE进程0，本窗口释放原生时段。无用户编辑器被
关闭。下一writer须明确采用611行及友伤变更账本，不能继续用旧555行误判后回滚。
远端[现有native清单](../../../Assets/Sync/manifests/paris-gameplay-native-playtest.json)
仍记录旧基类892836...，不包含本轮B包/友伤改动；未更新或再次发布，不能用旧恢复
清单覆盖当前已授权本地基类。后续发布/合并应另走相应授权和验证。

用户最新答复明确要求“等我标注握枪后再启用自动战斗”：本轮不启用NPC自主开火/换弹，
EquipmentHumanAccepted保持false，源握枪/手指/素材不修不采用。直接回归的盟军装备
精确复用同阵营PC_City_Ally1的实例配置，德军用已有nativeV2；不复制玩家数字、不算
最终握枪接受。B1/B2/B3上述数值子门禁通过；B4接触/完整自主动作、B5六人自主交互、
友军枪线AI避让、步态视觉/预算极限/近墙/全城压力/FPS/Shipping/第二机器仍未通过。
无正式地图保存/采用/新Catalog发布/commit/push，不能说NPC AI或课程MVP整体完成。

## 历史检查点（旧失败原因和保护数量已被上文的实际验证纠正）

2026-10-05更新。本记录是有界检查点：**B0通过；B1停止／防重发子门禁通过，但原生
视野未通过，NPC AI尚未完成**。Lane A正式采用后，当前权威保护为V21快照555项，
其中包含全部11个NPC草稿以及获准变化后的正式地图／Catalog。所有B任务进程已结束；
Lane B本轮未保存正式地图。

## 2026-10-05 B1继续结果

- `b1_stop_v2`在真实城市实际移动101.7653厘米后，先停止Brain/BT再停止移动；随后
  0.75秒5个连续样本的最大漂移为0.0厘米、速度为0，RestoreGeneration变为2且
  RequestID清零。它关闭了V1的循环树重发原因，但不代表B1整体完成。
- `b1_sight_author_v2`新建3个SightV1包；`b1_sight_runtime_v2`真实城市运行4秒始终
  `TargetActor=null`、`HasVisibleTarget=false`。原因定位为V1把PawnSensing放在
  AIController而不是被控制Pawn；531项保护不变，失败保留且没有位置扫描／延时重试。
- 修正路径先保存了新的`BP_PCNPCControllerSightV2`，随后在Pawn图创建Controller cast
  节点时停止；该单个未选择包纳入保护。下一次V3只尝试从图上下文查询真实cast type id，
  但当前UE Python环境没有`editor_toolset`模块，脚本在创建任何V3包前失败。任务自己的
  UE进程由4分钟上限关闭。依据预写停止条件，不做第三种作者绕行，也不进入B2-B5。
- `final_b1_v3_stop_audit`确认532项大小/SHA全部一致、TeamId仍为0/1、四个共享事务入口
  仍存在、UE进程为0。此结果不是感知、战斗、地图、打包或课程验收。
- 用户随后明确要求先修复Python工具链。`ue_python_tooling_v1`证明当前实际执行环境为
  UE内置Python 3.11.8，入口进程是`UnrealEditor.exe`；未启用的`editor_toolset`确实不可
  导入，但底层图API列出39921个节点，能用空上下文创建`CastToActor`、重定向到SightV2
  Controller并立即删除。532项保护不变、未保存资产／地图。作者源码已移除不必要的
  `editor_toolset`依赖并采用该已验证调用；NPC资产作者和城市测试尚未恢复。
- 用户批准后执行`b1_sight_author_v5`。经修复的Cast节点成功创建并重定向，证明Python
  工具问题已解除；随后Pawn图用裸函数名创建跨蓝图`PC_RecordSight`调用节点时返回空。
  作者门禁因此在保存Pawn前停止，只留下新的未选择SightV3 Controller；两个SightV3
  Pawn和城市测试均未产生。该Controller现登记为第533项保护文件。失败是跨蓝图函数
  调用节点需要可解析的真实type id／declaring class，不是原生视野运行失败。
- 最新V21正式采用后，Lane B已从旧533项切换到`FirstPersonFormalV21/selected_v1`的555项
  当前epoch，全部精确匹配；旧地图／Catalog哈希只作历史记录。
- `cross_blueprint_call_v1`找到真实`CallFunction|PCRecordSight`，但V3函数未公开时，即使
  显式declaring class也不能在Pawn图创建节点。`cross_blueprint_public_call_v1`随后只在
  内存中将函数设为public并编译，成功得到
  `Class|BPPCNPCControllerSightV3|PCRecordSight`，其pin为execute/self/SeenPawn/then；
  节点立即删除、未保存资产／地图、555项不变。这证明下一作者机制，但根据并行窗口最新
  人审顺序，暂不写Controller/Pawn/BT/BB，先等待NPC贴图三视图和用户标注。

## 最新原生结果

- `b0_author_v2`在保存前因UE5.8未导出Object键`base_class`停止，522项不变；移除非必要
  Actor类型收窄后，`b0_author_v3`成功新建5个未选中B0包：17键BB、真实Selector＋Wait
  BT、共享AI Controller，以及继承现有盟／德类的两个试验子类。
- `b0_runtime_v1`因地图加载期间Slate tick重入而重复调用`load_level`，180秒超时；启动器
  终止本任务PID，527项不变。一次测试器修正先切换`loading`阶段。
- `b0_runtime_v2`在新进程、正式城市未保存PIE中通过：两个盟军Controller和Blackboard
  实例不同、两者运行同一真实BT；只写A的最后目击后移动隐藏目标，A记忆不变，B仍未设置。
- `b1_author_v1`因UE5.8的WaitTime为结构体而在保存前停止；保留默认等待后，
  `b1_author_v2`新建真实Sequence→`BTTask_MoveTo(DesiredPosition)`→Wait树。
- `b1_runtime_v1`真实移动292.0697厘米、9个连续样本、最大段48.4868厘米；进入120厘米
  到达阈值后调用`StopMovement`，0.75秒内身体仍漂移43.5573厘米，超过1厘米门槛。
  这命中“停止／成功状态下身体仍移动”的明确停止条件；上方B1-V2已修复该子问题，
  但感知仍失败，因此B1仍未完成，未进入B2–B5。

历史`final_native_checkpoint_v1`确认当时528项大小/SHA完全一致、UE进程0；旧地图SHA
`2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`已由获准V21正式采用
取代，当前地图SHA为`f2aeac69bd17ace4a76057e8d2ab89cc6f0b087e76900406bdff74f38b7b4020`。
当前14个NPC新包均为
未选中诊断draft，清单见`NPC_INTERACTION_V1_DRAFT_INVENTORY_20261004.json`；不是Catalog、
release、恢复权限或AI完成证明。没有自动commit/push。

## SightV4作者与运行结果（2026-10-05）

用户暂停另一窗口后明确恢复本窗口。`b1_sight_author_v6`在V21当前555项基线上通过：
全新SightV4 Controller、盟军Pawn、德军Pawn均编译无图错误；Pawn各自拥有
PawnSensing，`OnSeePawn`通过public类函数节点连接`PC_RecordSight`，旧555项不变、地图
未保存。三个文件登记后当前保护数为558。

唯一真实城市测试`b1_sight_runtime_v4`按原固定布局运行：盟军观察者、250厘米盟军和
500厘米德军位于同一直线上；4秒内`TargetActor`始终为空，门禁失败。运行类确认为V4
Pawn／V4 Controller，558项不变，无蓝图运行错误。UE源码表明PawnSensing先用Controller
`LineOfSightTo`，所以前方盟军遮挡后方德军是与布局一致的可能原因，但本次没有单独事件
计数／可见射线证据，不能写成已证明原因。按预写条件不做位置扫描或延长超时，V4保持
未选择，B1感知仍未通过，B2-B5未开始。

## 已完成

- 已读交接要求、设计／验收、导航／动作／枪械结果和相关失败，并建立B专用实施文档。
- `capability_v1`因Blackboard键类型没有以Python短类名导出而在构造前停止；失败保留，
  514项不变。
- 一次最小技术修正改用安装引擎实际类路径。`capability_v2`在`/Engine/Transient`
  成功构造一个Blackboard键、真实BehaviorTree、Selector根和可执行Wait任务；树引用
  BB，514项完全一致，未保存任何包或城市。
- 离线接口核对确认现有盟／德TeamId为0／1，角色为Player／Ally／Enemy，四个动作
  事务入口存在。共享开火目前只有友军挡弹、不扣友军血；全局友伤合入仍属协调窗口。

## 保留的B0作者失败

`b0_author_v1`在第一行本地模块导入时报`ModuleNotFoundError: common`，作者主体没有
执行。异常发生在脚本退出保护之前，因此启动器在四分钟上限终止本任务PID。这是启动
脚手架失败，不是BT／Blueprint编译或资产失败。

退出后`post_b0_timeout_v1`确认：UE进程为0；514项大小/SHA完全一致；
`/Game/ParisCombat/AI/NPCInteractionV1/`不存在、文件数0；正式地图、共享类、配置、
Catalog和release均未改变。源码已离线修正为先加入自身目录再导入`common.py`，启动器
提示也区分author/capability；尚未重跑。

B还完成离线确定性契约模型及8项通过测试：独立最后目击／不跟踪隐藏目标、阵营筛选与
15秒搜索到期、切目标不重置累计短追距离、到点继续占用预约并在死亡释放、generation／
重复请求处理、无枪拒绝和友伤开关语义，以及连续移动／停止位置验证、最多两次重规划和
旧Move回调隔离。这只是可执行设计证据，不是UE移动／感知／战斗
验收。`SHARED_FRIENDLY_FIRE_PATCH_PROPOSAL.md`给协调窗口准确的首个命中分支和玩家／
盟军／德军回归矩阵，没有修改共享战斗蓝图。

启动器也新增双重互斥：既检查实际Unreal进程，也读取`HANDOFF.md`顶部显式槽位归属；
“没有进程”不再被误当作Lane A已经释放。B不写HANDOFF，只消费协调窗口的声明。
`slot_guard_probe_v1`负向检查在零UE进程但A仍声明占用时于预检前拒绝；未创建证据目录、
未启动UE、未写资产。
最终离线复核`final_offline_audit_v1`再次通过514项大小／SHA保护和实际接口检查；8项
契约测试、全部Python语法、PowerShell解析及`git diff --check`通过。

## 历史检查点状态（已被上方最新结果更新）

B0原生资产、两个控制器独立记忆和新鲜加载测试均未完成；B1–B5移动、感知、预约、
搜索、装备、事务和六人物交互均未实现。AI-01／NAV-01仍为Not run。

获得新的明确原生时段后，用新identity只重跑修正后的B0作者；必须先取得新包清单、
新鲜加载真实树执行和BB隔离，才可扩展。禁止复用`b0_author_v1`，不自动提交、推送、
发布、选择正式地图或合入共享友伤patch。

释放后，另一工作流已启动PID54048执行`ReloadRepairV5/ue_blend_capability.py`。B确认
该进程不属于本窗口，不终止它；它存在期间B不再执行任何Unreal工作。
