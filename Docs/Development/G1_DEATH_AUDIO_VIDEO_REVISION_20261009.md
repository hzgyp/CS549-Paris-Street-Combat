# G1 checkpoint death presentation, gameplay audio and video revision

9 October 2026. User requests fixing restored death-animation replay, checking
missing footsteps/run/fire/death audio, then recording again with English text only.

## Cases read, diagnosis and bounded change

Read AGENTS/HANDOFF/current baseline JSON/MD/retirement plan, MI012,MI013,
MI007–MI011 and the latest real WGC video result. Old recording routes remain
stopped; draft01/raw/provenance remain protected. Start from the exact selected
40-file hud_v3 snapshot in a new owned private working copy. Preserve canonical758,
current703/native359, source40/active authoring, all models/fingers/rigs/materials/
animations and original weapon/resource/save transactions.

Confirmed source cause: ApplySnapshot calls PC_Die for a saved dead NPC; PC_Die
plays existing Rifle_Death_3 from its beginning. The save's dead flag is correct,
but load reuses the new-death presentation. Keep original lifecycle side effects,
then evaluate the existing death clip at its terminal frame without notifies and
stop playback, in the same restoration call. Fresh kills still play normal death.
Cover the fresh-world preparation phase with a brief runtime loading screen so
unrestored living actors are not presented as loaded checkpoint state.

Video01 was intentionally launched with -NoSound and OBS audio disabled. Remove
both recording restrictions. The user playtest log already shows a functioning
48kHz WASAPI output device; "Audio input will be silent" is microphone input,
not proof that playback is broken. Existing native/Blueprint-authoring paths
have no footstep/fire/death sound hook. Audit local candidate sound assets before
adding anything; never claim a name/header scan is a complete AssetRegistry audit.

Add a small native presentation-only audio layer for actual displacement on
supported ground, accepted ShotSequence increments and genuine alive→dead
transitions; also standing reload/landing when supported. It never writes game
health/ammo/death, moves a character or changes the original animation graph.
Prime tracking only after initialization/restoration: load is not a new shot,
footstep or death. Stop voices and release state on world cleanup/restart.
Use compatible existing local sound assets if available; otherwise bounded
original synthesized PCM cues, with generator/provenance and explicit first-pass
quality limitations. No purchase, commercial audio scrape or character creation.
Runtime PCM sidecars avoid editing original UE assets or changing the save schema.

## Early acceptance and stopping condition

Before any mutation, source40/758/703/native359/current game and user-save
inventories must match; no user game/editor/build process may be active. Freeze
baseline references. Only the new owned working Project/executable/sidecars may
change. Build a Game executable from the selected snapshot; no cached Editor
entry. Reuse the authenticated hud_v3 cooked payload only if no reflected
schema/defaults/config/native dependency change requires recooking.

First gate: real packaged Ready with the original HUD/gun/resources, an active
audio output device, and audible/sampled actual accepted discharge and grounded
steps. Check ordinary idle, key release and airborne/blocked motion do not invent
steps; rejected actions produce no accepted-shot audio. Read actual sound data,
not just event counters. Stop on startup/GPU/dependency/game transaction error,
wrong pose, silent/clipped/misrouted audio or unrelated capture content. Preserve
the negative; no offset/finger/capture-backend retry or threshold relaxation.

## Integrated acceptance, delivery and recording

Run the existing finite action/legitimate checkpoint observer with new read-only
presentation witnesses. New deaths retain the original moving clip and one
death cue. From the first restored playable frame through at least3seconds,
each saved-dead German must be at the same terminal clip/time, stopped, health0,
collision/movement disabled and brain gated. No repeated death/fire cues; old
V5 journal compatibility, resources/ledger/consent/F9/F6 remain checked. Record
pose/resource witnesses and actual audio mix/OBS audio samples. Use isolated
UserDir/prefixes and preserve the user's journal and previous video.

After those gates, use admitted OBS WGC again, with game-process audio only,
microphone/desktop audio off. Review one finite audiovisual probe before full
capture; require real content/motion and nonzero matching audio, no other app
sound. Restore original OBS selection after work. New video stays2–3minutes,
1x, with disclosed automated input/cuts and **English-only burned-in text**.
Retain raw MKV, media timing/audio/decoded-frame checks, editable English SRT/
narration/edit manifest and private provenance. No fake audio laid over silent
game footage. Existing missing stress/performance/course gates remain disclosed.
Deliver a new fixed playable folder and draft02 without replacing the selected
old trial, saves or protected raw footage. No Git push or external upload requested.

Primary API reference: [USoundWaveProcedural](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/USoundWaveProcedural),
checked against installed UE5.8 headers/source; installed AnimSingleNodeInstance
SetPosition/SetPlaying semantics govern no-notify terminal evaluation.

## Read-only asset scan and preparation

The bounded first128KiB class-name scan covered16,722 local uassets, including
Content junctions. Only generic BP_SoundParent and Empty cue references were
found; no SoundWave/MetaSoundSource candidate. The installed FirstPerson feature
pack name listing also shows no audio sample entry. This is not a full registry
proof, but no compatible local footstep/fire/death cue was identified. Use the
documented original deterministic first-pass cues; no borrowed recording or voice.

New candidate_v1 is an independent42-file Project (selected40 plus two nonreflected
helpers). Only mission cpp, finite-observer cpp and module dependencies change;
AudioMixer is added for native sound output/mix-only diagnostic recording.
All39 original non-descriptor source/config files and descriptor were authenticated
before copying; canonical758/current703/native359 and old Game identity pass.
Forty-seven retained hud_v3 Archive rows are frozen for reuse. No native assets or
save schema/defaults/config change; Game build only, no cook/Editor entry.

## V1 compile negative and bounded V2 correction

The new helper's two diagnostic Serialize calls incorrectly apply ToSharedRef to
an already-shared reference, producing C2039/C2672. Compilation stops before any
Game entry/archive/capture. Freeze all42 failed source files and retain log/receipt.
Distinct candidate_v2 changes exactly those two calls to use the existing shared
reference directly. Reuse the owned working Project/build cache, with a new
authenticated preparation/build identity. No gameplay, audio data, schema, pose
threshold or original asset changes. All runtime/audio/corpse gates remain.

## First runtime negative: background output hypothesis

The finite checkpoint transaction/corpse checks pass, but its actual exported
master mix is all zero. Do not admit this run as audio/video acceptance. The
game was behind OBS and a Windows Firewall prompt; installed BaseEngine.ini
sets Audio.UnfocusedVolumeMultiplier=0.0. Keep the run/result/silent WAV/source.
Next diagnostic uses the separate actions identity with the actual game
foreground after initialization. Require nonzero unclipped actual mix under
the same thresholds; no sound/gain/capture-backend compensation. Focus is a
hypothesis until actual output passes. Three distant death sounds also return
null AudioComponents; inspect the engine's audibility culling before treating
this as a playback defect. Short loaded/restarted generations export no mix
data, so counters alone cannot establish their audio silence.

## Bounded V3 completion

After restarting the window-control kernel, foreground actions produce actual
48kHz stereo output (peak0.198761, RMS0.003221, no clipped sample). The background
run remains an audio negative. Keep the game foreground for the next probe and
recording; retain the project's normal mute-on-focus-loss behavior. Engine source
confirms short out-of-range sounds return null components. V3 separates footsteps
(23.4m maximum) from death equipment impact (61.2m maximum, distance attenuated),
skips outside-range cues before component creation, and records the original
death clip/time/play state on genuine new deaths. No sample/gain change.

Add an opt-in legacy observer that uses F9 to load a copied, unmodified original
HUDv3 V5 journal in an isolated directory, reusing the same terminal corpse gates.
Freeze V2's42 source files and executable/receipts; distinct V3 source/build/run.
Require foreground actual audio for steps/run/fire/death/reload, unchanged input
and checkpoint checks, ordinary fresh death playing, and old-journal restore.
Then an OBS game-audio-only probe must pass actual video/audio decoding and
event alignment before full draft02 capture. No other asset/schema changes.

The new executable receives another Windows Firewall prompt despite UDP
messaging being disabled. The permission UI is never automated. Its blocking
focus makes the first V3 runtime an additional audio negative, while numerical
checkpoint/corpse checks still pass. A recording/probe process may explicitly
use UE's per-process Engine [Audio] UnfocusedVolumeMultiplier=1.0 override so
OBS controls or that prompt do not silence actual game output. This is a
disclosed recording-context setting, not added/postproduced audio or an asset
fix; the delivered normal game retains default focus-loss muting. Keep the
same real mixed-audio/cue/transaction gates and preserve both background
negatives. Security permissions remain unchanged by our automation.

## OBS probe admission and fresh startup negative

The actual OBS probe passes full audiovisual decode, reviewed Ready/movement/
jump/fire frames and nonzero walking/running/fire audio. Its captured gun cue
matches the in-game cue with correlation0.9843 and delay0.1452s. The first full
checkpoint capture then fails at rendering frame2 before Ready: D3D12 device
removed, Aftermath MMU page fault, owned Game exit3. Local GPU use4,871.56MB is
below9,285MB budget; this log does not establish exhaustion or an audio defect.
Retain the original case and MKV as a failed identity. MI009/MI010 are re-read;
this attempt uses OBS WGC and has no custom viewport-readback callback. One
separate fresh process/case under identical admitted settings is permitted;
require Ready, original checkpoint gates, full AV decode and normal exit0.
Stop that recovery route if the same startup GPU fault repeats; do not lower
acceptance gates or claim the failed capture as a playable/video pass.

The admitted probe itself completes the whole finite actions test, exit0.
Reuse its real movement/prone frames and captured sound for the action excerpts,
with an explicit case/source alias in the edit manifest. No duplicate action
run is needed after those functional/audio/media gates pass. Capture the fresh
checkpoint mission separately and disclose all cuts and automated controls.

The broad0.4s audio-template/plus-minus0.5s matcher selects stronger neighboring
shots spaced0.30s apart, falsely reporting0.43s lag. Preserve its failed script/
diagnostic receipt. Actual recorded frames show first discharge/ammo change
by event+0.1s. A distinct assessment uses the initial0.16s gun transient and
the unchanged positive-latency<0.3s/correlation>0.5 gates, giving all9 gun
matches0.126-0.145s. Original-template subtraction is assessment-only to
distinguish simultaneous death impact; the first quiet impact's0.2-0.5s tail
passes0.9066, other impacts' full matches0.5548/0.7871. Raw and edited audio
remain exactly captured; no soundtrack subtraction, gain or sync shift is used.
The restored segment is actually zero PCM, beyond counters alone.

First draft02 export incorrectly scopes enc_time_base1:30 to all streams,
including AAC, and logs2,177 backward-input queue warnings. Reject and retain
the whole export/script in export_v1 (SHA7ece4256…f2a212e). Correct only option
scope to enc_time_base:v, preserving source frames, cuts, captions and actual
captured audio; AAC keeps its48000Hz sample clock. Re-export into a fresh output
identity. Require zero encode warnings, exact3869/30Hz video duration and complete
audio/video decode, then visual review and independently hashed delivery.
