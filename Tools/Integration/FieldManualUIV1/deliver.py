"""Close actual field-manual evidence and deliver an independent normal trial."""
from pathlib import Path
import sys,argparse,shutil,os
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,rows,sha,INNER
ap=argparse.ArgumentParser();ap.add_argument('--revision',default='candidate_field_manual_v2');ap.add_argument('--epoch',default='field_v2');a=ap.parse_args()
base=ROOT/'tmp/g1-field-manual-ui-20261011';runtime=read(OUT/a.revision/'runtime.json');game=runtime['game_sha256']
checks=[]
for mode in ['pause','equipment_pause','pages','confirm','pages_small']:
    p=ROOT/'tmp/g1-combat-ui-20261011/checks'/('ui_'+mode+'_'+a.epoch)
    result=read(p/'RESULT.json');launch=read(p/'launch.json')
    assert result['status'].startswith('pass') and launch['exit_code']==0 and launch['game_sha256']==game,(mode,result)
    checks.append(dict(mode='ui_'+mode,result=(p/'RESULT.json').relative_to(ROOT).as_posix(),result_sha256=sha(p/'RESULT.json'),game_sha256=game,status=result['status'],scope='actual final Game; normal input/pause/frames'))
for mode in ['menu','enemy_clear','p1','throw','smoke','interactions','mine_range','mine_post_clear','mine_post_clear_frag','save_equipment','restore_equipment','restore_legacy','restore_v16_equipment','performance']:
    p=OUT/'checks'/(mode+'_ui_'+a.epoch);result=read(p/'RESULT.json');launch=read(p/'launch.json')
    assert result['status'].startswith('pass') and launch['exit_code']==0 and launch['game_sha256']==game,(mode,result)
    checks.append(dict(mode=mode,result=(p/'RESULT.json').relative_to(ROOT).as_posix(),result_sha256=sha(p/'RESULT.json'),game_sha256=game,status=result['status'],scope='actual final Game; original opt-in fixture scope'))
assert read(OUT/a.revision/'field-protection.json')['status']=='pass'
visual=read(base/'VISUAL_REVIEW.json');assert visual['status']=='pass' and visual['game_sha256']==game
compiled=OUT/a.revision/'compiled-source-game';project=OUT/a.revision/'Project';files=rows(compiled)
assert len(files)==69 and all(sha(project/r['path'])==r['sha256'] for r in files)
source=ROOT/'Unreal/Variants/G1FieldManualUI20261011/Project';assert not source.exists();shutil.copytree(compiled,source)
write(source.parent/'SOURCE_MANIFEST.json',dict(status='unselected_local_field_manual_UI_candidate',revision=a.revision,files=files))
normal=ROOT/'tmp/Playtest-G1-FieldManualUI-20261011';assert not normal.exists();normal.mkdir()
stage=Path(runtime['path'])/'Windows'
for p in stage.rglob('*'):
    if not p.is_file():continue
    dst=normal/'Windows'/p.relative_to(stage);dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
launcher=(ROOT/'tmp/Playtest-G1-CombatUI-20261011/PLAY_COMBAT_UI.cmd').read_bytes().replace(b'G1CombatUI20261011',b'G1FieldManualUI20261011').replace(b'ParisCombatUIV1',b'ParisFieldManualUIV1')
assert not any(x in launcher for x in [b'Probe',b'EquipmentCheck',b'Observer',b'Out=',b'Solo',b'Background'])
(normal/'PLAY_COMBAT_UI.cmd').write_bytes(launcher)
(normal/'README_ZH.md').write_text('''# 战地手册 UI 与战术装备统一试玩

运行PLAY_COMBAT_UI.cmd。原开始按钮进入任务；Esc打开新的战地手册作战菜单，Tab在战斗中直接查看人物与小队，再按返回。

任务、人物小队、帮助、设置四页已统一美术；五类帮助支持1–5选择，顶部页签与左侧操作支持鼠标、方向键和Enter。读档/重开/退出仍二次确认，默认取消；F9/F6使用相同确认。

G/Q按住准备松开投掷，近处瞄准地雷hold E两秒拆除，补给箱E领取有限备用弹药。原模型/手指/枪械/存档逻辑保留：三名G1登记守军全灭即解锁，圈内E保存、进度和成功窗口不变；成功后保存操作提示消失。

暂停冻结原角色AI、手雷引信及烟寿命，恢复不补资源。设置仅本次会话生效。正常入口无探针、自动输入、solo或AI覆盖。新独立用户目录G1FieldManualUI20261011、prefix ParisFieldManualUIV1，旧用户档不迁移/覆盖。

这是本地统一试玩候选，等待人工视觉/玩法复验；正式enemy-clear基线不变。现有UE Editors继续开启。未Git/SFTP发布或清理原版本。
''',encoding='utf-8')
assert sha(normal/INNER)==game
review=dict(status='unselected_field_manual_UI_and_equipment_unified_playtest_candidate',revision=a.revision,game_sha256=game,source_snapshot=source.relative_to(ROOT).as_posix(),source_manifest=(source.parent/'SOURCE_MANIFEST.json').relative_to(ROOT).as_posix(),source_manifest_sha256=sha(source.parent/'SOURCE_MANIFEST.json'),source_files=len(files),active_authoring_project=project.relative_to(ROOT).as_posix(),playable_directory=normal.relative_to(ROOT).as_posix(),playable_entry='PLAY_COMBAT_UI.cmd',visual_entry='PLAY_FIELD_MANUAL_UI.cmd',legacy_equipment_entry='PLAY_TACTICAL_EQUIPMENT.cmd',user_dir='G1FieldManualUI20261011',save_prefix='ParisFieldManualUIV1',parent_record='tmp/g1-field-manual-ui-20261011/freeze.json',implementation='Docs/Development/MissionLoopV1/FIELD_MANUAL_UI_IMPLEMENTATION_20261011_ZH.md',result='Docs/Development/MissionLoopV1/FIELD_MANUAL_UI_RESULT_20261011_ZH.md',checks=checks,protection=(OUT/a.revision/'field-protection.json').relative_to(ROOT).as_posix(),visual_review=(base/'VISUAL_REVIEW.json').relative_to(ROOT).as_posix(),stopped_candidates=['candidate_field_manual_v1: actual footer/settings font metrics overflow / MI037; unchanged source and raw frames retained'],editors='Existing Editors remain open; Game tests only, no new Editor/PIE/cook acceptance',manual_review='pending_actual_visual_playtest',publication='none')
write(base/'DELIVERY_20261011.json',dict(review,normal_files=rows(normal)))
write(ROOT/'Docs/Development/CURRENT_UI_REVIEW.json',review)
wrapper=b'@echo off\r\ncall "%~dp0tmp\\Playtest-G1-FieldManualUI-20261011\\PLAY_COMBAT_UI.cmd"\r\n'
for name in ['PLAY_COMBAT_UI.cmd','PLAY_FIELD_MANUAL_UI.cmd','PLAY_TACTICAL_EQUIPMENT.cmd']:(ROOT/name).write_bytes(wrapper)
print(normal/'PLAY_COMBAT_UI.cmd')
