# Field manual UI implementation

2026-10-11. User approved the generated field-manual visual direction and authorized implementation. This dated plan starts from the exact 67-file candidate_ui_v5 UI/equipment source identified in CURRENT_UI_REVIEW.json; it does not restart from the older formal 52-file source.

## Scope and visual contract

Replace the four combat-menu pages with the approved ivory/brass/olive field-manual presentation: text navigation with an active underline, sidebar actions with small symbols, fine separators, consistent two-line rows, right-aligned outlined keycaps and movement/stance icons. Use the existing Cinzel title font and a readable packaged Roboto body font. Adapt mission progress, actual player/squad values, help categories, settings and confirmation panels to the same hierarchy. Keep original gameplay HUD composition and add restrained equipment/control marks.

The concept is an art reference, not a full-screen background or an acceptance screenshot. Real values, text, hit areas and focus must remain interactive. Omit its decorative slogan and duplicate city picture. Generated illustration and actual runtime images remain explicitly distinguished.

## Failure cases read and changes to this attempt

Read Failures/README.md and MI013 plus MI032–MI036. MI013 requires a runtime UFont adapter and actual text inspection, not Composite-only text or a successful process exit. MI032 requires compatible UE APIs and unchanged reflected layout. MI033 requires screenshot completion before subsequent navigation. MI034 requires saved checkpoint guidance to disappear immediately. MI035 requires the actual restore_equipment mode with a separately identified copied-v16 seed. MI036 requires an explicit real Begin click rather than assuming the legacy menu selection.

This attempt changes menu rendering and its matching hit coordinates only. It preserves the existing input/pause/confirmation state machine, gameplay resource transactions, save gates/schema/checksum/write/readback, equipment algorithms, models, fingers, native assets, navigation, AI, prior sources and user saves. No new reflected fields, native saves, recook, automatic formal adoption, cleanup or publication.

## Sequence and early acceptance

1. Freeze exact parent source, normal trial, user files and protected native identities; prepare a separate immutable candidate.
2. Implement actual fonts, layout and reusable small line icons. Keep paint and hit bounds consistent; update opt-in probes for the deliberately moved controls.
3. Build Game, then first inspect all pages at 1920×1080 and 1280×720. Confirm seven movement bindings, readable descriptions, fixed baselines, spacing, selected state and actual settings effect. Stop extension if glyphs disappear, clipping/overlap remains or clicks target a different visible action.
4. Run actual menu mouse/keyboard, confirmation/default-cancel, pause/resume/input isolation and hazard-timer checks. Exercise real enemy-clear save, post-success hint disappearance and new-process/legacy/copied-equipment restore. Preserve original gun/ammo/equipment checks where executed; distinguish inherited exact-code protection from new runtime tests.
5. Deliver one independent normal unified trial with no probes or automated input; record exact source/Game/files and actual inspected runtime figures. Existing Editors remain open. User makes final visual/playtest selection.

## Stopping conditions

Stop on protected-byte drift, reflected/cooked incompatibility, missing fonts, mismatched visual hit areas, misleading status, persistent save guidance, resource/pause/confirmation regression, failed actual write/readback/restore or an incomplete test result. Preserve each failed source/build/runtime identity and diagnose it before creating a different candidate. A good-looking frame does not waive a functional failure.

## Approved visual reference

The first visual candidate stopped under MI037: runtime point-size text exceeded the reference-pixel layout despite successful UI interaction checks. Candidate v2 converts pixels to rounded font points and repeats actual two-resolution inspection. All v1 source and raw frames remain unchanged. This is a different rendering measurement, not a relaxed layout gate.

![Approved generated field-manual concept; not an actual UE frame](../../Images/MissionLoopV1/FIELD_MANUAL_CONCEPT_20261011.png)

The unchanged actual parent help screen is COMBAT_UI_HELP_20261011.png; raw generation prompt and private comparison notes remain under tmp/g1-combat-ui-visual-20261011.
