# 滚轮装备与左键投掷结果

2026-10-11：本地统一候选完成，待人工试玩。实施方案已先写；先读MI024、026、032、034、042，见证修订补读MI033、043。

## 实现

滚轮向下步枪／手雷／烟雾弹循环，向上反向；同一UE滚动的按键与轴事件只切换一次。三项装备栏高亮当前选择，帮助和情境提示同步。选中投掷物时展示既有道具／隐藏显示枪，左键按下进入原Start，按住停在原Hold；超过4.5秒仍不扣库存、不生成弹体／启动引信。松开后原Far投掷在原提交时刻扣一个、生成唯一弹体，结束回步枪。

松手前Esc／滚轮取消，原Cancel恢复且不扣库存；旧鼠标松开不误射，需重新按下。已松手不能撤销或切换本次投掷。空槽仍可选择，左键／R／右键不会透传枪械；G/Q直接投掷停用。菜单／保存弹窗／死亡优先接管输入。选择和按压是非序列化临时状态；重开／恢复回步枪。窗口失焦取消未松手准备的代码已实现，人工系统级失焦尚待复验。

## 实测和保护

最终Game `332756d091f64678de7b124e4e216571211bead31c42e6226edc686a14b15695`；源码manifest `ed5fa89398381deb823deae4d907abaeade31ee60ecdfcef082809fff3fe2e68`，75文件；普通目录 `tmp/Playtest-G1-EquipmentWheel-20261011`，100文件。构建回执／保护审计在 `tmp/g1-tactical-equipment-20261010/candidate_equipment_wheel_build_v4`。

| 实际UE检查 | 结果 |
| --- | --- |
| `wheel` | `pass_native_wheel`，exit0 |
| `throw` | `pass_native_throw`，exit0 |
| `smoke` | `pass_native_smoke`，exit0 |
| `p1` | `pass_p1_ammo_radar_inventory`，exit0 |
| `enemy_clear` | `pass_enemy_clear_checkpoint`，exit0 |
| `interactions` | `pass_native_interactions`，exit0 |
| `save_equipment` | `pass_native_save_equipment`，exit0 |
| `restore_equipment` | `pass_native_restore_equipment`，exit0 |
| `restore_legacy` | `pass_native_restore_legacy`，exit0 |
| `ui_equipment_pause` | `pass_ui_equipment_pause`，exit0 |
| `ui_pages` | `pass_ui_pages`，exit0 |
| `ui_pause` | `pass_ui_pause`，exit0 |
| `ui_confirm` | `pass_ui_confirm`，exit0 |
| `death_frag` | `pass_player_death_frag`，exit0 |

滚轮检查明确覆盖真实digital+axis双事件、正反循环、旧G/Q停用、选中不准备、长按4.5秒无扣数／弹体／射击、重复松开仍只提交一次、投后原步枪射击、按住切换／Esc取消、真实投出两枚后空库存、旧释放不射击、新按压才能射击和暂停菜单输入隔离。烟幕沿用双向感知遮蔽、最后所见记忆、穿烟原枪械射击、消散重新发现；P1检查原资源守恒、换弹／射击与小地图。保存检查从选中烟雾弹状态进入原全灭存档，真实双槽checksum／write／readback、失败负载拒绝；新进程还原装备效果和旧档，选择回步枪。UI检查含真实暂停计时／确认／全部帮助分类。死亡检查用正常控制器实际投出手雷、原伤害和第三人称倒地后重开。

1754 native、父source74／普通100文件／原用户档／Catalog和全部除exe外运行资产精确保持。枪械／保存／互动门槛／世界逻辑／新模型网格和贴图／死亡主体源码逐字保持；原CommitThrow、PlayThrow、ThrowTick、BallTick、Blast保持，BeginThrow仅增加销毁临时选中展示，其初始化、原动画和原hand_r／掌指间挂接不变。源码变动限六个装备／UI／诊断文件，加一个可选滚轮探针；全量清单和文件哈希见本地DELIVERY和protection。

## 失败与限制

v1构建成功，轮换／长按／唯一提交通过；随后过早缓存原射击计数而误报失败。实际原步枪已射击一次，loaded7／reserve10／shots1。异步截图同帧继续按左键还造成“选中”图为准备状态。v2纠正夹具取值／截图时机后，射击／取消通过；随后从按下时刻提前要求已有烟幕，忽略原动作和提交后3.5秒引信。v3等待真实烟幕事件，输入通过，但实际HUD在切回步枪后仍残留烟雾弹空库存提示；v4切换时清除旧Notice、空槽不显示外壳，并检验实际像素。MI043／MI044保留各轮原身份；枪械／资源／保存门槛始终不变。最终所有检查来自同一v4Game。

本轮不修改原人物／手指／枪械模型，也不调整原Hold的低屏幕位置。真实UE图片已逐张查看装备栏和装备帮助；并不构成全动作握持／连续接触或人工输入认可。检查在当前人数／注明夹具中进行，无新增NPC压测、独立性能或第二电脑新验收。普通入口留tmp独立目录；正式基线、Git／SFTP发布与旧版本清理未执行，现有UE Editors仍开着。
