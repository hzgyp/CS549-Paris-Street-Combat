# Reload adaptation V2 — isolate sleeve deformation first

4 October 2026. Owner: yg745. [Chinese review](RELOAD_SLEEVE_ADAPTATION_V2_20261004_ZH.md).

## Scope and authorization

Yupu authorized incremental adaptation after inspecting the original D059 reload
with the existing M1. This increment addresses the stretched sleeve only. It does
not select a new gameplay baseline or fix framing, rifle contact, recoil, sprint,
prone, NPCs or weapon mechanics. Existing assets/mature motion first; no new action
keyframes. The source is `/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP`.

## Failure review and changed mechanism

Read AN001 and FP001 in full, their index, the AN001 result, source preview review,
and existing owner-view/import/retarget authoring source. AN001's FK/pelvis retarget
and recoil graph patterns remain stopped. FP001 excludes offsets, sleeve masks
and camera changes as a deformation fix. A hierarchy/hash match is not skinning
acceptance.

First separate three possible causes: bad target bone transforms in the existing
failed derivative; copied/leader poses being mismapped to owner arms; or actual
skin/mesh defects. Compare source, full target and continuous-arm reference poses,
tracks, component-space bones, lengths and scales at identical reload phases.
Use the original compatible Rifle_Reload_2 only as a diagnostic control, not a
visual-approved replacement. Inspect target deformation separately from view fit.

Only if this proves an auxiliary/twist-bone or pose-binding defect, author an
isolated **native existing-pose composition/binding** candidate under a new V2
namespace. Do not rerun the IK retargeter, change finger poses, move the camera,
remesh/reweight the soldier, or construct replacement motions. Document the exact
proved affected bones/binding and algorithm before authoring. If evidence instead
requires relaxing mesh/finger constraints or further reference-pose retargeting,
report the limitation and stop, without disguising it through placement.

## Storage, process and preservation

- Current user-owned UE editor PID44632 is the only writer; its native Animation
  Editor on Entry has original D059 and failed target tabs. Keep its original
  transient M1 preview; do not start another engine or close it automatically.
- Read-only/transient diagnostics can run in this same editor. Python authors or
  observes only; native animation evaluates itself, no per-frame display updater.
- Protect all507 preflight files and5 failed AN001 packages (512 records), vendor
  models/skeletons/materials/fingers/source clips, original gunplay/lifecycle/camera,
  map SHA2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519.
- New evidence: existing single workspace `Evidence/ReloadSleeveAdaptationV2/`;
  new native candidates, if justified: `/Game/ParisCombat/Animation/ReloadSleeveV2/`.
  Never overwrite an occupied identity. No commercial binaries/images in Git.
- Save only new candidate assets, never the Entry/formal map or shared originals.
  No Catalog/allowlist/immutable publication, commit or push.

## Order and early acceptance

1. Capture current process/Git/protected hashes; query animation/ref poses and
   native binding. A read-only diagnostic report must distinguish data from cause.
2. On identical target/phase compare full-body and owner-arm results against the
   compatible control. Early proof: demonstrate the offending transform/binding
   and its causal effect, not just different transforms or a prettier screenshot.
3. If supported, document and build one isolated native composition candidate.
   Inspect start, take, operate, return and finish from front/side and close sleeve
   views, plus original protected FP camera when safe. Check continuous sleeves,
   finite/unit scales, arm lengths and unchanged finger-local samples.
4. One technical correction maximum for this isolated mechanism; preserve failed
   diagnostics. No widening into a full owner Blueprint/recoil/gunplay rewrite.
5. Recheck512 protected records and summarize actual result; stop for visual review
   after a useful sleeve candidate. Fresh-load/gameplay regression is required
   before any future integration; editor preview alone is not that pass.

## Stopping and rollback

Stop if diagnosis is inconclusive, isolated skin test still stretches after one
correction, or a necessary change violates protected constraints. Retain new
unselected assets/evidence; remove only documented transient test actors to return
to the original source preview. Never restore older map/native hashes over work.
This document is a plan, not a completed repair or acceptance record.
