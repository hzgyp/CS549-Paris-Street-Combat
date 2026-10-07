# SP-R 成品底子适配 V10 结果

2026-10-04。使用 Blender 建模技能完成本机模型与导出复核，**当前为整枪人工复核候选，不是已选生产资产**。按中英文实施方案进行；先读 GP002/004/008，新导出失败记为 GP009。

## 改成了什么

保留 SP-R 已实际核对的机匣下部连通组件、枪栓/柄、扳机、枪管/枪口。整个塑料枪托/前罩、瞄准镜、导轨上部组件、托腮板、外挂弹匣/释放件均不进入候选；没有切旧 Aholo 枪。提取后原 UV 误差为0；枪管锥度、扳机位置为候选适配，不改原包。

新增连续枪托/握颈/长前护木和真实机匣/枪管沟槽、独立上护木、贴合箍带、枪托底板、开放护圈/底板、带过渡和倒角的机械瞄具。约 **1.1073米、24网格、24,466三角面**，根点按整枪包围盒居中。烘焙棕木/法线/粗糙度与源钢材派生贴图统一前中后完成度，没有复制盟军几何或贴图。

第一轮整枪灰模看六个角度后，缩小过大的护圈、改善方块瞄具底座。首轮材质偏浅橙、木纹过于规则；一次整幅木纹/颜色/粗糙度纠正改为较暗低对比木色，钢材反光也收敛。最终实看钢木界线清楚、枪托连续、主要部件有承托，没有旧软化机匣和现代外挂。目标是普通世界枪械道具，不是照片级磨损或完整第一人称套件；是否满意仍由用户判断。

## 成果文件与实际验证

- [Blender 模型](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-v10/finish_v3/GermanRifle_SPR_V10.blend)：13,077,144字节。
- [GLB 模型](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-v10/finish_v3/GermanRifle_SPR_V10.glb)：11,621,376字节，SHA256 `795967ab635064139c69a4e46ffacfce222b992e275a7ffec5043cb974642323`。
- [可重跑源码](D:/0.Rutgers/CS549/Project-New/Tools/AssetCreation/GermanRifleSPR_v10/main.py)，同目录有检查、参考和阶段记录。`Assets/Integration/GERMAN_RIFLE_SPR_DRAFT_INVENTORY_20261004.json` 是私有草稿元数据，不是 SFTP/Catalog/组员恢复授权。

新建实体按位置识别接缝后，无小于1e-12m²的三角、开放边或多面共边；不是全局布尔/自交证明，也没有声称原成品每个部件都水密。`finish_v3`/`audit_v2` 退出0，新鲜 GLB 保留24名称和三角数；位置最大误差0米、UV5.96e-8、法线0.0411594度。整体包围盒1.107304×0.079198×0.183007米。12张图片均内嵌、有像素，无外部图片依赖、无 Action。最终作者12张灰模/PBR和新鲜导入12张图逐张查看，包含反面、顶、底、机匣近景；初始8张零件/6张灰模也实际检查。早期材质只检查部分角度，没有假称所有历史PNG均已实看。

第一次 `finish_v2`/`audit_v1` 因默认导出没应用倒角，底板188对12三角，退出1，保留未选；显式 `export_apply=True` 后通过。精简依赖库另开后保存为正常独立 blend，最终重开不再有库文件 UI 警告。干净 `repeat_v1` 重跑及 `repeat_audit_v1` 通过作者/导入和两次导出的几何/UV/法线检查，**内嵌PNG字节相同**；GLB整体哈希不同（重复导出a8cbdba7...ae5c36），排序/编码原因未证明，不能宣称整文件逐字节可复现。

原2.2GiB库制作前后SHA均匹配 `9e5e1a18b1608f2359e9087834cf553621759e22d67ca343ec5182159f4b3a11`，没保存或复制原库。没有 UE/M1/V1–V9 写入程序，没有重新整批审计这些旧文件哈希；没有云端调用/扣费、SFTP/Catalog/发布、commit/push。自动 Blender 任务均结束，二进制/商业图片仅 ignored LocalWorking。

## 看这一版

下面是 **实际 GLB 重导入**，不是只渲染作者场景：

![整枪](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-v10/audit_v2/fresh_pbr_quarter.png)

![机匣与木托](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-v10/audit_v2/fresh_pbr_receiver.png)

仍需：人工整枪观感复核；现代底子的机匣/保险/抽壳器差异及具体历史变体/配枪审核；MW2项目使用/衍生共享许可确认；完整可动枪机/骨架/动作、握持换弹、碰撞/LOD/UE实际验收。分开的枪栓管/外柄是外观件，不是已验证完整可动机构。尚未替换游戏，也未关闭生产资产缺口。后续只修有意义的整体缺陷，不再重启 Aholo 失败机制或堆微细节。
