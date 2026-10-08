# NPC Interaction V1 实施方案

## 当前正式接入：2026-10-07

用户允许本地正式地图接入与试玩回归。遵循单独的[正式接入计划](NPC_FORMAL_COMBAT_IMPLEMENTATION_20261007_ZH.md)
及[实际结果](NPC_FORMAL_COMBAT_RESULT_20261007_ZH.md)，包含 NI001/GP010/AN008/
NI002 复核、原生启动早期门槛和明确停止条件；不扩大握枪/任务/SFTP/Git 发布。
当前 703 保护采用明确地图账本。

## 之前继续：2026-10-06

用户在两阵营正式外观采用后继续本窗口战斗开发；遵循
[有界战斗V2计划](NPC_COMBAT_V2_IMPLEMENTATION_20261006_ZH.md)。明确采用当前
GermanFormalV14的678项epoch，不回滚旧555/611地图或Catalog。下文等待握枪的
旧限制仅对这组已选定兼容装备被替代，不授权再拟合、正式地图/Catalog修改、
发布或Git操作。新实测和失败另记，不把作者成功当运行验收。

日期：2026-10-04。仅限 B 工作流。本轮执行 NPC 交接，不选择正式城市、不修改共享
战斗／玩家／换弹代码，不发布、提交或推送。

## 开发前已读证据

已读 `HANDOFF.md`、`Failures/README.md`、并行工作流、B交接、NPC行为草案第3版、
技术设计、Assignment 3目标／验收、导航foundation结果、玩家动作结果、德军枪UE结果、
AN003和FP001。重点保留：fresh_v1-v3的导航配置／重生成失败；runtime_v9虽然显示
blocked和速度零，身体仍推进49.12厘米；枪握点／绑定数值通过不替代扳机、换弹或画面
验收。B不改第一人称手臂、手指、动作、镜头和共享玩家显示。

## 本次机制改变

旧导航只串行移动单个角色，没有行为状态。本次使用一份共享Controller／决策定义，
每个NPC保留独立Blackboard、记忆、请求和恢复generation；动作请求返回可观察状态，
不能只改Blackboard文字就声称移动／开火／换弹完成。移动必须同时满足原生路径状态、
连续位置和到点条件。丢失视线后冻结最后目击位置，不能继续读取隐藏目标Transform。

第一个原生步骤先证明当前编辑器能真实创建Behavior Tree根／子节点及Blackboard键。
若不能，立即停止，不用Tick逻辑假冒Behavior Tree。

## 归属、顺序和早期验收

- 源码：`Tools/Integration/NPCInteractionV1/`。
- 文档：`Docs/Development/NPCInteractionV1/`。
- 原生包：`/Game/ParisCombat/AI/NPCInteractionV1/`。
- 私有证据：单一workspace的`Evidence/NPCInteractionV1/<identity>/`。

顺序为B0接口／原生能力，B1单NPC，B2双盟军预约与短追，B3三德军限时搜索，
B4装备和事务适配，B5六人物无保存城市集成。新包计划包含共享Controller、BB、BT、
动作适配、协调器、任务／服务和新的盟德试验子类。共享战斗基类、玩家、正式地图、
配置、Catalog和release均不在B写入范围。

早期验收必须证明：真实BB和BT能新鲜加载并执行；两个Controller拥有不同BB实例；
只写一个NPC的LastSeenPosition／Time不会影响另一个；丢视线后移动隐藏目标不会改变
记录。日志必须给出条件→TaskID→请求→允许／拒绝原因→身体结果，编译或BB值不算完成。

## 停止条件

出现其他UE写入者／归属不清、当前权威528项保护不一致、BT图无法原生建造或新树不能执行、
停止／成功状态下身体仍移动、部分路径／瞬移／无限重试、记忆串扰、双方装备接触无法
重新成立，或必须修改共享基类／玩家／换弹／手指／镜头／正式地图时，立即停止对应
写入并保留唯一证据。需要历史／权利／画面选择时交用户决定。不自动选择资产、保存
正式地图、打包、发布、commit或push。

## B1-V2继续实施（2026-10-05）

已读本项目失败索引、`PLAYER_ACTIONS_RESULT_20261003_ZH.md`中速度零仍推进49.12厘米、
`PARIS_NAVIGATION_FOUNDATION_RESULT_20261002.md`中单次原生取消稳定停止，以及
`b1_runtime_v1`的43.5573厘米漂移。V1只停止AIController移动，循环BT仍存活；本次改变为
先停止原生Brain/BT逻辑、使旧请求不再重发，再调用`StopMovement`。不修改现有B0/B1资产、
角色Movement参数或验收阈值。保护基线改读已验证恢复记录
`Evidence/ReloadIndexContactV6/map_recovery_v1/result.json`的528项，而非旧聚合清单。

早期检查：同一正式城市、同一起终点、同一原生MoveTo树；实际移动超过100厘米后执行
Brain停止→Move停止，随后至少0.75秒连续位置漂移必须≤1厘米，旧TaskID/RequestID不再产生
移动。若Brain停止API不可用、树仍重发、漂移>1厘米、528保护不一致或用户预览重新出现，
立即停止，不进入B2预约／B3搜索／B4装备／B5战斗。

## B1-V3原生视野修正（2026-10-05）

已读上述失败案例，并复核`b1_sight_runtime_v2`：观察者、友军和敌军均已在真实城市
生成，但4秒内`TargetActor`始终为空；日志无蓝图运行错误。V1把
`PawnSensingComponent`放在AIController上，传感器因而没有正确的Pawn朝向／Controller
所有者。这个失败保留，不覆盖、不删除，也不通过延长等待或扫描位置重试。

本次只新增V2包：Controller保留私有Blackboard、阵营过滤、最后目击写入和0.75秒
过期清除；`PawnSensingComponent`改装到盟军／德军Pawn，Pawn的`OnSeePawn`事件只把
实际看到的Pawn转交Controller的`PC_RecordSight`函数。不会读取已经移走的隐藏目标
Transform，不修改V1、B0、共享角色、正式地图或配置。

早期验收：同一真实城市中，盟军观察者面前250厘米的盟军不得成为目标，500厘米的
德军必须在4秒内被记录；随后把该德军移到5公里外，至少1.25秒后
`HasVisibleTarget=false`且`LastSeenPosition`变化≤0.001厘米。若V2原生事件仍不触发、
阵营过滤错误、记忆继续跟随隐藏目标、当前531项保护变化或出现其他UE进程，立即停止
B1并记录原因；不调整位置、不延长超时、不进入B2-B5。

## B1-V3作者API修正（2026-10-05）

`b1_sight_author_v3`在运行测试前停止：Controller V2已新建并保存，但通用字符串
`Utilities|Casting|CastToActor`在当前图上下文中不能直接创建节点。531项旧保护未变，
V2 Controller作为未选择的失败证据加入保护；没有Pawn V2、地图保存或运行验收。

本次改为先从当前蓝图图上下文查询真实`CastToActor` type id，再重定向到新Controller
类型；全部输出使用新的SightV3包名，避免覆盖V2。除此之外感知归属、距离、超时、阵营
和冻结记忆门禁完全不变。早期检查是V3三个包编译无图错误且新Controller/Pawn组件归属
正确；若节点查询／重定向仍失败，立即停止，不再尝试第三种作者路径。

## B1-V4 Python工具链探针（2026-10-05，用户明确要求）

用户要求先设置好Python工具并解释当前调用。本轮只验证工具链，不恢复NPC资产作者。
已复核V3日志、UE 5.8 `EditorToolset`插件描述和其`blueprint.py`实现：项目未启用
EditorToolset，因此`editor_toolset`包不在内置Python路径；但所需节点枚举的底层
`BlueprintGraphEditor.list_available_nodes()`已由当前环境提供。V3同时错误地把对象pin
作为`create_node_from_name`上下文参数，而Epic自己的实现使用空上下文创建后再接线。

改变：使用UE内置Python直接列举现有图的节点type id，以空上下文创建CastToActor，
重定向到现有SightV2 Controller，然后立即从图中删除；不保存蓝图、不启用实验插件、
不修改`.uproject`／Config。早期验收是节点查询、创建、重定向、删除均成功，532保护项
完全一致且UE进程正常退出。若任一步失败，保留探针结果并停止，不恢复V3作者或城市测试。

## B1-V5恢复感知作者（2026-10-05，用户明确批准）

用户在`ue_python_tooling_v1`通过后明确批准重新执行新的NPC感知作者流程。已读V1真实
感知失败、V2部分作者失败、V3导入失败和V4工具链成功记录。本次不启用EditorToolset；
使用已证明的底层节点枚举和空上下文Cast创建，把Pawn自有`PawnSensingComponent`的
`OnSeePawn`接到新SightV3 Controller的`PC_RecordSight`。只新建三个V3包，V1/V2原样
保留，不修改共享角色、配置或正式地图。

作者早期验收：Controller和两个Pawn V3均编译无图错误；感知组件属于各自Pawn，
Controller不含感知组件；盟德Pawn均使用同一个新Controller。532项旧保护必须不变。
任一作者门禁失败则停止且不做城市测试。作者通过后先登记三个文件形成535项保护，才可
做一次固定250厘米友军／500厘米敌军的真实城市测试；仍不触发、阵营过滤错误或记忆跟随
隐藏目标时立即停止，不扫描位置、不延长4秒门禁、不进入B2-B5。

## B1-V6跨蓝图调用探针（2026-10-05）

已读最新`HANDOFF.md`和`FIRST_PERSON_FORMAL_V21_RESULT_20261005.md`；Lane A已释放，
正式地图／Catalog的授权变化使旧533项成为历史。Lane B现直接采用
`Evidence/FirstPersonFormalV21/selected_v1/result.json`的555项当前epoch，其中已包含
全部11个NPC草稿。不得回退地图或Catalog。

V5已证明Cast创建／重定向可用，失败点仅为Pawn图用裸函数名调用另一蓝图Controller的
`PC_RecordSight`。本次先不保存资产：从现有SightV3 Controller图查询该函数的真实
type id，再在现有Pawn图用显式declaring class创建调用节点，核对`self`和`SeenPawn`pin后
立即删除。早期验收是查询、创建、pin类型和删除全部通过，555项精确不变且无地图保存。
若探针失败则停止；探针通过后才写新的SightV4三个包，绝不覆盖SightV1-V3。

## B1-V7公共函数探针（2026-10-05）

V6在555项精确保护下找到`CallFunction|PCRecordSight`，但显式declaring class仍不能在
Pawn图创建节点；没有保存资产。UE 5.8源码确认`BlueprintGraphEditor`提供
`SetFunctionIsPublic()`，而V3作者没有显式设置函数访问级别。本次只在内存中把现有V3
`PC_RecordSight`设为public、编译，再在Pawn图创建／核对／删除调用节点；退出时不保存。

早期验收：公共标记后跨蓝图节点必须具有`self`和`SeenPawn`pin，555项不变。失败则停止；
通过后新SightV4 Controller在首次编译前显式设public，并只创建全新V4 Pawn，不修改V3。

## B1-V8恢复SightV4作者（2026-10-05，用户明确恢复本窗口）

用户说明已暂停另一窗口开发并要求继续。已读最新HANDOFF、AGENTS和NPC握枪三视图结果；
Lane A已释放、无UE/Blender、555项当前epoch精确。握枪图只等待未来标注，本次感知作者
不改任何枪／手／骨骼／材质／动作，也不复制玩家数值。

改变：只新建SightV4 Controller和盟／德Pawn。Controller的`PC_RecordSight`在首次保存前
显式设public；Pawn自有PawnSensing，使用V7证明的
`Class|BPPCNPCControllerSightV4|PCRecordSight`类函数节点连接OnSeePawn。作者门禁要求
三个V4包编译无图错误、Pawn组件归属正确、旧555项不变。失败则停止；通过后登记三文件
为558项，再做一次固定距离真实城市测试。不得覆盖V1-V3、修改BT/BB或正式地图。

## B1-V9原因优先修复与持续推进（2026-10-05，用户恢复）

用户明确允许目标内中间失败继续修复，撤销此前单次失败即结束整轮的自行暂停规则。
已读本索引、导航停止失败、B1移动43.5573cm漂移、SightV1/V4无获取以及V2/V3作者失败。
本次查阅本机UE源码：PawnSensing明确支持Controller与Pawn所有者，先前“Controller
归属导致失败”没有证据，予以更正；5000cm+5000cm位移为70.71m，不是5km。

改变：不新增/覆盖资产，先在未保存城市测原生delegate绑定、CouldSeePawn、Controller
LOS、实际遮挡者、TeamId和Blackboard；2秒原场景→2秒只读原始事件监听→移开正中
友军并移除与观察者重叠的原盟军试验实例→4秒原生获取检查。Python监听只记事件，
不写BB，不驱动感知。监听安装前的delegate绑定单独记录，避免把监听自身的效果当作
资产成功。早期验收是可说明事件/视线/阵营/内存哪环失败；目标仍是无监听的新鲜
原生获取与丢视线冻结记忆，再B1完整移动、B2协作、B3搜索、B4/B5集成。

诊断失败保留唯一身份与证据并继续修复，不再因一次API或测试失败要求用户重复恢复。
真正停止条件是其他写入者、558项当前保护冲突、需要越界修改受保护共享内容，或
缺少必须由人决定的资产/视觉选择。玩家、正式地图、Catalog、原枪握姿与全部旧包保持。

离线机制同步修正：追击预算只在完成归队或生命周期恢复时清空，不因新的BT TaskID
重置；恢复时清除旧感知/搜索。新增两个反例，10个合同测试实际通过，非原生验收。
保护数从已核对555-row epoch加精确B新增清单计算，清单与epoch重叠项须一致，拒绝
重复路径；launch按preflight的精确数量核对。城市改为Entry启动后由脚本只加载一次，
不修改地图/项目配置，减少重复加载。

V9实际诊断：native OnSeePawn原本已绑定；原场景LOS=false/阻挡者PC_City_Ally1，
清理重叠/友军正中遮挡后LOS=true、原生事件和BB均记录敌军，丢失后记忆变化0cm，
558项精确。CouldSeePawn未反射为Python API，保留API不可用记录，不虚报通过。
下一步同一V4包、新进程、不挂Python监听：先友军单独0.75s不获取，再敌军500cm
4秒内获取，丢失1.25s后冻结记忆，并核对不同BB实例。仍无感知则继续诊断而非暂停。

## B1-V10原生守卫/巡逻与生命周期（2026-10-05）

V9 listener-free新进程实测通过：友军单独不获取、真实敌军LOS获取、两个BB独立、
70.71m丢失后记忆0cm变化，558项不变。已读停止漂移/旧请求重发案例；本次新增
BehaviorV1共享Controller、盟德子类及真实BT Planner/Arrival/Failure任务和Lifecycle
service，不覆盖旧包。保留SightV4父类原生事件和感知，Controller仅替换BeginPlay的
原生树启动，仍使用原17键私有BB。可配置PatrolEnabled/PatrolPoint；默认守卫。

实际BT为Selector：完整路径Plan→MoveTo（禁止partial）→Arrival→Wait，失败支路
有限重规划计数→Wait。最多两次重规划，耗尽后只守候、不再请求。根Lifecycle service
检查Health/RestoreGeneration，取消HasMoveGoal使原生MoveTo装饰器abort，StopMovement，
清目标/请求与旧generation；禁止仅StopMovement而保留旧任务。Python只安排测试、
采样，不逐帧驱动NPC行为。早期验收是新包编译/图无错误、旧保护不变；之后真实城市
守卫零漂移、巡逻完整路径/连续两点往返、不可达两次重规划封顶、原事务死亡/恢复取消。
API/编译/运行问题继续有证据修复。外部writer/保护冲突/需要共享越界改动或人工选择才停。

V10作者v1在导航函数的隐藏WorldContextObject pin停止；仅一个新Controller已保存，
完整保护精确且原位保留，登记为559项。UE源码该参数是WorldContext元数据，BT任务图
自动提供世界上下文；去掉不存在的显式pin，不更改导航机制/阈值。后续全新V2名称，
旧V1不覆盖。同时Home位置初始化用SelectVector单一执行链，避免多exec输入合流。

V2作者遇到NavigationPath const方法的pure K2节点没有exec pin；一个Controller保存，
保留并登记560保护。新V3仅按实际node是否有exec pin接线；pure方法由数据依赖求值，
不改变路径/预算/生命周期。作者失败继续修复，不要求用户再次恢复。

V3八个新包作者通过，旧560项精确，登记为568项。runtime_v1测试在LoadLevel泵入
Slate回调时重入、loading阶段提前访问None角色，加载中退出引擎exit3；未测行为树。
修正loading保护/异常延后退出。runtime_v2已通过守卫0cm漂移，随后配置字段不允许
实例编辑而停止。不是巡逻失败，也不绕过字段保护；新增V4 public PC_SetPatrol，
通过原生函数设置任务并取消旧目标。仅3个新派生包，原V3 BT/任务精确，登记571项。

## B3有限搜索原生服务准备（2026-10-05）

已读V9/V10和本失败索引；不让原生未测B1被离线算法替代，城市测试仍独立进行。
在B1真实BT/任务基础上，新Controller/BT service/Pawn派生仅增加敌军非战斗职责：
真实目击→丢视线后私有LastSeenPosition快照→最多5个固定候选完整可达搜索点，
SearchDeadline=起始游戏时间+15秒，不因服务重评/隐藏目标移动重置；耗尽/到期回
出生守卫位置或既定徒步巡逻。无枪只有感知/移动/接敌意图，不调用火力/伤害。
同一真实BT MoveTo/Arrival/有限失败叶仍负责身体移动，service不是Python移动驱动。
早期门禁为作者/旧保护精确，之后原生搜索点/期限/冻结记忆/职责返回与无枪无伤害。
错误继续修复；writer/保护冲突/共享越界或人审资产决定才停止。

首轮Search作者在新Controller图作者阶段native空指针崩溃exit3，没有保存Search包，
无完整result/运行验收；日志保留。与前一城市脚本重入不同，不混淆原因。下一轮用
全新V2名称、每个作者阶段提前落盘并日志标记，定位最小失败调用后修复；先核对571
旧保护/实际新包占用，不覆盖崩溃证据。B1数值城市测试独立已通过，非战斗步态人审未过。

阶段日志V2/V3将native崩溃定位到角色函数作者中第二图的Subtract_VectorVector调用
（不是编译/游戏搜索），仍零Saved Search包/571旧保护。新的V4改用固定签名
Vector_Distance，点平移用MakeTransform/TransformLocation而非promoted向量算子；
保留调用日志和未完成阶段result，不声称引擎实现的更深原因已证明。阈值/预算不改。

V4已越过向量距离，但同一跨编译图处的LessEqual_DoubleDouble作者调用仍native崩溃，
证明不是Vector_Distance替换就解决。新V5仅在任务独占进程临时请求
BP.TypePromo.IsEnabled=0，用固定签名K2节点而不做promotable算子；不改Config/uproject/
全局用户设置，不重写旧包。进一步记录节点创建/输入pin接线前后，保留每个崩溃证据。

V5控制台请求未改变实际TypePromotion：UE5.8源码读取BlueprintEditorSettings CDO，
不是该旧控制台项。崩溃在节点创建前，不是输入接线。V6直接读取并暂改本独占进程
CDO的enable_type_promotion=False且断言实际读值；finally恢复原值，不调用SaveConfig。
该类PostEditChange只刷新ActionDatabase，无配置保存；外部Config/项目配置不写。
保存的是固定签名的新图，下一UE进程仍正常默认设置。保留V5“请求而未验证”区别。

V6 snake-case属性无法查到；V7用实际C++属性bEnableTypePromotion读/改/断言/恢复成功，
原true→临时false→恢复true，未SaveConfig，Saved ini中无该项新增。已完整跨越此前
native崩溃点并编译搜索函数，正常exit0；后续SelectBool函数不存在为普通作者错误，
不用崩溃/无图错误混称。V8等价布尔AND/NOT替换，仍新名称、571旧保护，不改预算。

V8五个Search新包作者/固定签名/恢复设置通过，旧571项精确，登记576项；三德军实际
城市新进程默认TypePromotion设置测试进行中。新增任务将原生脚本/launch/common/graph
快照放入各自私有证据，不覆盖早期失败；早期没有该完整源码快照不能反称有。

runtime_v1的三德军确实走到搜索点附近（首点约40cm），但Visited计数0导致门禁失败。
原因是SearchIndex先写成下一点后，Blueprint pure的near表达式在Visited写入处重新
读取下一点；不是路径未动。V9只将旧点Visited计数置于Index更新前，保留15秒/5点/
完整路径/角色回归规则。五个新包登记581项，旧V8保留；新runtime_v2重验实际身体与
计数一致，任何成功必须包含守卫身体回原点及巡逻职责恢复，不只SearchActive=false。

## B2双盟军原生预约/跟随/归队/短追准备

已读V9/V10停止重发、TypePromotion作者崩溃原因、离线预算任务更替反例。新增Squad
Controller/真实BT service/两个Pawn子类和同世界两槽预约Actor，保留B1路径/失败/
生命周期任务及B3服务；五NPC仍同Controller/树定义，各自BB。同一协调器为2名盟军
分配独立slot与monotonic ReservationID，其他占用点至少150cm；到点/待机/开火/换弹
都保留，只在改任务/失败/死亡/恢复释放。默认不开战，保留原动作事务字段。

跟随目标为玩家后方400cm、左右200cm，超600cm跟随/1000cm归队，过近300cm也归位；
短追目标仅取实际可见时写下的LastSeenPosition，累计移动及离玩家均≤1000cm。目标
变化/BT TaskID变化不清累计预算，只有实际归队到预约点或生命周期清空。无枪/动作忙
不造开火/伤害。只选择CharacterMovement RVO，不混用Crowd；对照测试同起终点人数
和RVO，仅协调占点不同。早期门禁新包图/旧保护、随后真实双盟军预约独立/到点保留/
跟随归队/短追预算/死亡恢复释放/对照。失败继续修复，越界/冲突/人审选择才停。

短追先用850cm累计/900cm离玩家的保守运行停止线，留服务采样余量；正式验收仍是
各1000cm，不放宽，长帧严格上限尚须单独实测。原生0.1秒服务累计身体位移，目标/
TaskID变化不清预算，实际到预约归队点才清。动作非Ready只停止移动，不释放预约。
路径耗尽释放failed并锁住同目标重发，显著新目标/职责变更才重置；slot1存活者不会
在slot0死亡后偷偷换槽而留下旧预约。同一新Controller/树包括SearchV9，德国仍无枪
非战斗。新子类只启用RVO，不改原角色/AnimBP/地图或任何第一人称资产。

SquadV1图已编译但GetActorOfClass的exec未接，运行前测试器又在PIE调用editor-only
load_blueprint_class而拿不到Coordinator。V2接真实exec、测试按实际Actor标签取实例；
真实预约1/2保留、NPC0到点约44cm，但NPC1原始点在NavMesh之外，MoveTo在投影路径端
报告Arrived，离被预约的原始坐标仍125cm。身体验收失败，不据状态名放过。
V3在原生预约前调用K2_ProjectPointToNavigation，预约实际NavMesh点加该NPC胶囊半高
的身体中心；不能投影则释放failed/等待。点间隔仍150cm、身体到点仍≤55cm，原包保留。
下一城测重验实际到点、忙动作保留、追敌预算、死亡恢复及同起点/同点池/RVO对照。

V3同时在新Controller覆盖继承的PC_RecordSight：在真实OnSeePawn边界拒绝自身死亡/
目击到的死亡候选；如果该尸体正是旧Target才清它的BB/搜索记忆、停止旧移动。不是
后台读取隐藏目标当前位置/健康猜死亡；旧Sight/树包不变。新增函数override API由
本机UE5.8源码确认，删除的是新override自动生成的parent-call，避免旧无生命筛选
再写回死亡目标。实际目标死亡/恢复仍需新城市证据，不凭编译声称通过。

V3作者只保存一个预约Actor，胶囊属性的self需要Character、GetPawn输出只有Pawn，
类型接线失败，595项旧保护精确。新V4先原生Cast Character，再读取自己的胶囊半高；
新PC_RecordSight override已编译，其他路径/短追/角色阈值不改，仍须身体城测。

## B4原生动作请求/反馈和装备人审门

已读当前原动作事务、AN003旧回调、NPC握枪基线等待标注和本轮FF测试。新增独立
ActionGate Controller/BT观察服务/两方子类，在保留SquadV4动作树的基础上提供原生
PC_RequestNPCAction(Action,TaskID,RequestID,Generation)。反馈记录请求身份、允许/
拒绝原因及实际停止/原始ShotSequence/原始换弹ActionID和守恒；旧generation/任务、
重复请求/动作忙须拒绝或观察Running，不重开事务。停止先禁止自己的任务源，实际
0.5s稳定才Completed；换弹依原ActionID/gen和Ready反馈，不用计时造弹药。

装备numeric验证和human grip接受为分开默认false门。无枪/装备未验/接触未人审则
不调用开火/换弹。Fire还需实际可见敌军、身体已停和实际枪口到目标的无友军/世界
挡线，再调用原PC_RequestFire(自身眼位,方向)。这不是自动批准等待用户标注的NPC
基线，也不重做枪/手指或第一人称。新城测先验旧身份/重复/真实停止/人审拒绝不耗弹，
完整自动战斗接入仍等待NPC握枪确认。早期编译/旧保护；实际动作完成与图作者成功
分开。API/测试错误继续修复，真实共享冲突/新增权限/必要人审才停。

用户随后明确答复“等我标注握枪后再启用自动战斗”。本轮不开NPC自主开火/换弹树，
保留EquipmentHumanAccepted=false；只继续非战斗B1/B2/B3、原接口直接事务回归和
动作拒绝/停止/旧身份反馈测试。不开启未人审武器、不给人审门置true，不偷偷把
现有绑定当最终验收。实际三视图标注是后续自动战斗的必要人类输入，而不是作者错误
导致的人工暂停。原共享友伤合入/三类射手直接回归授权仍有效。

`squad_runtime_v4`已通过实际换敌保留episode/累计距离，以及真实目击目标死亡清记忆。
死亡友军预约检查在Regroup→Follow合法职责切换之前取基线，随后原生重新预约而失败；
记录表明slot未变，WaitingReason/TaskID对应职责变化，并非已证明“死亡导致存活者失槽”。
下一独立测试等待Follow职责稳定1秒再取死亡基线，不修改资产或预约/到点阈值。早期
门禁仍是身体到点/预约保留/原换弹守恒；其余死亡恢复/对照实际通过前不报B2完成。
ActionGate作者V1在Controller范围找不到Pawn的PC_RequestReload，零包保存；V2以已验证
declaring-class公共外部调用修复，并加入原始死亡/恢复中断Stop请求的原生观察子门禁。

ActionGate V2仍零包保存：本机UE CreateNodeFromName源码以定义函数的类精确过滤，
不接受继承该函数的CombatantV2作为declaring class。PC_RequestReload实际定义在保留
的SimplifiedReloadDraft/BP_PCCombatantReloadV1；V3只修正这个已确认函数归属，不把
失败猜成私有权限或改共享事务。记录实际type-id/declaring-class，新包/人审门边界不变。

ActionGate V3五个新包已真实编译/保存，601旧项精确，登记后606项；确切函数归属修复
成功，仍不是开火/换弹或完整B4验收。`combat_regression_v4`玩家两友伤模式、墙挡、
原尸体非碰撞/不二次死亡均通过，转盟军时测试新生Pawn的WeaponAppearance为None。
实际正式盟军枪是地图实例绑定，而非Pawn默认。下一测试从PC_City_Ally1读取并精确
复用同盟军mesh/枪类/LeftShiftCm/枪组件配置到未保存、同原rig的测试派生NPC；不复制
玩家参数或做枪位/手指新调整。ActionGate拒绝测试的“持枪盟军”也用此真实配对配置，
德军仍特意无枪。早期配置逐项精确、旧保护和原事务；不放宽阈值/保存地图/批准握枪。

V3接口静态审查发现拒绝一个新请求会覆盖reply身份，而旧动作随后完成未恢复原身份。
下一V4只加强新适配器：terminal从Active身份回填，重复身份但不同Action明确拒绝，
实际BB TaskID改变取消旧动作。新增原生测试在Stop运行时插入ActionBusy/动作不匹配
拒绝，再要求真实停止完成的反馈仍为原Task/Request/Generation；不凭输入日志替代
反馈身份。早期仍编译/旧保护/人审拒绝，保持V3包并另建V4，失败不改共享原事务。

同一Task/generation中较旧RequestID也明确拒绝；新测试再用原生PC_SetPatrol启动真实
下一任务，使BB TaskID自然变化，要求旧Stop收到TaskSuperseded且仍携带原请求身份。
不直接写BB/虚构Completed，不用这些非战斗测试解锁装备人审。

原生BrainComponent重启一次只刺激树重评估，实际TaskID必须自然改变才断言取消。
ActionGate V4五包作者606旧行精确，登记67个B包/当前611行；`action_gate_runtime_v1`
五项停止/身份/装备拒绝检查真实通过，16个停止样本漂移0cm/611精确/exit0，人审门false。
最终`final_20261005_v1`闭引擎611行精确，10项单测/编译/PS解析通过。正式地图/远端
manifest不改；旧远端清单基类SHA不能覆盖当前获准友伤版本。用户握枪标注之后仍须
独立配对校准/接触与实际自主行为测试，不把本轮原接口回归和非战斗子门禁算全NPC完成。

V3八个新包作者通过，旧560项精确，登记为568项。首轮runtime_v1测试脚本在LoadLevel
泵入Slate回调时重入，loading阶段误采样尚为None的mover，随后加载/PIE中退出导致
引擎exit3；本轮没有运行NPC门禁，不能归因为行为树失败。错误/result/log原位保留。
修正测试loading分支立即返回、异常退出等待下一回调PIE结束，原8个包不改，使用新
runtime_v2身份重测；任何保护变化/其他writer仍阻止启动。
