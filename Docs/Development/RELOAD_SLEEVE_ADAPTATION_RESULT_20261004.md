# Reload sleeve adaptation V2 — diagnostic stopped, not repaired

4 October 2026. [Chinese review](RELOAD_SLEEVE_ADAPTATION_RESULT_20261004_ZH.md).
Plan: `RELOAD_SLEEVE_ADAPTATION_V2_20261004.md`. Read AN001/FP001 and the
blender-character-workflow deformation/source-cause checks before acting.

## Outcome

No V2 animation/Blueprint/mesh candidate was authored or selected. Sleeve/contact
and first-person acceptance remain open. The new read-only skin-edge diagnostic
crashed the existing user-owned editor; its exact failing native call is not
proved. Stop that diagnostic path, preserve evidence and recover asset inspection
only. Do not infer successful adaptation from bone/hash checks.

## What was actually checked

Private evidence is in the existing single workspace
`Evidence/ReloadSleeveAdaptationV2/`.

- `bone_audit_v1`: source/full Allied/continuous-arm reference poses, parents,
  source/failed/control track data and six local-pose samples, collected without
  native saving. Source and target reference arm rotations differ; that is data,
  not proof of the sleeve's cause. Target and owner reference poses match.
- `binding_probe_v2`: native Animation Editor frozen at2.20s, complete Allied mesh
  beside its continuous-arm follower. Both externally inspected sleeves appeared
  intact at this one phase/view. This is not the protected first-person camera,
  whole animation cycle or proof that the old game-view defect is solved.
- `skin_probe_v3`: neither mesh has a post-process AnimBP.73 same-phase native
  component-space bone transforms agree: maximum translation-component delta
  `7.105427357601002e-15 cm`, quaternion/scale component delta0. This rules out a
  mapping discrepancy in this isolated direct follower, not the game's binding,
  LOD/bone refresh or projection.
- The old matched `reload_operate.png` was re-inspected: its large triangular
  sleeve/obstruction defect remains real. No new game-view comparison was run.

## Failures and stopping

`binding_probe_v1` used unavailable `set_playing`; `skin_probe_v1` used unavailable
`get_component_transform`; v2 used incorrectly spelled `get_all_triangle_ids`.
Original executed snapshots and log errors remain. Corrected v3 gathers API names
without requiring absent methods. These are diagnostic API mistakes, not native
animation corrections or proof of a cause.

At20:49:34 UTC /16:49:34 local, `edge_audit_v1` exited fatally before writing a
result: python311 access violation, engine `RequestExitWithStatus(1,3)`.
Callstack does not locate the exact mesh-copy/weight/query operation. Do not label
this an established Geometry Script bug, mesh corruption or fixed root cause.
No CPU edge measurements were obtained. Live entry is now stop-locked; executed
source remains private. See [AN002](../../Failures/AN002-20261004-reload-sleeve-diagnostic/FAILURE_ANALYSIS.md)
and its manifest for unchanged evidence/log/crash locations and hashes.

The plan's source-cause gate was not met, so no speculative reweighting, twist
track replacement, sleeve mask, camera change, IK rerun or offset sweep followed.
Future diagnostics should first observe the actual game's component-space bones,
LOD and leader relationship in a disposable process, distinguishing real skin
stretch from near-camera projection. This is a proposed next investigation, not
permission to repeat AN001 or this failed live skin-read path.

## Preservation and recovery

After the crash all512 protected/retained size/SHA records matched with0 changes,
including the formal city, source models/rig/fingers/actions and existing gun
transactions. No native assets/map were saved; all temporary preview components
vanished with that process. No Catalog/allowlist/release/commit/push.

Recovery uses a new preview-only identity
`human_reload_assets_20261004_165056_155`, PID42928, Entry, bridge disabled.
Its report is `ready_for_human_asset_inspection`, errors[], all three native tabs
opened and507 before/after guards match. Original D059 is foreground and looping.
This recovery is not repair resumption; do not launch a second writer or save the
retained failed target. Existing M1 transient preview is restored separately,
without source socket offsets or asset saves; actual recovery status is in HANDOFF.
