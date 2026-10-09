# G1小队请求诊断与测试输入修正

2026年10月8日19:10EDT。[英文原稿](MVP_G1_SQUAD_FIXTURE_DIAGNOSTIC_20261008.md)。
已读Failures/README、MI004、MI005、ML010、MI001，以及本次收尾和导航试验计划。
原正式运行代码、资产和703保护项不动；本次仍是私有隔离包装，不是正式采用。

instrument_v7／squad_diagnose_v1第一轮通过原小队门槛，第二轮失败。盟军2距离
HeldGoal3551.617cm，路径Idle；最后请求54返回Aborted／328。安装的UE5.8
AIController.cpp及PathFollowingComponent.h表明328是UserAbort、MovementStop、
ForcedScript组合，不是原生Blocked；仍不能确定哪个策略调用了停止。4秒静止
观察只覆盖playing，未覆盖regroup，因此实际在原25秒门槛停止，保留此观察缺口。
移动中的NPC也扫到同一残骸且法线可踏步，单次前向命中不能证明NPC被阻挡或导航
碰撞不一致。

新cohort_nativefinish_v1／instrument_v8只修正一个测试输入差异：玩家首次进入
原55cm对岸窗口时，不再主动取消SimpleMoveTo，保留原请求自然完成。之前通过的
PIE测试也没有取消它。目标、55cm／25秒、六人输入、原AI与已有单多边形试验排除
均不变。尚不能说提前取消就是NPC失败原因。

每秒以及原NPC请求结束时只读记录控制器／黑板：策略与小队模式、目标、预约ID、
PatrolEnabled、HasMoveGoal、DesiredPosition、WaitingReason、RetryCount及
HasVisibleTarget，观察器不写这些值。最多三个新世界轮次，首个原界限失败、任务
失败／Error、观察器缺失、保护项变化或路径无效即停并留证。不追加多边形、不改
容差／时间／队形、不强行重启NPC路径、不存资产、不按猜测补偿。失败后根据实际
状态另写有界原因修正方案。观察开销不是自然人工或FPS通过证据。

早期验收：758源码、359原生文件、703项精确；无占用引擎；新构建／运行身份；
实际观察器、1920x1080、Ready及原阻挡多边形证据均通过后再开始。必须观察原请求
自然完成与两盟军实际达到原门槛，不能从标志推断到达。
