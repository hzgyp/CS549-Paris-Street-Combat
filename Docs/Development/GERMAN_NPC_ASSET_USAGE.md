# German NPC baseline usage

Owner: Yupu. Integration plan:
[German V14 formal integration](GERMAN_NPC_FORMAL_V14_20261006.md).
Formal selection and private SFTP publication are complete; see the
[dated result](GERMAN_NPC_FORMAL_V14_RESULT_20261006.md) for measured gates.
Current release: `paris-native-playtest-20261006-german-grip-v11`.

## Current formal selection

Use the existing animated German soldier class
`/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisGermanNPCV1` (TeamId1),
its unchanged translation skeleton/mesh and original action family.
Add **one** native `ParisGermanGripPolicy` to a mission map:

| Field | Asset |
| --- | --- |
| GermanNPCClass | `BP_PCParisGermanNPCV1` above |
| BindingConfig | `/Game/ParisCombat/Animation/GermanGripV14/DA_PC_GermanGripV11` |
| RifleAppearanceClass | `/Game/ParisCombat/Weapons/GermanRifleUEV1/BP_PC_GermanRifleAttachmentV2` |
| RifleMesh | `/Game/ParisCombat/Weapons/GermanRifleUEV1/ImportV1/GermanRifle_FineWood_V15/StaticMeshes/SM_PC_GermanRifleV15` |

Config references `ABP_PC_GermanGripPostV11` in the same GermanGripV14 folder.
The generic `ParisNPCGripV15` plugin must be enabled with its matching UE5.8.2
module; the name is historical and does not mean German uses Allied numbers.

## Runtime and new NPCs

The policy equips/binds the three current Germans and later compatible same-
class/subclass spawns, excluding players/wrong teams. Missing equipment uses
the existing accepted V2 native rifle; original equipment is not overwritten.
It connects WeaponAppearance, GripMesh and Combatant, and cleans up its own
rifle/adapter after target destruction. Do not also place a second grip adapter
or duplicate gun for that actor. Other rigs/weapon classes require new measured
calibration; never copy first-person or Allied gun offsets.

V11's own 42 holding local rotations and gun/hand_r relation are persistent
native data. Ready uses the native postprocess; non-Ready releases to existing
animation input. Gun socket binding and original UE actions control the runtime,
not Python. Source mesh, bone translations/scales, weights, materials and clips
remain original. Do not import diagnostic frozen Blender meshes as soldiers.
AI intent/transactions remain outside this presentation policy.

## MVP scope and later visual work

Yupu chooses the prior refined **German V11** as the formal MVP visual baseline
instead of spending more iterations on grasp details. Its straight right index,
small stock overlap/self-contact and imperfect finger seating are deferred,
not zero-contact passes. Retired V12/V13 experiments are not dependencies.
Future polish must start from this published selection with a new bounded plan,
not resume failed solvers or replace it with an unreviewed derivative.

Basic native compatibility tests do not establish full visual motion/recoil,
death interruption/reset, near-wall clearance, FPS/stress, packaged build,
second-machine or Assignment 3 acceptance. See the dated result for actual runs.

## Storage / synchronization

Only `Assets/Sync/CATALOG.json` selects the authoritative native-playtest
release. Restore its exact map, new graph/data, rifle dependency closure and
matching DLL/modules with editors closed. Git contains generic source/config/
hash records; commercial and derivative asset bytes remain private SFTP. Do not
copy mutable workspaces or delete source/recovery dependencies. Team access is
CRUD; immutable object/release preservation is still mandatory procedure.
