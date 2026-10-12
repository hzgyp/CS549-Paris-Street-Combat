"""Select the unchanged reviewed76 source after verified local retirement."""
from pathlib import Path
from manage import ROOT, OUT, PROOF, CURRENT, AUTHOR, GAME, MANIFEST, INNER, now, read, write, sha, proof, selected_checks, engines

def prepend(p, text):
    old = p.read_bytes()
    assert text.splitlines()[0] not in old.decode('utf-8-sig'), 'Preserve occupied adoption identity'
    if old.startswith(b'\xef\xbb\xbf'):
        p.write_bytes(b'\xef\xbb\xbf'+text.encode('utf-8')+old[3:])
    else:
        p.write_bytes(text.encode('utf-8')+old)

def main():
    r = selected_checks()
    authority, plan, mapping = proof()
    retirement = read(OUT/'local-retirement.json')
    assert retirement['targets'] == len(plan['targets'])
    assert all(not (ROOT/t['path']).exists() for t in plan['targets'])
    prior = read(OUT/'previous_baseline.json')
    at = now()
    auth = '用户：已人工验证，还有衣服遮挡小问题，但逻辑没啥问题，把正式版同步到这一版，其他过渡版本可以删除'
    baseline = dict(prior)
    baseline.update(schema_version=3, status='selected_active_development_baseline', authorization=auth, selected_at=at,
        baseline_id='g1-complete-gameplay-grenade-equip-20261011', playable_directory=CURRENT,
        playable_entry=r['playable_entry'], stable_local_entry='PLAY_CURRENT_G1.cmd', game_sha256=GAME,
        source_snapshot=r['source_snapshot'], source_manifest=r['source_manifest'], source_manifest_sha256=MANIFEST,
        active_authoring_project=AUTHOR+'/WW2FranceLiberation.uproject', active_source_files=76,
        save_prefix=r['save_prefix'], save_directory='%LOCALAPPDATA%/ParisStreetCombat/'+r['user_dir'],
        human_manual_review='Logic accepted by explicit user manual verification11October2026; residual sleeve occlusion reported',
        human_review_scope='Logic manually accepted; sleeve visual issue remains. No new quantified contact/FPS/large-NPC/Editor/second-machine/course acceptance.',
        matching_source_revision='Exact reviewed76 local source; no Git commit or push in adoption task',
        verified_runs={c['mode']:dict(status=c['status'],result=c['result'],result_sha256=c['sha256'],game_sha256=c['game_sha256']) for c in r['checks']}, checks=r['checks'], selected_review='Docs/Development/CURRENT_EQUIPMENT_INPUT_REVIEW.json',
        retirement_map='Docs/Development/G1GameplayBaselineAdoption20261011/RECOVERY_MAP_20261011.json',
        previous_selected_baseline=dict(role='One previous formal52 normal package retained for older recovery dependencies; historical source/checks kept', selector=prior),
        sftp_release=None, sftp_download=None,
        publication_status='Local baseline adopted; no new Git/SFTP/course/video publication in this task',
        accepted_features=['Frag/smoke wheel selection, hold/release/cancel, available-only inventory cycle', 'Visible original frag/smoke exteriors and compatible native throw pose', 'Ground-contact mine explosion and nearby held-E disarm', 'Finite ammunition supplies', 'Field-manual help/mission/player-squad and real pause', 'All-player third-person collapse before restart menu', 'Enemy-clear-only checkpoint unlock, circle/explicit E and original durable validation'],
        remaining_gates=['User-reported sleeve/clothing occlusion', 'Fine contact/full-motion and remaining ADS/en-bloc presentation polish', 'Further HUD and mission/gameplay refinement', 'Additional NPC behavior and enlarged-population stress', 'Exact reusable German live-fire source', 'Matching76 Editor/recook and second-machine validation', 'Fresh private delivery and course acceptance for this76 revision'],
        future_rule='Start from exact76 G1GrenadeEquip20261011 or matching candidate_grenade_equip_v1/Project (contains final build_v4). Preserve models, rifle finger constants/branch, gun/resources, enemy-clear-only checkpoint and original save validators. Use existing licensed actions/assets. Build matching Editor before entry; existing Editors stay open. Consult failure records and current recovery map; old raw receipts retain dated status.')
    write(ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json', baseline)
    text=f'''# 当前正式开发基线

2026-10-11，用户人工验证完整玩法统一版，确认逻辑无问题，要求正式采用；仍有衣服／衣袖遮挡小问题，保留为待修项。

正常入口 `{r['playable_entry']}`；已有稳定入口 `PLAY_CURRENT_G1.cmd` 指向同一程序。包继续留在专用tmp目录。存档继续使用 `{baseline['save_directory']}`，前缀 `{r['save_prefix']}`；未移动、覆盖或合并旧用户存档。

当前精确76文件源 `{r['source_snapshot']}`，制作工程 `{AUTHOR}/WW2FranceLiberation.uproject`（历史v1目录含final build_v4）。Game SHA256 `{GAME}`；manifest `{MANIFEST}`。源码和已验证可执行字节均不变。本次没有重新构建／进入Editor；现有两个Editor保持开启，不能把旧Editor DLL当76版。

承接手雷／烟雾、长按准备松手投出／取消、可用库存轮换、地图地雷爆炸与附近拆除、有限弹药补给、战地手册UI、人物小队信息及死亡倒地后重开。两种投掷物全耗尽时保持步枪；原步枪手指常量／持枪分支、人物模型、枪械／资源、原全灭敌军圈内E保存校验保持。原步行2.2／跑步4.5米每秒、8+10初始子弹保留。

已有15项最终Game检查及实际就绪／长按图通过，最新人工逻辑通过。当前人数短性能记录与隔离夹具不等于新增大量NPC、全程精细接触、第二机或课程验收。衣袖遮挡及其余表现／玩法／NPC压力工作留在待办。

七份旧普通试玩、旧Runtime／Archive／Binaries和闲置构建缓存按[实施](G1_GAMEPLAY_BASELINE_ADOPTION_20261011_ZH.md)及[结果](G1_GAMEPLAY_BASELINE_ADOPTION_RESULT_20261011_ZH.md)清理；原源码、失败／日志／图／检测、Saved/Cooked、资产及用户档保留。唯一旧二进制见[恢复映射](G1GameplayBaselineAdoption20261011/RECOVERY_MAP_20261011.json)，缓存有小型元数据备份、需要重新编译。上一正式52普通包保留一份支持既有恢复引用，不再保留七份过渡试玩。运行中full_v8／full_v16作者目录未动。

正式选择只在本机完成。本轮未commit／push或SFTP同步，原课程包／视频／外机记录仍属于更早的audioV2发布，不能视为最新76交付。早前状态属于有日期的历史，以JSON选择器为准。
'''
    for name in ['CURRENT_DEVELOPMENT_BASELINE.md','CURRENT_DEVELOPMENT_BASELINE_ZH.md']:
        p=ROOT/'Docs/Development'/name
        write(OUT/(name+'.previous.json'), dict(text=p.read_text('utf-8-sig')))
        p.write_text(text, 'utf-8')
    for name in ['CURRENT_EQUIPMENT_INPUT_REVIEW','CURRENT_UI_REVIEW']:
        p=ROOT/'Docs/Development'/(name+'.json')
        review=read(p)
        review.update(historical_status=review['status'], status='manually_reviewed_selected_active_baseline',
            selection='Formal complete-gameplay local baseline', manual_review='logic_passed_with_residual_sleeve_occlusion',
            human_manual_review=baseline['human_manual_review'],
            human_review_at=at, human_review_authorization=auth,
            remaining_visual_issue='User reports minor clothing/sleeve occlusion',
            publication='Local adopted; no new Git/SFTP/video/course publication', current_baseline='Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json', retired_playable_recovery_map=baseline['retirement_map'])
        write(p,review)
        prepend(p.with_suffix('.md'),'## 2026-10-11：人工逻辑通过并采用正式76版\n\n用户确认逻辑无问题，仍有衣袖遮挡待修。已正式采用本文件的Game／源码身份；当前入口／本机清理见[正式基线](CURRENT_DEVELOPMENT_BASELINE.md)。以下原始阶段记录保留为历史；不再视为人工待审。\n\n')
    for name in ['CURRENT_EQUIPMENT_REVIEW','CURRENT_GRENADE_MODEL_REVIEW','CURRENT_PLAYER_DEATH_REVIEW','CURRENT_CHECKPOINT_REVIEW']:
        p=ROOT/'Docs/Development'/(name+'.json')
        review=read(p)
        review.update(historical_status=review['status'],status='historical_parent_integrated_into_selected76',
            integrated_into=baseline['baseline_id'],current_baseline='Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json',
            retired_playable_recovery_map=baseline['retirement_map'])
        write(p,review)
        old_package_note='上一正式52普通包仅作为既有恢复依赖保留。' if name=='CURRENT_CHECKPOINT_REVIEW' else '旧普通试玩已退休。'
        prepend(p.with_suffix('.md'),'## 2026-10-11：历史父版已合入正式76版\n\n此专项功能承接到人工认可的当前完整玩法版。'+old_package_note+'源码和检测收据保留。运行／开发以[正式基线](CURRENT_DEVELOPMENT_BASELINE.md)为准；不要把以下旧包当当前入口。\n\n')
    launcher='@echo off\r\ncd /d "%~dp0"\r\nif not exist "'+r['playable_entry'].replace('/','\\')+'" (\r\n  echo Read Docs\\Development\\CURRENT_DEVELOPMENT_BASELINE.md\r\n  pause\r\n  exit /b 1\r\n)\r\ncall "'+r['playable_entry'].replace('/','\\')+'"\r\n'
    (ROOT/'PLAY_CURRENT_G1.cmd').write_bytes(launcher.encode('utf-8'))
    (ROOT/r['source_snapshot']).parent.joinpath('README.md').write_text('# Reviewed formal complete-gameplay76 baseline\n\n11October2026: user manually verifies logic and adopts this exact source. Minor sleeve occlusion remains backlog. SOURCE_MANIFEST and Project bytes unchanged. Read CURRENT_DEVELOPMENT_BASELINE and G1_GAMEPLAY_BASELINE_ADOPTION_RESULT_20261011_ZH. Authoring candidate_grenade_equip_v1/Project contains final build_v4. Original models/rifle finger constants/gun and enemy-clear checkpoint validation remain. Current normal launcher stays in tmp. Old generated outputs use the new recovery map; historical source/raw and native assets remain. Local adoption does not publish a new SFTP/Git/course release or prove matching Editor/second-machine acceptance.\n','utf-8')
    paragraph='- Latest manual complete-gameplay adoption/local retirement,11October2026: user manually verifies grenade-equip finalv4 logic, reports residual clothing/sleeve occlusion, selects it as formal baseline and authorizes old transitional local versions deleted. Read CURRENT_DEVELOPMENT_BASELINE and G1_GAMEPLAY_BASELINE_ADOPTION implementation/result plus the exact retirement/recovery map. Formal source76 Unreal/Variants/G1GrenadeEquip20261011/Project, Game '+GAME+'; authoring candidate_grenade_equip_v1/Project contains final build_v4. Stable PLAY_CURRENT_G1.cmd points to unchanged tmp/Playtest-G1-GrenadeEquip-20261011/PLAY_GRENADE_EQUIP.cmd, UserDir G1GrenadeEquip20261011/prefixParisGrenadeEquipV2 retained. Original models/rifle finger constants/gun/save/native1754 and user files exact. Enemy elimination alone unlocks circle/E checkpoint; actual original validation retained. Sleeve issue remains backlog, not full visual/contact/motion/large-NPC/Editor/second-machine/course acceptance. Seven obsolete normal trials and frozen old Runtime/Archive/Binaries/caches retired with exact binary recovery and small cache metadata; keep all source/raw/failure/cooked inputs/current authoring/current final receipt, both running full_v8/full_v16 Editor projects and one old formal52 normal package for recovery dependencies. Existing Editors stay open; no process terminated. This supersedes dated pending-review/formal52/keep-generated-output claims ONLY for this selected revision and exact inventory. No Git/SFTP/video/course publication in this adoption task.\n\n'
    ag=ROOT/'AGENTS.md';old=ag.read_bytes();idx=old.index(b'\n')+1;ag.write_bytes(old[:idx]+b'\n'+paragraph.encode('utf-8')+old[idx:])
    prepend(ROOT/'HANDOFF.md','## 2026-10-11：完整玩法正式采用及本机清理（最新）\n\n'+paragraph[2:]+'\n')
    prepend(ROOT/'README.md','**Current formal local gameplay baseline,11October2026:** user manually accepted logic of the complete76 grenade-equip build; minor sleeve occlusion remains. Use [current baseline](Docs/Development/CURRENT_DEVELOPMENT_BASELINE.md) and existing `PLAY_CURRENT_G1.cmd`. Seven transitional trials/caches retired per [result](Docs/Development/G1_GAMEPLAY_BASELINE_ADOPTION_RESULT_20261011_ZH.md), with original assets/source/user saves/raw and exact unique binary recovery retained. This local selection has no new Git/SFTP publication; older course/video links below still refer to the published audioV2.\n\n')
    for name in ['TEAM_CURRENT_BUILD_20261009.md','TEAM_CURRENT_BUILD_20261009_ZH.md']:
        prepend(ROOT/'Docs/Development'/name,'## 11October2026 current local gameplay revision\n\nThe latest formal local revision is manually accepted76 `G1GrenadeEquip20261011`; read [current baseline](CURRENT_DEVELOPMENT_BASELINE.md). Minor sleeve occlusion remains. No new package sync happened in adoption; the SFTP course release below remains the earlier audioV2, not this76 source.\n\n')
    prepend(ROOT/'Failures/README.md','11October manual complete-gameplay adoption: reviewed76 grenade-equip is now formal, with residual sleeve occlusion explicitly retained. Old normal/runtime/binary/cache outputs retired through the [result](../Docs/Development/G1_GAMEPLAY_BASELINE_ADOPTION_RESULT_20261011_ZH.md) and [exact recovery map](../Docs/Development/G1GameplayBaselineAdoption20261011/RECOVERY_MAP_20261011.json). Source/raw/results/images retained; older per-case demands to preserve loose Game directories now resolve through this map, not deletion of failure evidence.\n\n')
    invp=ROOT/'Assets/Registry/assets/inventory.json';inv=read(invp)
    docs=['Docs/Development/G1_GAMEPLAY_BASELINE_ADOPTION_20261011_ZH.md','Docs/Development/G1_GAMEPLAY_BASELINE_ADOPTION_RESULT_20261011_ZH.md']
    for a in inv['assets']:
        if a['id'] in {'frag-grenade','smoke-grenade','anim-rifle-animset-pro','pressure-mine','smoke-effect','ammo-box'}:
            a['documents']=list(dict.fromkeys(a.get('documents',[])+docs))
    write(invp,inv)
    indexp=ROOT/'Assets/ASSET_INDEX.md'
    index=indexp.read_text('utf-8-sig').replace('[当前输入候选]','[当前输入／正式采用记录]').replace('[统一候选]','[当前统一版]')
    indexp.write_text(index,'utf-8')
    freed=retirement['free_after_bytes']-plan['free_before_prepare_bytes']
    result=dict(status='manually_reviewed76_adopted_local_retirement_verified',finished=at,game_sha256=GAME,source_files=76,source_manifest_sha256=MANIFEST,normal_files=100,checks=15,
        user_logic_accepted=True,remaining_visual_issue='Minor clothing/sleeve occlusion',targets_removed=len(plan['targets']),obsolete_playables_removed=7,
        logical_removed_bytes=authority['logical_removed_bytes'],recovery_bytes=mapping['recovery_zip']['size_bytes'],actual_net_free_increase_bytes=freed,
        native_files=1754,protected_files=len(plan['protected']),user_files_unchanged=len(plan['user_files']),cache_metadata_files=len(plan['metadata']),live_editor_logs_preserved=len(plan.get('live_editor_logs',[])),engines=engines(),
        game_and_source_bytes_unchanged=True,no_user_process_terminated=True,no_git_or_remote_publication=True,previous_formal52_retained_for_recovery=True)
    write(PROOF/'RESULT_20261011.json',result)
    result_text=f'''# 完整玩法正式基线采用与本机清理结果

2026-10-11。用户人工确认逻辑无问题，最新手持装备finalv4正式采用。衣服／衣袖遮挡小问题保留为后续修复；本次没有改源码／Game或重跑引擎验收。

正式源精确76文件 `{r['source_snapshot']}`，Game `{GAME}`，manifest `{MANIFEST}`。已有稳定入口 `PLAY_CURRENT_G1.cmd` 指向不移动的 `{r['playable_entry']}`。最新用户存档保持原目录／前缀。15项最终Game已有检查身份核对通过，原生1754、模型／原枪械手指参数／枪械／存档及原用户文件保持。

删除七个旧普通试玩及旧Runtime／Archive／Binaries／闲置编译缓存，共{len(plan['targets'])}个冻结目录，逻辑量{authority['logical_removed_bytes']/2**30:.2f}GiB。扣除私有去重恢复ZIP（{mapping['recovery_zip']['size_bytes']/2**30:.2f}GiB）及元数据备份后，D盘实测净增加{freed/2**30:.2f}GiB；hardlink及同期其他写入会使实际数与逻辑数不同。{len(plan['metadata'])}份小型构建元数据保留，PCH／obj重新构建。完整退休清单SHA `{authority['inventory_sha256']}`，恢复映射SHA `{authority['recovery_map_sha256']}`。

保留全部源／compiled-source-game、失败原收据／日志／图、Saved/Cooked、原资产／动作／模型／贴图／音频、全部用户档、已有恢复ZIP、最新作者工程及final build_v4。运行中full_v8／full_v16工程不动，两个Editor保持开启。上一正式enemy-clear52普通包只保留一份供已有恢复依赖使用，其源码／记录保持。所有目标已移除，{len(plan['protected'])}项保留文件及最新用户文件逐项核对，唯一恢复对象回读通过。

实时Editor日志追加曾使初次回读停止，未删除目录；初始清单原样保留。仅两份已识别的活动日志使用完整快照与原冻结前缀SHA核验，允许引擎继续追加，不把活动日志全文件误称固定。其他保护文件、退休清单和恢复字节未放宽。

用户日志里的既有UVChannelData报告仍是handled Ensure（IsEnsure=true），最新手动会话日志正常退出；原文件保留，不称为新增崩溃或零警告通过。衣袖、精细全程接触／运动、大量NPC压力、匹配Editor和第二机仍是后续工作。人工逻辑通过不等于这些全部通过。

见[实施](G1_GAMEPLAY_BASELINE_ADOPTION_20261011_ZH.md)、[正式选择器](CURRENT_DEVELOPMENT_BASELINE.json)、[退休／恢复映射](G1GameplayBaselineAdoption20261011/RECOVERY_MAP_20261011.json)。本机采用没有Git提交／推送、SFTP清理／同步、课程PDF／视频改动；旧公开／课程交付属于旧audioV2发布身份。
'''
    (ROOT/'Docs/Development/G1_GAMEPLAY_BASELINE_ADOPTION_RESULT_20261011_ZH.md').write_text(result_text,'utf-8')
    print('ADOPTED formal76; released net GiB',round(freed/2**30,2))

if __name__=='__main__':
    main()
