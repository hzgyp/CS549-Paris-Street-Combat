# AN003 — 修正绑定与枪握点，仍未通过游戏袖子门槛

后续人审（10月4日）：用户实际查看后确认换弹右食指穿模、衣袖碎片遮挡、结束接
持枪跳帧；记录为RLD-01/02/03。“缺动作”尚未证明。原有AN003夹具仍失败／未选中，
作者和冻结测试入口继续停止。用户另授权新V5原因优先动作修复及NPC并行交接，见
`Docs/Development/PARALLEL_GAMEPLAY_WORKFLOW_20261004.md`／`_ZH.md`。
这是新工作范围，不把人审失败改写成AN003成功，也不解锁旧建图／取样路线。

2026-10-04，状态：停止这一有界证明，未正式采用。
用户认可原始mannequin带M1预览，这份人审成立；不应因目标士兵失败而撤销它。
结果：`Docs/Development/RELOAD_APPROVED_GAME_INTEGRATION_RESULT_20261004.md`／`_ZH.md`。
MANIFEST关联34项原位私有native／source／result／图／log／exit，不表示搬到离线
归档或自动恢复权威；没有复制／删除商业资产。

## 新机制及已证实内容

已读AN001/AN002/FP001。没有重做FK/pelvis retarget、复杂recoil chooser、live
蒙皮批量查询或遮袖／改相机／offset扫描。先实测两个scope：正式地图绑旧Reload_2
正确；无保存ActionOwnerV1换弹时display被UE重路由到Body，Ready/reset不返回PoseMesh。
新枪为V3子类固定reload hand_r T；最小Owner修改使PoseMesh独立播放既有目标AS，
display始终跟它。两新夹具936,584字节，没有player／animation／map作者。

target visual_v2的五个冻结相位，display→PoseMesh、PoseMesh无leader均成立，
最大握点代理误差0.000190959cm，reset回归正确；7张游戏视口图实际查看。
然而开始／操作／返回／结束袖子仍有显著尖刺／薄片，操作／返回大面积遮挡。
**局部绑定／数值改善不等于源动作对当前第一人称士兵显示兼容。**
具体袖子原因仍未证明，不能由“未跟Body”反推权重坏，也不能排除近镜头投影／
aux骨映射；原Animation Editor外部正常仍不代替这一视图门槛。

## 技术失败与保护

首author Quat传给Rotator构造器在native保存前失败，exit0但不是作者成功；一次
结构属性赋值纠正后两夹具生成。首visual仅holding，default-only timing实例
不可写而正常失败；下一identity测试spawn前设置隔离未保存CDO、只读枪校准，
取得实际目标阶段图。四个任务的失败／成功记录均保留，没有native崩溃。
两个基础binding进程也保留。所有matched-error复核范围明确，不宣称warning为0。

514文件大小／SHA均一致，正式map仍2791b4a7...ad68519，源角色／手指／动作／
相机／原事务／Catalog与发布未动。冻结run显式reset取消，不是自然换弹完成，
没有新方案完整功能／近墙／动态回归；停止条件在此之前触发。

## 后续边界

停止锁在`run_reload_approved_v4.ps1`，不要新identity重复这套证明或选中夹具。
保留用户成功的原始preview参数。若继续，先不同的安全离线／最小原因定位，
证明实际owner皮肤／骨骼映射或投影原因，再取得改变保护边界的明确授权；
不猜测性改权重／手指／镜头，不新造动作／详细人物，不复活AN001／AN002路径。

## English review

Source preview remains user-accepted. Runtime proved an action-owner follower
rerouting defect; an independent native pose driver and calibrated fixed reload
attachment improve binding and proxy contact, but seven inspected target views
still fail sleeve/obstruction acceptance. Cause remains unproved. Stop this proof,
preserve34private entries and514hashes; no formal adoption/publication or further
same-mechanism runs. A separately authorized cause-first owner-view repair is next,
not another retarget/offset/mask or new motion.
