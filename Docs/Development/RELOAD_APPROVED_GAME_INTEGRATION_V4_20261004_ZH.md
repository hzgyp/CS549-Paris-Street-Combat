# 已认可换弹／接触版本 — 游戏采用 V4 有界实施

2026-10-04，yg745。用户明确认可当前原始预览成功，并要求实际游戏采用。
允许本地适配／验证后有限正式选择；不包含发布、commit/push、NPC/后坐力/VFX，
不取消原模型／手指／动作／相机／枪械事务保护。英文原稿同名无_ZH。

## 已读失败、这次区别

已读Failures索引、AN001/AN002/FP001、V3接触实施／结果，当前ActionOwner／
native owner／枪作者源码与本机UE leader实现。AN001重定向与复杂后坐力Owner
建图继续停止；AN002 live蒙皮读取停止；FP001遮袖子／改镜头／整套搬位不复活。

先实测游戏原生绑定切换，不猜测权重。当前人审通过的是原始mannequin带枪预览，
不是盟军游戏变形。保存已校准源hand_r参数，目标参考手不同，不能直接套坐标。
只复用同一库存动作与既有握点规则，不新造动作。

## 前置条件和保护

- 本轮检查未发现旧PID42928，已串行启动bridge-disabled saved诊断。
- 512已有文件大小／SHA保护，正式map仍2791b4a7...ad68519；保留Git已有脏改动。
- 原动作`/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP`。
  已有失败目标衍生AS_PC_D059AimReloadV1仅允许在隔离诊断内读取／对照，
  不选失败player/owner，不重跑停止的author/stage或重定向。
- 已正确Ready姿态、角色模型／rig／权重／手指，camera(25,0,60)/FOV90，
  ammo/token/阶段commit/打断/死亡/reset均受保护。通用现代换弹仍非M1机械装填。

## 实施顺序和早期验收

1. saved和actions独立新进程串行检查body/PoseMesh/display/gun、leader、LOD、
   相同阶段T。actions只是现有V6/OwnerV1无保存动作预览，不混写正式地图。
2. 若证实leader切换错误，先在隔离实例验证一个最小原生绑定修正：模式切换后
   显式将display重新绑定应有PoseDriver；不做Python每帧纠正。检查实际盟军模型／
   原连续手臂／受保护镜头，使用已有目标动作衍生进行完整同目标对照。
3. 按认可握点规则在目标0秒一次校准固定右手相对reload枪T，释放左手不控制枪口。
   Ready持枪保留。早期门槛是实际袖子连续、无大型中央遮挡、始／中／末枪右手
   运动连贯；数值接触不替代画面。
4. 上述隔离视觉门槛通过后，作者前追加具体native修改清单。仅新命名
   `/Game/ParisCombat/.../ReloadApprovedV4`，复用既有UE节点基础并做最小图／
   参数修正；不复活AN001复杂chooser／recoil建图，不新增动作／手指IK／模型。
5. fresh换弹／射击／弹药守恒、早期取消／timeout仅取消／死亡／reset／旧token、
   近墙枪口阻挡、移动及Ready回归检查。通过后备份并只选当前team-map规定actor／
   reference，再fresh-load复测。NPC与nav设置不变，旧所有草稿及原图私有备份保留。

私有证据每次新identity：唯一workspace的`Evidence/ReloadContactBindingV3/`。
native输出精确记录SHA/大小/依赖/选择与回退；immutable发布版本不变。

## 停止／回退

### 原生早期证明追加清单（作者前记录）

两个串行probe退出0，512文件不变。正式PlayerV1/ContinuousArmsNativeV1仍用旧
Reload_2。动作V6/OwnerV1证实display从PoseMesh转到Body，Ready/reset仍残留Body；
PoseMesh已解除leader。首个reload握点偏差3.158cm。LOD均0、73骨，不把此证据
直接当袖子根因。

为了不由Python每帧驱动，早期检查需要两个**未选中原生证明夹具**，仅此替代
第4步前不能作者的严格措辞，不允许提前改player/map/animation：
`Blueprints/ReloadApprovedV4/BP_PCReloadGunProofV4`是现有V3子类，
`BP_PCReloadOwnerProofV4`复制当前健康ActionOwnerV1。

- 枪子类只覆盖PC_UpdateRifleAttachment：非Reload走原parent；Reload用现有
  audit的目标0秒骨骼T一次校准hand_r相对T，实际组件再核对；不做新动作／重定向。
- Owner只改既有pose函数：PoseMesh始终独立不跟Body，Reload播放已有诊断AS，
  Ready回到原Rifle_Idle，模式切换显式display→PoseMesh；Init枪class换为兼容V3子类。
  Framing/相机/模型/手指/权重/原parent枪分支不变。
- 不建复杂chooser／recoil变量／函数，compile后不复用pin句柄。两包new-only，
  作者source/result/stage marker持久记录，完成复核原512文件。
- fresh无保存城市V6+证明owner，先正常请求reload；测试实例duration/commit
  4.133333/3.95只为诊断目标时间轴。五个冻结PoseMesh阶段＋Ready/reset，不作
  功能验收；旧AS只是诊断输入，不选为baseline。
- 一次证明仍不能通过实际目标袖子／接触画面则停止，不凭数值选夹具／失败旧版。

技术脚本纠正：首作者在任何native包前遇到Transform构造器需Rotator非Quat，
改用结构属性赋值后author_v2生成两夹具。首visual取到holding，随后timing实例
不可编辑而正常失败退出。下一identity只在测试spawn前改隔离进程内的未保存V6
CDO默认timing，枪默认校准只读核对，不再写其default-only实例。夹具native字节／
姿态机制不变，两失败identity保留，holding-only图不能作为换弹失败或通过证据。

只做一个隔离绑定修正，不扫leader/LOD/offset参数。修正绑定后若盟军目标袖子／
视图仍不合格，在native作者／正式选择前停止，说明真实兼容缺口。原生异常立即
停止该读法，保留log/crash/source；不在用户预览里重试。保存地图前先备份，再
核对限定actor／reference差异，不能旧哈希覆盖新独有工作。角色工作流要求真实
接触／变形证据；内部验证通过后不额外制造人审门槛，但保护范围必须改变时问用户。
