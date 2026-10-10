"""Record the user's selected exact source; never changes native/game bytes."""
import json
from pathlib import Path
from publish import ROOT, OUT, VARIANT, RELEASE, GAME, now, read, write, sha


def main():
    publication=read(OUT/'publication.json')
    assert publication['status']=='verified_selected'
    audio_path=ROOT/'Docs/Development/CURRENT_AUDIO_REVIEW.json'
    audio=read(audio_path)
    assert audio['game_sha256']==GAME
    audio['status']='manually_reviewed_selected_published_audio_v2'
    audio['human_acoustic_review']='PASS by explicit user manual retest; selected for continued development'
    audio['human_review_at']=now()
    audio['human_review_authorization']='User: manual retest passed; use this version, delete obsolete packages, commit/push and synchronize SFTP'
    audio['recording_gate']='Manual audio gate passed; natural turn correction and separate video gates remain. No recording in publication task.'
    audio['publication']='Verified private SFTP package and33 cue objects/manifests; matching source carried by this Git revision'
    audio['sftp_release']=RELEASE
    audio['sftp_download']=publication['download']
    audio['remaining']=[s for s in audio['remaining'] if not s.startswith('Manual step cadence')]
    write(audio_path,audio)
    baseline_path=ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json'
    parent=read(baseline_path)
    baseline=dict(schema_version=2,status='selected_active_development_baseline',authorization=audio['human_review_authorization'],
        selected_at=audio['human_review_at'],baseline_id=audio['candidate_id'],playable_directory='tmp/Playtest-G1-Foley-V2-20261009',
        playable_entry=audio['playable_entry'],game_sha256=GAME,source_snapshot=audio['source_snapshot'],source_manifest=audio['source_manifest'],
        source_manifest_sha256=audio['source_manifest_sha256'],active_authoring_project=audio['active_authoring_project'],active_source_files=42,
        audio_manifest='Assets/Sync/manifests/paris-g1-recorded-audio.json',audio_files=33,sftp_release=RELEASE,sftp_download=publication['download'],
        matching_source_revision='Git revision containing this selector; exact pushed HEAD recorded in publication handoff/private receipt',
        native_asset_anchor=parent['native_asset_anchor'],canonical_source_contract_role=parent['canonical_source_contract_role'],protected=parent['protected'],
        save_prefix=audio['saved_schema'],save_directory=audio['normal_user_directory'],human_manual_review='Passed; selected by Yupu Guo',
        latest_audio_review_candidate='Docs/Development/CURRENT_AUDIO_REVIEW.json',latest_local_repair='Docs/Development/CURRENT_LOCAL_REPAIR.json',
        remaining_gates=parent['remaining_gates']+['natural-turn recording correction','exact reusable German live-fire source'],
        future_rule='Start all future changes from this exact42 snapshot or matching authoring Project; read failures first, preserve native/model/finger/gun/ammo/HUD/save/dead-restore logic. Build selected source before Editor entry.',
        retirement_map='Docs/Development/G1AudioPublicationV2/RECOVERY_MAP_20261009.json',
        previous_selected_baseline=dict(role='Historical40-file visual/source anchor; old runnable packages retired by later user authorization',selector=parent))
    write(baseline_path,baseline)
    repair_path=ROOT/'Docs/Development/CURRENT_LOCAL_REPAIR.json';repair=read(repair_path)
    repair['current_selected_child']='Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json'
    repair['later_selection']='Audio V2 manual review passed;42-file child selected and privately published. Original AV repair remains historical, carry terminal-death fix forward.'
    write(repair_path,repair)
    (ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.md').write_text('''# Current development baseline

9 October2026. Yupu manually retested the latest audio V2 and explicitly selects
it for continued development. CURRENT_DEVELOPMENT_BASELINE.json is authoritative;
older HUD40/AV42/Foley42 entries are preserved historical source anchors.

Use `tmp/Playtest-G1-Foley-V2-20261009/PLAY_G1_REVISION.cmd` to play. Start new source
work from exact42 `Unreal/Variants/G1FootContactAudio20261009/Project` or matching
`tmp/g1-foot-contact-audio-v2-20261009/candidate_v2/Project`. The source manifest
SHA256 is2ff88f0e74040b46e8b7c26750602c56556857a06b45db96c28f297f534b468b;
Game SHA256 is53ab36d9da1975a2f8e1109fcf6745cc40e96d371fc89fbfa009139b91950aec.
Preserve the authoring Content junction and cooked inputs; an old folder name
does not make an active Project disposable. Build this selected source before
any new Editor entry; cached original Editor DLLs do not represent this Game.

Private SFTP release `paris-g1-playtest-20261009-audio-v2`; download
`/releases/paris-g1-playtest-20261009-audio-v2/Paris-G1-Audio-V2-20261009.zip`.
Extract all, run the launcher. Its92 members include the exact88-file trial,
English/Chinese controls, source identity and existing Microsoft prerequisite.
The separate33-cue manifest is Assets/Sync/manifests/paris-g1-recorded-audio.json.
For source rebuilding, restore its exact RuntimeAudio paths then copy WAVs to
the writable wrapper's Audio folder. Native city/character/weapon manifests and
source758/native359 remain restoration/protection anchors, unchanged. The Git
variant alone does not contain vendor Content or establish a clean Editor recook.

The selected version carries corrected player foot-phase sounds, takeoff/landing,
actual M1 report, realistic recorded reload cues and stopped saved corpses, on the
accepted HUD/model/finger/action/gun/resource/save basis. User manual sound review
passes;20 stable contacts were numerically checked and9 blend contacts remain
unassessed. German actual live-fire sourcing, physical contact, natural turning,
performance/stress/second-machine/video/course gates remain separate.

Obsolete local/SFTP playable packages are retired under the paired
G1_AUDIO_BASELINE_PUBLICATION_20261009 plan/result and exact inventory. For removed
old paths, consult G1AudioPublicationV2/RECOVERY_MAP_20261009.json; current bytes
plus the compact unique-file ZIP preserve recovery. Keep the prior V13 recovery
ZIP, old source/log/image/raw-video/checkpoint/failure evidence and originals.
Manual audio approval ends its prior listening hold; natural-turn correction
still precedes a future demo. This publication task creates no screen recording.
''','utf-8')
    (ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE_ZH.md').write_text('''# 当前开发基础

2026年10月9日。Yupu人工复验最新音效V2通过，明确选作后续开发基础。以同名JSON
选择器为准；HUD40、AV42及旧Foley42源码保留作历史锚点，旧可运行包可以退休。

试玩入口`tmp/Playtest-G1-Foley-V2-20261009/PLAY_G1_REVISION.cmd`。后续源码从精确
42文件`Unreal/Variants/G1FootContactAudio20261009/Project`或一致的制作工程
`tmp/g1-foot-contact-audio-v2-20261009/candidate_v2/Project`开始。源码清单哈希
2ff88f0e74040b46e8b7c26750602c56556857a06b45db96c28f297f534b468b；程序哈希
53ab36d9da1975a2f8e1109fcf6745cc40e96d371fc89fbfa009139b91950aec。保留Content
junction和烹饪输入，不因旧目录名称删制作工程。进入编辑器前必须从选定源码构建，
原编辑器缓存DLL不能代表当前Game版本。

SFTP版本`paris-g1-playtest-20261009-audio-v2`，下载
`/releases/paris-g1-playtest-20261009-audio-v2/Paris-G1-Audio-V2-20261009.zip`。
完整解压后启动，92成员含原88文件试玩、双语操作、源码身份及微软运行库。独立
33音效清单在Assets/Sync/manifests/paris-g1-recorded-audio.json；重建先恢复其
RuntimeAudio精确路径，再复制WAV至可写wrapper的Audio目录。城市/人物/枪械原生
清单与source758/native359保持原样作依赖恢复和保护锚点。Git源码不含商业Content，
发布不证明编辑器重新烹饪成功。

选定版本包含玩家落脚阶段音效、起跳/落地、M1实录枪声、已改善的换弹录音和直接
恢复死亡终态；保留原HUD、模型、手指、动作、枪械/资源/存档逻辑。人工音效复验
通过，数值验证仍为20稳定落脚通过、9混合过渡未评估。德军实录来源、物理接触、
自然转身、性能/压力、组员电脑、视频和课程验收仍单独处理。

旧本机/SFTP试玩包按G1_AUDIO_BASELINE_PUBLICATION_20261009双语计划/结果及冻结
清单清理。旧路径请查G1AudioPublicationV2/RECOVERY_MAP_20261009.json，用当前
字节和小型唯一文件ZIP恢复。保留旧V13恢复ZIP、源码/日志/图像/原始视频/存档/
失败证据及资产原件。人工通过结束音效复查暂停；后续演示仍需先修正自然转身，
本次发布没有新增录屏。
''','utf-8')
    (VARIANT/'README.md').write_text('''# Reviewed G1 audio V2 source

9 October2026. Yupu manually retested and selects this exact42-file source as
the development basis. Read CURRENT_DEVELOPMENT_BASELINE and the paired audio
publication result. SOURCE_MANIFEST pins original bytes; do not normalize them.
Public Git contains source/configuration and audio provenance only. Private SFTP
release paris-g1-playtest-20261009-audio-v2 supplies the playable ZIP and33 WAV
objects selected by Assets/Sync/manifests/paris-g1-recorded-audio.json.

Direct play: extract the complete ZIP and run PLAY_G1_REVISION.cmd. For rebuilding,
restore entitled native dependencies via existing team guides, use a separate
writable wrapper and overlay these exact Project paths; restore RuntimeAudio,
copy its WAVs plus AUDIO_MANIFEST/CREDITS to the wrapper's Audio sidecar directory,
and build its Game target with UE5.8.2. Existing integration tools and dated plans
record author-side preparation/cook inputs; private authoring paths are not clone
inputs. Editor recook/second-machine build remains unverified. Never point an
Editor writer at immutable SFTP objects. Models/fingers/actions/HUD/gun/ammo/save/
terminal restore remain protected; read MI014–MI016 before new implementation.
Original German fire is retained with an explicit live-recording source gap.
''','utf-8')
    print(json.dumps(dict(status='reviewed_audio_v2_baseline_adopted',source_files=42,game_sha256=GAME)))


if __name__=='__main__':main()
