# Existing M1 holding repair - 2 October 2026

**Subsequent human result: rejected.** Yupu reported severe clipping and degraded fingertips in the actual game. The sparse coarse-contact selection below did not survive human review; gameplay/navigation passes remain valid only for their recorded logic tests, not presentation. Follow `WEAPON_TRANSFORM_ONLY_REPAIR_V2.md`, restore the original AnimBP and adjust gun-relative translation/rotation only. Do not treat this trial as accepted or continue the finger/head repair route automatically.

## Outcome and limits

A coarse existing-asset grip increment is saved for local regression and human review, not final weapon-presentation acceptance. The selected terminal AnimBP reduces the prominent open left fingers; a recalibrated attachment brings the M1 fore-end into the support grasp in reviewed idle and ordinary 300 cm/s walking views. No soldier mesh, source clip, rig, weapon model or camera was regenerated/replaced. Fine right trigger/finger contact and complete directional/fire/reload presentation remain unaccepted.

The unchanged full-body camera has phase-dependent walking head/helmet occlusion, visible in source and corrected poses. Attaching the diagnostic camera to the actual player camera did not remove it. It is a real remaining view problem, not solved by this grip layer. Do not mark walking FP presentation passed, conceal hand contact with a camera move, or proceed to optional finger refinements. The next visual work should address owner-view head/helmet handling on the retained asset, after human review of this coarse increment.

## Retained changes

- Team map only: `LV_ParisStreetCombat_V1`, three Allied rifle attachments and three mesh AnimClass overrides. Current map size 2,704,136 bytes, SHA-256 `bd97f1a1a51683e8a72c9f3269aff4798a2496755938555e30cc14c674bdd861`.
- New `ABP_PC_AlliedGripV1`: 285,235 bytes, SHA-256 `febe706ba099ce95929740624f736441fd71c8d7bf2289b0ae1c126d1039070f`. Derived from the unchanged Allied stride AnimBP; retains its BlendSpace, event/speed/direction logic and skeleton. Standard local/component conversions and twelve additive left-finger controls; no runtime bridge call. Single-node simplified reload bypasses this ready-pose layer.
- Exact attachment parameters and rollback instructions are in `WEAPON_PRESENTATION_AND_PLAYER_ACTIONS_V1.md`. Camera `(25,0,60)`, M1 mesh/scale, muzzle `(0,83.23,0)`, combat/reload/default Blueprints, German actors and navigation settings are unchanged.
- `Assets/Integration/CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json` records eight current files plus the retained 28-file reload dependency snapshot: 36 current unpublished native drafts. Earlier navigation map hashes are historical, not current overwrite authority. The verified pre-grip map remains privately in `WeaponGrip/BeforeCityGrip`.
- One narrowly scoped Editor-only graph helper was necessary because Python supplied no Modify Bone palette action. `EditorBridgeBuild_grip_v23c` built successfully; deployed binaries matched it. Prior v22 DLL/PDB/modules remain verified in private `WeaponGrip/BridgeV22BeforeGrip`. The bridge remains disabled by default and is not gameplay C++ or a runtime dependency.

All native bytes/evidence remain in the existing single writable owner workspace. No immutable release, Catalog selection, vendor rename, full city copy, purchase, detailed character production, Git commit/push or external asset publication occurred. Follow/patrol/BT/faction interaction remain paused. VFX and new run/jump/slow/prone actions were not implemented by this holding increment.

## Actual evidence

The new `WeaponPresentationV1` alias directory is explicitly ignored by Git as well as its physical LocalShared home. No native Content file remains untracked outside exclusion rules. Only source/docs/configuration/hash metadata are intended for a later authorized commit.

Private evidence prefix: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/WeaponGrip/`. Logs remain under `tmp/paris-city-gameplay-20261002/`.

| Evidence | Recorded result |
| --- | --- |
| `probe_v1` | Unsupported root-component reflection; no native save |
| `probe_v2` | Six static action phases / 24 captures; old 35 draft hashes unchanged. Placement alone did not clear open fingers |
| `sparse_v1`, `sparse_v2` | First temporary fill overexposed; second readable contact comparison. Raising the gun did not clear contact |
| `curl_v1` | Memory-only source-key experiment, disk hashes unchanged; rear anchor misplaced the stock and runtime pose application insufficiently established. No selected source-track derivative |
| `layer_v1` | Python palette action absent; no retained native duplicate |
| bridge `v23`, `v23b`, `v23c` | Initial compilation rejected a TObjectPtr loop. Corrected build passed; next startup was stopped before authoring after source inspection identified a conversion-output pin mismatch. Final corrected build passed; all failures retained |
| `layer_v3` | Exact trial compiled without graph diagnostics and saved. First PIE harness failed on Python variable scope/PIE editor-asset access; no contact pass, old 35 unchanged |
| `layer_fresh_v1`, `layer_fresh_v2` | Bridge-disabled fresh trial load, unchanged trial/old 35, normal idle and 300 cm/s walking; diagnostic camera attachment did not clear walking occlusion |
| `layer_fresh_v3` | Six reviewed views including walking side contact and source walking FP; real velocity 300 cm/s, old 35/trial unchanged, no script or Error/Fatal/ensure matches. Coarse contact selected; full presentation pending |
| `city_author_v1` | Saved only the documented team-map increment; all 34 other prior drafts and the new trial unchanged. New inventory generated; not runtime acceptance |

Bridge-disabled actual-city `combat_grip_v1` passed the existing 15 cases/62 assertions, three fresh Allied grip-class selections, exact attachment location, and player grip-class persistence after reload/death/reset. Engine exit 0, zero Error/Fatal/ensure matches and protected bytes unchanged; the actual city/HUD initial image was reviewed. This is combat/lifecycle regression, not visual full-cycle acceptance.

Retained-navigation `grip_nav_v1` reproduced the prior 391 complete sample paths but its harness read the newer grip-author report as a navigation report, raising `KeyError: summary` before live movement. Native bytes stayed unchanged and no registration warnings occurred; it is not a pass. The corrected fresh harness explicitly reads the preserved navigation-author coverage evidence while guarding the current grip inventory. `grip_nav_v2` passed four ordinary Allied/German short/80 m arrivals, off-mesh rejection and in-flight cancellation; retained coverage is identical (391 complete sample paths). Engine exit 0, zero Error/Fatal/ensure/registration-replacement matches and protected native hashes unchanged. Capsule segment spot sweeps still include previously recorded world obstructions; these successful measured moves do not clear all-city collision/avoidance or every possible route.

Human visual acceptance, complete view/contact cycles, FPS and a new packaged build remain separate.

## Human review handoff

Final closeout verified all 16,606 Catalog-selected city/character/motion local files with `Tools/check_asset_storage.py --local --asset-id france-liberation-content --asset-id character-ue582-integration-baseline --asset-id rifle-pro-mocap-ue582-selected --git` (exit 0), all 36 current native sizes/SHA, and both prior v22/deployed v23c bridge DLL/PDB/modules against their retained builds. Five Python/three PowerShell sources parsed and `git diff --check` passed. These are local/source-storage checks, not an immutable SFTP publication or second-machine restoration. All automated engines exited before interactive review.

With automated engines closed, `Tools/Integration/run_paris_review.ps1` opens the current un-packaged city for the user. Controls remain WASD/mouse/left-click/R; Alt+F4 closes it. Review coarse left support contact, right stock placement and return to the corrected ready pose after simplified reload. Walking head/helmet occlusion is a known unresolved issue, not a new action feature or an accepted FP result. Do not certify the whole representation from one attractive idle screenshot. Stop at this visual review before further presentation changes; head/helmet handling should be the next documented bounded repair, not more finger/fabric iterations.
