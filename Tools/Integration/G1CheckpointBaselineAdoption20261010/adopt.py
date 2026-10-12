"""Record the human-approved local baseline after exact retirement verification."""
from manage import ROOT, OUT, PROOF, AUTHOR, CURRENT, GAME, MANIFEST, INNER, now, read, write, selected_checks, proof


def prepend(path, text):
    previous = path.read_bytes()
    assert text.splitlines()[0] not in previous.decode('utf-8-sig'), 'Preserve existing adoption identity'
    # Preserve historical bytes/line endings, especially Failures/** -text.
    prefix = text.encode('utf-8')
    if previous.startswith(b'\xef\xbb\xbf'):
        path.write_bytes(b'\xef\xbb\xbf' + prefix + previous[3:])
    else:
        path.write_bytes(prefix + previous)


def main():
    review = selected_checks()
    authority, plan, mapping = proof()
    retirement = read(OUT / 'local-retirement.json')
    assert retirement['targets'] == len(plan['targets'])
    assert all(not (ROOT / t['path']).exists() for t in plan['targets'])
    prior = read(OUT / 'previous_baseline.json')
    selected_at = now()
    auth = 'User: 已测试，没有问题，把这一版合并到正式基线中，其他过渡版本删除，过时正式版本不保留太多'
    baseline = dict(prior)
    baseline.update(schema_version=3, status='selected_active_development_baseline', authorization=auth,
        selected_at=selected_at, baseline_id=review['review_id'], playable_directory=CURRENT,
        playable_entry=CURRENT + '/PLAY_G1_REVISION.cmd', stable_local_entry='PLAY_CURRENT_G1.cmd', game_sha256=GAME,
        source_snapshot=review['source_snapshot'], source_manifest=review['source_manifest'], source_manifest_sha256=MANIFEST,
        active_authoring_project=AUTHOR + '/WW2FranceLiberation.uproject', active_source_files=52,
        save_prefix=review['save_prefix'], save_directory=review['save_directory'],
        human_manual_review='Passed by explicit user retest; adopted locally10October2026',
        human_review_scope='User reports no problems with latest trial; no new quantified FPS/contact or external-machine evidence supplied',
        checkpoint_rule=review['rule'], speed_preset_m_s=dict(walk=2.2, run=4.5, slow=0.65), fresh_ammo=dict(loaded=8,reserve=10,total=18),
        verified_runs=review['verified_runs'], sftp_release=None, sftp_download=None,
        publication_status='Local baseline adopted; no new Git/SFTP publication in this task',
        matching_source_revision='Current local52 snapshot; uncommitted repair/adoption changes retained',
        retirement_map='Docs/Development/G1CheckpointBaselineAdoption20261010/RECOVERY_MAP_20261010.json',
        previous_selected_baseline=dict(role='Historical audioV2 source/review/publication and earlier anchors; local runnable retired',selector=prior),
        delivery_revision_scope=dict(game_sha256=prior['game_sha256'], source_files=42,
            note='Existing SFTP course download, approved demo and second-machine attestation belong to the earlier audioV2 revision, not the new52-file baseline'),
        remaining_gates=['Remaining sleeve/ADS/en-bloc asset polish', 'HUD refinement', 'Richer gameplay and added NPC behavior/stress',
            'Exact reusable German live-fire source', 'Editor build/recook and second-machine validation of this52-file revision',
            'Private course delivery, independent reviewer download and course acceptance'],
        future_rule='Start from the exact52 snapshot or matching active authoring Project. Preserve models/fingers/actions/gun/resources/audio/native navigation and original validated journal. Enemy-clear-only objective gate. Build matching Editor before Editor entry. Historical package paths recover through the current retirement map.')
    write(ROOT / 'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json', baseline)
    review.update(status='manually_reviewed_selected_active_baseline', selection='Formal current local development baseline',
        human_review_at=selected_at, human_review_authorization=auth,
        publication='Local baseline adoption and exact local retirement complete; no new Git/SFTP/video/PDF changes',
        retirement_map=baseline['retirement_map'])
    write(ROOT / 'Docs/Development/CURRENT_CHECKPOINT_REVIEW.json', review)
    for name in ['CURRENT_INTERACTION_REVIEW', 'CURRENT_TEAM_FEEDBACK_P1_REVIEW', 'CURRENT_TEAM_FEEDBACK_REVIEW']:
        path = ROOT / 'Docs/Development' / (name + '.json')
        old = read(path)
        old['historical_status'] = old['status']
        old.update(status='superseded_local_runnable_retired', selection='Historical parent; use CURRENT_DEVELOPMENT_BASELINE.json',
            superseded_by=review['review_id'], retirement_map=baseline['retirement_map'])
        write(path, old)
        prepend(path.with_suffix('.md'), '## 2026-10-10：已被正式清场基线取代\n\n本文件以下为历史记录；普通试玩目录已退休，源与测试收据保留。\n当前入口和52文件基线见 [CURRENT_DEVELOPMENT_BASELINE](CURRENT_DEVELOPMENT_BASELINE.md)，\n旧字节见本轮恢复清单。\n\n')
    current_text = '''# 当前正式开发基线

2026-10-10，用户人工复验最新清场 checkpoint v3 无问题，明确选为正式基线。
唯一当前普通试玩为 `'''+CURRENT+'''/PLAY_G1_REVISION.cmd`；项目根目录
`PLAY_CURRENT_G1.cmd` 指向同一入口。用户存档继续使用 `'''+review['save_directory']+'''`。

当前源：`'''+review['source_snapshot']+'''`，精确52文件；制作工程：
`'''+AUTHOR+'''/WW2FranceLiberation.uproject`。Game SHA256 `'''+GAME+'''`；
manifest SHA256 `'''+MANIFEST+'''`。进入 Editor 前重新构建匹配 Editor，不能使用旧缓存。

本基线累计保留菜单选择、步行2.2/跑步4.5米每秒、8+10弹药、已接受德军角落布局、
雷达/HUD和audioV2；登记三名敌军全灭即完成并解锁存档圈，不再要求远岸点/小队/姿态/停步。
圈内主动E，实际写盘及回读通过后显示成功窗口，确认后同次进圈不再提示或重复写。
模型、手指姿态、原动作、枪械/资源、导航/AI、V5存档校验和死亡终态保护。

既有有限原生菜单37、清场26、独立恢复31、旧V5恢复31项通过，最新人工复验通过。
隔离清场诊断不是新增自然战斗/导航压测；本次选择没有新增引擎测试。
衣袖/ADS/弹夹动作、HUD精细化、玩法与大量NPC逻辑/压测等后续工作保留。

旧试玩和编译缓存已按 [实施](G1_CHECKPOINT_BASELINE_ADOPTION_20261010_ZH.md)
及 [结果](G1_CHECKPOINT_BASELINE_ADOPTION_RESULT_20261010_ZH.md) 清理。
旧源、日志、失败、图片、用户存档和必要恢复锚点保留；
[恢复映射](G1CheckpointBaselineAdoption20261010/RECOVERY_MAP_20261010.json) 支持旧路径。
JSON选择器为当前身份依据，早前日期的源/选定版本说明属于历史。

本次只合并本机正式基线。现有SFTP课程下载、已批准视频和旧版本第二机记录仍对应audioV2；
不冒称已同步最新52文件，没有自动commit/push、远端清理、课程PDF或视频修改。
'''
    for name in ['CURRENT_DEVELOPMENT_BASELINE.md', 'CURRENT_DEVELOPMENT_BASELINE_ZH.md']:
        path = ROOT / 'Docs/Development' / name
        write(OUT / (name + '.previous.json'), dict(text=path.read_text('utf-8-sig')))
        path.write_text(current_text, 'utf-8')
    (ROOT / 'Docs/Development/CURRENT_CHECKPOINT_REVIEW.md').write_text(current_text.replace('# 当前正式开发基线', '# 已人工通过的清场 checkpoint 正式基线'), 'utf-8')
    (ROOT / 'PLAY_CURRENT_G1.cmd').write_text('@echo off\ncd /d "%~dp0"\nif not exist "'+CURRENT.replace('/', '\\')+'\\PLAY_G1_REVISION.cmd" (\n  echo Current local playable is missing. Read Docs\\Development\\CURRENT_DEVELOPMENT_BASELINE.md\n  pause\n  exit /b 1\n)\ncall "'+CURRENT.replace('/', '\\')+'\\PLAY_G1_REVISION.cmd"\n', 'utf-8')
    (ROOT / CURRENT / 'CURRENT_BASELINE.md').write_text('Manually reviewed and selected formal local baseline10October2026.\nUse PLAY_G1_REVISION.cmd; all registered Germans eliminated unlocks G1/checkpoint.\nThe inherited dated candidate notes are historical. Models/fingers/weapon/save checks retained.\nSee Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json for exact52-source identity.\n', 'utf-8')
    variant = ROOT / review['source_snapshot']
    (variant.parent / 'README.md').write_text('# Reviewed formal G1 enemy-clear baseline\n\n10October2026: user manual retest passed and selected this exact52-file source.\nRead CURRENT_DEVELOPMENT_BASELINE and G1_CHECKPOINT_BASELINE_ADOPTION_RESULT_20261010_ZH.\nSOURCE_MANIFEST pins unmodified Project bytes. Licensed native Content/audio remain private.\nUse the matching active authoring wrapper; Game-only build does not establish matching Editor.\nRegistered enemy elimination is the only objective/save gate; preserve circle/explicit confirmation\nand original schema/resources/checksum/write/readback. Models, fingers and weapon logic retained.\nOld runnable packages/caches retired; historical sources, receipts and compact recovery remain.\nNo new SFTP package or Git publication is implied by this local selection.\n', 'utf-8')
    prefix = '''## 2026-10-10：人工通过并合入正式基线（最新）

用户已测试最新 enemy-clear v3，无问题，明确选为后续正式基线并授权清理本机过渡版本。
以 `Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json` 的52文件/Game身份为准；
根目录 `PLAY_CURRENT_G1.cmd` 启动同一正常入口，用户存档未迁移。
旧试玩/旧编译缓存已按精确清单清理；历史源/原记录和去重恢复包保留。
见 G1_CHECKPOINT_BASELINE_ADOPTION_20261010_ZH 及其 RESULT、恢复映射。
下面旧条目的“人工待复验/audioV2仍正式/保留旧包”等状态均为有日期的历史，
仅在本轮精确退休范围内被新授权取代。模型/手指/枪械、原生资产和用户存档保护。
本机正式选择未自动发布；既有课程SFTP/视频仍是旧audioV2，没有新Editor/性能/第二机验收。

'''
    prepend(ROOT / 'HANDOFF.md', prefix)
    ag = ROOT / 'AGENTS.md'
    text = ag.read_text('utf-8-sig')
    marker = '## Authority and scope\n'
    assert marker in text
    paragraph = '\n- Latest manual formal-baseline adoption/local retirement,10October2026: user manually retests enemy-clear v3 with no issues and explicitly selects it for continued development, permits superseded local transitional/obsolete formal versions to be deleted. Read CURRENT_DEVELOPMENT_BASELINE.json/md and G1_CHECKPOINT_BASELINE_ADOPTION_20261010_ZH/RESULT plus its exact retirement/recovery manifests. Current exact52 source is Unreal/Variants/G1EnemyClearCheckpoint20261010/Project; authoring tmp/g1-enemy-clear-checkpoint-20261010/candidate_v3/Project, Game b40409b08830cc0e1d306ceab0575d7e61db382f50853426bbda58d08f385079. PLAY_CURRENT_G1.cmd points to the unchanged normal trial/UserDir. Enemy elimination alone unlocks objectives/checkpoints; preserve explicit circle confirmation and durable original journal validation. This supersedes older pending-manual/audioV2-selected/keep-generated-package instructions only for the frozen local inventory. Keep sources/failures/receipts/images/user saves/native models/fingers/gun/audio/cooked inputs, current authoring and compact recovery including legacy V13. Older authoring wrappers retain source but removed caches must be rebuilt; old audio recovery references resolve through the new mapping. No automatic Git/SFTP/video/PDF publication or Editor entry; existing course download/video/second-machine evidence belong to prior audioV2, not the new52 revision.\n'
    ag.write_text(text.replace(marker, marker + paragraph, 1), 'utf-8')
    prepend(ROOT / 'README.md', '**Current local formal baseline,10October2026:** the user manually retested enemy-clear v3 and selected its exact52-file source. Use [current baseline](Docs/Development/CURRENT_DEVELOPMENT_BASELINE.md) and root `PLAY_CURRENT_G1.cmd`. Superseded local playable packages/caches are retired through the [adoption/cleanup record](Docs/Development/G1_CHECKPOINT_BASELINE_ADOPTION_RESULT_20261010_ZH.md); original models/fingers/weapon logic and user saves remain. Existing SFTP course download and video below still correspond to prior audioV2; this local selection has not published a new package. Older dated status entries are historical.\n\n')
    for name in ['TEAM_CURRENT_BUILD_20261009.md','TEAM_CURRENT_BUILD_20261009_ZH.md']:
        prepend(ROOT / 'Docs/Development' / name, '## 10October2026 current local revision\n\nThe current manually accepted local source is exact52 `Unreal/Variants/G1EnemyClearCheckpoint20261010/Project`; see [current baseline](CURRENT_DEVELOPMENT_BASELINE.md). Local entry `PLAY_CURRENT_G1.cmd`. The audioV2 SFTP download described below is the prior published/course revision and remains available; it does not contain the latest checkpoint repair. No new package sync occurred in this local adoption task.\n\n')
    prepend(ROOT / 'Failures/README.md', '10October manual checkpoint approval and local retirement: latest enemy-clear v3 is the formal52-file baseline. Superseded playable/build caches are removed under the [adoption result](../Docs/Development/G1_CHECKPOINT_BASELINE_ADOPTION_RESULT_20261010_ZH.md); source/failed identities/logs/images/journals retained, exact runnable bytes use the new compact recovery map. This supersedes older generated-output preservation claims only for the exact inventory, without changing raw failure/results.\n\n')
    freed = retirement['free_after_bytes'] - plan['free_before_prepare_bytes']
    result = dict(status='manually_reviewed_baseline_adopted_local_retirement_verified', finished=selected_at,
        game_sha256=GAME, source_manifest_sha256=MANIFEST, source_files=52, current_entry='PLAY_CURRENT_G1.cmd',
        local_targets_removed=retirement['targets'], obsolete_playables_removed=19,
        logical_removed_bytes=authority['logical_removed_bytes'], recovery_bytes=mapping['recovery_zip']['size_bytes'],
        actual_net_free_increase_bytes=freed, native_guards=1754, user_files_unchanged=len(plan['user_files']),
        no_engine_started=True,no_user_process_terminated=True,no_game_or_source_bytes_changed=True,
        no_remote_mutation=True,no_git_commit_or_push=True,existing_course_release_retained=True,
        recovery_interface_checks=read(OUT / 'recovery-interface-checks.json'))
    write(PROOF / 'RESULT_20261010.json', result)
    (ROOT / 'Docs/Development/G1_CHECKPOINT_BASELINE_ADOPTION_RESULT_20261010_ZH.md').write_text('''# 清场checkpoint正式基线合并与清理结果

2026-10-10，用户最新人工复验通过，enemy-clear v3 已正式选作开发基线。
累计菜单、速度/弹药、德军角落布局、HUD/audio和最新成功保存窗口及清场规则均承接。
模型/手指/枪械/导航/AI和原存档校验字节不变，本轮没有改Game或52文件源、重编译或新引擎运行。

正常入口：项目根目录 `PLAY_CURRENT_G1.cmd`，指向 `'''+CURRENT+'''/PLAY_G1_REVISION.cmd`。
后续制作从 exact52 `Unreal/Variants/G1EnemyClearCheckpoint20261010/Project` 或当前
`'''+AUTHOR+'''` 开始。Game `'''+GAME+'''`；manifest `'''+MANIFEST+'''`。
用户存档未移动/清空；1754原生保护文件、Catalog、当前源/Project/试玩和保留源/失败/图片/原收据核对通过。

删除19个旧普通试玩目录、旧版本派生编译缓存和本机旧audioV2完整ZIP，共'''+str(retirement['targets'])+'''个精确目标。
清单逻辑体积'''+format(authority['logical_removed_bytes']/2**30,'.2f')+'''GiB，不能当作实际释放量（旧包共享hardlink）。
唯一文件恢复包'''+format(mapping['recovery_zip']['size_bytes']/2**30,'.2f')+'''GiB；包含不同的Game/PDB/启动器/说明，
共有文件复用当前保留字节，所有恢复条目均逐项回读。扣除新恢复包后磁盘实测净增加
'''+format(freed/2**30,'.2f')+'''GiB。原样保留旧源码/用户存档/失败日志图像/检测结果、cooked输入、legacyV13和旧唯一恢复包。

恢复见 [精确清单](G1CheckpointBaselineAdoption20261010/RETIREMENT_INVENTORY_20261010.json)、
[路径映射](G1CheckpointBaselineAdoption20261010/RECOVERY_MAP_20261010.json)、
[机器结果](G1CheckpointBaselineAdoption20261010/RESULT_20261010.json)。
旧audioV2恢复工具已加入新的保留路径解析，原历史清单不改写；真实旧启动器恢复和跨代共同DLL解析通过。
Intermediate/DDC只保留尺寸/时间清单，可从原源重建，不承诺逐字恢复这些缓存。

没有终止用户进程或进入Editor，没有自动commit/push、远端清理/发布、视频/PDF修改。
课程SFTP下载、已批准视频和旧第二机记录仍指向先前audioV2；最新52文件尚未同步成新的远端试玩包。
旧小队通行测试属于历史路径证据，当前存档任务门槛只要求登记敌军全灭。
后续Editor须构建匹配版本；人工通过不扩大为新的性能/大规模NPC/第二机/课程验收。
''', 'utf-8')
    print(result)


if __name__ == '__main__':
    main()
