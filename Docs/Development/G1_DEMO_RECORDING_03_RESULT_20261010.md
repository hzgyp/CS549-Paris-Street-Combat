# G1 recording03 — actual result

10 October2026,08:51EDT. **Complete local review draft; human video/listening
review pending.** User authorized script03, A/Michael English narration, English
subtitles, genuine player death/restart, and a separate ordinary UE input helper.
See [implementation](G1_DEMO_RECORDING_03_20261009.md),
[reviewed script](G1_DEMO_SCRIPT_03_20261009.md) and
[MI017](../../Failures/MI017-20261010-demo-input/FAILURE_ANALYSIS.md).

## Delivery and verification

Local private delivery:
`Assets/LocalShared/Deliverables/Assignment3/DemoDraft03_20261009/Paris_G1_MVP_Draft_03.mp4`.
Duration161.433s (2:41),1920x1080,30fps/4843frames,H264/AAC48k stereo,
159,488,458bytes. SHA256:
`c0044c69776d153f4db34535fdc0942207ef9b5153d2d418e6aca029b1a122ca`.
Companion files: English.ass (burned source), English.srt (editable),
AI_Michael.wav, TIMELINE.json, QA/result.json and render/decode/loudness logs.
The earlier41.83s actions-only preview is superseded for delivery, retained as
evidence. No public video link, SFTP transfer or Git publication occurred.

Full AV decode with strict error handling exits0. All14 extracted final-caption
frames were inspected: text is readable, at most two lines, preserves the native
health/ammo/minimap/save prompt. Decoded peak0.719119; measured final mix
−18.39LUFS/−2.86dBTP; eight voiced windows have nonzero audio. Numeric checks
and representative frames do not establish subjective listening/full-motion
or human video approval. Do not interpret30fps export as gameplay performance.

## Actual content and edit boundaries

| Final interval | Included actual evidence |
| --- | --- |
| 0:00–0:41.83 | Walk150/run300/quiet65cm/s, jump/land, crouch/stand, prone clearance, conserved2/16→8/10 reload and7/10 shot; continuous gradual turns. |
| 0:41.83–2:04.33 | Separate victory run: physical bridge travel, both following Allies, pursuing guards, three eliminated, gold circle/prompt, E save, later shot, F9 and terminal corpses. Repeated initial Ready/reload omitted. |
| 2:04.33–2:11.13 | Separate fresh defeat run, Ready/Enter. |
| 2:11.13–2:33.93 | Earlier approach cut before first hit. From first damage through Lost/F6/fresh Ready remains continuous. |
| 2:33.93–2:41.43 | Same fresh Ready tail; remaining stress/teammate work labelled pending. |

Each clip runs at1x; automated normal UE input and AI narration are disclosed.
There are no teleports, direct actor/camera rotations, health/ammo/death/AI/pose
writes or replaced game Foley. The input helper follows read-only UE navigation
waypoints with held/released ordinary keys and gradual yaw/pitch. A/Michael is
stock Kokoro `am_michael`, eight separately generated and normalized English
stems. Original process sound is mixed at1.8 gain in unvoiced and0.8 in voiced
windows; no added music. Real turning and transaction intervals are retained.

Prone is not a false traversal pass: ProneBlocked remains false, a short actual
forward movement then stops at rubble; caption states this collision limitation.
The victory guards pursue but their shot maxima remain0. Genuine enemy fire is
demonstrated by the separate defeat take, not claimed for this victory run.

At1:39.19 the checkpoint prompt appears; actual E is1:42.21 and save completes
1:45.21, serial1,7 loaded/2 reserve/100health. One later ordinary shot changes
7→6 at1:47.72; F9 at1:49.72 restores7/2/100 at1:58.54. The full8.821s blocking
load remains, followed by about5.79s observation. Early/+3s restore frames show
all three corpses already in terminal pose, no repeated fall/death audio. Early
environment streaming is visibly retained and resolves; not mistaken for corpse
animation or hidden by a cut.

At2:13.13 real German fire changes100→65, then30→0/Lost at2:15.80. Two Germans
have shot sequences2/1; player fires0. Lost is held4.003s; F6 at2:19.80 produces
new Ready at2:28.14 with100health,2/16 ammo,2Allies,3guards and reset checkpoint.
The entire8.336s real restart interval remains; WGC holds the old rendered Lost
view while the original game blocks. No invented loading screen.

## Identities, protection and failure closeout

Private evidence root: `tmp/g1-demo-draft03-20261009`. Admitted actual AV/native
receipts are under each case's `av_audit/admission.json`:

- actions_probe_v3/PID54708, exit0: raw08:08:54,
  SHA2d7a9224f651f890e228a4e961c4d3690853c5efdbbd05ba69c91a8406c446d3.
- defeat_v5/PID35876, exit0: raw08:33:02,
  SHA07aa8ce2142835f6c417d4487279a6be6ab167160f40db22a9f272630bda3740.
- victory_v6/PID25812, exit0 at08:43:09: raw08:37:56,
  SHAf8689c7fb3cb0f9e715e4c3cae61ee017e84916b87beb5100fadf7b8dffa847f.

V1 pre-input stop, prepare namespace failure, V3 pre-Ready D3D12 page fault,
freshV3 missing R, V4 route/activation failure and V5 Won key-flush failure are
retained in MI017/MANIFEST.json and private evidence. They are excluded from the
final video. GPU fault cause remains unresolved; later Ready is not a GPU fix.
V6 only resynchronizes its own held-key ledger after actual original Won flush;
route/range/game rules remain V5. No automatic parameter sweep.

V6 Gamea6015c94fd91fb73732d4ea18316ba80754d6de0e5d369a16e7e5725c9799472,
compiled Game-only exit0. Exact44 source is frozen in
recording_v6/compiled_source_snapshot. Old-named recording_v2/Project currently
contains V6 authoring. Stable recording_v4/Archive currently executes V6;
runtime_remap_v6 retains previous V5 Game/source. Historical paths alone do not
identify current bytes. All normal88 closure bytes are reused/exact; no recook,
native asset/Editor save or formal baseline change.

protection_final_20261010.json passes45 rows (selected42 source plus3 existing
normal user files/config/log, not three save journals), exact normal user file
set and normal Game53ab36d9da1975a2f8e1109fcf6745cc40e96d371fc89fbfa009139b91950aec.
Models/fingers/weapons/HUD/resources/AI/save logic stay unchanged. Each take
uses a private UserDir. Victory's actual ParisG1PlaytestV5_A.sav exists. Defeat
started without a journal, so preservation of an existing journal across F6 was
not runtime-retested. Original restart source performs OpenLevel without save
deletion; this source observation is distinct from a runtime preservation test.

All owned engines closed; OBS42432 is idle and restored to original Untitled
profile/Untitled scene collection, remains open. Preserve all evidence/source/
raw/normalized narration/delivery and MI017 references during later cleanup.
Current-build stress/FPS/second-machine, human video/listening acceptance,
course submission/upload gates remain pending. This is the requested review
draft, not Assignment3 completion.
