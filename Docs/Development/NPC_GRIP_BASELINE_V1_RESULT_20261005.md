# Allied and German NPC grip baseline result

5 October 2026. [Capture plan](NPC_GRIP_BASELINE_V1_20261005.md).
The current native idle grip has been captured for user markup. Neither pair
has been fitted or accepted. The approved first-person presentation is unchanged.

## Captured pairs

| Pair | Actual source and binding | Status |
| --- | --- | --- |
| `PC_City_Ally1` | Adaptation `SK_WWII_US_Paratrooper_simple_UE582_v1`, original US skeleton, `ABP_PC_Allied_Stride_v1`, `BP_PC_RifleAttachmentV3`, original `Sm_M1_Garand` | Saved formal NPC and gun |
| `PC_City_Enemy1` | RetargetDraft/GermanTranslationV1 `SK_PC_German_A_Translation_v1`, its translation skeleton, `ABP_PC_German_Stride_v1`, `BP_PC_GermanRifleAttachmentV2`, `SM_PC_GermanRifleV15` | Saved NPC was unarmed; existing tested gun staged in memory only |

Both actors are native `Ready`, with no movement at freezing. Exact paths,
material identities, evaluated world bone transforms, gun transforms, attachment
parent/socket and camera axes are recorded in private
`Evidence/NPCGripBaselineV1/native_views_v3/result.json`. This is one representative
per faction, not proof that every mesh variant shares the same contact fit.

## Images and capture verification

Fourteen1600x1000 original PNGs cover front/right/top/reverse, whole upper body,
right grip and left support for each faction. Actor-local axes, camera targets
and orthographic widths are recorded. Four labeled2400x660 sheets retain native
pixels at a common half-scale with no retouching. Four sheets and both reverse
originals were inspected; right-grip originals were also opened. The tight right
crop does not contain the complete guard, so use the right-side three-view tile
or its original for trigger markup. Full-arm context supplies shoulder/elbow/
wrist relations; no geometry cut, model replacement or runtime mask was made.

Original UE material graphs render under temporary shadowless fill with fog
disabled. These are diagnostic lighting, not a comparison of city daylight or
Blender portable PBR. Source/material/rig/weights/digits remain unchanged.

First front image was visually inspected before the remaining views. Whole-world
pause keeps gun position drift exactly0cm across all14 captures; wrist/index/thumb
position checks remain below the declared0.01cm threshold. Source rig protection
and static imagery do not pass penetration, firing/reload, locomotion, collision,
NPC combat, historical equipment or gameplay acceptance.

## Preserved failures and protection

`native_views_v1` stops before an image on the wrong Python library name.
`native_views_v2` retains a dark front image and failed gun-stability assertion
after animation-only freezing. Both exit normally0 and keep all555 guard rows
exact; exit0 is not a successful capture claim. V3 uses the documented whole-
world pause and presentation lighting correction, not a new grip solver.

V3 exits normally0 with no task errors. Fresh closed-editor check confirms all555
current protected sizes/SHA values exact. All task UE processes are absent;
the serialized native slot is released. Images/data are Git-ignored private
workspace evidence; generic scripts compile and no asset was saved/deleted,
Catalog-selected, released, committed or pushed. Existing B AI work is intact.

Next: user marks these baseline images. Then write independent Allied/German
fitting constraints using the contact guide: preserve mature firing hand first,
fit each actual gun by translation and rotation, and only then fit the support
arm. No automatic player numeric copy or per-finger solver continuation.
