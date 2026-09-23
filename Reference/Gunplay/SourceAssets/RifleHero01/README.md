# Rifle Hero01 source

Exterior-only visual study, authored 21 September 2026. Reference: HistoricalReference S02, the cataloged US Garand/carbine comparison image. This establishes a recognizable silhouette; exact production variant and markings remain unapproved.

`RifleHero01.blend` contains editable parts with bevel modifiers. Rebuild its two FBXs using Blender 4.5 and `Development/Scripts/build_rifle_hero_blender.py`. Coordinates are centimeters. Exported UV0 is the face-oriented SurfaceMeters layer; inherited UV channels are removed before export.

Reimport the existing Wood and Steel meshes under `/Game/Normandy/Meshes/RifleHero01` in the open Unreal editor. Remove generated collision and retain the matching Wood/Steel material slots. These bind to RifleWood and RifleSteel on `BP_NormandyPlayerCharacter`; the original RiflePose, Muzzle and gameplay graph are retained. Save and inspect in PIE. Material source code is retained in `materials.json`.

The pair totals 13,172 triangles. The model adds a shaped stock, separate handguards, receiver, sights and trigger-guard silhouette. It still needs production UV/baking, surface wear and first-person hands with grip/reload animation. It is not a functional mechanical model or final weapon asset.
