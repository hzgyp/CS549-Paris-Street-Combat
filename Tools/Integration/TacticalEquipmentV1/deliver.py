from prepare import ROOT,OUT,INNER,read,rows,sha,write
from pathlib import Path
import argparse,os,shutil
ap=argparse.ArgumentParser();ap.add_argument('revision');ap.add_argument('--suffix',required=True);ap.add_argument('--carry-suffix');a=ap.parse_args()
required=['smoke','hazard','throw','frag_blast','interactions','sites','ally_trap','blast_occlusion','save_equipment','performance','restore_equipment','restore_legacy','menu','enemy_clear','p1']
receipts=[]
runtime=read(OUT/a.revision/'runtime.json')
rerun={'smoke','save_equipment','restore_equipment','restore_legacy','performance'}
if a.carry_suffix:
    older=OUT/'candidate_full_v15/compiled-source-game';current=OUT/a.revision/'compiled-source-game'
    previous=rows(older);now=rows(current);assert {r['path'] for r in previous}=={r['path'] for r in now}
    changed=[r['path'] for r in previous if sha(current/r['path'])!=r['sha256']]
    assert changed==['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisEquipmentSmoke.inl'],changed
    path=changed[0];assert (current/path).read_bytes().replace(b'SetScalarParameterValue(TEXT("Opacity"),3.f)',b'SetScalarParameterValue(TEXT("Opacity"),1.f)')==(older/path).read_bytes()
for mode in required:
    inherited=bool(a.carry_suffix and mode not in rerun)
    directory=OUT/'checks'/f'{mode}_{a.carry_suffix if inherited else a.suffix}'
    result=read(directory/'RESULT.json');launch=read(directory/'launch.json')
    assert result['status'].startswith('pass'),(mode,result['status'])
    expected=read(OUT/'candidate_full_v15/runtime.json')['game_sha256'] if inherited else runtime['game_sha256']
    assert launch['exit_code']==0 and launch['game_sha256']==expected,mode
    receipts.append(dict(mode=mode,inherited_unchanged_scope=inherited,result=str((directory/'RESULT.json').relative_to(ROOT)).replace('\\','/'),result_sha256=sha(directory/'RESULT.json'),game_sha256=launch['game_sha256']))
assert read(OUT/a.revision/'protection.json')['status']=='pass'
assert (OUT/'checks'/f'smoke_{a.suffix}'/'VISUAL_REVIEW.json').exists(),'Actual smoke image review required'
assert read(OUT/'checks'/f'smoke_{a.suffix}'/'VISUAL_REVIEW.json')['status']=='pass'
source=ROOT/'Unreal/Variants/G1TacticalEquipment20261010/Project';assert not source.exists()
project=OUT/a.revision/'Project'
shutil.copytree(project,source,ignore=shutil.ignore_patterns('Content','Binaries','Intermediate','Saved','DerivedDataCache','Audio','__pycache__'))
write(source.parent/'SOURCE_MANIFEST.json',dict(status='unselected_local_review_candidate',revision=a.revision,files=rows(source)))
normal=ROOT/'tmp/Playtest-G1-TacticalEquipment-20261010';assert not normal.exists();normal.mkdir()
src=Path(runtime['path'])/'Windows'
for p in src.rglob('*'):
    if not p.is_file():continue
    dst=normal/'Windows'/p.relative_to(src);dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
base=read(OUT/'freeze.json')['parent']
launcher=(ROOT/base['playable_entry']).read_bytes().replace(b'ParisG1PlaytestV5',b'ParisEquipmentV1').replace(b'G1EnemyClearv320261010',b'G1TacticalEquipment20261010')
early=b'-DPCVars="sg.ViewDistanceQuality=2,sg.AntiAliasingQuality=2,sg.ShadowQuality=2,sg.GlobalIlluminationQuality=2,sg.ReflectionQuality=2,sg.PostProcessQuality=2,sg.TextureQuality=2,sg.EffectsQuality=2,sg.FoliageQuality=2,sg.ShadingQuality=2,r.ScreenPercentage=100,r.Streaming.PoolSize=1536,r.VSync=0,t.MaxFPS=0" '
launcher=launcher.replace(b'-ExecCmds=',early+b'-ExecCmds=')
assert not any(x in launcher for x in [b'Probe',b'EquipmentCheck',b'Observer',b'Out=',b'Solo',b'Background'])
(normal/'PLAY_TACTICAL_EQUIPMENT.cmd').write_bytes(launcher)
(ROOT/'PLAY_TACTICAL_EQUIPMENT.cmd').write_bytes(b'@echo off\r\ncall "%~dp0tmp\\Playtest-G1-TacticalEquipment-20261010\\PLAY_TACTICAL_EQUIPMENT.cmd"\r\n')
(normal/'README_ZH.md').write_text('''# 战术装备统一试玩候选

启动 PLAY_TACTICAL_EQUIPMENT.cmd，菜单 Enter 开始。

- 按住 G 准备手榴弹，松开投掷；Q 为烟雾弹。开局各2枚。释放提交前 Esc 取消，不消耗。
- 手榴弹释放后3.5秒爆炸，有距离衰减与遮挡，会伤到玩家与盟军。
- 烟幕展开2秒、持续至18秒后消散，遮蔽双方视线和敌军雷达，不挡子弹和通路。
- 地面敌方陷阱可观察、绕过；近距离瞄准后按住 E 2秒拆除，移动/松开/ESC取消。触发一次即耗尽。
- 两处弹药箱各16发，近距离瞄准按 E 补充备用弹药；空箱不能重复领取。
- 原射击/换弹/移动操作保留。三个德军全灭解锁存档圈，圈内 E 保存；F9读档、F6重开。
- 独立存档目录 %LOCALAPPDATA%/ParisStreetCombat/G1TacticalEquipment20261010；不覆盖正式版用户档。

此为本机统一功能候选，等待人工试玩选定。投掷物和陷阱使用简单临时几何，弹药箱复用现有资产；未声称新增精细美术验收或大量NPC压测。
''',encoding='utf-8')
assert sha(normal/INNER)==runtime['game_sha256']
write(OUT/'DELIVERY.json',dict(status='unselected_unified_playtest_candidate',revision=a.revision,game_sha256=runtime['game_sha256'],source_snapshot=str(source.relative_to(ROOT)).replace('\\','/'),source_manifest=str((source.parent/'SOURCE_MANIFEST.json').relative_to(ROOT)).replace('\\','/'),source_manifest_sha256=sha(source.parent/'SOURCE_MANIFEST.json'),source_files=len(rows(source)),playable_directory=str(normal.relative_to(ROOT)).replace('\\','/'),playable_entry='PLAY_TACTICAL_EQUIPMENT.cmd',user_dir='G1TacticalEquipment20261010',save_prefix='ParisEquipmentV1',normal_files=rows(normal),checks=receipts))
print(str(normal/'PLAY_TACTICAL_EQUIPMENT.cmd'))
