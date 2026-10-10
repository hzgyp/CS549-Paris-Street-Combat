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
