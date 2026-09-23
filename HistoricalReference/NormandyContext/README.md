# Normandy Historical Reference Library

**Adaptive Normandy Battlefield Simulation · Research baseline · 17 September 2026**

Working scenario: **6 June 1944, the American Omaha Beach landings**. The team has not yet locked a beach subsector, company, landing wave, or precise playable time interval. This library supports those decisions; it does not certify the existing concept art or browser scene as a reconstruction.

The [Assignment 2 proposal](../Docs/proposal/CS549_Normandy_Assignment2_Proposal.md) defines the current gameplay scope and a fixed coastal lighting condition. Weather-progression examples in this library are retained research notes, not required MVP or current semester features. Evidence dates and uncertainty remain unchanged by this planning update.

## Start here

| Review | File | Purpose |
|---|---|---|
| 1 | [Scenario and accuracy rules](01_SCOPE_AND_ACCURACY.md) | Decide which place, unit and time the game represents |
| 2 | [Uniforms and ranks](02_UNIFORMS_AND_RANKS.md) | Distinguish nation, branch, rank and combat role |
| 3 | [Weapons and ammunition](03_WEAPONS_AND_AMMUNITION.md) | Choose correct visible shapes and animation behavior |
| 4 | [Vehicles and aircraft](04_VEHICLES_AND_AIRCRAFT.md) | Prevent variant, marking and deployment errors |
| 5 | [Weather evidence](05_WEATHER_EVIDENCE.md) | Read documented values with their actual spatial/time limits |
| 6 | [Blueprint implementation specification](06_BLUEPRINT_SPECIFICATION.md) | Convert evidence into explainable, bounded systems |
| 7 | [Historical review gates](07_REVIEW_GATES.md) | Approve assets before detailed production |
| 8 | [Asset production references](08_ASSET_PRODUCTION_REFERENCES.md) | Craft construction, shingle scale and material candidates for the first asset kit |
| 9 | [Landing performance references](09_LANDING_PERFORMANCE_REFERENCES.md) | Film/game observation samples, historical movement constraints and the new action script |
| Browse | [Image gallery](IMAGE_GALLERY.md) / [offline visual browser](gallery.html) | 34 local images with dates, provenance and limitations |
| Audit | [Sources](SOURCES.md) / [weather evidence CSV](data/weather_evidence.csv) | Inspect evidence and unresolved fields |
| Machine | [Primary workstation](../Development/PRIMARY_WORKSTATION.md) | Hardware, storage and first performance lab |

## Collection coverage

The local archive contains five PDFs: the U.S. Army uniform survey, the German forces handbook, the 1942 75-mm tank-gun manual, the Met Office D-Day factsheet and the contemporary 13 UTC weather chart. Thirty-four images cover uniforms, ranks, weapons/ammunition, terrain, Allied/German vehicle and aircraft recognition references, and the chart. Some are complete pages rendered from originals, not newly drawn historical illustrations. The 21 September supplement adds source records S27–S31, five archived pages, one NARA photograph and a small CC0 material sample; modern production materials are not historical evidence.

U.S. and German infantry receive the detailed treatment needed for Omaha. British recognition material and museum references are kept separately. Canadian and other Allied contingents are contextual references, not a completed model sheet for every nation. Adding them to the playable force requires additional dated, unit-specific research.

Every downloaded picture is reference material, not automatically a distributable game texture or approved 3D model. The catalogs retain attribution and rights notes. The 1945 German manual is intentionally marked as later than the scenario. Archival captions and original-language labels are retained; all new project writing is English.

## Evidence vocabulary

- **Period observation:** a report or image with an identified date/place; it can still contain errors.
- **Official retrospective account:** an institutional reconstruction of events, not a raw instrument log.
- **Period/general reference:** establishes an item's form; does not establish its presence in this encounter.
- **Modern reconstruction:** a numerical hindcast, museum reconstruction, or researched interpretation.
- **Design approximation:** a team-selected visual/gameplay value, clearly separated from evidence.
- **Unknown:** not established in this collection. A blank value is never zero.

The archive is approximately 135 MiB including reference images. Review binary storage before any future commit; no Git LFS policy or automatic push is introduced by this package.
