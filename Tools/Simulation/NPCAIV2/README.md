# NPC AI V2 offline candidate

This directory contains the candidate rule oracle, synthetic navigation adapter, finite fixtures and replay renderer. It never calls UE, changes Content, launches a playable, writes earned saves or transfers files. Current result: [English](../../../Docs/Development/NPCAIV2/RESULT_20261017.md) / [简体中文](../../../Docs/Development/NPCAIV2/RESULT_20261017_ZH.md). Current candidate pointer: `Docs/Development/CURRENT_NPC_AI_CANDIDATE.json`.

From the project root (Python 3, standard library only):

```powershell
python Tools/Simulation/NPCAIV2/simulate.py --out tmp/npc-ai-v2-20261017/your-new-identity
python Tools/Simulation/NPCAIV2/verify.py --out tmp/npc-ai-v2-20261017/your-new-identity
```

Open that output's `replay.html` directly. Choose a scene and NPC, play or scrub, inspect target/cover scores and state/move reasons. Playback ends at the finite deadline. The truth toggle is viewer-only: hidden positions are never inputs to candidate decision functions.

- `policy.py` / `policy.json`: immutable observations, private enemy memory/state, utility contributions, bounded joint assignments and callback identities.
- `geometry.py`: synthetic rectangle/disc LOS/clearance and bounded grid BFS; Unknown/BudgetExceeded differs from Unreachable.
- `simulate.py` / `scenarios.json`: fixed-step finite events, sensors, squad reservations/queue and actual toy movement/recovery. Seed54917 applies to bounded hearing measurement noise.
- `verify.py`: counterfactual/invariant/comparison/FPS-scheduling checks and sequential expectations for a future UE port.
- `replay.html`: rendering template; decisions are recorded Python outputs.
- `inspect_replay.cjs`: optional isolated headless UI checks using an already installed Playwright and browser. No browser installation, normal browser attachment or user session takeover.
- `audit.py`: optional read-only selected source/native hash audit; writes only its requested new receipt.
- `finalize.py`: task-owned manifest/reconciliation generator, intended once per new handoff identity.
- `ue_contract.json` / `map_contract.json`: integration module/data/authority and real survey/physical acceptance gates.

`run_v1`–`run_v5` remain retained, including failed scopes. `run_v6` is selected **offline evidence**, never a Game/source/native adoption. Initial game audit used revision10; live shared source advanced to revision11 while this work ran. Always re-read the live combined selector before future integration. No production path, cover, patrol, weapon transaction or checkpoint schema changes are delivered here.
