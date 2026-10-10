"""Prepare an independent normal review trial and exact42 source, no publication."""
import json,os,shutil
from pathlib import Path
from intake import ROOT,OUT,digest,save_json,row

def main():
    proof=json.loads((OUT/'checks/verification.json').read_text('utf-8'))
    assert proof['status']=='pass_scoped_actual_audio_resource_and_legacy_restore'
    candidate=OUT/'candidate_v1';prepared=json.loads((candidate/'prepare.json').read_text('utf-8'))
    build=json.loads((candidate/'build.json').read_text('utf-8-sig'));assert build['exit_code']==0
    archive=candidate/'Archive';game=archive/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    assert digest(game)==build['game_sha256']
    parent=ROOT/prepared['parent']['source_snapshot'];working=Path(prepared['project'])
    variant=ROOT/'Unreal/Variants/G1RecordedFoley20261009';assert not variant.exists(),'Preserve existing source delivery'
    variant.mkdir(parents=True);source=variant/'Project';source.mkdir()
    for r in prepared['source_files']:
        frm=working/r['path'];assert digest(frm)==r['sha256']
        dest=source/r['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(frm,dest)
    manifest=dict(format='paris-source-snapshot-v1',scope='Exact AVv3 extension by one nonreflected recorded-Foley cpp helper; no native/schema/resource/observer/turn change',files=prepared['source_files'])
    save_json(variant/'SOURCE_MANIFEST.json',manifest)
    shutil.copyfile(candidate/'Audio/PROVENANCE.json',variant/'AUDIO_MANIFEST.json')
    shutil.copyfile(candidate/'Audio/CREDITS.txt',variant/'AUDIO_CREDITS.txt')
    (variant/'README.md').write_text('# Recorded Foley review candidate\n\n9 October2026. Manual acoustic acceptance pending; recording HOLD. Exact42 source files extend AVv3 with one ParisGameplayAV.cpp helper change. Models/fingers/gun/HUD/resources/save/dead-restore and observer remain unchanged. Game Development compiled and scoped actual playback/legacy restore verified. Read Docs/Development/CURRENT_AUDIO_REVIEW.json and paired result; source is not committed/published.\n\nAudio bytes remain private with the playable trial. AUDIO_MANIFEST and Tools/Integration/G1RecordedFoleyV1 record CC0 sources, published HQ MP3 reference hashes, trims/gains and output hashes. These are recording-derived candidates, not a realism/historical-contact approval. Use local current runtimes and authenticated references when reproducing; no original-WAV fidelity claim.\n','utf-8')
    trial=ROOT/'tmp/Playtest-G1-Foley-20261009';assert not trial.exists(),'Preserve existing trial';trial.mkdir()
    # Immutable payload links reduce storage. Do not later edit linked files in place.
    for p in sorted(archive.rglob('*')):
        if not p.is_file():continue
        if p.relative_to(archive).as_posix()=='PLAY_G1_REVISION.cmd':continue # mutable normal entry is authored independently
        dest=trial/p.relative_to(archive);dest.parent.mkdir(parents=True,exist_ok=True)
        if 'Audio' in p.parts:shutil.copyfile(p,dest)
        else:os.link(p,dest)
    old=(ROOT/'tmp/Playtest-G1-AV-20261009/PLAY_G1_REVISION.cmd').read_text('utf-8-sig')
    assert old.count('G1PlaytestAV20261009')==1
    launcher=old.replace('G1PlaytestAV20261009','G1PlaytestFoley20261009')
    assert all(s not in launcher for s in ['ParisUXTest','ParisAVAuditOut','NoSound','UnfocusedVolumeMultiplier'])
    (trial/'PLAY_G1_REVISION.cmd').write_text(launcher,'utf-8')
    shutil.copytree(OUT/'listening',trial/'Listen')
    (trial/'Listen/README.txt').write_text('素材试听，不是新录屏，也不是实录游戏音轨。\n01普通步行；02跑步；03静步；04 M1换弹；05 K98换弹；06布料摩擦；07倒地；08落地。\n试听阶段按现有触发音量/间隔拼接；正式判断请进入游戏，听鞋底接触、摩擦、机构声及动作对应关系。\n许可/来源/裁剪记录见 Windows/WW2FranceLiberation/Audio/PROVENANCE.json 与 CREDITS.txt。\n','utf-8')
    (trial/'README_试听说明.txt').write_text('G1 实录音效试听版 — 2026年10月9日\n\n双击 PLAY_G1_REVISION.cmd，Enter开始，再测试：WASD步行、Shift跑步、Alt静步、Space跳跃落地、平整地面Z匍匐移动，站立R换弹。让游戏窗口保持前台，后台静音是现有行为。\n\n优先听脚步是否像靴底接触硬地/碎石，跑步是否更实，静步是否更轻；换弹金属声是否贴合手部动作。枪声保持原样。M1与K98采用不同实录机械声，不乱加弹夹叮声。\n\nListen内是素材试听样例，非实录游戏音轨。游戏内听感与时机仍待你人工通过，不把数值/波形当作真实感验收。K98、匍匐、倒地接触和换弹中断仍需人工检查。现有换弹动画/模型/手指/弹药/存档/HUD保留。\n\n本版使用独立本机存档目录 ParisStreetCombat/G1PlaytestFoley20261009，原试玩及存档保留。Ctrl+R/F6重新开始、F9读档和清场后存档圈沿用原规则。\n\n突兀回头已记录：旧自动观察器直接跳转控制朝向，本次未改转身/镜头。人工确认声音以前不会重新录屏。本版没有录屏开关。\n','utf-8')
    finish(trial,variant,source,working,prepared,build)

def finish(trial,variant,source,working,prepared,build):
    rows=[row(p,trial) for p in sorted(trial.rglob('*')) if p.is_file()]
    assert len(rows)==91 and digest(trial/'Windows/WW2FranceLiberation/Audio/fire.wav')==prepared['approved_fire_sha256']
    selector=dict(schema_version=1,status='local_runtime_verified_audio_candidate_manual_review_pending',candidate_id='g1-recorded-foley-v1-20261009',
        parent_repair='CURRENT_LOCAL_REPAIR.json',parent_repair_id=prepared['parent']['repair_id'],
        source_snapshot=source.relative_to(ROOT).as_posix(),source_manifest=(variant/'SOURCE_MANIFEST.json').relative_to(ROOT).as_posix(),
        source_files=42,source_manifest_sha256=digest(variant/'SOURCE_MANIFEST.json'),
        active_authoring_project=(working/'WW2FranceLiberation.uproject').relative_to(ROOT).as_posix(),
        game_sha256=build['game_sha256'],playable_entry=(trial/'PLAY_G1_REVISION.cmd').relative_to(ROOT).as_posix(),
        audio_manifest=(variant/'AUDIO_MANIFEST.json').relative_to(ROOT).as_posix(),audio_files=31,approved_fire_sha256=prepared['approved_fire_sha256'],
        saved_schema='ParisG1PlaytestV5',normal_user_directory='%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestFoley20261009',
        result='G1_AUDIO_REALISM_RESULT_20261009.md',human_acoustic_review='PENDING',recording_gate='HOLD until explicit manual sound approval',
        turn_defect='MI015: source46.47->46.53s snapped about-face; documented only, observer unchanged',
        publication='Local uncommitted/unpublished; no OBS/video export/Git/SFTP',
        future_rule='Read parent baseline/local repair, this candidate and MI015. Preserve exact parent40/AV42/assets/fire/history; human listening gates further recording. No automatic visual/source/publication adoption.',
        remaining=['Manual in-game realism and contact timing','K98/crawl/body-contact/active interruption runtime review','Continuous natural mouse/turn presentation','Original FPS/stress/teammate/course gates'])
    save_json(ROOT/'Docs/Development/CURRENT_AUDIO_REVIEW.json',selector)
    save_json(OUT/'delivery.json',dict(status=selector['status'],selector=selector,trial_files=rows,
        protected_history='Original trial/source/audio/video untouched; this is an independent candidate',no_new_recording=True))
    print(json.dumps(dict(status=selector['status'],trial=str(trial),files=len(rows),source_manifest_sha256=selector['source_manifest_sha256'],game_sha256=build['game_sha256']),indent=2))

if __name__=='__main__':main()
