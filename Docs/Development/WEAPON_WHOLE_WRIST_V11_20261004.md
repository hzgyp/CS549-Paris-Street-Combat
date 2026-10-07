# V11: intact-grip wrist placement, one offline comparison

4 October2026. [Chinese review](WEAPON_WHOLE_WRIST_V11_20261004_ZH.md).
User explicitly resumes the proposed whole-hand/wrist experiment. This resumes
only that bounded comparison, not V7–V10 digit fitting or formal game integration.

## Reviewed failures and changed hypothesis

Read current HANDOFF/Git, failure index, full AN003/AN004/AN005/FP001 analyses,
the closed-grip pause/result and approved trigger/index result. AN003 proxy
contact is not actual skin acceptance; AN004 transitions and AN005 sleeve
artifacts remain open; FP001 warns against whole-view offsets and hidden cuts.
V6–V10 individualized digit fits are stopped and will not be used or rerun.

Instead of changing finger curls, fit the intact existing grasp to the stock
neck. Baseline: existing D059 Aim Reload0s, V2 calibrated M1 gun transform,
V3 accepted index LOCAL rotations; other digits use the original D059 pose,
not V4/V5 thumb or V6–V10 candidates. Reuse the already inspected DVIDS/UNT
M1 shape references; hidden exact angles remain unknown.

## Scope and storage

- New tools only under `Tools/Integration/WeaponWholeWristV11/`.
- New private evidence only under the single existing workspace
  `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponWholeWristV11/`.
- New editable offline Blender comparison, no native UE package/map save,
  NPC edit, Catalog/release, commit/push or editor-slot claim.
- Keep model/topology/UV/material source/rig/weights/source clips/camera/gun
  transactions byte-exact. Preserve old diagnostics; no rollback/deletion.
- All right digit local rotations/translations/scales stay identical to the
  comparison baseline. A common right hand/wrist translation is the ONLY fit
  variable. Gun/left support fixed in the baseline frame; not hand co-motion.
- A source-length-preserving right upper/lower-arm IK adaptation may place
  the wrist without detaching it, using the existing elbow bend side. Preserve
  hand orientation; no digit targets, new bones, weights or action keyframes.

## Order and early check

Technical landmark correction, before any pose was changed: `landmarks_v1`
mistakenly treats a mean of finger-bone locations as the empty grasp cavity.
Its4.76172cm displacement stops at the1.5cm cap, inputs unchanged. The mean lies
inside/below fingers, not the space between palm and stock; three inspected
baseline views show this definition is unsuitable. Preserve that result.
ONE correction replaces this proxy with actual opposing palm/wood SIDE surfaces:
select the hand-dominant inward palm patch and nearest same-side stock-neck
surface, derive transverse seating from their true gap. No cap/gate relaxation,
alternative pose, digit-angle solve, or repeated offset candidates. Stop if
actual contact faces cannot be identified. All downstream checks unchanged.
The first palm-probe launch exits0 but fails importing its sibling helper before
creating evidence (`ModuleNotFoundError: wrist_common`); not a completed probe.
An explicit script-directory import path fixes this invocation only, new
`palm_landmarks_v2b` identity. No fitting change or model edit.

The corrected palm-side closure target is4.53482cm and is also STOPPED at the
unchanged1.5cm cap; no full seating candidate. That broad palm-side target is
not proof of the displacement needed for a C-shaped grasp. It cannot be used
as an accepted fit or a reason to enlarge scope. The user asks to move it only
"a little": retain those stopped measurements and create ONE separately named
`small_approach_v1` comparison,0.75cm along the measured inward transverse
direction, without attempting full palm closure. This is a bounded diagnostic
partial approach, not a second closure solver, changed finger pose, relaxed
contact threshold or parameter sweep. Report residual gaps/trigger loss honestly;
if it fails the original early checks, stop after retaining before/after evidence.

1. Read-only inspect actual palm/inner-pad geometry and closed stock-neck
   cross-section. Record the contact landmarks and ambiguity.
2. Derive ONE translation from the intact grasp cavity center to the actual
   stock section center; maximum1.5cm. No offset grid, separate finger solve,
   changed curls, or repeated target variants. If the section/grip landmark
   is invalid or translation exceeds this cap, stop before a candidate.
3. First fixed0s comparison uses fixed gun. Re-evaluate actual skinned
   hand, index/trigger, all digit/gun and nonadjacent digit/digit crossings,
   left support, bone lengths and wrist/forearm edge stretch.
4. Render before/after right, opposite, top, bottom, oblique and whole-arm
   images; actually inspect them. If contact fails, retain failed evidence
   and stop, without adopting or running a new fit. A static pose cannot
   establish continuous reload, movement or native gameplay acceptance.
5. Save new diagnostic blend and fresh-open it in a separate Blender process;
   verify saved data and input hashes, then recheck528 current native guards.

The user's shift necessarily changes world index position, but not its LOCAL
pose. Replace the former exact world-skin-zero criterion with explicit actual
trigger review; do not silently bend the index to compensate. Early success
requires a visibly better coherent stock-neck grasp without lost trigger/left
support, increased skin crossings or new severe wrist/forearm distortion.
Check maximum0.2cm actual index-pad distance, no new index stock/guard crossings,
no new severe edges (>3x and >2cm extra), arm length error<0.001cm. Existing
index blade22 crossings and source shoulder artifacts are retained limitations,
not automatically cleared or permissible increases.

Stop at failed geometry/visual/continuity check, >1.5cm translation, unreachable
arm target, or source/guard change. The result is an offline proposal requiring
user review, not a final animation/reload or NPC acceptance. Any later native
adaptation/continuous-action test first needs a new documented mechanism and
serialized editor coordination; do not unlock AN004/AN005 or prior digit fits.
