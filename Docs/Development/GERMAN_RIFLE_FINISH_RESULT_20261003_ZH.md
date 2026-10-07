# Kar98k V7结果：整枪法线改善有效，尚未精修完成

2026-10-03。按“继续修到差不多”开展整枪检查；先读GP001–005，先写V7实施文档，再用Blender建模技能执行。技能要求促使本轮先处理大片表面、固定多视角对比，并独立重跑/重新导入；不是只修一个球头。

## 已修好的部分

木托、机匣的大片碎片状高光明显减轻。采用跨UV接缝的面积加权/角度过滤法线，不焊接、不动任何顶点、面、UV、贴图或原材质；V6球头与背带保留。这是有效的着色改进，但近看机匣、照门、枪口结构仍像软块，贴图语义不够干净，完整可动枪栓仍未完成。

实际重新导入GLB的整枪图：

![V7整枪右侧，原贴图](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7/fresh_review/pbr_whole_right.png)

近景的软塌结构仍在，不算通过：

![V7机匣近景](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7/fresh_review/pbr_quarter.png)

## 未通过的部分

surface_v1 可见面手工描绘误选木肩/枪托孔及被独立背带遮挡的木头。唯一允许的surface_v2纠正纳入背带遮挡、扣除实际可见木肩、收紧轮廓。主要误选减轻，但保险/柄颈/护圈仍漏选，钢木边界锯齿、前护木仍含不确定区域，全部11图已检查。按预定停止条件，不再增加轮廓/摄像机，不使用失败选区上实际金属材质或修形；新增GP006保留分析。

## 导出验证和文件

- 2网格、299479三角面；暂定1.105m，不是NPC性能验收。
- 所有V6顶点/面/角UV、贴图/材质精确不变，背带原法线不变。
- 干净源码重跑GLB字节一致，SHA `34368dbb3e40828fd58c07ae668585d0f63fcb081d480b927bb17b3c15185c2d`。
- 原始GLB和Fresh Blender的三角位置/UV最大误差0；法线不逐位相同：载荷最大方向差0.00487912度，导入Blender最大0.16327650度。
- 两次较严的法线分量断言失败保留在GP006：首个traceback但Blender退出0，第二次设置python-exit-code1退出1；未假称通过。最终采用0.01/0.3度方向容差，具体编码根因仍未证明。
- 生成70张图，实际检查56张主证据；14张重跑重复图未单独复核。旧269份私有文件/39份源码、50份原生/动作和4份M1参考SHA保持不变。

[Blender候选](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7/normals_v1/Kar98k_Normals_V7.blend) · [GLB候选](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7/normals_v1/Kar98k_Normals_V7.glb) · [生成源码](D:/0.Rutgers/CS549/Project-New/Tools/AssetCreation/GermanRifleFinishV7/normals.py) · [独立验证](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7/independent_audit_v3.json)

全部仍在LocalWorking；未进SFTP/Catalog，不是组员自动恢复/生产选择。未调用云端/花积分，未改游戏/M1/UE，未commit/push。所有本任务自动Blender进程已结束。导出器多图片采样警告保留，不称原始材质语义已修好。

## 下一步需要的决定

这版尚未达到整枪“差不多完成”。当前融合网格的钢木交界还无法可靠选取，不能继续重复失败轮廓。建议允许另命名的局部机械拓扑重建：机匣、照门、枪口硬件；原输入、木托/背带和游戏不动，先证明一处连续接口再扩展。报告未创建或批准该重建。保持现有拓扑保护的话，本轮只能交付法线改善；不能据此宣布整枪完成。亦可使用授权兼容的完成枪模。
