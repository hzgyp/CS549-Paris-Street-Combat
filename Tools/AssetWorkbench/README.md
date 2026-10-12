# Paris Asset Workbench V1

Internal, read-only asset catalog for Paris Street Combat. [中文说明](README_ZH.md). [Implementation result](../../Docs/Development/AssetWorkbenchV1/IMPLEMENTATION_RESULT_20261011.md).

12 October source-publication scope: [the functional Git publication record](../../Docs/Development/GIT_FUNCTIONAL_PUBLICATION_20261012_ZH.md) covers this application's code, tools and documentation. Private media, models, animation caches, runtime configuration and authenticated sharing links remain excluded. Historical implementation results retain their dated validation limits.

Use **中文 / English** in the header to switch language. The browser remembers the selection; filters, revisions and the active template remain selected. Copied/downloaded templates use the selected language. Source excerpts retain their original language. [Bilingual update](../../Docs/Development/AssetWorkbenchV1/BILINGUAL_IMPLEMENTATION_20261011.md).

## Start

From the project root in PowerShell:

```powershell
./Tools/AssetWorkbench/run.ps1
```

The launcher reuses its own running service or starts a hidden Python service and opens an authenticated browser session. The default port is 8765. This workstation uses 8766 because another service already owns 8765. The local setting is `Assets/LocalWorking/AssetWorkbench/config.local.json`, containing `{"port":8766}`. Use `-Port 8767` to choose another free port; do not terminate an unrelated listener. `-NoBrowser` starts/reuses the service without opening a browser.

The launch URL carries a process-local bootstrap secret in its fragment; the frontend exchanges it for a local cookie and clears the fragment. Share only the links in the private `runtime/share-link.txt` with authorized members; do not distribute the session file. Closing a tab leaves the service running for later inspection. To stop it, inspect the PID in the ignored `runtime/session.json`, verify that its command line names this workbench's venv and `-m app.cli serve`, then stop only that process. Windows may use the base Python executable for a venv child, so executable path alone does not establish ownership.

## Install on a new workstation

Network sharing on this workstation uses `{"port":8766,"host":"0.0.0.0"}`. The existing launcher listens on all IPv4 interfaces. Use `-BindAddress 127.0.0.1` for local-only mode; restart the service when changing modes. Other machines use the actual server IP, not 0.0.0.0. Authorized sharing links are generated in the private `Assets/LocalWorking/AssetWorkbench/runtime/share-link.txt`, primary interface first. Links contain an access credential and are regenerated after service restart.

`enable-sharing-firewall.ps1` requires Windows administrator rights and opens only the current Python program's TCP port to the local subnet on Private/Domain profiles. Sessions, same-origin checks and CSRF remain required for remote requests.

For router port forwarding, add `"external_url":"http://your-public-IP:external-port"` to the private config.local.json and restart this service. The exact external Host and port are registered; external and local ports may differ. Direct forwarding currently supports HTTP. Copy the authenticated link from `runtime/public-share-link.txt` for teammates. Run `./Tools/AssetWorkbench/enable-sharing-firewall.ps1 -Port 8766 -RemoteAddress Any` as administrator to accept forwarded remote sources within the same program/port/profile restriction; the default remains LocalSubnet. Update the setting and restart after a public IP change. Links are regenerated after service restart. Verify from another network; LAN or router loopback success does not establish external reachability.

Prerequisites: Windows, Python 3.13+, Node 22.12+ and pnpm 11. The tested environment uses Python 3.13.7, Node 24.19 and pnpm 11.25. From the project root:

```powershell
./Tools/AssetWorkbench/setup.ps1 -Python python -Pnpm pnpm
./Tools/AssetWorkbench/run.ps1
```

Explicit Python/pnpm paths are accepted. Put the selected Node executable directory on PATH. The script creates a project-local venv, installs `requirements.lock`, installs `frontend/pnpm-lock.yaml` with frozen resolution, then checks TypeScript and builds the frontend. Python and JS dependencies require network access on first installation. No global dependency installation is performed. A repeat setup using existing dependencies was executed successfully; a clean second-machine installation has not been tested.

## Data and boundaries

- Public source mappings: `Assets/Registry/registry.json`, `assets/pilots.json`, `mappings/history.json`, `templates/requirements.json`.
- Authoritative project Catalog, exact manifests and selectors remain upstream. The workbench reads them; its SQLite index cannot adopt a gameplay baseline.
- Generated state: `Assets/LocalWorking/AssetWorkbench/{cache,runtime,runs,private-records}`. Frontend `node_modules`, `dist` and test output are ignored as well.
- Optional private previews: `private-records/media.json`. Each `files` member declares `id`, `asset_id`, workspace-relative `path`, `sha256`, `size_bytes`, `mime`, `audience: local_owner`, `label`, `kind`, and a reviewed `rights_basis`. Only explicitly reviewed local media belong here. Never copy keys, purchase receipts or unrestricted folder listings into it. Metadata-only clones work without this file and show placeholders. Missing historical private evidence remains unavailable, never passed.
- V1 supports PNG/JPEG/WebP/WAV. Registered bytes, content signatures and path boundaries are checked at read time. Existing Content junctions are not implicitly trusted. Models, textures, documents, archives and executable scripts are not generic browser-download endpoints.
- The inventory contains 229 asset/package records. Selected Catalog groups are indexed at file level; current counts follow the refreshed upstream Catalog rather than an old fixed group count. This is not a scene-wide UE Asset Registry export.
- Source excerpts are escaped text. Private preview-map source excerpts are redacted. Displaying local vendor previews grants no public redistribution rights.

Use Refresh index after asset registrations, revisions, usage records or upstream documents change. It automatically synchronizes the platform snapshot, JSON asset index and Markdown directory; no separate command is required. Historical snapshots remain readable. Critical metadata errors retain the previous snapshot. Optional missing evidence becomes a visible catalog issue. The file-group verification button checks local bytes within a bounded request; it neither restores files nor validates remote SFTP objects. A preview registration is not a claim that every asset file is locally present.

## Develop and verify

From `Tools/AssetWorkbench` with the local venv:

```powershell
../../Assets/LocalWorking/AssetWorkbench/runtime/venv/Scripts/python.exe -m app.cli index --metadata-only
../../Assets/LocalWorking/AssetWorkbench/runtime/venv/Scripts/python.exe -m pytest -q -s
```

From `Tools/AssetWorkbench/frontend`, with the service running and its session file present:

```powershell
pnpm run build
pnpm exec playwright test
```

UI tests use installed Google Chrome, target the session file's loopback port and save private screenshots under `Assets/LocalWorking/AssetWorkbench/runs`. They exercise search, sources, comparison, build channels, file queries, templates, refresh, keyboard use and audio loading. Do not publish those screenshots without the project's exact-path image review.

Architecture: React/TypeScript + Vite, FastAPI, SQLite DELETE journaling. `app/catalog.py` imports explicit sources; `store.py` atomically activates immutable snapshots; `security.py` validates actual file handles; `main.py` exposes scoped authenticated APIs; `cli.py` owns the local listener. Animation selection can launch a bounded UE/Blender conversion against registered private copies. Source editing, asset deletion, Git publication and SFTP writes are not exposed. Structured task editing remains a subsequent phase.

## Animation packages — 2026-10-11

All 125 animation packages now open in 3D, with a searchable directory of 25,219 native AnimSequence entries. Select an action, then play/pause, seek or change speed. Left drag orbits, wheel zooms and right drag pans. The camera follows native motion; Reset view restores framing. Chinese and English controls are available.

The 125 default actions are prepared. Other actions are converted on first selection using the local UE 5.8 and Blender 5.2 installations, then cached. Progress and explicit failures remain visible; conversion is serialized. Two measured first-use conversions took 41–45 seconds on this workstation. All directory entries are selectable, but only the default actions and three additional actions have been converted and checked so far.

These are neutral-material source previews. Movement Animset Pro explicitly uses an external compatible preview mannequin. No retargeting or native asset saves occur. Private `animation-packs.json`, the copied projects in `native-covers-v1`, and `animation-viewer-v1` caches are required on this workstation. They are not included in source-only clones. The six earlier model files remain registered alongside 125 package defaults. [Implementation and validation](../../Docs/Development/AssetWorkbenchV1/ANIMATION_PACK_3D_RESULT_20261011_ZH.md).

## 3D and animation — 2026-10-11

The German soldier, Allied soldier, first-person arms, German rifle, rifle animation set and candidate pressure mine have a **3D & animation** tab. The M1 source mesh is an additional model choice on Allied/first-person pages. Left drag orbits, wheel zooms, right drag pans, and Reset view fits the current pose. Seven existing source clips support play/pause, seeking and 0.25–2× speed. Static rifles/mine have no invented animation. Images and audio remain in their own tab.

Character previews omit UE camouflage/tint, native finger/grip overrides, weapon attachment and gameplay state transitions. They are source mesh/animation views, not a complete rendering of the selected game integration. Textures in generated copies are at most 1024 pixels; exact rifle/mine GLBs remain unchanged.

`private-records/models.json` registers six private self-contained GLBs, version/source hashes and local audience. `/api/v1/models/{id}/file` requires the existing session, snapshot, safe workspace path, matching SHA-256 and valid embedded-only GLB under 128 MiB. No arbitrary file endpoint exists. Three.js is lazy loaded; GPU resources are released on navigation. Preserve private `3d/export-v3` with the registration. Export/verification/registration scripts are `prepare_viewer_models.py`, `verify_viewer_models.py`, `register_viewer_models.py`; choose a fresh output identity before another conversion, then verify before registration. Existing output directories are not overwritten. [3D result](../../Docs/Development/AssetWorkbenchV1/VIEWER3D_RESULT_20261011.md).

## Inventory expansion — 2026-10-11

229 asset/package records cover 125 animation archives, 53 weapon collections, 33 runtime audio cues and project characters, city, adapted and created equipment. Search 50,151 contained resource records in Contents; browse package children with pagination. Each asset has a registered preview and revision. Previews distinguish supplier images, embedded source thumbnails, historical UE captures, diagnostic Blender renders and actual WAV files. Smoke-canister imagery currently shows its deployed effect, not a canister close-up.

Formal/candidate/source-only/unregistered usage is explicit. New source references are verified against selector-pinned manifests; they do not claim a new runtime scan. The full importer is `import_inventory.py`; it hashes roughly 24 GiB of animation archives and the 2.36 GB weapon source, without extraction or source saves. UI refresh reads the generated registry, not arbitrary intake folders. Preserve ignored private media and rebuild frontend translations after a full inventory import.
