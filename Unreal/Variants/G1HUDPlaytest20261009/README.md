# G1 HUD playtest source variant

9 October 2026. Exact forty-file source/configuration snapshot corresponding to
the privately shared hud_v3 executable. SOURCE_MANIFEST.json pins original bytes;
Project contains only team source/configuration, no purchased Content or binaries.
The canonical Unreal/ParisStreetCombat project and its 758-file contract retain
their previous release. This variant is explicitly selected by the packaged
playtest; cloning Git does not silently replace the formal editor baseline.

Use the packaged SFTP release for direct play: its prerequisites, launcher and
dependency payload are already included. The two readmes describe controls and
limits. Rebuilding additionally requires licensed private Content, including the
retained PlayerActionsV1/V6 dependencies, UE 5.8.2 and a supported Windows C++
toolchain. This source snapshot alone is not a complete editable native release.
Existing G1PlaytestRevisionV1 / G1HUDConceptV1 tools and dated implementation/result
documents record wrapper preparation, selected cook closure and original checks;
their private historical evidence paths are author-side inputs, not public files.
Never copy rejected draft cook directories or infer a teammate rebuild pass.

For a separate wrapper, restore entitled dependencies to a writable copy, overlay
these exact source/configuration paths and generate/build its Game target. The
font sidecar and G1 ground-map data are in the shared playable payload. An Editor
build, clean recook, teammate rebuild and formal source/native adoption have not
been verified for this published snapshot. Do not point a writer at immutable
SFTP objects or use this source publication to broaden asset redistribution.
