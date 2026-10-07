# GP002 — 局部金属精修不能覆盖木托接口失败

2026-10-03。用户认可GP001保留的原底模方向，授权继续本地精修。新方案读GP001/FP001后改用保UV精确裁切和独立光滑金属件；没有云调用，不是重新生成人物。当前整枪**未通过**，全部新草稿原位保留LocalWorking，不迁移为SFTP资产。

实施/结果：`Docs/Development/GERMAN_RIFLE_REFINEMENT_V2.md` / `_ZH.md`，`GERMAN_RIFLE_REFINEMENT_RESULT_20261003.md` / `_ZH.md`。私有证据：`Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/`；[逐文件大小/SHA清单](../../Assets/Integration/GERMAN_RIFLE_REFINEMENT_INVENTORY_20261003.json)不是Catalog或自动恢复权限。

## 实际进展

独立可见枪栓/柄、机匣、瞄具和枪口有稳定命名/连接。未全局焊接或减面；248,443原面保持原UV，零原角UV误差。最终265,976三角、46网格，重导入13项基础检查通过；新金属只读拓扑诊断闭合且法线朝外。原始底模、旧77文件/7源码、43原生/7动作草稿不变。19张最终图片实看。没有M1/UE/SFTP/Catalog/commit/push。

## 支持的失败原因

1. **外观一体网格的空间裁切不等于语义分件。** 即便每条新切边精确插值UV，盒子仍可能切入木托而不仅是金属。第一候选远侧残留和前箍切口，第二候选木托矩形开口可见；扩大盒子产生了新的接口问题。
2. **覆盖板不是接口设计。** 临时扩大承托板使顶面像导轨/积木，不能靠把开口盖黑证明符合馆藏形状。
3. **凸包跨接不相关轮廓。** 封口从同一平面收集全部位置，而不是先求连通闭合环；枪柄/木托等多条截面被当成一条外轮廓，产生大平面薄片。`final_v3/clay_receiver_top.png`、`pbr_receiver_quarter.png`及分离图明确支持这个源级原因，不是缺失贴图。
4. **程序校验范围窄于视觉要求。** 内部数据合法、三角相等、新金属闭合，均不检查新增补面的贴合/无薄片，也不批准历史外观或30k低模预算。
5. **可重跑不等于字节确定。** 两个最终GLB SHA不同；JSON/作者指标相同，18个UV/索引缓冲不同。自动UV/导出排序等是待查候选，不把未经隔离的根因写成已确认。

## 停止与下次必须改变

两轮结构草稿没有被选择。实施稿在动手前显式增加一次接口封口阶段，而不是暗中把第二轮称通过；这一次仍失败，现在停止，不延伸第四次覆盖/切盒/凸包试验。下一实现需要新有界文档：首先识别实际连通切边/材质边界，留出木托保护集合，证明一个小接口的侧/顶灰模和PBR，再决定扩大。考虑保留完整原主体的静态小修或成熟枪模/人工拓扑适配；这些是建议，不是已批准历史或自动发行。禁止直接导入本失败草稿到游戏。

## 工具/证据保留

首个setup `NoneType + set` TypeError发生在构建前，Blender返回0，不是成功；空目录及记录保留。structural_v1b旋转件绕序朝内，12/13而非13/13；修正后拓扑检查通过，但外观仍失败。初两轮源脚本冻结在各证据目录。最终初次/重跑GLB都保留，不能覆盖以制造哈希相同。原木托整体水密、动作、历史、UE/性能均未验收。

English summary: Exact UV-preserving clipping still damaged semantic stock interfaces. Whole-plane convex hulls incorrectly bridged unrelated sections, producing visible fins. New metal has useful local structure but the full rifle is not visually accepted. Numeric checks and executable reruns do not establish a finished or byte-reproducible asset. Preserve all drafts; no cloud, game or publication mutation.
