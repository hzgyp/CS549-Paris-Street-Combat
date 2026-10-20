# Shared tutorial and action source workflow

16 October 2026. Human instruction in 地图探索与玩法设计: both this chat and 优化人物动作与建模（轻量接续） must continue from the latest combined source, reconcile both sets of changes before packaging, and build only when the human requests a playtest/build. This is a coordination rule; it requests no new Game or feature work.

## Shared entry and ownership

1. Read HANDOFF_CURRENT.md and Docs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json before implementation. Verify the selected source manifest. That selector is the shared combined source entry; its status distinguishes built sources from unbuilt changes. A working directory, historical tutorial alias, source count or mutable compiler cache alone is insufficient to identify the current base.
2. Continue each work package in a named writable source workspace based on the latest combined source. Preserve immutable built snapshots, the other chat's workspace and all unfinished local edits. When the combined source advances during work, compare the original base, local edits and new combined source before carrying the local edits forward. Never replace a newer file with an older whole-file copy.
3. Use one writer for each actual mutable file/native byte set. Changes to a common file require an explicit handoff or sequential integration. Independent workspaces can proceed concurrently; shared binary/Content aliases still require existing ownership checks.
4. Record the base source/manifest identity, changed files, relevant functions/behavior, final file hashes and actual verification limits in each work package. Publish a pending-source pointer update only after reading its current value again and reconciling intervening changes. Retain previous pointer/source/receipt identities. An unbuilt source integration does not promote a playable or establish runtime acceptance.

## Before any requested build

1. Confirm a current human request covers this build/playtest package. A completed older request does not authorize another package; ordinary intermediate fixes remain source/config/docs/static work.
2. Check both chats' latest change records and unfinished-source status. Human-authorized messages between these two chats are limited to source base, file ownership, changed behavior, integration and build readiness. Preserve each chat's existing authorized task; coordination adds no unrelated feature, cleanup, adoption or publication authority.
3. Reconcile both change lists against the shared combined source. For common files, inspect the base/local/other differences and retain both intended behaviors. Resolve overlaps before building. If a relevant edit is still being written, wait for its source handoff and recheck the manifest; do not freeze a half-written source tree.
4. Record a pre-build reconciliation receipt identifying both input revisions, included changes, conflicts/resolutions, the final combined source manifest/hash and the exact human build request. Re-read the shared pointer immediately before freezing the build source. Keep all known pending fixes accounted for.
5. Build from that frozen combined source and record the resulting Game identity. Run checks appropriate to both changed scopes and report unverified branches honestly. Preserve actual earned saves and existing normal entries according to the project rules. Playable routing moves only to a verified matching source/Game; formal adoption stays separate.

## Initial status and scope

At this rule's creation the combined selector identifies G1ObserverStowHUD20261016, 118 files, Game 83c7a53f37f1defe993df95c1b77c31a97198aea161dbecdf090b016c6240339. Read the selector again for future work. It already retains the tutorial recruitment/popup changes. The action chat's ongoing smoke-grip correction must retain those changes and record its subsequent unbuilt source handoff. The present rule does not assert that correction is complete or included in the existing Game.

Only project instructions and continuity records are changed for this request. No build, engine entry, runtime/source promotion, native edit, save write, cleanup or external publication is part of adopting this workflow.
