# G1 HUD playtest — verified private sharing and source publication

9 October 2026. [Chinese review](G1_PLAYTEST_PUBLICATION_RESULT_20261009_ZH.md).
Follow the [implementation and stopping gates](G1_PLAYTEST_PUBLICATION_20261009.md).

## Delivered version

Private release: `paris-g1-playtest-20261009-hud-v3`.
SFTP download: `/releases/paris-g1-playtest-20261009-hud-v3/Paris-G1-HUD-20261009.zip`.
Download the entire ZIP, extract all files, then run `PLAY_G1_REVISION.cmd`.
The package includes English/Chinese controls and distribution readmes, original
HUD receipt, Cinzel OFL/provenance and UE-bundled `vc_redist.x64.exe` if needed.
No user checkpoint, generated log or connection secret is included. Authorized
recipients remain Yupu Guo, Yuqi Pu and Jingdi Wu for this project privately.

ZIP: **8,474,979,819 bytes**,54 members, SHA256
`5c8184c58f7a79ca30a669f99f017df79a04377acc027354607c6bb98452f968`.
Executable SHA256 remains
`497221422d7754d562b4e6d11fd8cc50c9223e40b329b26c8c14391a98d1c42b`.
47 runtime files authenticate against the original HUD delivery; the already
recorded debug-message launcher override is honored. Three original handoff
files plus four distribution/prerequisite/source-identity sidecars make54.
No game compilation, cook or launch occurred during publication.

## Actual storage verification

Every ZIP member was read in full and compared by size/SHA256. The immutable
hash object and release manifest were downloaded via pinned-host authenticated
SFTP and fully compared. The named ZIP uses a successful authenticated SFTP
hard-link operation to that object, avoiding a second remote archive copy; this
named entry was separately downloaded in full and SHA256/size checked. Both
download guides were uploaded and authenticated read back. Shared-account
create/overwrite/rename/get/delete passed on this release's own probe only.
Protected root ACL is unchanged; existing versions and three user trials remain.
Only this task's fully verified transfer samples were removed.

`Assets/Sync/CATALOG.json` adds independent `paris-g1-packaged-playtest`.
Manifest SHA256:
`05d493106c50d32121b24685429ff1807447f0a4473834d218b68b389af1f305`.
Existing city/native/model selections remain exact. Catalog metadata alone
advances44655b8c… to590e2567… through an explicit9October proof and mutable epoch
ledger retaining the original anchor and8October selected hash. Post-selection
703 guards pass at that authorized epoch; 758 canonical source rows remain exact.
Source/native files are not rebased or adopted by this separate playable share.

Initial PowerShell5 ACL read failed to autoload its Security module before any
publication directory was created. The established bundled PowerShell7 passes
the same process/ACL gate. A local-shell hard-link request was denied before
alias creation; the authorized SFTP shared account successfully performs it.
No permissions were weakened. Private preflight-corrections.json and transport
logs retain these distinctions; no failed native/game route was replayed.

## Source and verification scope

This Git revision carries accumulated closeout/playtest/HUD source tools, matching
plans/results, MI002–MI013 failure records and completed storage-cleanup tools.
The exact40-file tested source snapshot is
`Unreal/Variants/G1HUDPlaytest20261009/Project`, authenticated by its
`SOURCE_MANIFEST.json`. Exact-byte Git attributes preserve the snapshot, Catalog,
manifest and authorization proof on checkout. The formal project and its selected
758-file source contract remain at their existing native release. For direct
play, use the new packaged ZIP. Rebuilding the variant additionally requires
entitled private action/native dependencies; a source clone alone is not the city
or a verified clean Editor rebuild. See the variant README.

31 new Python scripts and10 PowerShell scripts parse without errors; these checks
do not execute stopped trials or cleanup. Publication uses the existing staged
asset/manifest hook and outgoing ancestry guard; remote main is independently
checked after push. Its actual commit identity is recorded in the private
publication receipt/final user handoff rather than embedded in its own Git tree.
Commercial/native/raster/document/archive bytes and credentials stay outside Git.

Previously observed HUD1080p/720p, legitimate three-death/consent/save/fresh-load/
restart checks remain attributed to hud_v3; prior movement/obstruction passes to
V10. No new runtime/performance/video/human/second-machine/course pass follows.
External forwarding and teammate execution remain untested here. Publication
does not imply whole MVP completion. MI002/006/010/011/012/013 lessons were read;
no broad cook, body-centre nav preflight, failed recorder or composite-only text
route was reopened. Private `tmp/paris-g1-playtest-20261009-hud-v3` retains package,
per-member receipt, transport logs and exact verification/publication records.
