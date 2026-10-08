# Native NPC convergence survey result

7 October 2026. **The retained25cm black/white map now has a completed first native convergence sample:69 uniformly covered50m tiles, each tested once with an accepted Allied and German NPC,138 role/start outcomes.** The original map remains unchanged. These are temporary tests, not final spawn/objective/encounter choices.

Read the implementation and dependency/avoidance/crowd addenda and ML010/11/13/14/15/17/18. New runtime negatives are archived in ML019. Browser/iPad interaction work is deferred by the user.

## Actual outcomes

| Original profile | Reached and stood safely | Negative | Unmeasured bank cases |
|---|---:|---:|---:|
| Allied | 25 | 44 | 0 |
| German | 25 | 44 | 0 |

Observed terrain-bank reasons: `{"saved_navigation_complete_path_rejected": 84, "native_path_following_failed": 4}`. Do not equate missing/partial saved paths with physically blocked terrain. Native following failures retain their original completion events and actual sampled positions/supports, without an invented obstacle diagnosis. Every negative25cm start centre is black in its role-specific, **current-saved-navigation/to-this-hub** derivative. Neighbours, whole50m tiles and other connected destinations are not rejected by that observation. Other white remains a geometry candidate; this finite sample does not certify all733900 white centres.

This bank verifies movement **toward** the hub only. It does not establish hub-to-origin return or mutual all-pairs reachability. A future reciprocal test must use a new bounded bank and preserve these original successes/negatives, especially ML014's arrival-offset lesson.

The central real floor is [187.5,-337.5,107.87759089519764]cm, about3.86m from the geometric map centre, with25 measured3m-stencil stations. Both original NPC profiles stand safely there. Origins are selected from retained expanded-survey white; actual locomotion uses unchanged saved production Recast/Detour A* and original PathFollowing/CharacterMovement. Installed engine source confirms the A* call chain. Partial paths are rejected. Original maximum speed300cm/s, acceleration/capsules/terrain/time rate and native animation/equipment remain unchanged. Native actual route length determines the unchanged distance-scaled deadline. A near35m straight-distance origin required154.574m native travel and passed in52.509game seconds; a short universal timeout would misclassify it.

Four early_v2 positives are reused once, with their original RVO configuration. The134 fresh Full cases explicitly isolate capsule test-agent collisions and RVO group steering in the disposable world; original RVO enable flags and movement profiles remain exact. Inactive movement ticks are suspended to prevent falling. Each arrival requires matching SUCCESS, idle path following, actual XY/feet-Z<=35cm, grounded walking, no terrain overlap and0.6s safe standing. Python schedules only initial placements and observes; no moving-frame pose/position driver.

## Separate simultaneous crowd observation

Three newly frozen starts use original RVO groups and mutual capsule collision, the same exact hub/gates and retained arrived bodies: **1 endpoint passes, 2 negatives**. Native final position/separation/event records and the near-hub trajectory plot are preserved. This is a measured interaction observation, not a production squad-follow pass. Crowd outcomes blacken zero terrain cells. A future rally region or assigned destinations must be designed separately rather than changing these failed gates.

## Layer status

The existing saved3/full5 local surface stacks and exact feetZ are retained. The new atlas shows full-survey geometric clearance nodes by local order:1242419,81265,13170,1740,76; admitted road white:733900,0,0,0,0. These are local XY-height stacks, not five globally consistent floors. **Semantic floor partitioning and real stair/ramp/bridge-above-below connections remain unverified.** No higher-layer origin is silently admitted or flattened into another floor. Native A* itself preserves real polygon heights/connectivity.

## Evidence and preservation

Private Evidence/NativeConvergenceV1 contains frozen bank, failed_dependency_v1, early_v2, full_v1, crowd_bank_v1, crowd_v1, layer_atlas_v1, artifact_v1 and the exact failed_runtime archive. Independent audits validate all138 finite bank outcomes and the separate3 crowd outcomes. Source mask differences are independently checked to be exactly the observed per-role negative starts; all ten derivative layer PNGs are4032² pure1bit. ML018's first setup failure had zero movement attempts, remains negative and blackens no cells. Its required snapshot-container contract was corrected in distinct early_v2; old functions/bank/thresholds remain exact.

Early native photographs were actually inspected and are dark/occluded, sometimes identical for overlapping isolated agents; they do not approve visual model presentation or full motion. The delivered map/layer/crowd figures are measured plots, not fabricated in-engine photographs. Selected original25cm source files, all703 frozen current guards and three historical survey helpers remain exact. No map/navigation/config/asset save, model/finger/grip/weapon/AI edit, Catalog adoption, release, Git commit or push. No whole-map, formation, performance, playable-build, teammate, MVP or course acceptance. All owned native exits and log gates are in closure; no user preview was terminated.
