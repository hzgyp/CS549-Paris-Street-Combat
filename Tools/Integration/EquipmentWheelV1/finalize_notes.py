from pathlib import Path
import sys
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import read,write
r=read(root/'Docs/Development/CURRENT_EQUIPMENT_INPUT_REVIEW.json')
body=f'''# 当前滚轮装备统一试玩候选

2026-10-11，本地待人工复验，未正式采用。普通入口：`{r['playable_entry']}`，源码 `{r['source_snapshot']}` 共75文件，Game `{r['game_sha256']}`。

滚轮下：步枪→手雷→烟雾弹→步枪；上反向。选中投掷物后左键按住准备、不计时爆炸，松开投出并扣一个；动作结束回步枪。松手前Esc或滚轮可取消，不扣库存，旧松开不会误射；必须重新按下。零库存不会透传开枪，G/Q旧投掷停用。操作帮助和装备栏已同步。

承接原 Mk II／AN-M8外壳、人物／手指／动作／枪械、全灭敌军存档、烟幕感知、地雷／补给及第三人称死亡。1754原生、原用户档、Catalog和全部除exe外运行文件哈希保持；枪械／存档代码及原提交、动画、轨迹、伤害函数保持。

14个同一Game实际UE检查正常退出并通过：滚轮／长按／释放／取消／空库存、投掷、烟幕、枪械P1、全灭存档、拆雷补给、装备保存与恢复、旧档恢复、装备暂停、各UI页、暂停、确认菜单、手雷死亡重开。早期v1计数／截图和v2过早烟幕见证见MI043，v3空库存提示残留见MI044，原回执保留。当前没有新增NPC／性能压力／人类失焦操作验收。

独立UserDir `{r['user_dir']}`，前缀 `{r['save_prefix']}`。原Hold姿态位于屏幕下沿，本轮没有重做握姿或消除该限制。选中道具沿用既有手部姿态，尚未获统一人工试玩通过。UE Editors保持开启，正常入口无探针／自动输入／AI或资源覆盖，正式source52和根启动器保持。

方案：[输入实施文档](MissionLoopV1/EQUIPMENT_WHEEL_INPUT_IMPLEMENTATION_20261011_ZH.md)；结果：[实际验证](MissionLoopV1/EQUIPMENT_WHEEL_INPUT_RESULT_20261011_ZH.md)。模型专项原评审见[模型记录](CURRENT_GRENADE_MODEL_REVIEW.md)，不改其历史身份。
'''
for name in ['CURRENT_EQUIPMENT_INPUT_REVIEW','CURRENT_UI_REVIEW']:(root/('Docs/Development/'+name+'.md')).write_text(body,encoding='utf-8')
result='''# 滚轮装备与左键投掷结果

2026-10-11：本地统一候选完成，待人工试玩。实施方案已先写；先读MI024、026、032、034、042，见证修订补读MI033、043。

## 实现

滚轮向下步枪／手雷／烟雾弹循环，向上反向；同一UE滚动的按键与轴事件只切换一次。三项装备栏高亮当前选择，帮助和情境提示同步。选中投掷物时展示既有道具／隐藏显示枪，左键按下进入原Start，按住停在原Hold；超过4.5秒仍不扣库存、不生成弹体／启动引信。松开后原Far投掷在原提交时刻扣一个、生成唯一弹体，结束回步枪。

松手前Esc／滚轮取消，原Cancel恢复且不扣库存；旧鼠标松开不误射，需重新按下。已松手不能撤销或切换本次投掷。空槽仍可选择，左键／R／右键不会透传枪械；G/Q直接投掷停用。菜单／保存弹窗／死亡优先接管输入。选择和按压是非序列化临时状态；重开／恢复回步枪。窗口失焦取消未松手准备的代码已实现，人工系统级失焦尚待复验。

## 实测和保护

'''
result+=f"最终Game `{r['game_sha256']}`；源码manifest `{r['source_manifest_sha256']}`，75文件；普通目录 `{r['playable_directory']}`，100文件。构建回执／保护审计在 `tmp/g1-tactical-equipment-20261010/{r['revision']}`。\n\n"
result+='| 实际UE检查 | 结果 |\n| --- | --- |\n'
for c in r['checks']:result+=f"| `{c['mode']}` | `{c['status']}`，exit0 |\n"
result+='''
滚轮检查明确覆盖真实digital+axis双事件、正反循环、旧G/Q停用、选中不准备、长按4.5秒无扣数／弹体／射击、重复松开仍只提交一次、投后原步枪射击、按住切换／Esc取消、真实投出两枚后空库存、旧释放不射击、新按压才能射击和暂停菜单输入隔离。烟幕沿用双向感知遮蔽、最后所见记忆、穿烟原枪械射击、消散重新发现；P1检查原资源守恒、换弹／射击与小地图。保存检查从选中烟雾弹状态进入原全灭存档，真实双槽checksum／write／readback、失败负载拒绝；新进程还原装备效果和旧档，选择回步枪。UI检查含真实暂停计时／确认／全部帮助分类。死亡检查用正常控制器实际投出手雷、原伤害和第三人称倒地后重开。

1754 native、父source74／普通100文件／原用户档／Catalog和全部除exe外运行资产精确保持。枪械／保存／互动门槛／世界逻辑／新模型网格和贴图／死亡主体源码逐字保持；原CommitThrow、PlayThrow、ThrowTick、BallTick、Blast保持，BeginThrow仅增加销毁临时选中展示，其初始化、原动画和原hand_r／掌指间挂接不变。源码变动限六个装备／UI／诊断文件，加一个可选滚轮探针；全量清单和文件哈希见本地DELIVERY和protection。

## 失败与限制

v1构建成功，轮换／长按／唯一提交通过；随后过早缓存原射击计数而误报失败。实际原步枪已射击一次，loaded7／reserve10／shots1。异步截图同帧继续按左键还造成“选中”图为准备状态。v2纠正夹具取值／截图时机后，射击／取消通过；随后从按下时刻提前要求已有烟幕，忽略原动作和提交后3.5秒引信。v3等待真实烟幕事件，输入通过，但实际HUD在切回步枪后仍残留烟雾弹空库存提示；v4切换时清除旧Notice、空槽不显示外壳，并检验实际像素。MI043／MI044保留各轮原身份；枪械／资源／保存门槛始终不变。最终所有检查来自同一v4Game。

本轮不修改原人物／手指／枪械模型，也不调整原Hold的低屏幕位置。真实UE图片已逐张查看装备栏和装备帮助；并不构成全动作握持／连续接触或人工输入认可。检查在当前人数／注明夹具中进行，无新增NPC压测、独立性能或第二电脑新验收。普通入口留tmp独立目录；正式基线、Git／SFTP发布与旧版本清理未执行，现有UE Editors仍开着。
'''
(root/r['result']).write_text(result,encoding='utf-8')
regp=root/'Assets/Registry/registry.json';reg=read(regp)
assert not any(s['id']=='equipment-input-review' for s in reg['selectors'])
reg['selectors'].append(dict(id='equipment-input-review',channel='candidate',title='滚轮装备／左键投掷统一评审候选',path='Docs/Development/CURRENT_EQUIPMENT_INPUT_REVIEW.json',assets=['frag-grenade','smoke-grenade','first-person','pressure-mine','allied-soldier','german-soldier','german-rifle','recorded-audio','paris-city'],optional=True))
write(regp,reg)
note=f"Latest local equipment-wheel input candidate,11 October2026: user requests wheel rifle/frag/smoke and held primary prepare/release throw. Read CURRENT_EQUIPMENT_INPUT_REVIEW and paired EQUIPMENT_WHEEL_INPUT implementation/result. Source75 Unreal/Variants/G1EquipmentWheel20261011/Project, Game {r['game_sha256']}; 14 final actual Game checks exit0, native1754/models/fingers/gun/save/parent74/user/Catalog/runtime assets exact. Authoring tmp/g1-tactical-equipment-20261010/candidate_equipment_wheel_v1/Project contains final build_v4; immutable v1/v2 witness failures MI043 and v3 stale hint MI044 retained. Normal100 tmp/Playtest-G1-EquipmentWheel-20261011/PLAY_EQUIPMENT_WHEEL.cmd uses new UserDir/prefix, no probes/AI/input overrides. Selection/press state transient; original enemy-clear circle/E and actual save validators remain. Manual review pending; original low Hold/grasp limitations and human focus test remain. Formal52/root launcher unchanged; no adoption/Git/SFTP/cleanup. Existing Editors remain open per user standing authorization."
for name in ['AGENTS.md','HANDOFF.md']:
    f=root/name;t=f.read_text('utf-8-sig');first=t.find('\n')+1
    t=t[:first]+'\n'+ ('- '+note if name=='AGENTS.md' else note)+'\n'+t[first:];f.write_text(t,encoding='utf-8')
print('Current notes and index selector registered; platform refresh pending')
