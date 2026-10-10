# G1 recording 03 implementation

9 October 2026. Execution plan; results are not yet established. The user selects
A / Michael (`am_michael`), authorizes recording script03 with English subtitles
and narration, and explicitly permits an independent native input assistant after
the available computer-use API proved unable to hold keys. This replaces the
manual-input sentence of the reviewed script only. Automated input is disclosed.

## Baseline and protected scope

Start from the selected exact42 audioV2 source and Game53ab36d9…950aec. Keep the
normal trial, authoring Project, native assets, models, fingers, animation, camera
parameters, HUD, weapons/ammunition, AI and V5 save/dead-restore logic unchanged.
Create a separate private recording Project/build using the existing cooked
closure. Only a new opt-in input helper and its module startup/shutdown wiring
may differ. No reflected class/schema change, recook or Editor save. Existing
user saves remain untouched; each recording entry uses its own private UserDir.

## Failures read and changed mechanism

Read AGENTS, HANDOFF, current baseline/audio selectors, script03 and failure index,
MI007–MI011 and MI014–MI016. MI015's old ParisUXTest director remains retired for
recording: never call SetControlRotation, set actor transforms, or hide a snap
with a cut. The new helper feeds ordinary held/released keys and bounded
AddYawInput/AddPitchInput per frame. UE navigation provides read-only waypoints;
movement itself is normal W/Shift movement and collision. A turn remains visible.
It reads state for timing but never writes health, ammo, death, AI, mission state,
poses or equipment. It may observe authentic target visibility to steer gradually.

MI014 requires actual process sound and stopped corpses after F9. MI016 requires
the accepted V2 sounds, with no replacement Foley in editing. The independent
Kokoro Michael narration stem is labelled AI, leaving original game-sound windows.
MI008–MI011 permit only admitted OBS specific-window WGC; no stopped internal
readback/GDI route. MI007 forbids 30fps media as proof of 60FPS gameplay. This
review draft keeps current-build stress explicitly pending.

## Workflow and early acceptance

1. Freeze source/executable/audio/protected-save identities and original idle OBS
   selection. Prepare separate input helper, finite deadline and telemetry.
2. Compile Game only, inspect source diff against exact42. Admit a10–15s real OBS
   AV probe: physical movement, continuous turn, shot, jump/land; inspect frames,
   actual sound, HUD and heading telemetry before the full take.
3. Record actions, squad bridge transit, original combat, final kill→gold circle→
   explicit E save, changed ammo→F9→restored ammo and≥3s terminal-corpse view.
4. Record a separate fresh run: actual enemy hits→HP0→player death→MISSION LOST
   hold≥2s→F6 actual loading→fresh Ready. Never inject damage, disable Allies or
   fake this with a victory restart. From first visible damage through Ready,
   retain continuous1x footage. Only earlier travel may be a declared cut.
5. Align concise Michael narration and English subtitles to witnessed events.
   Compose2–3min at1x with declared cuts, preserve captured game audio and loading.
   Full decode, representative frame review and state/timeline audit, then show
   the local MP4. Restore OBS selection/idle and close only owned games normally.

## Stopping condition

Stop on first strict GPU/startup failure, unknown ownership, snap/blank/wrong
content, missing/clipped/misaligned audio, blocked route, missing squad transit,
unwitnessed combat/save/load/death/restart, or protected-byte drift. Retain the
failed identity/raw/logs and explain it; no gameplay cheats or parameter sweep.
Any genuine rehearsal defect requires a separate bounded correction before its
shot. The mandatory defeat chain may require budget changes to the script;
optional pauses go first. No video upload, Git push or new gameplay selection.

Private evidence: `tmp/g1-demo-draft03-20261009`. Deliverable directory:
`Assets/LocalShared/Deliverables/Assignment3/DemoDraft03_20261009`.

Pre-capture source review: PC_ActionCrouch toggles posture on press; release alone
does not stand. The new input template now includes the ordinary second Ctrl tap.
The first compiled recording_v1 source/build is retained before this correction
and has not received GO or made gameplay inputs. Compile a distinct corrected
identity before capturing actions. At23:42EDT the owned PID55960 entry reaches
Ready, then shows a Windows Security network-permission dialog; user manual
Cancel is required by computer-use guidance. OBS is idle, no footage exists yet.
The owned pre-input entry was stopped at23:45EDT/exit−1 for the preflight source
correction, not a crash or user preview. Its source/executable/logs and absence
of GO remain recorded. The corrected44-row recording_v2 is separate: second Ctrl,
read-only original muzzle-clear checks and input deadline starting only at GO.
Its prepare receipt initially failed after source copy because the argparse
namespace was shadowed by a PowerShell command string. Retain prepare_failed.py;
the corrected receipt verifies parent42/normal88/user3 without repeated authoring.
Original selected Game, sound/assets and user saves remain protected.

At23:53EDT recording_v3 compiles successfully, Gamefb93cda3…921e, with a normal
0.2s Space hold before release. v2 source44 snapshot and executable are retained;
the same private authoring Project now carries v3, with exact44 frozen rows in
recording_v3_prepare.json. New owned PID54708/actions_probe_v3 reaches Ready and
all33 audio cues are primed, but Windows Security again blocks the window. GO is
absent, OBS idle, no new raw/video yet. Wait for manual Cancel; actual helper
behavior/turn/audio/defeat acceptance is still unperformed.8Michael stems ready.

## 10 October actual probe and bounded startup recovery

The user manually cancelled security. PID54708 exits0 after ordinary input.
Actual OBS08:08:54 MKV decodes; eight action frames were reviewed. Jump/land,
crouch/stand, conserved2/16->8/10 and7/10 shot pass. Maximum sampled yaw rate
30.763deg/s; captured walk/run/jump/reload/fire have nonzero audio, peak0.1524.
No subjective realism/listening or complete animation/FPS claim follows.
Overnight waiting produced562,748 Ready samples; preserve the749MB raw receipt,
derive input_window.json without deleting it. Extra serialization tail is excluded
from the editorial take, never used to hide a turn.

victory_v3/PID25868 exits3 before Ready/GO/OBS. D3D12 frame2 reports
DXGI_ERROR_DEVICE_HUNG and Aftermath page fault;4,873.81MB used/9,285MB budget
does not establish exhaustion. Exact cause is unresolved. Read MI014's matching
startup negative and documented single fresh-entry recovery. Freeze this case.
This separate recovery changes only entry/process/UserDir identity, with identical
Gamefb93/settings/assets. One new victory_fresh_v3 is permitted within this plan.
Early acceptance: Ready with no GPU errors and correct full client/audio before GO.
Stopping condition: a repeated startup GPU fault stops this route; no automatic
graphics setting/driver/capture change or retry sweep. This is not a stopped
MI008-MI011 capture rerun. Current final mission/death video remains pending.

### Bounded correction: victory reload input omission

victory_fresh_v3 reaches Ready without GPU fault, then fails the strict ammo gate:
its intro selected step_reload but never sent R. Original2/16 remains unchanged;
actions_probe_v3 already proves the original reload works. Preserve result/raw/log
and exact44 v3 source before authoring v4. Read MI015 input-snap and MI014 failed
transaction cases again. Change only this recording victory branch: one-second
standing reload_start, ordinary R tap, then the original nine-second reload wait.
No gun/ammo/save/AI/asset logic changes. Early gate:2/16->8/10 actually observed,
then physical route; stop on failed ammo gate or route, retain its evidence, no
state injection. All other v3 helper operations are byte-identical in v4.

### Bounded physical-input correction V5

Actual v4 reload passes. At bridge feet4039.774/-20767.106/110.216, movement
stalls; raw/native are preserved. Its3 early long-range shots killed one guard
before any enemy shot, so this is not admitted reaction/combat footage. The
helper repeatedly switches between route and muzzle-clear aim while sight is
available outside the original2000cm NPC sight range (read existing B1 sight
author source). Do not blame or modify formal nav/AI/assets based on this fixture.

Read MI017/MI014/MI015 and the original mission centreline source. A separate V5
helper waits to engage until1800cm, aims continuously before the muzzle test,
uses15cm corner tolerance rather than65cm and records exact path/corner/target
data. Physical W/Shift remains; no SimpleMove/direct rotation/teleport or
collision change. A midpoint continuous look-back/return (28deg/s) shows actual
following Allies before entering enemy range; no skipped turn. Before saving,
look continuously toward an actual nearby dead guard to make terminal restore
visible. No animation/health/ammo/AI/save writes. Early acceptance is travel past
the actual4039 obstruction, then observed living enemy reaction, squad transit
and safe checkpoint. Stop the V5 route on another stall or missing mandatory
evidence; retain it, no automatic compensating-jump or tolerance/offset sweep.

The recording executable may use the same private runtime path after retaining
the entire old executable/source identity separately. This avoids repeated new
program-path prompts without changing network permissions. A recorded remapping
must identify both hashes; historical V4 launch receipt is not a current-path
hash claim. Normal selected playable remains untouched.

RecordAudio is an explicit recording-launch-only switch, reusing MI014's admitted
`-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0`. V4 GO was mistakenly issued
after sky activation reported user input and the game was initially unfocused;
this take is already rejected. Prevent monitoring/remote UI focus from silencing
genuine game cues while still requiring a fresh actual game view before GO.
Normal launcher/source/cues/focus-loss mute remain unchanged. No soundtrack Foley
is supplied in editing; OBS still captures only this game's process audio.

### V5 stopped; bounded V6 input-lifecycle and reaction correction

At08:31:19 V5 fails its route gate after actual bridge transit/three kills/Won.
Exact route telemetry places the final feet6745.826/-20278.959,341.8cm from G1,
outside the180cm save circle. Source review finds GateBrains(false) at Won
flushes PlayerInput pressed keys, then resets move/look ignore flags. The helper
still marks W held and never presses it again. This provides a specific input
lifecycle explanation; a physical corpse obstruction is not established.
All five NPC ShotSequence maxima are0. The retained autonomous-combat author
uses1200cm fire admission, so1800cm sight/recording aim is insufficient reaction
framing. Guard positions change, but this is not enemy-fire evidence.

Read MI017, MI014/MI015, selected original ParisBridgeMission.cpp and retained
NPCInteractionV1/ue_autonomous_combat_author.py. Preserve V5 binary/source44/raw,
do not rerun its failed route. Separate V6 changes only recording input: on the
first actual Won while routing, release the helper's held keys and allow its
next normal W/Shift press; no controller ignore/mission mutation. Retain V5's
physical route and combat range/timing. Separate defeat_v5 already actually
shows enemy shots reducing100->65->30->0, Lost4s and F6/new Ready; native checks
pass, actual AV/frames need admission. Use this real enemy-fire evidence with
the victory take's visible pursuit, rather than introducing another combat
setting. Early gate: Won followed by real movement into the unchanged circle.
Stop on new stall, failed consent/save/restore or resource/protection gate. No
automatic further range, offset, jump or game-state compensation.
