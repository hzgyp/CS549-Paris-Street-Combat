## 2026-10-11：人工逻辑通过并采用正式76版

用户确认逻辑无问题，仍有衣袖遮挡待修。已正式采用本文件的Game／源码身份；当前入口／本机清理见[正式基线](CURRENT_DEVELOPMENT_BASELINE.md)。以下原始阶段记录保留为历史；不再视为人工待审。

# 当前手持投掷物与库存轮换修订

2026-10-11，本地统一候选，待人工试玩。普通入口 `tmp/Playtest-G1-GrenadeEquip-20261011/PLAY_GRENADE_EQUIP.cmd`；源码 `Unreal/Variants/G1GrenadeEquip20261011/Project` 共76文件，Game `b5357cd4ff39454ec40d72ba96ce8ab379f0e039c83b6170263f631e45c4124d`。原source75被用户否决，原包／源码／日志／图保留，见MI045。

滚轮只循环步枪及库存>0的投掷物，正反向均跳过空类型。两种都用完时保持步枪，滚轮不隐藏枪、不变姿势、不影响鼠标按压。切到投掷物采用已存在的Rifle_Grenade_Throw_Loop作为临时FP就绪源；左键Start准备、Loop保持、Far投出，动作结束回原步枪指姿。原角色身体／镜头、原模型／手指常量及枪械／存档代码保持。

手雷本来有模型，旧掌指中点将其遮在手后；显隐诊断确认渲染正常。本版按实际外壳半径及原动作掌面确定挂接，实际有手的MkII和烟雾就绪／长按均已复看。原模型尺寸／纹理不变，普通入口不隐藏手、不改镜头。详细全程接触与全部运动转换待人工试玩，图和投影不等于全面接触验收。

15项同一Game检查exit0，含真实投完两枚手雷、正反跳过空手雷、真实投完两枚烟雾、全空保持枪及原射击、投掷／烟幕／枪械P1／地雷补给／全灭保存／装备与旧档恢复／菜单暂停与确认／死亡重开及当前人数性能记录。1754 native、父75／普通100文件／用户档／Catalog／全部除exe外运行文件保持。原BeginThrow／CommitThrow／PlayThrow／ThrowTick／EndThrow／BallTick／Blast逐字相同；模型／枪械／保存／AI／导航／死亡主体保持。

独立UserDir `G1GrenadeEquip20261011`／前缀`ParisGrenadeEquipV2`。作者目录candidate_grenade_equip_v1/Project含final build_v4；v1旧握点投影失败、v2遮挡与见证提前、v3显隐诊断保留于MI046／MI047。正式source52和根入口保持，UE Editors仍开启。本轮无正式采用／Git／SFTP／清理／录像或第二电脑新验收。

方案：[实施文档](MissionLoopV1/GRENADE_EQUIP_REVISION_IMPLEMENTATION_20261011_ZH.md)；结果：[实测结果](MissionLoopV1/GRENADE_EQUIP_REVISION_RESULT_20261011_ZH.md)。
