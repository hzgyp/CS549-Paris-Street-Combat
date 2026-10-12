"""Reuse unchanged cooked files; independently copy writable text and new Game."""
import json, shutil, os, argparse
from prepare import ROOT, OUT, SOURCE, sha

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--revision',choices=['candidate_v2','candidate_v3','candidate_v4'],required=True);args=parser.parse_args()
    freeze=json.loads((OUT/'freeze.json').read_text('utf-8'))
    build=json.loads((OUT/args.revision/'build.json').read_text('utf-8-sig'))
    assert build['status']=='built_runtime_unverified' and build['exit_code']==0
    parent=ROOT/freeze['parent']['playable_directory']
    target=ROOT/('tmp/Playtest-G1-Interaction-20261010' if args.revision!='candidate_v4' else 'tmp/Playtest-G1-Interaction-V4-20261010')
    assert not target.exists()
    inner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    assert sha(parent/inner)==freeze['normal_game_sha256']
    target.mkdir()
    count=0
    for p in parent.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(parent);dest=target/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if rel.as_posix()==inner:continue
        if p.suffix.lower() in {'.cmd','.ps1','.md','.txt','.json','.ini','.log'}:shutil.copyfile(p,dest)
        else:os.link(p,dest)
        count+=1
    binary=OUT/args.revision/'Project/Binaries/Win64/WW2FranceLiberation.exe'
    assert sha(binary)==build['game_sha256'];shutil.copyfile(binary,target/inner)
    launcher=target/'PLAY_G1_REVISION.cmd';text=launcher.read_text('utf-8-sig')
    assert text.count('G1PlaytestFoleyV220261009')==1
    launcher.write_text(text.replace('G1PlaytestFoleyV220261009','G1Interaction20261010'),'utf-8')
    (target/'README_试听说明.txt').write_text('G1 菜单与 E 存档交互复查版，2026-10-10\n\n双击 PLAY_G1_REVISION.cmd。鼠标点击菜单；或 Up/Down/Tab 选择、Enter 确认。没有兼容存档时 Load 禁用。开始菜单点击不射击。\n\nWASD 移动，Shift 跑步，Alt 静步，Space 跳跃，Ctrl 蹲伏，Z 匍匐，R 换弹。F6 重开，F9 读档。原动作、音效、手指、枪械与资源规则保留。\n\n消灭三名 G1 守军后，到金色存档圈内站立并停止移动，按 E 明确请求保存。失败会说明原因；等待相应动作/盟军事务结束后可再次按 E。Esc 关闭提示后无需出圈再入圈，E 可重新请求。仅写入并读回校验成功才显示 Mission saved。\n\n本候选使用独立存档目录 %LOCALAPPDATA%/ParisStreetCombat/G1Interaction20261010，前缀 ParisG1PlaytestV5。原 audio V2 试玩与存档保持。候选等待人工复验；普通入口不启用任何测试辅助。\n\nListen 是此前来源音效试听，声音未在本批修改。\n','utf-8')
    (target/'INTERACTION_REVIEW.md').write_text('Menu/checkpoint review candidate, 10 October 2026.\n\nMouse or Up/Down/Tab + Enter selects the menu. Load is disabled without a compatible checkpoint.\nE explicitly requests/attempts saving; stand still inside the unlocked circle and wait for living squad actions to settle. Failures explain the cause and can be retried with E.\nOriginal models, fingers, gun/resources, audio and journal retained. Independent user-save directory.\nParent audio V2 remains selected; this candidate awaits human review.\n','utf-8')
    result=dict(status='runtime_staged_unverified',path=str(target),game_sha256=sha(target/inner),reused_parent_files=count,source_manifest_sha256=sha(SOURCE.parent/'SOURCE_MANIFEST.json'))
    receipt=OUT/'RUNTIME.json'
    if receipt.exists():
        archive=OUT/(args.revision+'_previous_runtime.json');assert not archive.exists();shutil.copyfile(receipt,archive)
    receipt.write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(result))

if __name__=='__main__': main()
