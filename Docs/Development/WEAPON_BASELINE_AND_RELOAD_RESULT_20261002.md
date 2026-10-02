# Selected weapon-motion baseline and simplified reload checkpoint

Date: 2 October 2026. Contract: [V1 plan](WEAPON_BASELINE_AND_SIMPLIFIED_RELOAD_V1.md). Selected baseline publication and bounded reload transaction are complete. This is not final P3/P4, playable-build or course acceptance.

## Useful new material

D059 provides a useful **generic source-motion baseline**. Fifteen clips were selected: aim idle, single fire, generic reload, four aim-walk directions, three aim-walk starts, two forward-walk stops, aim-to-relaxed and two deaths. Its mannequin/skeleton/material/texture/physics closure comprises **33 native packages**. Clean descriptor/config bring restoration to **35 files / 18,974,540 bytes** (18.1 MiB). This replaces neither the soldier rig nor a weapon-specific first-person kit.

Actual source-rig validation sampled 465 poses and captured 90 full-body front/side views at start/middle/end. All three contact sheets were opened and reviewed: no gross limb collapse in those views; generic reload changes hand pose and returns. Root motion is disabled and sampled root translation is zero in all fifteen clips. Pelvis motion during starts still needs CharacterMovement/contact integration. Death floor/physics, soldier retargeting, hand contact and FP framing are not accepted by these tests.

Selected adapted packages were resaved in **UE 5.8.2-56702186**. The modern M4 editor-preview attachment was removed from the adapted skeleton, without changing reference pose or motion tracks. A clean-project fresh load passed all 33 packages and recorded built-in **ACLPlugin** compression dependencies; enable this bundled engine plugin when restoring. No downloaded plugin is admitted. Originals remain unchanged.

## Storage and publication state

- Untouched D059 was moved once to `Assets/LocalShared/SFTP/baselines/rifle-pro-mocap-original/rifle-motion-20261002-v1/`: 1,563 files / 1,944,249,213 bytes. It is provenance/rollback, not default whole-pack restoration.
- The single writable selected tree was moved to `Assets/LocalShared/SFTP/workspaces/yg745/rifle-motion-ue582-v1/`; its old LocalWorking path contains no second copy.
- Thirty-five immutable hash objects and two release manifests were written via authorized SFTP. Final selected server bytes were checked; all 35 selected files were actually downloaded and SHA-256 verified.
- **Adopted into CATALOG:** `rifle-pro-mocap-ue582-selected`. The initial original read failure was inherited download-folder ACLs. Yupu approved Windows elevation; the exact helper verified shared Modify on 1,586 original-tree and 92 workspace entries. Protected root ACL/ownership remained unchanged. Repeated actual SFTP verified both manifests, all 35 selected files, an original sample, and workspace create/overwrite/rename/read/delete.
- Authority: `Assets/Sync/RIFLE_MOTION_PUBLICATION_STATUS.json`, `CATALOG.json` and its selected manifest. **Do not rerun publish/recover/client/adopt** into this occupied version. Preserve immutable history. New modifications need a new version, not an overwrite.
- Cleanup proved all 753 remaining discovery-native files identical to retained untouched originals before removal: **135,629,202 bytes** freed. Evidence and ShooterStarter candidates remain; the old lab `Content/Rifle_01` mount is a verified junction to the single writable selected workspace. No original/version/history bytes were removed. All 2,420 delivered files and 25 prior gameplay drafts remain hash-identical. No Git commit/push.
- At handoff, 102 task-generated verification download copies were separately rehashed against retained working/original files and removed (51,535,660 bytes). Final SFTP objects, original baselines, current writable files, manifests, logs and test records remain. Temporary asset downloads are not additional permanent local homes.

ShooterStarter arms remain LocalWorking candidates: different reference rotations, failed direct FP framing and modern sleeves/gloves. The assorted UE4 collection remains unselected; four inspected catalogs mainly overlap existing rifle families. Do not integrate the entire collection merely because it was purchased.

## Simplified reload and remaining gaps

Yupu approved simplified reload. Prepared Blueprint-authoring source uses a generic animation and a labeled halfway animation-position marker, not M1 en-bloc/bolt/finger simulation. One owner tracks capacity/loaded/reserve and guarded action/generation IDs. Start transfers no ammo; the marker transfers once at most; cancel/death/stale events cannot create ammo. Watchdog expiry cancels, never commits. Debug capacity values are fixtures, not historical approval.

Three new normal Blueprint assets were generated and saved under `/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/`: shared `BP_PCCombatantReloadV1`, player and NPC children. All physical bytes are in the existing owner-specific SFTP runtime workspace through the verified active-Content alias. Earlier drafts/vendor models were not overwritten. Gameplay calls standard engine/Blueprint nodes, not ParisEditorBridge.

Actual native-world tests passed **18 groups / 432 assertions**: player/NPC × 0.5/1/1.5 playback × 30/60/120 fixed simulation steps per second. Coverage includes busy/fire rejection, early marker rejection, normal one-time transfer and finish, duplicate commit/end, repeated reload conservation, partial reserve/empty loaded, before/after cancellation, absent marker timeout without ammo, wrong action/generation, death before/after, reset invalidation without refill, full/no-reserve/invalid ammo/capacity and zero/NaN/infinite rate rejection. The clip is 2.166667 s; placeholder commit is 1.083333 s. These step settings are **not measured game FPS**.

Bridge-disabled fresh process passed all three packages, default values and package dependencies. Twenty front/side static pose views (five times on each actual Blueprint mesh) and 150 joint records were produced in `Views_v2`; both sheets were opened/reviewed. Visible hand/body changes occur without gross limb collapse in these views. Empty hands, coarse sampled poses and unverified floor/accessory contact do not establish M1 insertion, first-person grips or final retarget acceptance. No native mesh/clip/map was saved by view capture.

Private immutable diagnostic snapshot: **28 native drafts / 12,743,253 bytes**, including the unchanged old 25 and three new reload packages. All 28 final hash objects and the snapshot manifest were actually SFTP-downloaded and size/SHA-256 verified. Matching metadata is `Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json`; `/releases/paris-reload-draft-20261002-v1/draft-snapshot.json` is a rollback checkpoint, **not CATALOG-selected production/restoration authority**. It depends on the published character baseline, is not a stand-alone playable build, and must not overwrite another owner's work. The three new writable Blueprint files also passed authenticated SFTP reads/hash comparison and UUID-probe CRUD. Root ACL unchanged. No Git binary allowlist or staging/push change.

### Preserved failures and evidence

The first generation failed because pure `GetPosition` was incorrectly given an execution connection. Editor helper v21 fixed the source and compiled/deployed successfully; authoring v2 passed. v20 used NoHostPlatform and produced no editor binary, so it is **not** native compilation evidence. The first fresh probe used snake-case for a Blueprint-authored property; exact FName lookup fixed only the test script, fresh v2 passed. Initial static views repeatedly reused SingleNode AnimationData and showed stale poses; they are retained as invalid sampling evidence. V2 forces transient instance initialization, checks actual position and rejects unchanged hand samples. Failed logs remain, not passed results.

Known non-fatal warnings are retained: deliberately stale/out-of-state commit probes eagerly evaluate the pure position getter while the mesh has returned to AnimBP mode. Ammo/state rejection still passes; short-circuit the token/state gate before that getter in the next action revision to avoid log noise. Static-view scripts also use a deprecated level-load wrapper. Neither warning is missing dependency or a zero-warning production claim.

Canonical runtime evidence is `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P4/SimplifiedReload20261002/`: `author_v2.json`, `probe_30_v1.json`, `probe_60_v1.json`, `probe_120_v1.json`, `fresh_v2.json`, `Views_v2/pose_views.json` and reviewed sheets. Scripts: `ue_simplified_reload.py`, `ue_reload_pose_review.py`, `snapshot_reload_drafts.py`, `verify_reload_workspace.py`. Editors/commandlets were closed at handoff.

Next bounded work: connect actual reload input/visible ammo feedback, attach/alignment-test the existing provisional world rifle, and implement shot obstruction/trace/damage under the P4 manual. That requires live input/view and collision tests; it does not require reopening detailed character production or purchasing a modern substitute. Final FP/contact/history/performance/packaging gates remain open.

| Missing capability | Current treatment |
| --- | --- |
| Coherent WWII FP arms, historical sleeves and matching actions | Not accepted from this delivery; preserve candidate diagnostics |
| M1 bolt/clip/round props and specific reload | Defer detailed parts/contact; generic simplified presentation |
| German rifle/approved variant | Still missing; MP40 is not a rifle substitute |
| Grip, muzzle clearance, sights/ADS, soldier contact | Requires attachment/retarget and live view tests |
| Public packaged-game rights and historical configuration | Private team sharing does not establish either |

No purchase, modern-weapon substitution or resumed detailed character production was performed.
