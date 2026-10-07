# Trigger/support contact calibration — bounded offline result

4 October 2026. [Chinese review](WEAPON_TRIGGER_CONTACT_RESULT_20261004_ZH.md).
Implements `WEAPON_TRIGGER_ALIGNMENT_V2_20261004.md` then
`WEAPON_TRIGGER_CONTACT_POSE_V3_20261004.md`. Human clarification: RIGHT index
operates the trigger, LEFT hand supports the rifle; no handedness conversion.
Reviewed AN003/004/005, FP001, the rejected coarse left-finger layer and V1;
AN001/002 were also reviewed in the preceding trigger-first investigation.

**Contact visibly improves, but remains an unselected offline diagnostic.**
No native authoring, formal game adoption, NPC fitting or runtime pass this turn.

## Gun-first mechanism and preserved technical stop

V1 translation lost left-palm contact. Instead of sweeping offsets, V2 derives
one rigid transform from actual trigger/pad surfaces and a palm/fore-end contact:
actual stock triangles intersect a sphere centred at the trigger pivot, then one
minimal-arc rotation keeps that pivot while meeting the support point. Scale1,
models, source poses, camera and all hands are unchanged during this gun-first step.

`pivot_fit_v1` stops before rendering at51.1044degrees, above the unchanged15degree
gate. Audit identifies a technical error: Blender→UE coordinate fit determinant
is -999997.6601; raw triangle cross products reversed normals under reflection.
This selected dorsal/upper surfaces rather than palm/lower stock surfaces. One
parity correction and fresh actual-face selection produce `pivot_fit_v2`, not a
parameter search. Retain both sources/results. The51degree result is not evidence
of physical impossibility; V1's face-direction labels are invalid, while its
visible conflicts and geometrical crossing observations remain valid.

Corrected gun fit rotates8.6893528degrees relative to its derived translation;
hand_r-relative translation cm=(-13.2919606,9.0126054,2.6116283). Full matrix and
actual triangle identities are recorded in private `pivot_fit_v2/result.json`.
Trigger/palm point residuals are approximately9e-16/2.4e-7cm, respectively: these
are solver-point checks, NOT whole-surface grip clearance or visual acceptance.
Left palm visibly returns to the fore-end; no left-arm lifting/IK was needed.

Gun-only phase checks show zero index/stock crossings at0/2.2/4.1s, but index/guard
crossings40/0/40. Existing index local rotation differences0→2.2s are approximately
21.75/3.82/8.40degrees. This supports a phase-specific contact-pose problem rather
than malformed finger geometry. Gun-only V2 is not selected as a complete repair.

## Existing-action right-index comparison

Only after gun-first comparison, reuse the already-existing2.2s LOCAL rotations
of `index_01_r`, `index_02_r`, `index_03_r`, under the user's earlier explicit
three-joint permission. Source target:
`/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1`, from
existing D059 `W2_Stand_Aim_Reload_IP`. No new motion/keyframes or source-clip rewrite.
Each current local translation/scale is preserved; every other bone component
matrix has exact0 delta in the offline evaluation. Wrist, thumb/other fingers,
left arm, geometry, rig, weights, original actions, sleeves and camera stay fixed.

| Recorded reload phases | Index/stock crossing triangles | Index/guard | Index/trigger blade |
| --- | ---: | ---: | ---: |
|0,0.4,1.2,2.2,3.4,3.8,3.98,4.1s — each|0|0|22|

The selected actual pad point is0.05150cm from the blade, not a whole-surface
clearance bound. Blade22 intersections remain; depth/volume is unmeasured, and
**complete no-penetration acceptance is not claimed**. Do not automatically
increase curl, add another finger layer or relax the gate to hide this residual.

## Visual and reloadable evidence

Private single workspace:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponTriggerAlignmentV2/`.
Reproducible tools: `Tools/Integration/WeaponTriggerAlignmentV2/`.

- `pivot_fit_v1`: retained technical stop before rendering, inputs unchanged.
- `pivot_fit_v2`:42 before/V1/after views,0/2.2/4.1s; preserved source/result/blend.
- `index_pose_v1`:33 gun-only/index-adapted views and whole unchanged arms.
- `review_v1`: all75 views inspected in sheets, ambiguous contact detail also
  opened individually; Chinese same-camera `before_after.png`. Frozen JSON's
  pending-inspection status describes composition time, before this human-readable
  inspection record. Close-ups show index inside guard near blade and restored
  support; no new visible finger collapse. Whole-arm views retain existing source
  shoulder web/spikes: no sleeve or whole-arm deformation acceptance from this work.
- `fresh_check_v1`: fresh Blender5.2 process opens saved diagnostic blend, exit0,
  unchanged SHA `a0848ad8320b3e8aa16c3b16f38761f7b62ebd9b9d2a0a0d3c3f48a95dc16903`.
  Imported source rig72bones; visible gun2131vertices/3923triangles. Hand diagnostic
  objects keep the full6135-vertex array with4308 selected triangles each; these
  are static skin evaluations, not native/playable animated-rig export proof.

All successful Blender jobs exit0, source/input hashes unchanged. Reflection-safe
normal selection and copied diagnostic face winding do not mutate source topology.
The Blender character workflow supplies multi-view/skin/fresh-open checks; it does
not substitute for Unreal motion/contact validation.

## Native protection, coordination and remaining gate

Current528 size/SHA guards exactly match `ReloadIndexContactV6/map_recovery_v1`
snapshot. This includes the known accidentally saved unselected V6 rate change;
it is NOT528 matches to the older inventory (527 old matches, one V6 difference).
Canonical map remains2707948bytes/SHA
`2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`, using PlayerV1.
No UE slot claimed; Lane B's controller/BT/BB/B6 files and ownership are untouched.
All current diagnostics stay unselected; no Catalog/release/package/commit/push.

Open: blade contact residual; actual native continuous reload/idle/walking and
start/end blending; sleeves/continuity; lifecycle/ammo/near-wall regression;
independent Allied/German NPC trigger/support fitting. Eight discrete source poses
cannot prove motion between samples. Further native integration requires a new
bounded graph/contact plan and serialized UE-slot coordination, preserving original
models/source motions/camera/transactions and stopped AN004/005 mechanisms. Do not
copy this player's transform to NPCs or silently choose it on the formal map.
