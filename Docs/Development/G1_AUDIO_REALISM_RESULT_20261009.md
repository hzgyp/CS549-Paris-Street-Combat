# Recorded Foley review candidate

9 October2026. [中文复核](G1_AUDIO_REALISM_RESULT_20261009_ZH.md).
Status: implemented, Game compiled and scoped native playback checked;
**manual acoustic acceptance pending / new screen recording HOLD**.
Read the paired implementation plan, MI015 and CURRENT_AUDIO_REVIEW.json.

The rejected synthetic footsteps and reload clicks have been replaced by adapted
field recordings. This is a concrete separate listening/playtest candidate; it
does not assert that the user has accepted realism. The approved gunshot WAV,
trigger, gain and spatial settings are exact, and the selected models, finger
poses, HUD, weapon/ammunition/save rules and terminal saved-corpse restore remain.

## Delivered change and provenance

- Normal entry: `tmp/Playtest-G1-Foley-20261009/PLAY_G1_REVISION.cmd`.
  Its91-file closure has the same cooked/native inputs, a new Game and31 mono
  48kHz/16-bit WAV cues with credits/provenance, plus separate listening examples.
  No test observer/audio-audit/background-volume override in this normal launcher.
  Save prefix remains ParisG1PlaytestV5, with isolated normal UserDir
  `%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestFoley20261009`.
- Six recorded hard-ground takes per walk/run/slow mode replace the two-tone
  alternation; slower movement is quieter, running firmer. Distance/grounded
  movement gates remain. Cloth movement, adapted two-boot landing and recorded
  dirt body impact replace other unapproved synthetic cues. These are Foley
  adaptations, not a claim of recorded WWII boots/uniforms or human death voice.
- M1 and German K98 have separate recorded mechanism cues. Reload handling begins
  on the existing accepted action, opening at14% of its rate-aware duration,
  loading on the existing ammo commit, closure at68% after commit. Original ammo
  writes/action timing/animation stay exact. Leaving reload/death stops that actor's
  reload voices with a short fade; world cleanup still releases all voices.
  No decorative clip-eject ping was added to every reload or last shot.
- Exact42 source: `Unreal/Variants/G1RecordedFoley20261009/Project`.
  Only ParisGameplayAV.cpp differs from AVv3. Its public SOURCE_MANIFEST and
  AUDIO_MANIFEST record identities; authoring is
  `tmp/g1-recorded-foley-20261009/candidate_v1/Project`. No Editor build/entry,
  recook, native asset save, reflected header/default/config/observer changes.

Sources were verified on primary CC0 pages and their explicitly published HQ MP3
references were acquired. Original uncompressed WAVs were not downloaded; converting
MP3 to PCM does not restore master fidelity. All edits/hashes/licenses are recorded:
[Fission9 boot contacts](https://freesound.org/people/Fission9/sounds/521590/),
[Vrymaa walk/run](https://freesound.org/people/Vrymaa/sounds/770084/),
[MPierluissi M1 pull](https://freesound.org/people/MPierluissi/sounds/460857/),
[M1 reload](https://freesound.org/people/MPierluissi/sounds/460855/),
[M1 release](https://freesound.org/people/MPierluissi/sounds/460856/),
[AugustSandberg K98](https://freesound.org/people/AugustSandberg/sounds/508747/),
[Federico_Casazza coat](https://freesound.org/people/Federico_Casazza/sounds/538930/),
[leonelmail body impact](https://freesound.org/people/leonelmail/sounds/504626/).
Processing is mono48k decode/DC removal/bounded gain/short fades and stated layering,
without artificial pitched tones, pitch shifts or time-stretching. Source/public
preview distinctions are explicit; acoustic and hand-contact approval is still human.

## Actual verification and limits

Game Development Win64 compilation exits0. Built Game SHA256
`0921d7557df84b3198eeb11f6cd99315f7f23476d9f51384dfa270e3aecdfba5`.
Approved fire SHA256
`3db2ca73ab698072a715ed1009cb5a8d7d94156262dc1a402a888def4706d0b1`.
31 cues load ready, output WAV headers are exact and have0clipped samples.

Actual existing finite actions loop PID20320 exits0: walk/run/slow/releases,
jump/landing/crouch, original terrain/prone/crawl obstruction gates, original
2/16->8/10 reload conservation and one accepted shot consuming one round pass.
M1 handling/open/load/close fire once; measured ages0/.585061/2.059298/2.814266s.
Six walk and six run takes actually play; only two slow takes are exercised.
Native stereo48k diagnostic output peak.198761/RMS.006389, no clipping. Independent
waveform match to open/load/close/fire is>.99993. This proves the new samples are
used by UE, not that their acoustics or full audiovisual timing are accepted.
The short19.2s diagnostic mix does not preserve the whole81s wall-clock sequence;
never use it as a captured soundtrack. Listen examples are constructed source
examples with stated intervals, not recorded gameplay audio.

Legacy loop PID37732 exits0: exact old V5 journal load, three German corpses stopped
at original3.933333s, first/three-second snapshots0events/0voices. After that gate,
one new accepted shot at4.037s changes saved shots9->10 and loaded7->6; input origin
unclassified. No death replay. Do not relabel the later shot as restoration noise
or omit it to make final history empty. Quiet pre-load world reports no recorded
audio data; a silent world can have no mix file. MI015 retains the original verifier
failure and its evidence-association correction, with the same native run/gates.

K98 reload/crawl sound/body-impact contact and an active reload interruption were
not exercised in these two loops. Generic existing reload animation and provisional
audio contact percentages remain; they are not a new historical mechanism simulation
or animation/contact pass. Hard-ground cues have no material-specific surface map.
Human in-game review must check timbre, level, cadence and visible contact; no model
auditory input or waveform metric substitutes for that gate. No FPS/stress/natural
encounter/full-motion/teammate/course acceptance follows from these checks.

## Recorded turn defect and hold

Existing raw frame46.47->46.53s changes forward bridge to rear street, immediately
after step_prone_move46.459s. The preserved observer directly sets control rotation
in Move() and later resets it to zero on arrival. This confirms an automated heading
snap, not a normal continuous mouse turn or accepted turn animation. Old raw images,
log/code and hashes are retained under MI015/private old_footage_review. This turn
is documented only; no observer/camera/model/animation change was made.

Do not record or re-export until the user explicitly accepts the sound after manual
review. When recording is subsequently authorized, the snapped turn also requires
its own continuous-input/turn presentation correction and review, retaining English
captions. OBS was not operated this turn; no new MKV/MP4 was created. Preserve all
previous trial/source/audio/video/raw/failure evidence and the new source/candidate.
No Git commit/push/SFTP/video hosting is authorized or performed by this revision.

Delivery's first mutable-launcher hard-link/count failure is preserved under MI015.
The old AVv3 Archive launcher briefly changed; exact authenticated original bytes
were restored, both candidate launchers detached and all47 parent payload rows
independently rechecked. No source/native/game/user-save drift occurred. The normal
trial is91files, not the initial92 assumption. Recovery does not erase that failure.
