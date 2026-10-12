# MI037: Field-manual point sizes exceeded the pixel layout

2026-10-11. The first independent candidate_field_manual_v1 compiled and its UI pages test passed actual selection/settings/pause checks. The captured actual frames nevertheless show oversized type: the ARROWS / MOUSE footer label exceeds its outlined keycap and touches SELECT; the first settings description extends past the right panel edge. The movement group caption is also too close to its divider. These are visual failures, not a model, input or checkpoint failure.

The new runtime FSlateFontInfo sizes were supplied as reference pixels, while runtime fonts render point sizes at 96/72 pixel scale. The existing geometry was specified in pixels; merely checking that DrawnSize was positive did not establish that text fitted. Keep candidate_field_manual_v1 Project, compiled-source-game, Game/runtime/build/protection records and both raw ui_pages_field_v1 and ui_pages_small_field_v1 folders unchanged. Do not rename their frames or claim a final visual pass.

The next distinct candidate_field_manual_v2 converts intended pixel sizes to rounded point sizes before rendering, preserving the same row/grid coordinates and normal input/state/guidance logic. It also gives Quiet walk a separate upright icon and uses a lock rather than a muted checkmark for a locked checkpoint. New actual 1080p and 720p frames must show readable titles, separate title/detail baselines, contained keycaps and settings text, with correct mouse selection and original functional regression.

Stop if actual glyphs or descriptions still clip, hit bounds mismatch, protected bytes drift or any actual regression fails. Generated beauty and exit0 do not establish usable layout.
