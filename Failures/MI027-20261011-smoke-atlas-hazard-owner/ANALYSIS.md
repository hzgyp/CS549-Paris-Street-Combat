# MI027：烟图集与有限避险动作所有权

读取 MI024–MI026 后复查 v11：烟幕感知/记忆/穿烟射击通过，但实际截图没有浓烟，不构成外观通过。环境材质使用 SubUV 图集与动态参数；新 transient 发射器只保留材质而丢失这些输入。引擎源码表明原始 Distribution 在没有 lookup table 时可直接求值，不能把空表未经验证认定为根因。下一方案复用现有 Required/SubUV/dynamic 模块的运行数据，保留原件，记录实际粒子数、大小、透明度和图集，重新审查画面。

`hazard_v11` 发出 MoveTo 但未通过实际位移门槛。旧策略/小队包装以 CombatHold 与 RestoreGeneration 匹配来保护动作；仅暂停 Brain 并不能凭 MoveTo 事件证明角色移动。下一有限适配记录并临时保留原 Hold/Generation，在避险期间匹配原动作所有权、结束还原，再测实际位移、存活和 Brain 恢复。保持旧行为树、地图、碰撞、武器算法。

v12 编译失败：TObjectPtr 数组不能用 auto* 元素推导；SmokeReceipt 位于 JsonText 声明之前。保留 compiled-source-game/build，不运行失败的 Game。下一身份修复显式元素读取和声明顺序；不覆盖 v12 收据。

早期门槛为真实浓烟截图、粒子数据、原生导航实际位移；若仍不成立、原模型/手指/枪械/存档漂移或发生断言，停止该候选并保留证据，不以事件计数替代通过。


v13 smoke 原生运行在 Required::Serialize 的 cooked-data 检查退出3：DuplicateObject 会经过加载序列化，却不是 cooking archive，不能复制这种已 cook 模块。引擎 ParticleModules.cpp 1104–1123 明确对应这个失败，不是GPU启动异常。后续新建 Required，仅复制必要图集数/插值/材质值；只读引用现有已cook的 SubUV/dynamic 模块，不串行化副本或修改原件。v13运行/源码保留，重新检查实际画面与粒子数据。


v13 hazard 实测位移仍为0，原生 MoveTo 返回2(RequestSuccessful)，不能据此认定移动通过或证明单一所有权推断。后续对有限避险路径增加正式胶囊实际 sweep，拒绝有碰撞的Nav候选；独立诊断把现有盟军放到已测胶囊/完整路径的视线车道，并记录实际速度、模式/路径状态，不改普通出生点或造新NPC。失败原件和假设限制保留。


v14 的实际速度0、路径状态Idle、位移0.796cm继续失败。读取 G1MissionV1/ue_bridge_hook.py 与原 UpdateBridgeSquad：hook 安装于 Controller ReceiveTick，独立于 Brain；原 CombatHold 分支调用 PC_PolicyHold/StopMovement，确会覆盖装备 MoveTo。v15 仅在有效、存活、AllowsPlay 的短暂装备导航所有权期间让桥接hook返回已处理；其余逐字进入原小队算法。结束恢复原状态，不修改BT/native包，不以暂停Brain代替Tick所有权。v14 135粒子、6x6图集、alpha0.595仍无充分可见浓烟；材质只读审计后再定参数，不把粒子存在当作显示通过。


只读 Editor commandlet MATERIALS.json 测得 MI_Smoke 的材质 Opacity=0.1、Fade_Distance=0；此前只调粒子透明度遗漏了材质自身倍率。下一 transient MID 使用已cook父材质，明确Opacity=1/Fade_Distance=20，复用已有实例的软接触尺度，仍用同一烟浓度驱动粒子alpha与体积；原材质字节不变，实际截图才作显示门槛。材料审计进程正常自行退出，主Editor保持开着。补正上文位置描述：ue_bridge_hook.py 在 PC_UpdateSquad override 插入桥接hook，并非脚本直接安装ReceiveTick；确定的冲突是原hook中的PC_PolicyHold/StopMovement，具体调用调度不冒称已逐帧追踪。


v15_early 已有可见烟，逻辑双向过滤/穿烟射击通过，且实际避险位移和Brain恢复通过；但画面仍能辨认中央敌人的姿态，记为烟浓度不足，不能给满浓度视觉通过。基于这张135粒子/180cm/alpha0.595/材质Opacity1的实际画面，做一次有界材质倍率3的浓度校正，粒子数、尺寸、逻辑半径、Shader/原资产不变；再看同一受控车道图，若仍可清楚辨认目标则停止本参数方案。机制回归有确切v15_early身份；v16仅此一行数值变化，新的烟幕/存取/性能必须实跑，其他逐字未变机制可明确承接，不改称v16实跑。
