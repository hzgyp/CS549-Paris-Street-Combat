"""Independent playable and exact source snapshot after bounded verification."""
import json,os,shutil
from pathlib import Path
from common import ROOT,OUT,digest,save,row
def main():
    proof=json.loads((OUT/'checks_solo/verification.json').read_text('utf-8-sig'));assert proof['status']=='pass_scoped_player_contact_jump_recorded_m1_and_legacy_restore'
    candidate=OUT/'candidate_v2';prepared=json.loads((candidate/'prepare.json').read_text('utf-8-sig'));build=json.loads((candidate/'build.json').read_text('utf-8-sig'));assert build['exit_code']==0
    working=Path(prepared['project']);archive=candidate/'Archive';inner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe';assert digest(archive/inner)==build['game_sha256']
    variant=ROOT/'Unreal/Variants/G1FootContactAudio20261009';trial=ROOT/'tmp/Playtest-G1-Foley-V2-20261009'
    assert not variant.exists() and not trial.exists(),'Preserve occupied delivery identities'
    variant.mkdir(parents=True);source=variant/'Project';source.mkdir()
    for r in prepared['source_files']:
        p=working/r['path'];assert digest(p)==r['sha256'];dest=source/r['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    save(variant/'SOURCE_MANIFEST.json',dict(format='paris-source-snapshot-v1',scope='Exact42 recorded Foley parent; only audio helper changes for evaluated player feet, jump and recorded M1 shot; original assets/schema/gameplay/observer unchanged',files=prepared['source_files']))
    shutil.copyfile(candidate/'Audio/PROVENANCE.json',variant/'AUDIO_MANIFEST.json');shutil.copyfile(candidate/'Audio/CREDITS.txt',variant/'AUDIO_CREDITS.txt')
    (variant/'README.md').write_text('# Foot contact and recorded M1 audio candidate\n\n9 October2026. Read CURRENT_AUDIO_REVIEW and paired G1_FOOT_CONTACT_AUDIO_V2_RESULT. Exact42 source extends recorded Foley by ParisGameplayAV.cpp only. Audio bytes private; AUDIO_MANIFEST/CREDITS document33 cues, existing31 intact, recorded M1 first shot and adapted takeoff. Foot pose phase is not sole-floor collision or human acceptance. Normal trial and source are independent of the older review. Recording HOLD; no publication.\n','utf-8')
    trial.mkdir();expected=[]
    for p in sorted(archive.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(archive)
        if rel.as_posix()=='PLAY_G1_REVISION.cmd':continue
        dest=trial/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if 'Audio' in rel.parts:shutil.copyfile(p,dest)
        else:os.link(p,dest)
        expected.append(row(p,archive))
    old=(ROOT/'tmp/Playtest-G1-Foley-20261009/PLAY_G1_REVISION.cmd').read_text('utf-8-sig');assert old.count('G1PlaytestFoley20261009')==1
    launcher=old.replace('G1PlaytestFoley20261009','G1PlaytestFoleyV220261009')
    assert all(s not in launcher for s in ['ParisUXTest','ParisAVAuditOut','ParisAVSoloPlayer','NoSound','UnfocusedVolumeMultiplier'])
    cmd=trial/'PLAY_G1_REVISION.cmd';cmd.write_text(launcher,'utf-8');assert cmd.stat().st_nlink==1
    shutil.copytree(OUT/'listening',trial/'Listen')
    (trial/'README_试听说明.txt').write_text('G1 落脚同步 / 跳跃 / 实录M1音效复查版\n\n双击 PLAY_G1_REVISION.cmd，Enter开始。WASD移动，Shift跑步，Alt静步，Space起跳，站立R换弹。让游戏保持前台，后台默认静音。\n\n重点听：开始/停止/跑步/静步的脚步是否跟步伐对应，Space是否有轻微起跳鞋底和衣物声，以及落地接触声；玩家和盟军是否采用新M1实录单发。换弹音/模型/手指/动画/弹药/存档/HUD保留。德军枪声仍是旧声：尚未找到免费可复用的精确K98实弹录音，没有冒充。\n\nListen只是来源素材试听，不是游戏录音或新录屏。新M1来自室内靶场公开HQ预览，不是无损巴黎室外录音。跳跃是实录鞋底/布料拟音。骨骼低位触发不证明物理鞋底碰撞或修复脚滑；听感/动作对应仍需你复查。\n\n独立存档目录 ParisStreetCombat/G1PlaytestFoleyV220261009；旧目录/试玩/存档保留。F6/Ctrl+R重开，F9读档，清场后存档圈沿用现有规则。转身问题仍记录，录屏暂停。\n','utf-8')
    actual=[row(p,trial) for p in sorted(trial.rglob('*')) if p.is_file()]
    expected_paths={r['path'] for r in expected}|{'PLAY_G1_REVISION.cmd','README_试听说明.txt'}|{'Listen/'+p.relative_to(OUT/'listening').as_posix() for p in (OUT/'listening').rglob('*') if p.is_file()}
    assert {r['path'] for r in actual}==expected_paths
    for r in expected:assert digest(trial/r['path'])==r['sha256']
    selector=dict(schema_version=1,status='local_runtime_verified_audio_v2_manual_review_pending',candidate_id='g1-foot-contact-audio-v2-20261009',parent_candidate=prepared['parent'],
      source_snapshot=source.relative_to(ROOT).as_posix(),source_manifest=(variant/'SOURCE_MANIFEST.json').relative_to(ROOT).as_posix(),source_manifest_sha256=digest(variant/'SOURCE_MANIFEST.json'),source_files=42,
      active_authoring_project=(working/'WW2FranceLiberation.uproject').relative_to(ROOT).as_posix(),game_sha256=build['game_sha256'],playable_entry=cmd.relative_to(ROOT).as_posix(),
      audio_manifest=(variant/'AUDIO_MANIFEST.json').relative_to(ROOT).as_posix(),audio_files=33,recorded_m1_sha256=digest(candidate/'Audio/fire_m1.wav'),old_german_fire_sha256=digest(candidate/'Audio/fire.wav'),
      human_parent_feedback='Recorded Foley much improved; residual player foot phase and missing jump; other issues minor; user authorizes real gunshot replacement',
      human_acoustic_review='PENDING for revised feet/jump/M1 report',recording_gate='HOLD until explicit manual revised sound approval, then natural turn correction before demonstration',
      result='G1_FOOT_CONTACT_AUDIO_V2_RESULT_20261009.md',saved_schema='ParisG1PlaytestV5',normal_user_directory='%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestFoleyV220261009',
      remaining=['Manual step cadence/jump/M1 report review','Exact licensed K98 live-fire source unavailable, original German report retained','Physical sole-floor contact/foot sliding remains separate','Natural turn/FPS/stress/teammate/course gates'],publication='Local uncommitted/unpublished; no OBS/video/Git/SFTP')
    save(ROOT/'Docs/Development/CURRENT_AUDIO_REVIEW.json',selector)
    save(OUT/'delivery.json',dict(status=selector['status'],selector=selector,trial_files=actual,independent_mutable_launcher=True,no_new_recording=True))
    print(json.dumps(dict(trial=str(trial),files=len(actual),game_sha256=build['game_sha256'],source_manifest_sha256=selector['source_manifest_sha256'])))
if __name__=='__main__':main()
