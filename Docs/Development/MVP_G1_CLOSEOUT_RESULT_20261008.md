# G1 MVP closeout: tested private candidate, open release gates

8 October 2026, EDT. [Chinese review and test guide](MVP_G1_CLOSEOUT_RESULT_20261008_ZH.md).
User confirms Assignment 2 and the Assignment 3 deadline of 13 October 2026.
Mentor confirmation was not separately supplied. This is a progress/handoff result,
not whole-MVP acceptance or a submission-ready declaration.

## What changed and what remains protected

Cases read: Failures/README, MI001-MI011, ML010/ML022; the closeout, native-route,
agent-coordinate, stress and three subsequent capture plans. Earlier failure
records remain authoritative for their particular entries; later bounded passes
do not rewrite them. The current candidate is instrument_v13, outside the canonical
project. It is not selected by the team Catalog or committed to public main.

The candidate corrects a single physically witnessed bridge navigation polygon,
removes the retired S prefix from the squad centreline, uses native agent feet for
one G1 planning preflight, and settles the trailing Allies on the existing far-bank
lane after the player naturally stops. Original 250 cm member spacing is retained.
The existing tree is duplicated at runtime with exactly one planning-task replacement;
other task/service/decorator classes, original blackboard and per-controller state
remain. The original 55 cm / 25 s arrival and body-X >= 5600 gates remain.
Checkpoint configuration is isolated as BridgeConstraintV2FeetPlan / V4.

No character model, source rig, skin weight, material, accepted finger/grip pose,
original animation, rifle transaction, damage/ammo rule, physical geometry, capsule
or movement speed was modified. This is a navigation implementation change, not
an assertion that every AI byte in the private wrapper is unchanged. The canonical
758-source contract, 359 selected native files and 703 protected rows remain exact.

Early admission was exact source/assets/guards, ordinary Ready/image, exact bridge
witness and one-task topology before movement. The plans stop at the first
original squad/resource/checkpoint/topology/hash error; no wider tolerances or
automatic offset/polygon search. Recording and performance stop conditions below
have been reached. Do not restart those stopped trials under this plan.

## Actual packaged results

| Entry | Observed result | Limit |
|---|---|---|
| candidate_agent_v1 / V13 | Three two-Allied crossings/regroups, G1 captures, Won saves and fresh-world loads; two full restarts; three newer old-configuration saves with correct MD5 rejected with good fallback and unchanged live state. 289.365 s, exit 0, strict errors 0, actual 1920 x 1080. | Scripted player input, not an unassisted human playthrough. |
| Same entry, regroup | 12.295 / 11.615 / 11.876 s, all original 55 cm / 25 s / far-bank body gates met. Native single-polygon policy and one-task binding checked in all six worlds; observer excludes zero polygons. | No full-map or all possible blocking guarantee. |
| agent_plain_v1 | Ordinary Ready startup with automation inactive; actual game image inspected, exit 0 / strict 0. | Startup, not a human full mission. |
| plain_recovery_v1 | Same V13 ordinary startup passes after V15 capture-variant GPU failure; game image inspected, exit 0 / strict 0. | Does not prove the cause of the V15 device hang. |
| stress_6_v1 | One separate original squad/capture/save/fresh-load cycle passes; 89.663 s, exit 0 / strict 0. | Initial six actors, normal guard deaths; not sustained six-active capacity. |

The scripted player finishes each Won round at health 100, ammo 2/0, 16 shots;
both Allies remain health 100, ammo 2/16, zero shots; three guards are dead with
zero shots. The driver aims only at visible targets but removes the guards early.
This result therefore does **not** establish a natural two-sided encounter in the
combined packaged mission. Earlier isolated faction-fire fixtures are separate
evidence and cannot fill this gap.

## Performance and stress stop

i9-12900F / RTX 3080 10 GB / 32 GB, Windows Development, High (ten quality groups
at 2), actual 1080p / 100%, hardware ray tracing off, 1536 MiB texture pool,
VSync off and uncapped. Twenty-second warmup; no recording; complete native CSVs,
no trimmed frames. Offscreen Development instrumentation is disclosed.

| Run | Frames / seconds | Mean ms | p95 ms | Maximum ms | FPS |
|---|---:|---:|---:|---:|---:|
| 1 | 1602 / 30.808032 | 19.230981 | 27.4845 | 75.0535 | 51.999427 |
| 2 | 1551 / 30.078239 | 19.392804 | 26.0789 | 63.4330 | 51.565519 |
| 3 | 1554 / 30.346688 | 19.528113 | 26.6920 | 75.1328 | 51.208224 |

**60 FPS fails.** Round 1 render-thread critical time is 19.176 ms versus game
11.684 / GPU 9.914 ms. This locates an observed limit; it does not prove a specific
material/model/culling cause. The separate six-starting-person stress entry measures
53.395617 FPS, 1631 frames / 30.545578 s, mean 18.728129 ms, p95 25.815 ms and
max 51.2748 ms. The predeclared 6 / 12 / 18 schedule stops at six. Twelve/eighteen,
sustained active capacity and matched independent/coordinated navigation are
unmeasured. A separate bounded optimization plan is required before new trials.

## Private review artifacts

All paths below are under `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/`
`Evidence/MVPCloseoutV1/`. Commercial bytes remain private; no wider distribution
or verified reviewer download/video URL is claimed.

- `delivery_v1/Paris_Street_Combat_G1_Private_Candidate_Win64.zip`: 8,475,354,576 bytes;
  SHA-256 `760dbf44028acae9486c3ff9f5883715d5cf17a1c6fe338f65f20c8caecf9d01`.
  All 41 cooked files were SHA-256 read back from the ZIP; total cooked bytes
  8,456,136,819. Game executable SHA-256
  `965bf17c967d313e67e717fbd24080ab5b6093237dcf927355d387a3c111c4e3`.
- ZIP includes ordinary launcher, English/Chinese instructions, cooked-file manifest,
  exact tested wrapper SourcePatch (no Content), CloseoutTools and Microsoft's
  Visual C++ x64 runtime installer. Other-machine runtime/rebuild is still untested.
  Legacy capture helpers are stopped experiments, not supported recording options.
- `delivery_v1/Evidence/` and `delivery_receipt.json` are **beside** the ZIP, not
  embedded in it. They retain selected functional/plain/stress receipts and their
  hashes. Full raw traces and recovery evidence remain separately private.
- `progress_v1/output/pdf/Paris_Street_Combat_Assignment3_Progress.pdf`: two-page
  English progress report, regenerated from these facts, rendered and both pages
  visually inspected. Build/video reviewer links remain open, so it is not a final
  submission report.
- `final_audit_v1.json`: final read-only source/703 guards, both manifests (16,209
  assets / 29,077,903,470 bytes), whole ZIP, 43 source entries, 11 retained receipts
  and two-page PDF verification **passes at 20:23:49 EDT**. All 14 Python tools
  parse. This is an integrity pass, not whole-MVP acceptance.

Published source remains `b8a3a6a1ba1f730730be23f6fa1d801787d58165` at
[the project GitHub repository](https://github.com/hzgyp/CS549-Paris-Street-Combat).
It does not contain this uncommitted candidate. SourcePatch carries its tested
wrapper configuration and four plugins; restore the entitled matching Content
and use UE 5.8.2 / CL 56702186 to rebuild. Do not copy machine-local junctions.
No canonical native save, Catalog adoption, Git stage/commit/push or publication
was performed by this closeout. No teammate test or message was performed.

## Teammate human verification guide (not yet performed)

1. Fully extract the ZIP into a writable Windows x64 folder. Compare the ZIP hash
   above and preserve any local work. Run `PLAY_G1_CANDIDATE.cmd`; install the
   bundled Visual C++ runtime only if required. The Unreal editor is unnecessary.
   Record machine/GPU/driver, this exact binary, settings and test date.
2. Enter starts; WASD moves; mouse looks; left mouse fires; R reloads; F5 requests
   safe save; F9 loads; Ctrl+R fully restarts; Alt+F4 exits. This candidate uses an
   isolated `%LOCALAPPDATA%/ParisStreetCombat/G1CandidateV4` user directory and
   ParisG1CandidateV4 save prefix. Do not overwrite it with V2/V3 slots.
3. Cross C bridge normally and check **both actual Allied bodies** reach the far
   bank. Record stalls, waiting, visible sliding/collision and time; a complete
   path or SquadFailed=false is insufficient. Do not teleport or relax thresholds.
4. Approach G1 at normal human speed. Give the factions an actual opportunity to
   see/engage each other before eliminating every guard. Record observed sight
   acquisition/loss, fire/damage, support and deaths. If no two-sided encounter
   occurs, mark the case failed/unproved rather than infer it from team IDs.
5. Inspect FP arm/camera visibility, NPC arm continuity, reload, recoil/muzzle and
   near-wall blocking without changing accepted grips/models. In a safe stationary
   location press F5 and wait for HUD confirmation; if denied, retain the denial.
   Record health/ammo/objective/NPC-death state, change state through normal play,
   then F9 and compare. A denied save is not a successful checkpoint.
6. Complete G1, verify Won and checkpoint restore. Ctrl+R must restore initial
   roster/resources/objectives. Repeat through human win/loss/partial-state cases;
   record what was actually tested. These broader lifecycle cases remain open.
7. On the teammate machine repeat startup and core play/save/load. Preserve logs,
   screenshots/video and exact steps for failures; do not change many settings or
   overwrite the failed identity. Stop at missing assets, wrong build, stuck squad,
   bad resources/checkpoint, crash or unacceptable camera/action behavior. New
   fixes need a bounded plan. Return observations; no pass is presumed in this doc.

## Manual video handoff (pending, no automatic retry)

Four automatic routes stopped: MI008 intermittent 50-frame callback; MI009 null
RHI/16 blank frames; MI010 device hang before Ready/zero frames, cause unproved;
MI011 owned-window output shows wallpaper instead of game/HUD. Whole failed
directories were moved into the private failure archive. MANIFEST files preserve
old/new locations and selected hashes; raw receipts keep historical paths. The
valid V13 functional source/build remains available, not discarded as a failure.

A future manual capture must first show 10-15 seconds of the **actual game/HUD**
and be inspected before the mission. Suggested 2-3 minute real-time sequence:
0:00-0:20 explain G1 scope/four pillars; 0:20-1:10 show the bridge and both Allies;
1:10-1:55 show genuine encounter, rifle/reload/collision and capture;
1:55-2:30 show successful save/load and original resources; 2:30-2:50 annotate
the separately measured FPS/stress limit and remaining gates. This is a storyboard,
not evidence these events fit that duration. Rehearse without speedup; adjust the
sequence or transparently label cuts if needed. Use a separately admitted actual
stress capture for any stress demonstration; a metrics slide alone does not pass it.

Stop immediately if capture is blank/wallpaper, HUD unreadable, cadence unstable,
the game crashes or the actual mission fails. Do not invoke stopped V13/V14/V15
capture routes, switch to desktop capture automatically, synthesize missing frames,
or treat movie cadence as game FPS. This plan delivers **no valid MP4**. Natural
combat, human/second-machine regressions, 60 FPS, stress comparison, matching
source selection/publication and final reviewer access remain release gates.
