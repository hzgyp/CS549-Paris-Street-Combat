# Local character validation tools

Read `../../Assets/CHARACTER_COMPATIBILITY_AND_REPAIR.md` for findings, scope and release gates. These scripts operate on the dated ignored lab, not the Paris game project. They contain no vendor bytes or credentials. Do not substitute the production project path into the capture scripts: they create diagnostic maps and the pose script saves lab-only compatible-skeleton metadata.

Prerequisites: an entitled local intake, its `tmp/asset-intake-review/intake_static_inventory.json` checksum baseline, UE 5.8.2 with Python/EditorScriptingUtilities/GLTFExporter, Blender 5.2.2, and Python with Pillow for contact sheets. Resolve the engine and Blender executables locally; do not assume every teammate has the same installation directory.

For a new lab, create the lab/Config directories and copy the two text templates to `AssetCompatibilityLab.uproject` and `Config/DefaultEngine.ini`. Then run `prepare_lab.py`. Do not rerun preparation over an adapted lab; it intentionally rejects edited copies. Current lab: `Assets/LocalWorking/Validation/UE582/2026-09-30-v1/`.

| Script | Invocation / purpose |
| --- | --- |
| `prepare_lab.py` | Ordinary Python; hash-preserving initial copy only. |
| `ue_inventory.py` | UE Python commandlet; actual registry/load/rig/material inspection. NullRHI allowed for structural checks, not appearance. |
| `ue_visual_exports.py` | UE rendering-enabled Python commandlet; FBX/GLB exports, pose evaluation and actual material captures. First use can require substantial shader compilation. |
| `ue_native_capture.py` | UE rendering-enabled Python commandlet; native materials only, without lossy optional glTF baking. |
| `blender_export_audit.py` | Blender `--background --factory-startup --python`; fresh FBX import metrics. |
| `blender_glb_audit.py` | Blender background Python; fresh baked-GLB texture and weight checks. |
| `ue_pose_validation.py` | UE rendering-enabled Python commandlet; hierarchy-gated lab compatibility declaration, actual component animation/skin refresh and frame captures. |
| `review_captures.py` | Ordinary Python; contact sheets without altering captured originals. |
| `verify_versions.py` | Ordinary Python; original preservation and staged-package hashes/header branch strings after resave. Not a published asset manifest. |
| `ue_export_resaved.py` | Rendering-enabled UE Python commandlet; 12 meshes and seven clips from resaved packages, FBX 2018 compatibility, per-file hashes. NullRHI mesh export is not supported by this verified route. |
| `summarize_results.py` | Ordinary Python; aggregate final evidence, compare pre/post-resave checkpoint positions and native/imported clip duration. |

For rendering-enabled UE tests use `-run=pythonscript -script=<absolute script> -AllowCommandletRendering -RenderOffscreen -unattended -NoP4 -stdout -abslog=<absolute evidence log>`. Run one UE test at a time against the lab. Preserve JSON/log completion timestamps and inspect errors; success exit alone is insufficient. Keep the pre-resave inventory, perform project-only resave as documented, and fresh-load again. A completed source compile check does not exercise Unreal/Blender APIs.

Binary exports, raw logs, images and diagnostic scenes stay outside Git. Any eventual team publication needs the existing immutable SFTP/version-manifest workflow and verified rights. Do not put connection credentials or engine-generated security tokens in these text templates.

## Repair and single storage on 1 October

Canonical lab: `Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/`; the former LocalWorking lab is a junction alias. Original intake was subsequently moved to the `character-20261001-v1` baseline with old intake aliases retained, and the rights-cleared lab now grants shared-account Modify. Do not rerun preparation or consolidation over existing trees. `consolidate_character_storage.ps1` documents the earlier one-time private intake migration, not the current published ACL state or a daily downloader.

`prepare_character_publication.py plan` checks original/repair hashes and generates the dated, ignored publication plan. `publish_character_release.ps1` is the administrator-only, dated server publisher: closed-editor guard, same-volume original relocation, scoped sharing permissions, final server SHA-256/size checks and immutable object/manifest publication. It does not publish Git. Do not rerun it as a daily synchronization or clean-up command. `prepare_character_publication.py adopt` requires successful administrator and actual SFTP verification reports before generating active catalog metadata. Published paths and remaining gates are in `../../Assets/Sync/README.md`. The fresh lab template matches the repair renderer and disables unnecessary Android file-server networking, with no generated token.

The bounded repair tools are `ue_repair_probe.py` (actual material parameters/graphs), `ue_repair_textures.py` (source PNG/EXR export), `ue_eye_environment_test.py` with `CS549_EYE_MATERIAL_TEST=1` (fixed-context legacy/PBR comparison), `ue_eye_repair.py`, and `ue_apply_eye_adaptation.py` (editor-aware duplication and forced material-binding save). Use rendering-backed exports; manually forcing PNG on an HDR source caused a native exporter assertion and was replaced with SourceFormat-aware EXR selection. Do not relabel that failed attempt as a corrupt model.

Run `blender_repair_exchange.py`, then independent `blender_verify_repair.py` with Blender 5.2.2. Both accept `CS549_ASSET_LAB` for the canonical lab. The repair keeps native UE meshes/actions authoritative. Portable PBR previews are not exact vendor material graphs. `CS549_NATIVE_REPAIR_REGRESSION=1` selects saved adapted meshes and separate outputs in `ue_native_capture.py` and `ue_pose_validation.py`; `CS549_REPAIR_INVENTORY=1` produces a fresh final inventory excluding diagnostic maps. `CS549_REPAIR_VERSIONS=1` checks the 540-package closure and original preservation without replacing the dated baseline report. `finalize_character_repair.py` freezes hashes and asserts recorded regression gates; it never uploads or changes CATALOG.

`cleanup_redundant_diagnostics.ps1` removes only enumerated task-generated old diagnostic outputs and lab caches after checking hashes of retained fresh-verified repair files, with affected jobs closed. It preserves originals, native Content and the post-resave baseline FBX inputs needed to reproduce the repair. It is not a repository/global cleanup tool. The old FBX audit creates extra diagnostic `.blend` files only when explicitly requested with `CS549_KEEP_DIAGNOSTIC_BLEND=1`; default numerical checks no longer leave those redundant scenes.

For the post-resave Blender audit, set the process-local environment variable `CS549_FBX_SUBDIR=UE582Resaved`; the tool writes a separate report, imports seven action files, and retains the initial FBX baseline. Do not confuse a diagnostic `.blend` with a complete texture-packed Blender production delivery.
