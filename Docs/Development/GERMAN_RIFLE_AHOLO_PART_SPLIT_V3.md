# German rifle — bounded Aholo part separation V3

2026-10-03. Authorization: Yupu permits a little more Aholo if necessary; earlier free/gift-only restriction remains. No purchase, top-up, M1 reload, character, Unreal, SFTP/Catalog selection or commit/push.

## Review and changed mechanism

Read Failures/README, GP001 and GP002, latest HANDOFF and Blender modeling workflow. GP001 damaged UV through global reduction and separated only an exterior handle. GP002's spatial cuts and whole-plane convex hull closures cut stock and bridged unrelated contours. Stop those routes; none of their adapted outputs is the input here.

Official live Lux3D OpenAPI documents POST `/lux3d/v1/part-split/task/create`, requiring `glbUrl`, and the shared task query. This bounded semantic-part candidate uses the original 299,479-triangle cloud base, SHA `a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60`. It does not regenerate the whole gun, deform the stock, add box cuts/cover plates, or assume part splitting improves softened geometry.

Official source: https://labs.aholo3d.com/api-docs/specifications/services/lux3d/openapi.json ; operation index https://labs.aholo3d.com/api-docs/en/llms.txt . Spec is checked live, not inferred from general 3DGS cropping documentation.

## Budget and storage

One task maximum, live quote <=20 credits and verified gift remainder only. Prior ledger: gift300 minus two character20 and one rifle20 =240. Reconcile live API balance before spending; unexpected balance stops. Reserve before POST and never retry an uncertain submission. Quote must be unexpired, exact body/account/balance unchanged. Poll/download do not submit. API keys, account contexts and signed URLs remain ignored private `api-state/`, never reported or committed.

New source: `Tools/AssetCreation/GermanRiflePartSplitV3/`; physical output: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/`. Preserve old77+7 and V2 files and all43+7 native hashes. No game writer. Use a fresh URL for task3919866 only if anonymous download SHA proves it is the exact unchanged original; otherwise stop before spend and plan explicit original-file upload.

## Order, early acceptance and stop

1. Read-only capability/balance/source-hash audit and exact pricing quote.
2. If <=20 gifted credits, submit once and reconcile actual debit. Store complete private task state for recovery. No automatic second job or articulation/texture task.
3. Fresh Blender import, inventory meshes/materials/UVs/texture images and whole-rifle dimensions. Compare source and split geometry; do not rename cloud parts to claim semantic accuracy.
4. Fixed side/top/underside/quarter views plus exploded-part diagnostic. Early falsifiable gate: a useful wood/metal separation with no stock fins/gaps, missing sling/guard, UV damage or changed major silhouette. Multiple output nodes alone are not a pass; partial handle is not a complete bolt. Inspect actual images.
5. If useful, retain as a local working candidate with exact limitations and next bounded interface proof. This task does not include a production remesh, finishing, LOD, runtime integration or historical approval. Otherwise stop at one task, preserve candidate and record why; do not repeat segmentation or fall back to failed box/hull scripts.

Rollback is non-selection: all input/game bytes stay untouched. Report exact live cost/balance, input and result hashes, actual reviewed views and whether separation is useful. No final weapon/game-ready claim from import alone.

Chinese review: 本轮只试一次 Aholo 原底模自动分件，最多20赠送积分；先查余额、报价和原模型SHA。重点看木托和金属能否真正拆开，不能把“多个网格”当成功。不会重生成整枪、继续失败的裁切补片，也不改M1或游戏。成功也只是本地分件候选，失败就停止。

## Pre-submit price amendment (supersedes quote-only20 cap above)

Before any submission, two read-only price requests returned HTTP422 `PRICING_ITEM_NOT_QUOTABLE`, retryable false. Source task URL did refresh and anonymously hashes to the exact original; live balance240 reconciles. No task/debit yet. The existing authenticated in-app browser at https://labs.aholo3d.com/pricing explicitly lists Mesh Segmentation40 original /30 promotional credits per task. Thus the quote API cannot price this operation; this is not an operation failure and not free. Public official pricing is the alternative price evidence, not a fabricated quote.

Within Yupu's new discretionary small-use permission and gift-only240, amend BEFORE POST to one task reserved40 gifted credits (current webpage30; undiscounted40 protects against promotion/API divergence). Refuse >40 debit, changed account/balance or any purchase. No automatic follow-up task, articulation, regeneration or retopology. Reservation records exact official URL, observed30/original40 and amendment. Actual debit must be queried and reported; no guarantee that a failed task receives a refund. Client retains failed quote diagnostics privately. The original quote-only route is preserved as historical evidence but cannot be executed as the new submission path.

中文变更：报价接口明确不支持本项，网页实际列出分件优惠30、原价40。在用户允许“必要时再用一点”且仅赠送额度内，动手前改为只试一次，预留40上限；不充值。剩余240已实时核对。实际扣费以任务后余额为准。
