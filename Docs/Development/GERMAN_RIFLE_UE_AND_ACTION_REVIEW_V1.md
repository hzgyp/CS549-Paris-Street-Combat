# German rifle UE integration and existing action review

4 October 2026. Owner: yg745. Authorized work package: step 1 only.
This plan precedes implementation; its presence is not a test pass.

## Scope and protected foundation

Use the Catalog-selected `german-rifle-model-20261004-v1` packed GLB, existing
Paris city, both soldier baselines and the already function-tested player V6 /
owner-view V1. Do not rebuild/refine the accepted rifle, people, fingers, source
motions or camera. Keep Allied M1 and the existing ammo/reload/damage graphs.
World presentation for the three Germans is the bounded rifle target, not a
German first-person kit, moving bolt, reload replacement, ADS, VFX or NPC AI.

Current city SHA: `2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`.
The native-playtest release, 43 retained native files, seven action drafts,
referenced source motions, original city maps and 16 accepted model files are
hash guarded. Fetch/read Git first; preserve the dirty worktree and unrelated
edits. No automatic commit/push or new Catalog/release selection.

## Cases read / different mechanism

Read Failures/README, FP001 analysis, GP009 analysis, the player-action V5/V6
safety record and the accepted model publication result. GP009 requires checking
the imported native mesh, not a Blender beauty render. FP001 forbids judging
contact/framing from unchanged hashes or numerical convergence. Player V5 shows
that zero velocity alone cannot prove prone safety. Reuse verified V6, do not
author another locomotion system or restart the rejected visual approaches.

This attempt imports the already accepted export with a declared axis/unit/frame
conversion, then fits only the new rifle to existing German hand data. Standard
Blueprint nodes own runtime attachment; Python stages/tests only. No IK, hand
editing, forearm masks, camera offsets or repeated offset searches.

## Storage / concrete changes

- New tools under `Tools/Integration/`, metadata under `Assets/Integration/`.
- New native assets only under `/Game/ParisCombat/Weapons/GermanRifleUEV1/`.
  Physical home is the existing single writable gameplay Content at
  `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/`.
  This is integration work on accepted dependencies, not a new original intake.
- Evidence under that workspace's `Evidence/GermanRifleUEV1/<unique identity>/`;
  logs/guard journals under ignored `tmp/german-rifle-ue-v1/`.
- Existing accepted model workspace is read-only input. No additional working
  Blender/GLB copy, editor-aware package renames or old release overwrites.
- Stage the three new guns and action player only in the unsaved real city.
  Do not select/save the canonical map before human review. Subsequent approved
  selection/publication is a separate recorded transaction.

## Integration contract and early checks

The supplied GLB has 24 meshes / 24,466 triangles / 14 used materials / 36 PNGs,
approximately 110.73 cm long. Import one combined movable static mesh with
original normals/UVs, no weapon collision, no automatic Nanite or new animation.
Verify the complete material/texture closure, import triangle count and bounds.
Engine import master-material/plugin dependencies must be recorded.

Existing shot code uses a virtual weapon root with local muzzle `(0,83.23,0)` cm.
Do not assign a centered GLB to WeaponAppearance blindly. Declare and measure a
rigid native conversion to this frame; calibrate the actual grip separately.
Source geometry/scale stays unchanged. Bind new appearance only after its actual
muzzle agrees within 0.5 cm and barrel direction within 1 degree; otherwise leave
Germans unarmed and record the blocker. No damage from a mere visible gun.

First falsifiable check: fresh UE import has one correctly assembled mesh,
24,466 triangles, expected length within 0.5 cm, correct wood/steel materials and
embedded texture coverage. If assembly/orientation/materials fail, stop before
attaching to three soldiers. One diagnosis-based import correction is allowed
under a new identity; no modeling refinement or parameter sweep.

## Order and acceptance

1. Verify no user-owned editor, current source/asset hashes, engine UE5.8.2,
   Content mapping, free space and ownership. Snapshot exact guards.
2. Import into a new namespace; save only new assets. Inspect actual native mesh,
   texture color spaces/mips and material bindings. Fresh-load in another engine
   process with ParisEditorBridge disabled.
3. Author a separate rifle attachment Blueprint using the existing holding
   mechanism and calibrated anchors. Fresh-stage Germans in the real city;
   inspect idle, original walking and reload contact, deformation and direction.
   Generic reload contact remains a limitation, not M1/German mechanical proof.
4. Regress the unchanged action player/combat and navigation as relevant to
   new attachments. Use continuous motion tests without frozen captures for
   functional claims; separate staged views for visual diagnostics.
5. Open an unsaved native-Blueprint human review containing the existing action
   candidate and the new German guns. Python's startup callback unregisters when
   ready. Provide WASD/Shift/Alt/Space/Ctrl/Z and fire/reload instructions.
6. Stop for Yupu's physical-input/body/contact/eye-height/weapon appearance review.
   Record each status separately. Do not call the integration selected, published,
   historically approved, AI-complete or Assignment 3-complete.

History remains provisional: August 1944 Paris setting, player/enemy unit and
exact mission date/weapon variant are not fixed here. V15 has modern SP-R donor
details and is a fictionalized technical derivative, not a certified Kar98k.
Technical review does not close that historical gate.

## Stop / rollback

Stop on source/hash/ownership conflict, occupied identities, unexpected dirty
original packages, failure of early import/muzzle checks, runtime bridge/Python
dependency or visible major contact/clipping. Preserve failed new assets/evidence;
allow at most one causal correction per failed mechanism. User-owned review
processes are never killed automatically. Task-owned jobs have bounded deadlines.
Rollback is to discard unsaved staging and keep the existing canonical map and
release; never restore older hashes over unique new work. No SFTP object/release
publication, broad cleanup or further modeling is included in this package.

## Execution addendum for the bounded native correction

Import V3 succeeds with 58 native files (one combined mesh, 14 materials,
42 native textures and one private import pipeline), 24,466 triangles,
110.7304058 cm length and muzzle Y83.2300034 cm. No bad D/N/ORM color-space
settings were found. Extra repeated normal texture assets are importer output;
their cause/equivalence has not been proved, so no speculative deduplication.

Preserve the aborted import_v1 (preflight source rows lacked a stored size),
import_v2 unavailable `unreal.duplicate_object`, review_v1 label mismatch and
review_v2 protected-ammo setter failure. Tool corrections do not prove visuals.
Review_v2 also proves V1's effective component collision remained
QUERY_AND_PHYSICS despite the initial CDO setter; this is a native safety failure.
Create new attachment V2, do not resave V1: final-compile default NoCollision plus
explicit native BeginPlay SetActorEnableCollision(false). Recheck actual runtime.
Use original ammo defaults/shot/reload interfaces, never unlock/edit ammo fields.
The three inspected review_v2 images show usable static form/wood/hand placement,
not reload, player-action human or whole-game acceptance. Continue one corrected
fresh review, then stop if collision/holding still fails. V1 stays unselected.

Review_v3's raw strict-scale assertion fails on one 0.9999997318 sample. Preserve
it and independently validate recorded numeric samples using a declared 1e-6
unit-scale tolerance (not permission to resize the model). No additional native
authoring follows this harness correction. Seven actual images are inspected:
static holding is reviewable, but generic reload/open hands remain limited;
early/mid rendered poses appear repeated despite different bone snapshots and
late/recovery views have foreground obstruction. These are not matched-phase
reload-contact acceptance. The next package addresses reload separately; this
package stops at human ordinary-holding/player-action review without selection.

Combat_v1 retains a fixture failure: the legacy unarmed-German negative case now
uses an equipped German and its real shot correctly consumes a round. Other
assertions/ammo conservation pass, but do not label the whole run passed. One
test-only correction in a separately recorded harness removes WeaponAppearance
for that single negative call, restores it in finally, and reruns under v2. No
gameplay graph/source ammo mutation or NPC auto-fire is added. New native rifle
namespace is explicitly ignored through the Content junction as well as SFTP.
