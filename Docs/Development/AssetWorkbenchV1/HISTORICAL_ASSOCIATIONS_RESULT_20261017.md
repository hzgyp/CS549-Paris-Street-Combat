# Historical associations result — 17 October 2026

Implemented in the local Asset Workbench. Asset and gameplay details now show reference text excerpts, image previews where registered rights permit, external source links, original-language text and bilingual association purpose. Reference pages navigate back to the corresponding assets and gameplay. Image previews support enlargement and original-image links; longer material opens the complete reference record.

The explicit register contains 15 groups, 48 distinct research records and 130 directional associations across 6 assets and 10 gameplay entries. The library retains all 129 records. The platform now has 230 assets and 18 gameplay entries; the additional entry registers the existing finite medical-kit design as unimplemented, without adopting/registering its candidate model.

| Asset | Associated records |
| --- | ---: |
| Paris city | 8 |
| Allied soldier | 14 |
| German soldier | 8 |
| First-person arms/rifle | 12 |
| German rifle | 17 |
| Pressure mine | 1 |

Gameplay associations cover G1, its tutorial, M2/M3, post-bridge and A/B bridge routes, Allied recruitment, rifle resources, enemy mines and the finite medical-kit design. Counts overlap because the same evidence can serve multiple explicitly explained uses.

Paris city and route links are context/comparison, not proof of a historical reconstruction. The purchased paratrooper is not identified as 4th Infantry Division by the Paris sources. The 1945 German handbook remains a qualified late-war comparison. Museum rifle photos retain the missing rod/hood and replacement British sling caveats. The mine's personnel trigger remains a game abstraction. Unrelated Normandy weather, landing footage and vehicle research remain searchable without invented Paris associations. Other assets display an explicit absence of registered corresponding research rather than fabricated provenance. The two Paris image records remain source-link-only because display rights were not established.

Maintenance: edit Assets/Registry/research/associations.json using exact register/key selectors, stable asset/gameplay IDs, relation type and Chinese/English purpose. Existing per-note asset links were migrated into this single explicit register. Platform Refresh index validates every selector and target, rereads changes and publishes the SQLite snapshot plus JSON/asset/gameplay/historical navigation outputs together. Invalid links, duplicate edges, missing bilingual text and source changes fail before publication; the prior snapshot/index remain available. No manual index command is required for synchronization.

Validation completed:

- Focused backend research/gameplay/association tests: 26 passed. Covers inline text/source/purpose, reverse consistency, target/selector rejection, duplicate rejection, immutable snapshot reads and all-four-output rollback.
- Frontend TypeScript/Vite build passed. Existing Three.js model-viewer size warning remains.
- Chrome Playwright research and association checks: 4 passed. Covers direct asset images/text/source links, zoom/original links, forward/reverse gameplay navigation, medical unimplemented status, bilingual UI, Paris image rights, weather separation, 1280px layout and all 39 permitted preview endpoints.
- Authenticated platform Refresh succeeded. Every one of the 130 association edges was read back in both directions in the same snapshot; navigation counts matched the API. Asset index check reported 230 unique assets, no missing references.
- Inspected the five-view JPEG contact sheet (142,181 bytes) for 1920/1280 layout; originals remain on disk. The contact review establishes layout only, not new historical/asset/game acceptance.

Evidence: Assets/LocalWorking/AssetWorkbench/runs/history-associations-20261017/refresh-result.json, ui-results.json, screenshots/ and retained registration/verification scripts. The latest refresh receipt is the snapshot authority for this package.

No UE/editor/game build, native/model/save changes, asset adoption, Git/SFTP publication or coursework delivery was performed. Original research text/images and unrelated work were preserved. Existing service binding and access-link identity were retained.
