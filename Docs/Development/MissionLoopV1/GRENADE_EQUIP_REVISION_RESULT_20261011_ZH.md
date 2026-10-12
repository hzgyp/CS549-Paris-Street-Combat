# 手持投掷物与可用库存轮换结果

2026-10-11，本地统一候选完成，人工试玩待审。先写实施文档，读MI024、033、043、044与本轮MI045；显示／挂接诊断记MI046、047。

## 本轮实现

Ready不能再无条件端枪：新增非反射的临时FP动作源，复用已有Loop／Start／Far／Cancel。源映射只作用于投掷物显示，原身体ActionState在就绪时保持Ready，移动／保存不新增门槛。临时状态切换已有0.25秒混合；回枪完成后原Alpha=1、指姿误差约0.0000034度。原枪械握姿配置、30指姿常量与模型／骨架／权重不修改；投掷物使用原动作自己的姿势。

滚轮按当前库存查找下一可用项，正反跳过0库存。只剩步枪时在任何释放原鼠标／隐藏枪／切换动画之前返回；真实四枚都投完后仍可按原规则射击。HUD保留灰色0作为库存信息，0不是可轮换装备。G/Q旧投掷仍停用，左键准备／保持／松手投出、取消和自动回枪保留。

手雷网格／纹理无缺失。旧模型中心落在掌指中点、短MkII被手遮；实际显隐对照确认原因。临时FP取景按两种模型最大轴长、实际FOV／视口解算24%画面高度与(0.68,0.70)手持中心，只改变投掷物显示根。挂接使用四指根平均掌面、原动作掌面法线及实际横截面半径；原镜头、身体、模型大小不变。实际有手的Frag／Smoke就绪与长按外壳已检查，普通入口不隐藏手部。

## 实测

最终Game `b5357cd4ff39454ec40d72ba96ce8ab379f0e039c83b6170263f631e45c4124d`；source manifest `9ac0620c0794c2cc64c0b701d50e7dba4a82941bee7d147be1f72cd604d9312d`，76文件；普通100文件 `tmp/Playtest-G1-GrenadeEquip-20261011`。回执在 `tmp/g1-tactical-equipment-20261010/candidate_grenade_equip_build_v4`，完整行清单／SHA见DELIVERY与protection。

| 同一Game实际检查 | 结果 |
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
| `performance` | `pass_native_performance`，exit0 |
| `ui_equipment_pause` | `pass_ui_equipment_pause`，exit0 |
| `ui_pages` | `pass_ui_pages`，exit0 |
| `ui_pause` | `pass_ui_pause`，exit0 |
| `ui_confirm` | `pass_ui_confirm`，exit0 |
| `death_frag` | `pass_player_death_frag`，exit0 |

早期wheel检查使用真实控制器轮格＋轴配对，正常镜头，无新NPC或摄影机；现有NPC仅为独立动作隔离暂停。实际两枚Frag投出耗尽，再正反滚轮跳过Frag到Smoke／Rifle；两枚Smoke实际投出耗尽后六次双向轮格不改变枪、姿势或已按下的左键；原射击扣一发，18发资源守恒。长按4.5秒无弹体／扣数／计时爆炸；四个模型状态的原屏内面积比例门槛0.75不放宽，有手实图另行复看。

原烟幕双向感知遮蔽／最后所见记忆／穿烟枪械射击／消散再发现、原P1资源／换弹／小地图、地雷与补给、全灭圈内E保存、双槽checksum／write／readback及严格负向验证、装备及旧档还原、停尸不重播、菜单实际暂停冻结／恢复、死亡倒地后重开均重新实跑。performance仅当前六名角色正常AI和真实输入、1080p质量2／cap60／Editor开启的短记录，不是新增NPC压力或性能全面接受。

性能原始RESULT沿用了动作隔离检查的通用scope文字，未改写原回执。此项实际分支在暂停AI夹具之前返回，具体范围以同目录PERFORMANCE.json及原代码performance分支为准：现有六名角色正常AI，装备触发原生避险，未增加NPC或脚本暂停其行为。其通过表示采样和两次实际投掷完成，不能等同于帧率目标验收。

## 保护与限制

1754 native、父75／普通100／用户档／Catalog、8个模型运行文件和全部除exe外包文件精确保持。原BeginThrow、CommitThrow、PlayThrow、ThrowTick、EndThrow、BallTick、Blast逐字不变；原保存／枪械内部／镜头／AI／导航／死亡主体源保持。只改装备就绪来源、挂接、轮换、对应帮助及可选诊断；FP旧反射字段和原枪分支／常量保留，新增状态不序列化。

v1旧枪握点锚的Frag屏内比47.338%失败，无实图不作视觉通过。v2投影已入画但实图仍被手挡；第二次投出后夹具在旧0.25秒返回混合完成前查Alpha而提前失败，原库存已经正确归0。v3保存同一姿势／挂接的有手／无手对照，证明模型确实正常渲染；这组仅作诊断。v4使用掌面与外壳半径机制并等待实际混合完成，保留原门槛／动作／模型。全部失败／诊断源、Game、结果和原图原位保留。

本轮修复人工报告的端枪、空槽和不可见表现；没有证明完整动画全程、所有运动转换或精细接触均无误。新普通包待人工统一试玩，独立UserDir和存档前缀，不迁移原用户档。正式基线不采用／不发布／不清理；现有两个UE Editors保持开启。
