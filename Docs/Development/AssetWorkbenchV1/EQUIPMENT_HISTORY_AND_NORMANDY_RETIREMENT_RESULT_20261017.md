# Equipment history and current library retirement — 17 October 2026

Implemented the requested equipment references and removed Normandy scenario material from the current platform. The platform retains 230 assets and 18 gameplay entries. History now has 67 records in two scopes: Paris and equipment. Explicit links cover 57 reference records, nine assets and thirteen gameplay entries, with 149 directional associations.

| Asset | Direct reference | Primary source | Gameplay |
| --- | --- | --- | --- |
| frag-grenade | Bilingual Mk II notes, original exterior figure, source record | War Department TM 9-1900, 3 July 1942, printed p37 Figure 12 A / PDF p38 | frag-throw |
| smoke-grenade | Bilingual AN-M8 notes, original exterior/container figure, source record | TM 9-1981, 8 December 1943, section 36 and printed p49 Figure 15 / PDF p52 | smoke-cover |
| ammo-box | Bilingual wooden packing-box comparison, original figure, source record | TM 9-1900, printed p34 Figure 11 / PDF p35 | finite-supply |

Each asset has three associated records: text, image and source. Images open inline and as authenticated original PNGs; primary-source links open the manual scans. Research pages link back to the asset and gameplay. Exact pages, original PDF/image SHA256, crops and rights are recorded in `HistoricalReference/Equipment1944/figure-provenance.json`. Two original PDFs remain local; no team-storage upload was performed.

The Mk II figure documents an early manual finish, not every grenade issued in August 1944. The smoke model is AN-M8-inspired. The Paris vendor's SM_AmmoBox_01a has no established historical box identity or contents; its reference is a qualified comparison. Existing models, accepted grips, inventory rules and gameplay were not changed.

## Current-library retirement

The previous 129-record research library was reconciled to 67 records: 56 stable records retained, 73 prior records removed from the current view, and 11 new/replacement records added. Two scenario production sheets were replaced by clean equipment notes. Shoe source S39 was replaced by independent museum source E03; both original CC0 images remain. Useful U.S./German/British uniform, rank, small-arms and shoe evidence remains equipment-scoped, including rank chronology and date limitations. No active Normandy background, beach, weather or landing-film category/record remains.

`Assets/Registry/library-scope.json` retires 33 exact file identities: 19 gunplay-scenario files (the beach browser raster and 18 Normandy-specific Unreal binaries), and 14 unused historical files. Five generic rifle source files and 24 useful historical files remain listed. Legacy CSV entries A05/A08 were retired; A03 now identifies readable scripts rather than current binary candidates. Original immutable Catalog/manifests, source folders, bytes, licenses, old snapshots and previously published resources remain recovery/provenance archives.

All 230 prior Paris asset IDs remain. The importer rejects retirement of a registered asset bundle, model, media, current source or research input; changed or missing exact manifest identities are rejected. Invalid selection keys/disallowed scopes fail before publication, preserving the previous snapshot/index. The generated navigation index includes the scope policy and fingerprint. Platform Refresh synchronizes curation and associations without a manual command.

The 17 active storage manifests declare no dependency on the retired scenario bundle. The selected pending 128-file source was audited through its 92 relevant text files; no selected Normandy/Battlefield01/BrowserPrototype/RifleHero reference was found. This is source/storage evidence, not a new runtime or full binary dependency test. No Game/Editor build, native edit, save operation, asset adoption, remote transfer or coursework delivery was performed.

## Verification and recovery

- Frontend TypeScript/Vite build passed; the existing Three.js bundle-size warning remains.
- Focused backend tests: 30 passed, including exact curation, rights/media, association consistency, protected-file rejection and failed-refresh preservation.
- Chrome Playwright: six passed. Verified the three equipment pages, original bytes, zoom, bilingual controls, reverse gameplay links, retained references, retired file exclusion and every permitted research-preview endpoint.
- Initial gallery test waited for offscreen lazy images and timed out. The test now scrolls each image into view before decoding. The failed report/screenshot/context remain retained; the complete rerun passed. No image-serving workaround was needed.
- Authenticated Refresh/readback snapshot `12a3cc0d66e34b83ab7218c0f1c4e15e`, job `388420909a214bf5ab3430232dff0a39`: counts, reverse links, three exact original images and retired file absence matched API/index. Index check: 230 unique assets, zero missing references.
- The bounded 34-file guard for Catalog/manifests, asset inputs and selectors remained exact. Six actual UI views were inspected in a 105,906-byte JPEG contact sheet; full-resolution originals remain. Figure crops were checked separately against the manual pages. This verifies platform presentation, not new game or historical-model acceptance.

Evidence: `Assets/LocalWorking/AssetWorkbench/runs/equipment-history-retirement-20261017/`. Receipts include `migration.json`, `refresh-result.json`, `backend-results.xml`, `ui-results.json`, `selected-source-audit.json`, `bundle-dependency-audit.json`, `preservation-before.json`, `registry-change-receipt.json`, `ui-contact.jpg` and exact pre-edit copies in `recovery/`. The initial 64-record curation and failed UI attempt remain separate. Rollback is limited to these active registration/document edits followed by authenticated Refresh; preserve all archives and unrelated work.

Shared-file coordination: this task intentionally added the `library_scope` key to `Assets/Registry/registry.json`. The exact before/after hashes and semantic diff are in `registry-change-receipt.json`; this explains that file's concurrent change reported by the independent medkit surface-stain work. Its preservation report is not overwritten or converted to a blanket pass. Its new handoff entry was preserved when adding this result.

中文复核：三类装备均可直接查看文字、图片、来源及对应玩法；当前历史资料67条、关联资产9项。诺曼底专用背景和33个专用文件已退出当前目录，通用装备资料、5个步枪源文件及230项巴黎资产保留。原始归档、清单和恢复副本保留；本次没有修改游戏或上传文件。
