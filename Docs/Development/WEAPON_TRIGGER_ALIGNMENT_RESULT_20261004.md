# Actual-trigger rigid translation — first comparison

**Later coordinate audit correction,4 October:** V2 verifies the Blender→UE
reflection; V1 omitted normal parity when assigning forward/rear-facing regions.
Those anatomical face-direction labels below are invalid. Preserve the original
parameters/counts/images as failed evidence; do not use its landmark labels for
future fitting. Visible conflicts remain valid. The corrected pivot/support and
bounded existing right-index pose comparison is recorded in
[the later result](WEAPON_TRIGGER_CONTACT_RESULT_20261004.md), still unselected.

4 October 2026. [Chinese review](WEAPON_TRIGGER_ALIGNMENT_RESULT_20261004_ZH.md).
Implements the first check in `WEAPON_TRIGGER_ALIGNMENT_V1_20261004.md`, after
AN001–005/FP001 and the rejected coarse finger case review. No finger correction
was authored/executed. **One translation was tested offline; candidate is stopped
and unselected because other contact conflicts remain.** No native authoring or
gameplay/transition/combat acceptance is claimed.

## Method and observations

Actual exported M1 has3923 triangles. Position-welded ANALYSIS adjacency (never
source edits) yields34 components; inspected side image identifies component5
curved trigger blade62 triangles and component4 guard126 triangles. Coordinates
fit72 owner reference positions with max0.00009025cm error; native compressed
poses at0/2.2/4.1 seconds skin the unchanged owner FBX. Component5's forward lower
blade region and actual distal-index rear-facing pad region define one translation
at2.2s. Area-weighted region centres are approximate contact landmarks, not proof
of exact3D surface contact; nominal0.03cm clearance is not measured penetration.

Gun-local translation cm=(+2.97981,-4.28746,+2.61890), hand_r-relative translation
delta=(+2.73130,+4.79925,+1.90457). Rotation and scale unchanged. These parameters
are a diagnostic candidate, NOT production settings or NPC restore authority.

All24 same-camera images were inspected as one sheet, plus original0s before/after
side/whole and2.2s after left/right/top detail. Index moves from upper stock toward
guard but still crosses geometry; support hand visibly loses contact at start/end.
At2.2s it overlaps receiver during reload, so this is not a clean fitted kit.
Crossing counts are surface intersections, not penetration depths:

| Phase | Index crossing triangles before→after | Entire right hand before→after | Left hand before→after |
|---|---:|---:|---:|
|0.0s|61→42|277→151|263→0|
|2.2s|62→71|278→180|329→233|
|4.1s|61→42|277→151|264→0|

Fewer intersections do not establish grip acceptance; zero left-hand crossings
here accompanies visible separation. Single-clip clay cutouts do not establish
native blended poses, camera presentation, movement or ammo/lifecycle acceptance.
This candidate does not prove all rigid gun fitting impossible or authorize
finger changes. Show the spatial comparison before deciding the next mechanism;
do not sweep this failed translation or adopt it in the game.

## NPC binding review — source evidence, not a new runtime test

Allied `Tools/Integration/ue_rifle_action_attachment_author.py` authors
`/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3`: hollow
averages (right index excluded), two-grasp heading and local(-LeftShiftCm,-8,0)
anchor; it has no actual trigger landmark. German `ue_german_rifle_author.py`
authors `BP_PC_GermanRifleAttachmentV2` with independent GripXYZ but the same
two-hollow strategy, no trigger contact. Earlier user report REV-03 remains open.
Review snapshot initially mislabeled Allied namespace as WeaponActionsV3; source
DEST above is correct, and source fixed for future runs; preserve frozen snapshot.

Player translation is not copied to either rig. NPC transform fitting/mesh views
are NOT performed this turn; no BT/BB/controller/B6 package changes. Before later
adoption, separately calibrate each rig/weapon/action family's actual trigger,
palm and support contacts, then fresh native movement/reload/near-wall regression.

## Recovery, protection and evidence

User-confirmed accidental Save All was backed up. Only canonical formal map was
restored from verified pinned-host SFTP, size2707948/SHA2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519.
V6 saved rate remains an unselected backed-up diagnostic; formal map usesPlayerV1.
Current528 size/SHA guards match recovery snapshot, including this recorded V6
change (527 match older records, NOT528 original matches). All inputs unchanged.
No Unreal/Blender process remains; A releases serialized engine slot back to B.

Private evidence under workspace `Evidence/WeaponTriggerAlignmentV1/`:
`topology_v1`, `trigger_fit_v1` (24views/source/blend/JSON), `review_v1`
(contact sheet/comparison/current528 verification). Recovery is
`Evidence/ReloadIndexContactV6/map_recovery_v1`. Blender5.2.2 exited0, no script
errors. Deprecation/missing imported normal-image path warnings preserved; clay
diagnostic uses independent materials, not a material/export pass.

No new native package, formal map trial selection, Catalog/release/package,
purchase, commit or push. Whole dirty-tree `git diff --check` also reports a
pre-existing DefaultEditor.ini trailing blank line; not changed as unrelated work.
