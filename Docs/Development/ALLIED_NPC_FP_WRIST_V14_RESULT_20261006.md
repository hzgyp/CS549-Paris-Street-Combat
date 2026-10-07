# Allied NPC right arm — approved FP reference V14 result

6 October 2026. Requested static comparison completed; human posture and motion
acceptance pending. Plan: `ALLIED_NPC_FP_WRIST_V14_20261006.md`.

## Reference and change

Read current HANDOFF/Git/guards, failure index/FP001/AN002/AN006/AN007, V13
plan/result, approved FP V21/config, existing W2 native source probe/selection,
holding C++ code, weapon-hand guide and Blender character/execution/form-fit
instructions. Opened approved formal FP `fresh_v2/ready.png` and prior V13 side/
body views. Source W2 inventory and immutable approved V20 config verified.

The approved FP Ready layer preserves W2 right-arm locals. Its rigid camera
assembly framing does not change forearm direction in hand coordinates.
Referenced existing `W2_Stand_Aim_Idle_IP` fraction0, not FP camera/world offsets,
gun attachment numbers or directly copied joint quaternions. Native source probe
is existing evidence; no new FP/action proof or live native skin query performed.

ONE analytic original-length right elbow fit from ACTUAL native V13, with fixed
shoulder and hand_r world transform and elbow no higher than shoulder. The
unconstrained closest direction would put elbow Z257.111cm above the head;
rejected analytically before candidate skin/native authoring. The constrained
elbow Z236.946cm equals shoulder height: delta(-5.404,+6.364,+14.994)cm. Only
upperarm_r/lowerarm_r and their original twist descendants change. Both hands,
all digit world/local poses, left chain, torso/head/legs and entire rifle fixed.

| Rig-axis comparison | Before V13 | After V14 | Approved FP source |
| --- | --- | --- | --- |
| Forearm direction vs hand_r local -X | 82.192deg | 57.881deg | 13.703deg |
| Direction error from FP analogue in hand frame | 76.552deg | 47.001deg | reference |

These are reproducible rig-axis diagnostics, not anatomical clinical angles.
Current frozen grip/shoulder geometry cannot reproduce FP's exact angle with a
below-shoulder elbow. Do not claim identical FP pose, low wrist world position,
or complete natural firing acceptance. Wrist world height did NOT change;
forearm direction and bend changed, visible side silhouette improves.

## Preservation and fresh checks

All611 guards/current source/retained inputs exact. Full immutable source skin
reconstructed; no model/rig/weights/topology/UV/materials/source actions edits.
All protected matrices, digit locals, actual digit skin and unaffected skin
exact offline. Rifle and both wrists exactly fixed; all10 digit stock/guard/
blade counts identical. Existing right index blade10 and other contact failures
remain, not repaired or accepted by this right-arm comparison.

Source upper/forearm lengths30.340127/26.975390cm retained; offline error<4e-13cm.
New severe edges0 (>3x AND >2cm-extra same prior screen); max extra edge3.641cm
retained, not zero skin deformation. Mixed right hand/forearm/cuff weights change:
all positive hand-influence max8.383cm, >0.5 max0.466cm, >0.99 max0.02246cm.
This is original continuous skin deformation, not a standalone hand move or a
claim that all hand-influenced cuff vertices stay fixed. Source weights unchanged.

Fresh clean-process geometry reconstruction max0.000160cm; source triangles
exact. One Blender process normal exit0. Actual native protected bones/gun
position0cm and digit-local rotation0degree; source length errors upper0.000068/
forearm0.000134cm. Native rig-axis angles82.191645->57.880517degrees.

## Actual native views and limitations

One serialized unsaved frozen native entry `fp_wrist_native_v14`, owned PID30296
normal exit0. V13 original-material side/wrist baseline reproduced and opened
before candidate. All15 original1600x1000 images and four labeled sheets opened.
Full original source mesh/materials, whole-world pause and diagnostic paused
refresh retained; no original NPC driver or FP binding code edited/called here.

Side/front show a less steep right forearm, elbow at shoulder height/outward,
horizontal rifle and existing grips. Wrist/shoulder/elbow/body views show
continuous arms/cuffs and no newly observed giant sheet or detached wrist in
STATIC views. Complete-body side/front include helmet and boots. Top covers
complete rifle but trims lower body; body views provide that coverage.
Reverse-wrist detail is heavily occluded by original backpack/torso: not a clear
right wrist view or complete hidden-side contact proof. Shoulder/butt partially
obscured by forearm; no complete butt penetration/ADS sightline proof. Cloth
fold/texture sharpness varies before/after, unchanged material paths/source
bytes; streaming/shader cause not diagnosed and no texture authored.

Private evidence: `Evidence/AlliedNPCGripV2/fp_wrist_v14` JSON/NPZ/fresh read and
`fp_wrist_native_v14` original views, verification and comparison/three_views/
wrist_details/body_shoulder sheets. Diagnostic cached skin is NOT an exported
playable rig, new animation or selected asset release.

All engines closed/fresh611 guards exact; lane A explicitly RELEASED. No formal
map/package save, adoption/deletion, FP/B/German/AI/gameplay/Catalog/release/Git
commit/push. German deferred until Allied review. No automatic additional pole,
arm/assembly offset or digit correction. Human whole-posture approval, moving/
fire/recoil/reload/lifecycle/FPS/build checks remain unrun.
