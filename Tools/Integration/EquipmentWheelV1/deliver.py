from pathlib import Path
import sys,shutil,os
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,sha,read,write,rows,INNER
rev=sys.argv[1];epoch=sys.argv[2];base=root/'tmp/g1-equipment-wheel-20261011';parent=read(base/'freeze.json')['parent'];runtime=read(OUT/rev/'runtime.json');game=runtime['game_sha256'];checks=[]
def check(mode,p):
    result=read(p/'RESULT.json');launch=read(p/'launch.json');assert result['status'].startswith('pass') and launch['exit_code']==0 and launch['game_sha256']==game,(mode,p)
    checks.append(dict(mode=mode,result=(p/'RESULT.json').relative_to(root).as_posix(),status=result['status'],sha256=sha(p/'RESULT.json'),game_sha256=game))
for mode in ['wheel','throw','smoke','p1','enemy_clear','interactions','save_equipment','restore_equipment','restore_legacy']:check(mode,OUT/'checks'/(mode+'_'+epoch))
for mode in ['equipment_pause','pages','pause','confirm']:check('ui_'+mode,root/'tmp/g1-combat-ui-20261011/checks'/('ui_'+mode+'_'+epoch))
check('death_frag',root/'tmp/g1-player-death-20261011/checks'/('frag_'+epoch))
assert read(OUT/rev/'protection.json')['status']=='pass'
assert read(base/'VISUAL_REVIEW.json')['game_sha256']==game
source=root/'Unreal/Variants/G1EquipmentWheel20261011/Project';assert not source.exists();shutil.copytree(OUT/rev/'compiled-source-game',source)
files=rows(source);assert len(files)==75
write(source.parent/'SOURCE_MANIFEST.json',dict(status='unselected_local_equipment_wheel_candidate',revision=rev,files=files))
normal=root/'tmp/Playtest-G1-EquipmentWheel-20261011';normal.mkdir(exist_ok=False)
for p in (Path(runtime['path'])/'Windows').rglob('*'):
    if not p.is_file():continue
    dst=normal/'Windows'/p.relative_to(Path(runtime['path'])/'Windows');dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
entry=(root/parent['playable_entry']).read_bytes().replace(b'G1GrenadeModels20261011',b'G1EquipmentWheel20261011').replace(b'ParisGrenadeModelsV1',b'ParisEquipmentWheelV1')
assert not any(x in entry for x in [b'Probe',b'EquipmentCheck',b'Observer',b'Solo',b'Background',b'BlastDiag'])
(normal/'PLAY_EQUIPMENT_WHEEL.cmd').write_bytes(entry)
(normal/'README_ZH.md').write_text('''# 滚轮装备／左键投掷统一试玩

运行 PLAY_EQUIPMENT_WHEEL.cmd。

- 滚轮向下：步枪 → 手雷 → 烟雾弹 → 步枪；向上反向切换，当前装备高亮。
- 选中手雷／烟雾弹：左键按住拉引信并保持，松开投出；按住不计时爆炸、不扣库存，真正投出扣一个。
- 松手前 Esc 或滚轮取消，不扣库存；旧左键松开不会误射，重新按下才能使用。已松手开始投掷后等待动作结束，自动回步枪。
- G/Q 直接投掷已停用；步枪左键／右键／R 保持，零库存投掷物不能开枪或换弹。
- Esc 战地手册，Tab 人物／小队，E 拆雷／补给／全灭敌军后的圈内保存保持。

已有模型、手指姿态、投掷动画、枪械内部逻辑、存档、烟幕、地雷、补给和第三人称死亡承接。原 Hold 姿态偏低限制仍保留，请统一试玩评审。独立 UserDir G1EquipmentWheel20261011／前缀 ParisEquipmentWheelV1；旧用户档不改。需要完整 Windows 目录，不能只复制 exe。普通入口无测试探针、自动操作、摄影机、AI／资源覆盖。未正式采用或发布。
''',encoding='utf-8')
assert sha(normal/INNER)==game
review=dict(status='unselected_unified_equipment_wheel_candidate',revision=rev,game_sha256=game,source_snapshot=source.relative_to(root).as_posix(),source_manifest=(source.parent/'SOURCE_MANIFEST.json').relative_to(root).as_posix(),source_manifest_sha256=sha(source.parent/'SOURCE_MANIFEST.json'),source_files=len(files),active_authoring_project=Path(read(OUT/rev/'prepare.json')['project']).relative_to(root).as_posix(),playable_directory=normal.relative_to(root).as_posix(),playable_entry=(normal/'PLAY_EQUIPMENT_WHEEL.cmd').relative_to(root).as_posix(),user_dir='G1EquipmentWheel20261011',save_prefix='ParisEquipmentWheelV1',parent_record=(base/'freeze.json').relative_to(root).as_posix(),parent_source=parent['source_snapshot'],implementation='Docs/Development/MissionLoopV1/EQUIPMENT_WHEEL_INPUT_IMPLEMENTATION_20261011_ZH.md',result='Docs/Development/MissionLoopV1/EQUIPMENT_WHEEL_INPUT_RESULT_20261011_ZH.md',checks=checks,protection=(OUT/rev/'protection.json').relative_to(root).as_posix(),assets=runtime['assets'],manual_review='pending',limitations=['Original finger poses/low grenade Hold framing remain; no new grasp or whole-motion acceptance.','Selected grenade exterior uses existing hand attachment/pose before primary preparation.','No expanded NPC/FPS stress or human input/focus acceptance claimed.'],publication='none; no Git/SFTP/adoption',editors='Existing UE Editors remain open')
review['visual_review']=(base/'VISUAL_REVIEW.json').relative_to(root).as_posix()
write(base/'DELIVERY_20261011.json',dict(review,normal_files=rows(normal)))
for name in ['CURRENT_EQUIPMENT_INPUT_REVIEW','CURRENT_UI_REVIEW']:write(root/('Docs/Development/'+name+'.json'),review)
print(normal/'PLAY_EQUIPMENT_WHEEL.cmd')
