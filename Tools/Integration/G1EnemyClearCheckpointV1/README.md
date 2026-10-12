# Enemy-clear checkpoint repair

Read the Chinese implementation/result and MI023 first. User explicitly changes
the objective/save gate to complete registered enemy clearance. Original soldier,
finger, weapon, resource, schema and durable transaction bytes remain protected.

Freeze and author a new immutable candidate, then `check_source.py`, Game-only
`build.ps1`, `stage_runtime.py`. Never rebuild a failed identity or mutate a
user-owned game. Normal launch has no observer flags and a separate UserDir.

`launch_check.ps1` modes: `menu`, `enemy_clear`, `restore` (shares only the named
isolated test UserDir), `legacy_restore` (copies actual old V5 bytes unchanged).
Enemy-clear explicitly uses diagnostic placement, AI hold and original PC_Die;
it is a functional gate matrix, not a real shooting/navigation/FPS benchmark.
Do not use old checkpoint probes expecting synchronous saves/unsafe wait/squad
victory. `verify.py` checks both functional receipts and independent protection.
Only after this succeeds, `finalize.py` records the local review candidate.
Current v3 production is the clear-only change plus `author_low_posture.py`:
only player snapshot centre Z uses standing-minus-current capsule half-height.
The original lifecycle loader resumes its existing standing state, not a saved
in-progress action; no extra schema field or live pose/resource edit is introduced.
Current success identities are menu_v1, clearance_v2, restore_v2 and legacy_v1;
v1 build and v2 low-posture location failures stay in MI023 and private receipts.
No Git/SFTP/formal-baseline adoption, cleanup, native save/recook or Editor entry.
