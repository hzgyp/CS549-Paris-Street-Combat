from pathlib import Path
import sys
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import read
r=read(root/'Docs/Development/CURRENT_GRENADE_MODEL_REVIEW.json')
summary=f'''# Current unified grenade model trial

11 October 2026, local candidate; manual review pending. {r['revision']}. Game SHA256 `{r['game_sha256']}`.

Source: `{r['source_snapshot']}` (74 files), manifest SHA256 `{r['source_manifest_sha256']}`. Active authoring `{r['active_authoring_project']}` contains final v5 despite its historical v1 folder name; compiled snapshots/receipts retained separately. Normal entry `{r['playable_entry']}`,100 files, independent `{r['user_dir']}` / `{r['save_prefix']}`; no diagnostic input/camera/AI/resource overrides.

Asset-index first: existing USParatrooper equipment slot9 MkII extracted,2733 triangles; no independent registered smoke can found, new 1943 AN-M8-inspired gray/yellow exterior,7562 triangles. Both1024 PBR and fresh GLB verified.13 same-final-Game runs pass. Original finger/character/weapon/save source and1754 native guards exact; parent73/normal92/user files remain. Existing Editors stay open.

Original hold pose is low on screen; lower body remains partly obscured. No new continuous hand-contact/full-action/manual/performance or expanded-NPC acceptance. Ground image is isolated photography fixture only. Formal enemy-clear52/PLAY_CURRENT_G1/Assignment3 release unchanged; no Git/SFTP/adoption/retirement.

Read [implementation](MissionLoopV1/GRENADE_MODELS_IMPLEMENTATION_20261011_ZH.md), [result, actual image and source assets](MissionLoopV1/GRENADE_MODELS_RESULT_20261011_ZH.md), [exact review record](CURRENT_GRENADE_MODEL_REVIEW.json), MI042 and parent death/field-manual results. Future unified changes start from this latest74 local candidate when the user asks to continue it, preserving formal52 as recovery/selected baseline.
'''
(root/'Docs/Development/CURRENT_GRENADE_MODEL_REVIEW.md').write_text(summary,encoding='utf-8')
(root/'Docs/Development/CURRENT_UI_REVIEW.md').write_text(summary,encoding='utf-8')
p=root/'HANDOFF.md';t=p.read_text('utf-8');marker='## 11 October 2026: grenade model unified trial'
assert marker not in t
t=marker+f''' (latest local candidate)

Read CURRENT_GRENADE_MODEL_REVIEW and CURRENT_UI_REVIEW. Asset-index-first, existing MkII equipment extraction + bounded new gray/yellow1943 AN-M8 exterior replace placeholders. Final74 source `Unreal/Variants/G1GrenadeModels20261011/Project`, Game `{r['game_sha256']}`. Normal100-file tmp/Playtest-G1-GrenadeModels-20261011/PLAY_GRENADE_MODELS.cmd, independent UserDir/prefix.13 final-Game runs+1754-native/parent/user/Catalog protection pass; finger/weapon/save and original gameplay functions exact. Existing Editors stay open. Active authoring is candidate_grenade_models_v1/Project containing finalv5; do not delete by historical name. All failed snapshots/results retained under MI042. Original Hold low-edge occlusion persists; no new contact/full-motion/manual/large-NPC acceptance. Source/modelGLB/packedBlend/texture inputs and diagnostics private; one approved exact document-render crop. No formal adoption/Git/SFTP/cleanup; formal52 and parent73 preserved. See paired GRENADE_MODELS_IMPLEMENTATION/RESULT_20261011_ZH and tmp/g1-grenade-models-20261011/DELIVERY_20261011.json.

'''+t
p.write_text(t,encoding='utf-8')
p=root/'AGENTS.md';t=p.read_text('utf-8');needle='## Authority and scope';assert needle in t
note='''

- Latest local grenade-model unified candidate,11 October2026: user requests asset-index-first/doc-first placeholder replacement, preserving fingers/weapon/save. Read CURRENT_GRENADE_MODEL_REVIEW and paired GRENADE_MODELS_IMPLEMENTATION/RESULT_20261011_ZH plus MI042. Final74 G1GrenadeModels20261011 Gamea927caa3…cf4eb59 inherits parent73 death/field-manual, uses existing licensed equipment MkII section2733tri and new bounded AN-M8-inspired gray/yellow exterior7562tri after registered smoke absence.13 same-Game runs/1754native+parent/user/Catalog protection pass. Normal100 files tmp/Playtest-G1-GrenadeModels-20261011/PLAY_GRENADE_MODELS.cmd, independent UserDir/prefix; no normal fixture/camera/AI/resource overrides. Active authoring candidate_grenade_models_v1/Project contains finalv5, historical folder name is not retirement authority. Keep original models/UV/fingers/throw actions/gun/save schema and all failure/source/raw; original Hold lower-view occlusion remains, not new full-contact/motion/manual/performance acceptance. Current UI review points here; formal52 and parent73 remain. Existing user-authorized Editors stay open. No automatic adoption/Git/SFTP/cleanup; reviewed exact document crop follows allowlist.
'''
t=t.replace(needle,needle+note,1);p.write_text(t,encoding='utf-8')
p=root/'tmp/g1-grenade-models-20261011/work_state.md';p.write_text(summary+'\nCompleted; no required implementation work remains. Manual trial pending.\n',encoding='utf-8')
print('CURRENT NOTES UPDATED')
