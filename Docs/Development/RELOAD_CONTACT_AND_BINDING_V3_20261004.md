# 换弹 V3：先修预览枪的握持，再检查游戏绑定

2026-10-04，yg745。用户本轮明确：游戏已有正确手枪接触，先纠正当前原始动作
预览的结合，再检查实际游戏绑定。本轮不重做动作／手指／模型，不改正式游戏。

2026-10-04后续授权更新：用户明确评价当前预览成功，并要求实际游戏采用当前版本。
预览人审已通过，准许本地游戏适配／在验证成功后有限选择；不是将原始mannequin
坐标或AN001失败目标直接写进正式地图的许可。先执行下述独立绑定检查，再以
新的实施文档明确实际机制与早期同目标视觉证据。保留原资产／原动作／手指／
相机／事务。No commit/push或新immutable发布权限；此前“本轮不改正式游戏”
只描述上一轮检查范围，不能覆盖这次用户采用授权。

## 已读失败与本轮区别

已读Failures索引、AN001、AN002、FP001、原始带枪预览记录、V3枪挂接实施与
作者源码、现有owner显示源码。用blender-character-workflow的同阶段接触／变形
检查。AN001重定向／owner作者路线停止，AN002 live蒙皮查询停止，FP001不再扫
整套摆位／裁袖子。本轮不是重复这些机制。

源动作：`/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP`。
现有游戏枪挂接：`/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3`。
游戏Right grip anchor为枪局部(-0.5,-8,0)厘米，Ready用两掌心方向，Reload用
已验证右腕枪方向；释放的左手不能被当作枪口方向。

## 范围、存储与保护

- 当前唯一用户编辑器PID42928，原始D059／旧失败目标／旧动作三标签。
- 先在此窗口的/Engine/Transient原始预览中读现有枪、socket、右掌心／右腕，
  对照已验证游戏参数。只改这一临时枪的刚性挂接；不保存socket／资产／地图。
- 精确记录before与after相对T，保留可恢复状态；枪尺度1、NoCollision。
- 所有512保护／旧候选文件、源动作／模型／骨架／手指、camera、ammo／生命周期
  不变。没有Catalog／allowlist／release／commit／push。
- 单一私有工作区 `Evidence/ReloadContactBindingV3/`，每次新identity、不覆盖。
- 不重跑AN002的Geometry Script／蒙皮边长查询，也不重跑AN001作者／launcher。

## 具体顺序与早期验收

1. 先只读源预览socket与右手，记录挂接before；冻0秒，后续UE原生刷新骨骼。
2. 使用游戏既有握点与起始持枪两掌方向作一个明确刚性枪候选，右掌心用原有手指末节
   的平均握持中心，仅作测量、不改手指。原始和目标参考手坐标若不一致，记录
   实际差异，不把同名hand_r/socket当成可直接通用。早期检查枪握点落右掌心、
   枪方向没有反转，从侧面／另一侧看接触，不只看正面枪口缩短。
   明确算法：0秒两掌心的FindLookAtRotation，用现有V3的
   (Pitch=0,Yaw=look.yaw-90,Roll=-look.pitch)；枪局部握点(-0.5,-8,0)对齐右掌。
   一次性换算成源hand_r的相对T，随后保持该相对T，由UE原生attachment运动。
   不把盟军不同参考手坐标的旧右腕角度直接套给mannequin，也不追随释放的左手。
3. 原生attachment随原动作运动，无Python每帧控制；0／1.2／2.2／3.4／末帧
   检查右手保枪、左手释放／回归，区分通用弹匣动作与M1机制缺口。一个小的
   接触修正最多，不扩展到姿态／手指／相机或全动作offset扫描。
4. 接触检查完成后，游戏绑定检查必须使用独立可退出测试进程，保持源预览
   不成为并发writer。若用户预览仍占用唯一编辑器，需要用户关闭后串行进行；
   可提前准备只读脚本与启动手册，不擅自关窗口。用户本轮授权检查，未授权
   保存／更换正式玩家／重定向。独立进程可对当前地图做无保存诊断：正式当前
   player/owner与旧失败D059仅作短期执行对照，后者不复用旧停止launcher。
5. 观察实际body/PoseMesh/display mesh的leader名称、mesh/skeleton、骨骼数量、
   预测／forced LOD、可见性tick策略、组件及手臂骨骼T、binding切换和相机。
   先写最小读数，再采相同阶段证据；Python仅观察／测试触发，不控制显示。
   若暂时切换失败动作，只改测试实例并恢复原clip／token状态，不保存游戏包。
6. 复核保护哈希和日志，记录实际结果，不从预览接触改善推断游戏适配成功。

### 游戏检查执行细化（在启动前记录）

使用新的`ue_reload_game_binding_v3.py`与独立launcher，两个串行独立scope：
`saved`为正式保存地图/player/native owner；`actions`仅使用现有
`ue_player_actions_stage.stage_actions_actor()`无保存暂存V6/ActionOwnerV1。
后者是最近用户动作预览，不是正式地图绑定；不会调用AN001停止的stage/author。
先写正式地图player、owner、gun绑定，20秒等待后观察Ready→原生Reload→Ready→
Lifecycle reset。只注入原生请求，不注入弹药、不切新clip、不改leader或显示姿态。
现有Rifle_Reload_2保留；本次不执行失败D059对照，先验证基础绑定完整性。

反射API已查本机UE5.8头文件：GetAnimationAsset、GetNumBones、GetPredictedLODLevel、
GetForcedLOD及LeaderPoseComponent；仅15个骨骼T，无蒙皮读取。还查了本机
SkinnedMeshComponent.cpp的SetLeaderPoseComponent：设置leader时会将followers
重定向到最终leader，而解除时不会自动还原followers。本次重点实测display是否
在Reload后残留BodySource绑定；源码推断不能代替运行结果，也不能直接归因袖子。
早期验收：512哈希匹配、桥禁用、实际player/owner正确，正常Reload获准。
API错误保留并正常结束新进程；原生异常则停止此路径，不在用户预览重试。

## 停止与回退

若一个刚性枪挂接不能在原动作内维持合理握持，报告M1／原通用动作的接触缺口，
不做新动作。原生访问异常立即停止该读法、保留证据，不在用户编辑器重试。
恢复只需将临时枪before挂接还原，不恢复旧native文件覆盖新工作。
未完成实际游戏绑定前不得说袖子根因已定位／换弹修好；不能取得串行测试窗口
时停在等待关闭窗口，而不是偷偷另开写入进程。
