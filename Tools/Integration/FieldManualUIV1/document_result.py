"""Record actual delivered identities, approved figures and scoped results."""
from pathlib import Path
import sys,shutil
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,sha
review=read(ROOT/'Docs/Development/CURRENT_UI_REVIEW.json');assert review['revision']=='candidate_field_manual_v2'
docs=['Docs/Development/MissionLoopV1/FIELD_MANUAL_UI_RESULT_20261011.md','Docs/Development/MissionLoopV1/FIELD_MANUAL_UI_RESULT_20261011_ZH.md']
figures={
 'FIELD_MANUAL_HELP_20261011.png':'tmp/g1-combat-ui-20261011/checks/ui_pages_field_v2/03_help_0.png',
 'FIELD_MANUAL_MISSION_20261011.png':'tmp/g1-combat-ui-20261011/checks/ui_pages_field_v2/01_mission.png',
 'FIELD_MANUAL_SQUAD_20261011.png':'tmp/g1-combat-ui-20261011/checks/ui_pages_field_v2/02_player_squad.png',
 'FIELD_MANUAL_SETTINGS_20261011.png':'tmp/g1-combat-ui-20261011/checks/ui_pages_field_v2/08_settings.png',
 'FIELD_MANUAL_POST_SAVE_20261011.png':'tmp/g1-tactical-equipment-20261010/checks/enemy_clear_ui_field_v2/clean_hud.png'}
allow=ROOT/'Assets/Sync/GIT_DOCUMENT_IMAGE_ALLOWLIST.json';obj=read(allow);ignore=ROOT/'.gitignore';ignore_text=ignore.read_text('utf-8-sig')
for name,reference in figures.items():
    target=ROOT/'Docs/Images/MissionLoopV1'/name;assert not target.exists();shutil.copyfile(ROOT/reference,target)
    assert target.stat().st_size<=5*1024*1024
    path=target.relative_to(ROOT).as_posix();assert not any(x['path']==path for x in obj['files'])
    obj['files'].append(dict(path=path,kind='project_document_illustration',documents=docs,provenance='Unmodified actual candidate_field_manual_v2 UE Game screenshot, '+reference+'. No generated scene, raw supplier images, credentials or private correspondence. Models are inherited approved runtime assets. Original private raw frame/result retained.',public_review='approved',reviewed_by='Codex actual pixels inspected 11 October 2026 under user UI-optimization authorization and standing document-image rule',approved_versions=[dict(size_bytes=target.stat().st_size,sha256=sha(target))]))
    rule='!/'+path
    if rule not in ignore_text.splitlines():ignore_text=ignore_text.rstrip()+'\n'+rule+'\n'
write(allow,obj);ignore.write_text(ignore_text,encoding='utf-8')
table='| Check | Actual result | Checks / events |\n|---|---|---:|\n'
for item in review['checks']:
    result=read(ROOT/item['result']);table+=f"| {item['mode']} | {result['status']} | {len(result.get('checks',[]))} / {len(result.get('events',[]))} |\n"
links='\n'.join(f'![Actual UE field-manual screen](../../Images/MissionLoopV1/{name})\n' for name in figures)
en=f'''# Field-manual UI result

2026-10-11. The approved generated appearance has been implemented as real interactive UI, starting from candidate_ui_v5. One normal unified equipment/UI trial is ready for human review; the formal enemy-clear baseline is unchanged.

## Delivered behavior

PLAY_COMBAT_UI.cmd, PLAY_FIELD_MANUAL_UI.cmd and PLAY_TACTICAL_EQUIPMENT.cmd enter {review['playable_directory']}. Esc opens the combat menu; Tab opens player/squad during gameplay. Four pages share Cinzel title hierarchy, readable Roboto body text, text tabs and active underlines, small line symbols, fine dividers, consistent title/detail rows and compact right-side keycaps. Movement and stance are grouped with whitespace. Squad values use fixed columns; mission progress and checkpoint lock reflect actual state. Equipment HUD plates are lighter, while original health/ammo/radar composition remains.

Mouse/keyboard selection, settings effects, default-cancel confirmation, original Ready/Lost controls and checkpoint priority remain. Original model/finger/weapon/save/navigation/AI/equipment behavior is preserved. Real save-success acknowledgment still removes the save action and first-use guide.

Independent UserDir {review['user_dir']} / prefix {review['save_prefix']}; no old user-save migration or override. Normal entry has no probe, automated input, observer or AI/resource override. Existing Editors remain open; this result establishes Game checks, not new Editor/PIE/cook acceptance.

## Actual final Game evidence

Game SHA-256: {review['game_sha256']}. Exact69 source: {review['source_snapshot']}; source manifest SHA-256: {review['source_manifest_sha256']}. Matching authoring project: {review['active_authoring_project']}.

All19 checks below actually ran this final Game with complete pass results and exit0. UI probes use controller input without gameplay overrides. Original regression fixtures retain their documented positioning, held-AI, endpoint-damage and bounded payload fixtures; they are not natural human combat or large-NPC stress evidence.

{table}

Ten 1080p images were individually inspected. Ten 720p frames were reviewed in a contact sheet and original-size pages; settings descriptions/footer keycaps fit, page/category labels match and two-line rows remain separate. Confirmation, live paused grenade, throw/supply guidance, actual save success and clean post-save HUD were also inspected. The generated concept is separately labeled in the implementation document, never used as runtime evidence.

1754 native files, parent67 source/normal trial, original formal52/Game, models/fingers/audio, Catalog and prior user files remain exact. All other parent files, reflected layout and UI state/pause/confirmation/guidance logic remain byte-equivalent after removing the approved render/hit-coordinate/accessor changes. Only three parent files plus two new rendering includes differ. Packaged Roboto fonts retain the installed distribution's original Apache2 license and provenance.

MI037 preserves v1's actual font overflow despite passing interaction checks. v2 converts intended pixel sizes to font points using the installed Slate96DPI/72-point contract; v1 source/receipts/raw frames were not overwritten. See the failure archive and implementation plan.

No automatic formal adoption, Git/SFTP/video publication or cleanup. Human visual/play acceptance is pending. Current six-actor short capped-performance check has its original limited scope; no whole-motion, long-term, second-machine or large-NPC claim.

All19 final logs were audited: no fatal error or new handled ensure. The inherited mine static-mesh UV-channel handled ensure and existing build warnings remain recorded; this is not a zero-warning claim or a fix for those earlier asset diagnostics.

## Actual runtime illustrations

{links}
'''
zh=f'''# 战地手册 UI 优化结果

2026-10-11。从candidate_ui_v5将用户选定效果稿实现为真实交互界面，统一试玩已准备，等待人工外观/玩法复验；正式enemy-clear基线保持。

## 使用与改动

根PLAY_COMBAT_UI.cmd、PLAY_FIELD_MANUAL_UI.cmd、PLAY_TACTICAL_EQUIPMENT.cmd进入{review['playable_directory']}。Esc打开作战菜单，Tab在战斗中直达人物与小队。四页统一Cinzel标题/Roboto正文、文字页签和选中线、小图标、细分隔线、固定两行说明、右侧紧凑按键；移动/姿态分组留白，人物状态按列对齐，任务和存档锁定读取实际状态。G/Q装备HUD减轻底板，原血量、枪械与雷达构图保持。

鼠标/键盘、设置实际效果、默认取消确认、原Ready/Lost操作和存档窗口优先级保持。真实存档成功确认后，E保存操作和首次引导仍立即消失。模型、手指、声音、枪械、存档、装备、导航与AI原逻辑保留。

独立UserDir {review['user_dir']}、prefix {review['save_prefix']}，旧用户档不迁移/覆盖。正常入口无探针、自动输入、observer或资源/AI覆盖。现有两个UE Editor继续开启；本轮是Game实跑，不冒称新Editor/PIE/cook通过。

## 同一最终Game验收

Game SHA-256：{review['game_sha256']}。精确69源：{review['source_snapshot']}；manifest SHA-256：{review['source_manifest_sha256']}。匹配authoring：{review['active_authoring_project']}。

以下19项均在此最终Game实际运行，结果完整通过、exit0；未把父结果称为本轮。新UI探针仅经controller输入，不改玩法资源；原回归仍有其明示定位/AI hold/伤害端点/有限负向载荷夹具，不算自然人工交战或大量NPC压测。

{table}

1080p十幅逐张复看；720p十幅通过总览及原图检查，关键帮助/设置字号、footer按键框、两行说明、页名/分类一致。确认、暂停活手雷、投掷/补给引导、实际保存成功与成功后干净HUD亦复看。实施文档生成参考图明确标为效果稿，不混入实测图片。

1754native、父67源/正常试玩、正式52/Game、模型手指声音、Catalog与原用户档精确。原反射布局不变，三个父文件只改绘制/命中坐标、诊断坐标及非反射Canvas访问方法，并增加两份绘制include；其余父文件以及UI输入/暂停/确认/引导逻辑经限定反向比较精确。Roboto随包保留安装分发的Apache2原许可和来源记录。

MI037原样保留v1功能通过但实际字体溢出的失败；v2依据本机Slate96DPI/72点规则将预期像素字号转点数，不覆盖v1源/结果/图片。未自动正式采用、Git/SFTP/视频发布或清理。六人短cap60性能用例保留限定范围，不作为完整动作/长期/第二机/大量NPC通过。

19份最终日志已复核，没有fatal或新增handled ensure；既存地雷静态网格UV通道handled ensure及原编译警告继续记录，不声称零警告或修复了此前资产诊断。

## 实际UE画面

{links}
'''
(ROOT/docs[0]).write_text(en,encoding='utf-8');(ROOT/docs[1]).write_text(zh,encoding='utf-8')
(ROOT/'Docs/Development/CURRENT_UI_REVIEW.md').write_text('''# 当前战地手册UI与装备统一试玩

2026-10-11。candidate_field_manual_v2，等待人工视觉/玩法复验。根PLAY_COMBAT_UI.cmd、PLAY_FIELD_MANUAL_UI.cmd、PLAY_TACTICAL_EQUIPMENT.cmd进入tmp/Playtest-G1-FieldManualUI-20261011。精确69源/Game/manifest/checks见同名JSON。

四页按已选效果稿采用Cinzel/Roboto、文字页签、图标、细分隔线与固定两行说明；保留原模型手指、枪械、存档及装备逻辑，Esc真暂停/Tab小队/确认默认取消。实际19项最终Game检查通过、1080p/720p实图复看；正式52、父67、1754native、Catalog与旧档精确。独立UserDir/prefix不覆盖旧档，正常入口无自动输入。

见[实施](MissionLoopV1/FIELD_MANUAL_UI_IMPLEMENTATION_20261011_ZH.md)与[结果/实际画面](MissionLoopV1/FIELD_MANUAL_UI_RESULT_20261011_ZH.md)。MI037失败v1及旧MI032–036保留。现有Editors开启；没有新Editor/PIE/cook、大量NPC/长期/第二机通过，无自动正式采用/发布/清理。
''',encoding='utf-8')
attr=ROOT/'.gitattributes';s=attr.read_text('utf-8-sig')
for line in ['Unreal/Variants/G1FieldManualUI20261011/Project/** -text whitespace=cr-at-eol,-blank-at-eof','Unreal/Variants/G1FieldManualUI20261011/SOURCE_MANIFEST.json -text whitespace=cr-at-eol','Docs/Development/CURRENT_UI_REVIEW.json -text whitespace=cr-at-eol']:
    if line not in s.splitlines():s=s.rstrip()+'\n'+line+'\n'
attr.write_text(s,encoding='utf-8')
print('Recorded actual result, exact document figures and source-byte preservation rules')
