# 德军步枪 Aholo 分件结果

2026-10-03。**任务运行成功，但没达到我们需要的分件效果，不能算枪模修好了。**

- 只提交一次任务3920959，消耗30赠送积分，实测余额240→210。没有充值、重生成整枪或连续追加任务。
- API报价不支持本项；提交前已在官方计费页确认优惠30/原价40，并先补写预算变更，预留40赠送积分上限。
- 实际只得到两个网格：整枪261,789三角 + 背带37,690三角。木托、机匣、枪栓、瞄具仍在整枪网格里，**没有拆开**。
- 独立全量检查确认原299,479个三角面的坐标、绕序、逐角UV和两个2048贴图字节一致。没有新切坏木托，但也没有精修掉原来的软细节。
- 实看15张侧/顶/底/斜视、PBR、分色及独立部件图，判定本次分件对修木托接口帮助不足。按一次上限停止，不再重复消耗积分。
- 原底模、旧两轮资产/源码以及游戏43原生文件+7动作文件均未改；没有动M1、UE或发布SFTP，也没有commit/push。

![实际分件：橙色仍是整枪，蓝色仅背带](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/evidence/part_audit/colored_quarter.png)

本地检查模型：[Blender场景](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/evidence/fresh_import/incoming_inspection.blend)；[原样分件GLB](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/incoming/kar98k-parts-v3-0-recovery.glb)。源码在 `Tools/AssetCreation/GermanRiflePartSplitV3/`，完整技术结果见同名英文稿。

下一次若继续本地精修，应沿真实表面/材质边界做一个小接口验证，保留木托UV和形体，不再硬切盒子、跨轮廓封凸包。自动分件不是自动按木材/金属拆分，不能靠再提交相同任务假定它会做对。成熟枪模或有限人工拓扑适配仍是备选。德军生产枪模缺口仍未关闭。
