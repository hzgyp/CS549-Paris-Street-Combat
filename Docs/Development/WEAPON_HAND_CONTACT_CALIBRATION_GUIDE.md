# Weapon–Hand Contact Calibration Guide

Project: Paris Street Combat · Updated: 5 October 2026

## Purpose and current status

Use this workflow to fit an existing licensed rifle to an existing animated
character, including Allied and German NPCs. Start with the mature holding pose
and the actual weapon geometry. Fit their relationship before editing fingers.
This is a fitting method, not a claim that the current player experiment has
passed every contact or gameplay test.

The V16 player fit is an **unselected offline experiment**. Its index is much
closer to the trigger, but thumb/guard intersections and support-skin tracking
remain open. V17 adds original textures only; it does not repair contact. Do not
use either inspection file as a production NPC rig or release authority.
The separately requested V18 little-finger proportion trial is not a prerequisite
or blanket permission to resize NPC fingers.

## Working rules

- Use the character, gun and finished motions already in the asset baseline.
  Search and inspect the purchased animation catalog before declaring a gap.
  Preserve vendor originals; do not make replacement motions from scratch.
- Write a bounded implementation plan first: relevant failure cases, protected
  inputs, changed mechanism, one early test and a stopping condition.
- Keep one physical asset workspace. Save new evidence/copies in the private
  SFTP workspace; Git stores tools, documentation, configuration and hashes,
  not commercial models, texture pixels, credentials or private evidence.
- Work offline first. Unreal authoring requires the project's serialized editor
  slot and an actual process/guard check. Do not close another person's editor.
- Treat each character/weapon pair separately. The player's first-person arms,
  Allied NPC and German NPC have different rigs, proportions, stock shapes and
  display chains. Reuse the method, **not the player's numeric transform**.

## Workflow at a glance

```text
Verified source character + mature holding clip + correct rifle variant
└─ Freeze the actual pose; verify scale, axes and binding
   └─ Keep the firing hand as the reference
      └─ Move AND rotate the gun to fit trigger / palm / stock neck
         ├─ Contact not acceptable → retain evidence; stop/replan
         └─ Contact acceptable → fit support hand through the whole arm chain
            ├─ Stretch/contact loss → retain evidence; stop/replan
            └─ Continuous arm + contact acceptable
               └─ Frame the complete fitted assembly; recheck aim/muzzle
                  └─ Test existing actions and transitions
                     └─ Fresh export/import + actual UE NPC/gameplay review
                        └─ Human acceptance → verified shared-asset release
```

## 1. Freeze and inspect the real target

Record source paths/hashes, character/weapon variant, units, rest hierarchy,
active display mesh, pose driver/leader and the exact clip/phase. Confirm the
weapon's real dimensions; avoid compensating for import-unit mistakes with
arbitrary gun or hand scaling.

Inspect the actual mesh rather than socket names. For each pair identify:

| Character landmark | Weapon counterpart |
| --- | --- |
| Right index pad and finger path | Actual trigger blade and free guard volume |
| Palm cavity / thumb web | Narrow stock wrist immediately behind the trigger |
| Thumb upper contact | Upper stock-wrist surface |
| Middle/ring/little wrap | Lower and opposite stock-wrist surfaces |
| Left support palm | Appropriate forward stock/handguard surface |

Use real holding photographs as shape references, not calibrated measurements.
The previously inspected M1 references are recorded in
[WEAPON_CLOSED_GRIP_RESULT_20261004.md](WEAPON_CLOSED_GRIP_RESULT_20261004.md).
A photograph with hidden fingers does not establish their exact joint angles.

Use fixed front/side/top, reverse/underside closeups and a full-arm context.
Diagnostic hand-only views may expose the grip, but must be clearly labeled;
they do not prove wrist/sleeve continuity. Restore actual corner UVs and source
material slots for textured inspection; never infer wood/metal membership from
a coordinate box or use dark textures to conceal intersections.

## 2. Keep the firing hand fixed; independently fit the gun

Keep the existing palm, wrist, approved index pose and other finger rotations
fixed initially. Translate the gun to the actual trigger/pad relationship, then
rotate it to seat the stock wrist inside the existing grasp. Translation alone
cannot fix an orientation mismatch. A guessed angle is a comparison hypothesis,
not the correct angle for every character.

Use an explicit pivot on actual weapon geometry:

1. Initial trigger placement: the trigger region is a useful alignment anchor.
2. Stock seating: inspect the palm cavity and thumb web; adjust the gun's angle
   and position without stretching the firing arm.
3. Final trigger correction: once the stock neck is seated, a measured pivot
   inside that grip can raise/lower the muzzle toward the fixed index. Confirm
   that this does not reintroduce thumb or guard penetration.

For column-vector transforms in one declared coordinate frame:

```text
G_new = Translate(pivot) · R · Translate(-pivot) · G_old
T_gun_to_hand = inverse(H_right) · G_new
G_runtime = H_right_evaluated · T_gun_to_hand
```

Here `G` is the gun transform and `H_right` is the firing-hand transform. Record
the frame, handedness, matrix convention and units. Blender/UE reflection can
reverse triangle-normal parity; review transformed geometry and normals rather
than copying a previously incorrect face-direction label.

Moving a hand and its already-attached gun together does **not** improve their
relative fitting. Conversely, keeping finger local rotations unchanged does
**not** guarantee world-space trigger contact after the gun moves.
Check both physical contact and the complete silhouette after each coherent
change. If a fixed gun scale cannot satisfy several landmark constraints, record
the residuals; do not silently distort the gun, stretch digits or sweep offsets.

## 3. Fit the support hand through the whole arm chain

After right-hand/gun contact is acceptable, derive the left-hand target from
the fitted weapon's support landmark. Use upper arm → forearm → wrist IK with
the original segment lengths and a stable elbow bend plane. Preserve the
existing support-hand grasp unless a separately authorized, source-based
adaptation is necessary.

Check actual palm skin, not just wrist-bone coordinates. Mixed weights can leave
small tracking differences even when the bone target is exact. Inspect the cuff,
wrist, elbow and shoulder in full-arm views; unreachable targets or new sleeve
stretching are stopping conditions. Do not detach/translate the hand mesh alone,
scale the arm to reach or hide a broken seam with a new mask.

## 4. Frame the assembly and preserve aiming responsibilities

Only after relative contact is stable should the complete hand–gun assembly be
framed for the intended view. NPC third-person holding is not the first-person
camera setup. Preserve protected player camera settings unless new permission
explicitly changes that scope.

For ordinary holding, review a natural composition; exact muzzle/crosshair
coincidence is a separate aiming requirement. Define ADS separately if needed.
Recheck the muzzle socket/direction, near-wall obstruction and any combat code
that reads the weapon transform. A cosmetic transform can change gameplay even
when the firing function itself has not been edited.

## 5. Reuse existing actions; verify the actual binding

Test the same fitted character/gun pair in idle, walk, sprint, fire/recoil,
reload and return-to-hold, and the project's crouch/prone/carry states. Use only
actions the asset catalog actually contains. Missing suitable actions must be
recorded rather than generated automatically.

The gun must follow the same evaluated firing hand and pose driver as its
visible hands throughout motion. Check ownership/leader changes during reload,
post-pose attachment ordering and cleanup after Ready, interruption or reset.
Do not calibrate one mesh while the visible mesh follows another. Native UE
controls the playable animation/update path; offline Python is for preparation,
measurement and evidence, not the production per-frame driver.

Preserve authoritative ammunition, reload, damage and friendly-fire transactions.
Review transitions at matched phases and natural completion, not just frozen
endpoints. Existing action availability, a socket fit or correct ammo transfer
does not prove a visually continuous reload.

## 6. Acceptance, persistence and NPC handoff

Before editing, declare pair-specific tolerances; do not relax them after a
failure. Measure trigger/pad separation, thumb/stock and guard clearance,
support-palm error, arm lengths, wrist/sleeve deformation and digit self-contact.
Triangle crossing counts are not penetration depth; contact against the trigger
surface must be distinguished from visibly passing through it or the guard.
Open actual rendered details—passing numeric counts alone is insufficient.

Keep before/after views at identical phase, scale, camera, lighting and materials.
Fresh-open/export/import the exact delivery and verify topology, UVs, rig,
weights, relevant poses/actions, texture dependencies and protected hashes.
Re-run affected checks after the final edit. A static Blender inspection is not
an animation, native collision or gameplay pass.

Each NPC fitting record must include:

- Character and weapon source identities/hashes, historical variant and rights.
- Mature source action/phase and the verified display/attachment chain.
- Actual landmark coordinates, fitted pivot/rotation/translation and final
  hand-relative transform, with explicit units/frame/handedness.
- Support-hand target/IK settings and which source constraints remain protected.
- Before/after views, fresh verification and tested/unrun action/runtime cases.
- Remaining defects, selected/unselected status and human-review decision.

Keep Allied and German records separate. After human and runtime acceptance,
publish through the established SFTP manifest/hash workflow and update the asset
metadata. Do not overwrite the canonical map, shared combat base or another
lane's NPC controller/BT/BB to make a visual test convenient.

## Failure lessons that remain binding

- [Closed-grip V6–V10](WEAPON_CLOSED_GRIP_RESULT_20261004.md): independently
  solving fingers can clear numeric gun intersections yet introduce self-contact
  or an extended little finger. Those solvers remain stopped/unselected.
- [V16 marked pivot](WEAPON_MARKED_GRIP_RESULT_20261005.md): a measured grip
  pivot can improve trigger proximity while worsening thumb/guard contact.
- [FP001](../../Failures/FP001-20261003-first-person-view/FAILURE_ANALYSIS.md):
  full visibility/crosshair alignment and gameplay assertions did not establish
  a natural holding composition; cuts exposed forearm boundaries.
- [GP004](../../Failures/GP004-20261003-kar98k-surface-labels/FAILURE_ANALYSIS.md)
  and [GP009](../../Failures/GP009-20261004-spr-export/FAILURE_ANALYSIS.md): use
  real UV/material boundaries and verify the final fresh deliverable, not only
  the authoring scene.

This guide does not reopen stopped AN001–AN005/FP001 repair routes, authorize
new motions, detailed from-scratch character production, purchases or cloud
spending. Future NPC fitting requires its own bounded implementation and tests.

## 7. Left support-hand workflow after firing-hand acceptance

### Recorded scope and decision tree

This supplement records the actual first-person V20 repair, not a new NPC
implementation. It follows the [V20 plan](LEFT_SUPPORT_V20_20261005.md),
[measured result](LEFT_SUPPORT_V20_RESULT_20261005.md),
[human review](LEFT_SUPPORT_V20_HUMAN_REVIEW_20261005.md) and later
[V21 formal selection](FIRST_PERSON_FORMAL_V21_RESULT_20261005.md).
The earlier V16/V17 unselected status in this guide is historical; the later
accepted first-person assembly includes V20 left-thumb data. It is not an
approved Allied/German NPC fit.

The cases reviewed include the rejected V20 whole-grasp trial and
[AN006](../../Failures/AN006-20261005-native-fp-body-source/FAILURE_ANALYSIS.md) /
[AN007](../../Failures/AN007-20261005-fp-upper-body-action/FAILURE_ANALYSIS.md).
The change from the earlier right-hand procedure is to classify the support
defect before choosing an arm or thumb intervention:

```text
Accepted firing hand and fitted gun: freeze both
  |
  +-- Support palm/wrist misplaced?
  |     -> Fit the whole original-length left arm to the gun
  |        Preserve/reuse a compatible mature grasp
  |
  +-- Palm already close, but thumb visibly open?
  |     -> Keep wrist/arm/gun fixed
  |        Reuse only the needed existing thumb locals, with scoped approval
  |
  +-- Existing grasp incompatible or several contacts fail?
        -> Reassess a compatible source grasp and document a bounded plan
           Do not force a solution by moving individual mesh pieces
```

### A. Locate the actual support contact

Start from the exact accepted native hold pose. Freeze the gun transform,
firing hand, camera and authoritative gameplay state. Inspect textured side,
reverse-side, top and underside details plus a full-arm view. Mark the wooden
fore-end, palm pad, thumb pad, wrist and elbow in their actual coordinate frames;
a wrist-target match alone does not prove skin contact.

Use real holding references to understand the grasp: the palm supports the
fore-end from below and the thumb opposes the fingers around its side. The
previous photographs in the [reference record](WEAPON_CLOSED_GRIP_REFERENCE_V6_20261004.md)
do not establish one exact thumb angle or require the thumb to cross the barrel.
Do not interpret "grip the gun" as touching an arbitrary top point.

If the palm is displaced, use section 3's whole-arm, source-length IK through
shoulder, forearm and wrist, with a stable elbow direction. Check continuous
skin/sleeve deformation and existing digit contact. Never translate a detached
hand mesh or stretch the bones to reach the stock.

**Early acceptance:** inspect actual palm/thumb contact and the full arm before
native motion testing. Stop if seating creates new intersections, wrist seams,
an unreachable arm target or a required change to protected right-hand/gun data.

### B. What the previous left-hand repair actually changed

The V20 whole-grasp experiment rotated the intact left grasp by about 13.2
degrees with source-length arm IK. Thumb proximity improved, but gun-crossing
faces increased from 44 to 69, including 36 new faces. That trial was rejected
before native integration. Its angle and offset are not a reusable recipe.

Actual views then showed the palm was already close to the fore-end; the
remaining visible defect was the open left thumb. With explicit user approval,
the successful narrow adaptation reused local rotations for **thumb_01_l,
thumb_02_l and thumb_03_l** from a recorded existing D059 AimReload derivative
at 2.2 seconds. This was retained source/cache data, not a new animation or
adoption of the stopped reload-owner route.

Only the three local quaternion arrays changed in a new binding configuration.
Their local translations/scales, left wrist, other digit locals, right hand,
gun, source model/rig/weights/materials/actions, camera and transactions stayed
protected. Existing recorded poses that introduced penetration were rejected;
there was no arbitrary angle scan or newly authored finger motion.

Mean sampled thumb-pad/wood gap decreased from 2.51 to 1.04 cm. This improved
the visible grasp but did not prove complete enclosure or zero penetration.
The full source-weight boundary retained the same eight crossing faces, with
no new ones. Audit **every vertex with any positive thumb weight** as affected:
small shared weights can move neighboring skin even when other digit bone
locals remain unchanged. Only true zero-influence skin belongs in the
unchanged-skin check. The initial contrary classification was corrected, not
used to relax the gate.

### C. Verify binding, motions and final state

Fresh-read the delivery: its difference from the protected baseline must be
exactly the authorized three rotations, with source/cache provenance recorded.
Compare before/after at identical pose, materials, lighting and views. Frozen
diagnostic meshes are evidence, not playable rig replacements.

The existing native UE hold/display adapter consumed V20; no Python per-frame
pose driver was added. Paired Ready observations kept gun and left wrist delta
at zero and other digit rotations unchanged. Native review covered Ready,
300 cm/s left walk, the original reload and return to Ready. One reload conserved
ammunition from 2/16 to 8/10. The hold override releases during reload so that
the original manipulation can play; it must not lock a grasp onto a moving gun.

Later human review accepted the appearance and V21 formally selected the
assembly. Sleeve obstruction remains deferred, residual contact limitations
remain recorded, and full-return continuity/lifecycle/near-wall/performance
gates are not all passed. The original Rifle_Reload_2 remains: sampling an
existing thumb pose did not replace the reload clip.

### D. Apply the method, not the player numbers, to NPCs

Wait for the user's Allied/German markings, then make a separate bounded plan
for each actual rig, weapon and existing hold action. Establish that faction's
landmarks and compatible source pose; do not copy the player's transform,
2.2-second sample, quaternions, camera or tolerances blindly. Preserve the
accepted firing-hand/gun pair while correcting support, and test each affected
existing action and transition before adoption.

Stop on new contact/deformation failures or unauthorized protection changes;
do not expand a failed trial, loosen thresholds or resume stopped solvers.
This supplement changes documentation only. No NPC fitting or new runtime
acceptance is performed by writing it.
