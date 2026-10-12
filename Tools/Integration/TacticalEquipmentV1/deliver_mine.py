"""Deliver only the verified local normal candidate; do not adopt/publish it."""
from prepare import ROOT, OUT, INNER, rows, read, write, sha
import os,shutil
revision='candidate_mine_v2';project=OUT/revision/'Project';compiled=OUT/revision/'compiled-source-game'
runtime=read(OUT/revision/'runtime.json')
mine=['mine_visual','mine_contact','mine_range','mine_ally','mine_german','mine_post_clear','mine_post_clear_frag','mine_spent_save','mine_spent_restore']
fresh=['throw','smoke','interactions','sites','menu','enemy_clear','p1','save_equipment','restore_equipment','restore_legacy','restore_v16_equipment','performance','hazard','blast_occlusion']
checks=[]
for mode in mine+fresh:
    identity=mode+('_v2' if mode in mine else '_mine_v2')
    p=OUT/'checks'/identity;result=read(p/'RESULT.json');launch=read(p/'launch.json')
    assert result['status'].startswith('pass') and launch['exit_code']==0,(mode,result['status'])
    expected=runtime['game_sha256']
    assert launch['game_sha256']==expected
    checks.append(dict(mode=mode,inherited_unchanged_scope=False,result=(p/'RESULT.json').relative_to(ROOT).as_posix(),result_sha256=sha(p/'RESULT.json'),game_sha256=expected))
assert read(OUT/'checks/mine_visual_v2/VISUAL_REVIEW.json')['status']=='pass'
assert read(OUT/revision/'protection.json')['status']=='pass'
base=OUT/'candidate_mine_v1/compiled-source-game'
changes=[r['path'] for r in rows(base) if sha(compiled/r['path'])!=r['sha256']]
assert set(changes)=={'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp','Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisPressureMineChecks.inl','Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisPressureMineMesh.inl'},changes
mission='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp'
old=(base/mission).read_bytes();new=(compiled/mission).read_bytes()
before=b'if(DeathLedger.Contains(TEXT("Player"))) { SetPhase(TEXT("Lost")); Feedback=TEXT("Player lost to a remaining hazard. F9 loads a save; F6 restarts."); GateBrains(false); return; }'
after=before.replace(b'{ SetPhase',b'{ SetCheckpointDialog(TEXT("None"),FString()); CheckpointPromptVisible=false; SetPhase')
assert old.replace(before,after)==new
source=ROOT/'Unreal/Variants/G1PressureMine20261011/Project';assert not source.exists()
shutil.copytree(compiled,source)
assert all(sha(project/r['path'])==r['sha256'] for r in rows(source))
write(source.parent/'SOURCE_MANIFEST.json',dict(status='unselected_local_review_candidate',revision=revision,files=rows(source)))
normal=ROOT/'tmp/Playtest-G1-PressureMine-20261011';assert not normal.exists();normal.mkdir()
for p in (OUT/revision/'Runtime/Windows').rglob('*'):
    if not p.is_file():continue
    dst=normal/'Windows'/p.relative_to(OUT/revision/'Runtime/Windows');dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
launcher=(ROOT/'tmp/Playtest-G1-TacticalEquipment-20261010/PLAY_TACTICAL_EQUIPMENT.cmd').read_bytes().replace(b'G1TacticalEquipment20261010',b'G1PressureMine20261011').replace(b'ParisEquipmentV1',b'ParisPressureMineV1')
assert not any(s in launcher for s in [b'Probe',b'EquipmentCheck',b'Observer',b'Out=',b'Solo',b'Background'])
(normal/'PLAY_TACTICAL_EQUIPMENT.cmd').write_bytes(launcher)
(ROOT/'PLAY_TACTICAL_EQUIPMENT.cmd').write_bytes(b'@echo off\r\ncall "%~dp0tmp\\Playtest-G1-PressureMine-20261011\\PLAY_TACTICAL_EQUIPMENT.cmd"\r\n')
(normal/'README_ZH.md').write_text('''# 地雷修订统一试玩候选

运行 PLAY_TACTICAL_EQUIPMENT.cmd，Enter开始。正式基线未改；此候选等待人工复验。

- 原灰白陷阱换成军绿盘形地雷；玩家、盟军、德军落地踩中都会引爆，一次性消耗。靠近但未接触、跳跃悬空不触发。
- 实际视线发现后显示位置/距离；墙体或烟幕挡住时不显示位置提示，不能隔墙拆除。
- 两米内看到并瞄准地雷，按住E两秒拆除；松开、移动或Esc取消，成功后装置与提示消失。
- 原G手榴弹/Q烟雾弹各2颗，按住准备、松开投掷，提交前Esc取消。手榴弹和地雷会伤及玩家/小队。
- 两处弹药箱各16发，近距离瞄准E领取，空箱不再给资源；原枪械/弹药交易和动作保留。
- 三个登记德军全灭即解锁；存档圈内E优先保存，不要求拆雷。完成后危险仍存在，死亡进入Lost，可F9读档/F6重开。
- 独立目录 %LOCALAPPDATA%/ParisStreetCombat/G1PressureMine20261011；不修改/迁移旧试玩或正式用户档。

人物/手指/枪械/原声音/原双槽存档验证保留。独立实测为本机夹具和当前六角色短性能流程，不等于人工自然交战、所有动作/大量NPC/第二机验收。正常入口没有自动输入、探针或AI暂停。UE Editor保持开启。
''',encoding='utf-8')
assert sha(normal/INNER)==runtime['game_sha256']
obj=dict(status='unselected_pressure_mine_unified_playtest_candidate',revision=revision,game_sha256=runtime['game_sha256'],source_snapshot=source.relative_to(ROOT).as_posix(),source_manifest=(source.parent/'SOURCE_MANIFEST.json').relative_to(ROOT).as_posix(),source_manifest_sha256=sha(source.parent/'SOURCE_MANIFEST.json'),source_files=len(rows(source)),active_authoring_project=project.relative_to(ROOT).as_posix(),playable_directory=normal.relative_to(ROOT).as_posix(),playable_entry='PLAY_TACTICAL_EQUIPMENT.cmd',user_dir='G1PressureMine20261011',save_prefix='ParisPressureMineV1',model_review='Assets/LocalWorking/Experiments/PressureMine/20261011-v1/ASSET_REVIEW.json',normal_files=rows(normal),checks=checks,stopped_candidates=['candidate_mine_v1: dark exterior / MI030','candidate_mine_v3: invalid pre-clear Waiting fixture / MI031'],editors='Existing owned Editors retained; no mine Editor/PIE/cook acceptance claimed',manual_review='pending',publication='none')
write(OUT/'MINE_DELIVERY_20261011.json',obj)
review=dict(obj);review.pop('normal_files');write(ROOT/'Docs/Development/CURRENT_EQUIPMENT_REVIEW.json',review)
print(normal/'PLAY_TACTICAL_EQUIPMENT.cmd')
