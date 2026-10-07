# Asset catalog and reload review — bounded inspection

Date: 2026-10-03. Owner: yg745. Status: bounded inspection complete; no gameplay/asset selection or publication.

## 4 October addendum — new intake and suspected duplicate

User has supplied Muzzle_Flash_VFX and Firearm_Animations in the two physical
LocalWorking/Intake/2026-10-04 folders and asks for verification/cataloging,
including a suspected repeat purchase. This is read-only asset inspection plus
source/metadata documentation, not gameplay/animation/VFX implementation.

Cases read: failure index, FP001 and GP010, latest human action feedback and
no-new-animation policy. Different approach: compare actual SHA/size and relative
package sets against the original RifleAnimsetPro manifest and its current
physical bytes; do not conclude duplication from title/CRC alone. Reuse prior
class/clip records only when the corresponding original bytes are proved exact,
and label their date/basis. VFX package header/embedded reference/name discovery
is not fresh engine compatibility, closed dependencies or visual acceptance.

Order: inventory/hash stable new deliveries; inspect engine-header version clues
and serialized package reference/class hints without loading supplied scripts;
compare native files and SourceFiles.zip to the existing original; inspect ZIP
members/CRC under fixed expansion limits without extraction; categorize VFX and
relevant motion families; update both Xianyu catalogs and preserve exact evidence.
No live project import, editor restart, original resave/rename, deletion/move,
SFTP publication, purchase or Git commit/push. New sharing rights stay pending.

Evidence: ignored LocalWorking/Validation/2026-10-04-xianyu-intake-v1/Audit/.
Source tool: Tools/AssetValidation/audit_xianyu_intake_20261004.py. Do not overwrite
an occupied report identity. Early acceptance: stable complete file hashes and
an explicit native-relative-path comparison are available. Stop on source/hash
changes, unreadable/corrupt or unsafe archives, unreasonable expansion, or any
need for native authoring/rights/new assets. Record differences; do not delete
even an exact duplicate without a separate cleanup request. Existing guarded
412 gameplay/model/source inputs must remain unchanged. This addendum alone is
not proof of any new test or a repair resumption.

4 October actual result: all369incoming files hashed/stability-checked; old300
RifleAnimsetPro originals rehashed. All298native plus SourceFiles.zip are exact
repeats, no new motions; ZIP324FBX CRC passes without extraction. New VFX68files
has4.26.2/4.26.0 clues, MsvFx_MuzzleFlash_Pack root and10effect candidates; only
file/header inspection, no native load/emission/closure/performance acceptance.
Both catalogs Section11 and source-only audit metadata updated;412guarded inputs
unchanged, no deletions/imports/SFTP publication. Promotional image inspected and
labeled as seller evidence, not runtime capture. Full private audit SHA
c8497e1d626a42d6c142fc6a184678ff8dd73cdd14416b52e6840b51f1c6d8b5.

Final QA's first one-line checker used the Windows GBK default and could not read
UTF-8 Markdown; no asset/evidence bytes changed. Explicit UTF-8 retry passes
source AST, metadata, new catalog links, evidence SHA, all68VFX hashes and412
guards. Catalog whitespace checks pass. Do not count the failed checker as a pass.

## Request and contract

Inspect the newly delivered `MW2_Guns_Asset_Library.blend`, identify possible German WWII weapons, produce a detailed Markdown inventory of the existing Xianyu deliveries with private local images, and compare the currently bound reload with existing D059 reload candidates. This is an inspection/recommendation, not permission to replace animations or select/release assets.

- Inputs: new physical LocalWorking intake; prior original manifests, actual files, native inspection records and existing compatible character/action baselines.
- Use Blender 5.2.2 LTS with automatic embedded script execution disabled. Inspect existing geometry, collections, rigs, actions, images and dependencies; do not save the delivered file or export production content.
- Render small, labeled diagnostic views in ignored `Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/`. Inventory all named weapon groups and all archive titles; distinguish name/catalog discovery from visual/runtime verification.
- Catalog delivery: English original and Chinese review under `Assets/`; private evidence remains outside Git. Markdown embeds refer to verified local images, not copied commercial bytes in tracked folders. No publication of new assets/screenshots or SFTP credentials.
- Reload: current actual binding is `/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Reload_2`, not D059 `W2_Stand_Aim_Reload_IP`. Compare current, D059 aim and relaxed reload using normalized phases and recorded seconds; use actual source skeletons, plus target-rig inspection only when hierarchy/ref-pose admission is explicit. Existing screenshots are labeled historical. No rig/mesh/finger/camera/action/source changes or gameplay ammo-transaction changes.

## Cases read / changed approach

Read `Failures/README.md`, FP001 `FAILURE_ANALYSIS.md`, continuous-arms native result, player-action result, weapon intake and simplified-reload results. FP001 warns that phase-mismatched images, empty-hand animation and functional passes do not prove weapon contact/FP quality. This attempt compares existing content with fixed diagnostic views, records actual current binding, and does not author another holding/offset repair. No from-scratch character production or trial selection.

## Order and early checks

1. Inspect Git/processes, actual intake and existing manifest paths. Preserve unrelated dirty changes. Refuse concurrent Unreal writers. Hash new blend before opening; record file stability.
2. Read-only Blender inventory. Early check: collections/objects are accessible, material image packed/external status is known, named German candidates can be isolated. Stop expensive views if load fails/memory grows unsafely; retain diagnostics, not guessed weapon identities.
3. Collate prior original/native inventories and the 125 archive/preview title pairs without extracting the 24 GB collection. Capture only representative useful visual evidence; list unexamined contents explicitly.
4. Compare reload source/native phases on a transient diagnostic world; save images/JSON only, no map/package saves. If no safe mounted target/source closure is available, use existing source-rig evidence and report the target-adaptation gap instead of adding compatibility flags or duplicating assets.
5. Open the new evidence images, write the two detailed catalogs and comparison recommendation, verify Markdown image paths and final guarded hashes.

## Acceptance / stop / rollback

Acceptance: actual weapon inventory and reviewed images; detailed per-delivery contents/location/status with action and archive lists; current binding vs candidate distinction; evidence-backed keep/replace recommendation with uncertainty. Loading alone does not certify UE compatibility, historical use, weapon-specific reload or license.

Stop if original bytes change, an affected editor is user-owned, an API/render failure repeats without a different bounded diagnostic, or further work needs native adaptation/rights/publication. Preserve failed jobs; close only task-owned diagnostics. There are no source-asset changes to roll back. Do not delete original/failed evidence, replace maps, publish Catalog/allowlist, commit/push, purchase, contact sellers or implement AI/VFX.

## Actual outcome

- New blend safely opened: 53 weapon-labeled collections plus one generic collection; 774 meshes, 274 rigs, zero Actions. Reviewed modern geometry does not fill the WWII German rifle gap; packed images are not PBR/UE/rights acceptance.
- All 125 archive headers read without extraction. Catalogs list delivery classes, prior actual native action names/durations, archive package names, storage status and private images: `Assets/XIAN_YU_ASSET_CATALOG_20261003.md` and `_ZH.md`.
- Reload `compare_v4` completed 42 fixed-phase captures/21 samples on current target versus D059 source rigs, exit 0/clean errors. Reviewed corrected sheets; retain current simplified reload, consider D059 aim only through a later matched-target test: `RELOAD_COMPARISON_20261003.md` / `_ZH.md`.
- Failures retained: v2 missing `Meshes` path; v3 occupied map name. Earlier `new_level` implicitly created a diagnostic-only empty map despite no save call. V4 uses a true transient `/Temp/Untitled` world. Old `packages_saved=false` does not prove no early lab map creation. Initial sheet orientation corrected in separately named v2 sheets. No formal game packages saved.
- Initial Markdown had Windows stdout encoding corruption; regenerated from original UTF-8 facts with explicit UTF-8 stdout, corrected German original directory, checked text/evidence paths. A document-output failure, not asset corruption.
- Final size/SHA checks cover new blend, 43 retained native files, 7 action drafts, 206 published non-city native files and 2153 original files across four manifests. Overlapping records are not physical copies. Link/hash evidence is ignored `Catalog/final_verification.json`; task-owned Unreal jobs closed.
