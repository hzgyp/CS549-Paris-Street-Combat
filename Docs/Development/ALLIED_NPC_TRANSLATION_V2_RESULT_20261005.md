# Allied NPC — user-directed translation-only views

5 October 2026. Implements only the latest instruction/addendum in
[the fitting plan](ALLIED_NPC_GRIP_V2_20261005.md): move the actual trigger to the
unchanged right-index pad, then show textured three views. No rotation, support
repair, finger adaptation or formal adoption is performed.

## Actual result

Private evidence: `Evidence/AlliedNPCGripV2/translate_only_v2` in the existing
single SFTP gameplay workspace. Actual native `PC_City_Ally1`, original M1/V3
attachment, Allied Stride and source materials; whole-world paused after Ready.

One world-space translation is `(-4.584193, +0.151078, +1.946161)` cm, total
4.982488 cm. This is approximately rearward4.6cm/up1.9cm for this actor, not
reusable NPC coordinates. Gun rotation and scale remain exact; every recorded
character bone transform is identical before/after. Original right-index three
locals match the reconstructed landmark source with0degree measured error.
Actual blade/pad landmark residual is0cm. This is a point-alignment result, not
whole finger/blade/guard clearance or a complete grasp.

All six native1600x1000 captures keep gun drift0cm: before/after right, after
front/top, full-arm context and trigger detail. Two2400x660 sheets contain only
original pixels resized equally and labels. Baseline side inspected before
translation; both sheets, after-side/top originals and full-arm context opened.
The gun's original collision mode is preserved, not repaired.

The visible partial result retains a straight index and changes stock/support
contact. Left support, other fingers, aiming and animation have deliberately
not been corrected. No continuous motion/fire/reload/lifecycle/near-wall test or
complete contact acceptance follows. Wait for the user's next marking; German
remains untouched and must wait for Allied acceptance.

## Preserved failures and verification

- Previous `stock_pivot_v1` remains stopped/unselected: 6.98degree rotation,
 4.98→3.90cm gap and new stock-crossing faces. It is not this candidate.
- `translate_only_v1` stops before movement on a harness-only NoCollision
 assumption. Actual baseline is QueryAndPhysics; equality to the actual source
 policy replaces that incorrect assumption, without a policy mutation.
- `translate_only_v1b` stops before movement at a Quat→Rotator constructor
 coercion error. Its native before-pose snapshot is retained. Pure xyz/xyzw
 arithmetic is separately checked against it: inverse roundtrip2.02e-13,
 all three index-local rotation errors0degrees. No guessed engine API/angle.
- Final `translate_only_v2` has errors[], normal process exit0/PID23032 absent.
 Both earlier processes also exit0; exit0 alone does not make their capture pass.
- All611 current combined size/SHA rows match before/after and fresh closed-editor
 check, including the exact user-authorized FF ledger. Old555-only mismatch was
 reconciled, never rolled back or silently ignored.

No UE/Blender process remains; Lane A releases the serialized native slot.
Approved FP, German, B AI, source models/rigs/weights/actions, formal map/Catalog
and commercial asset bytes remain unchanged. Images/data are ignored private
evidence. No package save, release/deletion, Git commit or push.
