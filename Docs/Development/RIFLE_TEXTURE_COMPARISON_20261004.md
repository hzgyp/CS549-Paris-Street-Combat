# M1 / V11 texture assessment — read-only plan and evidence

2026-10-04. User asks to compare current Allied rifle and V11 German candidate textures, not modify them. Blender modeling skill is used for rendering/inspection only; no modeling/export gates or new asset are necessary.

Read Failures/README, GP004 and GP009 plus the previous Allied reference study. Unlike GP004, do not classify/repaint surfaces. Use V11 actual exported GLB (GP009), and the already repaired portable M1 exchange with its own packed material/normal-green conversion. M1 source is related to current Sm_M1_Garand; Blender portable shading is not exact native UE master-shader/game-light parity. Do not transfer its commercial textures or claim new native acceptance.

New `Tools/AssetValidation/blender_rifle_texture_compare.py` renders both at real metre scale, long axis +X, bounds-centered for display only, identical studio/world/exposure/AgX/samples/cameras. Required evidence: whole quarter, receiver close, stock close. Separate new private `20261004-texture-comparison/compare_v1`, six PNGs, small saved inspection scenes and report with input/output hashes. No source saves or original-library load. Early check: sources loaded with visible wood/steel textures and correct orientation; if missing or axis wrong, stop before aesthetic judgment. Preserve failed identity; at most one diagnosed presentation correction, no material edits. Stop after the six images are inspected and wood/steel/wear differences explained. No cloud, UE/M1/V11 mutation, SFTP/Catalog or commit/push.

## 实际对比结果 / Actual assessment

Blender5.2.2LTS 新进程退出0，六张原图与拼接图已实际查看。轴向/尺度及贴图门槛通过，未作展示纠正。相同1200×700、40采样、AgX Medium High Contrast、曝光0、伽马1、三灯/环境/固定相机。M1独立模型和D/N/ORM三图、V11选中GLB共五个输入制作前后SHA完全一致；没有UE/游戏/原库写入或新的资产导出。保存的是独立只读检查场景，不是生产选择。只有Material/World.use_nodes未来弃用提示。

| 项目 | 盟军 M1 | 德军 V11 |
| --- | --- | --- |
| 木托 | 暖棕、不规则细木纹/划痕、边缘剥落和局部色差明显 | 偏灰棕、宽且规则的平行条纹；轮廓清楚但表面过匀，近景略像涂层塑料 |
| 钢材 | 明暗/磨损区域、污迹与细法线层次更丰富；本棚灯下银亮反光偏强 | 蓝黑钢区分清楚，反射带平顺；细划痕/粗糙变化不足以形成明确使用痕迹 |
| 旧感 | 长期使用的战场道具 | 接近新枪，仅极轻旧感；上一轮V11做旧幅度不足以匹配M1层次 |

结论是贴图内容/粗糙度层次有差距，**不是重做枪形或堆三角面的问题**。V11棕木1024² D/N/ORM三图，M1三图均2048²；单纯提分辨率不会自动补出自然纹理或合理磨损。M1金属的银亮程度来自这一可移植材质/棚灯组合，不等于游戏内真实亮度，不作“更亮就是更好”的判断。这里是人工比较意见，不是用户否决V11形体或纹理、历史/UE验收。

建议（本轮未实施）：保留已认可V10/V11枪形，优先更自然的非周期木纹/局部油色，再给枪托边缘和常接触钢件适度磨损；不需要复制M1的大面积掉漆，也不复制商业贴图。下一次修改仍须用户授权及独立有界计划。

English: M1 has much richer irregular grain, local abrasion/color/normal variation; V11 is coherent but overly uniform with broad periodic-looking wood bands and weak aging. Its dark bluing is not inherently inferior to M1's bright studio response. Main remaining difference is authored surface content/roughness, not triangle density. Proposed natural grain/local wear is advice only, not implemented or newly authorized; no UE shader parity or production acceptance claimed.

[实际六图/输入哈希报告](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-texture-comparison/compare_v1/comparison.json)。[渲染源码](D:/0.Rutgers/CS549/Project-New/Tools/AssetValidation/blender_rifle_texture_compare.py)，[拼图源码](D:/0.Rutgers/CS549/Project-New/Tools/AssetValidation/compose_rifle_texture_comparison.py)：只等比缩小/加标签，不裁切或修图。所有二进制与图片保持ignored LocalWorking，未SFTP/Catalog/commit/push；不重新整批审计旧资产。

![左M1右V11，同尺度/棚灯/相机](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-texture-comparison/presentation_v1/m1_vs_v11.png)
