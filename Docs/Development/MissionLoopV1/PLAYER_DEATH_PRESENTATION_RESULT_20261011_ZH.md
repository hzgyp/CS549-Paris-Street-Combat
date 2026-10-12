# 玩家死亡表现与试玩目录结果

2026-10-11。统一本地候选已完成，等待用户试玩。最终同一个Game的5项死亡测试与19项既有UI／装备／存档回归全部通过，24次均exit0；正式已选enemy-clear52与已发布课程包保持。

## 交互结果

所有新发生的玩家死亡立即执行原伤害、PC_Die和Lost保护，再由临时第三人称镜头显示原整身人物，播放原Rifle_Death_3至3.933333秒末态；结束后短停0.25秒，再出现YOU DIED和原重开／读档／退出按钮。地雷实测整段4.184637秒。倒地期间HUD和菜单暂不出现，射击、装备、读档、重开输入受限；重开后旧世界镜头清理，玩家100血恢复。旧NPC尸体读档仍直接停末态，不重播。

地雷与手雷爆炸都有可见短火光、尘烟与灯光；复用现有兼容火焰材质和11×11序列，瞬态曲线明确不烘焙，并更新动态模块用途标志。实际日志为24个火焰粒子、透明度0.891810及18个尘烟粒子，原始早期截图中火光清楚可见。火焰粒子0.65秒、尘烟1.6秒，不增加碰撞、视线遮挡规则或持续烧伤；原爆炸录音、半径／遮挡／伤害保持。v6同时补齐多个渲染前提，不能冒称某一参数已单独证明为唯一根因。

本轮三个根试玩cmd已依冻结SHA迁到私有tmp记录，新试玩包及入口一律放tmp/Playtest-*/。父普通包字节保持，正式既有根入口保留。

## 精确身份

Source: `Unreal/Variants/G1PlayerDeath20261011/Project` (73 files); manifest SHA256 `1023d2a2a5bd6d239e4fc17481dc3b670910f709d4a191c6048df1c8c2a6f26a`. Game SHA256 `290b51b5648c73261e119edbef8d0f7fbb2e9088de4126262afc8cb92988ea21`. Authoring: `tmp/g1-tactical-equipment-20261010/candidate_death_v6/Project`. Normal trial: `tmp/Playtest-G1-DeathPresentation-20261011/PLAY_COMBAT_UI.cmd`. Independent UserDir `G1DeathPresentation20261011` / prefix `ParisDeathPresentationV1`; no old-save migration.

普通启动无探针、自动输入、观察器或AI／资源覆盖，不迁移覆盖旧存档。现有两个Editors50836／51148继续开启；本次Game验证不冒称新Editor／PIE／cook验收。

## 实测与范围

| 测试 | 最终状态 |
| --- | --- |
| death_mine | pass_player_death_mine |
| death_frag | pass_player_death_frag |
| death_damage | pass_player_death_damage |
| death_crouch | pass_player_death_crouch |
| death_prone | pass_player_death_prone |
| ui_pause | pass_ui_pause |
| ui_equipment_pause | pass_ui_equipment_pause |
| ui_pages | pass_ui_pages |
| ui_confirm | pass_ui_confirm |
| ui_pages_small | pass_ui_pages_small |
| menu | pass_menu_input |
| enemy_clear | pass_enemy_clear_checkpoint |
| p1 | pass_p1_ammo_radar_inventory |
| throw | pass_native_throw |
| smoke | pass_native_smoke |
| interactions | pass_native_interactions |
| mine_range | pass_native_mine_range |
| mine_post_clear | pass_native_mine_post_clear |
| mine_post_clear_frag | pass_native_mine_post_clear_frag |
| save_equipment | pass_native_save_equipment |
| restore_equipment | pass_native_restore_equipment |
| restore_legacy | pass_native_restore_legacy |
| restore_v16_equipment | pass_native_restore_equipment |
| performance | pass_native_performance |

死亡5次共32条断言：原地雷／手雷致死；真实Ctrl蹲下、真实Z匍匐；站立／姿态伤害使用原PC_ApplyDamage端点。为有限隔离暂停NPC AI；地雷／匍匐定位明确属于测试夹具，既有平坦匍匐点不是新出生点，也不冒称自然人工交战。其余19次覆盖鼠标键盘菜单、枪弹资源、暂停后人物／引信／烟雾计时、全灭checkpoint与成功窗口／提示消失、地雷／清场后死亡、新进程与当前／copied-v16／旧档恢复，以及当前六人短时性能。已复看实际1080p／720p UI与死亡、确认、保存画面；未新增NPC压测、长期或第二机验收，人工视觉和手感仍待用户复验。

性能原始PERFORMANCE.json为900帧／14.997秒，平均帧耗时16.680ms、p95 18.452ms、GPU平均9.018ms。当前6人、正常AI、真实G/Q、1080p quality2/cap60、Editors开启，性能段不新增NPC／定位／hold；这是受限短测，不代表无上限FPS或长期压测。通用RESULT.scope的AI暂停描述不适用于性能分支，以原始PERFORMANCE.scope及实际分支记录为准。

## 保护与失败保留

精确逆向差异核对：父69仅7文件适配表现生命周期／UI、爆炸显示辅助及清场后探针时序，其余父文件与反射布局精确；新增4个非反射辅助文件。1754native、原模型／骨架／手指、枪械／弹药／伤害、存档schema／checksum／读回、NPC停尸、导航／AI、Catalog、正式52、父69／普通包与旧用户档均精确。

MI038保留v1编译失败；MI039保留v2数值通过但取景／footer失败；MI040保留v3／v4／v5火光不足及只读审计；MI041保留碎石初始位置匍匐准入失败。v6使用新身份，不覆盖失败原件。既存地雷UV handled ensure及原编译／材质／碰撞警告仍记录。raw／日志／源码／receipt保持私有，下面文档图按精确路径与哈希allowlist登记。无自动正式采用、Git／SFTP发布、录像或广泛清理。

## 实际文档图

![Actual mine blast / 实际地雷爆炸](../../Images/MissionLoopV1/PLAYER_DEATH_BLAST_20261011.png)

![Original collapse before UI / 原倒地后出界面](../../Images/MissionLoopV1/PLAYER_DEATH_COLLAPSE_20261011.png)

![Terminal corpse then menu / 终态尸体与菜单](../../Images/MissionLoopV1/PLAYER_DEATH_MENU_20261011.png)
