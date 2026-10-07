# 换弹预览接触修正与游戏绑定检查 — V3 记录

2026-10-04 17:15 EDT。状态：临时原始预览挂接完成检查；实际游戏绑定检查尚未执行。
实施依据：[V3实施文档](RELOAD_CONTACT_AND_BINDING_V3_20261004.md)。

后续更新（10月4日）：用户已认可本页原始预览并要求游戏采用。实际游戏两scope
绑定检查及隔离V4证明现已完成；绑定／代理握点改善，但目标士兵袖子实图仍失败，
正式地图未覆盖。详见[后续结果](RELOAD_APPROVED_GAME_INTEGRATION_RESULT_20261004_ZH.md)
与AN003。本页17:15的未执行／待确认描述是当时快照，不撤销源预览认可。

## 已完成：原始动作预览挂枪

用户说明游戏已有正确接触；本轮没有更改游戏持枪参数。原始D059
`W2_Stand_Aim_Reload_IP` / `SK_Mannequin`预览中的M1，原先直接挂在
`hand_rSocket_Aim`、相对T为identity。这个源骨架socket并非盟军游戏枪的已验证挂接。

只在当前Animation Editor的`/Engine/Transient`中采用一个候选：用既有V3枪局部
握点(-0.5,-8,0)cm、0秒两掌心方向规则，换算成源`hand_r`固定相对T。不是盲目
套用不同参考手坐标的盟军右腕角度，也不追随换弹时释放的左手。右掌心代理点
使用既有规则middle/ring/pinky/thumb的02/03骨骼均值，不修改这些骨骼。

- 相对平移：(-18.067599, 5.678340, -0.657171)cm。
- 相对旋转四元数：(0.019928, -0.061716, -0.776552, -0.626706)，反号等价。
- 枪尺度1，NoCollision；源动作、模型、手指和骨架不变。
- UE原生attachment随后驱动枪。Python只一次设置、明确seek和单次读数；没有每帧更新枪。

检查0、1.2、2.2、3.4、4.13秒五阶段，固定相对T一致，右掌心代理点误差最大
3.06e-14cm。五张Back侧面视图已实际查看：右手与枪整体更连贯，无明显枪手整体脱离。
这是代理握点与外观检查，不是所有指尖／扳机接触通过，也不能用接近零的数值
证明没有穿模。源为现代步枪通用换弹，左手操作仍不是M1真实装填机制；没有修
手指、新造动作或将其选为游戏baseline。

![0秒原始动作带枪预览](D:/0.Rutgers/CS549/Project-New/Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadContactBindingV3/contact_fit_v1/start_back.png)

![2.2秒原始动作带枪预览](D:/0.Rutgers/CS549/Project-New/Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadContactBindingV3/contact_fit_v1/phase_2_2_back.png)

私有证据：`Evidence/ReloadContactBindingV3/contact_probe_v1/`、`contact_fit_v1/`，
位于唯一SFTP workspace；截图不发布到GitHub。原输出状态保留pending visual review，
本记录补充实际检查，未伪改历史JSON。两次console缺少import builtins的NameError
保留在用户预览log；修正显式import后取得五个读数。随后原生play rate恢复1并循环。

## 待执行：正式游戏与当前动作预览的实际绑定

新只读诊断脚本和串行launcher已准备，Python AST／PowerShell parser检查通过，
但没有启动游戏测试。PID42928仍是用户拥有的原始资产预览；必须先关闭整个
Unreal编辑器，不能并发打开同一物理Content或擅自结束用户进程。

分别检查：

1. `saved`：当前正式保存的Paris地图、玩家与native连续手臂owner。
2. `actions`：同地图无保存暂存V6／ActionOwnerV1，代表最近动作预览；不是正式地图选择。

观察原生Ready→Reload→Ready→reset，以及身体／PoseMesh／display的leader、
骨架、LOD、15骨骼T、枪引用和相机。仅触发已有请求，不注入弹药、不切新clip、
不改leader，不调用AN001停止的author/stage或AN002蒙皮读取路径。

有一个源码疑点待实测：本机UE的SetLeaderPoseComponent会把followers重定向到
最终leader；解除leader不会自动恢复它们。ActionOwner在换弹时将PoseMesh绑定身体，
Ready时仅解除PoseMesh，没有显式还原显示手臂。可能导致显示手臂残留身体绑定，
而枪仍跟持枪PoseMesh。尚不能断言这是当前运行状态，更不能断言它导致此前袖子
三角形伸长；该问题与AN001参考姿态差异也要区分。

关闭编辑器后可按顺序执行，identity占用不可重跑：

```powershell
.\Tools\Integration\run_reload_game_binding_v3.ps1 -Scope saved -Identity binding_saved_v1
.\Tools\Integration\run_reload_game_binding_v3.ps1 -Scope actions -Identity binding_actions_v1
```

## 保护与结论边界

17:13 EDT复核507原保护文件＋5 AN001文件：512 size/SHA检查，0差异。
正式地图仍为2791b4a7...ad68519。无native保存、正式绑定修改、baseline/release/
Catalog/allowlist变化，无commit/push。blender-character-workflow只影响同阶段
接触检查和不把骨骼同名当作兼容证明的验证方法，没有调用Blender重建手臂。
游戏检查未执行；不能宣称袖子修复、换弹适配完成或游戏绑定已通过。
