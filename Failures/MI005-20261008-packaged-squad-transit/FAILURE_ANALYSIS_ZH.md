# MI005 - 玩家成功不代表小队通行

2026年10月8日。[英文原稿](FAILURE_ANALYSIS.md)。cohort_v1／instrument_v6沿用
MI004单块禁行试验，保留城市／胶囊／动作／AI／原玩家输入及对岸目标，先等待两
盟军，使用原55cm／25秒门槛。本次失败failed_original_cohort_25sec_bound，
观察墙钟79.755秒，正常退出0。

最终玩家(5837.618,-20290.487,206.383)，100HP、17发、1+0弹。两盟军均100HP、
2+16弹、0发；三德军由玩家原射击消灭。盟军1位于(5708.730,-20918.983,277.048)，
速度0、距HeldGoal110.488cm；盟军2在(2105.849,-20810.376,212.582)，速度0、
距HeldGoal3408.397cm；二者SquadFailed=false。该标志或有目标／查询不能代替
实际到达。navrepair_v1三次玩家胜利／存读／重开只保留原窄结论，不通过小队、
自然双向战斗或完整MVP。

停止本小队证明与单块修正路线，不追加禁行多边形、不扩大时间／容差、不猜测后
改队形、胶囊、速度、伤害或AI。正式源码／地图／Catalog未改。本版本没有NPC路径
状态或实际胶囊命中记录，尚不能推断是几何还是AI原因。

不同的原因观察squad_diagnose_v1／instrument_v7仍用相同六人世界／输入与已有
单块试验排除，但记录NPC原路径状态／下目标、请求结束原因、实际胶囊／台阶／
导航属性及60cm前向扫掠，含法线／可踏步属性／网格及导航碰撞信息。首个Ready、
HeldGoal误差>100cm的NPC静止4秒即停，或原180秒／任务失败／Error界限；不再次
证明完整小队、不新增排除或改玩法。早期要求观察器确实启动、保护输入精确。
原收据／二进制／源码／CSV在自有进程关闭后归私有MVPCloseoutV1/failures的
cohort_v1及instrument_v6。这是补缺失原因，不是重复停止的通过试验。

CSV限定：失败结束时EndCapture后立即退出，原CSV缺少UE最终重复表头／元数据
尾部，只是不完整前缀，不能算完整性能采样。保留初次摘要，后续csv_validation.json
明确使其FPS读数无效；后续摘要工具检查尾部。diagnose_v1及navrepair_v1三份CSV
尾部完整，原较窄范围数据仍成立。

后续squad_diagnose_v1／instrument_v7正常退出0，183.009秒：第一轮两盟军通过
原门槛，第二轮25秒失败。盟军1误差34.618cm，盟军2误差3551.617cm，路径Idle、
Ready、SquadFailed=false；最后请求54返回Aborted3／flags328。安装的UE
AIController::StopMovement传入MovementStop与ForcedScript，另有UserAbort，
表示脚本停止，不是原生Blocked；仍未记录哪个策略调用停止。4秒检测只覆盖
playing，regroup实际到25秒才停，保留观察覆盖缺口，不把第一轮冒充重复通过。
移动样本也以300cm/s扫到可踏步残骸，不能据此认定NPC物理阻挡。物理／导航凸体
缓冲均61顶点也不证明完整表面相同。

早期通过的PIE在55cm内未取消玩家SimpleMove，而打包测试提前取消。新的输入
修正及黑板／请求只读诊断见Docs/Development/MVP_G1_SQUAD_FIXTURE_DIAGNOSTIC_20261008.md，
保持原到达界限和全部玩法，不声称已确定NPC失败原因；未记录原因前不改AI。
