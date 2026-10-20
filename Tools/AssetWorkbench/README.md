# Paris Asset Workbench V1

18 October obstacle cover and maneuver: Allies use actual wall/obstacle hide-and-peek geometry and alternate covering/advancing after physical arrival. A German observer holds contact while squadmates take opposite reachable flanks; losing observers ends live flanking and starts separate finite search sectors. Map/tree/history show each assignment, cover blocker and readiness reason. The session-local tactical switch compares the former basic roles.124 backend,43 client and66 original-entry browser checks pass on the human-started8766 platform; protected data and saved browser layouts remain intact. Human tactical acceptance is pending; no UE. [Current result](../../Docs/Development/NPCAIMapMainV1/COVER_MANEUVER_RESULT_20261018.md). Previous [squad result](../../Docs/Development/NPCAIMapMainV1/SQUAD_RESULT_20261018.md) is retained.

18 October recorded German search: the native `/npc-simulation` route links private last-observation identity/time, frozen origin, actual requested/admitted search-point order and simulation-time countdown to the executing tree. Historical review uses the displayed prefix; skipped nodes, hearing events, advancement without arrival and renewed sight remain distinct. Frontend-only installation preserves the running service and rounds.35 client/79 installed-browser checks pass. See `Docs/Development/NPCAIMapMainV1/SEARCH_RESULT_20261018.md` for evidence and abstract-raster limits; no UE connection.

Internal, read-only asset catalog for Paris Street Combat. [中文说明](README_ZH.md). [Implementation result](../../Docs/Development/AssetWorkbenchV1/IMPLEMENTATION_RESULT_20261011.md).

Historical references: `/research` searches existing research text, source registers, image captions, institutions and places, including Chinese topic keywords. Filter Paris, retained Normandy background or equipment research. Images retain source credit, date, rights and limitations; permitted originals have a bounded preview and original-image link. Restricted/unresolved images remain source links. Original text keeps its source language. Global search includes assets, gameplay and references.

The existing authenticated **Refresh index** re-reads `Assets/Registry/research/library.json`, its CSV registers and Markdown folders, then atomically publishes the database and all navigation directories. Register new research in those sources; no separate import command. [Historical directory](../../Assets/Registry/HISTORICAL_DIRECTORY.md). Local lookup: `python Tools/AssetWorkbench/asset_index.py --research "canvas" --limit 5`. Source clones need reference image restoration; this feature does not change rights, asset adoption, game versions or storage publication.

12 October source-publication scope: [the functional Git publication record](../../Docs/Development/GIT_FUNCTIONAL_PUBLICATION_20261012_ZH.md) covers this application's code, tools and documentation. Private media, models, animation caches, runtime configuration and authenticated sharing links remain excluded. Historical implementation results retain their dated validation limits.

Use **中文 / English** in the header to switch language. The browser remembers the selection; filters, revisions and the active template remain selected. Copied/downloaded templates use the selected language. Source excerpts retain their original language. [Bilingual update](../../Docs/Development/AssetWorkbenchV1/BILINGUAL_IMPLEMENTATION_20261011.md).

13 October update: the asset catalog follows adopted sleeve baseline 78. **Gameplay design** (`/gameplay`) contains 14 bilingual records for current rules, G1 tutorial, M2/M3, post-bridge sites and A/B route validation. Details link to assets, 3D previews, builds and original documents. Design, implementation and validation states are separate; proposals and failed fixed routes retain those states. [Implementation](../../Docs/Development/AssetWorkbenchV1/GAMEPLAY_INTEGRATION_IMPLEMENTATION_20261013_ZH.md).

Register gameplay navigation in `Assets/Registry/gameplay/designs.json`; retain the original design documents. **Refresh index** updates the SQLite snapshot, JSON index, asset directory and gameplay directory together. Changed source documents flag summaries for review. No separate index command is needed. For an owned service code upgrade, `run.ps1 -NoBrowser -KeepAccessLink` retains the existing complete sharing link. After restart, local-only pages automatically establish a new session; shared-mode browsers must reopen their authenticated link.

## Start

From the project root in PowerShell:

```powershell
./Tools/AssetWorkbench/run.ps1
```

The launcher reuses its own running service or starts a hidden Python service and opens an authenticated browser session. The default port is 8765. This workstation uses 8766 because another service already owns 8765. The local setting is `Assets/LocalWorking/AssetWorkbench/config.local.json`, containing `{"port":8766}`. Use `-Port 8767` to choose another free port; do not terminate an unrelated listener. `-NoBrowser` starts/reuses the service without opening a browser.

17 October local access: when bound to `127.0.0.1`, open `http://127.0.0.1:8766/` or `/npc-simulation` directly without a token. The page automatically creates/reuses its browser session. Host, same-origin, CSRF and private NPC-world ownership checks remain. Shared mode still requires the authenticated launch/sharing link, including on loopback. [Local-access result](../../Docs/Development/AssetWorkbenchV1/LOCAL_ACCESS_RESULT_20261017.md).

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
# Historical associations — 17 October 2026

Asset and gameplay detail pages show historical excerpts, permitted image previews, original sources and bilingual association purpose. Research records link back to both target types. Maintain exact `register`/`key` selectors and asset/gameplay IDs in `Assets/Registry/research/associations.json`; do not infer associations from keywords. Each edge needs a relation type and Chinese/English explanation. Platform **Refresh index** validates and synchronizes associations with the snapshot and all navigation files; failed refresh preserves the previous publication. Sources remain qualified evidence, not asset adoption or runtime acceptance. See `Docs/Development/AssetWorkbenchV1/HISTORICAL_ASSOCIATIONS_RESULT_20261017.md` for verified scope and evidence.


## Live 2D NPC interactions

18 October installed sight diagnostics: selecting a German links the sampled player ray and three ordered gates (distance, off-axis angle, occlusion) to its tree-time evidence. Clear rays are green; unevaluated occlusion uses an amber dashed reference; blocked rays mark the exact first black cell/entry point in red. Skipped gates/nodes stay distinct from failures. Numeric distance/half-FOV, sensing time, and visible-hostile IDs explain why the any-hostile tree condition can pass while the player remains hidden. History restores its own sample, independent of smooth actor animation. The reviewed workspace is installed at the original8766 entry after the human retired the prior process. All65 installed browser checks pass; index/config/Catalog/tutorial selectors and access identity remain exact. Candidate/failed evidence is preserved. This is abstract raster evidence, not measured UE sight. [Sight result](../../Docs/Development/NPCAIMapMainV1/SIGHT_RESULT_20261018.md).

18 October node/map evidence: click an evaluated tree node to highlight its recorded desired/admitted formation slot, jointly assigned support point and scored/rejected candidates, requested/actual move goal, or frozen search origin and current offset envelope. The explanation below the graph shows the actual predicate values and Success/Failure/Skipped distinction; skipped branches never borrow another branch's target. Target focus is view-only; explicit focus from fullscreen retains the inspected node. Historical evidence stays synchronized. Final49 browser checks /18 client checks pass; installed maximum-vision paint P95 is16.9ms. Backend and service remain unchanged. [Node/map result](../../Docs/Development/NPCAIMapMainV1/NODE_MAP_RESULT_20261018.md).

18 October linked workspace: one parameter bar above a left map/right executing tree. NPC selection links both views; moving the player retains the observed NPC, its cone and search memory. The actual action/ancestor branch stays visible with automatic tracking; manual graph inspection suspends tracking, and Focus resumes it. Fullscreen return restores readable tracking. Desktop layouts through 900 px remain side by side; below 700 px map/tree switch in place. Installed22 linked/8 playback checks and isolated maximum-vision paint p9516.9ms pass. Frontend-only installation preserves the running service and episodes. [Linked-workspace result](../../Docs/Development/NPCAIMapMainV1/LINKED_WORKSPACE_RESULT_20261018.md).

18 October tuning: edit follow distance, German range/FOV, sight-loss grace and maximum search time in the shared parameter bar; apply to the current episode without resetting time/position/memory. Map shading and actual decisions use the values. Review retains historical settings; layouts save applied tuning and old layouts use defaults. Fullscreen editing and continuous playback remain available. [Parameter result](../../Docs/Development/NPCAIMapMainV1/PARAMETERS_RESULT_20261018.md).

17 October map/tree update: hold/drag the background to pan during playback or review; a short click still walks/places and a character drag still places. The integrated connected behavior-tree graph uses the exact executing server definitions, with per-NPC conditions/actions/statuses, node inspection, blackboard and historical traces. Move success requires actual arrival; failed paths and finite recovery remain explicit. [Behavior-tree and gesture result](../../Docs/Development/NPCAIMapMainV1/BEHAVIOR_TREE_RESULT_20261017.md).

17 October display fix: recorded0.1s physics poses animate continuously with requestAnimationFrame between the existing0.5s responses. Pause/review/reset cancel presentation; no extrapolation or path-corner shortcut. Installed local measurement: median16.7ms between paints, drawing p950.4ms. [Continuous-display result](../../Docs/Development/NPCAIMapMainV1/SMOOTH_DISPLAY_RESULT_20261017.md).

The **NPC interactions** sidebar opens native `/npc-simulation`: click-to-walk, validated drag placement, actual Allied following and distinct Support/Overwatch, German sight/lost-sight finite search and return, paths/private memories/arrival, timeline and local layout notes. It reuses platform authentication; navigation away pauses computation. Three presets run finite120s episodes. The audited Paris black/white bounded-expanded L0 raster is the main scene (180x240m): white admits abstract 2D navigation/sight, black including unknown blocks; a conservative footprint mask and bounded A* determine actual paths. Full-map/squad-focus, pan/zoom and authored headings are available. Saved layouts pin raster identity. Other surface ordinals are not merged or treated as floors. No UE or health/ammo transactions. The API is local-owner only (not shared-network mode). Saved layouts survive service restart; in-memory worlds/cookies do not. [Result and evidence](../../Docs/Development/NPCAIMapMainV1/RESULT_20261017.md).
