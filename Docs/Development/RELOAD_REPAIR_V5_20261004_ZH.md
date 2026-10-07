# A窗口：换弹修复V5实施文档

最新有界结果：[继续修复检查点](RELOAD_REPAIR_V5_RESULT_20261004_ZH.md)。AN004两版
owner及AN005单次权重实验均未过早期连续性／画面门槛、已停；三问题未关。522保护
一致／没有选择native，A释放时段回B。下方运行／预留状态是有日期的历史记录，
后续需不同机制，不重跑已停方案。

2026-10-04。你确认RLD-01食指穿模、RLD-02衣袖遮挡、RLD-03换弹结束接持枪跳帧，
授权本窗口继续修动作。[英文原版](RELOAD_REPAIR_V5_20261004.md)。

## 已读案例、本次不同机制、保护条件

### 已授权的局部衣袖权重实验（10月4日）

你明确允许在**新的第一人称手臂副本**上做一次肩部／腋下衣袖权重适配。例外仅覆盖
副本局部衣袖：原士兵、V3手臂、骨架／参考矩阵、手指／手部权重、源动作、网格坐标／
拓扑／UV／材质和相机不动。已读AN001/002/003/004/FP001及角色形变流程。

使用现有V3 FBX和已记录的实际2.20秒骨骼矩阵，不实时查询蒙皮。唯一确定性规则：
参考坐标|X|≥18cm、Z125..150cm，同时受spine_03和同侧已有upperarm／twist影响，
且没有前臂／手／手指影响的顶点，只将spine_03份额转给其同侧已有最大上臂影响。
不新增骨影响、不全局平滑、不扫参数。单独导出新SleeveWeightsV5 FBX／Blend。

早期门槛：实际2.20秒>3倍且额外>2cm的边至少减少50%；所有记录换弹阶段的最大
额外拉伸不得增加。导出前网格／拓扑／UV／材质／骨架参考矩阵完全一致，手指、手及
未选顶点权重完全一致。检查中立四视图和全部记录换弹阶段正／侧面黏土对比，尤其
袖口与相邻接缝。干净进程重导入按既有FBX容差核对（位置2e-5m、骨矩阵1e-5、
权重1e-5）、归一化／≤4影响／无动作。离线不是实际游戏通过。仅这些门槛通过后才
另记新UE导入及未保存显示替换，仍不正式选择／覆盖。唯一规则失败或产生接缝／尖刺
就保留并停止此机制，不扩大范围／隐藏衣袖。

offline_v1在FBX导入之前停止：旧骨矩阵结果没有errors键，与audit结构不同。唯一
读取器纠正将缺省errors视为空；输入哈希不变，保留v1，用新v2身份运行。权重规则、
门槛、范围不变，属于测试读取器纠正，不是第二个权重方案。

124顶点改动通过数值门槛（实际2.20秒严重边31->3）。导出后渲染初始化因空场景无
World停止，权重不重做；validate_v1只读已冻结FBX／Blend，显式建立渲染World，重
导入和36张黏土图通过。位置1.813e-7m／骨7.749e-7／权重0／UV0，材质拓扑不变。
已看正侧全阶段表和肩部大图：腋下薄片减少，但原肩口开口／尖边仍在。中立图是
肩部近景、部分手部出框，不当全身通过。

下一步只做一次UE导入／视角原因验证：新网格和新Skeleton放到
/Game/ParisCombat/Characters/ReloadRepairV5，不绑定／合并／保存原Skeleton，沿用
原材质，核对必需骨父级／参考姿态。实际城市不保存，用普通临时SkeletalMeshActor
驱动器＋旧V3／新权重两个显示actor，共用原Allied模型＋现有诊断D059动作；每阶段
0／1.2／2.2／3.4／4.1秒单次冻结seek，UE自身leader蒙皮。使用原相机与持枪owner
变换、原M1和记录的hand_r固定挂接，非Python逐帧控制，不建／启用停止的owner。
临时隐藏原FP显示。同阶段前后FP图与骨握点一致只验证权重效果，不是换弹生命周期
接入。如果仍遮挡镜头就停止权重候选，不建正式owner／player／不选地图。520旧
native保护不变，新导入2文件另加保护，无发布。

native_views_v1有10张冻结图／522保护／退出0，但普通StaticMeshActor枪的根组件
是Static，原生挂接拒绝、图里没有正确枪，因此不是完整比较通过。只纠正查看器：
PIE前设Movable，断言实际parent／socket／网格身份及两枪位置一致；权重、动作、
相机、frame、阶段不变，新v2身份保留v1，不新增资产／权重方案／停止的owner。
v2仍遮挡就停该候选。


### 最小证明后接入新owner

第一版owner集成已按AN004停止：519保护及单次换弹成立，但权重归0重新fit仍使
枪13.3543／腕13.2729cm跳变。先读新失败分析，不重跑／选旧owner。新机制单独
BP_PCReloadOwnerReframeV5：Ready恢复计算当帧原持枪目标，稳定权重0时缓存
ReturnStartFramingT；权重>0时以(1-ReloadWeight)从缓存frame TLerp到目标frame，
用同一frame重新计算ViewT／FitGunT。不是再加延迟或扫偏移；519旧文件不覆盖，
仍以3cm早期门槛检查实际地图及后续视觉／生命周期，不放宽、不正式选择。

reframe_author_v1在保存前停止：promoted算术节点首个输入还是wildcard，拒绝1.0。
唯一schema纠正先连类型明确的权重输入，再设常数；不换几何／时间参数。519保护
一致／正常退出0，保留失败源／结果；仅v2可继续，不覆盖旧资产。

fresh_v2有61采样，UE自身1->0过渡耗时0.257617秒，两端实际源pose位置误差<3e-14cm，
四元数0；不是模型／视觉通过。新ABP_PCReloadOwnerBlendV5复用两个evaluator／
two-way root，原生UpdateAnimation读取owner->combatant，累加现成clip时间及0.25s
权重；原Idle仍循环，Reloading进入重置源时间，离开保留当前相位再淡出。取消不能
伪造完成动作、不碰弹药／ActionID。

新BP_PCReloadOwnerBlendV5复制健康ActionOwner，不选AN003；Init赋新AnimBP，显示
保持独立PoseMesh leader、不再跟BodySource。权重>0期间保留换弹前framing，权重归0
后仍走原持枪fit。新BP_PCReloadBlendGunV5调用原父级挂接，在Ready／权重0缓存
原hand-relative持枪变换，用相同权重混合到已记录的诊断reload变换，不动手指／枪
网格。实际城市fresh检查最终fit是否仍跳；结束附近≤60ms相邻采样枪／腕>3cm就停，
不选择此集成。RLD-01/02仍未修复，数值平滑必须再看同阶段接触实图。
玩家只临时使用之前通过的速率0.5241936452，原duration／commit／事务不改；不保存
正式player／共享base／地图。

transition_proof_author_v1在函数反射名查找停下，没有保存／编译新图，515保护一致、
正常退出0但不是成功。唯一技术纠正核对安装KismetMathLibrary.h：实际反射名是
FInterpTo_Constant，不是C++ math helper的FInterpConstantTo；v2按真实签名建图。

fresh temporal v1未发出过渡请求就停止：PIE复制后两个直接动作参考仍为参考姿态，
不是指定换弹末点。安装SkeletalMeshComponent.cpp确认PlayAnimation／SetPosition
操作临时instance，不持久化到actor默认。唯一fixture纠正是在PIE后只初始化两参考
component一次，记录真实asset／position后等骨骼刷新；不逐帧更新混合模型、不改图
或放宽端点容差。516保护一致／退出0，此次不是过渡成功。

### 本窗口继续：离线蒙皮原因／最小原生混合证明

本次已重读AN001/002/003/FP001及角色工作流、共享指导、服装形变检查。B正在使用
下一原生时段；A先离线，不能并开UE。用已导出的V3 FBX与已有骨骼采样离线线性
蒙皮，区分真实边拉伸与镜头投影；不再live Geometry Script批读，不重定向、不改
模型／权重。先拟合FBX静止骨头位置到native参考姿态，最大误差需<0.01cm；失败或
缺权重骨则停止归因。离线模拟不是游戏实际LOD／leader蒙皮通过。

RLD-03下一步只证明新AnimBP的两个现成sequence -> 标准two-way blend -> root；
原D059失败衍生仅作诊断输入，不升级为baseline。先最小建图、编译、fresh-load，再
扩展owner。编译前后不复用pin，不做新关键帧／IK／遮罩／recoil chooser；API失败
则保留并停止，不用Python每帧更新替代。后续必须同时连续混合姿态、手部相对枪
变换、camera-local framing，最后回到原持枪端点；时钟通过不等于选择通过。

新增源／证据只在ReloadRepairV5；离线identity为offline_skin_v1。动作timing配套
skill当前未安装，采用项目UE标准节点工具作fallback，仍须实图与原生验证。

blend_capability_v1在菜单名查找提前停止，没有建线／保存，514保护不变、退出0不算
证明通过。实际资产菜单名带单引号且Rifle_Idle重名。唯一技术纠正采用通用
`Animation|Sequences|SequenceEvaluator`并显式指定现成sequence／ExplicitTime，
接`Animation|Blends|TwoWayBlend`；不生成clip key、不扫几何参数。

最小图v2已新存88,616字节AnimBP，编译无节点错误／514保护一致／退出0。下一步
只复制此新图为ABP_PCReloadTransitionProofV5：原生BlueprintUpdateAnimation ->
FInterpConstantTo(当前权重,目标权重,DeltaTimeX,4) -> 权重setter；单次函数请求把
目标从1改0，UE自身完成0.25秒现成姿态crossfade。固定换弹末点4.133333s／持枪0s
只是隔离诊断，不是游戏正式绑定／新源动作。fresh进程检查实际socket轨迹、与直接
播放源动作的端点一致，禁止Python每帧插值；失败先停，不扩展owner。

已读Failures索引、AN001/002/003/FP001、角色动画skill及共享执行指导。
原始预览认可保留，游戏目标失败。旧stop-lock不解锁，不重跑失败重定向、live蒙皮
批读、复杂后坐力chooser、遮袖或整套搬位／镜头调参。绑定改善已经证明不够。

先离线核对构造源／现有证据，之后看自然结束的连续过程，不拿AN003再扫偏移。
分别定位姿态硬切和显示Framing硬切；先区分真实衣袖伸长与近镜头投影再谈蒙皮。
先查现成动作的idle／return末段，不把“缺动作”直接当结论。
食指用真实同阶段指尖／枪几何复核，不再只看掌心代理点。

UE5.8.2、现有盟军连续手臂／M1、D059 Aim换弹和RifleAnimsetPro持枪；不是新动作。
原件、全身士兵、骨架／权重、手指原曲线、相机25/0/60/FOV90、枪弹药／伤害／死亡／
复位事务均保护。允许现成片段的有界时序／blend／挂接适配，不猜测性改权重／手指IK／
人体。若原因确实需要扩大保护范围，先给精确例外说明再取得授权，不重造人／动作／购买。

## 存储与步骤

代码只在Tools/Integration/ReloadRepairV5/；新原生资产只在
/Game/ParisCombat/Animation/ReloadRepairV5/和/Game/ParisCombat/Blueprints/ReloadRepairV5/。
证据Evidence/ReloadRepairV5/<唯一名字>、日志tmp/reload-repair-v5/。
单一SFTP Content不复制资产；原514项和正式map2791b4a7...ad68519保护。
A先占UE时段，B/C可离线并行。

1. 记录人审、保护／进程、离线逻辑；建立自然结束的action／pose／显示／枪取样契约。
   先不生成原生包；旧reset图不是自然结束证据。
2. 最小安全的同源／同目标／实际视角原因检查，不live读蒙皮。对比外部衣袖与原相机、
   leader／tick／骨骼／LOD／相机空间变换。外部看着正常不够；最小API失败就停。
3. RLD-03：硬姿态／Framing切换确证后，另起原生现成片段blend／transition驱动；
   不写新关键帧／轨迹。保留已认可持枪终点，枪和显示姿态一起运动。
   具体节点先写清，再做最小图证明，不先重建整套复杂Owner。
4. RLD-01：定位相交阶段，先查兼容现成源／参考姿态和枪刚性挂接，不改手指模型／曲线。
   检查全周期、支撑掌／扳机，不能为一个指尖破坏持枪／指向。
5. RLD-02：只修已证明的组件／辅助映射／投影机制。现保护下无法修则明确兼容缺口，
   不遮衣袖、不重复失败蒙皮读取／扫偏移。
6. 有效部分组合成未保存真实城市预览，重新测动作／事务／移动／近墙／死亡／复位，
   再人工复核。正式图选择另写协调计划，不自动发布。

## 早期验收与停止条件

natural_end_v1已采99项，514项保护一致、正常关闭日志、无匹配Python／Blueprint／
ensure／fatal；OS句柄未保留退出码，不能称进程exit0。body只到2.166667s，owner
4.133333s；诊断提交点3.95到不了。没有扣／转弹，4.637568秒后Ready。
跨切换连续两样本间52.684ms，枪位置差14.2417cm、右腕7.6803cm。这是时序／绑定
证据，不证明缺动作或衣袖原因。Ready时读body位置触发AnimBP模式警告，这些位置
不是有效相位数据；后续观察器跳过该读法，不掩盖原警告。

下一次timing_sync_v1保留原body时长2.166667、提交1.083333，仅在未保存玩家默认值
设ReloadPlayRate=bodyDuration/ownerClipLength（约0.52419）；原支持播放速率的相位
事务继续驱动，owner正常播放D059。不新造片段／图／资产、不直接改弹药。
一次自然换弹要求2/16→8/10、一次守恒提交、原生Ready与显示结束接近。
泛用中点marker仍暂定，不是M1机制／画面通过。若速率支持不成立，保留并停该假设，
不延长duration或按elapsed制造弹药。姿态／Framing blend、RLD-01/02仍分别未过。

首个native诊断只把已失败夹具当未保存的观察对象，不重新证明／修复／选中。
新natural_end_v1，桥关闭、隔离真实城市、现有V6／proof-owner临时舞台，同样进程内
诊断timing，一次原生换弹请求；不seek／reset／冻结／更新姿态。
记录body／pose位置、action／提交／弹药、组件／view／framing／gun／index变换，
到原生Ready后再0.5秒。保留原timing并区分全身和显示动作。不存新资产，正常退出；
API／保护失败或12游戏秒未返回就停止。这与AN003冻结验收不同，不自动修好RLD-01/02。

首审只输出有来源的原因证据和精确保护，不冒充修好。首个native证明要完整连续
finish→hold，以及同阶段食指／衣袖的第一人称和外部视图；不能只冻结端点。
普通持枪／相机／接触不变坏。早期视觉失败保留并停，不扩成完整Owner；最多一次
技术夹具纠正与视觉是否成功分开记录，不扫参数。

最终测三个问题全周期、站立／移动、重复输入和取消；原单次弹药守恒提交、前后打断、
死亡／复位／旧事件、开火／近墙、真实帧时序、源哈希。
弹药提交与显示完成分开，显示收尾不能重开／重复提交事务；取消不能演成功换弹。
掌心数值／exit0／编译不替代实际变形实图。

写入／哈希冲突、不安全读取、必须扩大保护、首视觉证明失败时停止对应操作，保留
失败和源快照，继续安全独立工作。不扩NPC／VFX／ADS／后坐力／其他动作，不改
Catalog／release／正式图，不打包／commit/push。skill要求原因优先及同阶段变形实证。
