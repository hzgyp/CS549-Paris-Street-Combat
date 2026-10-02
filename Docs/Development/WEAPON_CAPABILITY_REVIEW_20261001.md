# Weapon and first-person capability review — 1 October 2026

## Decision checkpoint

**Later selective-intake update, same date:** Yupu supplied three new deliveries and confirmed private three-member original/derivative sharing. [Actual validation results](WEAPON_ASSET_VALIDATION_RESULT_20261001.md) supersede the earlier absence of any dedicated FP arm candidate: ShooterStarter arm geometry is now inspected, but the tested direct animation/camera configuration is unaccepted, the modern weapon reload is not matching FP hand motion, and the coherent WWII rifle kit/parts/reload and German rifle gaps remain. No new production release or automatic P4 authorization resulted.

P3 inspection found world-weapon candidates but **no accepted complete first-person rifle/reload presentation** in the inspected native closure. A bounded existing-full-body eye-level camera test also failed as tested: clothing/helmet-region geometry occludes the view during idle and some action frames, while other frames leave the hands low in the image. P4 production weapon presentation therefore needs Yupu's weapon/asset or explicitly reduced-presentation decision. This is the [implementation plan's](CHARACTER_AND_WEAPON_IMPLEMENTATION_V1.md) human decision gate, not permission to purchase assets, remodel a character or silently substitute an SMG.

The findings describe the inspected three native mounts and the tested camera configuration. They do not prove every possible full-body arrangement fails or that the entire project contains no other usable reference. [Character work](CHARACTER_LOCOMOTION_LIFECYCLE_RESULT_20261001.md) remains usable and P2 remains partial.

## Available assets and gaps

| Capability | Status | Evidence / required next work |
| --- | --- | --- |
| Allied world rifle appearance | Available | `/Game/USParatrooper/Meshes/Weapon/SK_M1_Garand` and `Sm_M1_Garand`; material resolves. Skeletal candidate has one `polySurface2` bone, 3,923 triangles and no PhysicsAsset |
| World rifle orientation/size | Available | Static bounds approximately 7.43 × 112.36 × 20.84 cm, long axis +Y; attachment/sights still need alignment |
| Independent bolt/clip/round parts | Missing in inspected closure | Single-bone M1 is not an articulated reload rig; no separate ammunition/bolt props identified |
| Player first-person arms/camera | Needs bounded adaptation or replacement | No dedicated native FP arms/action kit identified. Tested full-body eye-level configuration is not accepted; camera-only correction/head hiding did not yield a consistently usable view |
| Generic idle/fire/reload/hit/death clips | Available | Native in-place rifle family, compatible mannequin tracks; not proof of weapon-specific mechanics |
| M1-specific reload | Not tested / unestablished | Generic `Rifle_Reload_2` is not certified as an en-bloc action; empty-handed camera probes cannot verify insertion, grip or bolt operation |
| Aim/sights, trigger/support-hand contact, muzzle clearance | Not tested | No weapon attachment or live aiming/contact test completed; requires selected coherent weapon/view representation |
| Animation-driven ammo commit | Needs bounded adaptation | Five inspected sequences have no named notify events; add guarded events at verified physical moments after reload representation is chosen |
| German rifle | Missing in inspected closure | Included MP40 is an SMG, not a selected rifle; enemy rifle/variant remains undecided |
| Ready-made weapon gameplay/AnimBP/montages | Missing in inspected native mounts | Registry has no native Blueprint, AnimBlueprint or AnimMontage packages; author team-owned logic rather than assume a complete FPS system |

The included Thompson static model is approximately 5.03 × 81.05 × 22.75 cm; MP40 is approximately 7.70 × 62.85 × 28.89 cm. These are alternative appearance candidates only, not equivalent substitutes for the planned rifle, historical approval or a finished action kit.

Selected clips are `Rifle_Idle` (6.4667 s), `Rifle_ShootOnce` (0.8 s), `Rifle_Reload_2` (2.1667 s), `Rifle_Hit_C_1` (1.6333 s) and `Rifle_Death_3` (3.9333 s), with 68 common mannequin tracks and empty named-notify lists. This does not audit every clip/event type or certify contact.

## Full-body camera test and evidence limits

An unsaved copy of the existing lifecycle scene was reduced to the Allied A player. SceneCapture used a fixed idle head-world position plus 8 cm forward and 10 cm upward, horizontal FOV 90 degrees, and five idle/fire/reload sample times. Head-visible/hidden conditions and pitches 0/-25 generated twenty PNGs at 1280 × 720. V2 uses a **capture-only 1 cm near plane**, explicit pitch/yaw/roll keywords, and no saved model/map/project changes. Saved map hashes remain unchanged.

Seven v2 captures were directly reviewed: idle head visible/hidden at pitch 0, fire at 0, reload at 0.3 and 1.0 seconds at pitch 0, and reload at 1.0/1.8 seconds at pitch -25. Idle and early/late sampled reload show severe surrounding-geometry occlusion; fire/mid-reload can show hands only near the bottom edge. Tested head hiding is not a complete sleeve/body/helmet visibility treatment. No dedicated arms extraction, camera offset sweep, weapon attachment, ADS, input or full action-cycle contact was tested. The failure is this candidate configuration, not evidence of a new skin-weight defect or universal impossibility of full-body FPS.

V1 used a 10 cm near plane and mistakenly passed a positional Rotator value as roll rather than pitch. Preserve its twenty captures but **do not claim down-look evidence from v1**. The initial native audit also failed on protected Notifies property access; the corrected event-name API retry succeeded. Failed logs remain retained, not accepted tests.

Canonical evidence: runtime `Evidence/P3/weapon_capability_v1.json`, `P3/FullBodyView/fullbody_view_v1.json`, `P3/FullBodyView_v2/fullbody_view_v2.json` and captures. Source: `Tools/Integration/ue_weapon_capability_audit.py`, `ue_fullbody_view_probe.py`. Logs are in ignored `tmp/paris-integration-20261001/`. No native asset was saved by these audits.

## Human choice and precise delivery requirements

Recommended production route: retain the provisional M1 appearance only if the team selects it, and obtain a **coherent licensed first-person M1 arms/weapon/action kit**. Alternatively, select another historically reviewed WWII rifle kit with a compatible complete action family. A third option is explicit approval of a temporary simplified weapon/reload presentation for diagnostic P4 work; that cannot pass final first-person/reload acceptance or establish historical correctness.

For any supplied kit, require:

- Native Unreal meshes, skeletons, materials/textures and complete dependencies; compatible animation skeleton or documented bounded retarget path. Pin/resave/test in UE 5.8.2 without overwriting originals.
- First-person arms/sleeves plus matching world weapon, aim/fire/reload clips and a defined grip/sight/muzzle configuration. FBX alone is not the full native release.
- Weapon-specific moving parts/ammunition props necessary for the chosen visible reload (for M1, a demonstrated en-bloc/bolt representation rather than merely a named generic rifle animation).
- A documented physical ammo-commit frame/event, cancellable actions and a compatible NPC/world grip representation. Existing notifies may be adapted; gameplay still owns ammo/ActionID/restore-generation guards.
- Verified team-sharing and packaged-game distribution rights, provenance and historical variant/unit review. Do not send credentials or assume purchase alone permits every redistribution.

After the choice: update P3/P4 scope first, then attachment/view/contact tests and the documented action/ammo transaction. Timer expiry may cancel a stuck action but must never manufacture an ammo commit. No final weapon, procurement, immutable SFTP release or Git publication is made by this checkpoint.
