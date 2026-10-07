# 当前 V16 持枪的原贴图三视图 / V16 textured three-view inspection

2026-10-05。用户只要求加载贴图、查看三视图。本轮是离线展示，不修姿态、不采用进游戏。

已读：Failures/README.md、GP004、GP009，V16 中英文结果；Blender character workflow 及其 form-review / astra-workflow 参考。GP004 要求沿用真实 UV/材质槽，不能按坐标猜木/金属；GP009 要求新鲜重载验证最终文件，不能只看原场景。

改动机制：冻结 V16 保存网格的位置、拓扑和握姿；从原 FBX 恢复逐角 UV 与实际材质槽，从已验证的原 M1 / US Paratrooper portable 材质恢复原贴图。只在新展示文件内构建 PBR、照明及互相正交的相机。DirectX 法线的绿色通道只在 shader 中转换，不改 PNG。没有生成/绘制新贴图、动作或几何。

早期检查：源三角顶点索引与 V16 完全对应；UV corner 与翻转的渲染 winding 一一对应；材质映射无缺项，实际图片存在且像素有效；顶点位置差 <0.0001cm。任一项不满足则停止，不猜图、不重展 UV、不改握姿。最终 fresh-open 核对几何/UV/材质图及输入哈希，检查三张原图。

交付：右手握持近景的正视、侧视、俯视（记录相机方向、同尺度），另留完整手臂上下文。所有图片/blend仅在单一私有 SFTP 工作区的新 Evidence/WeaponTexturedViewsV17 中；源码/本记录可入 Git，不提交商业图。原 V16 拇指/护圈交叉和肩部问题不会因贴图变为通过。不用 UE，不动正式地图、NPC、BT/BB、Catalog、release，不 commit/push。

English: presentation only. Preserve the frozen V16 vertex positions and topology; recover exact source FBX corner UVs/material-slot assignment and existing verified portable source materials. No coordinate-based semantic repaint, UV unwrap, grip/finger/weight/action edit, or native selection. Stop on mismatched topology, missing source maps or a positional delta above 0.0001cm. Inspect all three orthographic source renders and fresh-open the independent presentation blend; preserve source bytes and current 528 recovery guards. Portable PBR is not exact UE shader parity or motion/contact acceptance.

## 结果 / Result

首轮 presentation_v1 的真实贴图/UV/位置检查通过，四张原图已查看；完整手臂在 +X 近景挡住握持，属于展示可读性问题，不改为游戏模型修复。

展示纠正：presentation_v2 只复用 V16 **已经存在**的 Fixed right / Support 近景对象（不新增切割或模型遮罩），将它们恢复同一源逐角 UV。近景显示这两个对象，完整手臂仍保留在同一 blend 并另渲染总览。+X、-Y、+Z 相机/尺度和枪位不变。v1 及其脚本/证据不覆盖。图片可读性改善不是肩部缺陷被修复。

完成：三张1400×1200正交近景及同尺寸完整手臂总览已逐图查看；3000×960中文三视图拼图只缩放/排列原渲染，未修图涂掉穿模。9张现有2048² D/N/ORM 图片，原M1、US jacket、US skin三个 portable shader；手臂原四层UV、枪原两层UV和逐面材质归属恢复。冻结V16顶点位置最大变化 **0cm**，无动作/手指/枪位改动。

独立 fresh_v2 exit0/errors[]：四个展示网格位置/三角/逐角UV/材质槽哈希全部一致，9张图实际存在、像素尺寸/颜色空间/文件SHA一致，528当前恢复记录完全匹配（包含既有未选V6 rate差）。正式地图未改。所有 Blender 作业正常结束。

私有证据：`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponTexturedViewsV17/`，包括只读源探测、v1遮挡原图、v2三视图/blend/完整手臂以及fresh_v2验证。图片路径已经git-ignore；只引用现有贴图文件，不复制原资源包或发布资产。

局限：近景复用原有手部对象，因此手腕边缘是诊断截面，不是新断腕/游戏修改；完整手臂原肩部拉伸仍在总览可见。portable原图材质不包含全部UE衣料染色/复杂shader效果，不承诺与游戏完全同色。V16拇指/护圈接触失败仍未关闭，此次贴图展示不能当作握姿/换弹/原生验收。未选中进游戏、改NPC、发release、花积分或commit/push。

English result: v2 restores the original six UV layers across the gun/arms and uses three existing portable donor graphs with nine existing texture files. V16 vertex positions change by exactly zero. Three orthographic closeups and the complete-arm context were inspected; v1's obstructed full-arm closeup is retained. Fresh-open verifies positions/topology/corner UVs/material indices, all nine image paths/size/color spaces/hashes and 528 current recovery records. Closeups use pre-existing V16 diagnostic hand objects, not a new runtime mask or cut; full source shoulder artifacts remain visible in context. Portable shading is not complete native UE parity and does not close V16's contact failures. No native integration/selection/publication/commit/push.
