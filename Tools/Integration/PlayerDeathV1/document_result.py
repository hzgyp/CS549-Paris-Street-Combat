"""Publish local review documents only after the frozen delivery gates pass."""
from pathlib import Path
import sys,shutil
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import read,write,sha
base=ROOT/'tmp/g1-player-death-20261011';d=read(base/'DELIVERY_20261011.json')
assert len(d['checks'])==24 and d['revision']=='candidate_death_v6'
docs=['Docs/Development/MissionLoopV1/PLAYER_DEATH_PRESENTATION_RESULT_20261011'+s+'.md' for s in ['', '_ZH']]
figures=[]
allow_path=ROOT/'Assets/Sync/GIT_DOCUMENT_IMAGE_ALLOWLIST.json';allow=read(allow_path)
for name,raw in [('BLAST','02_death_start.png'),('COLLAPSE','04_collapse.png'),('MENU','05_terminal_menu.png')]:
    src=base/'checks/mine_v6'/raw;rel='Docs/Images/MissionLoopV1/PLAYER_DEATH_'+name+'_20261011.png';dst=ROOT/rel
    assert not dst.exists() and src.stat().st_size<=5*1024*1024
    shutil.copyfile(src,dst);assert sha(src)==sha(dst)
    figures.append(rel)
    allow['files'].append(dict(path=rel,kind='project_document_illustration',documents=docs,provenance='Unmodified actual candidate_death_v6 UE Game mine_v6 screenshot '+src.relative_to(ROOT).as_posix()+'. No generated scene, raw supplier image, credentials or private correspondence; approved runtime models. Private raw frame/result retained.',public_review='approved',reviewed_by='Codex actual pixels inspected 11 October2026 under user death-presentation request and standing document-image rule',approved_versions=[dict(size_bytes=dst.stat().st_size,sha256=sha(dst))]))
write(allow_path,allow)
with (ROOT/'.gitignore').open('a',encoding='utf-8') as f:f.write('\n# Exact reviewed death-sequence document figures.\n'+''.join('!/'+p+'\n' for p in figures))
with (ROOT/'.gitattributes').open('a',encoding='utf-8') as f:f.write('\nUnreal/Variants/G1PlayerDeath20261011/Project/** -text whitespace=cr-at-eol,-blank-at-eof\nUnreal/Variants/G1PlayerDeath20261011/SOURCE_MANIFEST.json -text whitespace=cr-at-eol\nDocs/Development/CURRENT_PLAYER_DEATH_REVIEW.json -text whitespace=cr-at-eol\n')
table='\n'.join('| '+c['mode']+' | '+c['status']+' |' for c in d['checks'])
ident=f"Source: `{d['source_snapshot']}` (73 files); manifest SHA256 `{d['source_manifest_sha256']}`. Game SHA256 `{d['game_sha256']}`. Authoring: `{d['active_authoring_project']}`. Normal trial: `{d['playable_entry']}`. Independent UserDir `{d['user_dir']}` / prefix `{d['save_prefix']}`; no old-save migration."
imgs='\n\n'.join('!['+n+'](../../Images/MissionLoopV1/'+Path(p).name+')' for n,p in zip(['Actual mine blast / 实际地雷爆炸','Original collapse before UI / 原倒地后出界面','Terminal corpse then menu / 终态尸体与菜单'],figures))
perf=read(ROOT/'tmp/g1-tactical-equipment-20261010/checks/performance_ui_death_v6/RESULT.json')
write(base/'PERFORMANCE_COPY.json',perf)
en=f'''# Player death presentation and trial placement result

11 October2026. Local unified candidate ready for human review. Five actual death runs and19 existing UI/equipment/save/regression runs pass on the same final Game; all exit0. Formal selected enemy-clear52 and published course package remain unchanged.

## Resulting behavior

All newly dead players use the original damage/PC_Die/Lost authority immediately. A transient third-person camera reveals the original full body and watches original Rifle_Death_3 to its3.933333s terminal pose; after its end plus0.25s, YOU DIED and original restart/load/exit controls appear. The mine witness completes at4.184637s. During collapse, HUD/menu/restart/load/fire/equipment input are suppressed. Restart removes the old world/camera and returns an alive100HP player. NPC saved corpses still restore directly stopped at their terminal pose; no replay.

Mine and frag blasts now visibly produce a brief warm fire burst, dust and light. Existing compatible cooked fire material uses11x11 SubUV with transient runtime curves explicitly not baked and dynamic usage flags. Mine diagnostic records24 fire particles, alpha0.891810, plus18 dust particles; unmodified early images show visible fire. Fire particle life0.65s/dust1.6s; no extra collision, cover or persistent fire damage. Original blast radii/occlusion/damage/audio remain exact. v6 fixes several rendering prerequisites together; the final pass does not isolate one parameter as the sole cause.

Three newly added root trial wrappers were relocated with exact frozen hashes to private tmp evidence. All new trial packages and launchers stay in tmp/Playtest-*/; the parent normal package remains byte exact. Existing formal root launcher is preserved.

## Exact candidate

{ident}

Normal launch has no probe, automatic input, observer or AI/resource override. Editor50836/51148 remain open; this Game validation adds no new Editor/PIE/cook acceptance.

## Actual checks and scope

| Run | Final status |
| --- | --- |
{table}

Death runs total32 assertions. Mine/frag use original hazards, crouch uses real Ctrl, prone uses real Z at the earlier measured flat site, standing/posture death uses original PC_ApplyDamage endpoint damage. NPC AI is paused for finite isolation; mine/prone relocation is a declared fixture, not a new gameplay spawn or natural combat claim. The existing19 include real mouse/keyboard menus, weapon/ammo checks, paused actors/fuses/smoke, clear-only checkpoint and success window/hint closure, mines and post-clear deaths, new-process/current/copied-v16/legacy restores and six-actor short performance. Actual1080p/720p UI and death/confirmation/save frames reviewed. No added NPC stress, long-term, second-machine or human perceptual acceptance claimed.

## Protected baseline and retained failures

Strict reverse-delta comparison: seven parent files adapt only presentation lifecycle/UI, blast render helper and later post-clear probe actions; all other parent files and reflected layout exact. 1754 native assets, models/rig/fingers, gun/ammo/damage, checkpoint schema/checksum/readback, original NPC terminal restore, navigation/AI, Catalog, formal52, parent69/normal package and original user saves remain exact. New source adds four nonreflected helper files.

MI038 preserves failed v1 compile; MI039 preserves v2 numeric pass but bad framing/footer; MI040 preserves v3/v4/v5 insufficient fire pixels and read-only audits; MI041 preserves the prior rubble-site prone-admission failure. Final v6 is a fresh identity. Native UV handled ensure and inherited compile/material/collision warnings remain recorded. Raw frames/logs/source/receipts remain private, reviewed document images are exact allowlisted below. No automatic adoption, Git commit/push, SFTP publication, recording or broad cleanup.

## Actual document images

{imgs}
'''
zh=f'''# 玩家死亡表现与试玩目录结果

2026-10-11。统一本地候选已完成，等待用户试玩。最终同一个Game的5项死亡测试与19项既有UI／装备／存档回归全部通过，24次均exit0；正式已选enemy-clear52与已发布课程包保持。

## 交互结果

所有新发生的玩家死亡立即执行原伤害、PC_Die和Lost保护，再由临时第三人称镜头显示原整身人物，播放原Rifle_Death_3至3.933333秒末态；结束后短停0.25秒，再出现YOU DIED和原重开／读档／退出按钮。地雷实测整段4.184637秒。倒地期间HUD和菜单暂不出现，射击、装备、读档、重开输入受限；重开后旧世界镜头清理，玩家100血恢复。旧NPC尸体读档仍直接停末态，不重播。

地雷与手雷爆炸都有可见短火光、尘烟与灯光；复用现有兼容火焰材质和11×11序列，瞬态曲线明确不烘焙，并更新动态模块用途标志。实际日志为24个火焰粒子、透明度0.891810及18个尘烟粒子，原始早期截图中火光清楚可见。火焰粒子0.65秒、尘烟1.6秒，不增加碰撞、视线遮挡规则或持续烧伤；原爆炸录音、半径／遮挡／伤害保持。v6同时补齐多个渲染前提，不能冒称某一参数已单独证明为唯一根因。

本轮三个根试玩cmd已依冻结SHA迁到私有tmp记录，新试玩包及入口一律放tmp/Playtest-*/。父普通包字节保持，正式既有根入口保留。

## 精确身份

{ident}

普通启动无探针、自动输入、观察器或AI／资源覆盖，不迁移覆盖旧存档。现有两个Editors50836／51148继续开启；本次Game验证不冒称新Editor／PIE／cook验收。

## 实测与范围

| 测试 | 最终状态 |
| --- | --- |
{table}

死亡5次共32条断言：原地雷／手雷致死；真实Ctrl蹲下、真实Z匍匐；站立／姿态伤害使用原PC_ApplyDamage端点。为有限隔离暂停NPC AI；地雷／匍匐定位明确属于测试夹具，既有平坦匍匐点不是新出生点，也不冒称自然人工交战。其余19次覆盖鼠标键盘菜单、枪弹资源、暂停后人物／引信／烟雾计时、全灭checkpoint与成功窗口／提示消失、地雷／清场后死亡、新进程与当前／copied-v16／旧档恢复，以及当前六人短时性能。已复看实际1080p／720p UI与死亡、确认、保存画面；未新增NPC压测、长期或第二机验收，人工视觉和手感仍待用户复验。

## 保护与失败保留

精确逆向差异核对：父69仅7文件适配表现生命周期／UI、爆炸显示辅助及清场后探针时序，其余父文件与反射布局精确；新增4个非反射辅助文件。1754native、原模型／骨架／手指、枪械／弹药／伤害、存档schema／checksum／读回、NPC停尸、导航／AI、Catalog、正式52、父69／普通包与旧用户档均精确。

MI038保留v1编译失败；MI039保留v2数值通过但取景／footer失败；MI040保留v3／v4／v5火光不足及只读审计；MI041保留碎石初始位置匍匐准入失败。v6使用新身份，不覆盖失败原件。既存地雷UV handled ensure及原编译／材质／碰撞警告仍记录。raw／日志／源码／receipt保持私有，下面文档图按精确路径与哈希allowlist登记。无自动正式采用、Git／SFTP发布、录像或广泛清理。

## 实际文档图

{imgs}
'''
for path,text in zip(docs,[en,zh]):(ROOT/path).write_text(text,encoding='utf-8')
current=f'''# Current player death and field manual unified trial

11 October2026. candidate_death_v6, local tested candidate; human review pending.

{ident}

All-player third-person original collapse precedes YOU DIED/restart/load; mine/frag short visible fire feedback. Models/fingers/gun/save/native assets preserved.24 final-Game runs pass. Trial packages/launchers stay under tmp. Existing Editors remain open; no formal adoption/publication.

Read [implementation](MissionLoopV1/PLAYER_DEATH_PRESENTATION_IMPLEMENTATION_20261011_ZH.md), [result and real images](MissionLoopV1/PLAYER_DEATH_PRESENTATION_RESULT_20261011_ZH.md), [review identity](CURRENT_PLAYER_DEATH_REVIEW.json) and MI038–041. Parent69 field-manual and older source/raw remain protected historical identities.
'''
for name in ['CURRENT_PLAYER_DEATH_REVIEW.md','CURRENT_UI_REVIEW.md']:(ROOT/'Docs/Development'/name).write_text(current,encoding='utf-8')
handoff=ROOT/'HANDOFF.md';text=handoff.read_text(encoding='utf-8-sig');start=text.index('## 2026-10-11：试玩入口目录与玩家死亡表现修订');end=text.index('## 2026-10-11：战地手册',start)
text=text[:start]+f'''## 2026-10-11：玩家死亡表现与tmp统一试玩（待人工复验）

当前候选读取CURRENT_PLAYER_DEATH_REVIEW.json/md与CURRENT_UI_REVIEW.json/md，再读MissionLoopV1/PLAYER_DEATH_PRESENTATION实施／结果及MI038–041。所有试玩包／cmd留tmp；三个本轮根试玩包装脚本已精确迁移，不重建。
{ident}
5项死亡+19项既有回归全部最终Game实跑通过，真实火光／整身倒地／末态菜单和1080p／720p UI已复看。原Lost立即，原3.933333秒倒地结束后短停再出YOU DIED；早期动作受限，重开清理镜头，旧NPC停尸不重播。原模型／手指／枪械／存档／1754native及旧用户档精确。
普通入口无探针／自动操作；Editors50836／51148继续开启。正式52与发布课程包不变，待人工复验，不自动采用／提交／发布／录像／清理。v1–v5失败源与raw均保留；v6组合渲染修正通过，不冒称单参数唯一根因。

'''+text[end:];handoff.write_text(text,encoding='utf-8')
agents=ROOT/'AGENTS.md';text=agents.read_text(encoding='utf-8-sig');text=text.replace('new Game acceptance is still required.','Final Game acceptance is recorded in CURRENT_PLAYER_DEATH_REVIEW and the paired result; human review remains pending.',1)
entry=f'''- Latest local player-death unified candidate,11 October2026: user requires mine fire feedback and all-player third-person collapse before death/restart UI. Read CURRENT_PLAYER_DEATH_REVIEW.json/md, CURRENT_UI_REVIEW.json/md and MissionLoopV1/PLAYER_DEATH_PRESENTATION_IMPLEMENTATION/RESULT_20261011 plus MI038–041. Exact73 `{d['source_snapshot']}`, manifest{d['source_manifest_sha256']}, Game{d['game_sha256']}, authoring candidate_death_v6; normal `{d['playable_entry']}`. All24 same-final-Game runs exit0, actual visible mine/frag fire, original3.933333s full-body collapse then YOU DIED, early input suppression/restart cleanup and1080p/720p UI reviewed. Original damage/Lost immediate; checkpoint enemy-clear-only/schema/resource/checksum/write/readback, saved-NPC stopped terminal restore and models/fingers/gun/AI/navigation/1754native/formal52/parent69/normal/old user files/Catalog exact. No native edits/cook/new rig/pose. Isolated death endpoint/posture/relocation fixtures declared, no natural-combat/full-map/large-NPC/long-term/second-machine claim. Independent G1DeathPresentation20261011/ParisDeathPresentationV1; no normal probes/automation or old-save migration. All trial launchers/packages stay in tmp, root wrappers remain retired. Existing Editors50836/51148 remain open. Manual play review pending; no automatic formal adoption/Git/SFTP/video/broad cleanup. Preserve v1–v5 failed source/build/raw and audits; v6 combined curve/dynamic/compatible-sprite correction passes, not isolated single-cause proof. Inherited UV handled ensure/warnings remain; reviewed actual document figures exact-allowlisted.

'''
text=text.replace('## Authority and scope\n\n','## Authority and scope\n\n'+entry,1).replace('Root PLAY_COMBAT_UI.cmd, PLAY_FIELD_MANUAL_UI.cmd and PLAY_TACTICAL_EQUIPMENT.cmd now enter tmp/Playtest-G1-FieldManualUI-20261011.','Historical root trial wrappers are retired; the parent remains at tmp/Playtest-G1-FieldManualUI-20261011/PLAY_COMBAT_UI.cmd.',1);agents.write_text(text,encoding='utf-8')
readme=ROOT/'README.md';text=readme.read_text(encoding='utf-8-sig');text=text.replace('Player death presentation is being revised under the [implementation plan](Docs/Development/MissionLoopV1/PLAYER_DEATH_PRESENTATION_IMPLEMENTATION_20261011.md);','The latest unified trial is `tmp/Playtest-G1-DeathPresentation-20261011/PLAY_COMBAT_UI.cmd`: visible mine/frag fire and original third-person collapse before the death/restart menu, with24 final-Game checks passing; see [actual results/images](Docs/Development/MissionLoopV1/PLAYER_DEATH_PRESENTATION_RESULT_20261011_ZH.md). Human review is pending;',1);readme.write_text(text,encoding='utf-8')
print('Documented exact candidate and three unmodified reviewed images')
