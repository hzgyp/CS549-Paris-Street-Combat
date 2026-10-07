# German formal V14 integration

Implementation authority and stops:
`Docs/Development/GERMAN_NPC_FORMAL_V14_20261006.md`.
V14 is the integration version; the selected visual pose is **German V11**.
No V12/V13 fitting tools are dependencies. Do not rerun occupied identities or
old guarded authoring scripts after a newer formal epoch has been published.

`preflight.py` checkpoints the current 618-row epoch and derives German-only
42 holding locals/gun-hand relation; `build.ps1` makes a vacant BuildPlugin
output and preserves previous binaries. `run_entry.ps1` serializes current-host
native entries with process checks. Python is author/test observation only;
production animation and gun attachment are C++/original UE animation.

Modes: early (new graph/data and unsaved-map policy), compat (bounded movement
and original reload), author (map policy save gated on inspected results), fresh
(saved-map binding, no preparation), audit (saved package closure).
`run_game.ps1` tests ordinary saved-map launch with Python/bridge disabled.
`publish.py` verifies objects over authenticated SFTP and produces reviewable
manifest patches. Apply the generated patches with apply_patch before finalizing;
normalize only identical semantic manifest values to exact published CRLF bytes.

Never call an entry a pass merely because the engine exits0: inspect its actual
result/errors and native images. Keep known visual backlog distinct from failed
technical contracts and from full mission/MVP/performance/Shipping acceptance.
No routine commits/pushes Git or deletes original dependencies.
