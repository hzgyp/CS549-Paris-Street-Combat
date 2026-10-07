# V19 — existing-motion first-person upper-body separation

5 October 2026. User asks to adjust observed problems. The accepted V18 hand,
gun/hand fitting, original camera25/0/60/FOV90, mesh/rest/weights/materials,
vendor clips, authoritative transactions, NPC work and528 current recovery
guards remain protected. No formal adoption/deletion or publication yet.

## Reviewed / different hypothesis

Read HANDOFF/Git, Failures/README, FP001, AN001–006, V18 binding plan/result,
current runtime C++ actor, old stride/directional source (read only), purchased
native animation index and character-workflow/execution guidance.
AN006's direct full-body copy is stopped. AN001–005 author/retarget/weights and
FP001 camera/offset/mask routes remain locked; no new motions or digit edits.

Source inspection: directional BlendSpace has idle at0, walk ring150, run ring300,
while ordinary player MaxWalkSpeed is300. Thus movement at300 selects third-person
run clips, including Rifle_StrafeRunLeftLoop; this is confirmed construction, not
yet proof of the offending bone. Diagnose actual existing idle/walk/run component
bone motion in an isolated Entry editor, using socket/component observations only,
no skin/vertex reads or native package saves. Measure root/pelvis/spine/clavicle/
arm local and component transforms. Keep original clip hashes/528 guards.

If compatible mature idle upper-body source removes the large third-person carry
translation, use a NEW native V19 subclass/source adapter: original body locomotion
continues unchanged; a hidden UE SkeletalMesh component plays the existing native
holding clip. Display root/torso/arm pose uses that existing clip while Ready,
with source-action takeover and return blended in the same bone space. Accepted
holding fingers, hand-relative rifle and source-length support IK remain V18.
Cache assembly frame once, not refit every frame/Ready transition. Source clip
paths/config stay private. This is reuse/blending, not hand-keyframed synthesis.

## Early acceptance / stopping

First prove source skeleton compatibility and pose excursions, then compile
native code and inspect actual-city idle/left/right/forward/back/stop views before
expanding. Require approved grip0.01cm/0.01degree, support0.2cm, arm length0.01cm,
camera1e-6cm, actual visible ordinary hold/clear center/no disconnected sleeve.
Reload must retain one conserved ammo transfer and natural return steps<3cm;
do not slow/offset/refit to hide a failed gate. Mid-reload images are required for
visual claims. No acceptance claims for unrun fire/recoil/lifecycle/near-wall/FPS.

Stop a physically/visually failing mechanism before adoption; preserve unique
evidence. Technical observer/interface faults are retained and may receive a
source-supported correction without changing physical thresholds or asset data.
Do not widen hand/skin/camera scope, overwrite old proofs, or silently freeze a
presentation mesh into production. If source compatibility/cause fails, report
the actual limitation rather than change the hand.

## Serialized slot

Initial process check: no Unreal/Blender. NPC thread snapshot notLoaded/completed,
B0 passed/B1 stopped, no B work dispatched. Lane A claims V19 diagnostic/native
slot before launch; recheck actual processes and release after task closure and
528 guard verification. Public Git stores generic code/metadata only; all native
configuration/media remain in the single ignored SFTP workspace.

### Diagnostic refresh correction

Entry editor source_probe_v1 exits0/40 samples/528 exact, but all clips and phases
produce zero bone excursions: the offscreen editor did not refresh the component
pose. This is not valid cause/compatibility evidence. Preserve v1/source_analysis_v1.
Use an isolated Entry PIE actor with AlwaysTickPoseAndRefreshBones and native
runtime refresh, still socket-only/no save; add actual cross-phase/cross-clip
motion assertions before treating measurements as valid. No animation/mesh edit.

Runtime source_probe_v2 produces real motion, but initial idle0/.125 samples still
show the precompile reference pose; exclude those from phase-range conclusions.
At refreshed normalized phase0.5, native idle hand Z125.150cm versus side-run
113.661cm (11.489cm lower), and forward-run hand Y34.064cm versus idle3.699cm.
This supports wrong full-body carry source, not a gun/finger fitting defect.
Do not claim the large initial idle33cm range as authored motion. A warmup-controlled
stock holding-clip comparison is allowed before selecting a stable mature source;
do not choose by clip name alone. No V19 runtime adapter authored yet.

holding_probe_v1 exits0 before samples: two catalog clips are not in the selected
native junction (v2 aim and relaxed idle). Original D059 Aim Idle IS present.
Correct only the available-asset list; keep failed receipt, no new import or pack
copy. V19 code draft has native hidden existing-motion source and separate class,
0.25s parent-local transitions from the previous displayed source pose, with
matched grip/IK blend; no Ready-time reframe. Base V18 default hook is no-op and
its alpha0/1 endpoints preserve original behavior. Old proof launchers stay locked.

### Refreshed source decision

holding_probe_v2:24 native samples,5s warmup, no errors/528 exact/original clips
unchanged. D059 W2_Stand_Aim_Idle_IP right-hand component span0.197/0.520/0.293cm,
versus original Rifle_Idle2.300/13.466/5.636cm. Generic US ThirdPersonIdle lowers
the arms and is not the rifle-hold candidate. Use the existing selected D059
aim-idle clip without editing/retargeting it, new V19 class only. Native socket
compatibility is preliminary, not full visual/export/deformation acceptance.
Preserve old plugin binaries privately before new build/install. Original body
locomotion/weapon transactions remain unchanged; this is display-source separation.

First host build fails with two source API errors: FReferenceSkeleton is struct,
not class; PoseableMesh derives from SkinnedMesh, so use CastChecked<USkeletalMesh>
on GetSkinnedAsset, not the SkeletalMeshComponent-only getter. Header/compiler
evidence retained in plugin_build_v1; one technical correction, new build_v2.
No runtime test or source/config/action/camera edit during this correction.

build_v2 compiles cleanly. Before any city proof, source evidence also shows
different authored holding origins (D059 hand +X20.7 versus current idle -X25.8
at phase0.5). Raw cross-source blending would mix incompatible stance frames.
Add ONE initialization-only hand_r source-space registration: original body
source is mapped into the holding source frame by its initial right-hand matrix.
This fixed registration affects action-source root only; all parent-local vendor
motions/limb lengths remain, no per-action re-fit or camera transform change.
Retain build_v2, rebuild_v3 for this source-space completion before first native
city launch. Early city idle/left images pause the test observer for explicit
image inspection, not a user permission gate. Only pass permits remaining tests.
