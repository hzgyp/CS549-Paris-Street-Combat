from pathlib import Path
import sys,shutil,os
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,sha,read,write,rows,INNER
rev=sys.argv[1];epoch=sys.argv[2];base=root/'tmp/g1-grenade-equip-20261011';parent=read(base/'freeze.json')['parent'];runtime=read(OUT/rev/'runtime.json');game=runtime['game_sha256'];checks=[]
def check(mode,p):
    result=read(p/'RESULT.json');launch=read(p/'launch.json');assert result['status'].startswith('pass') and launch['exit_code']==0 and launch['game_sha256']==game,(mode,p)
    checks.append(dict(mode=mode,result=(p/'RESULT.json').relative_to(root).as_posix(),status=result['status'],sha256=sha(p/'RESULT.json'),game_sha256=game))
for mode in ['wheel','throw','smoke','p1','enemy_clear','interactions','save_equipment','restore_equipment','restore_legacy','performance']:check(mode,OUT/'checks'/(mode+'_'+epoch))
for mode in ['equipment_pause','pages','pause','confirm']:check('ui_'+mode,root/'tmp/g1-combat-ui-20261011/checks'/('ui_'+mode+'_'+epoch))
check('death_frag',root/'tmp/g1-player-death-20261011/checks'/('frag_'+epoch))
assert read(OUT/rev/'protection.json')['status']=='pass'
assert read(base/'VISUAL_REVIEW.json')['game_sha256']==game
source=root/'Unreal/Variants/G1GrenadeEquip20261011/Project';assert not source.exists();shutil.copytree(OUT/rev/'compiled-source-game',source)
files=rows(source);assert len(files)==76
write(source.parent/'SOURCE_MANIFEST.json',dict(status='unselected_local_grenade_equip_candidate',revision=rev,files=files))
normal=root/'tmp/Playtest-G1-GrenadeEquip-20261011';normal.mkdir(exist_ok=False)
for p in (Path(runtime['path'])/'Windows').rglob('*'):
    if not p.is_file():continue
    dst=normal/'Windows'/p.relative_to(Path(runtime['path'])/'Windows');dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
entry=(root/parent['playable_entry']).read_bytes().replace(b'G1EquipmentWheel20261011',b'G1GrenadeEquip20261011').replace(b'ParisEquipmentWheelV1',b'ParisGrenadeEquipV2')
assert not any(x in entry for x in [b'Probe',b'EquipmentCheck',b'Observer',b'Solo',b'Background',b'BlastDiag'])
(normal/'PLAY_GRENADE_EQUIP.cmd').write_bytes(entry)
(normal/'README_ZH.md').write_text('# 手持投掷物与库存轮换修订统一试玩\n\n运行 PLAY_GRENADE_EQUIP.cmd。\n\n- 滚轮在步枪与仍有库存的手雷／烟雾弹之间正反轮换；耗尽类型直接跳过。\n- 两种投掷物全用完后保持步枪，滚轮不改变姿势或鼠标按压状态。\n- 切到投掷物使用现有手雷就绪Loop，外壳展示在手中；左键按住进入准备／持握，松开投出，完成后回枪。\n- 松手前Esc／滚轮取消，不扣库存，旧松开不误射；松手后等待原投出动作完成。G/Q旧直接投掷停用。\n- E拆雷／补给／全灭敌军后的圈内保存，Esc战地手册，Tab人物小队保持。\n\n本版修正上一版端枪姿势、手雷遮挡及空槽轮换。原MkII／烟雾模型和贴图、原枪械手指常量／枪械内部逻辑／原保存代码、身体移动、AI／导航、地雷补给及死亡承接。原准备／投出／库存／引信／伤害／烟幕函数逐字保持。独立UserDir G1GrenadeEquip20261011／前缀ParisGrenadeEquipV2；原用户档保持。必须保留完整Windows目录，不能只复制exe。\n\n普通入口没有探针、自动操作、隐藏手部或摄影机／AI／资源覆盖。15项同一Game检查和实际图通过本机验证，细致全程接触／所有动作与人类操作仍由统一试玩评审；未正式采用或发布。\n',encoding='utf-8')
assert sha(normal/INNER)==game
review=dict(status='unselected_unified_grenade_equip_candidate',revision=rev,game_sha256=game,source_snapshot=source.relative_to(root).as_posix(),source_manifest=(source.parent/'SOURCE_MANIFEST.json').relative_to(root).as_posix(),source_manifest_sha256=sha(source.parent/'SOURCE_MANIFEST.json'),source_files=len(files),active_authoring_project=Path(read(OUT/rev/'prepare.json')['project']).relative_to(root).as_posix(),playable_directory=normal.relative_to(root).as_posix(),playable_entry=(normal/'PLAY_GRENADE_EQUIP.cmd').relative_to(root).as_posix(),user_dir='G1GrenadeEquip20261011',save_prefix='ParisGrenadeEquipV2',parent_record=(base/'freeze.json').relative_to(root).as_posix(),parent_source=parent['source_snapshot'],implementation='Docs/Development/MissionLoopV1/GRENADE_EQUIP_REVISION_IMPLEMENTATION_20261011_ZH.md',result='Docs/Development/MissionLoopV1/GRENADE_EQUIP_REVISION_RESULT_20261011_ZH.md',checks=checks,protection=(OUT/rev/'protection.json').relative_to(root).as_posix(),assets=runtime['assets'],manual_review='pending',limitations=['Actual ready/hold frames reviewed; detailed continuous contact and all locomotion transitions remain manual review.','Temporary FP source only; original body/camera/rifle controls and save schema retained.','Current roster performance only, not expanded NPC stress or second-machine acceptance.'],publication='none; no Git/SFTP/adoption',editors='Existing UE Editors remain open')
review['visual_review']=(base/'VISUAL_REVIEW.json').relative_to(root).as_posix()
write(base/'DELIVERY_20261011.json',dict(review,normal_files=rows(normal)))
for name in ['CURRENT_EQUIPMENT_INPUT_REVIEW','CURRENT_UI_REVIEW']:write(root/('Docs/Development/'+name+'.json'),review)
print(normal/'PLAY_GRENADE_EQUIP.cmd')
