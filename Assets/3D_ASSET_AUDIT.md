# 3D asset inventory and acquisition gaps

Reviewed 30 September 2026 at source revision `701e0c77ab03a23f9da035976c96878e6cc9fd6e`. Chinese review: [model search checklist](3D_ASSET_AUDIT_ZH.md). This is a dependency audit, not authorization to acquire assets or restart the stopped character experiment.

**1 October update:** German Soldier, US Paratrooper and Rifle Animset Pro are now available in the verified private `character-20261001-v1` release, including preserved originals and the repaired UE 5.8.2/Blender lab baseline. See [restoration instructions](Sync/README.md#character-integration-baseline-on-1-october) and [remaining acceptance gates](CHARACTER_COMPATIBILITY_AND_REPAIR.md). The audit below is the earlier sourcing snapshot: do not buy those same bundles again merely because its rows originally described missing capabilities. First-person weapon/arms/reload, final history and gameplay/performance remain unresolved.

## Finding

The city dependency is present. The main acquisition gap is a coherent **rigged character, rifle and animation set** for both factions, including the player's first-person presentation. No accepted production soldier/action set was found in the inspected project. Six initial actors do not require six distinct character purchases: two faction configurations can be reused, with two Allied NPCs and three German NPCs; the player additionally needs a suitable first-person presentation.

Buy/search by complete usable sets, not by attractive isolated meshes. A full-body character, its compatible third-person actions, and a matching first-person weapon/arms kit are different dependencies unless a listing explicitly includes them all.

## Scope and evidence

- Inspected the active `Unreal/ParisStreetCombat/Content` tree, current manifests selected by `Sync/CATALOG.json`, retained gunplay source files, and local experiment deliverable paths and reports. Hidden/ignored model deliverables were included; `.git`, temporary migration backups, the protected SFTP store and experimental dependency archives were excluded from the model-file census. This is not a search of the entire computer or the team's online libraries.
- The active Content tree has exactly 15,850 files and no paths outside the selected city manifest. Its original vendor delivery is a preserved duplicate baseline, not a second environment collection.
- The selected release is `git-assets-20260930-210133`. Earlier source/server verification is recorded in `Sync/README.md` and `Sync/PUBLICATION_STATUS.json`. This audit does not claim a fresh SFTP login/download or teammate restoration.
- Five retained rifle source files were individually checked against the active gunplay manifest: all are present and match SHA-256 and size. Full selected local-asset verification also passed, as recorded below.
- Package filenames, folders and supplier descriptions establish inventory candidates, not an Unreal asset-class/deformation/runtime inspection. No Blender/Unreal editor, old generator, cloud job or paid service was run.

## What is already present

| Resource | Location and storage | Finding and limitation |
|---|---|---|
| Paris environment | `Unreal/ParisStreetCombat/Content/WW2City`; `france-liberation-content` SFTP manifest | 15,850 files across the complete Content dependency, 28,421,951,358 bytes (26.47 GiB). Named WW2City folders contain Environment 1,861, CarsSet 328, Library_Meshingun 780 and Maps 12 files; another 12,869 are external-actor packages. These are file counts, not distinct model counts. Buildings, streets, rubble, props and vehicle candidates are available; city survey, historical dressing, collision, NavMesh and packaging remain untested. |
| Vehicle rigs and background effects | `WW2City/CarsSet/Mesh/*_Rig` and `WW2City/Environment/Mesh/Proxy/Vista/Parachute` | Skeleton/animation-named packages belong to cars, field car, truck and tank. `MI_Soldier_Vista_01a`, `T_Soldier_D` and `NS_ParachuteSoldiers` are background-effect candidates, not evidence of a playable humanoid character. Driving remains outside scope. |
| Rifle Hero01 | `Reference/Gunplay/SourceAssets/RifleHero01`; private SFTP, source scripts/docs in Git | One `.blend` and two FBXs, plus two retained Unreal mesh packages. The recorded pair is 13,172 triangles. Exterior-only study; unfinished UV/baking and no accepted mechanical reload, arms or action set. M1 is a historical candidate, not approved final equipment. |
| Rifle silhouette prototype | `Reference/Gunplay/SourceAssets/RiflePrototype`; private SFTP | Two OBJ meshes and two retained Unreal mesh packages. Coarse study. No hands, clip mesh, clip ejection or reload montage. Old timer-based gunplay is reference code, not an accepted animation set. |
| Lux3D/MPFB soldier pilot | `Experiments/Lux3DCharacterPilot/blender/soldier-mpfb_01_ASSEMBLY.blend` and `models/soldier-mpfb_01_ASSEMBLY.glb`; local-only | Recorded 297,228 triangles and only `Root_StaticBody`, `Neck`, `Head` bones; body remains fixed to root. Head-motion interchange checks are not full-body animation or Unreal acceptance. Remaining collar/body issues. Stopped by the user on 27 September; do not resume or count as production-ready. |
| Other pilot samples | Same experiment: body inspection/refinement, shoe repair and MPFB head files | Sixteen `.blend`/GLB deliverable files were found outside dependency archives, including alternate stages/formats rather than sixteen independent usable assets. Prototype/reference only. |
| Historical and concept material | Selected `historical-reference-assets` and `project-document-assets` manifests | Historical bytes comprise 16 JPGs, 19 PNGs and 3 PDFs. They help verify appearance; they are not 3D characters, weapons, rigs or animations. Concept art does not close model gaps. |

The supplier explicitly excludes the trailer's soldier characters and some combat effects from France Liberation. Its inclusion of vehicle rigs and parachute effects does not change that exclusion. [Official Fab listing, checked 30 September 2026](https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6).

## Assets to find, in priority order

Rows describe missing capabilities, not necessarily separate purchases. An included component closes its row only after inspection; avoid buying duplicate components.

| ID / priority | Find | Minimum useful delivery | Reuse and cautions |
|---|---|---|---|
| CHAR-A / P0 | Finished Allied infantry character | Full-body skinned mesh, usable skeleton/weights, head/hands, appropriate uniform/helmet/boots/equipment, materials/textures; stated rig and available LODs/mesh density | Reuse for two allies and, if the chosen camera design needs it, the player body. Prefer an integrated character over separately assembling head/clothes. Allied nationality/unit remains undecided. |
| CHAR-G / P0 | Finished German infantry character | Same delivery requirements; visibly distinct faction uniform/equipment | Reuse for three enemies. Exact formation, insignia and equipment need historical review; no requirement for three unique heads/models. |
| ANI-TP / P0 | Compatible third-person rifle actions | Rifle idle, walking/running, aim/fire, hit reaction and death; documented source skeleton and action list | Both factions may share a compatible action family while keeping individual gameplay state. Crouch is Should; ragdoll/facial animation is optional. Reload is needed for any NPC reload behavior adopted, with suitable mechanical presentation. A rig alone does not include these actions. |
| FP-KIT / P0 | Player first-person arms and rifle presentation | Skinned arms with suitable sleeves, grip/aim/fire/reload actions and a documented matching rig/weapon; editable alignment/attachment data | A coherent arms + rifle + animation kit is preferred. A tested full-body first-person solution may substitute, but a third-person soldier mesh by itself does not establish first-person suitability. No full facial rig is needed. |
| WPN-A / P0 | Finished chosen Allied rifle | First-person-quality mesh/materials and a world representation; separate moving parts or rig where the chosen reload needs them; required clips/magazines/ammunition props | Can be included in FP-KIT and reused by allies. Existing Hero01 is a prototype fallback, not an accepted finished weapon. Reload type must match the selected rifle; do not reuse arbitrary magazine animations. |
| WPN-G / P1 | Visible German NPC rifle | Correct exterior mesh/materials, scale, grip and muzzle attachment; mechanics sufficient for adopted NPC actions | Still required before final acceptance; P1 only means it can be sourced after the player rig/action choice. Third-person world quality is sufficient; another first-person kit is unnecessary for enemy-only use. Exact weapon is undecided. |

## Listing checks before obtaining anything

1. Ask for the actual included-file and animation list, not just renders. Prefer Unreal-ready content with declared engine/skeleton dependencies, or FBX with a real skinned rig and textures. OBJ/static meshes do not satisfy the soldier requirement. GLB/Blender sources still need a validated engine import route.
2. Obtain the skeleton name/hierarchy, reference pose and animation compatibility information. A claim such as “UE compatible” does not prove that a different pack's actions retarget cleanly. Confirm root-motion/in-place variants against the chosen locomotion design; fingers/grips and weapon-moving parts need appropriate controls.
3. Require UVs and available PBR maps, material/texture counts, mesh/LOD triangle counts and a deformation/movement preview. Prefer ordinary game-distance quality over a cinematic sculpt without a usable game mesh. No untested triangle count is declared a performance pass.
4. Confirm the rifle/arms/action kit uses the same reload mechanism and offers a recognizable ammo insertion/commit moment for gameplay integration. Request weapon part, grip and muzzle information. Include required clip/magazine props in the bundle when possible.
5. Record source, author/version, applicable license and private three-person source-sharing permission before SFTP publication. Check packaged-build distribution separately. Do not assume private sharing or public source visibility grants raw-asset redistribution rights; keep receipts and account details private.
6. Record plausible date/unit/equipment configuration before final historical acceptance. Generic WW2 labels, airborne uniforms or modern tactical clothing are not sufficient. A candidate can undergo technical evaluation before this decision, but must not be marked historically accepted.

Send a candidate's source link, previews, formats/engine version, skeleton/animation list, mesh/texture information and license reference for review. No purchase/download was performed by this audit.

## Avoid spending time on these now

Do not source another city, new tanks/aircraft/drivable vehicles, civilian crowds, extensive interiors, separate photorealistic heads or modular clothing production systems for this MVP. Reuse the existing environment and integrated soldier equipment. Effects/audio and route-specific historical dressing need separate inspection later; no generic effects pack is declared complete here.

## Intake and acceptance

After an asset is actually obtained, preserve its unchanged original and record rights/dependencies before sharing. On this server, permitted assets use one physical home under ignored `Assets/LocalShared/SFTP/`, with immutable baselines separate from one writable workspace; `Assets/LocalWorking/` is only a transitional junction alias, not another copy. Assign a stable ID/owner and follow [new-asset intake](TEAM_SYNC_WORKFLOW.md#6-new-assets-and-original-baselines). Unresolved-rights intake remains private. Git receives source/configuration and exact hash/version records, not model bytes. Do not edit vendor `/Game/WW2City` package names on disk.

Test a separate compatibility map for complete textured import, full-body deformation, locomotion, aim/fire/reload, hit/death, hand/weapon/muzzle alignment and any chosen first-person camera arrangement. Team-authored integration belongs under `/Game/ParisCombat`. Repeat in a packaged build and record results against [ASSET-01 and ANI-01](../Docs/Development/ASSIGNMENT3_ACCEPTANCE.md). Engine association is currently UE5.8; actual asset/UE5.8.2 compatibility is not established by filenames or vendor marketing.

## Local verification record

**Subsequent authorized intake testing:** after this sourcing audit, the user downloaded German soldier, US Paratrooper and Rifle Animset Pro bundles and authorized isolated testing. See [the compatibility and repair record](CHARACTER_COMPATIBILITY_AND_REPAIR.md) for the later verified findings and remaining gates. The sourcing/audit snapshot below does not describe the later lab's mutations or completed tests.

`python Tools/check_asset_storage.py --local --git` completed successfully: all 15,927 selected local files match the catalog's manifest metadata, SHA-256 and sizes; tracked source paths pass the asset-storage check. This covers 15,850 city files, 24 gunplay reference files, 38 historical reference files and 15 document/illustration files. Stopped experiment files are outside the selected catalog and were not included in this hash pass.

This is the 30 September local-file integrity record, not that audit's server or runtime acceptance. The subsequent character repair/publication is recorded separately in `Sync/CHARACTER_PUBLICATION_STATUS.json`; use the actual Git history for source publication status.
