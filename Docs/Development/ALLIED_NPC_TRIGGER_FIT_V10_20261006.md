# Allied NPC — autonomous fixed-hand trigger calibration V10

6 October 2026. User authorizes continuous gun calibration until index/trigger
position is correct, without stopping for review after every2degrees. This
supersedes V9's per-comparison no-extra-angle stop ONLY for this Allied static
calibration. German, formal adoption and publication remain out of scope.

## Reviewed cases and changed hypothesis

Read HANDOFF/current dirty Git state, Failures/README, AN002, FP001, V7/V9
results, immutable V7 measurement/geometry and weapon-hand contact guide;
Blender character workflow and shared/form-fit references. Preserve V8's
interrupted unknown-exit evidence; its translation is not an input.

Unlike guessed2degree comparisons, new measured rigid fitting uses actual fixed
index skin, trigger-blade surface and free guard volume together. Continuous
iterations are authorized, but old finger/FP/AN solvers are not reopened.
Do not equate pad proximity with an index passing through stock or guard.

## Protected contract and routine bounds

Actual Allied US source/M1/native V9 Ready pose, cm. Entire right arm/hand/all
digit locals, source rest/rig/mesh/weights/UV/materials/actions, gun scale,
shoulder/clavicle, approved FP/German/B/BT/BB/map/Catalog/gameplay transactions
remain protected. Whole original-length left chain follows the final gun.
No new motion, separated hand shift, digit compensation or source edit.

Start from recorded actual V9, not V8. First solve3D rotation about marked
stock-grip pivot; allow measured small gun seating correction only if rotating
alone leaves irreducible contact error. Working local bounds: at most30degrees
relative to V9 and at most3cm pivot displacement,100iterations total; these
prevent runaway fitting, not a full-contact acceptance relaxation. No grid or
unbounded random angle/offset search. Retain trajectory/failed residuals.

## Early checks and completion/stop

Build signed-distance/contact diagnostics from original topology; verify
component winding/closure before interpreting signs. Use actual distal pad
and full index samples, not invented joint averages. Requested local gate:
pad–blade gap<=0.15cm, zero actual index stock/guard/blade crossing faces,
visually appropriate index/trigger relationship in both sides/top/underside.
Other digit stock contact is reported separately, not falsely accepted or
used to claim the requested local trigger result. No new gross thumb/palm
damage may be hidden by materials.

Retain unchanged right/unaffected skin<0.001cm and digit locals<1e-8; whole-left
segment lengths<0.01cm, palm tracking<0.05cm, zero new severe edges (>3x and
>2cm added). Stop on protected-input/geometry/arm-reach failure, unknown
surface sign, exhausted finite bounds or lack of demonstrable progress—not
merely an intermediate2degree misalignment. Do not expand to fingers or relax
acceptance thresholds when fitting is infeasible.

## Native evidence and handoff

Use only the proved paused-refresh frozen original-mesh viewing scaffold, new
identity and serialized slot, fresh actual process/611-guard checks. Inspect
baseline actual pose before final candidate. Render original textures, right/
reverse/top/front/underside trigger details and full arm; open actual originals.
No native live skin query, FP binding, source NPC driver change or map save.
Close own viewer normally, fresh-check input/guard hashes and process absence,
release lane A. Deliver fitted data/evidence and exact remaining limitations;
static contact is not playable-motion/AI/runtime-release acceptance. New files
and private ignored SFTP evidence only; no selection/deletion/Catalog/commit/push.

## Functional-surface correction within authorized continuous work

The first closed-stock/unsigned-open-component least-squares attempt completed
without source changes but retained37stock/17blade index crossings and1.106cm
gap at29.864degrees. It is unselected; its finite residual is not a reason to
ask the user to review another tiny increment. Inspection shows the inherited
nearest blade landmark is near its upper attachment/side, not the lower curved
working blade. Do not carry that failed optimized transform into the next fit.

Continue from protected V9 with actual component5 lower curved trigger faces,
excluding upper mount and flat lateral plates by their measured face normal/
location. Derive rigid rotations from these actual contact surfaces around the
marked stock point, with the minimum measured radial seating needed. Test
actual full-index stock/guard/blade intersections and closest distal pad,
instead of optimizing an arbitrary nearest upper-stem anchor. This is bounded
landmark-driven candidate selection, not random offset/angle sampling. Retain
all candidate residuals, same30degree/3cm bounds, unchanged source fingers and
full-left-chain checks. Unknown semantic/surface orientation or inability to
meet the unchanged local gate remains a stop requiring explanation, not an
automatic finger edit. No native viewing of the failed first optimizer.

Functional-point fitting V10b reached0.0379cm yet retained49stock/47guard/
33blade index crossings. This demonstrates why another point-only angular
increment is not enough. Continue the same protected rigid-gun method with
surface tangency: actual blade outward normal opposes measured finger-pad
normal; solve the remaining twist to minimize displacement of the original
marked stock pivot. Use actual curved faces, unchanged finite bounds and exact
triangle tests. This replaces point-only alignment with surface orientation,
not a new hand pose. No failed V10/V10b transform is adopted as its source.

V10c finds no fixed terminal-tip tangency within the existing30degree/3cm
bounds; retained failed result, no native authoring. The inherited pad is at
the forward tip, while a firing contact uses the distal fleshy/inner surface.
One further geometry reidentification considers only existing index_03 skin
faces within3cm of that terminal pad, facing inward toward the middle finger;
no hand/finger pose changes. Pair them with actual lower blade surfaces,
analytically match opposing normals and minimize marked-stock displacement.
Rank finite real surface pairs, exact-check up to80feasible pairs. This changes
which legitimate finger surface touches the blade, not acceptance thresholds
or firearm geometry. Keep every rejection and exact residual. If no valid pair
exists, report the actual fixed-pose constraint rather than generate fingers.
