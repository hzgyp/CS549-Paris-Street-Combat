# Illustrated homepage modules — installed result

17 October 2026. The local Asset Workbench homepage now separates **Gameplay release, Actions, Characters, Scenes and maps, Equipment and props**. It retains the existing visual style and Chinese/English switch. The current tutorial 1.0 has its own illustrated release panel; older releases, trials and source builds remain in a collapsed archive and the existing build pages. No build is treated as current merely because its channel is formal.

## Installed behavior

- One current gameplay release, two scoped action cards, two character cards, one Paris scene card and five equipment/prop cards. Category and asset-library links keep the full 231-asset library available.
- Eleven registered pictures: matching-Game tutorial capture, accepted grip captures, actual Ctrl crouch frame, native character previews, actual Paris scene capture and model/runtime prop previews. Image labels distinguish capture types; no supplier advertising or generated illustrations were added.
- Action cards link to the exact adopted comparison or the asset's version tab. Models keep their own detail/3D pages. “Current adopted”, “In current release” and “Registered” remain distinct states derived from existing adoption and usage records.
- Snapshot refresh resolves explicit IDs, validates category/asset/revision/media relationships and preserves atomic publication. The formal preview checks its original capture record, Game identity, SHA256 and size. A future different formal Game displays an explicit missing-preview state until its corresponding image is registered.
- Module navigation wraps on narrow screens; the retained-build list starts collapsed. Missing images have a visible fallback. Link modifier keys retain normal browser behavior.

Configuration: `Assets/Registry/mappings/homepage.json`. Backend resolution: `Tools/AssetWorkbench/app/homepage.py`; integrated into catalog collection and overview API. Frontend: `Tools/AssetWorkbench/frontend/src/HomeOverview.tsx` and `homeOverview.css`. Structured navigation index includes homepage configuration and exact cover identities through the existing authenticated Refresh flow.

## Verification and evidence

Evidence directory: `Assets/LocalWorking/AssetWorkbench/runs/home-modules-20261017`.

- `BACKEND_TESTS.txt`: **20 passed**, including invalid/cross-asset references, scoped action adoption, stale formal preview, invalid provenance, failed-refresh preservation, original cover identities and existing local/shared access contracts. Live-source tests use temporary databases and suppress writes to the owner's navigation index.
- `BUILD.txt`: TypeScript and production build passed. Existing Three.js chunk-size warning remains.
- `BROWSER_TESTS.txt`: **3 passed** on the installed service. All 11 images decode; five modules and current formal identity are correct; archive collapses; action/model/build/gameplay routes work; English and 1920/1366/640/390-width layouts pass; missing formal preview is explicit.
- `REFRESH_JOB.json`, `FINAL_READBACK.json`: authenticated refresh succeeded; snapshot `e445d93addc54766b1ef440b7fdf16ea`. Readback confirms 231 assets, 18 gameplay designs, 67 research records, 20 bundles and 19,009 indexed files. All 11 homepage cover identities match the refreshed structured index. `INDEX_CHECK.txt`: index current, zero missing references.
- `PAGE_QA.jpg` and `ACTION_CHARACTER_QA.jpg`: small contact sheets visually inspected for desktop, English narrow layout, action, character and prop modules. Original screenshots are retained in `screenshots/`; asset originals remain unchanged at their existing paths. This is homepage visual QA, not a new model/game acceptance.
- `PRESERVATION.json`: all **2,376** existing media records are unchanged; one local-only genuine release capture registration was appended. Existing registry fields are unchanged; only `homepage` was added. The original image SHA256 is `b7a89e6d7ad7c5c1ef017bc87d69fe14f3a7fa359ed5ffa576fcdca544fea948`, Game `3bb90f646cbbfb3652bab5fcab23c0af2b3bd2d7add577028e6810a9c5576967`.

Retained attempts: the first browser run caught inherited global navigation/definition-list styles and 390px toolbar overflow; scoped homepage CSS fixes them. The second run exposed a test interceptor missing the snapshot query suffix; its glob was corrected. Logs/contact evidence are retained. Initial backend test-authoring errors used a non-generated fixture path and an incorrect prop ID; corrected tests now pass. No production asset data was altered to satisfy tests.

## Preservation and review entry

The owned idle platform service was reloaded with its existing loopback binding, port and private access-link identity. No network/authentication policy, authority selector, gameplay/model/native/vendor/save data, Catalog, remote storage or Git publication was changed by this package. Concurrent NPC/local-access work remains in place. Local review: `http://127.0.0.1:8766/`.

Targeted preimages and the pre-task Git state are retained under this run's `recovery/` and `GIT_BEFORE.txt`. Rollback must reverse only this package's fields/hunks; do not restore entire shared files or indexes over later work. The asset-index code change has no pre-task whole-file copy, so use its narrow homepage additions rather than a wholesale restore. Refresh atomically after any authorized reversal. No intermediate asset deletion, new Game build, deployment or coursework delivery occurred.
