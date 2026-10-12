# Asset Workbench: bilingual UI and concise copy

Date: 2026-10-11. Scope: user-requested Chinese/English switching and concise internal-tool language.

Implement a persistent language selector without resetting the active route, filters, selected versions or template. Translate navigation, controls, status labels, metadata summaries, errors and copied/downloaded requirement templates. Keep record IDs, hashes, paths and original source excerpts unchanged; mark source excerpts as original text. Remove the promotional overview banner, slogans and redundant labels. Keep technical limitations needed to interpret a result.

Read failures: MI037 (font metrics and real layout overflow) and this workbench's prior deep-link and accessible-name failures in `IMPLEMENTATION_RESULT_20261011.md`. This change uses explicit locale resources and stable data keys; language must not change filters or evidence identities. Early acceptance: switching language on a filtered asset page preserves its URL and selected values. Stop if locale changes asset selection/state, rewrites upstream records, hides a failure/limitation, or causes overflow. Check both languages at 1920×1080 and 1366×768, template output, refresh persistence and existing browser workflows before reopening.

Source changes are limited to this workbench and its documentation. No asset, baseline, UE, Git or SFTP operation is required.

## Result

Implemented: persistent Chinese/English buttons in the header and session entry screen; translated controls, statuses, curated asset summaries, requirement fields and template output. Language changes preserve route, search, detail tabs, selected revisions and template category. Locale is stored only in the browser. Original source excerpts remain labeled as original text. Removed the overview promotional banner, slogans, decorative page numbers and redundant card subtitles; cards now show stable asset IDs.

Production build and TypeScript checks passed. Six browser workflows passed in 15.3 seconds, including the existing three workflows. New checks cover switching without losing state, persistence after reload, unchanged source excerpt/hash, English copy/download content, returning to Chinese, seven page types at 1920×1080 and 1366×768, horizontal overflow and untranslated Chinese UI text in English mode. The language selector itself and source originals are intentional exceptions. Actual Chinese overview and English asset/filter/template pages were visually reviewed. Backend and game validation were not rerun for this presentation-only change.

The first new template check failed because Windows clipboard reads use CRLF while downloaded Markdown uses LF. Both contained the same complete English template. The comparison now normalizes line endings only; original failure screenshot, context and report remain under `Assets/LocalWorking/AssetWorkbench/runs/bilingual/failures/clipboard-line-endings`. Final screenshots and report are private under `runs/bilingual`; no new public image allowance was created. Existing Node color-environment warnings remain.

Translation resources cover current interface and curated metadata. Future metadata additions require matching translations; unregistered source text is retained rather than silently rewritten. No network translation service is used.
