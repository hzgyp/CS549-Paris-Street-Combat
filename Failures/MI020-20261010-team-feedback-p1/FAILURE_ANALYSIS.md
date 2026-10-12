# MI020 — P1 loadout / movement / HUD trials

2026-10-10. New independent trials start from P0 v4. Preserve current models,
fingers, weapon/resource/save transactions, source parents and protected assets.

## candidate_v1: diagnostic compile error, not an asset failure

`ParisP1Probe.cpp` inferred `TSharedRef` from `auto = MakeShared`, then called
`ToSharedRef`, which belongs to `TSharedPtr`. Game build failed before launch.
Explicitly use `TSharedPtr<FJsonObject>`; the correction changes diagnostic typing
only. Original failure source, build log and exit receipt remain under
`tmp/g1-team-feedback-p1-20261010/candidate_v1`. The distinct candidate_v2 is
prepared from that source with this single correction. Do not reuse a failed
build identity or infer native/visual acceptance from compilation.

Read before future P1 repairs; record subsequent runtime failures separately.

## candidate_v2 / ammo_v1: white cell fails formal capsule occupancy

The first fixed A1 candidate (1562.5,-21212.5 cm) projected onto native navigation
and ground, but its unchanged formal capsule was blocked. Preparation stopped
before any of the five target actors moved. The game exited normally (0), while
the finite diagnostic explicitly reported failed_mission_preparation with zero
checks. Normal exit is not test success. Source, Game, launch and native receipt
remain private in the candidate_v2/ammo_v1 directories.

The measured 25cm white cell was a proposal, not spawn admission. Do not widen
the capsule test, ignore static collisions, or search repeatedly under this trial.
candidate_v3 removes that entire initial-placement entry and retains the accepted
layout, while continuing loadout, movement and HUD validation. New dispersion
requires a separate full-space survey. Layout feedback remains unresolved.

## candidate_v5: Editor-only sample-count API used in Game diagnostic

The added read-only BlendSpace inventory called GetNumberOfBlendSamples, declared
inside WITH_EDITOR, so the Game-only build failed before launch. The runtime
GetBlendSamples array accessor is available without WITH_EDITOR; candidate_v6
uses that array directly. Check preprocessing scope as well as the declaration
when reusing Editor-authoring APIs in a Game diagnostic. Preserve the failed
source/build receipt; this was not a character/model or animation-data failure.

## candidate_v6 / actions_v1: later prone fixture occupied by a living Ally

Walk/run/slow, key release, jump, crouch and the original unsuitable-terrain
prone refusal passed. The retained flat prone site was subsequently blocked by
BP_PCAlliedFormalCombatV1_C_1. Its capsule hit the box, and the forward floor
trace hit that Ally rather than ground. The evidence identifies dynamic occupancy;
it does not show bad city geometry or failed prone controls. The diagnostic exited
0 with an explicit failed_retained_prone_site_obstruction_and_complete_path.

Stop that combined ordering. Do not ignore the Ally or expand collision/path/
arrival tolerances. candidate_v7 changes diagnostics only: the ordinary speed/
jump/crouch case ends after the terrain-refusal assertion, while a separate fresh
prone run visits the exact retained site before forward movement makes the squad
follow. The same footprint, complete path, physical arrival and obstruction gates
remain. No teleport, AI pause, collision switch or resource writes are introduced.

## candidate_v7 / prone_v1: valid stance too close to predictive obstruction

The independent test actually reached X1771.834 at the retained X1762.5 anchor
(+9.334cm), passed the same footprint/ground checks, entered prone (34cm capsule),
and denied low-posture fire. Its forward input was immediately blocked by the
unchanged predictive footprint, so forward movement was 0cm and the test failed
its positive-crawl gate. Static clearance at the current point does not guarantee
clearance at the next predicted point. This was not evidence of normal forward
prone movement, nor a reason to disable the guard.

candidate_v8 changes only diagnostic alignment: release backward input at the
anchor X itself instead of allowing +15cm before releasing. The fixed destination,
Y bound, physical <=20cm arrival, complete path, forecast, capsule, travel and
obstruction-drift criteria remain unchanged. This tightens placement at the same
measured anchor; no wider site search or teleport. Preserve prone_v1 as a failure.

## candidate_v8 / prone_v2: forward footprint blocked after 1.569cm

The tighter arrival reached X1757.167 and again passed current footprint, prone
entry and low-fire denial. Forward movement reached only 1.5689cm (peak34.13cm/s),
then the existing Blueprint ProneClear became false / ProneBlocked true and held
drift at0cm. The native future flag was false while the BP rejected input; it does
not demonstrate an unblocked pending input. This is another FAILED positive-crawl
case, not a pass or full-motion acceptance. Do not loosen/disable either guard or
continue anchor adjustments. The point needs a separate full swept-space survey.

Current P1 changes do not edit the original crouch/prone Blueprint, capsule,
floor/footprint criteria or native forecast code. Continue the separately scoped
speed/HUD/ammo/G1/journal checks; explicitly retain the unresolved prone fixture
in candidate status and the final review instructions. No fresh positive prone
traversal claim follows from the protected-source comparison.

## candidate_v8 / route_v1: player victory froze Allies before crossing

The old route observer returned success for clearing, E-save, load and restart.
Independent examination of its 739 actual samples found both Allies alive, but
their maximum X positions were only 4871.308 / 4585.812cm; neither reached the
original far-bank X>=5600 condition. Entering Won stopped all brains immediately.
Player success was therefore insufficient proof of squad traversal. This route
is FAILED for the complete squad requirement despite its narrower observer status.

candidate_v9 waits for the existing bridge_transit_complete flag before admitting
a fresh Won transition, retaining the original G1 occupation conditions. It keeps
AI running in Occupying, without edits to the bridge path, HeldGoal, 55cm arrival,
SquadFailed, navigation, collisions, or save/dead restoration. The observer must
assert the flag and actual positions at victory. Do not gate Crossing->Clearing
on that flag: the existing transit condition requires player X>6500 and would
deadlock at the original far-bank anchor. Keep original diagnostic deadlines;
failed arrival remains a failure, with no teleport or forced completion.
