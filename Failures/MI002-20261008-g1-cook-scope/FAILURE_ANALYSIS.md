# MI002 - G1 cook scope includes retired drafts

8 October 2026. English original; [Chinese review](FAILURE_ANALYSIS_ZH.md).

The first closeout wrapper (`package_v1`) compiled the selected four runtime
plugins and Windows Game successfully, but Cook exited 1 / UAT 25. Its broad
`DirectoriesToAlwaysCook=/Game/ParisCombat` loaded the retired
BP_PCSquadReservationV3, whose BP_PCNPCSquadV3 cast target is absent. Nine compiler
errors (three unique invalid-pin/cast messages) prevented packaging. Existing
BehaviorV1/V2 missing-tree hints and other draft warnings are retained too.
There is no G1 packaged startup or integrated gameplay result from this attempt.

Cause: the new build helper confused the development inventory with the runtime
dependency closure. A successful selected-entry editor scan does not prove every
old package in its parent directory is cookable. This is a build-scope error,
not evidence that current G1 AI or map navigation fails.

Private raw source/config/prepare/build receipt and full UAT log remain in
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/package_v1/`.
The original native inputs are retained, not repaired/deleted/resaved. Stop this
identity; no automatic compiler-node refresh, class redirect or disabled-error
retry. Baseline native/source/703 guard recheck accompanies the next entry.

Different bounded correction: new `package_v2` follows the G1 map's hard
dependencies and explicitly includes only the selected dynamically loaded muzzle
profile directory plus the existing InPlace rifle action directory. Preserve
required referenced engine resources. Early acceptance is successful cook with
zero errors and no retired V3 reservation in the cooked package set; then actual
native-ready roster at verified1920x1080 in a separate packaged launch. Stop on
missing required dependencies, compiler/runtime errors or input drift. Do not
reduce any gameplay, ammo, save, path, FPS or human acceptance criterion.
