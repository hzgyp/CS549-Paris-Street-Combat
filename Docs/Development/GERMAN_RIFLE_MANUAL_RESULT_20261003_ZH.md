# Kar98k V9：前端接回整枪，机匣新面未通过

2026-10-03。按用户要求继续手工指定形体，以盟军枪普通游戏道具完成度为目标，不做微小刻字/复杂内部机械。使用 `blender-modeling-workflow`：先实施文档、灰模真实接合、自有标准钢材、干净重跑和导出后复核。**有实质前端进展，但整枪没修完，没达到盟军M1整枪完成度。** 无云端扣费、UE/游戏/M1修改、SFTP/Catalog或commit/push。

## 实际改好了什么

新枪管、枪口和准星已接到完整枪上，不再只是一堆独立零件。保留原木托、背带、球头、截线后位置/UV，最终恢复原自定义法线。固定X=.480真实截面为74边外壁+42边内孔，分别接面，前端形成真正中空枪口；去掉多个软塌凸起，只留一个有底座的准星。无跨环凸包、堵孔盖板、重复旧前端或重画木头。实际灰模侧/顶/反向/斜视未见接缝裂口。

![实际整枪](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-manual-v9/front_audit_v1/fresh_whole_right.png)

![接好的枪口](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-manual-v9/front_audit_v1/fresh_muzzle.png)

296,719三角面/5网格仍继承大量原底模面数，**不是已优化游戏资产**。主体257,769面、背带37,690面、新枪管1,044面、准星座/刀片各108面。原2048²D/ORM打包不变；新钢材为自己的标准常量材质，不借用盟军贴图。**新黑钢与旧浅色钢面明显不同，机匣/照门/保险/前箍仍软塌，整枪观感尚未合格。** 未做完整可动枪栓/配套拉栓换弹、历史型号或UE测试。刻字可忽略，明显色差与结构不能冒充忽略的小细节。

## 机匣为什么没装新件

[GP008](../../Failures/GP008-20261003-kar98k-manual-skin/FAILURE_ANALYSIS.md)：同一1,884钢面/156边接缝，展直10个折边点、同步14个同坐标副本，最大0.995565mm，投影无交叉。但新面细分后1条四面边、6个极小面；唯一构造纠正让初始三角化通过，最终细分仍失败。全部在删原钢面前退出1，**没把坏面塞进枪里**。首次Blender5.2返回整数的API错误和失败源快照也保留；细分器内部具体原因未证实。停止这条边细分路线，不扫选区/容差/盖片；`assemble.py`是停止试验，不是合格生成入口。下一步应换简单明确的面连接/材质整合方法或成品，不是刻字/内部机械，也不自动调Aholo。

## 验证与文件

最终前端、干净重跑和独立导入均退出0；GLB18,266,924字节，SHA `1232612899a1ede8de05db3e8d6ebb3694b15fd5f3d4fa07a335399ce97d771a`，字节复现一致。自包含blend19,433,327字节。重新导入验证5对象/三角拓扑绕向/位置UV/轴心/原贴图哈希；最大角点误差2.98023224e-8、轴心0。法线/材质另看真实灰模PBR，不冒充独立法线数值检查。保留API弃用/同图多节点采样警告，不隐藏原材质问题。

32图实际看28张：首次4接合、最终8灰模、8材质、8导入；首次另4张未独立复核。旧414私有文件/59源码、50原生动作、4M1参考SHA不变。Git检查只验证17,479选中清单元数据，没有SFTP上传下载。产物仍在LocalWorking，新库存不是生产baseline/组员恢复许可。自动Blender进程已结束，没开预览或游戏。

[源码](D:/0.Rutgers/CS549/Project-New/Tools/AssetCreation/GermanRifleManualV9/barrel.py) · [Blender整枪](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-manual-v9/front_finish_v1/Kar98k_ManualFront_V9.blend) · [GLB](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-manual-v9/front_finish_v1/Kar98k_ManualFront_V9.glb) · [指标](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-manual-v9/front_finish_v1/metrics.json) · [导入验证](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-manual-v9/front_audit_v1/audit.json)
