# GP005 — 柄根实际边路径未形成简单闭环

2026-10-03。V6先验证球头，后验证不同的柄根接口。不是GP004坐标包络、不是空间裁切。本轮球头局部改善与柄根失败并存；整枪生产缺口仍未关闭。

柄根16个环向射线点在原网格上选面/顶点，最短边路径并集度数分布为675个点度数2、两个度数1、两个度数3，违反简单封闭环。断言在连通选面/修形前阻止继续，没有修改枪柄根或木托，没有材质适配。Blender返回0不能覆盖AssertionError。实际原因只确认路径并集不满足环结构；不能仅凭此断言宣称源网格不水密，或断言一定是UV/射线击中木托。保留原位空失败目录和源机制，诊断文字记录于V6结果。

早期球头选区1918面/44边环另已通过四可见方向，球头单次修形最大1.14mm、全部原面/UV与木托位置保留，前后图和新GLB核对，干净重跑GLB字节一致。这些通过不批准失败柄根，也不是完整可动枪栓。

停止柄根机制：不移动截面/扫射线参数、不扩大选择、不把球头材质强行延伸到木托，不复用GP004标签/GP002封口。下一次若修柄根，需要显式人工面环/不同的已证明表面机制或成熟资产；新计划先小接口证明。

文档 `Docs/Development/GERMAN_RIFLE_SURFACE_JOINT_V6.md` / `_ZH.md`，结果 `GERMAN_RIFLE_JOINT_RESULT_20261003.md` / `_ZH.md`；源码 `Tools/AssetCreation/GermanRifleSurfaceJointV6/`；私有原位 `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6/`。元数据 `Assets/Integration/GERMAN_RIFLE_JOINT_INVENTORY_20261003.json`，无移动/删除、Catalog或恢复选择。此前五轮228私有/29源码、M1四文件、游戏50文件SHA不变。没有云消费/UE/M1/发布/提交推送。
