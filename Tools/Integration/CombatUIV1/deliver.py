"""Close verified local UI evidence and create one normal, unselected trial."""
from pathlib import Path
import sys, shutil, os
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT, read, write, rows, sha, INNER
revision='candidate_ui_v5'; epoch='v5'; base=ROOT/'tmp/g1-combat-ui-20261011'
runtime=read(OUT/revision/'runtime.json'); game=runtime['game_sha256']
checks=[]
for mode in ['pause','equipment_pause','pages','confirm','pages_small']:
    p=base/'checks'/('ui_'+mode+'_'+epoch)
    result=read(p/'RESULT.json'); launch=read(p/'launch.json')
    assert result['status'].startswith('pass') and launch['exit_code']==0 and launch['game_sha256']==game,(mode,result)
    checks.append(dict(mode='ui_'+mode,result=(p/'RESULT.json').relative_to(ROOT).as_posix(),result_sha256=sha(p/'RESULT.json'),game_sha256=game,scope='actual final Game'))
for mode in ['menu','enemy_clear','p1','throw','smoke','interactions','mine_range','mine_post_clear','mine_post_clear_frag','save_equipment','restore_equipment','restore_legacy','restore_v16_equipment','performance']:
    p=OUT/'checks'/(mode+'_ui_'+epoch)
    result=read(p/'RESULT.json'); launch=read(p/'launch.json')
    assert result['status'].startswith('pass') and launch['exit_code']==0 and launch['game_sha256']==game,(mode,result)
    checks.append(dict(mode=mode,result=(p/'RESULT.json').relative_to(ROOT).as_posix(),result_sha256=sha(p/'RESULT.json'),game_sha256=game,scope='actual final Game; original opt-in fixture scope retained'))
assert read(OUT/revision/'ui-protection.json')['status']=='pass'
assert read(base/'VISUAL_REVIEW.json')['status']=='pass' and read(base/'VISUAL_REVIEW.json')['game_sha256']==game
compiled=OUT/revision/'compiled-source-game'; project=OUT/revision/'Project'
source_rows=rows(compiled)
assert len(source_rows)==67 and all(sha(project/r['path'])==r['sha256'] for r in source_rows)
# Only the actual Ready Begin input in the opt-in probe changed from v4.
v2=OUT/'candidate_ui_v4/compiled-source-game'
changed=[]
for row in rows(v2):
    old=(v2/row['path']).read_bytes().replace(b'\r\n',b'\n')
    new=(compiled/row['path']).read_bytes().replace(b'\r\n',b'\n')
    if old!=new:changed.append(row['path'])
assert changed==['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisCombatUIProbe.cpp'],changed
source=ROOT/'Unreal/Variants/G1CombatUI20261011/Project'; assert not source.exists()
shutil.copytree(compiled,source)
write(source.parent/'SOURCE_MANIFEST.json',dict(status='unselected_local_UI_review_candidate',revision=revision,files=source_rows))
normal=ROOT/'tmp/Playtest-G1-CombatUI-20261011'; assert not normal.exists(); normal.mkdir()
stage=Path(runtime['path'])/'Windows'
for p in stage.rglob('*'):
    if not p.is_file():continue
    dst=normal/'Windows'/p.relative_to(stage);dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
launcher=(ROOT/'tmp/Playtest-G1-PressureMine-20261011/PLAY_TACTICAL_EQUIPMENT.cmd').read_bytes().replace(b'G1PressureMine20261011',b'G1CombatUI20261011').replace(b'ParisPressureMineV1',b'ParisCombatUIV1')
assert not any(x in launcher for x in [b'Probe',b'EquipmentCheck',b'Observer',b'Out=',b'Solo',b'Background'])
(normal/'PLAY_COMBAT_UI.cmd').write_bytes(launcher)
(normal/'README_ZH.md').write_text('''# UI与战术装备统一试玩候选

运行PLAY_COMBAT_UI.cmd，Enter开始。等待人工复验，未选定为正式基线。

- Esc：打开作战暂停菜单；Tab：直接查看人物与小队，再按返回。
- 任务、人物与小队、五类操作帮助、设置可鼠标点击。左右键切页，上下键选择左侧操作，Enter确认。
- 读档、重开、退出有二次确认，默认取消；F9/F6使用同样确认。无有效存档时读取禁用。
- 完整菜单真正暂停角色、AI、已释放手雷引信和烟幕寿命，返回后按原剩余状态继续。
- 投掷准备、拆雷和保存窗口中Esc优先取消当前交互，本次不同时开菜单。
- HUD保留原血量/弹药/小地图，新增G/Q装备数量和按键、姿态及Esc/Tab入口。首次相关交互显示简短引导。
- 设置可切详细/简洁提示与HUD大小，本次会话生效，不改存档。
- G/Q按住准备松开投掷；近处瞄准地雷hold E两秒拆除；补给箱E领取有限备用弹药。
- 三个G1登记德军全灭即完成；圈内E保留原保存进度和成功窗口。危险仍存在，地雷/手雷会伤及玩家和盟军。

独立用户目录：%LOCALAPPDATA%/ParisStreetCombat/G1CombatUI20261011，prefix ParisCombatUIV1。旧用户档不迁移、不覆盖。正常入口无自动输入、探针或AI暂停。
人物/手指/枪械与原存档事务保留；功能检查为本机独立夹具，不代替人工自然交战、完整动作、大量NPC或第二机复验。现有UE Editor继续开启。
''',encoding='utf-8')
assert sha(normal/INNER)==game
obj=dict(status='unselected_UI_and_equipment_unified_playtest_candidate',revision=revision,game_sha256=game,source_snapshot=source.relative_to(ROOT).as_posix(),source_manifest=(source.parent/'SOURCE_MANIFEST.json').relative_to(ROOT).as_posix(),source_manifest_sha256=sha(source.parent/'SOURCE_MANIFEST.json'),source_files=len(source_rows),active_authoring_project=project.relative_to(ROOT).as_posix(),playable_directory=normal.relative_to(ROOT).as_posix(),playable_entry='PLAY_COMBAT_UI.cmd',legacy_equipment_entry='PLAY_TACTICAL_EQUIPMENT.cmd',user_dir='G1CombatUI20261011',save_prefix='ParisCombatUIV1',parent_review='Docs/Development/CURRENT_EQUIPMENT_REVIEW.json',implementation='Docs/Development/MissionLoopV1/COMBAT_UI_IMPLEMENTATION_20261011_ZH.md',result='Docs/Development/MissionLoopV1/COMBAT_UI_RESULT_20261011_ZH.md',checks=checks,normal_files=rows(normal),protection=(OUT/revision/'ui-protection.json').relative_to(ROOT).as_posix(),visual_review=(base/'VISUAL_REVIEW.json').relative_to(ROOT).as_posix(),stopped_candidates=['candidate_ui_v1: UE API compile errors / MI032','candidate_ui_v2: UI runtime checks pass, screenshot labels mismatch / MI033; retained','candidate_ui_v3: stale save guide / MI034 and invalid restore alias fixture / MI035; retained','candidate_ui_v4: Ready Enter selects Exit, no RESULT / MI036; retained'],editors='Existing owned Editors retained; no UI Editor/PIE/cook acceptance claimed',manual_review='pending',publication='none')
write(base/'DELIVERY_20261011.json',obj)
review=dict(obj);review.pop('normal_files');write(ROOT/'Docs/Development/CURRENT_UI_REVIEW.json',review)
wrapper=b'@echo off\r\ncall "%~dp0tmp\\Playtest-G1-CombatUI-20261011\\PLAY_COMBAT_UI.cmd"\r\n'
(ROOT/'PLAY_COMBAT_UI.cmd').write_bytes(wrapper)
(ROOT/'PLAY_TACTICAL_EQUIPMENT.cmd').write_bytes(wrapper)
print(normal/'PLAY_COMBAT_UI.cmd')
