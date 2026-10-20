# Historical reference library — implementation

17 October 2026. Authorized scope: organize previously researched historical text and images in the internal asset platform. No new acquisition, coursework delivery, game build, asset adoption or publication.

## Inputs and prerequisites

Read HANDOFF_CURRENT, Assets/ASSET_INDEX, HistoricalReference/README, Paris1944 registers/context/gaps, NormandyContext/AGENTS and source/image/motion registers, equipment reference notes and the 17 October medical-bag source audit. Preserve originals and other sessions' modified files. Paris is the current setting; Normandy production instructions are inactive reference material.

Failures reviewed: Failures/README and FP001's distinction between numeric success and actual visual review. The medical-bag audit records a specimen-label mismatch and an unsuccessful PDF screenshot: collection metadata and visible specimen attribution must remain separate; a registered image does not prove new visual inspection. Existing gallery captions warn about captured aircraft, post-event photos, late manuals and Crown Copyright. Preserve these qualifications.

## Work package

- Add a read-only Historical references section, Chinese/English navigation, search of original text/captions, scope/type filters, image previews, source links, rights, dates, location and limitations. Source text retains its original language.
- Register Paris source/image CSVs, all historical research notes and Normandy source/image/motion/weather registers, plus existing equipment research notes and the latest medical-bag audit. Keep legacy implementation/production notes explicitly inactive. Include the four existing CC0 Paris museum rifle photographs with the credited collection and specimen caveats.
- Refresh reads the registered collections directly, so new CSV rows, changed notes and new Markdown in registered research folders are picked up by the existing authenticated Refresh index action. No background network crawling or manual import command.
- Permit media only from registered paths with recorded public-domain/CC0 basis. Rights unresolved or restricted: searchable record and original source link, no image redistribution. Missing local bytes remain visible as unavailable records. Preserve full-resolution originals; use a bounded derived image response for UI viewing.
- Publish research records and a generated HISTORICAL_DIRECTORY alongside the existing asset/gameplay navigation files and database snapshot under the existing rollback transaction. Include source/image hashes and source fingerprints. Link applicable records back to existing assets; no asset version/status changes.

## Sequence and acceptance

1. Implement validated bounded importer and registration. Reject traversal, unsafe URLs, duplicate identities, invalid scopes and unregistered media.
2. Wire API, index publication and bilingual UI. Retain authentication, CSRF, Host and Origin checks.
3. Verify temporary-fixture refresh, changed sources, missing/restricted images, tampering, authentication and rollback; run existing backend contracts and frontend build.
4. Inspect the owned workbench service, preserve its access link during upgrade, use authenticated Refresh index, read back counts/hashes. Browser-check filters, text, actual image decoding and both languages; save bounded screenshots and inspect them.

Stop on source races, invalid rights/path/schema or index publication failure; the last valid snapshot remains active. Record actual imported counts and verification limits in the result. No UE/editor/game entry or runtime acceptance claimed.

## Storage and rollback

New source: Tools/AssetWorkbench/app/research.py, frontend Research.tsx, tests and Assets/Registry/research/library.json. Derived output: Assets/Registry/HISTORICAL_DIRECTORY.md and research fields in asset-index.json; SQLite remains local. Originals stay in their current homes. No Catalog/native/vendor/save changes. Rollback restores only this package's code and registry key; existing refresh transaction restores all navigation outputs on failure. Retain results/evidence; no cleanup authority.
