# 德军步枪精修 V2：有局部进展，但整枪未通过

2026-10-03。[英文原件](GERMAN_RIFLE_REFINEMENT_RESULT_20261003.md)。依据用户认可底模方向、允许继续本地精修，使用Blender建模流程，先读GP001/FP001并写了[实施稿](GERMAN_RIFLE_REFINEMENT_V2_ZH.md)。用户没有验收这轮新结果。

这轮把机匣、可见枪栓及连接的拉机柄、照门和枪管/准星做成独立命名的光滑金属部件。保留248,443个原面，未改原面UV误差为零，不焊接不减面。但**整枪画面仍不合格**：木托接口有接缝/缺口，封口把不同切边跨连成薄片，右侧枪栓旁和木托远侧很明显；金属高光也过强，部分支承形状仍像积木。没有把它当更好的baseline，不替换原底模。

本地草稿265,976三角、46个网格，GLB15,899,872字节，源blend15,686,768字节。约1.101m长（实际尺寸以validation.json为准），是高细节草稿，不是30k运行低模；没有LOD、UE、性能、历史、专用换弹验收。仍保留馆藏后配帆布背带，不认定德军制式。

实际检查：Blender5.2.2下重导入13项基础检查通过，新金属在只读焊接诊断副本中闭合/法线朝外；这不代表原木托及补面整体闭合。19张最终灰模/PBR/枪栓分离图片均已打开查看，视觉失败明确，不用数值覆盖。整枪分离图只是外观分件证明，不是真实拉栓动作。

独立重跑三角、JSON和作者指标相同，但GLB SHA不同：第一份`6f4261db...63249fd`，重跑`1fa3432f...4d5cc348`。只读诊断有18个UV/索引缓冲不同，具体非确定性原因未确认，不能写“字节复现通过”。两份保留。首个构建前Python错误、第一候选法线朝内、第二候选切口，以及最终薄片都保留，不抹成成功过程。第二候选看了五张关键图，其他生成图不冒称逐张实看。

原始GLB哈希、之前77个私有文件/7脚本及当前43个原生/7动作草稿均核对保持不变。本轮零云调用/零追加积分消耗，不动M1、游戏或角色，不启动UE，不传SFTP，不选Catalog，不commit/push。240是上轮最后核对的额度，本轮未重新查账。

[精修草稿blend](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/blender/interface_finish_v3/Kar98k_RefinedMaster_V2.blend) · [GLB](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/blender/interface_finish_v3/Kar98k_RefinedMaster_V2.glb) · [带相机审查场景](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/evidence/final_v3/Kar98k_RefinedMaster_Review.blend) · [源码](../../Tools/AssetCreation/GermanRifleRefinementV2/refine_rifle.py) · [哈希清单](../../Assets/Integration/GERMAN_RIFLE_REFINEMENT_INVENTORY_20261003.json)

本轮未通过的整枪效果：

![未通过草稿](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/evidence/final_v3/pbr_three_quarter.png)

顶面最能看出错误薄片：

![封口薄片](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/evidence/final_v3/clay_receiver_top.png)

本工作包到此停止局部切盒/凸包封口路线，记录[GP002](../../Failures/GP002-20261003-kar98k-interfaces/FAILURE_ANALYSIS.md)。下一次先识别连通切边或真实材质边界，只验一个小接口再扩展，不能再跨不相关轮廓做凸包、加板遮盖、扫切盒或自动选本草稿。参考底模仍保留原样；德军可用于游戏的资产缺口没有关闭。
