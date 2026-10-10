# Git storage for document illustrations

10 October 2026. The user directs that images closely associated with project
documents belong in Git alongside those documents. This supersedes the earlier
blanket SFTP rule for reviewed document illustrations only. Models, textures,
animations, commercial source assets, private evidence, videos and document
binaries retain their existing storage rules.

## Scope and checks

Read AGENTS, the current HANDOFF, Failures/README, ML014, ML015 and ML020, the
current development/audio selectors, audio publication plan/result, the team
synchronization manual and the original mission layout documents. These map
cases distinguish planning admission from actual collision/navigation/travel;
publishing an image must not promote the historical draft to implemented scope.

Publish the two existing project-authored mission overview/detail illustrations
under Docs/Images/MissionLoopV1, with relative links in both layout translations.
Preserve the private originals, receipts, raw masks and layout JSON unchanged.
The figures contain planning masks/annotations, not vendor texture/model bytes,
private correspondence or connection secrets. This task does not migrate every
old screenshot or restore missing external assets.

Before changing storage guards, check both figures visually and freeze their
size/SHA-256. Add a narrow reviewed-image allowlist with linked documents,
provenance, public-sharing review and approved byte versions. Permit only those
exact image paths in ignore rules and Git checks; enforce real raster signatures,
the 5 MiB per-image cap and approved hashes. New illustrations follow the same
review process; do not globally unignore images or weaken private-tree rules.

Update AGENTS, the synchronization manual and repository/storage introductions
to distinguish document illustrations from production asset images. At task end,
check relative links, copied bytes, ignore classification, current/staged storage
guards and negative tests for unlisted/private/oversized/disguised images. Check
staged data in a temporary Git index without changing the user's real staging.

Stop on unclear public-sharing rights, private information, source-byte drift,
existing destination conflicts, missing document references or any failed guard.
Keep unrelated ongoing team-feedback files untouched. No engine entry, game
change, SFTP mutation, asset deletion, commit or push is part of this change;
publication remains a separately authorized action.

## Local verification result

Completed the bounded storage change. Overview is 300,350 bytes with SHA-256
`3e1ef5f6c79478de77aec9fd1a547985345900be79d24554024f99522d8f91c9`;
detail is 167,156 bytes with SHA-256
`d06c7dbb2c179c0543087d0d05ad7ca65e6b22a2465712c2360c8e6e2928d5b4`.
Both document copies exactly match the retained private originals. Both figures
were visually inspected; EN/ZH documents now link them and identify the original
full-route draft versus the current bridgehead-only MVP.

All 13 regression tests pass, covering approved/changed/disguised/oversized
bytes, retained historical approval, actual figure/link checks, staged approval,
private/production-path rejection, missing links, unlisted images and unapproved
outgoing-history bytes. The current Git check and temporary-index staged check
pass with metadata for 17,682 selected external files; this is metadata validation,
not a new local/SFTP asset hash audit. The latter includes the two PNGs and only
the 15 files belonging to this change, plus the existing HEAD ancestry check.
Whitespace checks pass; other images/private paths remain ignored.

The temporary index file was removed and the real index remained empty. No commit,
push, SFTP mutation, deletion of original evidence or gameplay change occurred.
Concurrent team-feedback/MI019 files were not included or edited. Future document
image revisions must update their approved byte versions and linked text together.

## Unannotated maps and the 25 cm only correction

10 October follow-up: the user also requests the confirmed unannotated black/white
maps, then explicitly discards the 1 m edition for planning because its precision
can misidentify usable space. Only the selected 25 cm lowest-surface walk masks
are included: `full_walk_L0.png` and `saved_walk_L0.png` from the independently
audited FineMapGridV1/expanded_v2_20261007/derived source. The former uses the
disposable expanded survey; the latter uses the separately measured saved scope.
Do not merge their scopes, invent white cells or label L0 a building floor.

Read the fine/coarse grid results and the retained ML014/015/020 limitations.
Both original masks were visually inspected and have audited source SHA-256;
copy them unchanged as document illustrations, preserving 4032 by 4032 pixels,
1-bit grayscale and 25 cm per pixel. Add relative EN/ZH links, exact ignore rules
and byte approvals; mark the coarse-grid report as retired for current planning.
Early check: source hashes must match the original fine-mask audit, including
quarantine. Stop on byte/dimension/link drift or a guard failure.

No 1 m image was copied into Docs/Images before the correction, so there is no
coarse document copy to delete. Coarse originals, failed tests and historical
receipts remain protected private evidence, not current planning inputs or public
document illustrations. No raw mask, navigation data, game or SFTP asset is
changed. Recheck the four-image document list with a temporary index, leaving
unrelated team work and the real staging area untouched; no commit/push.

Follow-up verification passes: both copied SHA-256 values match the original
fine-mask audit, no resampling/interpolation, 4032-by-4032/1-bit grayscale
preserved. The new masks total 106,926 bytes; the complete four-image set totals
574,432 bytes. All 14 regression checks pass. The 21-file temporary-index
storage/staged/HEAD-ancestry check passes with 17,682 asset metadata entries;
exactly four reviewed 25 cm figures are eligible, with no 1 m document image.
The temporary index is removed, real staging stays empty, and private originals
and unrelated team-feedback/MI019 work remain unchanged. No commit/push or
coarse-evidence deletion is claimed.

## Scoped Git publication

The subsequent 10 October user request explicitly authorizes commit and push
of this window's changes only. It supersedes the earlier no-publication scope
for the 21 reviewed document-image/policy/guard files, not the other repair
window's work. Read the current Git state and diffs; fetch confirms local main
and origin/main are initially identical with no unpublished commits.

Stage only the exact reviewed paths and use a path-scoped commit. Exclude
Failures/README.md, G1_TEAM_FEEDBACK_IMPLEMENTATION_20261010_ZH.md, the MI019
directory, G1TeamFeedbackV1 tools and G1TeamFeedback20261010 source variant.
Keep their changes intact. Rerun tests, whitespace, storage and staged-byte
checks without bypassing hooks; verify the commit's exact 21-path inventory.
Push that exact commit to origin/main, not a potentially changed shared HEAD.
Stop on unexpected staged/shared-file changes, divergent Git history, guard
failure or a different outgoing commit inventory. Verify remote main afterward;
the actual resulting commit/remote identity is reported in the user handoff.
No SFTP/model/native/gameplay changes are part of this publication.
