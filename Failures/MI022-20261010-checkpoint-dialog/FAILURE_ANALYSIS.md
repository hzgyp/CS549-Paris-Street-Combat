# MI022 — Checkpoint dialog build failure

10 October 2026. Independent candidate_v1 fails compilation with C4456:
the new HUD modal's local `Detail` shadows the existing mission HUD `Detail`.
The project's warning/error policy rejects this before a new Game can run.
This is a source naming failure, not a save-file or asset failure.

Preserve `tmp/g1-checkpoint-dialog-20261010/candidate_v1/Project`, its exact
52-source prepare.json, build.json and build.log. No native tests or user saves
were changed by this build. Next candidate_v2 changes only the dialog local name
to `DialogDetailText`; no safety checks, durable transaction, UI states, reflected
declarations, models, grips, fixed NPC sites or test pass gates change.
Recheck the exact protected blocks and build under a distinct identity.
See [implementation](../../Docs/Development/G1_CHECKPOINT_DIALOG_IMPLEMENTATION_20261010_ZH.md).

candidate_v2 builds successfully, Game e11d4819cd77252bc6dd85e6ab97de2293893cc961ca4fb58db177f73c6b541b.
Its independent menu_v1 (37 checks) and checkpoint_v1 (54 checks) both exit0/pass,
including real readonly failure, retry, saved modal/hidden prompt and F9/F6.
These successful receipts remain, not failure evidence. The subsequent v3 only
improves player-facing HUD copy (no internal journal number/slot terminology) and
adds explicit pending-request leave coverage to the opt-in probe; the transaction,
interaction state and gameplay inputs are identical. v3 requires its own Game
and dated results; do not relabel v2 results as v3 runs.

v3 menu_v2 (37 checks) and checkpoint_v2 (56 checks) both pass/exit0,
including explicit pending-request leave cancellation. Its first separate
restore_v1 process exits3 before Ready, reporting D3D12 device removal/GPU crash;
no fresh-process restore result exists. Preserve launch.json and game.log under
checks/restore_v1 and the shared diagnostic UserDir crash records; this is not a failed save validation
or evidence of an asset/reflection fault. The historical MI014 also preserves
an intermittent pre-Ready GPU crash. No root cause is established. A bounded
one-time distinct restore_v2 entry with identical Game/settings and the same
isolated verified checkpoint is permitted by the new plan addendum; a second
occurrence stops this verification route. Never relabel restore_v1 as success
or alter RHI/model/save/runtime settings to manufacture acceptance.

The retained restore_v1 diagnostic is DXGI_ERROR_DEVICE_HUNG at frame2;
local GPU use4394.25MB versus9285MB budget, and DRED reports no PageFault data.
Do not claim VRAM exhaustion or the exact historical MI014 MMU cause.
Because restore uses the checkpoint_v2 test UserDir, its crash artifacts live
under `checks/checkpoint_v2/User/Saved/Logs` and `Saved/Crashes`, while its
distinct abslog/launch receipt are under `checks/restore_v1`.

The one permitted unchanged-settings restore_v2 then passes31 checks/exit0;
its real restored serial3 roster matches the new journal and terminal corpses
remain stopped. Current v3 menu37/checkpoint56/fresh-restore31 receipts and final
1754-native/source/Game/user-file/reflection/transaction protection pass are in
`tmp/g1-checkpoint-dialog-20261010/verification.json`. The first crash is still
retained, and the recovered entry does not establish startup stability or its
root cause. No further same-cause retries are authorized by this addendum.
