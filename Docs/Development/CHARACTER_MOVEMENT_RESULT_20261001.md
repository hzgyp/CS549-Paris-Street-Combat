# Character movement checkpoint — 1 October 2026

Later same-day [directional/stride/lifecycle results](CHARACTER_LOCOMOTION_LIFECYCLE_RESULT_20261001.md) supersede the unresolved persistent German float, speed-only direction and absent health/death implementation below. This file preserves the earlier checkpoint and its evidence; remaining full contact/input/city/performance acceptance is still not claimed.

## Outcome

The active Paris project now has a shared **Blueprint Character shell**, player/NPC children, two skeleton-specific velocity-driven locomotion AnimBPs/BlendSpaces and a six-Character diagnostic map. Fresh loading with the authoring bridge disabled passed. Four meshes at three fixed timesteps passed bounded numeric movement/braking/wall tests. **Full P2 is not accepted:** German visible ground contact fails, directional animation is incomplete, and health/death/action ownership is not yet implemented.

Owner: Yupu Guo's local integration session. Starting source revision: `37de53688530d379d73115a22604bd7ee02c03c9`; HEAD/origin/main were equal after fetch. UE **5.8.2-56702186+++UE5+Release-5.8**, DX12/SM6, RTX 3080, ray tracing enabled for the rendered probe. No Blender modeling, vendor resave, city change, immutable publication, catalog update or commit/push was performed. The [previous result](CHARACTER_INTEGRATION_RESULT_20261001.md) remains the P0/P1/initial-preview record.

## Implementation and tooling

The 540-package native intake has no Blueprint/AnimBlueprint to reuse. Python reflection cannot create/allocate the required graph nodes; installed engine headers expose these as C++ editor methods. The documented specific need is addressed by **Editor-only, disabled-by-default** `ParisEditorBridge`. It generates standard engine Blueprint nodes and runs diagnostics, not C++ gameplay. Generated assets inherit native Character/AnimInstance, do not call bridge functions, and load with the bridge absent.

BuildPlugin succeeded with VS 2022 14.44 and Windows SDK 10.0.26100, using a new ignored empty host project, not a city/model copy. Earlier compilation failures were repaired; final packaged plugin source is in `tmp/paris-integration-20261001/EditorBridgeBuild_v6/Source/` (AutomationTool removed its temporary host after packaging). Source and installed DLL hashes match the successful packaged plugin. Binaries/caches remain ignored. Main `.uproject` and renderer settings are unchanged.

`BP_PCCombatantBase` provides instance-editable TeamId/RoleId and four Blueprint movement/look requests. `BP_PCPlayer` binds diagnostic WASD/mouse axes and has a trailing spring-arm camera, **not final FPS presentation**. NPC inherits the shell without player input; no AI/controller/navigation behavior was added. Six axis mappings were added while preserving existing EnhancedInput settings; real keyboard/mouse behavior remains untested.

The AnimBPs calculate GroundSpeed from Pawn planar velocity. BlendSpaces reference unchanged native **in-place** `Rifle_Idle`, `Rifle_WalkFwdLoop`, `Rifle_RunFwdLoop`, at provisional 0/150/300 cm/s. Mesh scale is 1, yaw -90 degrees, capsule radius 34 cm. Half-height/mesh offset come from imported bounds, not arbitrary actor lowering or skeleton scaling. No root-motion double application.

The first authoring attempt failed on non-instance-editable identity variables. Its eight draft hashes were verified before bounded recovery; only the two flags were corrected. The failure is preserved inside `authoring.json`. Recovery is not a general overwrite/rebuild mode.

## Actual checks

| Check | Result and limitation |
| --- | --- |
| Published baseline before/after | Local size/SHA-256 verification of 721 selected files completed with exit 0; existing native character bytes retained. |
| Blueprint generation | Three Character BPs and two AnimBPs compiled; initial child parent-event signature fixup messages retained. No health/death/action implementation. |
| Fresh reopen, bridge disabled | Five generated BP classes loaded/compiled, no bridge package dependencies, six persisted Character configurations matched. Zero commandlet errors; not a package/build pass. |
| Numeric movement v3 | **12/12 passed**, four meshes × fixed 1/30, 1/60, 1/120 s. Sequential single-character worlds, not simultaneous six-AI/performance. |
| Tested phases | Settle 1 s, forward walk 3 s, right movement 2 s, brake 1 s, run-to-wall request 5 s, wall stop 1 s. Same Blueprint requests and native CharacterMovement/collision. |
| Render evidence | 24 valid 1000×1000 PNGs; all variants/checkpoints reviewed on a contact sheet, four forward-walk views also inspected at full resolution. Controlled shadowless lights, endpoint stills only. |
| Source/storage | Python compilation, manifest metadata/tracked-source storage guard and `git diff --check` passed. No code allowlist entry or asset staging. |

The transient Game World has no GameMode/LocalPlayer. The harness explicitly designates its controller local, dispatches BeginPlay, and advances the engine frame counter before every World tick. These declared lifecycle conditions do **not** establish PIE/device-input acceptance. Initial movement probes are preserved: v1 lacked local-controller designation; v1/v2 left the commandlet outer frame counter unchanged, suppressing normal tick-task/pose updates. V3 repairs these harness conditions without bypassing collision or changing gameplay graphs. It finished at **16:56:19 EDT**, zero commandlet errors/warnings.

| Measurement, all four meshes | 30 steps/s | 60 steps/s | 120 steps/s |
| --- | ---: | ---: | ---: |
| Forward walk displacement / 3 s | 446.827 cm | 445.689 cm | 445.120 cm |
| Right displacement / 2 s | 297.977 cm | 296.654 cm | 295.942 cm |
| Final center X, wall face X=1050 | 1015.785 cm | 1015.899 cm | 1015.900 cm |
| Capsule penetration into wall | 0 cm | 0 cm | 0 cm |

All phases remained walking-on-ground with capsule floor clearance approximately **2.150 cm**. Braking ended at zero planar velocity; animation speed tracked endpoint velocity (150 while walking, zero after braking/at the wall). Timesteps are **not measured achievable FPS**. The run-to-wall endpoint is stopped, so its geometry measurement is not a running-stride sample.

## Defects and next work

| Priority | Evidence and next action |
| --- | --- |
| P2-MOVE-01: German visible contact | Lowest skinned geometry is ~10.982 cm above floor at idle and 18.588–18.934 cm at forward-walk endpoints, confirmed visually. Capsule clearance is stable. Compare source/target reference poses, pelvis/leg translations and retarget settings before a bounded engine-native adaptation on new team-owned drafts. Do not mask phase-varying gaps with one constant actor drop. |
| P2-MOVE-02: directional animation | Speed-only blending plays forward gait during right movement. Use verified directional actions and velocity direction; regress backward/lateral/diagonal transitions. |
| P2-MOVE-03: gait coverage | Allied endpoint geometry is ~1.545 cm at idle and 1.892–2.105 cm on forward walk. Full-cycle slip/penetration is unmeasured. Sample complete idle/walk/run cycles, distinguish bone pivots from visible soles, review joints/equipment and test slopes/steps plus actual city ground. |
| P2-MOVE-04: shared lifecycle | Movement/identity shell only. Implement shared health/death/cancellation with explicit ownership and repeat tests; no independent AnimBP health/ammo. |
| P2-MOVE-05: input/view | Camera/bindings saved but physical input/PIE untested. Run local player input/camera and later packaged smoke tests; do not treat trailing camera as accepted FPS arms. |

Reviewed endpoints retain textures/equipment and show no obvious gross limb collapse in these particular frames. Faces remain shadow-obscured here; earlier filled-face checks are separate evidence. Empty-handed rifle poses do not certify weapon grip/reload. Historical configurations, city lighting, AI/navigation, mission/checkpoint, performance, packaging and teammate restoration remain unrun by this task. No course acceptance status was advanced.

## Storage and recovery

Eight new packages total **313,338 bytes**, physically under `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/`, through the existing active Content alias: three `Blueprints/Characters/BP_PC*`, two `Animation/LocomotionDraft/ABP_PC_*`, two `BS_PC_*`, and `Tests/Integration/P2_CharacterMovement_20261001`. The generated player BP retained NTFS Authenticated Users Modify (covers the shared account); no ACL/protected-root change. Yupu retains binary ownership. These are ignored **unpublished drafts**, not immutable releases or teammate restore authority.

Runtime `Evidence/P2/Movement/draft_inventory.json` records exact package sizes/SHA-256 and PNG hashes; it is explicitly not an active release manifest and has no remote object authority. `GIT_CODE_ALLOWLIST.json` stays empty. Models/native animation bytes cannot be admitted as code.

Evidence in that same directory: `authoring.json`, `fresh_reopen.json`, `movement_probe.json`, `movement_probe_v2.json`, **`movement_probe_v3.json`**, `Captures_v3/`, `movement_v3_contact_sheet.jpg`. V1 PNG-named captures contain EXR bytes because the initial render-target format was unset; they are rejected as PNG evidence and preserved. Logs are ignored `tmp/paris-integration-20261001/p2-movement-*.log`. All commandlets exited; no editor remains open.

Next: P2-MOVE-01/02 under the [updated plan](CHARACTER_AND_WEAPON_IMPLEMENTATION_V1.md), full contact/transition regression, shared lifecycle, then P3 weapon/view/reload feasibility. Preserve vendor baselines and uniquely identify new evidence. Verified immutable publication and matching Git commit/push require their own task authorization.
