# G1 real gameplay video draft 01 — actual result

9 October 2026. [Chinese review](G1_DEMO_DRAFT_RESULT_20261009_ZH.md).
The requested local annotated draft is complete. This is a review artifact,
not a passed Assignment3 video/stress/submission gate.

## Delivered recording

Local review directory:
`Assets/LocalShared/Deliverables/Assignment3/DemoDraft20261009`.
Open `Paris_G1_MVP_Draft_01.mp4`: **129.7seconds,1920x1080,30fps**, silent,
with burned-in English/Chinese explanations. Editable `NARRATION.md`, English
and Chinese SRT, ASS styling, edit/verification/delivery manifests accompany it.

The video uses actual OBS game-window recordings of the selected hud_v3.
Its executable SHA256 remains
`497221422d7754d562b4e6d11fd8cc50c9223e40b329b26c8c14391a98d1c42b`.
Input is the existing opt-in finite native observer plus owned manual probe
input. It performs simulated key presses, UE navigation, visible aim and real
weapon transactions. No teleports, fabricated resources/deaths, replacement
game imagery, speed-up or optical frame interpolation. Automated input and cuts
are disclosed on screen. The final9seconds are an explicit editorial backlog
card, not gameplay.

| Output range | Recorded content |
|---|---|
| 0–10s | Actual Ready screen, title and recording disclosure |
| 10–23.767s | Walk/sprint/slow walk, jump/landing, crouch and rejected unsafe prone |
| 23.767–32.6s | Prone on measured support, obstruction, reverse/stop; camera polish gap disclosed |
| 32.6–120.7s | Continuous original-speed G1 mission/checkpoint excerpt: reload, bridge travel, real shots/three guard deaths, unlocked circle, question/decline/re-entry, safe E confirmation, F9 fresh-world load |
| 120.7–129.7s | Editorial backlog: workload stress, performance target and teammate review |

## Cases, admission and recording provenance

Read HANDOFF, selected baseline/retirement records, Assignment3 requirements,
MI007–MI011 and current HUD/input/save results. Followed the
[bounded implementation plan](G1_DEMO_DRAFT_RECORDING_20261009.md).
The new route is **OBS32.2.2 specific-window WGC**, not any of the four stopped
capture routes. The user explicitly approved launching the updated OBS.
Unknown ownership, wrong/blank imagery, strict GPU/game error or failed game
transactions would stop recording; no capture-backend sweep was used.

Project-only profile/scene `ParisG1Demo20261009`: title-must-match/client-area,
cursor off, desktop/microphone sources disabled, NVENC CQP23/P5,MKV,1080p30.
The ordinary selected game runs foreground, with isolated UserDir/save prefix
and Python disabled. `-NoSound` means this draft has neither game audio nor
voiceover. Original OBS selections **Untitled/Untitled** were restored after
recording; OBS remains open and idle, no game/editor remains running.

The probe took35.866seconds rather than the planned10–15 because UI operation
latency delayed the stop. Actual early/middle/late frames and reload originals
were inspected: authentic Paris/HUD and2/16→8/10. A24–26second slice decoded60
frames with60 distinct hashes. This admitted the finite checkpoint/action clips.

Private raw MKVs under `tmp/g1-demo-draft-20261009/raw`:

| Identity/start EDT | Media duration | OBS output/drawn frames |
|---|---:|---:|
| Probe,18:53:40 | 35.866s | 1077/1094 |
| Checkpoint,18:56:03 | 136.866s | 4105/4122 |
| Actions,18:58:42 | 110.300s | 3308/3325 |

OBS reports no encoding/render-lag rows for these sessions; output/drawn totals
are recorded as observed and are not equated. Game logs contain no strict
GPU/fatal/assertion failures. Startup/equipment preparation and post-exit black
tails are excluded from the edit, with exact frame ranges retained in its manifest.
All raw bytes and OBS profile/scene/log provenance remain private and preserved.

## Observed game and media checks

- Checkpoint observer:111.504seconds,exit0. Three legitimate deaths from9shots/
  9hostile hits unlock the circle. Entry is a question with serial0; Esc/leave/
  re-entry cannot autosave, moving E is denied, stationary E produces serial1.
  F9 creates a fresh world and restores Won/serial1/ammunition7/2. Full restart
  restores Ready/3guards. Restart is in raw footage/receipts beyond the draft cut.
- Actions observer:67.839seconds,exit0. Measured walk/run/slow150/300/65cm/s,
  jump/land,crouch half-height60cm, prone half-height34cm and60cm/s crawl.
  Unsafe support/low-posture transactions are denied; forward travel36.9513cm
  then physical obstruction stops further travel (blocked drift0). Reverse/stop,
  standing reload conservation and one-round discharge pass their local gates.
  These are functional checks, not full animation/camera acceptance.
- The initial stationary separation check reports459.619cm minimum ally distance
  and0cm ally travel during that check. Captions identify the two-allied starting
  roster without claiming that this proves a complete follow/regroup sequence.
- Probe closed normally through owned Alt-F4; shutdown log/process absence
  checked, exit code not measured. Only the checkpoint/actions exit codes are0.
- Final MP4: **3891 decoded frames**,H264High level4.1,yuv420p/BT709,exact30Hz,
  MP4 timescale30000/sample duration1000;129.7seconds,faststart,no audio.
  Whole-file decode exit0/errors0 and final encode warning count0. Fourteen final
  representative frames/contact sheet and full-size caption/question views were
  inspected: readable captions/HUD, authentic game, no unrelated desktop content.

First export's concat timebase produces an x264 rate warning; the full export is
retained under `export_v1`. A pre-output option rejection is also retained. The
bounded correction fixes only export timing/metadata, preserves all3891 source
frames and the same cuts, and replaces unsupported "allies accompany" wording.
It does not retry the game or alter the footage's observed behavior.

Final file124,050,759bytes,SHA256:
`b90d98437e42734c87fea10237591c69e6fbedd05a848460b0c001fd6154222a`.
The local deliverable copy was independently size/SHA256 checked against output.

## Protection and remaining gates

Before/after canonical758/current703/selected40/executable checks match exactly;
user save/config/log file inventories are byte-identical. Models, finger poses,
animations and accepted weapon/resource/save rules are unchanged. No source/game
patch, recook, Editor entry, Git commit/push or external upload/submission occurred.

Preserve **both** `Assets/LocalShared/Deliverables/Assignment3/DemoDraft20261009`
and `tmp/g1-demo-draft-20261009` in future cleanup. The latter contains raw videos,
finite observer receipts/userdirs, before/after identities, OBS provenance,
composition/verification scripts and first-export warning evidence. Private
media stays outside Git. It is a new protected review artifact, not an obsolete
package folder.

This draft still lacks genuine NPC workload stress footage/readable stress
metrics and fuller AI interaction. Current selected-build60FPS, full-motion/
camera, human/teammate and final link/report/access gates remain open. A30fps
recording does not measure game FPS. No YouTube/Vimeo link exists, and historical
V13 performance is not relabelled as current HUD-build evidence.
