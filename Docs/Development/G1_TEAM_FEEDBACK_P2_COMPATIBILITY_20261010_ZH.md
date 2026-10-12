# ADS 与 M1 换弹：当前资产兼容性检查

2026-10-10。本批 v6 的 `ammo_v3` 原生 Game 只读库存及 22 项功能检查已通过。
原始证据：`tmp/g1-team-feedback-p1-20261010/checks/ammo_v3/RESULT.json`。
这份记录用于决定下一步，不把动作名称或弹药功能通过当成视觉验收。

已读 AN003、AN005、WEAPON_BASELINE_AND_SIMPLIFIED_RELOAD_V1、
RELOAD_APPROVED_GAME_INTEGRATION_RESULT、RELOAD_REPAIR_V5 及本批实施文档。
原 D059/M1 预览接受不等于 US Paratrooper 连续手臂适配通过；旧换弹绑定/
权重/偏移试验仍停止，不能用新名称重跑。

| 检查项 | 实际采用内容 | 对后续实施的含义 |
|---|---|---|
| 人物 / 手臂 | 既有 US Paratrooper simple UE582 与 ContinuousArmsV3；正式握持策略保持 | 不新建人物、不换已接受手指/模型 |
| Ready 来源 | W2_Stand_Aim_Idle_IP，3.266667 秒 | 是当前握持来源；名字含 Aim 不证明铁瞄准星与相机对齐 |
| 当前移动 | ABP_PC_Allied_Stride_v1；真实 cooked BlendSpace 17 样本，X/Y 最大 300 cm/s | 150/300 样本分别已校准 RateScale；220 步行保留倍率 1，超 300 的普通移动才补偿 |
| 当前换弹 | RifleAnimsetPro InPlace/Rifle_Reload_2，clip 2.166667 秒，ReloadPlayRate 0.524194 | 原壁钟完成时间约 4.133 秒；动画相位提交点 1.083333 秒。不能把泛用动作说成 M1 八发弹夹插入 |
| 当前实际枪体 | Engine.StaticMeshActor，USParatrooper/Sm_M1_Garand，一个 StaticMeshComponent | 此枪体没有当前执行的独立枪机/弹夹动画字段；没有本批新增的可移动机件或弹夹组件 |
| 资源事务 | 八发后空枪拒发；原换弹 0+10→8+2；重开 8+10，总量原 18 | 功能可继续使用；不证明手、弹夹、枪机与声音的完整视觉配合 |

Content 文件名检索发现既有 AimOffset/通用 Rifle reload 与旧失败 proof 资产；
没有找到名为 clip/magazine 的 M1 弹夹 uasset。文件名检索不能证明所有供应商
原件都没有相关零件；**当前正在运行的枪体与动作没有已验证的 en-bloc/ADS
实现**是本次可以确认的结论。Jingdi 的 YouTube Shorts 引用此前抓取受限，
仍未宣称已观看；不能用未观看视频指定动作细节。

本次也已定位既有供应商 `SK_M1_Garand.uasset` 及原修复工作区的 FBX/blend，
并核对 [原兼容性检查](../../Assets/CHARACTER_COMPATIBILITY_AND_REPAIR.md)：
原记录该枪为单骨骼、3923 三角面，交换 FBX 无 armature/weights，只可作为
刚体参考。它的存在不等于已有枪机/弹夹动作；本批没有替换当前 Sm_M1_Garand，
没有重新导入、拆件或重启已失败的换弹绑定试验。单骨骼结论来自原检查记录，
不是本批再次打开 UE/Blender 得出的新模型验收。

下一步先清点供应商原件中的 M1 机件、八发弹夹与兼容动作，检查骨架/时长/
握持关系。若有兼容资产，再写单独有限适配文档：保留原 Ready 手指和枪械
事务，先做独立入/出 ADS 或换弹关键相位的视觉门槛，随后测近墙、射击、
部分备用弹药、重复 R、中断/死亡与恢复。没有兼容资产时先列出采购/专业
适配或简化表达的选项，未经用户选择不购买、不改正式人物/手指/枪体。

本批只完成可读准星与兼容性检查，未新增 ADS 或八发弹夹动画。衣袖遮挡仍
列为旧动作的后续问题。若早期出现手臂断裂/衣袖遮挡、模型或手指漂移、
枪械事务变化即停止；不得自动恢复 AN003/AN005 的旧权重、绑定或偏移试验。

## 继续收尾时的供应商原件清点

用户要求完成后一次性检查。本轮只读清点完整 character-20261001-v1 原件目录
的 590 文件（不是再次采购/导入）：名字匹配 reload 9、aim 24、M1_Garand 7，
magazine/enbloc/clip/bolt 均为0。9个换弹文件包括 RootMotion/InPlace 的
Rifle_Reload_2、Rifle_Crouch_Reload、Rifle_Crouch_Reload2、Rifle_Prone_Reload
以及另一组 Prone_Reload_Rifle；都是已有通用/低姿态动作，没有由此确认 M1
弹夹插入。私有逐文件路径/大小/SHA 和原实际 Ready/Reload 使用项已存于
`tmp/g1-team-completion-20261010/supplier_inventory.json`。原件未改。

名字计数不证明未命名嵌入零件也不存在；但结合当前实际刚体枪、原单骨骼检查
和停止的袖子试验，现有组合没有可直接采用并已验证的 M1机件/弹夹/手部换弹
或瞄具对齐。不能把 AimOffset 名字、FOV缩放或保持数值守恒写成实现完成。
本轮继续独立完成点位/匍匐功能验证，P2资产缺口统一进入最终人工检查清单。
