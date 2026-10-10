# Player foot contact, jump and recorded M1 audio result

9 October 2026. Game-only implementation built and scoped native checks passed.
Revised human cadence/jump/report approval is pending, recording HOLD.
The user reports the previous recorded Foley is substantially better, with minor
remaining player step mismatch and absent jump feedback. This qualifies that
parent review; it does not establish full acoustic or course acceptance. The user
explicitly authorizes replacing the prior protected synthetic firing cue with
real firearm recordings where a suitable reusable source exists.

The final measured source is candidate_v2, Game
`53ab36d9da1975a2f8e1109fcf6745cc40e96d371fc89fbfa009139b91950aec`.
It extends exact42 recorded-Foley source by ParisGameplayAV.cpp only. Original
models, skeletons, fingers, animation clips, camera, NPC behavior/navigation, HUD,
weapon/ammunition transactions, save schema and stopped saved-death restoration
are retained. ReloadAudio and RestoreTerminalDeath implementations remain exact.
No Editor compilation/entry, native asset save, recook or publication occurred.

Player walking/running/slow/crouch sounds now read the evaluated foot_l/foot_r
pose. A descending foot reaching its low phase emits one contact; it must lift
from its subsequent lowest height and separate above the other foot before it
can emit again. Ground/movement/teleport/air/posture/reload gates remain. This
avoids the v1 heel/toe double event while keeping animation-driven cadence rather
than a distance or timer loop. NPC and crawl policies stay scoped to their prior
implementation. A joint low phase does not prove physical sole-floor contact,
repair foot sliding or replace human timing review.

Actual grounded-to-airborne upward motion triggers a boot/cloth takeoff cue,
gain.65, rather than firing from Space input alone. A rejected request and an
ordinary falling ledge do not trigger it. The existing grounded landing edge
retains its recorded boot contacts at gain.85. Player walking impacts are gated
out in air. The takeoff sample adapts boot release/scuff and coat rustle, not a
dedicated recorded military jump or invented vocal effort.

Player and Allied reports use [MPierluissi's M1 live-fire field recording](https://freesound.org/people/MPierluissi/sounds/460851/),
CC0. This is actual live firing, distinct from the dry-fire/handling files in
the same pack. Official HQ MP3 SHA c20d06db…c6f83f, decoded mono48k PCM; first shot
.195–.780s gives one.585s cue, bounded peak.60, DC removal and1ms/12ms fades.
There is no pitch/time synthesis, no whole eight-shot burst and no extra empty
clip ping on each round. The indoor recording retains its natural room tail;
it is not a Paris outdoor capture or the original lossless master. One source
first-shot full-scale PCM sample is retained in provenance diagnosis; output
has no full-scale clipping. Successful ShotSequence gating and spatial
attenuation remain; no new damage/ammo behavior is introduced.

Exact freely reusable K98 live firing was not established by the bounded search.
German reports retain the original fire.wav, explicitly a gap; M1, Mauser pistol,
modern.308, reload/dry fire and paid previews were not mislabeled as K98. Existing
31 WAV identities remain exact; fire_m1 and jump make33. Reload, crawl and impact
source credits from the parent remain. Audio bytes are private with the trial;
source/rights/trim/gain/hashes are in AUDIO_MANIFEST and Audio/PROVENANCE/CREDITS.

The initial instrumented candidate d889ff5c passes original actions and legacy
terminal checks, but its viewed foot graph exposes two minima from one planted
roll. It is stopped, not delivered. Its initial complete jump template match
.364 and land.782 are contaminated by NPC footfall overlap; M1.999999 is already
present. Preserve the negative verifier/mix and first graph. The distinct measured
candidate adds the foot latch and audit-only SoloPlayer isolation, which is
effective only with an explicit audit output directory. Normal NPC playback and
normal background muting remain unchanged. This diagnoses actual cue output;
isolated diagnostic playback does not certify human audibility in normal combat.

Finite checks reuse the original native input observer, isolated test UserDirs
and diagnostic WAV output. They create no new screen video and do not correct
the documented abrupt camera turn. Original models and accepted gestures are
not driven by Python. MI016 also retains intake's common-module import failure
before protected mutation and plotv1's missing matplotlib; explicit guard-module
loading and local plotting dependencies repair these diagnostics.

Normal review entry after completion:
`tmp/Playtest-G1-Foley-V2-20261009/PLAY_G1_REVISION.cmd`. New normal UserDir
`%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestFoleyV220261009`, unchangedV5 prefix.
Normal launcher must be independent and have no observer, audio audit, solo flag,
NoSound or background override. Listen contains source examples, not a captured
game soundtrack. Source snapshot: `Unreal/Variants/G1FootContactAudio20261009/Project`;
authoring/evidence: `tmp/g1-foot-contact-audio-v2-20261009/candidate_v2/Project`.
Preserve that Content junction and both authoring candidates despite their names.

Final actions PID9660 exits0:6169 pose samples,29 player contact events;20 stable
gait contacts independently meet the original3cm/descent bounds (maximum residual
1.208093cm). Nine acceleration/blend-transition contacts are explicitly UNASSESSED,
not passed. The raw walking minimum comparison negative and two over-filtering
verifier negatives remain. Association/scoping changes do not alter Game53ab36d9
or rerun input; full transition timing still needs human review. Viewed final
walk/run/slow graph shows the planted-roll duplicate removed.

Takeoff occurs at29.091634s, upward349.841714cm/s, and landing29.877898s; one each,
no airborne player walking impact. Actual solo-native waveform correlations:
M1.999999483, jump.999996316, land.999996294, reload insertion.999936019.
This establishes actual playback, not normal-mix audibility or realism. Diagnostic
mix18.090667s/48k stereo/peak.152893/no clipping is shorter than the~80s wall-clock
test and is not a full gameplay soundtrack. Original reload2/16->8/10 preserves18
total rounds; open/insertion/close at.585044/2.060858/2.819432s after start; accepted
shot consumes exactly one. Existing source C4701 validation warning is unchanged.

Legacy PID41456 exits0: exact oldV5 journal and3 saved corpses remain stopped at
original3.933333s death end, health0/collisionoff/brainoff. First and3-second audio
snapshots have0events/voices; final restored events are also empty. Silent worlds
yield no diagnostic WAV; that is a scoped quiet restore, not a missing game cue.

Read the completed verification/completion JSON for actual outcomes. Foot-contact
plots show sampled existing animation and actual sound edges, not render/contact
acceptance. Human timing/timbre, exact K98 source, NPC/crawl/body contact/active
reload interruption, natural turn, performance/stress/teammate/course gates remain
separate. No OBS, new MKV/MP4, video export, Git commit/push or SFTP upload. The
earlier footage/source/trials and original saves remain protected. New recording
requires manual revised sound approval and correction of natural turning first.
