# German NPC V11 → formal native baseline (V14 integration)

6 October 2026. Owner: Yupu / coordinating lane A. Status: implementation planned;
results, not this plan, establish completion. Completed adoption is recorded in
[V14 result](GERMAN_NPC_FORMAL_V14_RESULT_20261006.md); retain this planning snapshot.

## Authority and scope

Yupu rejects the V13 Allied-grasp experiment, returns to the previously refined
German V11, and explicitly requests formal German NPC adoption **with its gun**
and private publication. Adopt V11 as an MVP visual baseline; do not refine
fingers/gun again. This is NOT a declaration that Assignment 3 or the whole MVP
has passed. No Git commit/push, asset deletion or AI selection is requested.

Source: private `Evidence/GermanNPCLowerGripV11/source_frame_v4/result.json`,
its retained full-geometry review, unchanged German translation skeleton/mesh,
and the existing native FineWoodV15 rifle / AttachmentV2. Do not consume V12/V13
poses or replace the animated character with a frozen diagnostic mesh.

## Cases read / changed mechanism

- `Failures/README.md`, AN008 native Allied analysis and GP010 gun-native
  analysis; V11/V12/V13 result records and current Allied formal V18 result.
- V13's visually poor whole-Allied parameter copy is retired. This attempt
  uses **German V11's own locals and gun-hand relation**, not Allied offsets.
- AN008 fixed additive deltas failed on a different Ready phase. Reuse the
  verified absolute accepted-holding native node, with a separate German
  AnimBP/DataAsset. Original animation input and action release remain native.
- GP010 CDO collision was misleading. Use AttachmentV2 and check actual spawned
  gun components are NoCollision; register WeaponAppearance/GripMesh/Combatant
  without modifying ammo, health, source packages or action transaction code.
- Old snapshots remain historical. Explicitly checkpoint the verified 618-row
  Allied formal epoch before changes. Preserve authorized B code/dependencies.

## Packages, storage and preservation

New packages under `/Game/ParisCombat/Animation/GermanGripV14/`:
`ABP_PC_GermanGripPostV11` and `DA_PC_GermanGripV11`.
New native map-level `ParisGermanGripPolicy` covers the three present standard
German NPCs and later matching spawns (TeamId1, not players). Existing equipment
is never silently replaced. Source mesh/rig/weights/materials/clips remain exact.

The generic adapter gets only an explicit TeamId check from its JSON (old
Allied configs default to 0). Existing Allied policy/node algorithm/config
remain unchanged. Rebuild the generic plugin, preserve old binaries privately;
test both faction policies and approved first-person after rebuilding.

Ready reproduces V11 arm/clavicle and hand local rotations (42 explicit bones),
with all translations/scales, original bone lengths and remaining source pose
preserved. Non-Ready releases to existing input; no new motion or source clip.
The rifle follows evaluated hand_r natively, including movement/reload.

Only one physical formal map save is authorized, retaining the existing FP and
Allied policies. Descriptor is already enabled and remains byte-exact. Assets
live in the existing one physical SFTP workspace; Git stores generic source,
documents and hashes. Publish a new immutable native-playtest version with
full dependency closure, only changed objects transferred, authenticated SFTP
readback and shared CRUD; then select matching local manifest/Catalog through
reviewed patches. Existing history/dependencies/failure evidence stay intact.

## Execution and early acceptance

1. Inspect Git/local asset guards/process ownership; checkpoint map/config,
   descriptor and matching binaries before native changes. Lane A takes a new
   serialized native slot only after no engine is running.
2. Derive German locals and gun relation from V11; prepare separate config,
   add native policy and minimal team check, build. No parameter fitting.
3. Early unsaved-map entry: create/save only new graph/data, instantiate policy;
   require three German adapters, real V2 guns, correct mesh/TeamId1, exact
   accepted Ready locals (<0.01 degree), gun-hand errors <0.01cm/degree,
   protected input error <0.0001. Inspect real native views before map save.
   Verify current Allies and accepted FP still initialize without errors.
4. Bounded compatibility check: native walk and one original conserved reload
   with Ready return and attachment; this does not certify full visual motion,
   continuous blending, recoil, death interruption, near-wall or FPS. Test later
   compatible spawn and owned adapter/rifle destruction cleanup.
5. Save policy only after early pass; fresh-load saved map, audit hard/soft
   dependency closure in that same fresh process (separate audit receipt), and
   ordinary `-game` with Python/bridge disabled. No duplicate city load is needed
   merely to query its already fresh-loaded dependency registry.
6. Close owned engines; verify preserved guards except explicit map/plugin
   binary changes. Publish/verify immutable SFTP closure, update Catalog and
   establish a new guard epoch. Update asset usage, AGENTS/HANDOFF/team guide.

## Stop / recovery

Stop on a foreign engine/writer, unexpected guard/package/config change,
wrong source/team/gun, invalid evaluated pose, collision enabled, failed native
binding or broken original transaction. Preserve failed receipts and unique
outputs; do not repeat old AN008 full-city proof, tune offsets/fingers/blend,
weaken protection or overwrite a newer map. If an interface-only capability
problem occurs, preserve it and document a bounded correction before proceeding.
Do not select/publish a runtime-broken candidate. Existing V11 straight index,
small stock overlap/self-contact and imperfect grasp are explicitly deferred
visual backlog under this user's MVP baseline decision, not zero-contact passes.

No packaged build, second-machine, full mission/stress/FPS, annotated video or
course readiness is established by this adoption. Git publication remains
pending a separate commit/push request.

## Bounded startup correction (ordinary-game v1)

The first ordinary-game PID42060 remains at `Waiting for ZenServer` before map
loading, while its spawned Zen service responds HTTP200 on local ready-health.
Installed UE source `Developer/Zen/Private/ZenServerInterface.cpp:2340–2410`
has an interactive Yes/No wait after20seconds unless unattended. No actual
dialog pixels were inspected, so dialog blocking is an inference, not a proven
asset failure. Preserve the v1 log/abnormal termination receipt. Stop ONLY the
owned startup process after checking its PID/path/start time; no user editor
or cache/source deletion. New `ordinary_game_v2` adds only `-unattended` to the
same Python/bridge-disabled saved-map test. No pose or asset retrial. Require
fresh Ready logs and normal exit0; stop if that bounded startup test fails.
