# G1 录制04实际结果：实时性能画面

**后续用户验收：** 10月10日确认视频没有问题，人工视频/听感通过。只保留完整
视频04；其他24个游戏录制视频按用户授权删除，日志/截图/字幕/配音/源码保留。
下文为完成时快照，原片保留与审批待定已被后续记录取代，见[清理结果](G1_VIDEO_RETIREMENT_RESULT_20261010_ZH.md)。

2026年10月10日10:11EDT。本地审查稿完成，待用户审查视频和听感。
当天Assignment3报告仍不通过，本次只完成视频、不重新成稿。
参见[实施文档](G1_DEMO_RECORDING_04_20261010_ZH.md)、
[RP001](../../Failures/RP001-20261010-assignment3-report-focus/FAILURE_ANALYSIS_ZH.md)
及[MI018](../../Failures/MI018-20261010-native-stat-placement/FAILURE_ANALYSIS.md)。

## 成片与验证

本地：`Assets/LocalShared/Deliverables/Assignment3/DemoDraft04_20261010/Paris_G1_MVP_Draft_04_Live_Performance.mp4`。
158.233333秒（2分38秒），1920×1080、30fps/4747帧，H264/AAC48k立体声，
152,158,232字节；SHA256：
`8048195262f6dd45cc583985b1297227065bb9b4b2454d16763037564d073be0`。
英文字幕、A/Michael标准am_michael英文AI配音、原始游戏声音，全部1倍速。
English.ass/srt、AI_Michael.wav、TIMELINE/RECEIPT、QA截图和日志同目录保留。

三份新原始录像均通过完整解码、实际AV/普通输入及实时数字变化验收。成片严格
AV解码退出0，14张关键成片截图全部打开检查：字幕/面板清楚，小地图、血量、
弹药、保存提示完整。8段配音时窗均有声音；混音−18.53LUFS/−2.25dBTP、
采样峰值0.771730，不等于人工听感批准。计划4746帧与实际4747帧差一个CFR
边界帧，首次精确计数失败及解码日志保留。只读检查器允许最多一个边界帧，报告
实际时长；未修改视频或运行数据。

## 实时性能来源与限制

原生stat fps/summary/unit探测确实更新，但小字体覆盖小地图，停止该探测。
新独立诊断Game仅加opt-in只读Canvas面板/RHI依赖，用UE stat unit同源帧/
线程/GPU计时、FPlatformMemory进程RAM及RHIGetMemoryStats显存/驱动预算。
面板在UE中先绘制，再由OBS录入；后期仅加文字与配音，没有覆盖统计数字。
右上小地图左侧显示FPS/帧耗时、CPU Game/Draw、GPU/RHI、RAM、VRAM/预算、
draw calls/primitives。ms是耗时，不是利用率百分比；预算不是物理显存容量。
耗时0.9/0.1平滑、文字4Hz更新，缺失值N/A；导出30fps不是游戏FPS。

保持1玩家、2盟军、3德军，不增NPC。硬件i9-12900F/RTX3080/约31.79GB RAM，
1080p High/RT off/uncapped。包含诊断、输入辅助、OBS开销，仅代表本次捕获，
不是正式普通Game容量测量。F9/F6阻塞时保留最后一帧，恢复后真实耗时尖峰可见。
读档后短暂贴图预算警告和环境加载保留，不遮盖，也不归因于硬件单一原因。

## 真实流程与剪辑

| 成片区间 | 实际内容 |
| --- | --- |
| 0:00–0:41.77 | 动画/碰撞：走跑、静步、跳跃落地、蹲起、匍匐被碎石挡住、渐进转向、原换弹/开枪。 |
| 0:41.77–2:03.23 | 独立胜利：UE导航过桥、两盟军跟随、德军追击/消灭、金色圈/E存档、改变弹药、F9与终态尸体。 |
| 2:03.23–2:10.03 | 独立全新失败任务，明确说明分次录制。 |
| 2:10.03–2:30.70 | 首次伤害前剪去接近路程；真实伤害→Lost→F6→新Ready连续保留。 |
| 2:30.70–2:38.23 | 同次Ready尾段/实时面板说明，没有旧测量数值或过时组员待验证声明。 |

保存7/2、HP100，随后正常射击变6/2；F9恢复7/2、HP100，三尸体直接终态。
F9实际阻塞约8.096秒全部保留。胜利段德军追击但未开枪；敌军开火证据在失败段：
100→65→30→0，玩家不还击，失败保持约4秒，F6重开约8.013秒，Ready恢复
100血量/2+16弹药/2盟军/3守卫。获准普通原生UE输入，不传送或直接写入旋转、
血量、弹药、伤害、AI/状态。自动输入、AI配音、分次录制和剪辑有英文说明。

## 来源、保护与收尾

私有证据`tmp/g1-demo-draft04-20261010`，各次av_audit/admission.json：

- actions_panel_v1/PID7608，raw09:55:49，SHAf65a23601c7642ebf8401fa6187620a7ff94f83526c285542c7da2066f0f375f。
- victory_panel_v1/PID55608，raw09:58:59，SHA148239415920e9f022215e224b99e835e021b7a51e1933161f8dcfd6eb8fe683。
- defeat_panel_v1/PID8920，raw10:02:51，SHAd5507f058fe9ddcf3b69868ccbe5fb4a76e224c70b53f828d054fbecfbe1de7a。

三游戏正常退出0。仅这三新MKV从既有OBS输出目录移入04/raw，原OBS日志路径
保留并由审计说明映射，旧录像不删除。原生探测PID41628未发GO/录制，退出0。
新Gameaa11d14dde3ff346089a9fbb70647bfd84e220ec5cc70713fd5bd57fd2757a78，
46源冻结在recording_stats_v1/compiled_source_snapshot。仅Game编译退出0，
原V6 ParisDemoInput.cpp逐字一致，没有Editor/资产保存/recook/schema改变。
178源/冻结源/熟化闭包前后检查一致，普通audioV2/Game53ab36d9不变。
tmp/g1-demo-draft03-20261009/protection_video04_after.json的45行一致：42正式
源加3普通用户配置/日志文件，用户文件集合不变。模型/手指/武器/HUD/AI/存档
逻辑保留，每次独立UserDir。

诊断Game临时映射到03/recording_v4/Archive已获准路径，录制后已恢复原V6
Gamea6015c94；历史aa11哈希保留，runtime_remap.json记录当前映射。新诊断
Game独立保留。未来录制必须显式准备，当前launch.ps1哈希保护会拒绝直接重放。
OBS42432空闲，原Untitled Profile/Scenes及Scene2恢复且保留打开。
没有Git推送、SFTP同步或公开视频上传。人工视频/听感及课程完整验收待定；
组员第二台电脑试玩已通过。下一步共同讨论以四pillar为主线，结合AI/建模经验。
