# V16 — user's red-arrow stock-grip pivot

2026-10-05. The user supplies an explicit red-arrow location on V14's oblique
image. This supersedes V15's inferred thumb-edge section pivot for ONE new offline
gun rotation. Palm/all fingers/source mesh/weights/rig/actions remain unchanged.
Use existing V14 seating, not the failed V15 rotation; no native/game selection.

Read HANDOFF/Git, Failures index, AN003/004/005/FP001, V14 plan/result, V15 source
and actual results, plus existing real M1 references and character skill guidance.
Interrupted execution audit: no engine remains; V15 v1 stopped before rotating
at face-center sampling, v1b actually completed despite tool interruption. Its
17.479745-degree inferred-pivot rotation fails: thumb51wood, index74guard, gap
0.884671cm/radial residual0.893722cm, left tracking0.043453cm. Preserve both and
do not rerun them or call the interruption a rollback. This new attempt differs
by using the user-marked stock location and transverse muzzle-raising axis.

## Pivot and one calculation

Attachment649x515 includes31px header; source render1200x900 was scaled to the
remaining image rectangle. Arrow tip is approximately(319,324), i.e. source
pixel(591,545). Document this approximate mapping; use V14's exact saved camera
and projection to raycast actual wood triangles there. Inspect a marker image
before the rotation. The returned stock surface point is the fixed grip pivot,
not a thumb-nearest/hand-bone hollow. Preserve pivot within0.001cm.

Raise about the V14 rifle transverse axis; choose the single angular alignment
of actual blade landmark toward the unchanged index pad in the perpendicular
plane. No sweep, no pivot translation, no gun scale or digit compensation. Bound
additional raise to30degrees and require measured muzzle height increase. Report
remaining radial/axis mismatch rather than secretly forcing a contact.

Early screen: unchanged right skin<0.0001cm, all digit locals<1e-10; thumb whole
gun crossing0/visible above stock, index stock/guard0 and pad/blade gap<=0.2cm.
Other three digit counts are reported/non-gating under prior user instruction,
not presumed clear from a single picture. Left source-length IK follows gun;
bone length error<0.001cm/no new severe edges, palm tracking increase<=0.01cm from
V14's known0.029614cm. This relative screen does not clear the old0.02cm failure.

Inspect fixed-camera both sides/top/bottom/oblique/left-support/full-arm before
and after, retaining original shoulder sheets. Fresh independently read any
saved static blend; it is not a new playable rig/motion or UE contact acceptance.
If this one marked-pivot rotation fails actual contact, retain comparison and
stop; no angle/offset/marker grid, finger/weight edits or native/aim integration.

New tools WeaponMarkedGripV16, private evidence Evidence/WeaponMarkedGripV16 only
in the single SFTP workspace. Protect V14/V15/10/20 evidence/code and528 current
recovery files incl known unselected V6 rate difference. No UE slot/B/NPC/BT/BB/
formal map/Catalog/release/package/cloud/commit/push changes. No AN004/005/FP001
stopped mechanism reruns. The supplied screenshot is placement guidance, not
proof that the current lower fingers or future rotated grip pass intersections.

Pre-rotation geometry check: the marked pivot ray was visually inspected at the
arrow location, no pose authoring. A transverse-only rotation leaves0.898192cm
axis mismatch; thus choose the single minimal THREE-dimensional rigid rotation
about the same marked pivot, predominantly muzzle raising, rather than secretly
translate the gun/index. Raw equal-radius residual0.116471cm is reported; pivot
is not moved onto a bisector plane. All30degree/contact/clearance bounds remain.
