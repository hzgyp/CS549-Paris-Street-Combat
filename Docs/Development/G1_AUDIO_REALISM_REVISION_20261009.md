# G1 recorded Foley revision and recording hold

9 October 2026. Status: planned, not accepted. [中文复核](G1_AUDIO_REALISM_REVISION_20261009_ZH.md).

The user accepts the current gunshot, rejects the walking and reload sounds as
unrealistic, and reports a snapped about-face in the opening movement demonstration.
No new screen recording or demo export is authorized until the user manually
reviews and accepts the sound revision. Record the turn defect now; defer its fix.

## Cases read and what changes

Read AGENTS, HANDOFF, CURRENT_DEVELOPMENT_BASELINE JSON/MD, package-retirement
plan, CURRENT_LOCAL_REPAIR, MI012, MI013 and MI014. MI012/MI013 show that numerical
integration gates cannot establish player or presentation acceptance. MI014's
nonzero mixed audio and alignment checks prove playback, not acoustic realism.
New MI015 retains the human rejection and the synthetic audio/source/video.

Start from the exact 42-file AVv3 child and matching game49da3a2c…28ad9c.
Preserve parent HUDv3, original models, rigs, finger poses, weapon transactions,
HUD, save format, terminal corpse restore, all original user files and prior raw
recordings. The gunshot WAV, gain, timing and spatial treatment are protected.
Do not change gameplay, camera, navigation or native assets for sound selection.

Replace rejected tonal synthesis with licensed recordings of boots on hard ground
and an actual M1 Garand mechanism. Inspect the source recordings and the existing
reload footage before trimming. Keep source/license URLs, downloaded-byte hashes,
all edits and resulting WAV identities. Prefer a sound-data-only trial using the
same executable; a necessary event-timing/code change requires a separate bounded
source copy and Game build. Do not overwrite the old trial or its Audio directory.

## Early acceptance and manual review

Before authoring: authenticate 42 source files, AVv3 game, parent40 and approved
fire.wav; ensure no active user game/editor is being displaced. Freeze the rejected
sound files and relevant source/code locations in MI015's private evidence manifest.

Recorded samples must identify their physical origin and permit reuse. Match dry
boot contact/scuff to the hard Paris street, quieter slow movement and firmer run
contacts. Reload should contain actual metal handling/clip/bolt sounds aligned to
the retained original animation, without arbitrary pitched beeps or an invented
modern detachable-magazine sequence. Do not add a decorative ping to every reload.
Archive unselected downloaded references rather than claiming they are integrated.

Provide clean WAV listening examples and a separate normal playable entry, retaining
ordinary background muting. Check WAV format, clipping, cue duration versus original
reload timing, exact fire identity, and actual UE playback if source/runtime changes
are necessary. No OBS capture or demo re-export. The user's in-game listening review
is the perceptual gate; counters, licensing and waveform metrics alone cannot pass it.

## Recording defect and stopping conditions

The finite observer directly calls SetControlRotation in Move() and resets to zero
at prone arrival. Inspect the old footage/logs to locate the reported turn; direct
rotation is a credible cause, not proof of a normal mouse-input defect. Record the
future requirement: continuous visible turning driven by normal input, with an
appropriate turn presentation where supported by existing animations, no snapped
yaw or footage cut used to hide it. Do not implement or record this now.

Stop for uncertain license, unexplained background speech/shots in a proposed cue,
protected-byte drift, failed decode/build/playback or repeated GPU startup fault.
Do not keep synthesizing alternate tones to manufacture a realism pass. If suitable
recordings cannot be admitted, report the remaining source gap precisely. Keep all
failures. No commit/push/SFTP/video-host publication is part of this revision.

## Evidence-based timing addendum (before runtime authoring)

Existing raw action footage was extracted for inspection, not newly recorded.
It shows a roughly4.13s reload. The old audio fires its end sound at ammo commit
around2.066s, while hands continue the original animation. Therefore a data-only
replacement cannot fully correct event semantics. Author only the nonreflected
ParisGameplayAV.cpp helper in a separate exact42 copy: use recorded variations,
three phased presentation cues, and cancel reload voices when that actor leaves
Reloading/dies. Read existing per-actor reload timing/rate; no resource writes or
changes to animations/observer/headers/build/defaults/config. Preserve exact fire
code/settings and old helper. Recorded cloth, landing and body impact may replace
the other unapproved synthetic Foley with honestly labelled adapted recordings.
Never use M1-specific mechanisms on the German bolt-action rifle; source separately
or report that gap. Human acoustic/contact approval remains pending.
