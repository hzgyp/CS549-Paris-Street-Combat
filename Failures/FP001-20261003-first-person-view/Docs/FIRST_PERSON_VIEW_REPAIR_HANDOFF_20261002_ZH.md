# 第一人称手臂与镜头遮挡修复交接

## 本次结论

你已经看完运行时瞄准试验，确认两个实际问题：**手臂偏出画面、运动时遮挡镜头**。两项视觉验收均未通过。本轮只做交接，不继续修复、不改模型、不提交或推送。

这是 [英文交接原文](FIRST_PERSON_VIEW_REPAIR_HANDOFF_20261002.md) 的同步中文回顾。项目为 `D:\0.Rutgers\CS549\Project-New`，日期为 2026 年 10 月 2 日，二进制资产负责人为 `yg745`。

## 要修的两个问题

| 问题 | 已确认 | 下一步先查什么 |
| --- | --- | --- |
| 手臂偏出画面 | 你实测确认；此前真实巴黎场景截图也出现手臂可见范围不足。枪口数值对准不代表构图正确。 | 在相同动作相位记录手、肘、枪的镜头空间坐标和屏幕投影，区分上身旋转、组件位置和原有动作的影响。 |
| 运动遮挡镜头 | 你实测确认。此前记录有头部／头盔侵入，但这次还没有定位具体遮挡物。 | 对移动起步、持续移动、停止逐段截图，定位具体模型和动作相位，不能直接认定全部是头部造成。 |

两项根因还没有被证明。左手接触误差和通用换弹动作的贴合限制也没有消失，只是本次优先处理这两个视觉问题。

## 别把保存版本和试验版本弄混

项目是 `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`，UE 5.8.2。保存地图为 `/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1`，仍使用 V3 枪械挂接，玩家和两个盟军 NPC 仍用原来的 `ABP_PC_Allied_Stride_v1`。地图记录的 SHA-256 为 `d00056e8e65d3de6cf7c6af08fe9e52fa4e95e656bfe10a7392c03a82409f51f`。

你刚才看到的 V4 只在 PIE 运行时替换玩家：

- 动画类：`/Game/ParisCombat/Animation/WeaponAimingV4/ABP_PC_PlayerRigidAimV4`。
- 枪械类：`/Game/ParisCombat/Blueprints/WeaponAimingV4/BP_PC_PlayerRifleAimV4`。
- 标准 `spine_03` LookAt 上身控制加枪械残余收敛；保留原有移动图、手指局部姿态和换弹源动作，NPC 不替换。
- 摄像机 `ParisPlayerCamera` 局部坐标 `(25,0,60)`，FOV 90，准星仍在中心。

关闭 PIE 不会保存 V4。普通游戏启动脚本打开的是已保存 V3；不能以为它会自动复现新试验。另一个 `ABP_PC_PlayerAimV4` 是未选中的现成 AimOffset 对照版本，有接触缺陷，不是刚才预览的版本。

## 新对话先读的内容

先读根目录 `AGENTS.md`、`HANDOFF.md`，然后读：

1. [V4 实施范围](RIFLE_CROSSHAIR_ALIGNMENT_IMPLEMENTATION_V4.md) 和 [实际测试结果](RIFLE_CROSSHAIR_ALIGNMENT_RESULT_20261002.md)。
2. [当前地图与枪械清单](../../Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json)、[保留依赖快照](../../Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json)、[未选中瞄准试验清单](../../Assets/Integration/PLAYER_AIM_TRIAL_INVENTORY_20261002.json)。
3. [V3 动作挂接结果](RIFLE_ACTION_ATTACHMENT_RESULT_20261002.md) 和 `Assets/TEAM_SYNC_WORKFLOW.md`。

记录中共保留 40 个原生文件：之前的 37 个，加上 3 个瞄准试验包。新增三包合计 702,473 字节，准确路径、大小和哈希见试验清单。这些是本地草稿记录，不是 Catalog 选择的组员恢复版本。动手前重新检查哈希；如发现新的本地修改，先保留，不能用旧清单覆盖。

资产只有一份物理可写 Content：`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content`，项目 Content 是其目录联接。不要再复制整套资产、搬目录或同时打开实验项目和游戏项目写同一批文件。商业资产及试验二进制不进 Git。

Git 有本对话积累的多处修改和未跟踪文件，全部保留。上次查看 HEAD 为 `137993ac47ef1b1de0810c30f0e491a7244826b8`，新对话要重新检查，不能强制重置。此前预览 PID 为 6184；本次交接查询未返回 UnrealEditor 进程，但下次仍要重新检查，不能擅自关掉后来启动的用户会话。

## 怎么复现

关闭相关编辑器后，在项目根目录运行：

```powershell
& .\Tools\Integration\run_paris_aim_preview.ps1
```

脚本会打开真实巴黎地图，禁用 Editor-only bridge，生成新的预览记录，只替换 PIE 玩家。点击游戏视口后 WASD 移动、鼠标转向、左键开火、R 换弹、Esc 结束 PIE。不要通过保存编辑器地图来“保存”这个运行时替换。

关键入口在 `Tools/Integration/`：

- `ue_player_aim_human_preview.py`、`ue_player_aim_runtime_preview.py`：预览与带哈希保护的运行时替换。
- `ue_player_rigid_aim_author.py`、`ue_player_rifle_aim_author.py`：当前试验类的制作。
- `ue_paris_combat_pie.py`：可选瞄准回归，使用当前 V3 检查点及 `CS549_PLAYER_AIM_PREVIEW=1`；执行前检查其他环境要求并使用新记录标识。

私有证据根目录：`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/`。

- `Runtime/combat_aim_preview_v2/`：`combat.json`、`hud_initial.png`、`hud_hostile_hit.png`。
- `RifleCrosshairV4/rigid_live_v1/`：测量及 `aim_idle_fit_fp.png`、`aim_idle_fit_front.png`。
- `RifleCrosshairV4/human_preview_v1.json`：此前预览准备记录，不是验收通过。启动日志为 `tmp/paris-city-gameplay-20261002/human-aim-preview-20261002-233027.log`。

## 已有成果和不能重犯的错误

独立真实城市回归已通过 15 个案例、62 个断言，退出码 0：弹药守恒、遮挡／友军／无效开火、换弹阶段保护、死亡重置和试验动画类保留正常；摄像机、NPC 选择及 40 个文件未变。这些只证明对应玩法逻辑，不证明视觉通过。

瞄准采样最大枪口误差约 0.000100 度，但左手接触距离仍最多 4.82 厘米。`rigid_live_v1` 在关闭时异常退出 `-1073741819`，必须保留失败记录；后一次城市正常退出没有解释此前崩溃。早先下肢采样不是同一播放时刻，不能声称全部动作等价。看结果文档，不要重复所有旧试验，也不要夸大验收范围。

不要重做人模、手臂或枪模，不改原始骨架／源动作，不再使用被你否定的手指改造，不移动准星，不换成现代枪。不能禁用玩法碰撞或枪口遮挡检测来掩盖视觉问题。摄像机参数维持基线；若提出修改摄像机／FOV、拆分第一人称表现或仅对本人隐藏某些部件，要先明确范围和实施文档，超出现有授权的选择再请你确认。不能简单隐藏整个人体，也不能直接选中已失败的瞄准版本。

不顺带做 NPC AI、跟随／巡逻、双方交互、新移动动作或枪口特效；不自动启动 Blender 重建、买资产、发布 SFTP 不可变版本、修改 Catalog、打包或提交推送。

## 后续顺序和验收

先复现并写修复实施文档，列明前置条件、改哪些组件／节点／包、诊断办法、回滚和验收。先做同相位测量再选修法，优先对现有资产做小范围适配；本交接没有替你选定某个具体方案。

对比站立、前后及横向移动、起停、正常上下看、转向、开火、站立／移动换弹、死亡／重置。用真实地图截图和镜头空间测量确认：手臂和握枪区域在预期构图中可读，正常运动没有自身模型间歇遮住中心视野，枪口与准星／实际射击方向一致，右手挂接不退化。左手或换弹仍有缺陷就明确记录。

修后回归受影响的开火／弹药／换弹／生命周期逻辑，核对 NPC 和导航依赖未变；若涉及导航则回归导航。保留实际枪口遮挡规则，检查退出码和日志。先给你在真实巴黎地图人工复核，再决定是否保存选中。保存后还要新启动验证和更新草稿哈希；发布同步需另有授权。

目前没有宣称这两项修好，也没有完整动作、性能、打包或 Assignment 3 完成结论。本次没有编辑原生资产、继续开发、commit 或 push。
