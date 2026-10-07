# V14 — fixed hand, thumb-only rifle seating

2026-10-04. Status: implementation authorized; results not yet claimed.

The latest user explicitly changes this iteration's target: move/rotate the rifle
toward the unchanged right palm; the thumb must remain above the stock without
penetration. Middle/ring/little positions are reported but do not gate this trial.
This supersedes V13's no-third-angle/aggregate-digit gate for this bounded trial
only, not its failed result. Thumb-only success is not complete grip acceptance.

Read: HANDOFF, current Git state, Failures index, AN003, AN004, AN005 and FP001
full analyses, V12/V13 results and previously inspected real M1 grip references.
AN003 warns against proxy contact; AN004/005 and FP001 stopped native mechanisms
are not rerun. Broad-palm nearest points are direction evidence, not grip centers.

## Changed mechanism and early proof

Use the original D059 0-second pose, V2 rifle calibration and accepted V3 index
locals. Right arm/hand/all digit poses remain fixed. Start from the measured
turn-toward-palm direction, choose one analytically derived rigid rotation, then
seat the actual stock upper surface beneath the fixed thumb underside. A read-only
surface probe precedes fitting. No angle grid or individual digit solver.

One coherent rigid fit may include translation, pitch/roll/yaw, within 45 degrees
from baseline and 4 cm additional translation from the trigger-pivot placement.
Actual wood/skin surfaces, not bones or a single thumb tip, govern the fit. Check
all thumb triangles against all rifle triangles and underside-to-upper-stock
clearance/placement; inspect top, both sides, bottom and oblique original images.
The thumb must visibly be above the stock, near it, not simply far from the gun.
Keep index local pose exact; report actual trigger gap/crossings separately, with
no automatic finger compensation or claim that approved trigger contact survived.

Left support follows the rifle's position/orientation using original-length arm
IK and original elbow side. Protect wrist continuity and source skin/weights;
check right skin <0.0001 cm, all finger local matrices <1e-10, arm lengths <0.001
cm, left palm following <0.02 cm, and no new severe edges (>3x and >2 cm extra).
Middle/ring/little intersection counts are explicitly non-gating this iteration.

If thumb placement cannot satisfy these bounded constraints, retain the evidence
and stop rather than bend digits, edit weights, rescale the gun, move the camera,
or restart a parameter sweep. A numerical pass still needs actual multiview review.
Save one new static diagnostic blend and fresh-open it in an independent process.
Static success is not motion, native integration, export or gameplay acceptance.

## Storage and protections

New code: Tools/Integration/WeaponThumbGunSeatV14. Private evidence only in the
single SFTP workspace Evidence/WeaponThumbGunSeatV14. Preserve all earlier inputs,
10/20-degree blends/results/source hashes and 528 current recovery records (the
snapshot includes the previously recorded unselected V6 saved-rate difference).
No UE slot/writer, NPC/B/BT/BB, formal-map selection, Catalog, release, package,
cloud spending, commit or push. Source actions/model/rig/weights/camera/ammo and
gun transactions remain unchanged. After local thumb review, whole-grip, trigger,
aim and native/motion validation remain separately open.
