# German NPC V11 — mature middle/ring/little grasp adaptation

6 October 2026. User accepts V10 thumb and marks the lower three right fingers:
their finger pads must seat on the stock rather than loosely hover. This permits
local adaptation of middle/ring/pinky only. It does not authorize new animations,
source model/weight edits, native entry or formal asset replacement.

## Reviewed cases and changed hypothesis

Read HANDOFF/618 current epoch, Git state, Failures index, V10 result, complete
stopped WeaponClosedGripV6–V10 result and calibration guide, character workflow
and its full references; GP010/AN002/AN008 previously reviewed. Old per-finger
envelope/chain-seat/coupled/triangle-witness solvers remain stopped. They produced
self-crossings or extended little fingers; do not run them or copy player values.
This new German pair starts from human-approved V9 position/V10 thumb and first
reuses ONE compatible mature D059 AimReload2.2s three-digit grasp together, not
independent target pointing or a freshly created action. Recorded source/local
differences range5.47..53.24deg, with source joint basis verified before reuse.

## Character contract and protected scope

Same69-bone native-cm rig/full25,236-vertex skin/42,753 triangles/original weights,
FineWoodV15 gun24,466 triangles. Only nine middle/ring/pinky RIGHT local rotations
eligible. Preserve local t/s/lengths, right wrist/palm/arms, accepted thumb locals
and skin, all index bones and actual distal trigger-contact skin, gun, whole LEFT
grasp/arm and all other body bones. Vendor rest/model/actions/UV/materials remain
untouched; diagnostic copies are not playable rig exports. Static pose only.

Actual shared-weight audit finds four proximal index-boundary vertices with
middle01 influence0.22745..0.36078, no shared lower-three/thumb influence.
Right index BONE preservation does not mean these four skin vertices stay fixed.
Report their motion and inspect the web/boundary/trigger; no source weight edit
to disguise it. This is not permission to change index local rotations.

## Early checks and evidence

Reproduce V10 fresh-view skin/gun<0.0001cm; current618 guards and input hashes
exact; source reference axes<0.001deg. Source-only exact quaternion reuse with
original local translations/scales, no finger stretch. Protected bone matrices
<1e-8, accepted whole thumb/actual distal index and true-zero-changed-influence
skin<0.0001cm; gun exact. Evaluate actual full positive-weight digit geometry.
Select broad distal-pad faces from source skin/normals facing the actual stock,
record their IDs, evaluate same pads after reuse. Report mean/min gap, nearest
wood face and skin direction separately from complete grasp/enclosure.
Target pads within0.3cm; decreased distance alone is partial improvement, not
successful seating. No new lower-digit gun crossing faces, nonadjacent finger
self-crossing pairs or severe skin edges (>3x AND >2cm-extra). Existing accepted
thumb/proximal overlap retained; do not restore a blanket zero-contact criterion.

Fresh separate-process reconstruction within existing0.01cm display parity,
matched right/reverse/top/underside and complete-arm views. Show accepted thumb/
index in context and inspect every original. Character workflow requires actual
deformation/contact views, not just bones or smaller numeric gaps. Gray colors
do not prove native materials, runtime motion or export compatibility.

## Stopping condition

Stop this source-only grasp comparison if guards/protection/contact/self/edge
gates fail; retain actual geometry and views without selection. Do not silently
repeat a stopped solver, scan angles or alter protected gun/thumb/index/wrist.
Any different bounded follow-up needs cause evidence and a documented mechanism
first. No formal adoption, source deletion, native engine/slot/map/package save,
Allied/FP/B/AI/Catalog/release/publication/Git commit/push. Formal German remains
unarmed; motion/reload/recoil/lifecycle/FPS/Shipping/second-machine untested.

Private evidence: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/
Evidence/GermanNPCLowerGripV11/mature_reuse_v1` and read-only review.

## Stock-section contact follow-up

ONE source-only grasp fails: pad mean middle/ring/little4.514/5.188/4.459cm ->
2.851/3.351/4.021cm, all still loose,16 new self pairs. Gun crossings remain0.
Retain this comparison; do not replay or scale its failed source rotation.

Changed mechanism: actual stock sections plus closed-form original-length
two-link finger chains, rather than old abstract envelopes/per-vertex angle
iterations. Start again from approved V10 and its mature original digit shape,
not the failed source reuse. Each MCP root stays fixed; all nine local t/s and
rest lengths remain protected. Actual gun longitudinal coordinate at each MCP
defines a section; small declared finger fan offsets are middle+0.3cm/ring0/
little-0.3cm along the gun, not bone translation. Ray actual wood at the section
center from its opposite palm side, use actual face/normal. Place a distal-pad
contact0.08cm outside it and orient the existing pad toward that surface.

Derive terminal bone target from the original pad/bone relation, not finger
bone head mistaken for skin. Solve original01->02->03 segment lengths once,
stable elbow toward gun underside to wrap rather than point straight at wood.
Keep separate longitudinal finger planes/read their positions, audit adjacent
fingers together. There is no source action authoring or continuous IK driver.
ONE measured static contact candidate only; no fit loop/angle scan. Cap each
local rotation change90deg and reject unreachable or straight/collapsed chains.

Earlier pad<=0.3cm/contact/self/edge/protection gates remain. Require joint-span
and local-t/s errors<0.0001cm/1e-5 scale, inspect finger flexion/negative space,
accepted thumb/index contact and actual skin. A bone/pad target is not visual
acceptance. Stop if any required chain/protection/contact/self/skin check fails;
do not retry another target fan/offset or revive stopped solvers. Separate
`stock_section_v2` receipt and fresh views preserve this attempt and the failure.

## Reach diagnosis and lower-surface correction

The section-center opposite-side target is rejected BEFORE candidate skin:
ring terminal reach9.185833cm exceeds original4.429875+3.476593cm. No stretch,
fan retry or angular increase. Read-only `reach_diagnosis_v1` then measures each
original pad's nearest ACTUAL wood point. These lie on the stock lower edge,
not the rejected center-height opposite wall: middle/ring/little oriented
terminal reaches4.352806/4.897669/4.931504cm, within original chains.

ONE different lower-surface candidate: nearest ACTUAL wood from the original
broad skin-pad centroid, with the actual outward normal, no section fan or
guessed center-height. Use original pad-to-terminal relation and orient it
toward that measured lower wood face0.08cm outside. Same closed-form original
two-link chain and underside elbow; fixed MCP roots, local t/s and90deg budget.
This changes incorrect surface selection, not the reach gate. The saved diagnosis
precedes authoring; retain unreachable receipt, no target/angle scan. All previous
protection, actual pad<=0.3cm, no-new-cross/self/severe-edge gates still apply.
Stop on a failure without silently loosening the gate or advancing native assets.

## Source-frame correction, same measured targets

Lower-surface v3 stops BEFORE candidate skin at middle02 local delta91.549864deg
>90deg. The gate remains90; do not relax it. Its fixed gun-down elbow and independent
world rotations add an unnecessary phalange-frame turn. `frame_diagnosis_v1`
reads the RETAINED exact three targets, uses the closest original elbow-plane
direction and transports the root swing through02 before its minimal bend.
Predicted largest local delta63.387227deg, no target/length change. Source-plane
turns44.82/36.76/28.56deg, so this is closest-source-plane adaptation, NOT literal
unchanged plane. Same mature original finger, no new animation tracks.

ONE source-frame correction of those same actual lower-wood targets, no new
surface/fan/angle scan. Protected root positions, t/s, lengths, accepted thumb/
index/left/gun and all earlier skin/contact gates remain. Fresh full skin and
matched original views are required; predicted joint angles alone are not pass.
Retain v3 receipt and frame diagnosis; failure stops without further fit retries.
