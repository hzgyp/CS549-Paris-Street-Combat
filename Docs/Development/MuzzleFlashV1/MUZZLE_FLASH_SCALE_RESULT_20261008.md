# Smaller rifle-flash comparison

8 October2026. The user requests “缩小一点” after the unit-scale rifle preview.
One isolated comparison uses instance scale0.25 on both actual selected rifles.
The original images show a visibly smaller, compact outward main flame. Native
origin, direction and completion checks pass. Human size review is pending;
this is not formal installation or a completed firing-flame fix.
[Chinese review](MUZZLE_FLASH_SCALE_RESULT_20261008_ZH.md).

## Scope and acceptance boundary

Read HANDOFF, Failures/README, AN010 and the paired weapon-binding plan/result;
retain the AN001/AN008/AN009 stopped routes. The plan's smaller-flash addendum
sets one new identity, an early actual-scale/origin/direction check, one pulse
per rifle and a stop for human review. Quarter scale is the announced artistic
test choice following the earlier recommendation, not a factor explicitly
specified by the user or an assertion of historical realism.

mount_scale_v3_20261008 reuses the exact private transaction-intake candidate
and compiled native_pulse_v7_20261008. Only each effect instance's local scale
changes from1 to0.25. Measured muzzle centres, named yaw90/pitch0/roll0, original
rifles,01 system, typed rate20, ordinary0.10s Deactivate request,8s completion cap,
camera, diagnostic lights and26-frame budget are unchanged. Purchased defaults,
graphs, materials and accepted character/grip/recoil inputs are not authored.
No second scale, variant, rate or timing trial occurred.

## Actual result

Owned PID32952 exits0, strict log errors0, no timeout. Exactly two activations
and two true native completions occur. Both components remain valid through
complete=true/active=false and are destroyed only afterward.

| Rifle | Observed true completion seconds | Actual relative scale |
| --- | --- | --- |
| M1 Garand | 1.2755776979 | 0.25,0.25,0.25 |
| German FineWoodV15 | 1.2764891014 | 0.25,0.25,0.25 |

All samples retain0cm component-origin error and4.9651e-16 outward-vector error.
The native timer requests0.10s ordinary deactivation; this fixture does not
directly observe callback time. Completion around1.28s includes particle tail
cleanup, not a claim of1.28s continuous firing or inactive-by0.10s.

All26 unedited1600x900 originals were manually inspected: two before frames,
seven early no-flame frames, four clear main-flame frames, six remaining-spark
frames and seven later frames without visible particles. M1 main flame is in05;
German main flame17–19. Main flames fit inside the camera and are visibly
smaller than the unit preview with the same camera. Remaining sparks can reach
or clip its edge. The finite capture budget is retained, not rerun to obtain
more peak images. Request ages, random particle shapes and unequal samples do
not establish an exact pixel ratio or visible lifetime. Front-sight glow/overlap
is not zero-overlap proof; no reverse-view, first-person or world-length claim.
Diagnostic fill still saturates some rifle highlights, not production materials.

Separate visual_review.json authenticates the unchanged native result and all
originals; it records readable compact flame but human_approved=false,
scale_accepted=false and candidate_admitted=false. final_verification.json
records703 guards,68 original delivery files and25 candidate copies exact,
17 Python sources parsed and empty native/integration-launcher inventory.
Twenty-one offline tests pass. No original DLL or formal map/profile/enable row
is installed or changed; no Git commit/push, deletion, SFTP or Catalog operation.

## Stop and review

Show original M1 rifle_0_pulse_05.png and German rifle_1_pulse_19.png from private
Evidence/MuzzleFlashV1/mount_scale_v3_20261008. Stop here for human size review;
do not automatically reduce again or run city tests. Recurring follow-up stays
PAUSED. If this size is accepted, continue the original bounded player/Allied/
German committed-shot/rejection/repeat/reload/death/reset/equipment/world and
first-person visibility gates before any narrow local installation.
