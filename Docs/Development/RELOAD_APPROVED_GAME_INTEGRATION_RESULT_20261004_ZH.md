# 已认可换弹版本 — 游戏集成实测结果

2026-10-04 18:48 EDT。**原始预览获用户认可；实际游戏适配未通过，未采用。**
实施文档：`RELOAD_APPROVED_GAME_INTEGRATION_V4_20261004.md`／`_ZH.md`。
失败记录：[AN003](../../Failures/AN003-20261004-reload-binding-proof/FAILURE_ANALYSIS.md)。

## 当前版本的准确含义

用户“这一款改得很成功，实际游戏用当前版本”已记录为原始D059 mannequin + M1
校准挂接的人审通过，以及本地游戏适配授权。没有撤销这份认可。
该预览不是当前US Paratrooper第一人称手臂；不能将预览通过直接写成游戏适配通过。
本轮没有覆盖正式地图或悄悄选中之前失败的D059士兵适配版。

## 实际游戏绑定查清的内容

- `binding_saved_v1`：正式地图PlayerV1／ContinuousArmsNativeV1，23个观测、exit0、
  无匹配Python／Blueprint／ensure／fatal错误，512文件大小／SHA一致。仍使用
  Rifle_Reload_2；display直接跟BodySource，绑定稳定。2/16→8/10，一次commit，
  总弹药18守恒；这里只证明原有换弹事务和绑定，不认可旧动作外观。
- `binding_actions_v1`：最近无保存V6／ActionOwnerV1预览，exit0／512文件一致。
  Ready display→PoseMesh；Reload会被UE改到BodySource；回Ready／reset仍是BodySource，
  而PoseMesh已恢复独立Holding。首个reload握点偏差3.158cm。这个绑定缺陷已实测，
  不是猜测；但不足以证明旧袖子问题由它造成。各组件LOD0、73骨，相机25/0/60、FOV90。

## 一个不同机制的原生证明

两个新native夹具，合计936,584字节，全部未选中，位于唯一SFTP workspace：

- GunProofV4：V3子类，仅Reload用目标0秒校准的固定hand_r相对T，其余走原parent。
- OwnerProofV4：在现有健康Owner上最小修改，PoseMesh独立播放已有诊断目标动作，
  不再跟Body；模式切换时明确display→PoseMesh。Ready／镜头／Framing算法保留。

没有新动作、重定向任务、骨架／权重／手指／模型／相机修改，没有运行时Python
显示更新。旧AS只作为隔离诊断输入，并未选成baseline。
作者v1因Quat／Rotator构造器类型不符在任何native包前失败；一次技术纠正后的
author_v2正常生成两包／exit0／原512文件不变。没有重跑AN001停止的retarget或
复杂chooser／recoil作者。所有技术错误与源快照保留。

visual_v1只取到holding后因default-only timing不能写实例而失败。visual_v2改为
spawn前设置隔离进程未保存的CDO默认timing；没有改磁盘游戏默认值或枪实例参数。
时间4.133333／commit3.95仅服务冻结诊断；**这不是功能换弹测试**。

## 数值改善成立，但真实画面仍失败

`binding_proof_views_v2`：exit0，无匹配错误，7个实际1280×720游戏视口图已全部查看。
五个reload PoseMesh相位0／1.2／2.2／3.4／4.1秒在截图前后读数一致，display全程
正确跟独立PoseMesh；最大右掌心代理握点偏差0.000190959cm。Ready/reset回归绑定
正确。只读核对的实际0秒枪T与作者audit校准近似一致，不是每帧追手修正。

然而reload_start、operate、return和finish仍有明显袖子薄片／尖刺；operate／return
手臂占据很大画面，take阶段枪托也过近。holding和显式reset_ready可正常显示。
因此即使代理握点几乎零误差，也**没有通过同目标袖子／第一人称接触视觉门槛**。
按预定停止条件，不再作者player／复制animation／保存正式地图或继续扫参数。

![游戏内2.2秒：握枪跟随正常，但袖子仍不合格](D:/0.Rutgers/CS549/Project-New/Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadContactBindingV3/binding_proof_views_v2/reload_operate.png)

这些HighResShot图不作为HUD验证。冻结run显式reset取消诊断reload，不是自然完成。
新方案完整弹药／打断／死亡／旧token／近墙／移动回归没有运行，因为早期视觉失败；
不能引用旧正式图回归替新方案通过。

## 保护、停止和下一步权限

最终514项大小／SHA（512原保护＋2证明夹具）全部一致，正式map仍
2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519。
所有任务UE已正常退出；无用户preview进程。新夹具／34项私有证据原位保留，
launcher停止锁定，库存不是恢复／发布权威。未改变Catalog／allowlist／release，
没有commit/push。临时CDO设置随隔离进程退出丢弃，磁盘旧版本保留。

绑定修正不能解决这一目标视图，袖子具体是蒙皮／辅助骨映射还是近镜头投影原因
仍未确证，不能断言需要改权重。下一步若继续：先对现有第一人称手臂做离线／
最小安全原因定位，证明后再提有界兼容修正；不得复活AN002 live skin读取、
AN001 retarget或FP001遮袖／相机／offset方案。若需要改owner-view蒙皮／骨骼
映射，先取得新的明确范围授权；全身士兵、手指、相机和现成源动作仍保留。
blender-character-workflow的同阶段真实变形门槛阻止了把数值成功误写为游戏采用。
