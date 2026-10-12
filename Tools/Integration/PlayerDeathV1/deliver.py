"""Deliver only after same-Game runtime, visual and protection acceptance."""
from pathlib import Path
import sys,argparse,shutil,os
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,rows,sha,INNER
ap=argparse.ArgumentParser();ap.add_argument('--revision',default='candidate_death_v6');ap.add_argument('--epoch',default='death_v6');ap.add_argument('--death_suffix',default='v6');a=ap.parse_args()
base=ROOT/'tmp/g1-player-death-20261011';parent=read(base/'freeze.json')['parent'];runtime=read(OUT/a.revision/'runtime.json');game=runtime['game_sha256'];checks=[]
def check(mode,path):
    result=read(path/'RESULT.json');launch=read(path/'launch.json')
    assert result['status'].startswith('pass') and launch['exit_code']==0 and launch['game_sha256']==game,(mode,path)
    checks.append(dict(mode=mode,result=(path/'RESULT.json').relative_to(ROOT).as_posix(),result_sha256=sha(path/'RESULT.json'),status=result['status'],game_sha256=game))
for mode in ['mine','frag','damage','crouch','prone']:check('death_'+mode,base/'checks'/(mode+'_'+a.death_suffix))
for mode in ['pause','equipment_pause','pages','confirm','pages_small']:check('ui_'+mode,ROOT/'tmp/g1-combat-ui-20261011/checks'/('ui_'+mode+'_'+a.epoch))
for mode in ['menu','enemy_clear','p1','throw','smoke','interactions','mine_range','mine_post_clear','mine_post_clear_frag','save_equipment','restore_equipment','restore_legacy','restore_v16_equipment','performance']:check(mode,OUT/'checks'/(mode+'_ui_'+a.epoch))
assert read(OUT/a.revision/'death-protection.json')['status']=='pass'
visual=read(base/'VISUAL_REVIEW.json');assert visual['status']=='pass' and visual['game_sha256']==game
compiled=OUT/a.revision/'compiled-source-game';files=rows(compiled);assert len(files)==73
assert all(sha(OUT/a.revision/'Project'/r['path'])==r['sha256'] for r in files)
source=ROOT/'Unreal/Variants/G1PlayerDeath20261011/Project';assert not source.exists();shutil.copytree(compiled,source)
write(source.parent/'SOURCE_MANIFEST.json',dict(status='unselected_local_player_death_UI_candidate',revision=a.revision,files=files))
normal=ROOT/'tmp/Playtest-G1-DeathPresentation-20261011';assert not normal.exists();normal.mkdir()
for p in (Path(runtime['path'])/'Windows').rglob('*'):
    if not p.is_file():continue
    dst=normal/'Windows'/p.relative_to(Path(runtime['path'])/'Windows');dst.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix.lower() in {'.ini','.json','.txt','.md','.cmd','.ps1','.log'}:shutil.copyfile(p,dst)
    else:os.link(p,dst)
entry=(ROOT/parent['playable_directory']/'PLAY_COMBAT_UI.cmd').read_bytes().replace(b'G1FieldManualUI20261011',b'G1DeathPresentation20261011').replace(b'ParisFieldManualUIV1',b'ParisDeathPresentationV1')
entry=entry.replace(b'-DisablePython ',b'-DisablePython -UDPMESSAGING_TRANSPORT_ENABLE=false ')
assert not any(x in entry for x in [b'Probe',b'EquipmentCheck',b'Observer',b'Solo',b'Background',b'BlastDiag'])
(normal/'PLAY_COMBAT_UI.cmd').write_bytes(entry)
(normal/'README_ZH.md').write_text('''# 死亡表现与战地手册统一试玩

运行此目录PLAY_COMBAT_UI.cmd。所有试玩入口留在tmp，不在工程根加快捷脚本。Esc战地手册，Tab人物小队；原G/Q装备、E地雷拆除/补给/清场存档保持。

玩家死亡立即保留原Lost/资源保护，但先切第三人称，完整播放原整身倒地，再显示YOU DIED与重开/读档；倒地期间不接受菜单/重开/读档/射击/装备。地雷与手雷增加短火光/尘烟，原录音/半径/遮挡伤害不变。

模型、手指、枪械、全灭保存判定和双槽校验/读回保持；旧NPC尸体读档仍直接停在末态。正常入口无探针、自动操作或AI/资源覆盖，独立UserDir G1DeathPresentation20261011 / prefix ParisDeathPresentationV1，不迁移覆盖旧用户档。现有UE编辑器继续开启。

本地统一试玩候选，等待人工复验；正式enemy-clear基线和已发布课程包不变。
''',encoding='utf-8')
assert sha(normal/INNER)==game
review=dict(status='unselected_player_death_and_field_manual_unified_candidate',revision=a.revision,game_sha256=game,source_snapshot=source.relative_to(ROOT).as_posix(),source_manifest=(source.parent/'SOURCE_MANIFEST.json').relative_to(ROOT).as_posix(),source_manifest_sha256=sha(source.parent/'SOURCE_MANIFEST.json'),source_files=len(files),active_authoring_project=(OUT/a.revision/'Project').relative_to(ROOT).as_posix(),playable_directory=normal.relative_to(ROOT).as_posix(),playable_entry=(normal/'PLAY_COMBAT_UI.cmd').relative_to(ROOT).as_posix(),user_dir='G1DeathPresentation20261011',save_prefix='ParisDeathPresentationV1',parent_record=(base/'freeze.json').relative_to(ROOT).as_posix(),implementation='Docs/Development/MissionLoopV1/PLAYER_DEATH_PRESENTATION_IMPLEMENTATION_20261011_ZH.md',result='Docs/Development/MissionLoopV1/PLAYER_DEATH_PRESENTATION_RESULT_20261011_ZH.md',checks=checks,protection=(OUT/a.revision/'death-protection.json').relative_to(ROOT).as_posix(),visual_review=(base/'VISUAL_REVIEW.json').relative_to(ROOT).as_posix(),stopped_candidates=['candidate_death_v1 compile/MI038','candidate_death_v2 mine numeric pass but framing/terminal text rejected/MI039','candidate_death_v3 fire shader usage failed/MI040; prone admission fixture failed/MI041','candidate_death_v4 mine numeric pass but fire still indistinct/MI040','candidate_death_v5 short authored Niagara flame invisible/MI040'],editors='Existing Editors remain open; no new Editor/PIE/cook acceptance',manual_review='pending_actual_visual_playtest',publication='none',trial_storage='all candidate packages and launchers under tmp; no root trial wrappers')
write(base/'DELIVERY_20261011.json',dict(review,normal_files=rows(normal)))
write(ROOT/'Docs/Development/CURRENT_PLAYER_DEATH_REVIEW.json',review);write(ROOT/'Docs/Development/CURRENT_UI_REVIEW.json',review)
print(normal/'PLAY_COMBAT_UI.cmd')
