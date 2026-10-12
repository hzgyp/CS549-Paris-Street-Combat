## 2026-10-11：历史父版已合入正式76版

此专项功能承接到人工认可的当前完整玩法版。旧普通试玩已退休。源码和检测收据保留。运行／开发以[正式基线](CURRENT_DEVELOPMENT_BASELINE.md)为准；不要把以下旧包当当前入口。

最新统一入口已增加UI，见[CURRENT_UI_REVIEW](CURRENT_UI_REVIEW.md)；本文及同名JSON保留地雷父候选身份。

# 当前地雷修订统一试玩候选

2026-10-11，等待人工试玩。根入口 `PLAY_TACTICAL_EQUIPMENT.cmd` 指向 `tmp/Playtest-G1-PressureMine-20261011`；63文件源为 `Unreal/Variants/G1PressureMine20261011/Project`，最终authoring为candidate_mine_v2，精确身份见同名JSON。

格纹陷阱已替换为军绿盘形地雷，双方落地脚底接触触发一次；发现后显示实际位置/距离，两米内有效视线瞄准并按住E两秒拆除，松开取消。G/Q和有限弹药箱保留。三个德军全灭单独解锁圈内E保存，完成后危险仍可致死并进入Lost，关闭旧保存窗口，F9/F6保留。

详细见[新实施文档](MissionLoopV1/PRESSURE_MINE_IMPLEMENTATION_20261011_ZH.md)与[结果和UE实图](MissionLoopV1/PRESSURE_MINE_RESULT_20261011_ZH.md)。23项最终Game实跑通过，夹具/短性能边界明确，等待用户美术与自然试玩。独立UserDir G1PressureMine20261011，未迁移原档。正式基线仍为enemy-clear v3；现有Editor继续开启，无新mine Editor/PIE验收、自动发布或清理。mine_v1与不可达Waiting测试的mine_v3停用保留，当前交付只用v2。
