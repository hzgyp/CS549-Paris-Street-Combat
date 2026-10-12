# MI021 — complete-space survey / team feedback completion

2026-10-10. Read MI020 and the new completion implementation plan first.
The finite survey is separate from the stopped white-cell placement and prone
anchor adjustments; no collision exceptions, wider tolerance or actor writes.

## candidate_v1: incomplete overlap result type in diagnostic build

The new read-only overlap inventory accesses FOverlapResult actor/component and
bBlockingHit, but Engine/World.h and capsule/movement headers only forward-declare
the struct. Game compilation fails with C2027; subsequent JSON argument errors
are parser consequences, not an asset/native failure. No survey game ran.

candidate_v2 includes Engine/OverlapResult.h explicitly. It does not change query
profiles, radii/heights, ignored actors or admission criteria. Retain v1's exact
source/build/log receipt; use a new identity. Existing P1 v9 and selected audio
V2, native/model/finger/weapon/save assets and ordinary user files stay protected.

## survey_v1: static space exists but the complete five-point proposal fails

The corrected read-only Game measured2205 NPC cells and289 prone corridors,
normal exit0. Static/full-path admitted A1/D1/D2/D3 counts341/169/94/88; A2 has
437 capsule-clear cells but no complete source/destination paths. Prone has46
corridors with all measured footprint/support stations passing, but no complete
player-to-start path. Do not present the survey's execution pass as placement or
crawl acceptance. No actor was moved; stop this proposal without range expansion.

A separate finite witness compares original/current feet, native projections and
path validity/partial/points at original and already measured endpoints. This is
cause observation, not a looser admission or another point search. If the area
is unconnected, keep it rejected; an explicitly documented subset may retain
accepted original A2 and use measured A1/guard points, with actual whole-squad
arrival still required. Do not replace an original failed witness receipt.

## candidate_v3: path-point loop shadows the survey index

C4459 rejects local `Point` hiding the existing global survey `Point`. The
diagnostic build stops before any path witness runs. candidate_v4 renames the
loop variable `PathPoint`, retaining the same five endpoints/query criteria and
compiler settings. No warning-policy change; failed v3 source/log kept.

## prone_cause_v1: observer misses the earlier native prediction branch

The control point advances1.568899cm then native prediction blocks before BP
ProneBlocked becomes true. Run exits0 with stop status but CAUSE.json is absent;
this is incomplete cause evidence, not clearance or a weapon/terrain diagnosis.
Separate v5 adds the same-frame read-only callback to existing native !Clear,
before input consumption, recording native_future floor samples. Original
bounds/query/actors/movement stay exact; first block still ends the observation.

## prone_cause_v2: early exit still misses Blueprint ActorTick block

v5 normal exit0 at first block again has no CAUSE file. The earlier inference
that native prediction necessarily blocked first is withdrawn. BP also updates
ProneBlocked inside the Character ActorTick, and the finite observer exits in
WorldPostActorTick before another controller read. Separate v6 explicitly calls
the read-only cause callback in that first-rejection branch, records both flags,
and reports same-position post-actor queries separately from exact original BP
execution. No diagnosis or collision repair follows if all those queries pass.
No further cause rounds if this bounded record remains incomplete.

## v6 route_v1: fixed linear observer does not clear the covered third guard

The native layout admits all5 actors; menu25 and ammo22 checks pass. The original
checkpoint route kills two guards, reaches G1, then finite240-second deadline
exits0 with one defender left. Preserve failed route_v1; no save/full-layout
acceptance follows. Last samples show the player at G1 and both living Allies
across the bank; they do not include the last German transform or prove that
German unreachable. The old helper only walks FarBank->Bridgehead and shoots
visible targets, with no covered-area search.

Separate bounded checkpoint_patrol observer uses the same fixed actor layout
and original engine navigation to visit actual living-guard feet, then returns
to original G1. Every waypoint must have a complete original-agent path; gun/
visibility/barrel/camera inputs and actual squad/save gates remain original.
No new actor sites, enemy damage/health/ammo/AI overrides or ordinary gameplay
changes. Failure of this covering-route witness stops the fixed proposal.

## prone_cause_v3: current support ray exposes a steep road collision edge

The completed explicit cause record exits0: BP blocked=true/native=false,
forward1.568893cm. Body box is clear and does not hit the owned gun. At feet
(1758.731,-20662.5,114.211), centre support hits BP_Road_Childs_C_40 with
normalZ0.141258 and heightDelta-4.411632cm; front/back pass. This post-actor
same-position query is consistent with original BP refusal, not a replacement
execution receipt. Keep original normal>=0.97 and world collision; reject this
apparently flat control footprint and stop positive-crawl proposal. No weapon
collision exemptions, road recook or smaller positive-crawl claim.

## candidate_v7 route_v2: diagnostic mode omitted from startup whitelist

The new checkpoint_patrol mode is in the CLI and finite Tick branch but was
omitted from StartupModule's explicit supported-mode assertion. Launch exits3
before map load; this is a diagnostic registration error, not an asset/layout
failure or actual route run. Keep exact v7 source/build/crash log. Separate v8
adds only checkpoint_patrol to the existing whitelist, retains the assertion
and every other gate; ordinary gameplay is byte-for-byte source equivalent v6.

## candidate_v8 route_v3: preload dispatch still treats patrol as walking mode

Startup now accepts checkpoint_patrol, but stationary->preload dispatch only
recognizes checkpoint. It presses/holds W into step_walk; because the explicit
actions branch excludes patrol, no action-release or mission combat executes.
Real German fire kills the player (Lost), shots0/defenders3, before any covering
route. This is actual gameplay loss caused by a wrong diagnostic sequence,
not a run of the planned covering-route witness. Stop/retain route_v3.

v9 adds patrol to that one checkpoint preload dispatch. Audit every Mode use:
legacy load, checkpoint/preload, actions/prone branch, patrol-only G1 search,
legacy terminal return and startup allowlist. No unconditional walk fallback
for patrol remains. Original fixture/thresholds/site/ordinary gameplay exact
v6. New route_v4 is the first correctly dispatched covering-route attempt.
