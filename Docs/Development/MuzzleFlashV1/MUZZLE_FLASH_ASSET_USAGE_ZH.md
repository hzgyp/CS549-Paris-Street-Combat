# 枪口火焰本地正式资产使用说明

2026年10月8日。本地接入完成，本请求不包含发布。
[英文原文](MUZZLE_FLASH_ASSET_USAGE.md)。
[验收结果及保留历史](MUZZLE_FLASH_FORMAL_RESULT_20261008_ZH.md)。

## 已安装内容

正式工程`Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`已启用独立
`ParisMuzzleFlashV1`运行时插件。保存配置为
`/Game/ParisCombat/VFX/MuzzleFlashV1/DA_PC_MuzzleFlashV1`，选用已购
`/Game/MsvFx_MuzzleFlash_Pack/Prefabs/Niagara_Riffle_MuzzleFlash_01`系统；
供应商原名确实拼为**Riffle**。

本地内容唯一家目录为
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content`。
正式工程已有的Content父junction直接提供两条子路径：

- `MsvFx_MuzzleFlash_Pack`：25个供应商原字节依赖包。
- `ParisCombat/VFX/MuzzleFlashV1`：1个保存的原生配置资产。

3个插件二进制文件位于
`Unreal/ParisStreetCombat/Plugins/ParisMuzzleFlashV1/Binaries/Win64`。
合计29个新文件，不是29个新商业资产；没有新建子junction。商业包、保存DA、
二进制及证据图片继续私有，本次不Git/SFTP/Catalog发布。

## 在现有项目中的用法

保留原人物、认可的原生握枪策略和原玩法开火入口，不要再为每把枪添加重复
Niagara生成、计时器或蓝图开火驱动。原生世界子系统观察真实已提交ShotSequence，
在当前实际显示、已验证的步枪上挂一份枪火。它不发起子弹，也不改弹药、伤害、
射线、人物姿势、后坐力或AI。

Game/PIE世界自动读取保存配置，等待Niagara就绪，并周期发现兼容的已就绪人物。
玩家须已有初始化的认可第一人称原生Actor；NPC须已有初始化的原生握枪适配器
及WeaponAppearance。必须精确匹配保存配置中的步枪Mesh，仅原M1和已选FineWoodV15。
装备显示被隐藏、未注册或不可用时，不生替代效果；新绑定以当前序号为基线，
不补播此前的枪声/枪火。

代码周期发现机制可接后来兼容且就绪的角色；本请求正式测试验证原六人队伍，
不等于所有后续生成、武器、骨架、地图或多人场景都通过。不同武器/骨架须单独
测量和审阅配置，不能直接复制M1偏移。

| 固定选定项 | 值 |
| --- | --- |
| 特效实例比例 | 0.25，用户已认可 |
| 实例SpawnRate | 20；供应商原资产不变 |
| 普通Deactivate请求 | 0.10游戏秒；不宣称实测精确回调年龄 |
| 完成标准 | 真实IsComplete，8秒上限内 |
| 挂点 | 各步枪保存的实测局部枪口；pitch0/yaw90/roll0 |

冷却/空弹/忙碌/死亡拒绝的开火不出火焰。换弹、死亡、reset、装备隐藏再恢复会
取消自有显示且不补播。真实完成与取消分开统计，强制销毁不算完成；世界结束
清理自有特效。销毁NPC原装备仍不是通过项，先前由此触发的认可握枪错误保留。

## 已验证范围与未验证项

独立formal_transactions_v1_20261008从正式安装读取此配置，无私有Python
Configure及命令行插件启用覆盖。20次原真实开火提交、拒绝/换弹/取消、两发
实际同时存活及原生非空世界清理2→0通过。39张本轮新原图逐张实看，玩家06/
盟军20/德军32有清晰主火焰，独立视觉及审计通过。运行时观察是原生机制；
这次有界测试仍使用诊断Python夹具、pre-actor开火队列及延迟审阅取图，没有
新增Python人物姿势驱动。

这不等于普通手控/无Python启动、全城/近墙可见性、确定性可靠性、FPS、Shipping、
组员机器或完整MVP/课程验收。完成本地范围后后台后续检查已停止，收尾不再
需要新启动引擎。

## 维护约束

已读Failures/README、AN009/AN010、成对正式计划及请求/就绪/生命周期/取图/
继承绑定修正。本次只新增选定显示插件、配置、资产、一条启用行及共享保护
读取器窄接，不改认可玩法或正式地图。早验为严格编译、35离线+4共享保护测试、
703保护、68原件、25私有依赖和29安装文件准确；保护只推进授权描述符一行，
其余702准确。私有证据位于上述唯一工作区的`Evidence/MuzzleFlashV1`。

任何哈希/根路径/配置/严格日志/运行/视觉/时限漂移即停止。保留占用身份、原回执
及复制失败，不重跑失败机制、不覆盖资产、不豁免或扫参数/相机/取图时序。
不可变安装证明有意保留Formal前的false标志，由后续Formal审计证明最新完成。
额外验证或不同适配须新有界计划及真实进程检查。
