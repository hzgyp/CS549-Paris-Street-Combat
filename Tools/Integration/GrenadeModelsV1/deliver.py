from pathlib import Path
import sys,shutil,os
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,sha,read,write,rows,INNER
rev='candidate_grenade_models_v5';epoch='gmv5';base=root/'tmp/g1-grenade-models-20261011';parent=read(base/'freeze.json')['parent'];runtime=read(OUT/rev/'runtime.json');game=runtime['game_sha256'];checks=[]
def check(mode,p):
    result=read(p/'RESULT.json');launch=read(p/'launch.json');assert result['status'].startswith('pass') and launch['exit_code']==0 and launch['game_sha256']==game,(mode,p)
    checks.append(dict(mode=mode,result=(p/'RESULT.json').relative_to(root).as_posix(),status=result['status'],sha256=sha(p/'RESULT.json'),game_sha256=game))
for mode in ['models','throw','smoke','p1','enemy_clear','interactions','save_equipment','restore_equipment','restore_legacy','restore_v16_equipment','performance']:check(mode,OUT/'checks'/(mode+'_'+epoch))
check('equipment_pause',root/'tmp/g1-combat-ui-20261011/checks'/('ui_equipment_pause_'+epoch))
check('death_frag',root/'tmp/g1-player-death-20261011/checks'/('frag_'+epoch))
assert read(OUT/rev/'protection.json')['status']=='pass'
visual=read(base/'VISUAL_REVIEW.json');assert visual['status']=='pass_render_with_inherited_hold_crop_limit' and visual['game_sha256']==game
source=root/'Unreal/Variants/G1GrenadeModels20261011/Project';assert not source.exists();shutil.copytree(OUT/rev/'compiled-source-game',source)
files=rows(source);assert len(files)==74
write(source.parent/'SOURCE_MANIFEST.json',dict(status='unselected_local_unified_grenade_model_candidate',revision=rev,files=files))
normal=root/'tmp/Playtest-G1-GrenadeModels-20261011';normal.mkdir(exist_ok=False)
for p in (Path(runtime['path'])/'Windows').rglob('*'):
    if not p.is_file():continue
    dst=normal/'Windows'/p.relative_to(Path(runtime['path'])/'Windows');dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
entry=(root/parent['playable_entry']).read_bytes().replace(b'G1DeathPresentation20261011',b'G1GrenadeModels20261011').replace(b'ParisDeathPresentationV1',b'ParisGrenadeModelsV1')
assert not any(x in entry for x in [b'Probe',b'EquipmentCheck',b'Observer',b'Solo',b'Background',b'BlastDiag'])
(normal/'PLAY_GRENADE_MODELS.cmd').write_bytes(entry)
(normal/'README_ZH.md').write_text('''# 手雷与烟雾弹模型统一试玩

运行 PLAY_GRENADE_MODELS.cmd。G手雷、Q烟雾弹：按住准备，松开投掷，准备时Esc取消；Esc战地手册、Tab人物/小队，E拆雷/补给/敌军全灭后的圈内保存保持。

Mk II手雷从原盟军装备提取；烟雾弹无库存模型，按1943 AN-M8外观制作灰罐黄标。原人物、手指、枪械、投掷动作/库存/轨迹/伤害/烟幕、地雷、补给、存档和第三人称死亡承接。原Hold动作手部偏低，道具下半部仍会被手/屏幕下沿遮挡，本次保留原姿态；请统一试玩评审。

独立UserDir G1GrenadeModels20261011、前缀ParisGrenadeModelsV1，旧用户档保持；普通入口没有探针、自动操作、摄影机或AI/资源覆盖。所有新增模型运行数据在Windows/WW2FranceLiberation/Equipment/Grenades，不能只复制exe。试玩包留在tmp，不改正式启动入口。本次未Git/SFTP发布或正式采用。
''',encoding='utf-8')
assert sha(normal/INNER)==game
author=Path(read(OUT/rev/'prepare.json')['project'])
review=dict(status='unselected_unified_grenade_models_candidate',revision=rev,game_sha256=game,source_snapshot=source.relative_to(root).as_posix(),source_manifest=(source.parent/'SOURCE_MANIFEST.json').relative_to(root).as_posix(),source_manifest_sha256=sha(source.parent/'SOURCE_MANIFEST.json'),source_files=len(files),active_authoring_project=author.relative_to(root).as_posix(),authoring_name_note='candidate_grenade_models_v1 Project contains final v5; v1–v5 immutable compiled snapshots/receipts remain separate',playable_directory=normal.relative_to(root).as_posix(),playable_entry=(normal/'PLAY_GRENADE_MODELS.cmd').relative_to(root).as_posix(),user_dir='G1GrenadeModels20261011',save_prefix='ParisGrenadeModelsV1',parent_record=(base/'freeze.json').relative_to(root).as_posix(),parent_source=parent['source_snapshot'],implementation='Docs/Development/MissionLoopV1/GRENADE_MODELS_IMPLEMENTATION_20261011_ZH.md',result='Docs/Development/MissionLoopV1/GRENADE_MODELS_RESULT_20261011_ZH.md',checks=checks,protection=(OUT/rev/'protection.json').relative_to(root).as_posix(),visual_review=(base/'VISUAL_REVIEW.json').relative_to(root).as_posix(),assets=runtime['assets'],manual_review='pending',limitations=['Original hold pose remains at lower screen edge; no new continuous grasp/contact or whole animation acceptance.','Ground close image uses independent photo fixture camera; normal entry has none.','Performance run covers current roster, not expanded NPC stress.'],publication='none; no Git/SFTP/adoption',editors='Existing UE Editors remain open')
write(base/'DELIVERY_20261011.json',dict(review,normal_files=rows(normal)))
write(root/'Docs/Development/CURRENT_GRENADE_MODEL_REVIEW.json',review);write(root/'Docs/Development/CURRENT_UI_REVIEW.json',review)
print(normal/'PLAY_GRENADE_MODELS.cmd')
