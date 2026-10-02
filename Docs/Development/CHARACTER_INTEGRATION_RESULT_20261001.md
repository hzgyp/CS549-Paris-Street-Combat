# Character integration result — 1 October 2026

**Later checkpoint:** [Character movement result](CHARACTER_MOVEMENT_RESULT_20261001.md) adds shared Character Blueprints and measured movement/collision. The initial-preview snapshot below is preserved; its statements about the sole new map/no authoring bridge describe that earlier pass, not the latest working state. Full P2 remains unaccepted.

Owner/tester: Yupu Guo, with local automation. Starting source revision: `37de53688530d379d73115a22604bd7ee02c03c9`; implementation-plan and tool changes are uncommitted. Asset baseline: `character-20261001-v1`. Follow the [implementation plan](CHARACTER_AND_WEAPON_IMPLEMENTATION_V1.md) for remaining work.

## Verified storage and dependency results

| Check | Actual result | Limit |
| --- | --- | --- |
| P0 Git readiness | Fetched `origin`; HEAD and origin/main had zero ahead/behind commits. Existing documentation edits preserved. | No new commit/push in this task. |
| P0 canonical storage | 15,850 city files and 540 native character packages moved on the same volume; every selected file passed SHA-256/size before and after relocation. Runtime Content initially contained 16,390 files. | Required originals, immutable releases and private backups preserved; this is not asset-history cleanup. |
| P0 aliases | Active project Content and four lab character mounts resolve to the same physical runtime tree; five junction checks passed. | Never open the lab and game as simultaneous writers of those packages. |
| P0 permissions | Shared account passed actual local SFTP create/overwrite/rename/read/delete in the new workspace; downloaded probe SHA-256 matched and unique probes were removed. OpenSSH root ACL stayed unchanged. | Local connection only; not teammate restoration or external reachability. |
| P1 native closure | Fresh active-project UE **5.8.2-56702186** loaded **540/540** selected packages, zero inventory/probe errors. | NullRHI structural inspection; not rendered appearance or gameplay. |
| P1 eyes/rigs | All four adapted meshes retained exactly one intended PBR eye-material binding and their native skeleton/PhysicsAsset references. | Does not establish full skin/contact/ragdoll or historical approval. |
| P1 city package | `/Game/WW2City/Maps/LV_Paris_WW2` loaded as a World package object. | Not an editor survey, external-actor streaming, collision/NavMesh or city-rendering pass. |

Storage completed at 14:25:14 EDT; authenticated storage check at 14:25:50. P1 completed at 14:27:50. The commandlet exited successfully; its summary reported zero errors/warnings. Startup messages about unavailable non-Windows SDKs and uncached NTFS-journal discovery do not establish a Windows packaging failure or pass. No system journal settings were changed.

## Physical storage and ownership

Canonical writable runtime Content is `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/`. `Unreal/ParisStreetCombat/Content` is its junction alias. Character mount identities remain `/Game/GermanSoldier`, `/Game/USParatrooper`, `/Game/RifleAnimsetPro` and `/Game/ParisCombat/Characters/Adaptation`.

The four old lab directories under `Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Content/` are aliases to the corresponding runtime mounts. Lab diagnostic maps/exchange evidence remain separate. This relocation creates no second complete editable character/city copy and does not redirect an editor into immutable originals/objects.

Yupu retains the binary editing reservation across both aliases. All team members have technical shared CRUD; that is not permission for concurrent edits or changing published versions. Existing selected manifests still resolve through the old lab aliases with unchanged hashes. Do not rewrite immutable release manifests merely to describe this workstation move. The next authorized native release must establish runtime restore destinations and explicitly supersede lab restore paths without competing owners.

## Presentation checkpoint

**P2 is partial, not accepted as a whole.** A team-owned diagnostic map was saved at `/Game/ParisCombat/Tests/Integration/P2_CharacterPreview_20261001`. It contains three Allied and three German SkeletalMeshActors playing native in-place idle/walk/run previews, a controlled floor and two diagnostic obstacles. They are not playable Characters or AI agents.

The render-enabled process used the active project's DX12/SM6 configuration without changing its renderer or descriptor. Four adapted meshes were sampled at 0, 0.5 and 0.999 of each of seven sequences: `Rifle_Idle`, `Rifle_WalkFwdLoop`, `Rifle_RunFwdLoop`, `Rifle_ShootOnce`, `Rifle_Reload_2`, `Rifle_Hit_C_1` and `Rifle_Death_3`, all under `/Game/RifleAnimsetPro/Animations/InPlace/`. All **84** sampled poses had finite pelvis/head/hand/foot positions. Walk/run/reload/death had measured pose variation; across the four variants, walk maximum checkpoint displacement was 18.455–24.376 cm, run 22.775–23.638 cm, reload 10.825–13.218 cm and death 142.187–156.133 cm. These are sampled bone displacements, not locomotion distances or foot-slip measurements. Sparse numeric samples do not certify complete skin deformation.

Two 1600×1000 group captures and four initial head captures were generated. Reviewed group views showed resolved clothing/equipment textures and posed meshes, but some sampled feet were above the floor. The initial head views obscured the face with helmet shadows and were unsuitable for eye approval. Preserve these observations: do not classify every elevated animation frame as a broken mesh, or claim grounded locomotion from this harness without movement/capsule synchronization.

A separate **unsaved**, reference-pose material diagnostic disabled light shadows and added controlled fill, producing eight 1200×1000 front/three-quarter captures. All eight were visually inspected: skin, iris/sclera, clothing and helmet textures are visible, without an obvious missing-material/checkerboard or solid-white-eye fallback. This clears only the bounded controlled-light material check. It does not prove city daylight/shadow, facial animation, historical uniform approval or production face quality. No character resculpt, material edit or skeleton/action resave was made to obtain these views.

Generation completed at 14:33:59 EDT, fresh saved-map reopen at 14:34:59 and reference-pose face capture at 14:35:52. A separate fresh NullRHI process found exactly six saved actors, with all expected mesh/action references and looping/playing defaults retained. Preview generation reported zero errors and two deprecated EditorLevelLibrary API warnings; reopen and face capture each reported zero errors and one such warning. They were not shader/Blueprint compile errors.

### Remaining integration work

| Item | Status / next action |
| --- | --- |
| Native closure and saved preview references | Pass within the structural/diagnostic limits above. |
| Controlled-light texture/eye display | Pass for the eight reviewed reference-pose captures only. |
| Full P2 / INT-CHAR-02 / INT-CHAR-03 | Not passed: shared Character/health/action shell, capsule contacts, movement synchronization, full action-deformation review and actual city lighting remain. |
| Weapon / first-person / reload | Not run. Empty-handed rifle-family playback is not hand/weapon or M1 reload acceptance. |
| Navigation, NPC behavior, objectives, checkpoints | Not run by this task. |
| Performance / packaged Windows / second machine | Not run; a commandlet capture is not a 60 FPS or packaged-build measurement. |

Next bounded work is the planned shared combatant Blueprint/configuration and capsule/grounded movement test. Separate actual mesh-relative offset, pelvis motion, capsule clearance and foot placement before bounded fixes; do not resculpt or arbitrarily scale skeletons. Then evaluate weapon attachment/player view/reload feasibility under P3 before action transactions. The available editor API probe confirmed Blueprint parent creation, variables, compilation and subobject operations; complete gameplay graph authoring was not implemented or validated by this pass. No new C++ or third-party automation plugin was added.

## Evidence and publication

Raw local evidence is ignored/private and not downloadable from public Git:

- `tmp/paris-integration-20261001/storage.json` and `p1-probe.log`.
- Runtime workspace `Evidence/P0/storage_verification.json`.
- Runtime workspace `Evidence/P1/ue_load_inventory.json` and `active_project_probe.json`.
- Runtime workspace `Evidence/P2/presentation.json`, `fresh_reopen.json`, the six initial PNGs and `HeadReview/face_review.json` plus eight reference-pose PNGs.
- `tmp/paris-integration-20261001/p2-presentation.log`, `p2-reopen.log` and `p2-face-review.log`.

The only new native package is the ignored local preview map, **27,558 bytes**, SHA-256 `7f0cb1358e843d41ebef57c6996e9d8e9f4741e82f458cf8a7256029a72b9b00`. It is an unpublished diagnostic draft, not a selected manifest or teammate release. Native vendor/adaptation bytes remain on the existing selected baseline. The direct Unreal aliases now have explicit vendor/adaptation/diagnostic-map ignore rules so relocated bytes cannot accidentally enter Git. Small Blueprint source logic still requires its exact allowlist entry.

Tools: [integration entry points](../../Tools/Integration/README.md). No new immutable asset release, catalog update or Git publication has been made by this implementation task. Keep Assignment 3 acceptance statuses unchanged: these are partial local checks, not an MVP/course completion record. Unrelated performance-monitor documentation/tools appearing during this work were preserved without editing.
