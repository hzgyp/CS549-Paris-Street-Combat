# Token-free local Asset Workbench access

17 October 2026. The user requests removal of the current page's token verification. Scope: direct local page entry and reload on the owned loopback service, including the integrated NPC scene. Network/shared mode keeps bootstrap authentication. No UE, game build, asset registration, index refresh, external transfer or coursework delivery.

Read the current handoff, NPC selector/result, Asset Workbench functional specification and implementation failure/result sections. Relevant failures: occupied port and launcher parent/child ownership, SPA deep-link reload, initial missing browser session. Preserve the selected map/world implementation and the latest live database/Catalog, not a dated snapshot.

## Sequence and acceptance

1. Preserve exact preimages of the auth source and edited routing/documentation under `tmp/asset-workbench-local-access-20261017/work_v1`. Existing changes remain the edit base.
2. Automatically create a cookie/CSRF session when a local-only loopback page calls GET `/api/v1/session`. Reuse a valid cookie to preserve NPC ownership. In this mode bootstrap token comparison is bypassed; shared mode and non-loopback authorities still verify it. Keep Host, Origin, CSRF, expiry and per-browser NPC ownership checks.
3. Check fresh entry, existing/expired cookie, stale local bootstrap link, separate browser ownership, denied origins/hosts, CSRF and unchanged shared/public authentication with isolated databases. Re-run the existing NPC motion/API and raster checks. No frontend changes are needed because it already calls GET session for plain URLs.
4. Inspect the exact owned loopback process and its active jobs immediately before replacement. Restart only that idle service, preserving its private access link and latest index. Verify plain `/npc-simulation` in a fresh owned browser context, an actual step, reload and asset navigation without supplying a token. Save bounded receipts and source hashes.
5. Update the current local-access pointer and targeted documentation/handoff after acceptance.

## Storage, stopping and rollback

New tests and browser QA source remain in Tools; private evidence/preimages remain in the new ignored tmp directory. No frontend bundle build, binary packaging, Catalog edits or native resource writes. Stop on a failed auth boundary, ownership ambiguity, active index task or unintended database/asset mutation. Report actual local QA separately from human design acceptance. Rollback restores only the exact auth patch after checking concurrent edits, then restarts only the verified idle owner; never blanket checkout or restore the database/Catalog or other lanes.
