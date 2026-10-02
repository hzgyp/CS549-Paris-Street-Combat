# Selective weapon / animation intake validation V1

Date: 1 October 2026. Owner: Yupu Guo (yg745), integration reservation.
Source checkpoint: `37de536`; preserve existing dirty source and all 25 unpublished gameplay drafts.

## Authority, scope and contract

Yupu authorized testing the three new deliveries and using only resources needed by the project. He explicitly confirmed private three-member sharing of their original and adapted files in this conversation. This is an owner attestation, not independent vendor-license verification or permission for public asset/source redistribution or a packaged game. No purchase or detailed character creation is authorized.

Intake is physically `Assets/LocalWorking/Intake/2026-10-01/`: ShooterStarter FPS Arm A, Rifle Pro - MoCap Pack D059, and an assorted UE4 animation collection. Preserve original deliveries and directory structure. Password-bearing directory names and extraction passwords stay private; sanitize public paths and never print passwords or put them in process command arguments, public metadata or logs.

Existing P3 deficiencies in `WEAPON_CAPABILITY_REVIEW_20261001.md` are the selection criteria: dedicated FP arms/camera; compatible idle/aim/fire/reload actions; correct hand/weapon contact; weapon moving parts/ammunition for a demonstrated WWII reload; usable German rifle; action/ammo event integration. The provisional M1 appearance is not a complete kit. Modern-rifle clips/models cannot silently become a WWII weapon selection or certify M1 en-bloc reload. A lower-detail diagnostic representation needs explicit approval if the full kit remains absent.

## Storage and changes

- Original files stay in the physical ignored intake until relevant acceptance/sharing gates pass. New validation work stays in `Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1/`; it is not the live Paris project or a published release.
- Use one isolated native lab with a clean team-owned descriptor/config; never execute vendor build scripts, utilities, installers, downloaded Python or unknown plugins. Do not overwrite active city/soldier assets, vendor skeletons, original configuration or prior drafts.
- Stage only required Content roots, preserving package identity and dependency closure. Exclude Saved/Intermediate/DDC/logs and bundled source wrappers from the native test tree. Broad candidate registry inspection is discovery, not approval to add all animations to the game.
- Inventory archives before extraction. Extract only selected candidates/dependencies, into a refused-if-occupied task-specific directory. Reject absolute/traversal paths, symlinks and unexpected destinations; apply expanded-byte/file-count limits. Never unpack the entire 24 GB collection merely because it is available.
- Git receives this plan, reusable authored tools, sanitized selection/result/provenance/hash metadata. Models, captured pixels, logs and credentials stay ignored. No Git commit/push is requested by this task.

## Execution order and evidence

1. Inspect Git/remote state and local incoming files without overwriting drafts. Record per-delivery file counts, sizes and SHA-256; record changed/incomplete files honestly. Identify duplicated Rifle packages against the existing accepted family before creating another copy.
2. Discover existing native content/action names and archive listings. Select a minimal relevant set: FP hands and matching idle/ADS/fire/reload; supporting movement/cover only if it fills a recorded gap. Reject fantasy, civilian, swimming/driving/parachuting and unrelated combat packs from this integration scope. A name is a candidate signal, not evidence of its contents or quality.
3. Stage selected native dependencies and fresh-load in UE 5.8.2. Inspect meshes/skeleton hierarchy, scale, skinning, materials/textures, PhysicsAssets/sockets, action skeletons/duration/tracks/root motion, notifies and dependencies. Investigate failures before resave; do not infer a coherent FP kit from successful registry discovery.
4. Test required poses/action phases with the actual arms/weapon in a controlled lab: idle/aim, fire, early/insertion/late reload, extremes at elbow/wrist/fingers and required motion/contact samples. Review fixed FP and external views for occlusion, grip penetration, detached parts, material defects and deformation. Select/bound camera settings and document sight/muzzle/grip targets. No full-body from-scratch modeling.
   - Check reference local rotations/translations, not just common names and parents. An in-memory compatible-skeleton declaration is a diagnostic trial only; materially different bind/reference poses require evaluated retargeting before use. Keep failed capture V1; run the daylight/1cm near-plane/reference-pose controls as V2 in a separate evidence directory. Do not retarget a generic reload into a claim of weapon-specific contact without the actual chosen weapon/parts.
5. Use Blender 5.2.2 only for needed exchange/weight/material/rig diagnostics or bounded adaptation. Export selected native meshes/actions through rendering-enabled UE; fresh-import and compare hierarchy/weights/material paths/timing/scale. A passing FBX does not replace native UE material/AnimBP/physics dependencies.
6. Resave the selected usable native dependency closure in UE 5.8.2 and fresh-load it without authoring bridges. Recheck affected visual/action samples after changes; preserve originals. Package/header conversion alone is not compatibility/contact/gameplay acceptance. Record whether M1-specific reload and enemy rifle gaps actually close; if not, stop that use at its documented decision gate without claiming all missing assets are supplied.
7. For accepted, rights-cleared selected subsets only, prepare immutable SFTP publication with original provenance and dependency-complete adapted outputs. Verify retained source/final SFTP bytes before active manifests. Grant shared CRUD to published asset areas without changing the chroot root. No wholesale collection/game import. Preserve originals/history and clean only verified redundant LocalWorking copies, retaining aliases only where tools need them. Incomplete findings remain local and unpublished.

## Acceptance and stop / rollback rules

| Gate | Evidence required |
| --- | --- |
| Preservation | Original hashes unchanged after extraction/staging/tests; no prior draft/live Content mutation. |
| Selection | Every admitted package closes a recorded gap or is a required dependency; excluded collection remains outside runtime/release. |
| Native compatibility | Fresh UE 5.8.2 load, complete references, required renderer/plugin compatibility and saved adaptation header evidence. |
| Appearance/deformation | Opened evidence views with usable FP framing, required joint motion, materials and hand/weapon contact. |
| Weapon semantics | Actual selected weapon/action/moving-part reload representation; do not relabel modern/generic actions M1-specific. |
| Release | Rights attestation, full selected dependency inventory, immutable final bytes verified, matching catalog metadata; teammates' actual restore is separate. |

Failure preserves originals, unique edits and failed evidence. Retry only the diagnosed cause on a new/adapted lab copy. If an essential dependency or weapon-specific representation is absent, report the exact remaining gap and continue independent checks; a weapon substitution, reduced presentation, new purchase or public licensed-asset disclosure needs the relevant human decision. No automatic whole-tree deletion or merging into occupied destinations. Maintain ignored lab `work_state.md` at meaningful checkpoints and a sanitized dated result in Docs/Development.
