"""Freeze a locally verified revision and prepare a separate human trial folder."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source
BASE=ROOT/'tmp/g1-playtest-revision-20261008'
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'

def main():
    p=argparse.ArgumentParser();p.add_argument('build');p.add_argument('actions');p.add_argument('checkpoint');p.add_argument('ordinary');a=p.parse_args()
    assert all(x.replace('_','').isalnum() for x in vars(a).values())
    built=BASE/a.build;prepared=json.loads((built/'prepare_revision.json').read_text());receipt=json.loads((built/'build_revision.json').read_text(encoding='utf-8-sig'))
    project=Path(prepared['project']);checks=[]
    for identity in [a.actions,a.checkpoint,a.ordinary]:
        audit=BASE/identity/'read_only_audit.json';r=json.loads(audit.read_text())
        assert r['status']=='pass_integrity_numeric_visual_review_separate' and r['strict_issues']==[]
        checks.append(dict(identity=identity,numeric_status=r['numeric_status'],audit_sha256=digest(audit)))
    assert checks[0]['numeric_status'].startswith('pass_scoped_input')
    assert checks[1]['numeric_status'].startswith('pass_checkpoint')
    assert checks[2]['numeric_status']=='ordinary_ready_only_no_action_or_checkpoint_claim'
    assert verify_source()['source_files']==758
    guards=guard_rows();assert len(guards)==703 and guards_match(guards)
    native=json.loads((ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json').read_text())
    assert len(native['files'])==359
    for row in native['files']:assert digest(ROOT/row['path'])==row['sha256'] and (ROOT/row['path']).stat().st_size==row['size_bytes']
    for row in prepared['private_source_files']:assert digest(project/row['path'])==row['sha256']
    descriptor=project/'WW2FranceLiberation.uproject';assert digest(descriptor)==digest(BASE/'candidate_v3/SourceAtV3/WW2FranceLiberation.uproject')
    binary=built/'Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    assert digest(binary)==receipt['game_sha256']
    out=STORE/'Evidence/G1PlaytestRevisionV1/delivery_v1';trial=ROOT/'tmp/Playtest-G1-20261009'
    assert not out.exists() and not trial.exists(),'Protect occupied evidence/user trial'
    out.mkdir(parents=True);source=out/'SourcePatch'
    for row in prepared['private_source_files']:
        dst=source/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(project/row['path'],dst)
    shutil.copyfile(descriptor,source/descriptor.name)
    shutil.copytree(built/'Archive',trial)
    en='''# Paris Street Combat — revised G1 trial

Private team trial, 9 October 2026. Start PLAY_G1_REVISION.cmd.
Existing 8 October trial and its saves are preserved. This revision uses a separate
G1PlaytestV5 save directory; it does not load the earlier candidate's checkpoint.

Enter starts; WASD walks; hold Shift runs; hold Alt walks slowly; Space jumps;
Ctrl toggles crouch; Z toggles prone; W/S crawl; mouse looks/fires; R reloads;
F9 loads the checkpoint; F6 restarts the mission.

Prone requires flat supported ground and space for the whole body. Bridge rubble
can refuse entry or stop crawling. The original prone only moves forward/back;
crouch/prone cannot fire/reload. Dedicated first-person sprint/jump lowering and
posture-specific eye-height/contact remain unfinished; accepted grips are retained.

After all three guards die, the green ground circle marks the G1 checkpoint.
Enter it to see the question. E explicitly saves when standing, still and safe;
Escape declines. Entering never saves automatically. Leave/re-enter to ask again.
The upper-right minimap covers the surveyed G1 ground sector, with live player,
Allies, objective and currently visible enemy markers. It is not a full-city or
multilevel map. Ammo shows loaded rounds, reserve rounds and 8-round load equivalents;
the game still stores reserve rounds, not individual magazine objects.

Finite local input/obstruction/checkpoint tests and ordinary HUD images were checked.
An earlier V9 entry failed at GPU startup; its cause remains unverified. The final
V10 entries start cleanly, but that does not explain or repair that earlier failure.
This is a new human trial, not human/second-machine/full-contact/60FPS or course
completion acceptance. Commercial assets remain private to the authorized team.
'''
    zh='''# 巴黎巷战 — 修订版G1试玩

2026年10月9日，团队私下试玩。双击 PLAY_G1_REVISION.cmd。
10月8日旧试玩和旧存档保留；新版使用独立G1PlaytestV5存档目录。

Enter开始；WASD步行；按住Shift跑步、Alt静步；Space跳跃；Ctrl切换蹲伏；
Z切换匍匐，W/S前后爬行；鼠标观察/开火；R换弹；F9读档；F6重开。

匍匐要求平整、有支撑且整个人体有净空；桥面碎石可能拒绝趴下或阻止爬行。
保留原有规则：匍匐仅前后移动，蹲伏/匍匐不能射击换弹。第一人称专用
冲刺/跳跃收枪和低姿态眼位/接触还没完成；已认可的握枪模型继续保留。

三个守卫全部死亡后，G1地面出现绿色保存圈。进圈弹出问题，站立、静止且
安全后按E确认保存；Esc暂不保存。进圈不会自动保存，离开再进可重新询问。
右上小地图是已测G1地面区域，显示玩家、盟军、目标和当前可见敌人；
不代表完整巴黎或分层地图。弹药显示已装弹、备用弹及每8发可装载数量；
原逻辑仍存储备用子弹，没有虚构独立弹夹物品。

本机有限输入/遇障/存档测试及普通启动UI实图已核对。此次供人工重试玩，
此前一次V9启动发生GPU故障，原因尚未确认；最终V10测试正常启动，
但这并不能解释或证明修复了此前的GPU故障。
不代表人工、第二台机器、全动作接触、60FPS或课程全部验收通过。
商业资产仅供已授权团队私下使用。
'''
    (trial/'README.md').write_text(en,encoding='utf-8');(trial/'README_ZH.md').write_text(zh,encoding='utf-8')
    archive_rows=[]
    for f in sorted((built/'Archive').rglob('*')):
        if not f.is_file():continue
        rel=f.relative_to(built/'Archive');dst=trial/rel;sha=digest(f)
        assert dst.stat().st_size==f.stat().st_size and digest(dst)==sha
        archive_rows.append(dict(path=rel.as_posix(),size_bytes=f.stat().st_size,sha256=sha))
    # Match the tested HUD entry's debug-message suppression; the frozen Archive
    # remains byte-exact. Record this one delivery-only launcher change explicitly.
    launcher=trial/'PLAY_G1_REVISION.cmd'
    original_launcher_sha=digest(launcher)
    launcher_text=launcher.read_text(encoding='utf-8')
    assert launcher_text.count('-ExecCmds="')==1
    launcher_text=launcher_text.replace('-ExecCmds="','-ExecCmds="DisableAllScreenMessages,',1)
    launcher.write_text(launcher_text,encoding='utf-8')
    launcher_override=dict(path=launcher.name,archive_sha256=original_launcher_sha,
        delivered_sha256=digest(launcher),reason='Suppress development screen messages as in all final native/ordinary HUD tests; no game or cooked content change')
    source_rows=[dict(path=f.relative_to(source).as_posix(),size_bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(source.rglob('*')) if f.is_file()]
    result=dict(status='private_revision_local_scoped_tests_pass_human_review_pending',build=a.build,trial_directory=str(trial),
        game_sha256=receipt['game_sha256'],source_patch_files=source_rows,archive_files=archive_rows,checks=checks,
        archive_copy_verified_before_launcher_override=True,delivery_launcher_override=launcher_override,
        canonical_source_files=758,protected_files=703,selected_native_files=359,action=prepared['action'],
        minimap_sha256=digest(trial/'Windows/WW2FranceLiberation/UI/g1_minimap.png'),
        old_user_trial_preserved=True,commercial_scope='private authorized team only',
        limits=['human motion/contact','second machine','60FPS','natural two-sided firefight','full-city multilevel map','unexplained earlier V9 GPU startup failure','course/video gates'])
    (out/'delivery_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    (trial/'REVISION_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],trial_directory=str(trial),game_sha256=receipt['game_sha256'],archive_files=len(archive_rows),source_files=len(source_rows)),indent=2))
if __name__=='__main__':main()
