# MuzzleFlashV1 local formal asset usage

8 October2026. Local integration complete; publication is not included.
[Chinese review](MUZZLE_FLASH_ASSET_USAGE_ZH.md).
[Verified result and retained history](MUZZLE_FLASH_FORMAL_RESULT_20261008.md).

## What is installed

The formal project `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject` enables
the independent `ParisMuzzleFlashV1` runtime plugin. The saved profile is
`/Game/ParisCombat/VFX/MuzzleFlashV1/DA_PC_MuzzleFlashV1`. It selects the purchased
`/Game/MsvFx_MuzzleFlash_Pack/Prefabs/Niagara_Riffle_MuzzleFlash_01` system
(supplier spelling **Riffle**).

The single local content home is
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content`.
The formal project's existing Content parent junction exposes these children:

- `MsvFx_MuzzleFlash_Pack`:25 exact supplier packages.
- `ParisCombat/VFX/MuzzleFlashV1`:one saved native profile.

Three plugin binary files live under
`Unreal/ParisStreetCombat/Plugins/ParisMuzzleFlashV1/Binaries/Win64`.
These are29 new files, not29 new commercial assets. No new child junctions were
created. Purchased packages, saved DA, binaries and evidence images stay private;
this request performs no Git, SFTP or Catalog publication.

## Intended use in the existing project

Keep the original character, approved native grip policies and normal gameplay
fire entry. Do not add another per-gun Niagara spawn, timer or Blueprint fire
driver: the native world subsystem observes an actual committed ShotSequence and
attaches one effect to the currently presented verified rifle. It neither causes
the shot nor changes ammunition, damage, raycasts, pose, recoil or AI.

Game/PIE worlds load the saved profile automatically and wait for its Niagara
readiness. The subsystem periodically discovers compatible ready characters.
The current player needs the initialized approved first-person actor; current
NPCs need their initialized native grip adapter and WeaponAppearance. Exact
saved rifle-mesh identity is required: original M1 and selected FineWoodV15 only.
Hidden/unregistered/unavailable presentation does not spawn a substitute effect.
Binding baselines the existing sequence, so historical shots are not replayed.

The discovery code supports later compatible ready actors; this request's
Formal test verifies the original six-person roster, not every future spawn,
weapon, rig, map or multiplayer case. A different weapon/rig needs a separately
measured and reviewed profile, not copied M1 offsets.

| Fixed selected setting | Value |
| --- | --- |
| Effect-instance scale | 0.25, user-approved |
| Instance SpawnRate | 20; supplier package unchanged |
| Ordinary Deactivate request | 0.10 game seconds; not a measured exact callback age |
| Completion acceptance | actual IsComplete, within8-second bound |
| Mount | saved measured local muzzle for each rifle; pitch0/yaw90/roll0 |

Cooldown/empty/busy/dead rejected shots create no flame. Reload, death, reset and
equipment hidden/restored cancel owned presentation without replay. True
completion and cancellation are distinct; forced destruction is not completion.
World teardown clears owned effects. Destroying the original NPC equipment is
NOT a passed case: its earlier approved-grip failure is retained.

## Verified use versus remaining gates

The independent formal_transactions_v1_20261008 loads this installed profile
without private Python Configure or command-line plugin enable override. It
passes20 real original fire commits, rejection/reload/cancellation cases, two
actually simultaneous pulses and native nonempty world cleanup2→0. All39 new
originals were individually inspected; FP06/Allied20/German32 clearly show main
flame, and separate visual review/audit pass. Runtime observation is native;
the bounded test still uses its diagnostic Python harness, pre-actor fire queue
and deferred review capture. No Python pose driver is introduced.

This is not an ordinary manual-input/no-Python startup test, whole-city/near-wall
visibility guarantee, deterministic reliability proof, FPS/Shipping/teammate
test, or whole-MVP/course acceptance. The automated follow-up is stopped after
this local scope completes; no further engine entry is needed for closeout.

## Maintenance contract

Cases read: Failures/README, AN009/AN010, paired formal plan and its request,
readiness, lifecycle, capture and inherited-binding corrections. This attempt
adds only the selected presentation plugin/profile/assets/one enable row and
the narrow shared protection-reader hook; approved gameplay and formal map stay
unchanged. Early checks are strict build,35 offline+4 shared guard tests,703
guards,68 originals,25 private dependencies and29 exact installed files. Only
the authorized descriptor row advances; other702 remain exact. Evidence is at
the private `Evidence/MuzzleFlashV1` under the single-home workspace above.

Stop on hash/root/profile/strict-log/runtime/visual/cap drift. Preserve occupied
identities, original receipts and copy failure; never rerun a failed mechanism,
overwrite assets, waive gates or sweep parameters/camera/capture timing. The
immutable installation proof intentionally retains its pre-Formal false flag;
the later Formal audit proves latest completion. Any additional verification or
different adaptation requires a new bounded plan and actual process inventory.
