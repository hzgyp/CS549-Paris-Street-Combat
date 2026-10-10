# G1 saved-corpse, gameplay audio and English video — actual result

9 October 2026. [Chinese review](G1_DEATH_AUDIO_VIDEO_RESULT_20261009_ZH.md).
The requested local repair and re-recorded draft02 are complete. Follow the
[bounded plan](G1_DEATH_AUDIO_VIDEO_REVISION_20261009.md) and
[MI014](../../Failures/MI014-20261009-checkpoint-death-audio/FAILURE_ANALYSIS.md).
Cases read: MI007–MI014, including the stopped capture routes; selected HUDv3,
retirement, input/save results and Assignment3 requirements. This is a local
functional/media result, not course, stress, full-motion or teammate acceptance.

## Delivered identities

| Item | Local path / identity |
|---|---|
| Repaired playable | `tmp/Playtest-G1-AV-20261009/PLAY_G1_REVISION.cmd` |
| Game Development Win64 | SHA256 `49da3a2cf5f10a05bba40073206f7727831b98c8d17f8538c49d4d40b328ad9c` |
| Exact42-file source | `Unreal/Variants/G1PresentationAV20261009/Project` |
| Source manifest bytes | SHA256 `3301ebd3d541d16a97b42d1e5843ed4305146c6c09a42ef21fff23028c826f50` |
| New English/audio video | `Assets/LocalShared/Deliverables/Assignment3/DemoDraft02_20261009/Paris_G1_MVP_Draft_02.mp4` |
| Video | 128.966667s,1920x1080,30fps,3869 frames,123,856,376bytes |
| Video SHA256 | `286e8c89544b09ee58618e75a6bcd55a9125c91a6e03d0bf5e5f200d742f4268` |

The source extends the exact selected40-file HUDv3; only mission cpp, finite
observer/module cpp and Build.cs change, with two nonreflected helpers added.
No reflected schema/default/config/save-format change. Game compilation exit0;
retained47-file cooked HUD closure reused with only the inner executable replaced
and Audio folder added. No recook, Editor entry, native asset save or canonical
source replacement. The previous selected40/source758/native359 remain anchors.
Read [CURRENT_LOCAL_REPAIR.json](CURRENT_LOCAL_REPAIR.json) before future work;
carry this tested repair forward without treating it as new model/HUD approval.

## Saved death and sound behavior

ApplySnapshot invoked ordinary PC_Die, starting Rifle_Death_3 at0 even for a saved
dead guard. Keep the original reset/die lifecycle protections, then seek the
existing clip to its3.933333s end without notifies, stop and evaluate its pose.
During fresh-world restore, the game covers pending initialization with
RESTORING CHECKPOINT. Real new deaths retain their original playing transition.
The saved terminal state keeps health0, dead=true, collision/movement disabled
and NPC brain gated. It primes audio trackers as already dead and releases old
world voices. Ammo, legitimate shot/hit, consent, serial/fingerprint and save
journal rules remain unchanged.

Draft01 explicitly ran -NoSound and disabled OBS audio. Normal previous game
WASAPI output initialized, but source lacked gameplay sound hooks. A bounded
first128KiB/class-name scan of16,722 local uassets found no SoundWave/MetaSound
candidate, only generic parent/empty cue references; this is not a full registry
audit. Added12 original deterministic48kHz mono PCM cues: walk/run/slow pairs,
crawl, fire, death body/equipment impact, reload/end and landing. Runtime queues
them through USoundWaveProcedural and actual world-spatial playback, using
physical displacement/grounding, accepted shot sequence and real alive-to-dead
events. No resource/pose/movement transaction is driven by the audio helper.
These are basic synthesized SFX, not professional recorded Foley or human voice.

Footsteps retain23.4m maximum; death impacts use a separate attenuated61.2m
maximum; guns163m. Outside-range cues are skipped before engine audibility
culling. The normal playable retains default mute-on-focus-loss behavior.
Only recording/test processes disclose an Engine Audio unfocused-volume1.0
override so OBS controls cannot mute output. No replacement sound/music/voice
is laid over footage in editing.

## Actual checks

- Final native checkpoint/audio run:9 accepted shots/3 legitimate deaths, all3
  death clips playing near0.012s. Entry/decline/re-entry do not autosave, moving
  E denied, stationary E saves serial1; F9 restores Won/7loaded/2reserve and F6
  restarts Ready/3guards. First and subsequent3seconds show all3 stopped end
  poses/lifecycle guards, with restored tracker events/voices0.
- Exact old HUDv3 V5 journal copied to isolated UserDir passes the same restored
  corpse gates and normal exit0; original user files are not migrated or changed.
- Actions pass physical walk/run/slow150/300/65cm/s, jump/land/crouch, unsafe prone
  refusal, measured flat prone34cm/crawl60cm/s, real obstruction/reverse/stop,
  original reload2/16→8/10 and one-round fire. Current probe's forward crawl
  reaches38.459cm before obstruction; blocked drift0. Low-posture camera polish
  remains backlog. No acceptance threshold or original model/finger pose changed.
- Actual UE master mixes: checkpoint peak0.200745/RMS0.009346, actions
  peak0.198761/RMS0.007411, stereo48kHz/no clipped samples. Audit mixer clocks are
  shorter than wall runtime; those WAVs are diagnostics, never video soundtrack.
- OBS32.2.2 WGC uses exact game title/client area/cursor off and game-process
  loopback audio only, desktop/microphone disabled during capture. Admitted
  actions probe19:50:56 (92.866s,2785 output/2801 drawn frames) supplies both
  opening/action cuts. Fresh checkpoint19:58:27 (133.166s,3995/4013) supplies
  the continuous87.3667s mission excerpt. Both finite games exit0; successful
  sessions have no reported render/encoder-lag rows. This does not measure FPS.
- Actual OBS walking/run/fire PCM is nonzero. Nine gun matches are0.126–0.145s
  after logged events; three overlapping impact cues are identified in actual
  recorded audio. Restored3s segment PCM is exactly zero. Actual saved/early/
  settled frames show stationary terminal corpses; first fresh image retains
  ordinary motion blur, not a replayed death transition.
- Final H264High4.1/yuv420p MP4 has exact30Hz sample timing, faststart, AAC48kHz
  stereo, audio128.9813s (14.7ms padding), peak0.203484/RMS0.005904. Whole-file
  AV decode exit0/errors0 and encode warnings0. English SRT/ASS checks pass.
  Fifteen representative final frames plus full-size save/corpse/caption views
  were inspected. Delivery bytes were independently hashed against the output.

The video runs at1x with automated input and cuts disclosed. Ranges: opening
0–10s, movement10–23.7667s, supported prone23.7667–32.6s, continuous mission
32.6–119.9667s, explicit editorial backlog card119.9667–128.9667s. English
narration outline/SRT/ASS/edit/verification/delivery manifests accompany MP4.
The card uses silence; all gameplay sound comes from the raw game capture.

## Retained failures and operational state

V1's two shared-reference Serialize mistakes stop compilation; frozen42 source
and logs retained, V2 corrects only those arguments. Two blocked/background
checkpoint entries pass numerics but produce silent audit mixes; neither is
audio acceptance. Old23.4m impact culling is retained before V3's separate range.
The user manually handles Windows Firewall prompts; no security UI is automated.

First full OBS mission startup exits3 at frame2 with DXGI device removed/MMU page
fault, before Ready. Its raw19:56:44 MKV and checkpoint_gpu_fail_1 remain private.
Use4871.56MB/budget9285MB does not prove exhaustion; exact GPU cause unresolved.
One documented separate fresh entry then passes the complete task and exit0.
This does not establish absence of occasional graphics-startup faults.

Broad waveform matching incorrectly picks a stronger neighboring rapid shot and
reports0.43s lag; original diagnostic retained. Distinct short-transient and
impact-tail assessment keeps correlation>0.5/delay<0.3s gates. Template
subtraction is analysis-only; final audio has no subtraction/gain/sync shift.
First export's global enc_time_base1:30 mistakenly reaches AAC and emits2177
backward-queue warnings. Entire export_v1 is retained; a video-only option scope
fix produces the admitted export with unchanged frames/cuts/captions/audio.

Original OBS selections Untitled/Untitled are restored; recording off, OBS idle.
All successful owned games exit0 and none remain running. Protected canonical758,
current703, native359, selected40, old authoring40, new42, old executable and
original3 user files remain exact (private protection_after.json).

Preserve both old trial/draft01 and the new local trial/video/source. Preserve
`tmp/g1-av-revision-20261009` and `tmp/g1-demo-draft02-20261009` evidence, failed
identities/raw/exports/isolated UserDirs/build/source/receipts. New playable
payload hardlinks are limited to unchanged admitted cooked dependencies; never
edit them in place. New normal saves use G1PlaytestAV20261009, preserving old
G1PlaytestV5. No Git commit/push/SFTP/video-host publication occurred this turn.
Current-build performance/stress/natural battle/full motion/second machine,
report/hosted links/mentor/course gates remain open.
