# Directional locomotion and lifecycle checkpoint — 1 October 2026

## Outcome and scope

German persistent floating was causally diagnosed and corrected in **separate native adaptations**, not by lowering the actor or changing vendor files. Both factions now have eight-direction walk/run BlendSpaces, measured stride-rate variants and shared Blueprint damage/death/reset functions. Twelve fixed-step cases passed for each of two animation profiles; bridge-disabled fresh reopening passed for sixteen new packages and six saved Character configurations. **P2 remains partial**, not an accepted playable FPS or MVP.

Owner: Yupu Guo. Starting source revision `37de53688530d379d73115a22604bd7ee02c03c9`; UE 5.8.2-56702186. Follow the [implementation plan](CHARACTER_AND_WEAPON_IMPLEMENTATION_V1.md). Earlier [movement results](CHARACTER_MOVEMENT_RESULT_20261001.md) and their failures remain historical evidence. No detailed character production, Blender edits, city edits or vendor resaves occurred.

## Diagnosis and bounded changes

Source, Allied and German reference root/pelvis/leg transforms are effectively equal. German root/pelvis translation retarget modes were `Skeleton`, whereas source/Allied modes were `Animation`. Restored in-memory comparisons reproduced the visible elevation: German idle model-space minimum Z was 8.606–11.728 cm with original modes and -1.196–-0.579 cm with the override; forward walking was 12.934–17.064 cm versus -0.625–0.194 cm. These are model-space comparisons, not world-floor clearances. Running includes genuine flight phases. Original skeleton/mesh hashes were retained.

New packages under `/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1/` contain one duplicated skeleton and two adapted meshes. Only the new skeleton's root/pelvis translation modes changed. Reference pose, geometry, weights, materials and source animations did not change. Matching proportions did not justify an additional IK-retarget pipeline.

Two faction AnimBPs under `Animation/DirectionalDraft/` calculate actor-local forward/right velocity with standard Blueprint nodes. Their two-dimensional BlendSpaces contain idle plus eight walk and eight run directions. CharacterMovement owns translation; source actions remain in-place. Walk/run sample points use provisional 150/300 cm/s radii.

Four separately named `_Stride_v1` copies calibrate moving sample RateScale from matching native root-motion displacement, duration and in-place sequence rate. Example source speeds are 203.61 cm/s forward walk, 186.37 backward, 167.92 left strafe and 216.31 right strafe. Source root-motion clips are measurement references, not a second actor-movement driver. Old profiles/maps remain unchanged.

## Recorded tests

| Check | Actual result | Limitation |
| --- | --- | --- |
| Directional profile v5 | 12/12 cases: four mesh variants × 30/60/120 fixed steps/s; 21,000 poses | Not measured FPS, real device input, PIE or performance |
| Stride profile v6 | Same 12/12 numerical cases; another 21,000 poses | Contact/stride quality is separately reviewed, not included in numeric pass |
| Movement assertions | Forward/side/back travel, braking, local direction axes, stable grounded capsule, wall blocking and finite full pose series passed | Transient diagnostic World; no city/NavMesh/AI proof |
| Rendered review | Both profiles' front/side sheets reviewed: 64 selected views per profile | Resolved clothing/equipment and no gross collapse at examined endpoints; not every frame/face/lighting condition |
| Lifecycle | Player and NPC children × three cycles each, repeated with stride AnimClass overrides: 12 cycle checks | Ready/Dead only, not full weapon action coordination or checkpoint restoration |
| Fresh reopening | Bridge disabled; sixteen new packages and six stride-scene Character instances loaded; recorded hashes retained | Not packaged-build acceptance |

Heuristic lower-foot bone drift improved in the Allied A, 30-step/s comparison:

| Walk direction | v5 median cm/s | v6 median cm/s |
| --- | ---: | ---: |
| Forward | 59.18 | 9.78 |
| Right | 72.55 | 20.41 |
| Backward | 23.43 | 11.52 |
| Left | 17.28 | 8.76 |
| Diagonal | 43.82 | 13.78 |

This metric selects the lower foot with low vertical motion; it is **not a validated planted-sole detector**. Residual sliding is not waived. German A v6 at 60 steps/s settles at approximately 1.527–1.767 cm visible floor gap rather than the earlier ~11 cm; its complete forward phase still dips to -6.521 cm. Across all v6 phases/variants/rates, visible geometry minimum Z spans -7.760 to +8.785 cm relative to the test floor. Transition penetration remains a recorded defect; running flight can contribute positive values. Do not claim full foot-contact acceptance or lower the actor globally to mask it. Next bounded contact work should isolate blend transitions/plant phases and evaluate foot/pelvis correction against actual ground, preserving these baselines.

## Shared Blueprint lifecycle

`Blueprints/Characters/LifecycleDraft/BP_PCCombatantV2` inherits the earlier shared shell; `BP_PCPlayerV2` and `BP_PCNPCV2` share its normal K2 functions. Damage clamps health, ignores nonpositive/nonfinite values and dead actors, and performs one death transition. Death stops movement, disables capsule collision, increments ActionID and plays the existing finite death sequence. Reset increments restore generation/ActionID, restores health, collision, walking and the prior AnimClass. Post-death damage and repeated death calls were ignored; NaN/infinity were rejected. Death animation advanced to approximately 3 seconds; restored characters travelled 280.48 cm in the controlled one-second request.

No ragdoll, hit montage, weapon input/action FSM, ammunition refill, replacement actor, AI or checkpoint snapshot is implemented by this test. The harness separately restores the actor transform. `P2_CharacterStride_20261001` uses explicit per-instance stride AnimClass overrides on six Characters; class defaults and earlier maps retain the uncalibrated profile.

## Evidence, failures and preservation

Canonical evidence root: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/`.

- `P2/Retarget/reference_diagnosis_v1.json`, `translation_compare_v1.json`, `directional_author_v1.json`, `stride_author_v1.json`.
- `P2/Movement/movement_probe_v5_<variant>_<rate>.json`, corresponding v6 files, `directional_v5_review.json`, `directional_v6_review.json`, PNGs and derived sheets.
- `P2/Lifecycle/authoring_v1.json`, `probe_v1.json`, `fresh_reopen_v1.json`, `stride_scene_v1.json`, `probe_stride_v1.json`, `stride_reopen_v1.json`.
- Execution/build logs: ignored `tmp/paris-integration-20261001/`.

The initial translation comparison failed under NullRHI because CPU geometry needed a render MeshObject; its rendering-enabled retry passed. Multi-case v4 completed only five numeric cases before renderer OOM; it is not a twelve-case pass. Repeated GPU/CPU skinning transitions recreated render resources within one commandlet frame. The corrected harness retains CPU skinning on its transient component, flushes end-of-frame render data and runs one case per fresh process. These diagnostic settings do not change production renderer configuration and cannot establish GPU performance. Earlier build/API errors and failed evidence remain retained. Final bridge build is `EditorBridgeBuild_v17`; it remains Editor-only and disabled by default. Generated gameplay uses native engine/Blueprint nodes, not bridge calls.

All usable draft bytes have one physical home in the existing mutable SFTP workspace. [Local draft inventory](../../Assets/Integration/LOCAL_DRAFT_INVENTORY_20261001.json) records all 25 current draft packages, **12,181,561 bytes**, with hashes and aliases. It is explicitly **not selected by Catalog, not remotely immutable and not restore authority**. Native baseline originals remain separately authoritative. No new immutable release, Catalog/allowlist change, staging, commit or push is claimed.

Final checks: all 25 draft hashes/sizes and NUL-delimited Git-ignore queries matched; the 721-file native integration baseline local verification and 17,238-file selected manifest/source-history storage checks passed. Integration Python compilation and Git whitespace checks passed. The installed bridge DLL and three source files match the successful v17 packaged output. No Unreal/Blender process remained at handoff. Ordinary CRLF conversion warnings do not indicate whitespace-test failures. These checks do not verify remote publication of the new drafts.

## Remaining gates

P2 still needs transition/ground-contact treatment, actual player input, city daylight/shadow and ground tests, weapon contact, performance and packaged smoke testing. P3 evidence and the required human weapon/view choice are in [the weapon capability review](WEAPON_CAPABILITY_REVIEW_20261001.md). Do not rerun one-time relocation or overwrite any existing draft identity. A future authorized release must verify its complete native dependency closure and explicitly transition native restore paths from lab aliases to runtime paths before matching metadata is published.
