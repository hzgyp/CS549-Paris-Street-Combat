# Historical reference library — result

17 October 2026. Implemented the requested historical text/image library in the existing internal workbench at `/research`. Original research files and image bytes remain in their existing locations.

## Registered coverage

129 records: 45 source records, 42 image records, 27 research notes, 8 film/motion references and 7 weather records. Scope: 10 Paris records, 102 retained Normandy/background records and 17 equipment-research records. Supplemental S27–S39 entries in SOURCES.md are included, as well as the original service-shoe pictures that were absent from IMAGE_CATALOG.csv. Equipment research includes rifle/mine notes and both the medical-bag construction references and latest real-photo audit.

All 40 existing local research images in the Normandy image tree and four-photo rifle-original collection are registered. 39 have a recorded public-domain/CC0 basis and authenticated previews. One local Crown Copyright weather image and two Paris image-link records remain source links without served pixels. No additional source media was downloaded or rights inferred. Existing remote-only medical/mine photographs remain original links with their recorded inspection limitations.

Registered local HTML/PDF archive locations are shown with availability; this version searches research notes/registers/captions, not the complete contents of every archived PDF/HTML. Original source links remain available. Source text and original captions keep their existing language; UI labels and topic-keyword search support Chinese/English. Original historical images were not newly authenticated by this import.

## Behavior and integration

- Search text, captions, source/institution/place and bilingual topic keywords; filter scope/type. Read original notes and provenance/limitations. View bounded image previews, enlarge and open full-resolution originals.
- Global search includes assets, gameplay and historical references. Applicable rifle/mine records link to their asset pages, which also link back to research.
- Authenticated Refresh index reads the research registration, current CSV rows and Markdown in registered folders. Newly added notes in those folders and changed registered records are picked up without another command. New collections outside those roots require a registration entry.
- Refresh publishes SQLite plus asset-index.json, ASSET_DIRECTORY.md, GAMEPLAY_DIRECTORY.md and HISTORICAL_DIRECTORY.md within the existing rollback transaction. Source/image hashes and path/URL checks are enforced. Changed registered image bytes fail until their source registration is reviewed; prior snapshot remains active.
- Assets/ASSET_INDEX.md now points to the generated historical directory. CLI: `python Tools/AssetWorkbench/asset_index.py --research "急救包" --limit 5`.

## Verification and limits

Authenticated final-refresh receipt: `Assets/LocalWorking/AssetWorkbench/runs/history-library-20261017/refresh-result.json`. Readback: 230 assets, 17 gameplay entries, 129 research records; navigation index current, zero missing asset references. The service's existing loopback binding/port 8766 and private bootstrap link were retained during owned-service upgrades. No external reachability or sharing claim is made.

- Research and gameplay backend tests: 18 passed. Final research tests: 7 passed, covering authentication, text search, new-note discovery, permitted/restricted/missing images, original reads, tampering, unsafe URL/path/scope, supplemental sources and rollback after database failure.
- Broader backend run: 61 passed, 2 failed. Both failures are retained stale live-data assertions: `test_inventory_coverage_members_and_precise_usage` expects 229 rather than the existing 230 assets; `test_grenade_model_versions_and_current_formal_usage` expects the old v1 front cover instead of the accepted 17 October grip cover. No data was reverted to satisfy them; other historical expectations in those tests were not reached. This is not an all-suite pass.
- TypeScript/Vite build passed. Existing Three.js chunk-size warning remains.
- Two Playwright cases passed: Chinese body/topic search, scope/type filters, four museum-rifle pictures decoded, enlargement/Escape, original access, English navigation, global search into the medical-bag audit, source excerpt, 1280px horizontal fit, no page errors. Every one of the 39 permitted preview endpoints returned validated JPEG data; this is decoding/transport verification, not fresh visual acceptance of each historical caption.
- Screenshots retained under `runs/history-library-20261017/screenshots/`. Inspected the compact review sheet: gallery, photograph, medical audit and 1280px library. Full-resolution screenshots remain on disk. UI retains the existing muted internal style. The initial Chinese-query browser check failed before topic-keyword indexing was added; a greedy supplemental-source parser and an image-size test expectation were also corrected. Final checks cover those corrections.

No game/UE entry, compile, native asset save, model/texture edit, current selector/adoption change, original save write, Catalog change, cleanup, Git/SFTP publication or coursework delivery. No historical photo, old production note or marketing material becomes Paris gameplay evidence merely by appearing in this library. Medical-bag material acceptance remains separate.

Implementation and rollback: [work package](HISTORICAL_LIBRARY_IMPLEMENTATION_20261017.md). Preserve all original source/image records. A failed refresh retains the last valid database and complete navigation publication.
