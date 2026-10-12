## 2026-10-11：历史父版已合入正式76版

此专项功能承接到人工认可的当前完整玩法版。上一正式52普通包仅作为既有恢复依赖保留。源码和检测收据保留。运行／开发以[正式基线](CURRENT_DEVELOPMENT_BASELINE.md)为准；不要把以下旧包当当前入口。

# 已人工通过的清场 checkpoint 正式基线

2026-10-10，用户人工复验最新清场 checkpoint v3 无问题，明确选为正式基线。
唯一当前普通试玩为 `tmp/Playtest-G1-EnemyClear-candidate_v3-20261010/PLAY_G1_REVISION.cmd`；项目根目录
`PLAY_CURRENT_G1.cmd` 指向同一入口。用户存档继续使用 `%LOCALAPPDATA%/ParisStreetCombat/G1EnemyClearv320261010`。

当前源：`Unreal/Variants/G1EnemyClearCheckpoint20261010/Project`，精确52文件；制作工程：
`tmp/g1-enemy-clear-checkpoint-20261010/candidate_v3/Project/WW2FranceLiberation.uproject`。Game SHA256 `b40409b08830cc0e1d306ceab0575d7e61db382f50853426bbda58d08f385079`；
manifest SHA256 `66d8c6e3fc005090ebe44e31f6a8dabd0fdbe1871ffed613cb3769f5b334508a`。进入 Editor 前重新构建匹配 Editor，不能使用旧缓存。

本基线累计保留菜单选择、步行2.2/跑步4.5米每秒、8+10弹药、已接受德军角落布局、
雷达/HUD和audioV2；登记三名敌军全灭即完成并解锁存档圈，不再要求远岸点/小队/姿态/停步。
圈内主动E，实际写盘及回读通过后显示成功窗口，确认后同次进圈不再提示或重复写。
模型、手指姿态、原动作、枪械/资源、导航/AI、V5存档校验和死亡终态保护。

既有有限原生菜单37、清场26、独立恢复31、旧V5恢复31项通过，最新人工复验通过。
隔离清场诊断不是新增自然战斗/导航压测；本次选择没有新增引擎测试。
衣袖/ADS/弹夹动作、HUD精细化、玩法与大量NPC逻辑/压测等后续工作保留。

旧试玩和编译缓存已按 [实施](G1_CHECKPOINT_BASELINE_ADOPTION_20261010_ZH.md)
及 [结果](G1_CHECKPOINT_BASELINE_ADOPTION_RESULT_20261010_ZH.md) 清理。
旧源、日志、失败、图片、用户存档和必要恢复锚点保留；
[恢复映射](G1CheckpointBaselineAdoption20261010/RECOVERY_MAP_20261010.json) 支持旧路径。
JSON选择器为当前身份依据，早前日期的源/选定版本说明属于历史。

本次只合并本机正式基线。现有SFTP课程下载、已批准视频和旧版本第二机记录仍对应audioV2；
不冒称已同步最新52文件，没有自动commit/push、远端清理、课程PDF或视频修改。
