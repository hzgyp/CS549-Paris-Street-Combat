# Selected motion baseline and simplified reload implementation V1

Date: 2 October 2026. Owner: Yupu Guo (yg745). Starting source: `37de536` with preserved dirty changes and 25 unpublished gameplay drafts.

## Current authorization and contract

Yupu now explicitly authorizes keeping usable new assets as baselines, recording missing capabilities, and **simplifying reload first**. This supersedes the previous pending reduced-presentation choice, not the outstanding asset/history/packaging gates. Private three-member original/derivative sharing of the three deliveries was confirmed. No purchase, modern-rifle substitution, public vendor-byte distribution or detailed character production is authorized. No Git commit/push is requested by this message.

Use UE5.8.2 and Blender5.2.2. Follow `WEAPON_ASSET_VALIDATION_RESULT_20261001.md`, `CHARACTER_AND_WEAPON_IMPLEMENTATION_V1.md` and `Assets/TEAM_SYNC_WORKFLOW.md`. Ordinary bounded implementation/tests continue without another intermediate approval.

## A. Useful baseline selection and publication

1. Verify source/Git and external-asset state; preserve originals and previous drafts. Use the existing weapon discovery lab, never rerun staging into it.
2. Select a small D059 generic-motion subset: aim idle, single fire, generic reload, forward/back/left/right aim-walk, forward and 90-degree left/right aim-walk starts, two forward-walk stops, aim-to-relaxed and forward/back death. These support aim locomotion/start-stop transitions and provisional actions; they are not M1-specific/FP contact acceptance. Keep its original mannequin/skeleton/material/texture/physics dependency closure for reproducible source-motion evaluation.
3. Check actual registry dependencies and reference transforms. Test full sequences on the original compatible mannequin, compare needed soldier-target compatibility separately, inspect controlled captures and finite joint/geometry bounds. Reject unexplained missing dependencies or gross deformation; root-motion and contacts are recorded, not assumed from clip names.
4. Save only the accepted selected native closure in UE5.8.2, preserving package namespaces and original deliveries. Move that closure into a clean minimal verification descriptor, without another full working Content copy. Fresh process verifies no missing references, persisted duration/skeleton/material settings and UE5.8.2 headers.
   - The selected working packages are moved into one minimal physical LocalWorking projection, not cloned; fresh load uses only that Content closure. Removing the editor-only M4 attachment needs a small editor-bridge helper because Python does not expose `FPreviewAssetAttachContainer`. Its source-rig reference poses/actions are unchanged. UE5.8.2 resave introduces the engine-bundled ACLPlugin compression assets; enable/record this engine dependency explicitly, never copy an unknown downloaded plugin.
5. After the subset passes its defined **generic source-motion baseline** checks, preserve the complete D059 delivered bundle once as an immutable original SFTP baseline (provenance/rollback, not automatic runtime restoration). Publish only the selected native closure in an active restoration manifest, with the bounded test scope prominently recorded. No collection-wide or all-animation runtime admission. Keep pending ShooterStarter/civilian collection outside SFTP until their own use gates pass.
6. Relocate the selected editable tree once to `Assets/LocalShared/SFTP/workspaces/yg745/rifle-motion-ue582-v1/`, verify all selected bytes, and retain a lab junction only for scripts that need the old editor path. Original and versioned object bytes are separate from this writable tree. Preserve prior diagnostics. Remove only redundant task-generated discovery copies after original/retained hashes are proven, not original deliveries or unique edits.
7. Verify immutable final-server bytes, actual shared-account SFTP read/CRUD and manifests before Catalog adoption. Grant shared-account Modify only in these published areas; root ACL unchanged. Git receives hash/version metadata only. Teammate restoration and public-build rights remain separate.

ShooterStarter provides a technically inspectable arm mesh but its current rig/action/camera and modern appearance fail the intended FP-use gate. Do not label it game-ready or publish the modern rifle to fill a WWII gap. The assorted animation collection mostly duplicates relevant families; leave unrelated/untested packages unselected.

## B. Simplified reload behavior

Use a new team-owned **Blueprint** action draft, retaining earlier lifecycle drafts untouched. Editor-only ParisEditorBridge may author/test normal Blueprint nodes because installed Python cannot create those graphs; generated gameplay must not call or inherit bridge classes. No C++ runtime ammo system.

The simplified reload is a labeled generic capacity/reserve model, not simulation of M1 en-bloc mechanics. Preserve existing provisional M1 appearance without selecting a new historical variant. This slice can validate the action transaction without an accepted FP arm kit; it cannot mark FP sights/grips/parts or final presentation passed.

- Authority: one owner holds LoadedAmmo, ReserveAmmo, Capacity, ActionState, ActionID, RestoreGeneration and ReloadCommitted. Initial debug capacity/reserve values are test fixtures, not historical weapon rules. Parent lifecycle retains death/reset ownership.
- Start: reject dead/busy/full/no-reserve requests; increment ActionID, snapshot current generation and start a named simplified animation/presentation. No ammo transfer on start.
- Commit: an explicit **animation-phase** event reaches a documented simplified marker; carry the captured action ID/generation. Check alive/reloading, matching token and not-yet-committed. Transfer `min(Capacity-LoadedAmmo, ReserveAmmo)` exactly once. This marker is a placeholder, not proof of physical clip insertion.
- Finish: the matching end event returns the action to Ready. A missing commit/end is cancelled by a watchdog; timeout **never creates ammo**. Before-commit cancel transfers nothing; after-commit cancel preserves the single transfer. Duplicate/stale/wrong-generation events do nothing.
- Death/reset invalidate tokens through the existing lifecycle. Reset/restore ammo is an explicit test fixture or later checkpoint snapshot, never automatic healing/refill caused by a save.
- Fire requests while reloading are rejected for this bounded slice. Shooting obstruction/damage, input/HUD and full mission remain later checks; a simple test decrement is not a gunplay pass.

## Order, acceptance and rollback

Complete A selection/native regression and publication, then B simplified action transaction. Record actual tests and missing assets in a dated result. Preserve failed outputs and use unique evidence identities. Any unmatched references/pose defect blocks that candidate's release, not independent action-logic work.

## C. End-of-task diagnostic checkpoint

After the native transaction and bridge-disabled load checks, close affected editors and preserve the three new Blueprint packages with their 25 unchanged local draft dependencies as a private immutable **diagnostic snapshot**, not a production asset baseline. Verify old hashes first; transfer only missing hash objects, download every snapshot file for size/SHA-256 comparison, and keep the protected root ACL unchanged. Store matching snapshot metadata in `Assets/Integration/`; retain the dated 25-file inventory unchanged. The snapshot depends on the already published character native baseline; it is not a stand-alone build. Do not add unfinished gameplay drafts to CATALOG or the Git binary allowlist. Current working files remain in the one owner-specific writable workspace; versioned snapshot bytes remain separate. Record exact test coverage and open FP/contact/input/packaging gates. No commit/push without user request. Any failed transfer/verification leaves metadata unadopted; never overwrite an occupied immutable snapshot.

Tests for B: normal/partial/empty-reserve/full reload; repeated reloads; duplicate and stale/wrong-token events; cancellation before/after commit; death/reset during reload; missing marker/watchdog; invalid capacity/reserve; repeated finish; and the same transaction at 0.5/1/1.5 animation rates. Fresh load with bridge disabled verifies runtime dependency isolation. Engine tick/frame-rate settings are test inputs, not measured FPS. Inspect any animation/view output before claiming it useful. No packaged or actual input-device acceptance is implied.

Missing capabilities remain explicit: coherent historical FP arms/weapon contact, M1 moving parts/clip/rounds and weapon-specific reload, German rifle, historical sleeves/gloves, contact/ADS and public-build distribution permission. Simplification unblocks diagnostic implementation only.
