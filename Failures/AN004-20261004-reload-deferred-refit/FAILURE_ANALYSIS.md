# AN004 — 混合完成后才硬切framing，实际城市仍跳

2026-10-04。本窗口修复RLD-03的第一版集成停止／未选中。原始源码、生成包与
证据原位保留，不搬共用依赖，不恢复旧地图或发布。无commit／push。

先读AN001/002/003/FP001，新机制用两个现成动作evaluator与UE标准two-way blend，
UE自身0.25秒变换权重，枪hand-relative变换使用同权重。最小fresh证明61采样、
0.257617秒，两端与实际直接播放动作<3e-14cm／四元数0，516保护一致。

实际城市owner_blend_city_v1却失败：Ready约4.142555秒，2/16->8/10单次保守提交；
淡出期间观察到连续权重／位移，但约4.39秒、权重归零时枪13.3543cm／腕13.2729cm
跳变，超过预定3cm门槛。519原生保护不变、正常退出0；功能／退出0不是视觉通过。
原因证据是源代码的Ready&&Holding硬门控加采样framing切换：只延迟原持枪重新fit，
并未消除这一步的硬切。不要重跑这版或加延迟／偏移样本。

保留的技术失败：菜单单引号／同名资产发现失败；反射函数FInterpTo_Constant与
C++名差异；PIE直接参考实例初始化丢失。各自纠正与成功最小证明分开记录。
无native崩溃；没有重新权重／手指／镜头／源动作或弹药事务修改。

下一机制必须同时混合camera-local显示变换：Ready后原算法只生成当帧持枪目标，
用同一ReloadWeight从换弹前的cached frame连续混到目标，枪和手统一套同一结果。
独立新owner身份；不覆盖失败owner。3cm早期门槛不放宽；后续要检查实图和全部
中断／移动／近墙事务，不能把数值通过升级为三项缺陷全部解决。

## 连续framing新机制的实际结果（同日）

owner_reframe_author_v2生成独立BP_PCReloadOwnerReframeV5，不覆盖旧owner。首次
author_v1在算术wildcard设常数处安全停下，唯一schema纠正先接类型化输入。
新实际城市owner_reframe_city_v1有520保护一致／正常退出0、4.157014秒Ready、
单次2/16->8/10守恒；最终归0原13cm切换没有同量级跳变，但首次Ready淡出阶段
仍在43.620ms内移动枪5.08655cm／腕4.48709cm，超过不放宽的3cm早期门槛。
这是有界连续性检查失败，不是视觉通过；没有完整人审／移动／生命周期回归。

**新owner也停止／未选中。** 不重跑这两版实际城市集成，不以减慢混合、增加延迟、
偏移采样或放宽3cm门槛修结果。后续需要把Ready时新持枪目标的产生时序、原生
显示算法与阶段证据分开诊断，先形成不同有界机制，不把当前改善当成功基线。
两个失败owner及4个共享最小诊断资产均原位保留；独立衣袖权重实验不是本集成续跑。

证据：workspace Evidence/ReloadRepairV5/{blend_capability_v1,v2,
transition_proof_author_v1,v2,transition_proof_fresh_v1,v2,
owner_blend_author_v1,owner_blend_city_v1}。商业native只在单一Content；
MANIFEST.json记录共用与本案例专属身份，非Catalog或自动恢复权限。
