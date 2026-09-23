# Weapons and Ammunition: Visual and Animation Baseline

The playable scope remains **one weapon**. Recommended first candidate: an M1 Garand consistent with U.S. infantry. Final selection remains part of the scenario review. Other entries are reference coverage and environment checks, not additional promised playable weapons.

| Item | What the developer must distinguish | Local / primary reference | Scope status |
|---|---|---|---|
| M1 Garand | Semi-automatic rifle; eight-round clip; correct loading and empty-clip presentation | [U.S. rifle page](images/weapons/us_rifle_comparison.png), [M1 page](images/weapons/us_garand_carbine.png) | Recommended player candidate |
| M1 Carbine | Distinct weapon, cartridge and magazine; do not substitute later M2 behavior | [Carbine variants](images/weapons/us_carbine_variants.png) | Optional reference only; check variant date |
| M1903 / M1903A3 | Bolt action and distinct sights, unlike the Garand | [Comparison](images/weapons/us_rifle_comparison.png) | Specialist use requires scenario evidence |
| Karabiner 98k family | Bolt-action silhouette, stock and receiver; not an automatic rifle | [German rifle plate](images/weapons/german_rifle_reference.png) | Defender candidate; exact submodel review required |
| MP38 / MP40 family | Folding-stock submachine gun; not the default weapon of every defender | [Submachine-gun plate](images/weapons/german_submachine_guns.png) | Optional role-specific prop |
| MG34 / MG42 | Different receiver/barrel-jacket silhouettes; mount and belt presentation must match | [Both silhouettes](images/weapons/mg34_mg42.png) | Candidate emplacement reference; exact position inventory unverified |
| German 81-mm mortar | Mortar geometry and finned bomb differ from a tank gun and fixed round | [Period reference](images/weapons/german_81mm_mortar.png) | Background context only |
| Captured 76-mm artillery | German defenses could include captured equipment; avoid labeling every gun an 88 | [Omaha emplacement](images/weapons/captured_76mm_emplacement.jpg) | Photo caption identifies Russian origin; exact model not resolved |

These references establish visual families. A model's existence by 1944 does not establish its presence in the selected strongpoint. The full German handbook contains later weapons; do not turn its complete contents into an Omaha inventory. Sources: [S02, S03 and S01](SOURCES.md).

## Ammunition categories that must not be mixed

| Category | External-art distinction | Review requirement |
|---|---|---|
| Small-arms cartridge | Bullet plus cartridge case; cases ejected from a firearm are not complete projectiles | Match the selected weapon, feed system and visible ejection event |
| 75-mm fixed round | Complete gun round includes projectile and case; distinguish it from the projectile alone | [M48 external reference](images/weapons/us_75mm_m48_external.png), FM 23-95 Figure 19 |
| Mortar bomb | Finned tail and body silhouette; not a scaled rifle cartridge | Period mortar image establishes family only; close-up asset needs model-specific reference |
| Artillery projectile / shell | Caliber, form and paint scheme depend on weapon and period | No generic shell mesh reused as tank, mortar and naval ammunition |
| HE versus armor-piercing or smoke | These are different ammunition roles; visible markings vary | Never invent stripe colors or inscriptions from contemporary ammunition |

The locally saved **1942 FM 23-95 is for the M2 gun in the M3 medium tank**. Its M48 picture is a form reference, not proof of the ammunition loaded in a particular Omaha Sherman. A museum record for a 1945 M3-gun firing table lists M48, but is later than D-Day. Keep the exact load and markings unresolved until the tank asset requires them. [S18 and S23](SOURCES.md)

## Rendering and animation consequences

The gun model, hands, clip or magazine, reload montage and ammunition counter must describe the same weapon. Separate empty reload from any partial-reload behavior actually supported. A simplified partial reload must not show a box magazine being inserted into a Garand. Align muzzle flash and traces with the muzzle; keep the existing camera/muzzle collision lab.

For impacts, distinguish sand, wood, metal and concrete responses. A bullet hitting ordinary concrete should not trigger a large fireball. The designated destructible cover object is a gameplay abstraction with an explicit material/state transition. It does not imply that every obstacle or bunker is destroyed by rifle fire.

No internal explosive design, ammunition manufacture, real-world firing procedure or detailed artillery simulation is part of this project. The collected military manuals are archival references; this development sheet uses only classification, appearance and game-animation implications.
