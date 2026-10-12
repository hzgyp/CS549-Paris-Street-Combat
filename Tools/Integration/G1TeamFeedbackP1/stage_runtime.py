"""Immutable cooked bytes are linked; all writable files and Game are independent."""
import argparse, json, shutil, os
from prepare import ROOT, OUT, SOURCE, sha

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--revision',default='candidate_v1');args=ap.parse_args()
    assert args.revision in {'candidate_v1','candidate_v2','candidate_v3','candidate_v4','candidate_v5','candidate_v6','candidate_v7','candidate_v8','candidate_v9'}
    freeze=json.loads((OUT/'freeze.json').read_text());build=json.loads((OUT/args.revision/'build.json').read_text('utf-8-sig'))
    assert build['exit_code']==0 and build['status']=='built_runtime_unverified'
    parent=ROOT/freeze['parent']['playable_directory']
    target=ROOT/('tmp/Playtest-G1-TeamP1-'+args.revision+'-20261010');assert not target.exists()
    inner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    assert sha(parent/inner)==freeze['p0_game_sha256'];target.mkdir()
    for p in parent.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(parent);dest=target/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if rel.as_posix()==inner:continue
        if p.suffix.lower() in {'.cmd','.ps1','.md','.txt','.json','.ini','.log'}:shutil.copyfile(p,dest)
        else:os.link(p,dest)
    binary=OUT/args.revision/'Project/Binaries/Win64/WW2FranceLiberation.exe';assert sha(binary)==build['game_sha256'];shutil.copyfile(binary,target/inner)
    launcher=target/'PLAY_G1_REVISION.cmd';s=launcher.read_text('utf-8-sig');assert s.count('G1Interaction20261010')==1
    launcher.write_text(s.replace('G1Interaction20261010','G1TeamP1'+args.revision.replace('candidate_','')+'20261010'),'utf-8')
    (target/'README_试听说明.txt').write_text('G1 组员反馈 P1 复查候选（未替换人工接受基线）\n\n双击 PLAY_G1_REVISION.cmd。菜单鼠标或方向键/Tab + Enter；原菜单与 E 存档修复保留。\n\n新任务/重开 8 发装填 + 10 备用，读档恢复原数值。步行 2.2 米/秒、跑步 4.5 米/秒；Alt 静步、Ctrl 蹲伏、Z 匍匐、Space 跳跃、R 换弹保持。\n\n北朝上玩家中心雷达，半径 25 米；A1/A2 显示距离与圈外方向，阵亡标 DOWN。背景仍是 G1 已测绘区域，UNSURVEYED EDGE 提醒未知范围。绿色描边十字仅改可读性。\n\n消灭 3 守军后等待小队过桥和 G1 secured，再在金色圈内站立停下，E 保存；F9 读档、F6 重开。独立 user-save 目录，不覆盖 audio V2 或 P0。普通入口无自动输入/测试 helper。\n\n人物、手指、枪械/资源/保存事务与录音保持；本批未新增 ADS 或八发弹夹换弹动画。人工复验步伐、声音和 HUD。\n','utf-8')
    (target/'INTERACTION_REVIEW.md').write_text('P1 extends the P0 menu/E-save repair. See README_试听说明.txt and Docs/Development/G1_TEAM_FEEDBACK_P1_RESULT_20261010_ZH.md. The selected audio V2 parent remains protected. This ordinary entry contains no diagnostic observer.\n','utf-8')
    r=dict(status='staged_unverified',path=str(target),revision=args.revision,game_sha256=sha(target/inner),source_manifest_sha256=sha(SOURCE.parent/'SOURCE_MANIFEST.json'))
    if (OUT/'RUNTIME.json').exists():shutil.copyfile(OUT/'RUNTIME.json',OUT/(args.revision+'_previous_runtime.json'))
    (OUT/'RUNTIME.json').write_text(json.dumps(r,indent=2)+'\n','utf-8');print(json.dumps(r))

if __name__=='__main__':main()
