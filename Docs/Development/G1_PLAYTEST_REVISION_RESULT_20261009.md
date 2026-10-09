# G1 playtest revision — actual local result

9 October 2026, 01:16 EDT. Chinese review: [paired result](G1_PLAYTEST_REVISION_RESULT_20261009_ZH.md).
Authority: Yupu's actual packaged-playtest feedback. Implementation and successive
bounded changes are recorded in [the plan](G1_PLAYTEST_REVISION_V1_20261008.md).
This supersedes its in-progress snapshots, not the original core or failure records.

## Outcome and protected scope

Private `candidate_v10` passes its final finite input/obstruction and checkpoint
entries, plus observer-disabled ordinary Ready at 1280×720. Actual 1920×1080
Ready/crouch/prone/question/saved images were inspected; the 1280×720 ordinary
image also shows the health, ammo, objective and upper-right map without clipping.
Numeric results and image review are distinct. Human full-motion/contact and
second-machine acceptance remain open. This is a private human-trial revision,
not formal native/Catalog adoption, publication, course completion or a 60FPS pass.

Canonical 758 source-contract files, 703 protected guards and 359 selected native
manifest files remain exact. The frozen V13 user folder and saves are preserved.
The changes live in a private wrapper; the accepted original character meshes,
rigs, materials, finger/grip configuration, clips, FP camera binding and gun/ammo/
damage/reload/journal transactions are retained. Intentional player-class/input,
squad-hold, mission-interaction and HUD changes are not claimed byte-identical AI.

## Cases, changed attempt and admission

Read Failures/README, MI004–MI012, ML022, AN007, original PLAYER_ACTIONS plans/
results, FP formal V21 and V13 route/coordinate/closeout records. MI012 contains
the exact intermediate compile, preparation, terrain, ballistic-occlusion and GPU
negatives. The core mistake was treating input mappings and a bounded mission
proof as integration of the action child and usable human HUD.

This attempt integrates the authenticated retained V6 action child, holds Allies
before their trailing arc exists, uses explicit checkpoint consent, and adds the
designed HUD/static metric map. A separately documented native future-floor check
prevents prone movement entering support that would subsequently reject both
forward and backward. V10 changes only the opt-in test placement from V9; product
code, headers/config and reused cooked dependencies remain V9-exact.

Early checks: exact original/source/native identities; ordinary startup; real
input press/release, posture and resources; actual stationary bodies; legitimate
three deaths; no automatic save; authentic question and saved-state images.
Stop at the first unmet assertion, strict log, ownership/resource mismatch,
unsupported footprint or repeat GPU failure. Each failed entry stopped and its
raw result was retained. No threshold, death or collision gate was relaxed.

## Final actual tests

All three final entries use executable SHA256
`f79f76a31ed8fc8daa041331bc10dc3d156300921ee9a8105828be1be5480db0`.
They exit 0 with zero strict issues and initialized native FP. The finite native
observer uses simulated UE key events/native navigation and real visible shots;
it never sets health, death, resources, pose or player position to manufacture a pass.

| Entry | Actual result | Limits |
|---|---|---|
| `actions_v5` | 67.916 s; walk150/run300/slow65 cm/s, releases, jump/land, crouch/stand, held-Ctrl reload does not restart. Original bridge prone refusal agrees with collision/support probes. Real complete UE path and manual input reach the one measured flat site; posture2/half-height34 cm, crawl36.808 cm, blocked drift0, real backward crawl and release, stand/reload18 rounds conserved, original fire consumes one. | Not arbitrary-terrain prone, low-ceiling stand denial, all visual transitions or full contact acceptance. Shot's friendly-blocked outcome is not a damage pass. |
| `checkpoint_v5` | 110.714 s; nine real hostile-hit shots eliminate all three Germans. Two/one survivors keep checkpoint locked; zero survivors unlock. Original bridge/capture policy governs progress. Enter: Serial0/question/no autosave. Escape/leave/reenter, moving E denied, safe standing E saves once Serial1. Fresh world F9 restores Won/death ledger; F6 returns Ready/three guards/reset circle. Three native worlds each integrate one action player and original bridge policy. | Observer-driven encounter, not natural two-sided squad combat, human or course acceptance. |
| `plain_small_v10` | Observer-disabled ordinary Ready; actual1280×720 image inspected; exit0/strict0. | Ordinary UI startup only; CSV frame count is a finite exit/image trigger, not a new performance or recording result. |

Both input/checkpoint entries observe eight stationary seconds: nearest player/
Allied distance459.619 cm, maximum Allied displacement0. This fixes crowding from
premature negative trailing targets without moving saved spawns. It does not
prove separation after a player deliberately walks back into the squad.

Private read-only audit/result receipts are under
`tmp/g1-playtest-revision-20261008/{actions_v5,checkpoint_v5,plain_small_v10}`.
Input result SHA256 `af09ea6b9f9dad6cdbf98703c9cd040008e777811bd55f2e243842234828a5d5`;
checkpoint result `d9161de18e271390f9a9bfde9615a83a4b959d041b600b4f3e2b1e2359e8e91f`.
Source/guard audits pass separately. The delivery repeats selected native hashes.

## Delivered controls and interaction

Enter begins; WASD walks; held Shift runs; held Alt slow-walks; Space jumps;
Ctrl toggles crouch; Z toggles prone; W/S crawl. Mouse looks/fires; R reloads;
F9 loads and F6 restarts. The conflicting Ctrl+R restart shortcut is removed.
Original restrictions remain: flat supported full-body prone footprint, forward/
backward crawl, and standing-only fire/reload. Dedicated sprint/jump lowering,
posture-specific eye height and full animation/contact presentation remain open.

Three legitimate G1 guard deaths unlock a green180 cm ground ring and map marker.
Entering asks “Save your checkpoint? [E] SAVE [ESC] LATER”. E commits through the
original safe journal only while standing, grounded, still and safe; Escape
declines. Leaving/reentering rearms the question. Won retains living-player move/
look. Save prefix `ParisG1PlaytestV5` and UserDir
`%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestV5` isolate old trial saves.

HUD: muted olive/dark panels, cream labels, health bar/squad bottom-left; loaded
rounds/reserve/capacity pips bottom-right. Reserve “8-round loads + remainder” is
derived from rounds; no individual-magazine inventory was invented. Upper-right
map uses one authenticated1024px texture from1656 ground NavMesh polygons and
live player heading/Allies/objective/checkpoint. Enemy markers require current
100 m/FOV/LOS visibility, cached at5 Hz. Ground scope is G1 XY, +Xright/+Yup,
with a30 m scale; “N” means local grid north, not historical georeferencing.
It is not a complete Paris or multi-elevation map. Minimap SHA256:
`834ddb7514ccce462c88c0b0c9bac11852e6f856117c9dfe256e27c38df0414a`.

Official FPS references and their claim limits are linked in the implementation
plan. Information hierarchy was adapted; commercial HUD artwork was not copied.

## Private handoff and remaining risks

New trial: `tmp/Playtest-G1-20261009/PLAY_G1_REVISION.cmd`. Old
`tmp/Playtest-G1-20261008` remains untouched. Delivery receipt and exact40-file
private SourcePatch are retained in ignored
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/G1PlaytestRevisionV1/delivery_v1`.
Its `FinalQualification/MANIFEST.json` authenticates20 retained final raw logs,
receipts, numeric results and images. All44 Archive files were copy-verified.
Every Archive payload is copied and hash-verified; one explicitly recorded
delivery-only launcher override adds `DisableAllScreenMessages`, matching the
final test HUD entry. Frozen Archive bytes remain unchanged. Do not describe the
modified launcher as byte-identical to Archive. No new ZIP/public asset upload.

The V9 `checkpoint_v4` startup failed before Ready with device-hung/GPU page
fault (4.865 GB usage vs9.285 GB budget); cause remains unverified, not proven
VRAM exhaustion or save failure. Raw private crash evidence is preserved in
MI012. Final V10 entries run after preparation completes using unchanged quality/
RT-off settings and start cleanly; they do not explain or prove repair of V9's
failure. Stop if it recurs; do not reopen stopped recording/backend sweeps.

Human full motion/camera/contact, second-machine, natural two-sided encounter,
60FPS, valid demo video and remaining course gates are still open. Assignment2
is user-confirmed and Assignment3 deadline13October; mentor confirmation remains
separate. No commit/push, formal native save/Catalog selection or asset refinement
in this revision. Inspect actual processes before any later writer; never stop
user-owned previews automatically.
