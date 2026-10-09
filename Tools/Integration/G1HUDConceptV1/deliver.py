"""Freeze the tested HUD-only revision without replacing prior user trials."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source
BASE=ROOT/'tmp/g1-playtest-revision-20261008'
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'

def rows(folder):
    return [dict(path=f.relative_to(folder).as_posix(),size_bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(folder.rglob('*')) if f.is_file()]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('build');parser.add_argument('ordinary');parser.add_argument('small');parser.add_argument('checkpoint');args=parser.parse_args()
    assert all(x.replace('_','').isalnum() for x in vars(args).values())
    built=BASE/args.build;prepared=json.loads((built/'prepare_revision.json').read_text())
    build=json.loads((built/'build_revision.json').read_text(encoding='utf-8-sig'))
    project=Path(prepared['project']);checks=[]
    for identity in [args.ordinary,args.small,args.checkpoint]:
        folder=BASE/identity;report=json.loads((folder/'read_only_audit.json').read_text())
        launch=json.loads((folder/'launch.json').read_text(encoding='utf-8-sig'))
        assert report['status']=='pass_integrity_numeric_visual_review_separate' and not report['strict_issues']
        log=(folder/'game.log').read_text()
        assert launch['binary_sha256']==build['game_sha256'] and 'PARIS_HUD_CINZEL_DRAW runtime_ufont=1' in log
        assert any('Cinzel.ttf' in line and 'Freetype font face in memory successfully created' in line for line in log.splitlines())
        checks.append(dict(identity=identity,audit_sha256=digest(folder/'read_only_audit.json'),status=report['numeric_status']))
    assert checks[-1]['status'].startswith('pass_checkpoint')
    assert verify_source()['source_files']==758
    protected=guard_rows();assert len(protected)==703 and guards_match(protected)
    assert prepared['save_schema_config_and_nonrender_policy_exact']
    for r in prepared['private_source_files']:assert digest(project/r['path'])==r['sha256']
    assert digest(project/'WW2FranceLiberation.uproject')==prepared['descriptor_sha256']
    assert digest(built/'Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==build['game_sha256']
    assert digest(built/'UI/Cinzel.ttf')==prepared['font']['font_sha256']
    assert digest(built/'UI/Cinzel-OFL.txt')==prepared['font']['license_sha256']
    trial=ROOT/'tmp/Playtest-G1-HUD-20261009';evidence=STORE/'Evidence/G1HUDConceptV1/delivery_v1'
    assert not trial.exists() and not evidence.exists(),'Preserve occupied user/evidence directories'
    evidence.mkdir(parents=True);source=evidence/'SourcePatch'
    for r in prepared['private_source_files']:
        dst=source/r['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(project/r['path'],dst)
    shutil.copyfile(project/'WW2FranceLiberation.uproject',source/'WW2FranceLiberation.uproject')
    archive_rows=rows(built/'Archive');shutil.copytree(built/'Archive',trial)
    for r in archive_rows:assert digest(trial/r['path'])==r['sha256'] and (trial/r['path']).stat().st_size==r['size_bytes']
    launcher=trial/'PLAY_G1_REVISION.cmd';before=digest(launcher)
    text=launcher.read_text(encoding='utf-8');assert text.count('-ExecCmds="')==1
    launcher.write_text(text.replace('-ExecCmds="','-ExecCmds="DisableAllScreenMessages,',1),encoding='utf-8')
    # Keep the same V5 journal identity and user save directory; only presentation changes.
    for name in ['README.md','README_ZH.md']:
        text=(ROOT/'tmp/Playtest-G1-20261009'/name).read_text(encoding='utf-8')
        text=text.replace('green ground circle','thin gold ground circle').replace('绿色保存圈','细金色保存圈').replace('G1地面出现绿色保存圈','G1地面出现细金色保存圈')
        text=text.replace('8-round load equivalents','capacity ticks').replace('每8发可装载数量','容量刻度')
        text=text.replace('Finite local input/obstruction/checkpoint tests and ordinary HUD images were checked.',
            'Fresh ordinary HUD and checkpoint tests pass locally. Prior V10 input/obstruction\nresults are retained; that action suite was not rerun for this rendering change.')
        text=text.replace('V10 entries start cleanly','HUD entries start cleanly')
        text=text.replace('本机有限输入/遇障/存档测试及普通启动UI实图已核对。此次供人工重试玩，',
            '本次普通启动UI实图与存档流程已核对；V10输入/遇障结果保留，\n本次纯渲染修改未重跑该动作套件。此次供人工重试玩，')
        text=text.replace('最终V10测试正常启动','最终HUD测试正常启动')
        intro=('Approved ivory/brass HUD concept implemented, 9 October 2026.\nCircular minimap, serif type, floating health/ammo and compact save prompt.\nUses the SAME V5 checkpoint identity and save directory as the prior revision.\n\n' if name=='README.md' else
            '2026年10月9日：按已选概念图实现米白/旧黄铜HUD、衬线字、圆形小地图、\n紧凑血量弹药和悬浮保存提示。沿用上一修订版的V5存档身份与目录。\n\n')
        (trial/name).write_text(intro+text,encoding='utf-8')
    final=evidence/'FinalQualification'
    for check in checks:
        origin=BASE/check['identity'];dest=final/check['identity'];dest.mkdir(parents=True)
        files=['launch.json','game.log','read_only_audit.json']+([ 'result.json'] if (origin/'result.json').exists() else [])
        files += [f.name for f in origin.glob('*.png')]
        for name in files:
            shutil.copyfile(origin/name,dest/name);assert digest(origin/name)==digest(dest/name)
    (final/'MANIFEST.json').write_text(json.dumps(dict(scope='Actual finite local HUD/checkpoint and ordinary startup evidence; no human/FPS/course acceptance',files=rows(final)),indent=2)+'\n')
    receipt=dict(status='private_hud_concept_implemented_local_checks_pass_user_review_pending',trial_directory=str(trial),
        build=args.build,game_sha256=build['game_sha256'],checks=checks,archive_files=archive_rows,
        archive_copy_verified_before_launcher_override=True,
        delivery_launcher_override=dict(path=launcher.name,archive_sha256=before,delivered_sha256=digest(launcher),reason='Match tested debug-message suppression'),
        source_patch_files=rows(source),save_prefix='ParisG1PlaytestV5',save_directory='%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestV5',
        prior_v10_user_checkpoints_compatible_by_exact_policy_schema_config=True,old_trials_preserved=True,
        canonical_source_files=758,protected_files=703,font=prepared['font'],concept_sha256=prepared['approved_concept_sha256'],
        limits=['human visual acceptance','full motion/contact','second machine','60FPS','natural two-sided firefight','full-city/multilevel map','unexplained earlier GPU startup failure','video/course gates'])
    (evidence/'delivery_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (trial/'REVISION_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(status=receipt['status'],trial_directory=str(trial),game_sha256=build['game_sha256'],archive_files=len(archive_rows)),indent=2))
if __name__=='__main__':main()
