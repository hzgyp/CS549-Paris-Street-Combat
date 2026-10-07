# German rifle UE integration / action review checkpoint

4 October 2026. Human review reports issues requiring correction; visual/action
acceptance is not passed. Not selected or released. [Implementation](GERMAN_RIFLE_UE_AND_ACTION_REVIEW_V1.md),
[Chinese review](GERMAN_RIFLE_UE_AND_ACTION_RESULT_20261004_ZH.md).

## Latest human feedback — open issues, 4 October

Yupu's physical-play text report, not new scripted reproduction or screenshot
evidence. All four issues remain unimplemented/unretested:

1. REV-01: sprint moves the hands but not the rifle, separating visible hands
   from the gun. Review attachment/display/action ownership; do not rebuild hands.
2. REV-02: prone still points the rifle forward. User proposes back-slung carry
   while prone and no firing. Existing prone fire rejection remains bounded
   functional evidence; back attachment and enter/exit transitions are not built.
3. REV-03: both Allied and German NPC right index fingers do not contact their
   respective triggers. Palm-anchor convergence is insufficient. Inspect actual
   finger/trigger contact without treating feedback as permission for finger/rig
   edits or reusing rejected finger layers.
4. REV-04: no visible firing recoil. Inventory existing recoil/fire motions and
   their bindings before proposing a change; root cause is undiagnosed, not proof
   of missing source animation. No automatic camera/spread/ammo changes.

User reaffirms the German gun model itself is fine; no new geometry/texture work.
The user calls it a "German machine gun"; record the comment against this reviewed
model, without inferring a new machine-gun asset requirement or weapon swap.
Prior numeric tests remain functional evidence, not visual approval. This turn
only records feedback/state: no repair, map save, closing the user's preview,
release, commit or push. Any repair still needs a bounded implementation document
and the existing source/model/finger/camera protections.

## Animation repair policy — user confirmed 4 October

Existing purchased Xianyu finished motions first, then small bounded adaptations;
do not create new motions. Applies to reload, firing/recoil, sprint, prone and
weapon-carry transitions.

1. Read the [Xianyu catalog](../../Assets/XIAN_YU_ASSET_CATALOG_20261003.md),
   [native index](../../Assets/XIAN_YU_NATIVE_ASSET_INDEX_20261003.md) and actual
   clip content, prioritizing the already purchased RifleAnimsetPro, D059 and
   ShooterStarter deliveries where relevant. Names alone do not establish gaps.
2. Compare finished candidates on the same actual target soldier, gun and view;
   source mannequin/empty-hand playback is not target contact/runtime acceptance.
3. Bounded source-derived retargeting, cropping/playback timing, blending and gun
   attachment may adapt the selected motion. Name the source and exact changes,
   preserve vendor originals. Target files exported by retargeting are traced
   adaptations, not permission for new motion creation. Existing protected
   fingers/rig/model/camera/gun-transaction rules remain binding.
4. No from-scratch keyframing, procedural new motions or AI-authored replacement
   actions. If no suitable mature source exists, log the gap and seek the user's
   finished-content/reduced-scope choice; do not create or buy automatically.

Reload changes still require guarded ammo commit/cancel/death/reset regression.
Inspect existing fire/recoil clips and actual trigger bindings; do not bypass the
policy with a newly scripted gun-bob action. No automatic ammo/damage/camera
change. Implementation document, target contact/function tests and human review
precede selection. This clarification records policy only; four issues are open.

## Verified technical slice

- UE5.8.2, ParisEditorBridge disabled. Accepted V15 GLB imported as one static
  mesh, 24,466 triangles, 110.7304058 cm long, 14 materials, 42 native textures.
  Source has 36 embedded images; repeated native normal assets are retained,
  without assuming their cause or equality. BaseColor sRGB; Normal/ORM linear;
  normals use normal compression and textures use group mip settings. This is
  configuration evidence, not warmed shimmer/FPS acceptance.
- Rigid import yaw90 and translation `(1.35631766,27.86479966,-5.45035005)` cm
  align the actual muzzle to existing local `(0,83.23,0)` cm. Measured maximum
  Y83.2300034 cm agrees within 0.5 cm. Grip station is independently calibrated
  at `(0,3.79960053,-3)` cm; original M1 anchor was not borrowed.
- Attachment V2 uses native Blueprint holding/reload wrist nodes, PostUpdateWork
  tick/prerequisites and native BeginPlay collision disable. Three Germans are
  staged once in the unsaved actual city. No AI controller/autofire was added.
- `review_v3` has 29 samples (22 continuous walking samples plus seven view
  snapshots), 87 equipped-actor samples. Actual component collision is NoCollision
  throughout; max right-grip error 0.000001299 cm. Raw strict-scale summary failed
  on one 0.9999997318 sample. `review_validation_v1` independently passes a
  declared 1e-6 scale tolerance, max deviation 2.68221e-7; raw report stays intact.
- Combined `german_combat_v2` passes 16 cases / 66 assertions, ammo and reload
  conservation, exit0; matched error/traceback/ensure/fatal search is clean.
  The unarmed negative fixture temporarily removes WeaponAppearance for its
  single call and restores it in finally. No protected ammo or gameplay graph
  edit. This is not NPC decision/targeting/history acceptance.
- Existing player-action `runtime_v10` evidence is reused only with verified
  unchanged source/native hashes: 29 strict checks / 2,410 observations / 40
  phases. Closed-editor `run_player_actions_preview.ps1 -CheckOnly` passed.
- All 412 protected inputs remain exact, including canonical city
  `2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`, accepted
  blend/GLB, original M1/characters/actions, Input configuration and Catalog.

## Storage / dependency boundary

59 candidate native files / 79,944,882 bytes: import58 plus attachmentV2. Failed
V1 is separately retained (233,491 bytes), never overwritten. Diagnostic metadata:
`Assets/Integration/GERMAN_RIFLE_UE_DRAFT_INVENTORY_20261004.json`.
Physical storage is only the existing writable SFTP gameplay workspace Content;
the active Unreal Content junction aliases those same bytes. No new model copy.
Exact-file named shared-account Modify grants were verified for all60 files;
root ACL and unrelated assets were untouched. This is not authenticated remote
download/CRUD verification of a new immutable release.

New namespace: `/Game/ParisCombat/Weapons/GermanRifleUEV1/`, explicitly Git-ignored
through the junction. Engine material dependency is InterchangeAssets glTF
`MI_Default_Opaque_DS`; preserve that installed-engine dependency. Accepted source
model release is unchanged. New native drafts are not Catalog/teammate-restore
authority and are not yet in the selected native-playtest release.

## Actual images / known limitations

Seven `review_v3` viewport PNGs were opened and inspected. Idle/front/contact show
recognizable rifle form, dark wood and material coverage on the German soldier;
generic hand shape/contact still require human approval. Walk-side is standing
after movement, not a walking-phase image. Early/mid reload rendered poses appear
repeated despite differing bone snapshots; late/recovery views have foreground
occlusion and recovery's left-palm station differs markedly from idle. Do not
claim phase-matched reload contact/recovery passes. Generic reload/open hands
remain an explicit separate next-package problem; no finger/IK patch or further
offset sweep is performed. Numeric convergence is not geometry approval.

V15 remains a modern-donor fictionalized static derivative, not certified Kar98k;
no operating bolt/clip mechanism, weapon-specific animation, historical loadout,
ADS/VFX/full navigation/AI/mission/performance/package/course pass follows.

## Preserved failures / bounded stop

Read FP001/GP009 before implementation and record GP010's native collision case.
Retain aborted import_v1, unavailable-API import_v2, label fixture review_v1,
V1 collision and protected-ammo fixture review_v2, strict-scale review_v3, and
combat_v1's three false unarmed assertions. Combat_v1 actually used an armed
actor and consumed a round; it is not a passed regression. One separately named
native V2 collision correction and a test-only negative-fixture correction were
made. No original source geometry/rig/fingers/motions/camera/gun transactions were
changed. Skill workflows guided export/native and action checks, not modeling.

Human review is the stopping gate: ordinary German holding plus player movement,
body/contact/eye height. `run_german_rifle_ue.ps1 -Mode preview -Identity <new id>`
stages an unsaved city and unregisters Python at ready; native Blueprints then
control normal play. The user owns that process. Click the viewport; WASD move,
Shift run, Alt slow walk, Space jump, Ctrl crouch, Z prone. Fire/`R` reload only
in ordinary standing/walking; sprint/air/crouch/prone reject them. Prone is only
forward/back on supported low-gradient ground, without yaw/lateral input. F8
ejects for body inspection; Esc ends PIE. Do not save the temporary staged map.

No formal selection, SFTP object/release publication, Git commit/push or further
reload/AI implementation. Discarding unsaved staging keeps the canonical map and
previous release, without overwriting unique drafts.

Three additional combined-combat images (initial HUD, reload-complete HUD and
near-wall blocker) were actually inspected: M1/arms/HUD and equipped Germans are
visible. They are game views within editor UI, not the seven frozen NPC closeups,
and do not establish phase-matched reload movement or user action approval.

Human preview actually opened: PID4324, identity
`human_german_actions_20261004_143353_700`, ready at14:35 local. Ready record has no
errors, protected hashes exact, camera(25,0,60)/FOV90, three equipped Germans and
`startup_callback_unregistered:true`. Startup log has no matched errors. The
window is user-owned; check its actual process before launching any writer.
Git storage metadata check covers17,495 selected records; diff whitespace, Python
AST/inventory and launcher PowerShell syntax checks pass. Not a full remote
rehash or native release publication. This is the historical startup snapshot;
the four later human issues above supersede its pending-feedback wording.
