"""Write the result from closed receipts and register manually reviewed game frames."""
from pathlib import Path
import sys, shutil, json
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,sha
base=ROOT/'tmp/g1-combat-ui-20261011'; d=read(base/'DELIVERY_20261011.json')
perf=read(OUT/'checks/performance_ui_v5/PERFORMANCE_SUMMARY.json')
all_perf=perf['groups']['all_after_1s']
visual=read(base/'VISUAL_REVIEW.json'); assert visual['status']=='pass'
doc=ROOT/d['result']
figures=[('01_mission.png','COMBAT_UI_MISSION_20261011.png'),('02_player_squad.png','COMBAT_UI_SQUAD_20261011.png'),('03_help_0.png','COMBAT_UI_HELP_20261011.png'),('10_combat_hud.png','COMBAT_UI_HUD_20261011.png'),('post_save','COMBAT_UI_POST_SAVE_20261011.png')]
allow_path=ROOT/'Assets/Sync/GIT_DOCUMENT_IMAGE_ALLOWLIST.json';allow=read(allow_path)
ignore=ROOT/'.gitignore';ignore_text=ignore.read_text('utf-8-sig')
for src_name,dst_name in figures:
    src=OUT/'checks/enemy_clear_ui_v5/clean_hud.png' if src_name=='post_save' else base/'checks/ui_pages_v5'/src_name
    dst=ROOT/'Docs/Images/MissionLoopV1'/dst_name
    assert sha(src) in {p['sha256'] for p in visual['images']}
    assert not dst.exists() and src.stat().st_size<=5*1024*1024
    shutil.copyfile(src,dst);rel=dst.relative_to(ROOT).as_posix()
    assert not any(e['path']==rel for e in allow['files'])
    allow['files'].append(dict(path=rel,kind='project_document_illustration',documents=[d['implementation'],d['result']],provenance='Unedited actual UE final candidate_ui_v5 game frame, opt-in simulated UI input after approved FP display initialization. No debug geometry, commercial model/texture files, credentials, reference photos or private OS UI. Rendered project gameplay covered by the user-authorized public demonstration scope. Raw private diagnostic originals retained.',public_review='approved',reviewed_by='Codex under Yupu Guo document-image rule; actual final game pixels inspected on 11 October 2026 after MI033 timing correction',approved_versions=[dict(size_bytes=dst.stat().st_size,sha256=sha(dst))]))
    rule='!/'+rel
    assert rule not in ignore_text
    ignore_text+='\n'+rule+'\n'
write(allow_path,allow);ignore.write_text(ignore_text,encoding='utf-8')
table=[]
for c in d['checks']:
    result=read(ROOT/c['result'])
    table.append(f"| {c['mode']} | {result['status']} | {len(result.get('checks',[]))} / {len(result.get('events',[]))} |")
text=f'''# 作战菜单与操作帮助结果

2026-10-11。帮助、任务、人物与小队信息及情境提示已完成，合并手榴弹、烟幕、地雷、弹药补给，交付一个正常统一试玩候选。等待用户人工体验与选定；正式 enemy-clear 基线保持。先形成[实施文档](COMBAT_UI_IMPLEMENTATION_20261011_ZH.md)，再在独立源开发。

## 正常试玩

根 `PLAY_COMBAT_UI.cmd` 和现有 `PLAY_TACTICAL_EQUIPMENT.cmd` 都进入 `{d['playable_directory']}`。Enter开始；Esc打开作战暂停菜单，Tab直接查看人物与小队。菜单支持鼠标，左右切页、上下选择左侧操作、Enter激活，帮助页1–5切分类。F9读取、F6重开有确认，默认取消；已有保存窗口继续优先处理原交互。

人物、任务、装备数值均从现有实际对象读取。当前标签英文，沿用已cook字体。设置实现详细/简洁引导与HUD大小；会话偏好不进入存档。未实现的ADS、按键重绑和中英切换不显示可用按钮。

独立 UserDir `{d['user_dir']}`，prefix `{d['save_prefix']}`；旧正常用户档没有迁移或覆盖。运行入口无自动输入、探针、观察员、AI暂停或后台solo配置。UE现有两个Editor保持开启，诊断Game自行退出。

## 实际画面

任务只用三个登记敌军全灭完成，过桥是路线提示；显示圈内保存解锁和实际距离，明确未解除危险。

![实际任务页](../../Images/MissionLoopV1/COMBAT_UI_MISSION_20261011.png)

人物与小队显示真实血量、存活、姿态/动作、装填与备用弹药、距离及装备库存；没有新设军衔/技能或隐藏敌人列表。

![实际人物与小队页](../../Images/MissionLoopV1/COMBAT_UI_SQUAD_20261011.png)

五类帮助覆盖移动、武器、装备、交互与保存。G/Q按住准备松开投掷、hold E两米拆雷、箱子有限备用弹药、圈内保存均有说明。

![实际操作帮助](../../Images/MissionLoopV1/COMBAT_UI_HELP_20261011.png)

原血量、准星、枪械资源和玩家中心雷达保留；新增带按键和计数的G/Q装备、姿态、Esc/Tab入口。首次相关交互有短引导，原目标检测、拆雷进度与保存进度/成功窗口继续使用。

![实际战斗HUD](../../Images/MissionLoopV1/COMBAT_UI_HUD_20261011.png)

实际保存成功并关闭成功窗口后，原E保存选项与新增保存引导均消失；仍然保留真实地雷提示。

![保存完成后的干净HUD](../../Images/MissionLoopV1/COMBAT_UI_POST_SAVE_20261011.png)

图为实际UE帧，没有生成场景或替换模型。1080p与720p各十幅UI/帮助/设置/HUD原图、确认窗口已复看：题目/分类匹配，没有裁切、溢出或互相覆盖。低分辨率细节文字较小，最终可读性仍由用户体验确认。文档图公开安全审核、精确尺寸/哈希、文档链接及负向ignore规则已登记；raw证据保留私下。

## 同一最终Game实测

最终 `candidate_ui_v5` Game SHA-256 `{d['game_sha256']}`。以下19项全部在此Game实际独立运行，退出码0；没有将父候选通过结果算作本轮实跑。新UI探针仅用正常controller按键/鼠标事件，不改血量/库存/AI或传送。原回归探针仍有其明示的定位、AI hold、伤害端点/有限载荷夹具，不能算自然交战。

| 流程 | 结果 | checks / events记录 |
|---|---|---:|
{chr(10).join(table)}

暂停实测冻结游戏时间、玩家/全NPC位置、已释放手雷位置与引信、烟幕剩余寿命；关闭后继续剩余状态。菜单不执行移动/开枪/换弹/G/Q/E，鼠标返回不漏成一枪，释放移动键不粘住，普通移动可恢复。投掷准备Esc优先取消不扣资源。

原菜单37项、enemy_clear27项与P1回归检查原输入/枪械资源/动作和保存入口。圈内E实际保存显示原进度/成功窗口；真实双槽checksum/write/readback、新进程活引信/烟/库存/已拆雷/箱子状态恢复、复制旧v16和原V5兼容通过。额外弹药、补给ledger、库存、配置、引信守恒、重复ID和不存在陷阱等负向载荷继续被拒绝。没有加回过桥、盟军到达、站立/静止等保存任务门槛。

实际陷阱拆除/补给、两米边界/墙遮挡、烟幕行为、手榴弹取消与有限消耗回归通过。清场后真实地雷/手雷伤害仍能使玩家Lost，关闭旧保存窗口；F9确认读回、F6确认重开保留原世界与资源生命周期。

本机当前六人、原AI、1080p画质2、cap60、Editor开启的16秒装备合并短测：{all_perf['frame_ms']['samples']}个样本，平均{all_perf['mean_fps']:.2f}FPS，P95帧时间{all_perf['frame_ms']['p95_ms']:.2f}ms。不是无上限FPS、大量NPC压测、完整自然交火或长期稳定性验收。

## 保护闭合与失败记录

精确67文件源 `{d['source_snapshot']}`，manifest `{d['source_manifest_sha256']}`，authoring `{d['active_authoring_project']}`。在父63文件上添加四个非反射UI/诊断文件；八个已有文件只接绘制/输入/生命周期和opt-in确认回归。派生controller仅加非反射方法，没有新成员或反射字段，不改变cooked布局。

1754 native文件、正式52源/原Game、父63源/正常包、原与地雷用户档、Catalog与旧反射精确匹配。保存载荷/校验/事务、开枪/换弹/弹药/导航/匍匐及装备算法保留原字节范围。v2→v3去除换行差异后仅opt-in截图探针改变；v3→v4仅保存引导有效期及其诊断断言改变；v4→v5仅UI探针实际点击Ready开始，不再假定旧选择。详见本地 `{d['protection']}`、`tmp/g1-combat-ui-20261011/DELIVERY_20261011.json` 和各独立原始结果。

MI032保留首候选受保护API/TObjectPtr编译失败；MI033保留第二候选截图同帧切页错位，等待截图完成才切页。MI034保存类引导残留改为按当前操作可用性清除；MI035将旧v16 seed用例正确映射为原restore_equipment模式，最终实跑兼容。MI036明确点击原Ready开始按钮，正常退出无RESULT不算通过。实际像素重新验收。没有覆盖失败源/日志或把错位图改名充当通过。相关已有MI019/022/023/024/028/029/031防止反射、旧gate和失真验收再犯。

日志仍有父地雷候选既存的 transient static-mesh UVChannelData handled ensure；父原日志已核对同样信息，本轮未修改地雷模型/材质代码来消除该警告。运行继续且检查退出0，但不能声明日志零警告或GPU启动问题已根治。

尚未人工自然试玩、全动作/所有画面比例/失焦设备组合、大量NPC、第二机或新UI Editor/PIE/cook验收。没有自动选正式、Git提交/推送、SFTP、录像或清理。下一步由用户统一试玩反馈决定局部调整与正式选定。
'''
doc.write_text(text,encoding='utf-8')
implementation=ROOT/d['implementation']
with implementation.open('a',encoding='utf-8') as stream:
    stream.write('\n## 本轮结果与实图\n\n见[结果与验收边界](COMBAT_UI_RESULT_20261011_ZH.md)。实施后的实际画面：\n\n')
    for _,name in figures:stream.write(f'![实际UE作战UI](../../Images/MissionLoopV1/{name})\n\n')
(ROOT/'Docs/Development/CURRENT_UI_REVIEW.md').write_text(f'''# 当前UI与战术装备统一试玩候选

2026-10-11，等待人工试玩。根PLAY_COMBAT_UI.cmd与PLAY_TACTICAL_EQUIPMENT.cmd进入{d['playable_directory']}。精确67源、Game和manifest见同名JSON；authoring candidate_ui_v5。后续从此候选继续时不要从正式52或地雷63丢失新UI。

Esc作战暂停菜单，Tab人物/小队；四页与五类操作帮助、真实资源和任务、G/Q按键计数、情境引导。F6/F9与菜单危险操作二次确认。已有投掷/拆除/保存Esc优先，三守军全灭单独解锁圈内E。

19项最终Game实跑通过，1080p/720p实图复看，保护1754native/原模型手指/枪械/保存/父包与用户档。独立UserDir G1CombatUI20261011、prefixParisCombatUIV1，无旧档迁移，正常入口无自动输入。原正式基线未改；现有Editors保持开启，无新UI Editor/PIE/cook通过。MI032–036原件保留。

详见[实施文档](MissionLoopV1/COMBAT_UI_IMPLEMENTATION_20261011_ZH.md)和[结果/实图/验收范围](MissionLoopV1/COMBAT_UI_RESULT_20261011_ZH.md)。等待人工复验，无自动发布或清理。
''',encoding='utf-8')
equipment_doc=ROOT/'Docs/Development/CURRENT_EQUIPMENT_REVIEW.md'
equipment_doc.write_text('最新统一入口已增加UI，见[CURRENT_UI_REVIEW](CURRENT_UI_REVIEW.md)；本文及同名JSON保留地雷父候选身份。\n\n'+equipment_doc.read_text('utf-8-sig'),encoding='utf-8')
agents=ROOT/'AGENTS.md'; content=agents.read_text('utf-8-sig')
anchor='## Authority and scope\n'
assert content.count(anchor)==1
notice=f'''\n- Latest combat UI unified candidate,11 October2026: user authorizes implementation document then help/mission/player-squad/context UI and one combined equipment trial, preserving models/finger/gun/save. Read CURRENT_UI_REVIEW.json/md and MissionLoopV1/COMBAT_UI_IMPLEMENTATION/RESULT_20261011_ZH plus MI032–036 before continuation. Unselected normal PLAY_COMBAT_UI.cmd and PLAY_TACTICAL_EQUIPMENT.cmd point to {d['playable_directory']}; exact67 {d['source_snapshot']}, manifest {d['source_manifest_sha256']}, Game {d['game_sha256']}, authoring candidate_ui_v5. Esc true UE pause, Tab direct squad during gameplay, four pages/five help groups, actual status/resources, finite GQ plates/context guidance, session-only HUD scale/detail settings. F6/F9/new menu load/restart/exit use explicit default-cancel confirmation; Ready/Lost original buttons and checkpoint modals retain their original priority. Actors/world time/live frag fuse/smoke lifetime freeze then resume without refill. Save guidance clears immediately when its prompt is unavailable; do not reintroduce persistent E after success. Enemy elimination alone still completes/unlocks, circle/E/durable original validation unchanged. All19 final Game checks actually run, including explicit post-success hint disappearance, original menus/gun/equipment/negative payloads, real saves/new-process/legacy/copied v16, post-clear hazard Lost/F9/F6; 1080p/720p actual frames inspected. 1754native/formal52/parent63/old user files/Catalog/old reflection and protected gun/save/navigation/equipment algorithms exact. Independent UserDir G1CombatUI20261011/prefixParisCombatUIV1, no old-save migration. Formal selected enemy-clear baseline unchanged; manual review pending, no automatic adoption/Git/SFTP/cleanup/video. Preserve all v1–v4 failed/source/raw/receipt identities, including unknown-mode command rather than save-incompatibility claim. Existing Editors50836/51148 remain open; no UI Editor/PIE/cook or whole motion/large-NPC/second-machine/long-term acceptance. Short current-six-actor cap60 test is scoped in result; inherited mine UV handled ensure remains, no zero-warning/GPU-root-cause claim. Public-safe reviewed UI figures are exact-allowlisted, raw evidence remains private.\n'''
assert 'Latest combat UI unified candidate,11 October2026' not in content
agents.write_text(content.replace(anchor,anchor+notice,1),encoding='utf-8')
handoff=ROOT/'HANDOFF.md'
handoff.write_text(f'''## 2026-10-11：作战UI与装备统一试玩（未选正式）

用户授权先实施文档再开发帮助/任务/人物小队/情境提示；从地雷63继续，保留模型/手指/枪械/存档，正式52仍选定。
先读CURRENT_UI_REVIEW.json/md、MissionLoopV1/COMBAT_UI_IMPLEMENTATION/RESULT_20261011_ZH及MI032–036。
根PLAY_COMBAT_UI.cmd与PLAY_TACTICAL_EQUIPMENT.cmd进入{d['playable_directory']}；精确67源{d['source_snapshot']}，manifest {d['source_manifest_sha256']}，Game {d['game_sha256']}，authoring candidate_ui_v5。
Esc真暂停、Tab战斗中小队直达；四页/五类帮助/实际任务与血量动作弹药距离/有限GQ按键图示/首次引导/会话HUD设置。F6/F9及新菜单危险操作默认取消确认，原Ready/Lost按钮与保存modal优先。
暂停冻结原角色AI、世界时间、活引信与烟寿命，返回继续不补资源；鼠标返回不误射，松键恢复。保存引导按可用性立即消失，保留全灭单独解锁和圈内E原双槽读回。
19项同一最终Game实跑含UI与原菜单/枪械/装备/负向载荷/清場/真存档/跨进程/复制V5和v16/危险致死读档重开；1080p/720p实图复看、成功后干净HUD再检。
1754native/正式52/父63正常包/原用户档/Catalog/旧反射和受保护算法精确。独立UserDir G1CombatUI20261011/prefixParisCombatUIV1，无旧档迁移，正常入口无探针自动输入。
MI032 API编译、MI033异步截图、MI034保存引导残留、MI035误把用例名当模式均保留原件；当前候选只有v4可交付，原地雷63仍是父身份。
Editors50836/51148保持开启；没有新UI Editor/PIE/cook/完整动作/大量NPC/第二机/长期通过。既存地雷UV handled ensure保留说明，短六人cap60范围见结果。
人工复验待定，无自动正式选定、Git/SFTP/录制/清理。文档实图已精确登记allowlist，raw/资产/用户档继续保护。

'''+handoff.read_text('utf-8-sig'),encoding='utf-8')
print(doc)
