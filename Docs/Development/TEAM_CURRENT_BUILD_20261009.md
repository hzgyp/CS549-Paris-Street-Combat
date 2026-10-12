## 2026-10-11：最新正式76版已同步SFTP

最新组员包 `/releases/paris-g1-playtest-20261011-gameplay-v1/Paris-G1-Gameplay-20261011.zip`；精确76源／运行资源／SHA及恢复步骤见[最新同步指南](TEAM_CURRENT_BUILD_20261011_ZH.md)。原老师audioV2下载及课程附件保留，以下旧日期文字为历史。衣袖遮挡待修；新的76版外机验证由组员进行。

## 11October2026 current local gameplay revision

The latest formal local revision is manually accepted76 `G1GrenadeEquip20261011`; read [current baseline](CURRENT_DEVELOPMENT_BASELINE.md). Minor sleeve occlusion remains. No new package sync happened in adoption; the SFTP course release below remains the earlier audioV2, not this76 source.

## 10October2026 current local revision

The current manually accepted local source is exact52 `Unreal/Variants/G1EnemyClearCheckpoint20261010/Project`; see [current baseline](CURRENT_DEVELOPMENT_BASELINE.md). Local entry `PLAY_CURRENT_G1.cmd`. The audioV2 SFTP download described below is the prior published/course revision and remains available; it does not contain the latest checkpoint repair. No new package sync occurred in this local adoption task.

# Current private playable and source

9 October2026. Yupu manually retested audio V2 and selects it as the development
basis. Read G1_AUDIO_BASELINE_PUBLICATION_RESULT_20261009.md for actual delivery
and cleanup; [Chinese guide](TEAM_CURRENT_BUILD_20261009_ZH.md).

Preserve unfinished code and ignored asset edits, then `git pull --ff-only` in a
current clean clone. Old asset-bearing clones follow the safe team rejoin flow,
not an old-history merge. Current source is exact42 under
`Unreal/Variants/G1FootContactAudio20261009/Project`; follow the baseline selector.

Obtain SFTP account/endpoint/fingerprint privately from Yupu. Download
`/releases/paris-g1-playtest-20261009-audio-v2/Paris-G1-Audio-V2-20261009.zip`.
Verify SHA256/size against Assets/Sync/manifests/paris-g1-packaged-playtest.json.
Extract all to a writable Windows folder and run PLAY_G1_REVISION.cmd. Read
README.md for controls/runtime prerequisite. No Editor/Python required for play;
no personal saves or credentials included. Commercial cooked assets remain
private to the three entitled members. Previous HUD download ZIP is retired.

For editable assets, TEAM_PLAYTEST.md still governs unchanged native359/city
restoration. Cached old Editor DLLs do not implement the selected newer Game
audio source. Use a separate writable wrapper and overlay the exact42 Project
paths. Restore the33 WAV paths in paris-g1-recorded-audio.json, then copy them to
wrapper Audio. Copy AUDIO_MANIFEST.json as Audio/PROVENANCE.json and
AUDIO_CREDITS.txt as Audio/CREDITS.txt. Preserve unique asset edits; never edit
immutable SFTP objects. Author-side wrapper/build receipts describe actual local
preparation. Clean Editor recook/second-machine rebuild are unverified.

Teammates verify download/extraction/startup, walk/run/slow movement, jump/landing/
M1/reload sound, G1 three-guard clear and consent-circle save, F9 stopped-corpse
restore and restart. Return Git revision, ZIP SHA, engine/prerequisite version,
actual observations and errors. Publisher hashes and Yupu's review do not pass
second-machine, FPS/stress/video/course gates. No teammate message is sent.
