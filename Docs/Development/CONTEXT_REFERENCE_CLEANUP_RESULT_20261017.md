# Current action chat reference cleanup — result

17 October 2026. Current file-reference cleanup passed. Chat attachment removal was not performed and is not claimed.

Removed the superseded source/tutorial/pending-review/cleanup checkpoints from current entry documents. AGENTS now routes through live source/acceptance selectors; HANDOFF_CURRENT contains the current source, separate accepted actions/model and build ownership; the original light-continuation note is a short context policy. Earlier pending states for accepted grips/Ctrl/medical pouch no longer compete with current selectors. The growing failure index must be read by relevant section, not loaded whole for every task.

| Entry | Before | After |
| --- | ---: | ---: |
| AGENTS.md | 16,236 bytes | 15,677 bytes |
| HANDOFF_CURRENT.md | 29,303 bytes | 5,747 bytes |
| ACTION_LIGHT_CONTINUATION_20261015.md | 16,295 bytes | 2,436 bytes |

Combined entry text decreased from 61,834 to 23,860 bytes. Exact preceding text is preserved, hash-pinned and retired from current routing in `InstructionHistory/ContextReferenceCleanup20261017/INDEX.json`. This retains instruction/evidence history without presenting every dated paragraph as current.

`CURRENT_ACTION_CONTEXT_REFERENCES.json` lists only two optional accepted previews: medical pouch HERO.jpg (84,998 bytes) and accepted runtime grips (188,417 bytes), total 273,415 bytes. No images were opened or embedded during this cleanup. Old candidate/raw images and original human screenshots remain preserved as evidence; no model/asset/image bytes were deleted or republished.

## Recorded chat-image audit and limit

Read-only local current-chat audit: `tmp/context-reference-cleanup-20261017/CHAT_AUDIT.json`. Latest recorded compaction at 2026-10-17 19:13:18 UTC has 46 replacement items and still includes **three inline image occurrences, 15,435,142 data-URL characters (about 15.4 MB)**. No further inline images appear in the recorded suffix at audit time. This measures local stored structure, not the next serialized/compressed request; the 15 October incident's 105.99 MB compressed request is not a measurement of this chat today.

Available tools have no operation to detach/delete historical image messages or force a current-chat context replacement. No Codex database/session file was changed, no private app-server/state workaround was used, and no new chat was created. Removing disk files or document links cannot remove inline data already stored in chat history. Native context compaction is documented, but removal of these specific retained image items has not been demonstrated; it is not reported as completed. A future human-requested text-only continuation can use the small current handoff without carrying old attachments.

Official OpenAI documentation describes native `/compact` as a way to summarize chat context: [Developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli). This documentation is not evidence that this tool run invoked compaction or removed attachments.

## Preservation and actual scope

`tmp/context-reference-cleanup-20261017/RESULT.json` verifies 225 protected files exact, including the current 134-source manifest/files, 71 actual save files, accepted selectors/manifests/previews/model, native action inputs, Catalog and the existing project config. All three archived entry preimages match their before hashes. No engine/build, source/Content/native, gameplay, original save, registry, SFTP or other-chat operation occurred.

Implementation: `CONTEXT_REFERENCE_CLEANUP_IMPLEMENTATION_20261017.md`. Reproduction/check: `python Tools/CodexDiagnostics/context_reference_cleanup_20261017.py verify`. Do not rerun prepare over this frozen audit. Later legitimate selector/source changes require a fresh bounded audit; never roll them back to make this receipt pass.
