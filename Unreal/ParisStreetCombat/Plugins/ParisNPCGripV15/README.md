# Native NPC grip presentation

Status,6 October2026: the generic plugin is explicitly enabled in the formal
project. The saved map selects Allied V16 and German V11 WITH FineWoodV15 rifles
through separate native policies. Read the current dated results before editing:

- `Docs/Development/ALLIED_NPC_FORMAL_V18_RESULT_20261006.md`
- `Docs/Development/GERMAN_NPC_FORMAL_V14_RESULT_20261006.md`
- the respective `ALLIED_NPC_ASSET_USAGE.md` / `GERMAN_NPC_ASSET_USAGE.md`

Older unselected-draft statuses and map hashes are historical. Current678-row
guard epoch: private `Evidence/GermanNPCFormalV14/selected_v1/result.json`.
The plugin name is historical, not an instruction to copy faction parameters.

## Source / runtime relationship

Original meshes, skeletons, weights, materials, directional AnimBPs and source
clips remain runtime dependencies. Private DataAssets/graphs consume the original
evaluated pose, applying each faction's accepted Ready locals and releasing to
the same input outside Ready. This is not a new clip or frozen mesh replacement.
The generic actor attaches the existing rifle to evaluated hand_r and disables
only its competing placement tick. There is no Python per-frame pose driver.

`expected_team_id` defaults to0 for existing Allied configs; German data explicitly
uses1. Other values are unsupported. Never copy player/Allied transform numbers
to another faction, rig or weapon. Separate policies bind present/later compatible
same-class/subclass NPCs, supply a missing existing rifle without replacing current
equipment, and clean only their owned rifle/adapter when the target is destroyed.

Native protection checks remain strict. New zero-evaluation instances may wait
at most0.5game-seconds; these frames are counted, not called validated. Evaluated
invalid input stops the adapter. Do not hide failures by weakening thresholds.

## Build, storage and remaining limits

Generic C++ source is managed in Git. Commercial-derived UAssets, numeric binding
data, screenshots and binaries remain private/ignored. Catalog-selected matching
UE5.8.2 Win64 Editor Development modules are supplied by SFTP. Preserve prior
binaries and use a vacant planned build identity with no existing editor; old
one-time author scripts are not reusable against the current epoch.

Current policies, basic movement/original conserved reload, saved-map binding and
later-spawn owned cleanup are verified within their dated scopes. Full continuous
motion/recoil/contact, death/interruption/reset, near-wall, warmed/stress FPS,
Shipping and teammate runtime remain unpassed. German small grip imperfections
are deferred under the user's MVP decision. Do not restart stopped AN008 proofs,
finger/offset/blend solvers or refine accepted hands automatically.
