# Formal map NPC combat integration

7 October 2026. Yupu explicitly permits the tested NPC AI to enter the formal
Paris map and receive fresh-process play regression. This permits local map
and new AI package saves only. Commit, push, SFTP release, Catalog updates,
asset removal, grip refinement and mission expansion remain outside this work.

## Cases read and changed mechanism

Read HANDOFF, the current NPC combat results, Failures/README, NI001, GP010 and
AN008. NI001 requires actual weapon collision and original reload identities;
GP010 requires runtime instance checks rather than CDO claims. AN008's stopped
grip and full-motion experiments remain stopped. Functional AI tests do not
certify visual contact, recoil or complete motion.

CombatV2 currently needs one-time test setup to enable its accepted equipment
and combat. A new native Behavior Tree bootstrap service will wait for the
selected faction's original rifle, its correct combatant/mesh references and
the selected evaluated postprocess class with valid protected input. It will
then call the existing equipment and combat configuration once. A ten-game-
second deadline fails closed; no Python behavior or pose loop is introduced.
The existing native combat, search and reservation services remain unchanged.

Replace the five saved NPCs with compatible sensing/CombatV2 derivatives,
retaining labels, faction, transforms, original source mesh, animations and
existing rifle actors. Rewire only the replaced bodies' rifle references.
Keep the original player, both selected grip policies, city and navigation.
Use one squad coordinator and one friendly-fire policy, default OFF. Allies
follow/regroup; Germans initially guard and use the existing bounded search.
New patrol routes or objectives are not inferred from this integration.

## Early acceptance and sequence

1. Verify current 698 protection rows and sole UE ownership. Author separately
   named bootstrap assets; compile and retain an actual saved-map roster survey.
2. Fresh unsaved city test: all five compatible bodies initialize without
   Python configuration; individual controllers/Blackboards, both selected
   native grip configs and effective rifle collision must be correct. Exercise
   a finite encounter without Python combat requests before a formal map save.
3. Back up the exact single current map privately. Save only the formal map
   after verifying replacement roster and original presentation references.
   Record its two junction aliases as ONE authorized physical mutation. Preserve
   the immutable A snapshot and old B receipts; advance guards through an
   explicit before/after ledger, never silent rebaselining.
4. Fresh-load the saved map, observe native startup and finite play behavior.
   Run ordinary saved-map -game with Python and editor bridge disabled. Check
   original player/gear, five native controllers, FF OFF and unchanged other
   protected bytes. Background/offscreen cadence is not target FPS acceptance.

Saved global policies also require the older transaction/autonomous fixtures
to reuse the map's one FF policy/coordinator rather than adding duplicates.
Cache the class before PIE, as NI001 requires. Repeat the current-equipment
three-shooter OFF/ON transaction matrix after formal startup regression; its
AI-disabled fixture is not evidence that the new formal startup is disabled.

## Stopping conditions and storage

Stop for another writer, unexplained protection mismatch, incompatible selected
equipment, non-AI asset mutation, or missing authority. Diagnose scoped graph,
API and fixture mistakes with new identities and preserved failed receipts.
Do not loosen numeric gates or repair grips to make combat pass. If an owned
map save fails validation, preserve its bytes and restore only this attempt's
exact backed-up map under the same exclusive slot before further work.

New packages stay in /Game/ParisCombat/AI/NPCInteractionV1. Private evidence and
the single-map recovery copy stay in the existing workspace's
Evidence/NPCInteractionV1. A locally integrated map is not a new immutable SFTP
release: do not restore the older Catalog-selected map over this authorized
local increment, and do not publish a manifest for missing remote AI packages.

Full route/objectives, checkpoint/restart, foreground/stress performance,
complete visual actions, Shipping and second-machine acceptance remain separate.
