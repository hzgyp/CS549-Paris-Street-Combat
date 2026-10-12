# Asset Workbench V1 — implementation result

Date: 11 October 2026. Revision: 1.0. Status: local implementation and scoped automated verification complete; user interface acceptance pending. [中文](IMPLEMENTATION_RESULT_20261011_ZH.md).

The user authorized implementing the [functional specification](FUNCTIONAL_SPEC_20261011.md) and [technical design](TECHNICAL_DESIGN_20261011.md), followed by opening the finished platform for inspection. This delivery is a working local application with real project metadata and registered previews. [Start and installation](../../../Tools/AssetWorkbench/README.md).

## Delivered behavior

The six navigation pages provide overview, asset library, version comparison, build relationships, new-asset requirements and catalog health. Asset details include original sources, review limitations, scoped evidence, usage links and revision history. File tables provide paginated path search and bounded local verification. Seven requirement templates can be copied or downloaded. Metadata refresh and cancellation write only the workbench's own state.

Current coverage is 8 curated logical assets, 13 selected Catalog groups, 17,866 indexed file rows including source snapshots, 47 evidence records and 83 read sources. The 17,519 unique hash/size identities imply 39,907,772,400 expected bytes; this is a manifest estimate, not measured disk consumption. All planned pilot families are present: German, Allied, first-person, pressure mine and recorded audio; rifle, city and animation are also curated. This is not exhaustive semantic registration of every mesh in the environment.

Three purposes remain separate: formal enemy-clear v3, current UI review `candidate_field_manual_v2`, and the recorded audio V2 published package. The equipment-specific candidate remains accessible separately. The current UI selector changed after the original planning snapshot; the platform reads its actual authority rather than freezing the old v5 name. UI review Game identity begins `b40590bdec9c`; formal `b40409b08830`; published `53ab36d9da19`. Complete identities and source hashes are available through the platform.

The mine comparison preserves the failed dark UE image and corrected UE image. Both point to the same registered Blender/GLB/baked-map identity. Blender success does not override the failed UE result. German V13 rejection and V14 adoption of V11 remain distinct; V13 is a decision predecessor, not a source parent of V14. German contact limitations and historical duplicate-animation delivery remain visible. Preview dates and scopes are recorded; old soldier portraits are not newly captured V14 acceptance pictures.

## As-built technical decisions

- React/TypeScript + Vite serves from FastAPI on loopback. SQLite uses DELETE journaling and transactional activation of immutable snapshots. Generic typed entity families are stored as JSON rows, with relational file/snapshot/job tables and indices; the initial cache schema is version 1, not a full future schema-upgrade framework.
- Python dependencies are pinned in `requirements.lock`; frontend uses `pnpm-lock.yaml` rather than the design's illustrative npm command. The setup script executes frozen installation and a production build.
- Default port 8765 was occupied by unrelated PID 22664. It was preserved; the ignored local config selects 8766. `run.ps1` recognizes the venv child through its exact command line and parent relationship, rather than assuming the launcher PID is the listening Python process.
- API session cookies, CSRF, Host/Origin checks, opaque media IDs, exact hashes, signature checks, bounded reads and final Windows handle paths constrain local access. No API executes project commands or edits upstream asset records.
- Nine explicitly registered previews reference existing bytes; none were copied into public source. Missing private media or receipts degrade to placeholders/issues. Metadata import does not traverse Content or follow junctions. There is no implicit trusted-junction exception in this initial implementation.
- Build-to-asset links are curated family-level document bindings. They are visibly distinguished from fresh runtime observations or an exhaustive dependency scan. Existing native packages are neither opened nor saved.

## Executed verification

The final backend run returned **27 passed in 8.13 seconds**. The final browser run returned **3 workflow tests passed in 12.1 seconds** using installed Chrome. TypeScript checking and Vite production build passed. Repeat setup with installed dependencies and launcher reuse passed. A fresh owned service start passed after the Windows child-process correction; the launcher measured 1,363 ms with the existing index.

| Scope | Actual evidence |
| --- | --- |
| AC01, AC03, AC05–AC07 | Real selector identities remain independent; mine model identity matches; failure/adoption/duplicate records remain scoped; build and reverse usage navigation exercised |
| AC02, AC08, AC12 | Chinese and English search, category/card/list modes, source modal/ESC, template copying, and 1920×1080 / 1366×768 browser workflows; rendered overview, library, comparison and requirement screenshots visually inspected |
| AC04, AC09, AC11 | Synthetic source-only fixture; missing/MIME-invalid/unauthorized media denied; bad manifest/schema and concurrent source drift preserve active snapshot; exit0/missing result and unknown-mode cases never pass |
| AC10, T08–T10, T14 | Hash-change rejection, traversal cases, actual Windows junction denial, read-size bounds, HTTP ranges, same-origin/session checks, idempotent jobs, busy rejection/cancel, unsupported write endpoint, process crash before commit, rebuild semantic identity |
| T13 | 17 registered upstream metadata files and 9 served media files retain their original SHA-256; inspected implementation writes only own state. This is not an OS-wide write trace or complete native-file audit |

Machine: Windows, Intel i9-12900F (16 cores/24 logical processors), approximately 31.8 GiB physical memory; Python 3.13.7, Node 24.19, pnpm 11.25. SQLite 3.50.4 operates in DELETE mode. The 20,000-file synthetic query benchmark measured **p95 3.74 ms** in the final backend run. A production metadata refresh measured **3,428 ms**. First interactive overview with server/index ready measured **387 ms**, including the registered spotlight image decode. Nine authenticated media reads measured **29.16–63.68 ms** each. These are local single-session observations, not remote, concurrent-user or fresh-machine benchmarks.

Private receipts live under `Assets/LocalWorking/AssetWorkbench/runs/`: `backend-tests.xml`, `ui-results.json`, `browser-timing.json`, `verification.json`, service logs and `screenshots/`. The verification receipt contains exact application source hashes and the sampled upstream/media identities. No raw screenshot was added to the public image allowlist. One Starlette/httpx deprecation warning and Node color-environment warnings remain; they did not fail the checks.

## Failures retained and corrections

1. pnpm initially withheld the esbuild install step. Its known build dependency was explicitly allowed in `pnpm-workspace.yaml`, rebuilt, and the frozen setup then passed.
2. Initial port 8765 binding failed; preserved the existing service and selected 8766. Raw startup logs remain.
3. Launcher initially timed out because the venv parent PID differed from the listening child. Process ownership detection was corrected and start/reuse both passed.
4. A direct `/assets/recorded-audio` refresh returned a static-file 404. Static bundle handling now requires a filename extension, while asset deep links return the SPA. A backend regression check and the browser's audio-detail loading flow pass. Original screenshot/error/report remain under `runs/failures/deep-link-v1`.
5. A negative test expected unauthorized media to return 403, while the importer deliberately excludes that entry and records `RIGHTS_NOT_ESTABLISHED`, producing 404. The fixture now checks the actual exclusion and issue record; no access rule was relaxed. The failed XML remains under `runs/failures/media-denial-expectation.xml`.
6. Nested select labels included option text, so an exact accessible-name locator timed out. Explicit aria-labels now identify rights and owner filters; the complete workflow passed. Original evidence remains in `runs/failures/filter-accessible-name`.
7. A one-off edit helper failed under Windows' GBK default before modifying a file. The edit was reapplied through a Unicode-safe patch. A separate helper used the wrong working directory and also failed before writing; an exact-path patch completed that edit. The successful setup command that followed was not treated as success of the failed edit.

`ui-results-before-service-ready.json` is an older copied receipt whose name is misleading: its content records the deep-link failure, not the initial no-session startup attempt. Preserve that historical name; use the explicitly named failure directory for interpretation. No failed result was used as a passing asset result.

## Acceptance limits and follow-up

The user still needs to inspect the opened UI. The 30-second human discovery target has not been measured with the user. The enumerated tests cover the implemented V1 workflows, not every possible malformed schema, image mismatch, decompression attack or concurrent workload in the planning matrix. No fresh second-machine installation, multiplayer access, UE import/save, gameplay retest, SFTP readback or asset reacquisition was performed.

There is no task editor, online approval writeback, 3D model viewer, public hosting or automatic asset generation in V1; those retain the planned V1.1/V1.2 boundaries. Additional logical assets can be curated into the versioned mappings; adding source or media adapters must preserve the same authority and audience rules. No Git commit/push or SFTP publication was performed for this task.

Read cases: MI030, MI033, MI035, MI036 and GP010, linked in the [technical design](TECHNICAL_DESIGN_20261011.md#15-verification-matrix-and-stopping-rules). This attempt changes the mechanism to explicit metadata adapters, scoped result mapping and atomic snapshot activation. The early check was distinct build purposes plus failure/missing/incomplete evidence before UI expansion. The stopping conditions remain protected-byte changes, unregistered path access, private-media leakage, ambiguous authority or a false passing result; preserve the old snapshot and repair the bounded adapter/contract before continuing.
