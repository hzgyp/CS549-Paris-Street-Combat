# Lane C handoff — regression and integration preparation

4 October 2026. Optional user-opened third conversation; not dispatched.
Chinese review: [_ZH](INTEGRATION_TEST_HANDOFF_20261004_ZH.md).

Read AGENTS/HANDOFF, parallel workflow, NPC handoff/draft, Assignment3 acceptance,
AN001/002/003/FP001, player-action failure/continuous-position checks, navigation
fresh_v1–v4 and current combat/reload results. Write an implementation identifying
cases, changed test design, early check, stopping rule and actual tested identity.

Own only Tools/Validation/ParallelGameplayV1/ and Docs/Development/ParallelGameplayV1/;
private evidence under workspace Evidence/ParallelGameplayV1/<unique-id>. Prepare
tests/offline checks in parallel; do not modify production assets, shared harnesses,
configuration, formal map, Catalog/releases or other lanes' files. Import/reuse
existing read-only helper APIs where suitable. Runtime requires the single native
slot released by A/B and hash/dependency validation of exact candidates.

## Work and evidence

1. Inventory selected release vs unselected A/B drafts; compare dependency closure,
   signatures/capability flags and request-generation contracts. Early reject an
   unvalidated or unresolved dependency rather than silently restoring over it.
2. Prepare reload conservation/one commit/duplicate notify/repeated input/pre- and
   post-commit interruption/death/reset/stale events/near-wall/moving tests. RLD-01
   finger, RLD-02 sleeve and RLD-03 finish→hold need actual matched views and normal
   continuous playback; reset/cancel is not natural completion. Old passes cannot
   pass a new candidate. Do not fix models yourself.
3. Prepare AI faction/private sight memory/hidden-position/search timeout/chase
   budget/reservation retention-release/bounded blockage/actual stop/stale callback
   tests; independent vs coordinated destination comparison uses matched load.
4. Cover player+both factions FriendlyFireEnabled on/off, friendly body blocking
   hostile behind, no duplicate damage/ammo, death cancellation, unarmed rejection,
   legal NPC own-origin shots and no firing while prohibited/running/reloading.
5. After coordinated unsaved city merge, run fresh native tests with bridge disabled,
   retain versions/settings/game-time traces and inspect images/errors/normal exit.
   No manufactured pass for unrun paths or warning suppression.

Stop on guarded changes/shared writer/unsupported fixture. Return a compact actual
result with exact Git/draft/release identities, tests Pass/Fail/Not run/Blocked and
evidence, including first failing frame/transition and remaining risks. Do not mark
AI-01/NAV-01/ANI-01/MVP/course complete from subsets. Packaging/FPS/stress/second
machine/public links remain later work; do not claim them or publish automatically.
Coordinator alone merges selects and updates common progress.
