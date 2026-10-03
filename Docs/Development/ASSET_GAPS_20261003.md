# Remaining weapon models and animation gaps

Date: 3 October 2026. For Yupu's next Xianyu search. [中文](ASSET_GAPS_20261003_ZH.md). This is an inventory-based requirements list, not a purchase, seller recommendation, historical approval or license verification. Existing city, soldiers, generic rifle animation families and accepted complete-arm presentation remain the foundation.

## Priorities

| Priority | Look for | Why and minimum delivery |
| --- | --- | --- |
| First | M1 Garand articulated model with matching first-person actions | Existing M1 has usable appearance but one bone; no independently usable bolt/operating rod, en-bloc clip or rounds are established. Prefer a coherent rigged kit with matched idle/fire/reload actions, textures and world mesh. Request both empty and tactical reload demonstrations if advertised; a modern magazine reload is not equivalent. A bare static M1 would duplicate what we have. |
| Second | German rifle candidate, preferably Kar98k for review | No accepted German rifle model/kit exists in the inspected closure. The included MP40 is an SMG. Variant/date/unit still require historical selection, so Kar98k is a search candidate, not an already approved loadout. Ask for textured world/skeletal mesh, moving bolt and ammunition, and matching bolt-cycle/reload clips if available. |
| Optional | UE muzzle flash, surface impact and bullet-mark pack | Active inspected selections do not establish a ready muzzle/impact/decal system. Search for Niagara-compatible muzzle flash, masonry dust, metal sparks, wood/glass impacts and matching decals. These are effects, not missing soldier meshes. Existing texture/trail candidates may help; do not buy another large environment merely for one effect. Simple effects can be separately authored later. |

## Do not repurchase now

The Paris city, US/German soldier models, complete-arm mesh and M1 appearance are available. Named native candidates already cover run (8), jump (5), slow-walk adaptation (4), crouch (7) and prone (6), as inventoried in `Assets/Integration/PLAYER_ACTION_CANDIDATES_20261002_V2.json`. They are not all integrated or contact/runtime accepted; lack of a key binding does not mean missing motion assets. No verified specifically named sneak/stealth clip was found, but existing walking can be evaluated for low speed first. NPC following, patrol and decision trees are code/design work, not purchases.

## Questions to send a seller

Ask for original pack name/source and proof of rights to deliver and permit three-member private project sharing; cheap resale alone is not authorization. Request actual UE version, skeleton/hierarchy, source FBX if supplied, complete textures/materials and an uncut gameplay/animation preview. UE project/native assets with full dependencies are preferred; FBX can be adapted but does not carry a complete UE material/animation setup. Do not buy a newer-engine-only package without a compatible export. Our pinned integration target is UE 5.8.2; all deliveries still need selective fresh-load/material/pose/contact validation. Do not send account credentials or receipts into public Git.

Ask whether the M1 bolt and clip/rounds are independent controllable parts, whether the advertised FP animation actually animates hands with that weapon, and whether fire/reload fit the exact included mesh. Rendered promotional images and generic animation lists are insufficient. A coherent complete M1 kit takes priority over buying separate incompatible hands, rifle and animations.

New deliveries start in `Assets/LocalWorking/Intake/<batch>/`. Only validated useful content/dependencies move to the shared SFTP baseline/workspace; verify hashes before removing redundant working bytes. No new batch folders or purchases were made in this audit.

## Evidence and limits

Read `WEAPON_CAPABILITY_REVIEW_20261001.md`, `WEAPON_ASSET_VALIDATION_RESULT_20261001.md`, `WEAPON_BASELINE_AND_RELOAD_RESULT_20261002.md`, `WEAPON_PRESENTATION_AND_PLAYER_ACTIONS_V1.md`, the current action inventory and `CONTINUOUS_ARMS_DYNAMIC_RESULT_20261003.md`. Latest user review accepts the preview model appearance, not weapon-specific reload, historical loadout, all actions or frame-time performance. Findings apply to the inspected set; uninspected collection archives are not certified empty of every possible candidate.
