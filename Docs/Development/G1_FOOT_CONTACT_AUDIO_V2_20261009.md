# Player foot contact, jump Foley and recorded M1 report

9 October 2026. Implementation plan; runtime and revised human review pending.

The user reports that recorded Foley is much improved, but player walking does
not align with footsteps and jumping has no audible response. Other sounds are
generally satisfactory. The user explicitly requests replacing the previously
approved synthesized report with genuine firearm recordings where available.
This supersedes the earlier fire-byte freeze for this local revision only.
New screen recording remains on hold; the documented automated heading snap is
not part of this increment.

Read AGENTS, HANDOFF, CURRENT_DEVELOPMENT_BASELINE JSON/MD, the package retirement
plan, CURRENT_AUDIO_REVIEW, MI012, MI013, MI014 and MI015. Numerical/audio playback
passes do not establish contact or acoustic realism. MI015 also requires keeping
mutable launchers independent and associating diagnostic worlds from logged
generations, rather than UUID order. New MI016 preserves this human timing/jump
feedback and the rejected distance-only player step implementation.

Start from exact42 G1RecordedFoley20261009 source, Game0921d755…cdfba5 and its
31-cue manifest. Freeze this parent's source/audio/playable identities, previous
AV/HUD/native/source anchors, old captures and user saves before editing. Work
in a distinct project/trial; models, skeletons, finger poses, motions, camera,
accepted weapon/ammunition/save/terminal-death and reload presentation are
protected. Only the nonreflected audio helper and external WAV data may change.
No editor entry, asset save, recook, Git/SFTP publication or OBS operation.

Player step presentation will read the existing evaluated left/right foot bones,
emitting on a descending foot reaching its low/contact phase, gated by actual
grounded movement. Track each foot separately with anti-jitter rearming/cooldown;
reset across stop, air, teleport, posture and reload transitions. Do not create
a new fixed-time or fixed-distance player cadence. Keep existing NPC/crawl
behavior scoped. Diagnostic-only foot samples must expose actual bone phase,
speed, movement mode and emitted side for independent review. This does not
repair physical foot sliding or certify sole/floor collision.

Add a quiet recorded boot/cloth takeoff cue only on grounded-to-airborne upward
jump transition; never on rejected input or ordinary ledge fall. Retain the
grounded landing transition, make its existing recorded contact audible, and
prevent walking impacts in air. No human grunt or invented vocal recording.

Use MPierluissi's CC0 M1 live-fire field recording (460851), rather than the dry
fire or reload recordings, for player/Allied M1 reports. Acquire the official
public HQ preview and preserve source/rights/hash/trim/gain details. Decode to
mono48k PCM; keep the report onset immediate, retain its bounded natural tail,
avoid leading handling/background content and do not pitch/time synthesize it.
The original source is an indoor range recording, not an outdoor Paris capture
or a lossless original download. Bounded search found no freely reusable exact
K98 live-fire recording: retain the German cue as an explicitly stated gap,
not relabel M1, Mauser pistol, modern .308, dry fire or paid previews as K98.
Preserve successful ShotSequence gating and spatial attenuation.

Early gate: exact parent42/31/Game and source758/native359/protected703/parent40
closures, no active user engine/build, confirmed foot_l/foot_r runtime evaluation,
licensed actual live-fire origin, valid PCM and unclipped output. One instrumented
finite actions check will diagnose the contact implementation and verify an
upward takeoff, landing, silence in air/at rest, original conserved reload and
successful-shot decrement. Inspect independent foot trajectories/event timing.
A second distinct measured correction is allowed only if actual sampled anatomy
demonstrates a different contact criterion; preserve the original negative and
update this plan first. Do not sweep timing offsets or invent a numerical pass.
Recheck legacy V5 three-second stopped corpses, quiet restore and old closures.

Stop on license/provenance ambiguity, missing/stale evaluated feet, unexplained
protected drift, compile/playback failure or repeated startup GPU failure.
Keep every negative with its identity. Deliver a normal independent playable
entry and labelled source listening examples. Human in-game cadence, jump and
report acceptance remain separate; no new recording until the user passes them.

Measured correction addendum: candidate_v1 Game d889ff5c passes original finite
actions/legacy terminal checks, but reviewed foot trajectories expose a planted
foot roll producing a second low-point event on the same step. Stop that contact
candidate. Add a per-foot latch rearmed only after visible rise from the lowest
post-contact height and separation above the other foot; retain the original
ground/movement and low-phase gates. Use a distinct candidate_v2 source/build and
checks_actions_solo/checks_legacy_solo identities, preserving v1 data/graph.
The first full-template jump match also fails under overlapping NPC footfalls;
this is not proof of absent player playback. Add an audit-only SoloPlayer flag,
effective only with the explicit audit directory, to admit independent actual
player cue matches. Normal NPC playback is unchanged. Raise takeoff gain from
.48 to .65; landing stays .85. Human audibility/realism remain pending. No more
contact tuning rounds are authorized by this plan if this measured version fails.

Diagnostic association correction: the measured Game is unchanged. Verifierv2
compares a41.389755s walking heel event with a lower slow blend after speed drops
150->63.939cm/s20ms later, failing its absolute-window residual4.940552cm. Actual
walking minimum16.118528 at41.379853s precedes the emitted16.166165 by9.902ms.
Preserve the failed verifier; associate raw trajectory minima within the event's
walk/run/slow speed regime, retaining3cm/.14s/.09s and descent gates. This is a
diagnostic correction, not a contact code retry, game rerun, erased failure or
physical contact approval. Transition timing remains a human review boundary.

Final diagnostic scope: same-regime filtering itself leaves too little data at
some actual acceleration boundaries; preserve both subsequent verifier negatives.
The final verifier keeps the original3cm and descent bounds for stable gait
windows and explicitly labels all mixed/insufficient windows UNASSESSED. Actual
result:20 stable contacts checked,9 transition contacts unassessed; no claim that
those9 passed. No further Game edit, input run or erased earlier gate failure.
