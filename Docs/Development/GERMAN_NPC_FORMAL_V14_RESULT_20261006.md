# German NPC V11 with rifle — formal V14 integration result

6 October 2026. Yupu selected the previously refined German V11 **with its rifle**
as the formal MVP visual baseline. Local saved-map adoption and private SFTP
publication are complete. This document accompanies the matching generic
source/configuration/Catalog Git revision; verify remote main for push completion.
This supersedes older unarmed/unselected German statuses only in this scope;
it does not erase failed contact tests or declare the whole MVP passed.

中文摘要：三名现有德军及后续新增的兼容德军，正式使用原精修V11握姿和
FineWoodV15枪械。基础原生移动、一次原换弹、保存后重开及无Python启动
已验证；细小握姿问题延期，下一步回到MVP功能闭环，不继续精修手指。

## Selected assets and preserved sources

The saved `/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1` contains one native
`ParisGermanGripPolicy`, labelled `PC_GermanApprovedGripV11`. It binds the three
standard TeamId1 Germans and later compatible same-class/subclass spawns,
excluding players and other teams. Missing equipment uses the existing
`BP_PC_GermanRifleAttachmentV2` and `SM_PC_GermanRifleV15` FineWoodV15 mesh;
existing equipment is preserved. Policy-owned rifle/adapter cleanup is verified.

New private native packages are under `/Game/ParisCombat/Animation/GermanGripV14/`:
`DA_PC_GermanGripV11` and `ABP_PC_GermanGripPostV11`.
Ready uses **42 German V11 own local rotations**, not Allied copied parameters.
Original translations/scales, bone lengths, mesh, skeleton, weights, materials,
source actions, first-person and accepted Allied configurations remain unchanged.
Non-Ready releases to original UE animation; the rifle follows evaluated hand_r.
Python is authoring/test observation only, not runtime pose control.

The generic adapter adds only configured TeamId selection (existing Allied data
defaults to0; German explicitly uses1). Original node/attachment algorithms and
Allied policy are preserved. See the [plan](GERMAN_NPC_FORMAL_V14_20261006.md)
and [usage contract](GERMAN_NPC_ASSET_USAGE.md). The character-workflow skill
guided original animated-source preservation and actual native deformation
validation; no frozen diagnostic mesh was promoted into gameplay.

## Actual tests and boundaries

| Entry | Actual result |
| --- | --- |
| early_v1 / PID39084 / exit0 | Three present Germans and one later spawn bind V11; real V2 rifles/mesh and NoCollision verified. Later-target/owned-equipment cleanup passes. Existing two Allies and first-person initialize. Five original native Ready views inspected. |
| compat_v1 / PID33164 / exit0 | Native walk300cm/s, displacement185.599467cm; rifle follows hand. One original conserved reload2/16→8/10, overlay releases and returns Ready. Actual walk/mid-reload/return images inspected. Not full continuous action/contact acceptance. |
| author_v1 / PID2764 / exit0 | Saves only the new policy in the existing formal map. No source NPC package or model overwrite. |
| fresh_v1 / PID24208 / exit0 | Saved-map policy binds all three Germans and later spawn without Python preparation/binding. Five original native Ready views inspected; Allied/FP regression and owned cleanup pass. |
| audit_v1 / same fresh PID24208 | Read-only closure receipt:15,519 native files hashed, zero missing hard dependencies. Same five supplier soft gaps retained; bundled InterchangeAssets material parent recorded. Large hash work is outside motion/performance measurements. |
| ordinary_game_v1 / PID42060 / exit−1 | Stopped only owned startup process while waiting for Zen before map load. Service ready-health HTTP200. Possible interactive dialog wait is inferred from installed UE source, not visually proven and not an asset crash. Failure log/receipt retained. |
| ordinary_game_v2 / PID38840 / exit0 | Same saved ordinary-game entry with only unattended test mode added, PythonScriptPlugin/ParisEditorBridge disabled. Exactly three German and two Allied Ready logs, existing FP Ready;35-second timed normal shutdown. No FPS/action test inferred. |

Observed Ready local maximum error was0.000002414837degrees. Gun-hand relation
was below0.000000000001cm /0.000001708degrees in the pose-observed entries;
ordinary-game logger reported0cm /0.004928036degrees, within the declared
0.01cm/degree gate. Evaluated input/protection checks pass. These numbers are
binding checks, not zero intersections or a proof of every animation's contact.

## Saved authority and private SFTP

One physical map, referenced by two Content aliases:2,714,784bytes, SHA-256:

```text
70df2be5458961341a8ca47b473d1e89bb1a68276c4395941a8000532053f5b6
```

Selected release: `paris-native-playtest-20261006-german-grip-v11`.

- 294 files /634,257,570bytes, excluding the separately reused city manifest.
- 63 new immutable objects /83,180,437bytes (about79.3MiB);231 reused objects.
- All294 objects and release manifest authenticated-SFTP-download/SHA/size verified.
- Shared account create/update/rename/read/delete passes; root ACL unchanged.
- Exact published CRLF manifest SHA:
  `6c8eab2205379c796c0a446de71b8a3032e9adbaa5b254464859228cd3c86cd8`.

The new dependency closure adds60 content files /79,976,693bytes, including
the German native graph/data and existing rifle/material dependencies. Only
changed/new objects were transferred, not the26GiB city. The current project
descriptor remains exact. Original assets, private recovery and immutable release
history remain intact;294 verified disposable download samples were removed.
No source dependency or failed V12/V13 evidence was deleted.

Current **678-row guard epoch**:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/GermanNPCFormalV14/selected_v1/result.json`.
Old map, rebuilt NPC DLL and Catalog hashes are historical, not rollback authority.
Other lanes must explicitly adopt this verified epoch before their next writer;
never blanket-ignore guard failures. Restore the Catalog's city and native
playtest manifests, not a mutable owner workspace. See [team guide](TEAM_PLAYTEST_ZH.md)
and [publication receipt](../../Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json).

## Deferred, not blockers for this visual baseline

Straight right index, small stock overlap/self-contact and imperfect finger
seating remain visual backlog. V11 raw30/32/39 stock crossings and19 new self
pairs remain recorded; human MVP selection does not convert these to passes.
V12/V13 stay retired/unselected. No more grip fitting occurred in this adoption.

Full visual motion/recoil, continuous release/return, interruption/death/reset,
near-wall, warmed/stress FPS, Shipping/package and actual second-machine tests
are not passed by these bounded checks. NPC AI/mission decisions were not
selected or changed. Assignment3 still needs its four-pillar running mission,
performance/stress and submission deliverables.

Local selected-asset hashes, Git storage check, launch CheckOnly and seven
restore unit tests pass. These are not teammate runtime acceptance. The subsequent
user commit/push request authorizes publication of the matching source/configuration
revision, not commercial bytes or additional runtime adoption.

Final read-only QA initially expected a nonexistent first-person readiness
marker. The actual log has `Paris approved first-person native binding ready;
original gameplay retained`; only that observer assertion was corrected. No
native rerun, threshold relaxation or asset change. Final QA verifies all678
current rows, preserved baseline/config/descriptor, Python/PowerShell parsing,
actual faction/FP Ready logs and no running engines; A native slot is RELEASED.
