# Real M1 references and closed-grip diagnostic — stopped, unselected

## Later checkpoint: user pause and whole-wrist proposal

4 October2026,23:06 EDT. This addendum records the interrupted continuation and
supersedes older pending-review statuses. The V6 report below remains historical
evidence; no candidate is adopted. The user pauses the per-digit direction and
suggests preserving the preceding grip, moving the entire right hand/wrist toward
the stock neck. This request is handled as assessment, not resumed authoring.

All continuation evidence remains private under `Evidence/WeaponClosedGripV6/`
in the same workspace; no native/game/NPC changes occurred:

| Offline identity | Actual outcome; not acceptance |
| --- | --- |
| `envelope_fit_v7` | Eight sampled non-index gun-intersection checks clear, but inspected grasp remains loose and the gun-only gate lacks complete self-contact acceptance. Four0s candidate views inspected; not all33 generated views. No V7 self-crossing count is inferred from V8. |
| `chain_seat_v8b` / `final_review_v8` | Root-chain seating clears sampled gun crossings, but actual nonadjacent middle/ring58 and ring/little141 triangle-pair intersections are new against source0. Four0s views inspected; six whole-arm review images and composed sheets generated but not inspected. Preserve v8's initial applied-vs-target angle-gate mistake and corrected v8b separately. |
| `coupled_grip_v9b` | Two-iteration stall retains58/141 self-crossing pairs; stopped. v9's NumPy integer JSON serialization failure retained; v9b only fixes serialization. Its30 images were not inspected. |
| `triangle_witness_v10` | Source-ordered triangle witnesses clear sampled gun and self-crossings, but four inspected0s views show little finger extended away from the stock; closest-pad mean gaps1.68/2.094cm. Numerically clear is not a closed grasp. |
| `triangle_witness_v10b` | One documented source-axis selection correction completes exit0/errors[], unchanged inputs/no native authoring. Eight samples retain middle/ring4 and ring/little20 self-crossing pairs; early gate false, stopped. Its30 images not inspected; no retry. |

Intersection pair counts are not penetration depth/volume. V7/V8 earlier gun-only
gates were insufficient; their frozen `pending_visual_review` flags do not grant
acceptance. V10b was already running when the user interrupted and finished
without further edits; the session was polled to completion, not restarted.
All fingers-only solvers are now stopped/unselected, not a starting point for
more iterations. Source models/rig/weights/clips/camera/gun transactions unchanged.

### Assessment of the proposed whole-hand shift

The proposal changes the hypothesis from independently shaping digits to fitting
the intact grip relative to the stock. It is a worthwhile first comparison, not
a proven fix. Suggested baseline: prior V2 actual-trigger gun calibration plus
V3 approved three-index local rotations over the existing D059 pose, **before**
thumb/full-digit experiments. No old native files are restored; this is a
comparison baseline only, and the user may identify a different prior pose.

Read-only source check: the existing native source preview attaches the gun to
`hand_r` with a fixed relative transform (`ue_reload_contact_fit_v3.py`31–40);
the accepted offline calibration likewise uses a hand-relative gun matrix.
For gun transform `G=H*T`, moving both through `H'=D*H` preserves `H' inverse*G'=T`.
Thus changing only that shared parent cannot close their relative gap. It is
necessary to distinguish the independent gun target from the hand fitting layer;
this algebra is not a new actual-game binding/runtime test.

Retaining finger LOCAL rotations preserves the grasp shape, but translating the
whole hand also translates the index. The previous exact world-space index-skin
zero-delta condition cannot remain simultaneously true for a nonzero whole-hand
translation. Check trigger alignment visually as a separate requirement; do not
silently compensate with new index rotations. Wrist movement must also retain
continuous forearm/cuff geometry, not detach the hand or stretch a seam. A
later bounded owner-view trial may use arm-chain fitting of existing motion;
it must not rewrite source actions/weights/rigs or automatically propagate to NPCs.

After explicit user resumption, first document ONE fixed-pose comparison with
intact fingers and independently held gun, derived from actual palm/stock-neck
contact. Inspect thumb/web, underside enclosure, index/trigger, left support and
wrist continuity. Stop if contact improves only by losing trigger/support,
creating new penetration or wrist/sleeve distortion. Only after this early
comparison succeeds consider continuous holding/reload transitions and native
integration with a serialized UE slot. No wrist transform, IK, new render,
animation or runtime test was authored in this pause assessment.

### Verified protection at the pause

Read-only23:06:05 EDT recheck: all528 current `map_recovery_v1` size/SHA records
match; canonical map SHA256
`2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`.
This current snapshot includes the known unselected V6 saved-rate difference;
not a claim that528 files equal the older original inventory. No Unreal/Blender
process remains. B's editor reservation is unaffected; no B6/controller/BT/BB,
formal asset/map selection, Catalog/release/package/commit/push. Dirty source
work and all failed evidence retained. HANDOFF/AGENTS/failure index updated;
stay paused until user resumes, without continuing the digit solvers.

## Earlier V6 result

4 October2026. [Chinese review](WEAPON_CLOSED_GRIP_RESULT_20261004_ZH.md).
Plan: `WEAPON_CLOSED_GRIP_REFERENCE_V6_20261004.md`. Relevant AN003/004/005,
FP001 and the rejected coarse left-finger result were reviewed before authoring.
Blender character workflow requires actual skin/multiview evidence; numerical
contact improvement does not replace grasp acceptance.

## Reference correction

The user rejects isolated thumb contact: thumb/web above the stock wrist and
middle/ring/little fingers wrapping beneath must form one grasp. The approved
right index/trigger contact remains protected; left hand remains support.

Actual browser images inspected, not merely search captions:

- [Official Marine Corps,2013 M1 photograph](https://www.dvidshub.net/image/979778/52nd-annual-interservice-rifle-championship):
  standing side view shows the firing hand enclosing the rear stock wrist.
- [Official U.S.Army,2024 M1 photograph](https://www.dvidshub.net/image/8584839/european-best-sniper-team-competition):
  alternate kneeling/reaction view supports the upper thumb/web and surrounding
  palm relationship. This is modern shape reference, not1944 loadout approval.
- [UNT/12th Armored Division Museum,1943–45](https://texashistory.unt.edu/ark:/67531/metapth436643/):
  actual high-resolution historical crouched outline inspected; the firing hand
  is largely hidden, not evidence for exact hidden digit angles.

Only links/observations retained; no remote images downloaded, committed or used
as textures. Occluded finger pressure/angles are unknown. The correction is
enclosure, not fingers independently pointing at nearest wood.

## What ran

Offline evidence under the single private workspace
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponClosedGripV6/`.
Source helpers under `Tools/Integration/WeaponClosedGripV6/`.

1. `probe_v1`: existing D0590/2.2s and Rifle_Idle0s rotations compared on the same
   accepted index/gun calibration. D059 is closer; its mature wrap retained.
   Four index-mask vertices have middle_01_r weights0.22745..0.36078. That joint
   also remains fixed to protect exact evaluated index skin.
2. `fit_v1`: ONE bounded local adaptation of middle_02/03 and ring/pinky_01/02/03,
   using broad second/distal phalange patches and evaluated near-stock envelope;
   maximum18 iterations,30degree local/20degree distal limits. The V5 upper thumb
   hypothesis is copied, not selected as a complete grasp. No new animation.
3. Eight sampled phases preserve approved index vertices exactly0cm, other bones
   and unaffected skin exactly0; no new severe edges under the stated diagnostic
   criterion. This is not a complete hand/shoulder deformation pass.
4. Thirty matched before/after images generated. Eight individual images actually
   inspected:0s baseline bottom; candidate0s right/left/top/bottom/rear-oblique;
   candidate2.2s bottom and4.1s rear-oblique. Bottom views still show deficient
   enclosure/spacing; the visual improvement is small, NOT a successful grasp.

| Each of8 phases | Thumb stock crossings | Middle | Ring | Little |
| --- | ---: | ---: | ---: | ---: |
| New candidate |0|18|1|0|

Baseline D059 middle/ring counts were48/6. Reduced intersections are still failed
contact, not acceptance. Approved index remains stock0/guard0/blade22, unchanged;
complete blade clearance was never claimed.

Read-only `failure_probe_v1` localizes remaining middle intersections predominantly
to distal skin, and the ring intersection to distal skin. Thus the shared middle
root is a protection constraint, NOT a proven sole cause or proof that a fixed
palm/gun is impossible. No second fit/angle scan or threshold relaxation ran.

## Stop and protection

`fit_v1` status `stopped_at_actual_contact_gate`, exit0, errors[], inputs unchanged.
Read-only localization also exit0/unchanged. Fresh Blender5.2.2 opens the diagnostic
blend, exit0/read-only/bytes unchanged; SHA256
`611a0eb82b1cbef4431e24852517ae7f8e9841972992fe2183fa45a586b08c2b`.
Gun2131vertices/3923faces; each selected-hand object uses the6135vertex array and
4308faces. This is static evaluated diagnostic geometry, NOT a playable rig export.

All528 current map_recovery_v1 size/SHA guards rechecked and match, including the
known unselected V6 saved-rate difference. Canonical map remains2791b4a7...ad68519.
No UE/Blender process remains. No engine reservation/native authoring/NPC/B6/BT/BB
change, formal selection, release/Catalog/package/commit/push.

V4 thumb-only fit retained28stock crossings; V5 removed sampled thumb crossings
but the user rejects isolated-thumb target. Neither is a closed-grip baseline.
Retain all old inputs/evidence, no rollback over unique work.

Before another attempt: explicitly change the contact mechanism for coherent
stock-wrist enclosure, inspect compatible mature grip content first, preserve
approved index contact and source/weights/gun/camera rules, document whether any
protection exception is actually needed. Do not infer one from this failed solve.
No native integration or automatic repeat of this stopped patch-target fit.
