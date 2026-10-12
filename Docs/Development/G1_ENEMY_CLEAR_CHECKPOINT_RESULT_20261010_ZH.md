# G1 清场即可完成与保存修复结果

2026-10-10，本地候选 candidate_v3，人工试玩待复验。
用户最新规则优先于旧版小队到达/占领阶段门槛；旧小队测试结果作为历史证据保留。

## 已修复

三名登记德军实际死亡即直接 Won 并解锁圈，Crossing 阶段也可完成，
不会因漏过指定远岸点或队友尚未过桥卡住。0/1/2 名死亡不能解锁。
保存提示、E/F5 发起交互、失败重试和实际存储共用清场条件；姿态、速度、
小队 Ready/位置和安全等待秒数不再作为存储 admission。
仍需在金色圈内主动按 E，成功后 OK 窗口和关闭询问保留，同次进圈 E/F5 不重复写。
双槽序号、身份/资源守恒、原存档 schema/checksum、写盘及回读校验保持原字节逻辑。
保存低姿态时仅把 player 的位置高度按原站姿胶囊换算，供原 lifecycle loader
恢复同一脚底位置；现场姿态、其他角色位置与存档字段均不改变。

## 验证与范围

| 独立运行 | 状态 | 检查数 | 退出码 |
| --- | --- | ---: | ---: |
| menu_v1 | pass_menu_input | 37 | 0 |
| clearance_v2 | pass_enemy_clear_checkpoint | 26 | 0 |
| restore_v2 | pass_fresh_process_restore | 31 | 0 |
| legacy_v1 | pass_fresh_process_restore | 31 | 0 |

clearance 是明确的隔离门槛回归：原新游戏六人阵容、诊断玩家摆到 G1、
AI hold、逐个执行原 PC_Die 端点；不是自然交火或实际移动过桥。
实测最后一敌死亡时任务仍来自 Crossing、两名活盟军均在对岸且 transit 未完成，
立即 Won；移动/蹲姿圈内 E 直接进入 Saving，真实写盘回读成功 serial1。
隔离的下一槽只读造成真实写失败、旧槽和序号不变，Retry 后成功 serial2。
全过程无 Waiting/Finish securing，写盘均发生在 Saving 已画出之后。
成功窗口/提示消失、重复键、圈外交互拒绝、F9/F6 与新进程 serial2 恢复通过。
legacy 单独读取原 V5 已验证 journal，尸体第一帧及三秒终态保持。
模型/手指/枪械和固定 NPC 位置、导航碰撞/AI 实现没有变化。

52 源文件只改任务/HUD、交互 admission、有限诊断三个 cpp；反射声明不变。
1754 原生资产、父源/Game、当前用户文件、Catalog 与七个原受保护区段通过。
旧失败 candidate_v1 注释编译错误及 v2 低姿态恢复中心偏移见 MI023，原 Project/日志保留。
没有进入 Editor、录制、清理、Git/SFTP 发布或新自然交战/小队/性能/第二机验收。

## 可复查身份与入口

- 正常试玩：`tmp/Playtest-G1-EnemyClear-candidate_v3-20261010/PLAY_G1_REVISION.cmd`。
- 独立正常用户目录：`%LOCALAPPDATA%/ParisStreetCombat/G1EnemyClearv320261010`，原 V5 格式。
- Game SHA256：`b40409b08830cc0e1d306ceab0575d7e61db382f50853426bbda58d08f385079`。
- 52-file manifest SHA256：`66d8c6e3fc005090ebe44e31f6a8dabd0fdbe1871ffed613cb3769f5b334508a`。
- 新源：`Unreal/Variants/G1EnemyClearCheckpoint20261010/Project`；当前 Project：`tmp/g1-enemy-clear-checkpoint-20261010/candidate_v3/Project/WW2FranceLiberation.uproject`。
- 私有原生结果/图片/保护清单：`tmp/g1-enemy-clear-checkpoint-20261010`。

人工复验：从新任务自行过桥、击杀三敌；无需特意经过远岸点或等小队。
进金色圈按 E，查看 CHECKPOINT SAVED / OK；关闭后不应再有 E SAVE / ESC LATER。
F9 检查死亡德军、资源与已完成任务；F6 重开应有三名活敌军且圈再次锁定。
本轮仅 Game 构建；后续 Editor 入口必须重新构建当前匹配源，不能使用缓存 Editor DLL。
