# MI016 — Distance cadence does not establish player foot contact

9 October 2026. The user played recorded-Foley Game0921d755…cdfba5 and reports
substantial improvement, with player step phase mismatch and an inaudible jump;
other issues are minor. This is qualified human feedback, not approval of full
motion, K98, stress/performance or another recording. The user authorizes replacing
the previously protected synthesized report with actual recorded gunfire.

ParisGameplayAV uses accumulated planar distance (walk82/run105/slow55cm) for
player footsteps. These thresholds are independent of the evaluated locomotion
phase, especially starts/blends/rate changes. Changing sample timbre cannot fix
that relation. The helper only reacts to landing; there is no takeoff cue. Earlier
jump motion and land event counters did not prove audible takeoff or timing.

Preserve parent source/audio/playable identities and prior evidence. Read the
paired G1_FOOT_CONTACT_AUDIO_V2_20261009 plan. Read evaluated feet rather than
adding a timer offset; expose the phase evidence. Add actual transition-gated
recorded takeoff Foley, retaining rejected-jump/fall/air/stop protections. Confirm
source recording and rights before replacing successful-shot presentation. Do not
mislabel a K98 reload click or a paid preview as a freely usable live-fire report.
Keep the existing heading-snap issue recorded and screen recording on hold.

The v1 evaluated-height detector also fires twice when a planted walking foot
rolls through two local minima. Its reviewed trajectory figure and raw samples
are retained; merely passing a local-minimum numerical gate would miss this.
Add a per-foot lift/separation rearming latch in a distinct measured candidate.
The first jump template matcher fails amid NPC footfall overlap (full correlation
.364, land .782, M1 .999999). Preserve the matcher failure and full diagnostic;
do not present it as silence or acoustic acceptance. Use an explicitly audit-only
player isolation for independent output evidence, keeping normal NPC playback.
Guard intake also fails on a Python module-name collision before any protected
write, and plotv1 lacks matplotlib. Preserve scripts; explicit module loading and
local-only plotting dependencies correct these diagnostics without game changes.

Measured verifierv2's absolute future-minimum test fails4.940552cm at41.389755s.
The raw actual walking minimum16.118528 is9.902ms before the emitted16.166165;
20ms after the event speed drops150->63.939 and both feet lower into a different
slow blend baseline. Keep that failed verifier. Associate the same raw trace by
the event's speed regime, retaining the numerical bounds and descent requirement.
No Game edit/rerun or full transition/physical contact acceptance follows.

Further regime filtering fails at descent/short-window boundaries, preserved in
verify_v3/verify_v4. Final diagnosis keeps the unchanged3cm/descent gate for20
stable contacts and reports9 mixed contacts UNASSESSED, not passed. The same
53ab36d9 run supplies full isolated M1/jump/land/insertion matches>.99993 and
original conserved ammo/legacy quiet terminal restore. Manual transitions/acoustics
and recording remain pending. This scoped result does not erase earlier failures.
