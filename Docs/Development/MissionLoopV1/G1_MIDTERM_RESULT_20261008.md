# G1 midterm mission development — 8 October 2026

English source; synchronized Chinese: `G1_MIDTERM_RESULT_20261008_ZH.md`.
Implementation was documented before development in
`G1_MIDTERM_IMPLEMENTATION_20261008.md`; separate bounded bridge/staging plans
record the two subsequent mechanism changes. Status: local G1 functional version
implemented; nine scoped native-entry audits pass, including current-map travel,
save/load, lifecycle, outcomes, encounter and ordinary-game admission. This is
not whole-Assignment3 acceptance.

## Delivered local implementation

The isolated runtime `ParisBridgeMissionV1` and saved map
`/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1` implement **Ready → cross C →
reach T1 → clear the three registered G1 defenders → living-player occupation →
Won**, with player-death Lost, missing-actor Error, full restart and local saves.
There are exactly one player, two Allies and three Germans; phase advancement
does not heal, refill, revive or replace them. Private Blackboards initialize
before the retained original behavior trees are released once by Start.

Native HUD/input: Enter starts, F5 requests a safe save, F9 loads, Ctrl+R fully
restarts; R remains original reload. Test slots have distinct prefixes; human
play uses `ParisG1V2`, unaffected by test checkpoints. Invoke
`Tools/Integration/G1MissionV1/play.ps1` explicitly for the visible local game,
or add `-LoadSave`. This entry needs the installed UE5.8 and local private assets;
it is not a packaged redistributable build.

## Current map and two corrections

The original S is traversable but sits inside the visible residence proxy's
bounds. All four cardinal screenshots were reviewed; the dark initial view is
an unsuitable rendered staging site, not a lighting or FP-grip diagnosis.
ML022 excludes that spawn while retaining its actual movement evidence. An
unsaved ten-second/four-view test admits exact25cm white near-bank centres:
player[1912.5,-20662.5,113.762134], Ally1[1762.5,-21112.5,110.377514],
Ally2[1487.5,-20837.5,96.834814]cm, yaw0. Their subsequent owned-map save leaves
the defenders, city, agent, collision and310tiles/1656polygons unchanged.

The original lateral squad formation genuinely fails crossing: after the player
arrives, both Allies remain2437.88/3022.50cm from goals and report SquadFailed at
the unchanged25-second limit. The mission-only controller instead uses one
shared **UE-native navigation centreline**, trailing the leader450/700cm through
C. Original reservation/MoveTo/RVO/capsule/speed300cm/s and55cm/25second arrival
gates remain. Combat/other locations delegate to the original policy. There is
no custom A*, actor-position driver or original AI asset edit.

Current saved-map TravelV4 physically crosses with the original player and both
Allies. The bridge leg is4708.27cm; the Allies finish31.15/49.93cm from HeldGoals,
SquadFailed=false, both beyondX5600, past C's footprint. Defenders were isolated
only for this navigation fixture. This does not establish natural combat victory.

The updated black/white figure preserves raw survey bytes, marks the rejected old
S and the current assembly/C/T1/G1, and overlays the actual TravelV4 trajectory:
private `Evidence/G1MissionV1/staging_layout_v2_20261008/G1_MVP_LAYOUT_20261008.png`.
White remains a measured planning candidate, not automatic spawn eligibility.
The figure uses the existing L0 local-surface filter, not a semantic floor map;
all six selected centres retain their measured source-node XYZ. It does not
establish whole-city multi-floor connectivity or all black cells as physical walls.

## Save contract and evidence

Two alternating SaveGame slots contain checksummed payloads with schema,
map/config, serial, six ordered stable IDs/classes, transforms, health/death,
loaded/reserve/shot count, phase and control rotation. Ammo conservation is
validated. The inactive write is read back; newest invalid slots can fall back
to an older compatible snapshot. Validation precedes world travel; rejected
snapshots never partially mutate the live run. Restore uses a new world and
original lifecycle/death endpoints, verifies all restored state before releasing
behavior, and does not resume half reloads or old-world timers.

Safe saves require grounded still living bodies and completed actions, no active
NPC combat transaction, and no hostile LOS in active play. Ready/Won are eligible;
Lost/Error are not. FunctionalV3 correctly refuses the new near-bank active save
for hostile LOS, leaving serial1 intact. The separate documented V4 save unit
fixture freezes original AI/sensing/movement and places the Allied group once at
the measured old approach, then exercises the original shot/damage endpoints.
That isolated use does not readmit the old enclosed site as a production spawn.

| Entry | Actual scope/result |
| --- | --- |
| ready_v2, load_v1 | Prior staging: ten-second passive admission/Start and separate-process persisted serial2 restore pass; isolated newest-corrupt fallback and checksum/schema/duplicate-ID/created-ammo rejection pass. |
| spawn_view_v1, staging_author_v2 | Current staging: six original ready bodies/bindings/resources and reviewed four views pass; owned map saved with exact nav/defenders/703 and older valid controls. |
| travel_v3, travel_v4 | Shared native bridge policy passes actual player/two-Allies travel from old approach and current saved near-bank start respectively. |
| functional_v4, load_v2 | Current-map serial2 passes: player75HP/1+16ammo/1shot, Ally2/German1 dead. New-process exact restore, corrupt-newest fallback, checksum/schema/duplicate-ID/created-ammo rejection and old-staging fingerprint rejection pass; valid controls unchanged. Exit0/log0/703/runtime inputs exact. |
| lifecycle_v1 | Living required-actor removal enters Error without counted kill/save; fresh restart restores exactly six original actors/five bindings. Saving during original reload is rejected, good revision retained. Load Ready during that reload establishes a new generation; four-second wait retains2+16/0shots/Ready, no late old ammo commit. Start remains once-only. Exit0/log0/703/runtime inputs exact. |
| outcomes_v2 | Explicit unit fixture passes early-kill retention, out-of-order G1 rejection until T1, three-member clearance, ally casualty permitted, same-update player death over occupation, Lost save rejection, fresh restart/default roster/resources/five bindings, living occupation Won and saved Won result. Deliberate original damage/one-time placements are not natural victory or traversal proof. Exit0/log0/703/runtime inputs exact. |
| encounter_v2 | Independent unsaved T1 group passes native two-sided shots/damage: Allies9/Germans5 shots; all three Germans dead, Ally2 dead, Ally1 at30HP, player100HP/0shots. Original actions/tree, no scripted damage/aim/pose driver. This single encounter is not a balance or full approach/playthrough acceptance. Exit0/log0/703/runtime inputs exact. |
| plain_v1 | Ordinary saved `-game -DisablePython` reaches native Ready and exits0; no interpreter usage, bridge absent, strict log0/703/runtime inputs exact. Initial audit's wrong log wording stays failed; separate `audit_python_log_v2.json` checks the installed UE source's explicit disabled message against the identical authenticated log/exit. No native rerun or criteria relaxation. |

Completed native audits require normal exit0, zero strict Error/Fatal/ensure,
raw receipt gates,703 exact protected rows and unchanged runtime-source/DLL
manifest. Earlier failed author/Ready/functional/travel entries stay failed.
MI001 and ML022 retain analyses and authenticated private reference manifests.
Private `Evidence/G1MissionV1/closure_v1_20261008/result.json` authenticates all
nine selected audits, current config/owned packages/runtime manifest/figure,
unchanged older valid controls and both failure manifests. All G1-owned engines
closed normally; verify actual other/user ownership before another native entry.

## Ownership and limits

Current fingerprint: `G1V2_20261008_nearbank703_roster6_v1`. Authoritative owned
admission: private `staging_author_v2_20261008/result.json` and its independent
audit. New map1504660bytes SHA256
`7f5410b71475db328c3cef2d265e8bc0a8b2f41a12b63e1fa6decb9904e759bb`;
controller55753bytes SHA256
`9c9ffd8a589eddedf861854e36db7a1071934a2eb596e8c5e79762aaa092a5dd`.
Do not revert to historical owned-map hashes or modify the original formal map.

Original models/fingers/rig/weights/materials/actions, accepted FP/Allied/German
presentation, collision, fire/reload/damage and Catalog remain protected. Native
packages/binaries/screenshots/raw commercial bytes stay private. Current new
mission packages are local and are not in the selected shared Catalog. No commit,
push or publication is performed in this increment; unrelated NPC/MuzzleFlash
changes are preserved. Inspect actual native process ownership before any entry.

A complete unassisted human playthrough/balance review, measured1080p/60FPS and
stress tests, Shipping packaging, second-machine access, annotated2–3minute video,
progress PDF/source/build links and course-prerequisite evidence remain separate
Assignment3 gates. Local functional proofs do not establish whole-MVP/course
completion or remove any of the four required pillars.

## Subsequent source publication checkpoint

On8October the user explicitly requests Git commit/push after the local result.
This revision carries the G1 runtime source, finite authoring/test tools, bilingual
plans/results, failure analyses/hash references and G1-only shared-document
additions. Other-lane work is excluded. Earlier "no commit/push" statements record
the completed development turn; this request supersedes that source restriction.
Native mission packages, screenshots, DLLs, credentials and private raw evidence
remain outside Git; the selected asset Catalog is unchanged. This source
checkpoint is not a new asset release, standalone teammate restoration, or
whole-MVP acceptance. Verify remote main before claiming push success.
