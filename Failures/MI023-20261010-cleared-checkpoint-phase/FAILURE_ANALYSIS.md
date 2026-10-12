# MI023 — 清场后的 checkpoint 被过桥阶段锁住

2026-10-10。用户实际试玩 checkpoint dialog v3 后报告三名德军已死亡，
保存窗口仍显示 WAITING TO SAVE / Finish securing G1 before saving。
关闭游戏后原始日志复制保留于 `tmp/g1-enemy-clear-checkpoint-20261010/manual_failure/`，
原用户目录文件、当前源/Game 与新冻结清单保留；本记录不改变历史测试结果。

日志有 Crossing 与 checkpoint enter/prompt，但没有 Clearing/Occupying/Won；
两次请求 30 秒后失败且 serial=0。checkpoint 开放说明原封闭登记的三个敌军死亡
已经被认可，不能把此问题解释为敌军尚存或硬盘写入失败。

旧流程只允许玩家进入半径 250cm 的指定 FarBankFeet 检测区后，
Crossing→Clearing→Occupying→Won。玩家可以实际过桥并完成清场，却未触发该区域；
存储又要求 Won、小队过桥、站立和所有存活角色安全停稳。
窗口里的“停步、站立”通用提示与真正的 phase blocker 不一致。
旧完整路线诊断经过该特定点、旧存储诊断从 Won 存档开始，均没有覆盖这次人工路线。

用户新指令明确：所有 checkpoint 的保存任务门槛改为完全消灭敌人即可。
这是玩法规则变更，取消旧过桥/占领/小队/姿态/停步门槛；不是放宽存档身份、
资源守恒、死亡合法性、checksum 或回读校验，也不是小队实际过桥通过的新证据。
保留 MI005/MI020 的历史小队失败及后续实际过桥记录。

新实施见 [清场判定计划](../../Docs/Development/G1_ENEMY_CLEAR_CHECKPOINT_IMPLEMENTATION_20261010_ZH.md)。
新的有限诊断必须明确覆盖 0/1/2 敌死亡不解锁、最后一敌死亡时
Crossing 且队友仍在河对岸也能完成，以及移动/低姿态确认的实际保存和独立恢复。
诊断摆位/AI hold/原死亡端点须注明，不能描述成自然交火或新的导航压测。

## candidate_v1 诊断注释吞掉同行初始化

新诊断初始化本来为单行函数，插入的 `//` 注释吞掉了同行后面的输出路径、
delegate 初始化和闭合括号，编译报 C2601/未匹配括号。尚未启动新游戏。
保留 candidate_v1 的 52 文件 Project、prepare/build/log；任务完成及事务改动不是本错误来源。
不同 candidate_v2 仅改成闭合的块注释，原诊断场景、接受条件和 production 源不变；
不能在失败 Project 上修补或复用失败 identity。

## candidate_v2 取消蹲姿门槛后暴露恢复中心问题

v2 Game 构建成功，隔离 clearance_v1 的 26 项和独立 restore_v1 的 31 项
在各自窄范围通过（真实门槛/写盘/资源/第一帧恢复）；原结果保留。
进一步比较三秒后玩家位置：保存的蹲姿胶囊半高 60cm，原 lifecycle loader
恢复站姿半高 96.2331619cm，但原 journal 只记胶囊中心。
加载第一帧仍等于旧中心，随后落地解穿造成实际 34.6996713cm 位置漂移，
含 X/Y 移动，因此 v2 不通过新的低姿态存储位置验收，不能以原两份 pass 掩盖。

不同 v3 保留原 CaptureSnapshot/ValidateSnapshot/ApplySnapshot、字段和动作实现，
只在保存 payload 的 player location.Z 加“原站姿半高−当前半高”，
用原 capsule scale 计算；不修改玩家现场姿态/模型/手指、任何资源或其他角色位置。
原双槽写盘/回读部分仍逐字保护。新 identity 重新实测三秒地面稳定位置，
若仍漂移，停止本候选分析具体障碍，不用放宽原位置验收制造成功。
