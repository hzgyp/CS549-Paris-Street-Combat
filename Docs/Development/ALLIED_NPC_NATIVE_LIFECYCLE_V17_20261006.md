# Native animation-instance lifecycle V17

6 October 2026. Read V15/V16 plans, actual audit17b result/native observations,
AN001–007, FP001, weapon-hand guide and source UE SkeletalMeshComponent/Quat APIs.

Audit17b proves SourceReload protected raw quaternion component delta0,
norm error8.715524e-7, old raw angle0.151291deg but physical normalized angle
3.415095e-6deg. Previous nonunit-angle alarm confirmed; actual pose not normalized
or changed. Standing/300cm/s walk binding pass. Original ammo1/16->8/9 returns.
Return remains STOPPED: wrapper retains a transient native input/protection
failure, while freshly observed new Ready instance evaluates3 times/valid input/
physical protection1.707547e-6 and raw component delta0. Source mode transitions
Blueprint->SingleNode->Blueprint reset instance/evaluation counters. No full
continuity/near-wall/clear-shot/lifecycle/visual action acceptance or adoption.

Native buffer ends before Ready and records exact0.333333s frames. Background
editor throttling is a supported source-code explanation, not a measured sole
cause. These frames cannot establish the planned<=100ms continuity gate/FPS.
Do not rerun the stopped full city motion proof, increase blend time or change
gun/hand/weights/camera/motions.

## Bounded lifecycle correction / early check / stop

New native handling waits ONLY while the EXPECTED postprocess instance has
Evaluations==0. Maximum0.5game-seconds. No accepting a evaluated invalid pose,
protection error or wrong class; same existing tolerances. Count pending frames
explicitly, not a full-frame validation claim. The mesh/engine owns evaluation;
wrapper never writes a fallback pose. Include exact eval/valid/error in any
future stop message. Preserve11 accepted locals/.15blend/gun/source/611 guards.

One NEW reload-only diagnostic: original2/16->8/10 transaction, actual source
mode/reinitialization audit/Ready return and images; no walk/fire/full old proof
rerun. Early Ready11locals <.01deg; actual gun <.01cm/.01deg. Pending initialization
must resolve within0.5s; first evaluated input/protection must pass. Stop on any
failure, no broader lifecycle suppression. Report full transition as unpassed
if pending frames/long frames prevent coverage; no threshold relaxation.

Persist/fresh-read the unselected native V16 draft per V16 plan. Never select
formal map or publish Catalog from this diagnostic. Actual foreground continuity,
compatible contact through reload, clear shot/recoil, near-wall, full lifecycle,
NPC2, FPS and packaging remain separate gates. No new finger/skin fit, FP/B/
German edits, original deletion or Git commit/push.

## Candidate-only project configuration closure

Read actual lifecycle V17 and V16 limits before closing. V17 reload-only result
does not pass the full-motion selection gate. After draft save/fresh read and
owned engine closure, remove ONLY this attempt's ParisNPCGripV15 enable row
from the project descriptor. Verify exact original descriptor SHA-256/text
against preflight_v1 and all611 separate guards. Preserve the already-formal
ParisGripBindingV18 entry and every unrelated project change. No asset removal.

Future candidate entries must explicitly enable ParisNPCGripV15 on their own
command line and verify the restored descriptor exactly, not silently accept
either epoch. Lock the stopped full-motion launcher. This keeps the current
formal teammate build free of an unpublished candidate binary dependency;
it is not a source/map/FP rollback or a successful candidate publication.

## Draft registry observer correction

Save entry PID31060 wrote the new8272-byte DataAsset, then dependency reporting
returned None and stopped. Fresh entry PID53556 stopped on the retained save
error, without authoring. Both normal exit0/611guards exact; neither receipt is
a successful persistence proof. Preserve both and the actual saved file.

Read installed IAssetRegistry.h: dependency queries concern on-disk packages;
ScanPathsSynchronous explicitly populates the registry. ONE new READ-ONLY entry
will hash-anchor the occupied two packages first, load/compare class/config/
skeleton, then force-scan ONLY /Game/ParisCombat/Animation/AlliedGripV15 before
dependency reporting. None remains an error, never treated as an empty list.
No re-save/recreation, new package, city map or motion proof. Field/hash/dependency
failure stops this correction; preserve the file as an unverified draft. This
is an observer correction, not permission to relax dynamic selection gates.
