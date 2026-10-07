# Visible firing recoil — local repair complete

7 October 2026. The requested presentation fix is installed locally and passes fresh original-project regression. It is not a full character/contact/MVP acceptance or a published release. [Chinese review](RECOIL_RESULT_20261007_ZH.md).

## Cause and change

The retained baseline_v3 runtime confirms that the original firing transaction consumes a round and increments ShotSequence while ActionState remains Ready. Accepted FP and NPC displays keep Ready holding without consuming that counter, so they suppress the existing shooting motion. No ammunition, damage, input, AI or action transaction was changed.

Both display plugins now observe authoritative committed ShotSequence and RestoreGeneration natively. They sample the existing licensed Rifle_ShootOnce through full source-Skeleton GetAnimationPose, including its retarget rules; direct compressed bone extraction was not equivalent and its failed candidate is retained under AN009. The clip remains byte-exact:0.8s,31 samples, native maximum6.179330cm, endpoint0.006420cm/0.042915degrees. Native/editor differences0.004832cm/0.044260degrees pass unchanged gates.

The FP display moves its accepted whole assembly about the current hand without moving the camera. NPCs move rigidly related hand goals and solve six original-length arm rotations after accepted holding. Finger locals and all other locals are not modified by this recoil operation; source meshes, rigs, weights, materials, original clips, accepted configurations and guns remain unchanged. This is bounded adaptation of existing motion, not synthetic animation, whole-grasp transfer or further hand fitting.

## Actual tests

| Private identity | Verified result |
| --- | --- |
| native_source_v3_20261007 |31 native/editor source samples; owned40172 exit0/strict0/703exact |
| candidate_early_v3_20261007 | Original one-shot/cooldown rejection for player/Allied/German;18/20/19 active samples; gun excursion5.699/5.732/6.117cm; owned32584 exit0/strict0/703exact |
| candidate_contract_v3_20261007 | Each representative commits5 shots/starts5 recoils; repeated fire, cooldown/empty/busy/dead rejection, reload interruption/return, death/reset and Ready reset cancellation;1776 samples,4 unevaluated recreated-instance samples marked pending and NOT audited; owned45444 exit0/strict0/703exact |
| candidate_lit_visual_v3_20261007 |9 unpaused originals inspected: player ordinary viewport, NPC fixed show-only diagnostic with one temporary10000-lumen fill; visible recoil/return, connected arm outlines and no new obvious gun separation; owned35744 exit0/strict0/703exact |
| installed_runtime_v3_20261007 | Fresh ORIGINAL project, not temporary candidate: each role original one-shot/cooldown rejection,18/21/20 active samples, excursion5.672/5.506/6.069cm, max interval0.070308s, gun-hand drift below8.3e-13cm; owned51084 exit0/strict0/current703exact |

Candidate contract maximum hand-goal error3.076e-13cm and protected-pose metric3.818e-6 remain within original limits; untouched quaternion components are exact.38 offline tests pass (20 existing NPC guards/acceptance audits +18 recoil contracts/audits). Frame intervals are observation cadence, not FPS benchmark evidence. The one-shot samples remain Ready as intended; the observer does not commandeer ActionState.

Earlier world views with railings and dark isolated views were all retained, inspected and excluded from complete visual admission. Lit NPC images remove foreground geometry from the diagnostic render only; they do not establish world clearance or hidden contact. Texture streaming sharpens details between images; no texture/material authoring occurred. Native source idle motion may continue while recoil returns to identity; NPC return does not freeze the original animation at the earlier screenshot time.

## Local selection and recovery

Only three display DLLs changed: ParisGripBindingV18 runtime and ParisNPCGripV15 runtime/editor. Both module manifests are byte-identical and were not replaced. Installation occurred with no native process; exact original DLL backups reside in private RecoilV1/local_install_v3_20261007. Its immutable receipt remains correctly marked runtime-unpassed at installation time; the later runtime proof is separate, never rewritten into it.

[AUTHORIZED_LOCAL_BINARIES_20261007.json](AUTHORIZED_LOCAL_BINARIES_20261007.json) authenticates the exact three-path mutation and receipt. NPCInteractionV1/common.py applies that explicit allowlist after the immutable678+B+9ff map epoch.703 guards remain,700 other paths exact, including current map, source assets, accepted grip configurations, gameplay/AI and Catalog. Final selected_local_v3_20261007/result.json records current703 and authenticated runtime/image paths. Other lanes must adopt this local increment rather than restoring historic DLL/map hashes.

No formal map/asset/config save, SFTP/Catalog publication, commercial-byte publication, deletion, Git commit or push. All this lane's engines exited; later foreign engines are preserved and ownership must be checked again.

## Limits and next step

7 October source-only publication addendum: the user now requests commit/push
of this window alone. The prior no-Git statement is the dated repair checkpoint.
Only recoil source/tools/hash metadata/reviews/AN009 and recoil-only shared-file
hunks are in scope. The other window's unfinished AI/map/navigation work and
editor presets remain unstaged; private DLLs/asset bytes/receipts/images stay
private and Catalog/SFTP are unchanged. The shared recoil guard is a wrapper
around the existing base epoch; this separation does not alter the current703
rows. A clean source checkout without the excluded local baseline/private
receipts must fail closed, not silently adopt or reconstruct them. Source push
is not a new standalone playable-release or whole-MVP acceptance claim.

This closes missing visible recoil for the current supported player and representative Allied/German presentation types. Existing standard NPCs use the shared native policies; this does not assert separate firing tests for every individual or a different rig/weapon. Human artistic motion acceptance, full skin/contact/depth/recoil-chain smoothness, clear-shot/muzzle/near-wall, all actors/stress FPS, Shipping and second-machine gates remain unpassed. Multiple unseen committed shots fail closed rather than inventing missing motion; binding captures the current sequence and does not replay historical shots. Stopped AN001/AN008 routes and original German/Allied contact failures remain stopped/evidence, not retroactively passed. Navigation/startup stays with the other window.
