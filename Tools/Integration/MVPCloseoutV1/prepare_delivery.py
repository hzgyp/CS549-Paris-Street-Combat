"""Prepare a private, hash-identified review bundle without selecting/publishing it."""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--build',default='instrument_v13');p.add_argument('--functional',default='candidate_agent_v1');p.add_argument('--plain',default='agent_plain_v1');p.add_argument('--stress',default='stress_6_v1');p.add_argument('--demo',default='demo_v1');p.add_argument('--media-status',choices=['pending','verified'],default='pending');p.add_argument('--identity',default='delivery_v1');a=p.parse_args()
    base=ROOT/'tmp/mvp-closeout-20261008';build=base/a.build;out=STORE/a.identity
    assert not out.exists(),'Preserve occupied delivery identity'
    gates={n:json.loads((base/i/'read_only_audit.json').read_text()) for n,i in [('functional',a.functional),('plain',a.plain),('stress',a.stress)]}
    assert gates['functional']['rounds']==3 and gates['functional']['old_configuration_rejections']==3
    assert gates['plain']['status']=='pass_observer_disabled_native_ready_only'
    assert gates['stress']['rounds']==1
    media=STORE/a.demo;mr=None;media_candidate=None
    if a.media_status=='verified':
        mr=json.loads((media/'media_receipt.json').read_text());assert mr['status']=='encoded_visual_review_pass'
        media_build=base/mr['source_build'];media_candidate=json.loads((media_build/'agent_candidate.json').read_text())
    else:
        assert not (media/'media_receipt.json').exists(),'Do not hide an existing media receipt'
    for i in [a.functional,a.plain,a.stress]:
        launch=json.loads((base/i/'launch.json').read_text());assert launch['build']==a.build
    candidate=json.loads((build/'agent_candidate.json').read_text())
    for row in candidate['changes']:assert sha(build/row['path'])==row['candidate_sha256']
    if media_candidate:assert [(x['path'],x['candidate_sha256']) for x in candidate['changes']]==[(x['path'],x['candidate_sha256']) for x in media_candidate['changes']]
    out.mkdir();source=out/'SourcePatch';source.mkdir()
    prereq=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Extras/Redist/en-us/vc_redist.x64.exe')
    assert prereq.is_file(),'Missing exact bundled x64 runtime prerequisite'
    (out/'Prerequisites').mkdir();shutil.copy2(prereq,out/'Prerequisites/vc_redist.x64.exe')
    project=build/'Project'
    for folder in ['Config','Source']:
        shutil.copytree(project/folder,source/folder)
    shutil.copy2(project/'WW2FranceLiberation.uproject',source)
    for plugin in (project/'Plugins').iterdir():
        if not plugin.is_dir():continue
        dest=source/'Plugins'/plugin.name;dest.mkdir(parents=True)
        for desc in plugin.glob('*.uplugin'):shutil.copy2(desc,dest)
        if (plugin/'Source').is_dir():shutil.copytree(plugin/'Source',dest/'Source')
    for name in ['prepare.json','instrument.json','native_candidate.json','agent_candidate.json']:
        shutil.copy2(build/name,source/name)
    # This small patch is private review source, not a new selected Git/native revision.
    shutil.copytree(ROOT/'Tools/Integration/MVPCloseoutV1',out/'CloseoutTools',ignore=shutil.ignore_patterns('__pycache__'))
    files=list((build/'Archive').rglob('*'));files=[f for f in files if f.is_file()]
    assert len(files)>20
    rows=[dict(path=str(f.relative_to(build/'Archive')).replace('\\','/'),size_bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(files)]
    games=[r for r in rows if r['path'].endswith('/Binaries/Win64/WW2FranceLiberation.exe')];assert len(games)==1
    for i in [a.functional,a.plain,a.stress]:assert json.loads((base/i/'launch.json').read_text())['binary_sha256']==games[0]['sha256']
    relative=games[0]['path']
    launch='@echo off\r\ncd /d "%~dp0"\r\n"%~dp0'+relative.replace('/','\\')+'" -windowed -ResX=1920 -ResY=1080 -DisablePython -noraytracing -ParisSavePrefix=ParisG1CandidateV4 -UserDir="%LOCALAPPDATA%/ParisStreetCombat/G1CandidateV4" -ExecCmds="sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0"\r\n'
    readme='''PARIS STREET COMBAT - PRIVATE G1 CANDIDATE / NOT FINAL COURSE RELEASE

Extract the entire ZIP to a writable folder. Run PLAY_G1_CANDIDATE.cmd on Windows x64.
Keep all cooked content beside the executable. Install the bundled UE prerequisite
installer (Prerequisites/vc_redist.x64.exe) if runtime dependencies are missing. No Unreal editor,
Python pose driver or network service is required for this packaged game.

Enter starts. WASD moves; mouse looks; left mouse fires; R reloads.
F5 requests a safe save. F9 loads the latest valid checkpoint.
Ctrl+R restarts the full mission. Alt+F4 exits.
Cross bridge C with two Allies, defeat the three G1 guards and occupy G1.
Wait for the HUD to report a successful save; combat/movement can deny unsafe saves.
This candidate uses isolated ParisG1CandidateV4 slots in the user's local app data.
Old V2/V3 saves are not compatible and must not be copied over these slots.

Validated: three scripted original squad/capture/save/fresh-load cycles, two full
restarts and three correct-checksum old-configuration rejections; separate ordinary
startup with automation inactive. NOT validated: unassisted human full playthrough,
second machine, natural two-sided encounter in this combined packaged fixture,
all animation/contact/collision/lifecycle regressions or full course acceptance.
High 1080p/100%, hardware ray tracing off, 1536 MiB texture pool:
three complete route captures average 52.00 / 51.57 / 51.21 FPS. The 60 FPS target
is NOT met. See the separate finite stress receipt; no unmeasured capacity claim.

Baseline public source: b8a3a6a1ba1f730730be23f6fa1d801787d58165.
Selected native source assets: paris-native-playtest-20261008-g1-npc-vfx-v1.
SourcePatch contains the private tested wrapper's source/configuration, including
the opt-in test module. It is NOT committed/selected by main or the team Catalog.
To rebuild, restore entitled baseline content locally, use this wrapper source
with UE 5.8.2/Win64 SDK, and use CloseoutTools. Do not copy tmp machine junctions.
The source/cooked manifest and binary hashes identify this exact private candidate.
SourcePatch has no Content. Restore the entitled manifest content to its Content
directory, then build/cook that project with the exact UAT arguments in build.ps1.
The helper scripts expect the original repository layout; copy CloseoutTools to
Tools/Integration/MVPCloseoutV1 in a baseline checkout rather than running them
directly here. Fresh-machine source rebuild remains a teammate verification gate.

Private three-teammate review only. Commercial assets remain private. Do not upload
the build or source assets publicly or distribute to reviewers until that audience
and the relevant finished-product rights/access have actually been confirmed.
No valid annotated video is delivered: four recording routes failed observation
admission and are archived. Do not invoke the legacy -ParisCapture flag on this
V13 playable; its inactive recording experiment is not part of the play interface.
'''
    (out/'PLAY_G1_CANDIDATE.cmd').write_bytes(launch.encode('utf-8'))
    (out/'README_FIRST.txt').write_text(readme)
    (out/'README_FIRST_ZH.txt').write_text('''巴黎街头战斗：G1 私下测试候选，尚非课程最终版。

完整解压 ZIP 到可写目录，双击 PLAY_G1_CANDIDATE.cmd。
Enter 开始；WASD 移动；鼠标转向；左键开火；R 换弹；F5 安全存档；
F9 读档；Ctrl+R 完整重开；Alt+F4 退出。请等 HUD 确认存档成功。
目标：带两名盟军过 C 桥，清除三名 G1 守卫并占领桥头。
此候选使用独立的本机存档目录，不要用旧 V2/V3 存档覆盖它。
缺少运行库时安装 Prerequisites/vc_redist.x64.exe。

三轮脚本过桥、汇合、攻占、存读档及两次重开已通过；三次旧配置存档拒绝通过。
普通启动的自动测试输入关闭。真人完整通关、另一台电脑和完整动作／碰撞回归未通过。
1080p High、100% 渲染、关闭硬件光追：52.00／51.57／51.21 FPS，未达 60 FPS。
独立初始六人负载 53.40 FPS，按预设门槛停止，12／18 人未测；非持续六人存活容量。

这是 main b8a3a6a 与既有授权资产之上的私下源码／程序候选；未提交、未选入 Catalog。
SourcePatch 不含原始商业资产；从本项目授权清单恢复 Content 后方可重建。
保留现有模型、手指、动作与原枪械事务，只修正已验证的 G1 导航和桥头队形问题。
仅供本项目三名组员私下验证；课程评审／公开视频的成品权限和访问尚待确认。
不要因本机脚本通过就写成整体验收或课程完成。
''',encoding='utf-8')
    (out/'build_manifest.json').write_text(json.dumps(dict(files=rows,scope='Private candidate; no Catalog selection or publication'),indent=2)+'\n')
    archive=out/'Paris_Street_Combat_G1_Private_Candidate_Win64.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
        for f in files:z.write(f,str(f.relative_to(build/'Archive')))
        for name in ['PLAY_G1_CANDIDATE.cmd','README_FIRST.txt','README_FIRST_ZH.txt','build_manifest.json']:z.write(out/name,name)
        for folder in ['SourcePatch','CloseoutTools','Prerequisites']:
            for f in (out/folder).rglob('*'):
                if f.is_file():z.write(f,str(f.relative_to(out)))
    with zipfile.ZipFile(archive) as z:
        assert z.getinfo(relative).file_size==next(r['size_bytes'] for r in games)
        for row in rows:
            h=hashlib.sha256()
            with z.open(row['path']) as stream:
                for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
            assert h.hexdigest()==row['sha256'],'ZIP readback differs: '+row['path']
    retained={}
    for label,i in [('functional',a.functional),('plain',a.plain),('stress',a.stress)]:
        folder=out/'Evidence'/label;folder.mkdir(parents=True)
        for name in ['launch.json','read_only_audit.json','result.json','performance_summary.json','finite_stress_result.json']:
            f=base/i/name
            if f.exists():shutil.copy2(f,folder);retained[label+'/'+name]=sha(f)
    receipt=dict(status='private_review_bundle_prepared_not_selected',build_identity=a.build,baseline_git='b8a3a6a1ba1f730730be23f6fa1d801787d58165',
        game_binary_sha256=games[0]['sha256'],zip_size_bytes=archive.stat().st_size,zip_sha256=sha(archive),
        cooked_files=len(files),cooked_bytes=sum(r['size_bytes'] for r in rows),zip_cooked_sha256_readback='all exact',runtime_prerequisite_sha256=sha(out/'Prerequisites/vc_redist.x64.exe'),retained_receipt_hashes=retained,
        source_patch_files=[dict(path=str(f.relative_to(source)),sha256=sha(f)) for f in sorted(source.rglob('*')) if f.is_file()],
        media_status=a.media_status,demo_receipt_sha256=sha(media/'media_receipt.json') if mr else None,demo_build_identity=mr['source_build'] if mr else None,demo_binary_sha256=mr['source_binary_sha256'] if mr else None,limits=['60 FPS target missed','No valid demo delivered; capture failures archived','Human / second-machine and wider reviewer access open','Current changes uncommitted / not selected'])
    (out/'delivery_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ['source_patch_files','retained_receipt_hashes']},indent=2))

if __name__=='__main__':main()
