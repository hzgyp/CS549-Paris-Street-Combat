# GP009 — evaluated bevels omitted from default GLB export

2026-10-04. Work package `GERMAN_RIFLE_SPR_ADAPTATION_V10_20261004.md` / `_ZH.md`. This is an export-validation failure, not a failure of donor separation/whole-rifle geometry. Keep private `20261004-spr-v10/finish_v2` and `audit_v1/audit.json` unchanged.

Authored `.blend` opens and new stock/band/guard/furniture solids pass positional-seam tiny-face/boundary/overfull-edge checks. The first fresh GLB comparison exits1: `Furniture_FloorPlate` has188 evaluated authored triangles but only12 exported triangles; bevelled new parts were exported as their raw base forms because `export_apply` was left at its default False. A rendered source with visible bevels is not proof of the delivered GLB.

One causal correction explicitly sets `export_apply=True`. New `finish_v3` and `audit_v2` preserve24 mesh names and24,466 evaluated/exported triangles; position max0m, UV max5.96e-8, normal max0.0411594deg under declared0.5deg gate. All12 source and12 imported gray/PBR views were opened, including actual imported receiver detail. Audit exits0. This closes the modifier-export mismatch, not history, complete animation, game import or human satisfaction.

The dependency-only `libraries.write` intermediate warns on missing active UI when directly opened. Final generator reopens only that small dependency closure, chooses the authored scene and saves a normal standalone `.blend`; audit opening final file has no library-file warning. Original2.2GiB delivery is never saved/copied. All bytes stay ignored LocalWorking; metadata/source only Git, no SFTP/Catalog/game writer.

Clean repeat exits0 and passes authored/imported and cross-export geometry/UV/normal checks with identical embedded PNG bytes, but whole GLB SHA differs. This is **not byte-exact reproduction**; encoding/corner-order cause is unproved. Do not invent a diagnosis or delete the differing export. Use the exact selected local candidate hash and document semantic/byte distinctions.

中文要点：原场景倒角正常不代表 GLB 带了倒角；第一次188对12三角失败保留。显式应用导出修改器后数量/属性/实图通过。库写入只是依赖精简步骤，最终须保存正常独立 blend。干净重跑是几何/UV/法线及嵌入图片一致，不宣称整文件哈希一致，更不能据此批准历史/游戏/人工外观。
