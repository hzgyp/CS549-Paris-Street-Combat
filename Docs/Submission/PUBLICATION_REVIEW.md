# GitHub Public Visibility Review

Updated 30 September 2026. The user explicitly authorized migrating permitted asset/history bytes to private SFTP, removing the bytes and their Git history from this same repository, keeping code/docs/config/hash records, and making it public only after matching verification. This supersedes the earlier proposal for a separate public repository. Actual final status is recorded in `Assets/Sync/PUBLICATION_STATUS.json` once remote verification finishes; do not infer public visibility from authorization.

## Concrete unresolved content

Before migration, all 20 files in the old historical mirror's `excluded_files` were in `origin/main`, including initial Git history. The migration plan removes those bytes, other historical/model bytes and document/raster binaries from reachable source history. It preserves local originals and the existing private Git/LFS backup. These 20 items and two unchanged supplier showcase JPEGs remain local-only with source links and SHA-256/size records, not in the private SFTP shared set.

The current permitted non-city release contains 77 files: 38 historical assets, 24 retained team gunplay assets and 15 project/course document or generated-image files. Current city bytes are fully compared with the selected SFTP baseline/objects; only changed files need new objects. `Assets/Sync/CATALOG.json` selects exact verified active manifests. Old historical mirror records are provenance only.

The checked sensitive local directories `Docs/Submission/LocalEvidence`, `Assets/LocalShared` and `Assets/LocalWorking` were not found in the tracked history for those paths. The raw France Liberation city remains excluded from the current Git tree; retained team-authored gunplay reference assets are separate from the vendor city. This is a bounded content review, not a comprehensive legal or secret audit.

## Files with unresolved redistribution records

Paths below are relative to `HistoricalReference/NormandyContext/` and exactly match the published historical manifest's exclusions:

- `archive/metoffice_19440606_1300utc.pdf`
- `archive/metoffice_dday_factsheet.pdf`
- `archive/metadata/coast_sand_01_files.json`
- `archive/metadata/pebbles_files.json`
- `archive/metadata/pebbles_info.json`
- `archive/pages/british_uniform.html`
- `archive/pages/fw190.html`
- `archive/pages/nara_into_jaws_of_death.html`
- `archive/pages/omaha2.html`
- `archive/pages/omaha3.html`
- `archive/pages/plane.html`
- `archive/pages/pocketguide_links.json`
- `archive/pages/polyhaven_coast_sand_01.html`
- `archive/pages/polyhaven_coast_sand_rocks_02.html`
- `archive/pages/polyhaven_sand_rocks_small_01.html`
- `archive/pages/S24.html`
- `archive/pages/S25.html`
- `archive/pages/tank.html`
- `archive/pages/ww2museum_lcvp_lcm.html`
- `images/weather/metoffice_19440606_1300utc.png`

Unresolved is not a claim that every item is prohibited. Public-domain or open-license material may be publishable once item-specific rights and any applicable attribution are verified. The private three-member city-sharing attestation does not establish public redistribution rights for these historical files.

## Verification and teammate recovery

The user's latest request is explicit migration/history-rewrite authorization. Prepare in an isolated clone, preserve private Git/LFS and current source/asset backups, verify SFTP source/final bytes, then publish only matching manifests/source using an expected-old-head force lease. Check fresh remote refs/history and current tree. Local originals are kept and ignored, not deleted. Python source checks and local pre-commit/pre-push guards prevent reintroducing asset/LFS bytes. The active catalog is the only current restoration authority.

Teammates must preserve unfinished code and ignored assets, clone the rewritten repository into a new sibling folder, restore required private SFTP versions, configure guards and reapply reviewed source edits as new commits. Do not merge/push old asset-bearing history. See `Assets/TEAM_SYNC_WORKFLOW.md` section 8. No teammate messages are sent automatically.

## GitHub retention check before public visibility

Actual result, 30 September 2026 at 21:18 EDT: cleaned `main` was pushed as `f904daa88cf43b1f4f51459ad1635522948e4d23` with a lease against the expected original head. A fresh GitHub clone passed active-catalog hashes and source/history checks; its source pack is 2.66 MiB. A bounded scan of 213 blob/commit objects found no common credential signatures, scoped private paths, NUL binaries or LFS pointers. This is not a comprehensive secret/legal audit. All 15,927 selected SFTP files (28,582,935,268 bytes) were source/server hash-verified; no city files changed. Local originals remain intact.

**Publication is blocked by verified GitHub retention, not missing visibility authorization.** The old initial commit and removed historical HTML blob both still return HTTP 200; the downloaded blob matches its original Git object identity. GitHub LFS also offered and served a removed 1,434-byte object whose SHA-256 matches the privately backed-up original. The repository remains private. [GitHub's LFS removal guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/removing-files-from-git-large-file-storage) describes deletion/recreation or provider support for retained objects; [history-removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) explains cached/old-commit access. Deleting/recreating the same repository name is a materially different operation and requires the user's explicit choice; no deletion or support message was performed.

After pushing rewritten history, test whether GitHub still returns removed raw blobs/old commits and orphaned LFS objects. Rewriting branch history does not prove provider storage/cache removal. GitHub documents that old cached commits and orphaned LFS can require provider cleanup; its self-service LFS guidance can require deleting/recreating a repository. Preserve the same project/name and all prepared work; do not delete the repository or send support messages without the additional authorization those actions require. Keep visibility private while any actual removed-content retrieval remains unresolved.

Visibility authorization is already established. Any remaining pause must identify an actual provider-retention result or verification failure, not ask again for permission to publish a verified clean source repository.
