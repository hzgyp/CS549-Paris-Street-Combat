# V18 — bounded right little-finger length adaptation

Later user review,5 October: hand appearance accepted. Its older failed-contact
counters remain historical evidence, not authorization for more finger edits.
Overall first-person/runtime adoption is conditional and not established; see
[FIRST_PERSON_V18_ACCEPTANCE_20261005.md](FIRST_PERSON_V18_ACCEPTANCE_20261005.md).

5 October 2026. The user asks whether the little finger was previously altered,
requests a modest shortening, and requests a reusable English NPC fitting guide.
This authorizes only the right little-finger proportional adaptation in a new
offline copy, not a renewed multi-finger solver or native/NPC integration.

Reviewed: Failures/README.md, FP001, the complete closed-grip V6–V10 result,
V16 marked-pivot result and V17 textured-view record; Blender character workflow
and its form-review/shared execution references. The historical V10 extended
little finger is stopped/unselected, not a permitted baseline. V17 preserved
all V16 positions; audit the current pinky local matrices against D059 before
attributing its appearance to an earlier edit.

Different mechanism: ONE fixed 0.90 uniform scale at pinky_01_r, inherited by
pinky_02/03_r around the fixed knuckle. This shortens the complete little finger
by 10% with a corresponding 10% width reduction, preserves its existing local
rotations and maintains skin continuity through unchanged source weights. It
does not independently move the tip, rotate finger joints, change the palm,
adjust the gun, or synthesize a new motion. Vendor/source meshes, rest rig,
weights, UVs, actions, other fingers and all formal assets remain unchanged.
The previous blanket finger protection is relaxed only for this user-requested
little-finger scale in the new copy, not for other fingers or original assets.

Early acceptance: identify the actual right pinky by source bone weights;
current local-pose audit; fixed knuckle, three segment ratios 0.90; unchanged
approved index and all non-pinky skin (<0.0001cm); unchanged gun/camera/textures;
no new severe stretch edges or increased ring/little self-crossings. Stop if
these fail; do not scan percentages or resume stopped angle/IK/digit solvers.
Test the same proportion adapter on recorded existing D059 phases without
editing/baking replacement animation. Static/source-rig verification does not
establish native gameplay or complete trigger/stock contact acceptance.

Deliver a matched textured before/after and an editable offline inspection
copy with source rig/weights retained, plus fresh-open verification. Binary
evidence stays solely under the ignored SFTP workspace
Evidence/WeaponPinkyLengthV18. Do not use UE, overwrite V16/V17, select assets,
release, update Catalog or commit/push. The English guide documents the general
hand-anchor → independent gun translation/rotation → source-length support-arm
IK → whole-system framing → action/runtime regression process. NPCs must fit
their own hand/weapon landmarks; no copying this player's numerical offset.

## Source audit / bounded boundary clarification

probe_v1 exit0: all three current pinky local matrices match D0590s to
1.43e-14; the old extended V10 pose is not inherited. 378 vertices have source
pinky influences; none belong to the protected index mask. Two ring-root mask
vertices also have pinky weights. Preserve all ring bones and rotations; allow
only the natural unchanged-weight contribution at these two boundary vertices,
bounded below 0.1cm, while all vertices without pinky influence stay exact.
This is not a ring-pose edit or permission to alter source weights. Record that
boundary explicitly rather than claiming the entire ring skin stays exact.
The source joint spans (first→second→third) are 6.556491cm for pinky versus
7.906542cm for ring; these spans exclude the terminal tip and are not anatomical
surface lengths. probe_v1's `rest_bone_lengths_blender_m` label is incorrect:
those values are armature-data units before object scale, not world metres.
Use verified native-cm measurements for this trial, preserving the probe.

## Stopped root trial and different distal-only mechanism

shorten_v1 stopped before any candidate mesh/rig/render was saved. Read-only
boundary_diagnosis_v1 identifies vertex1735 with pinky_01/ring_01 weights
0.737255/0.262745: whole-chain scale displaces it 0.150372cm, exceeding the
declared 0.1cm boundary limit. Vertex1744 moves0.002751cm; unaffected skin0.
Do not repeat that root trial or relax its gate.

New bounded mechanism: keep pinky_01 and its entire first segment unchanged;
apply the same ONE0.90 scale only at pinky_02, inherited by pinky_03. The shared
ring vertices have no pinky_02/03 influence, so this preserves them rather than
editing weights or freezing isolated vertices. It shortens the two distal
segments10%, not the whole finger10%; record the actual total reduction.
This is one cause-led hierarchy change, not a percentage/angle scan. Keep the
same protection/deformation/fresh checks, require ring-boundary delta0 and keep
all other finger local rotations (including pinky) intact. No new motions or
automatic gameplay/NPC integration. Use a separate distal_v1 identity/script.

## Final local result

distal_v1 exit0/errors[]: existing finger curl retained, pinky_01 unchanged;
pinky_02 scale0.90 inherited by pinky_03. 289 source-weighted vertices affected,
with exact0 approved index, ring-boundary and all uninfluenced skin delta at all
eight recorded D059 samples. Other bone matrices remain exact; child03 local
matrix error<=1e-10. No new severe stretch edges; current ring/pinky self-crossing
pairs remain0→0. The first-to-third joint span changes6.556491→6.257949cm,
a0.298542cm/4.553% span reduction, excluding the terminal tip. This is **10% of
the distal chain**, not10% of the entire finger. Distal width also scales10%.

An editable source rig is retained in the new copy, with its mesh/rest bones,
hierarchy and weights unchanged. The uniform distal-root pose scale gives actual
skinned error0.000069921cm against offline evaluation. No motion was synthesized
or baked; sampled adaptation uses the existing D059 poses.

All eight matched original before/after views (front, stock-end, top, full arms)
and the labeled comparison sheet were inspected. The tip is visibly shorter,
without a new detached wrist or ring/little self-crossing in those views.
Existing shoulder geometry remains visible in context. Shortening is not gun
clearance: little-finger stock-crossing faces increase62→72, while thumb51,
middle64,ring70 and index guard23/blade17 remain unchanged. These counts do not
measure penetration depth. Overall contact remains failed/unselected; do not
silently adopt this anatomical correction or resume a fitting/angle sweep.

Fresh_v1 exit0/errors[]: saved source mesh, rest rig/hierarchy and weights exact
against original FBX; nine rendered source image dependencies unchanged;
inspection topology/UV/material slots/gun exact. Saved rig produces inspected
skin to0.000140075cm, distal-root scale approximately0.90. Source input/blend
hashes preserved,528 current recovery guards exact, including known unselected
V6 saved-rate difference. No native/continuous-gameplay/exported-runtime test.

Private editable file:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponPinkyLengthV18/distal_v1/RightPinkyDistalShorter.blend`
(SHA256 `7a1d0520b11e7d9c8d29377c46909cfa2b65fea39254789e28eff083de404219`).
Comparison: same folder `before_after.jpg`. Root-trial failure, boundary diagnosis,
all inputs and old versions retained. No UE slot, native/NPC/BT/BB changes,
formal map selection, Catalog/release/package/commit/push.

English reusable guidance:
[WEAPON_HAND_CONTACT_CALIBRATION_GUIDE.md](WEAPON_HAND_CONTACT_CALIBRATION_GUIDE.md).
The method is hand reference → independently fit gun with actual pivots/rotation
and translation → support-arm IK → complete-system framing → existing-action
and native regression. Each NPC must calibrate its own actual hand and weapon;
no copying this player's offsets, diagnostic mesh or little-finger proportion.
