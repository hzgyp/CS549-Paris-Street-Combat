# Field-manual UI result

2026-10-11. The approved generated appearance has been implemented as real interactive UI, starting from candidate_ui_v5. One normal unified equipment/UI trial is ready for human review; the formal enemy-clear baseline is unchanged.

## Delivered behavior

PLAY_COMBAT_UI.cmd, PLAY_FIELD_MANUAL_UI.cmd and PLAY_TACTICAL_EQUIPMENT.cmd enter tmp/Playtest-G1-FieldManualUI-20261011. Esc opens the combat menu; Tab opens player/squad during gameplay. Four pages share Cinzel title hierarchy, readable Roboto body text, text tabs and active underlines, small line symbols, fine dividers, consistent title/detail rows and compact right-side keycaps. Movement and stance are grouped with whitespace. Squad values use fixed columns; mission progress and checkpoint lock reflect actual state. Equipment HUD plates are lighter, while original health/ammo/radar composition remains.

Mouse/keyboard selection, settings effects, default-cancel confirmation, original Ready/Lost controls and checkpoint priority remain. Original model/finger/weapon/save/navigation/AI/equipment behavior is preserved. Real save-success acknowledgment still removes the save action and first-use guide.

Independent UserDir G1FieldManualUI20261011 / prefix ParisFieldManualUIV1; no old user-save migration or override. Normal entry has no probe, automated input, observer or AI/resource override. Existing Editors remain open; this result establishes Game checks, not new Editor/PIE/cook acceptance.

## Actual final Game evidence

Game SHA-256: b40590bdec9c27d4a2c2f321ae32c0eca12936923f36d003872df2dabc113d11. Exact69 source: Unreal/Variants/G1FieldManualUI20261011/Project; source manifest SHA-256: 1d7e1fa292e463c2f501be44d346c85f2a3569f93a2d5bc3394bd433a47f9887. Matching authoring project: tmp/g1-tactical-equipment-20261010/candidate_field_manual_v2/Project.

All19 checks below actually ran this final Game with complete pass results and exit0. UI probes use controller input without gameplay overrides. Original regression fixtures retain their documented positioning, held-AI, endpoint-damage and bounded payload fixtures; they are not natural human combat or large-NPC stress evidence.

| Check | Actual result | Checks / events |
|---|---|---:|
| ui_pause | pass_ui_pause | 6 / 0 |
| ui_equipment_pause | pass_ui_equipment_pause | 7 / 0 |
| ui_pages | pass_ui_pages | 11 / 0 |
| ui_confirm | pass_ui_confirm | 9 / 0 |
| ui_pages_small | pass_ui_pages_small | 11 / 0 |
| menu | pass_menu_input | 37 / 0 |
| enemy_clear | pass_enemy_clear_checkpoint | 27 / 0 |
| p1 | pass_p1_ammo_radar_inventory | 22 / 0 |
| throw | pass_native_throw | 0 / 9 |
| smoke | pass_native_smoke | 0 / 19 |
| interactions | pass_native_interactions | 0 / 29 |
| mine_range | pass_native_mine_range | 0 / 16 |
| mine_post_clear | pass_native_mine_post_clear | 0 / 5 |
| mine_post_clear_frag | pass_native_mine_post_clear_frag | 0 / 5 |
| save_equipment | pass_native_save_equipment | 0 / 16 |
| restore_equipment | pass_native_restore_equipment | 0 / 11 |
| restore_legacy | pass_native_restore_legacy | 0 / 9 |
| restore_v16_equipment | pass_native_restore_equipment | 0 / 11 |
| performance | pass_native_performance | 0 / 14 |


Ten 1080p images were individually inspected. Ten 720p frames were reviewed in a contact sheet and original-size pages; settings descriptions/footer keycaps fit, page/category labels match and two-line rows remain separate. Confirmation, live paused grenade, throw/supply guidance, actual save success and clean post-save HUD were also inspected. The generated concept is separately labeled in the implementation document, never used as runtime evidence.

1754 native files, parent67 source/normal trial, original formal52/Game, models/fingers/audio, Catalog and prior user files remain exact. All other parent files, reflected layout and UI state/pause/confirmation/guidance logic remain byte-equivalent after removing the approved render/hit-coordinate/accessor changes. Only three parent files plus two new rendering includes differ. Packaged Roboto fonts retain the installed distribution's original Apache2 license and provenance.

MI037 preserves v1's actual font overflow despite passing interaction checks. v2 converts intended pixel sizes to font points using the installed Slate96DPI/72-point contract; v1 source/receipts/raw frames were not overwritten. See the failure archive and implementation plan.

No automatic formal adoption, Git/SFTP/video publication or cleanup. Human visual/play acceptance is pending. Current six-actor short capped-performance check has its original limited scope; no whole-motion, long-term, second-machine or large-NPC claim.

All19 final logs were audited: no fatal error or new handled ensure. The inherited mine static-mesh UV-channel handled ensure and existing build warnings remain recorded; this is not a zero-warning claim or a fix for those earlier asset diagnostics.

## Actual runtime illustrations

![Actual UE field-manual screen](../../Images/MissionLoopV1/FIELD_MANUAL_HELP_20261011.png)

![Actual UE field-manual screen](../../Images/MissionLoopV1/FIELD_MANUAL_MISSION_20261011.png)

![Actual UE field-manual screen](../../Images/MissionLoopV1/FIELD_MANUAL_SQUAD_20261011.png)

![Actual UE field-manual screen](../../Images/MissionLoopV1/FIELD_MANUAL_SETTINGS_20261011.png)

![Actual UE field-manual screen](../../Images/MissionLoopV1/FIELD_MANUAL_POST_SAVE_20261011.png)
