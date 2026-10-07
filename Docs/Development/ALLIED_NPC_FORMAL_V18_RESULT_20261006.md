# Allied NPC V16 formal adoption — V18 result

6 October 2026. Yupu accepted the current native Allied appearance and explicitly
requested that both current and future Allied NPCs use it. Formal adoption is
complete locally and in the private SFTP Catalog. Matching Git changes are not
committed or pushed. This report supersedes earlier unselected/in-progress
statuses only for this adoption; it does not erase failed tests.

## What is now selected

The saved `/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1` includes the native
`ParisAlliedGripPolicy` actor, labelled `PC_AlliedApprovedGripV16`. It creates one
existing V16 native pose/weapon adapter for each standard Allied NPC, including
both level-placed Allies and later compatible same-class/subclass spawns.
The policy supplies the original M1 appearance only if a later spawn lacks it;
existing level-authored equipment is preserved. Destroying a later target also
removes its adapter and policy-created appearance.

The exact accepted graph, DataAsset payload and adapter algorithm are unchanged.
There is no new model, skeleton, skin weight, material or animation clip and no
Python pose driver. The original model/actions remain runtime dependencies.
First-person V20, Germans, NPC AI and gameplay transactions are not modified.
Old Allied grip presentation is unselected, not destructively deleted. The
character workflow influenced the native binding/source-preservation checks,
not another modeling iteration. See the [implementation plan](ALLIED_NPC_FORMAL_V18_20261006.md)
and [asset-use contract](ALLIED_NPC_ASSET_USAGE.md).

## Actual verification

| Entry | Result and boundary |
| --- | --- |
| early_v1 / PID52292 / exit0 | FAILED future-spawn equipment check; both existing Allies bound correctly. Preserved, not relabelled successful. |
| early_v2 / PID29800 / exit0 | Both Allies plus a later third bind the accepted native config. Eleven Ready-local angle errors are 0 degrees; valid input, source/gun identity and protection checks pass. Later-target/owned-gun cleanup passes. Two actual city views inspected. |
| author_v1 / PID27500 / exit0 | Saved one physical map with the policy; project descriptor explicitly enables ParisNPCGripV15. No source NPC package save. |
| fresh_v1 / PID36352 / exit0 | Saved-map load, both Allies and later-spawn/cleanup gates pass without staging or Python binding. Two fresh city views inspected; FP/player/German exclusions pass. |
| audit_v1 / PID42712 / exit0 | 15,459 referenced files hashed; zero missing hard dependencies. The same five supplier soft-reference gaps remain documented. |
| ordinary_game_v1 / PID37240 / exit0 | Saved ordinary -game, PythonScriptPlugin and ParisEditorBridge disabled. Exactly two Allied native Ready logs, gun residual 0cm/0deg, existing FP Ready log; 35-second timed normal exit. No action/FPS test implied. |

The early failure arose because the soldier Blueprint alone does not recreate
the separate rifle actor/wiring previously authored in the level. A different
native equipment-registration mechanism fixed that gate; no pose, blend,
finger, offset or threshold retry was used. Final build identity is
`Build_formal_policy18_v4`; earlier binary snapshots remain private.

Measured protection error was 0.000002414837, below the declared 0.0001 gate.
Existing and later-spawn relative gun errors were below 0.000000000001cm and
0deg; accepted eleven Ready locals were exact. Static native views showed
continuous arms/cuffs. These checks do not prove zero mesh intersections or
continuous contact throughout every animation.

The previous user-owned preview PID50884 was already absent and its log showed
normal shutdown; its OS exit receipt is unavailable. It was not terminated.
All six owned adoption entries above exited normally; no UE/Blender engine
remains at closure. Lane A explicitly releases the serialized native slot.

## Saved authority and guard epoch

The map is 2,712,851 bytes, SHA-256:

```text
f268693b63fc23db0317b8fc60f7f0a6a7f01acd5450082eed4c84727e7b2416
```

Two protected paths refer to this one physical map through the Content junction.
Before publication, 609 other old guard rows were exact. Catalog selection then
intentionally changes Catalog metadata too. The new 618-row snapshot is private:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/AlliedNPCFormalV18/selected_v1/result.json`.
All 618 rows, accepted adapter/config/packages and descriptor scope were freshly
verified. Old map/Catalog guards are historical, not rollback authority. Other
lanes must explicitly adopt the current snapshot before their next writer;
never blanket-ignore a guard mismatch.

## Private SFTP publication

Selected release: `paris-native-playtest-20261006-allied-grip-v16`.
Restore `france-liberation-content` and `paris-gameplay-native-playtest` using the
Catalog, not an owner's mutable workspace. [Team instructions](TEAM_PLAYTEST.md)
and the synchronized [Chinese guide](TEAM_PLAYTEST_ZH.md) describe restoration.

- 234 selected files, 554,256,416 bytes excluding the separately reused city.
- 8 new immutable objects uploaded: 3,596,009 bytes; 226 objects reused.
- All 234 objects and the manifest authenticated-download/SHA-256/size verified.
- Shared-account create/update/rename/read/delete verified; root ACL unchanged.
- Exact published CRLF manifest bytes retained; SHA-256
  `78c6a0eb95a6ad8ee3615155afddc11af6e9992241b44da89ef2c3a9f70f2ba5`.

The added closure contains the two unchanged V16 native packages, three new
matching Win64 module files and an already authorized friendly-fire policy
dependency. The changed map and previously authorized shared-combatant revision
are published; this work did not modify that B revision or select its NPC AI.
Existing city/character/animation assets are reused, not retransmitted in full.
After verification, 234 disposable download samples were removed (about 554MB).
Published objects, originals, recovery copies and failed evidence remain intact.
See [publication receipt](../../Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json).

## Remaining limits

Native source preservation and formal selection are complete; the user's
appearance acceptance is recorded separately. AN008's stopped fixed-delta and
full-motion launchers remain locked. Full-return cadence/instance reset,
clear-shot/muzzle/recoil, interruption/death/reset, near-wall, warmed/stress FPS,
Shipping and actual teammate restoration/runtime are not passed by this work.
The limited future-spawn destroy cleanup check is not whole combat lifecycle
acceptance. Supplier soft gaps are retained, not repaired or hidden.

Local storage/hash checks, startup CheckOnly and seven restore unit tests pass.
Storage metadata covers 17,523 selected files; this is not a repeated complete
local hash test of every manifest. Scoped Git diff whitespace check passes;
the unrelated pre-existing DefaultEditor.ini trailing-blank warning is retained.
No further hand refinement, German correction, asset acquisition or Git
commit/push is part of this adoption.
