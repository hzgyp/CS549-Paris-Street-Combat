# MI011 - Owned-window GDI recording does not contain the game

8 October 2026. [Chinese review](FAILURE_ANALYSIS_ZH.md).
external_demo_v1 uses exact V13 binary, no internal capture flag, owned HWND1444932,
FFmpeg7.1 gdigrab,1920x1080. The numeric early image admission passes resolution/
nonblank checks, but inspected actual frame shows wallpaper and NO game/HUD.
Therefore it fails visual content admission; no valid movie, gameplay or FPS proof.
This is an observation failure, not evidence that the game renders wallpaper.
The previous native Shot images and ordinary V13 startup actually show the game.

Numeric color/dimensions/owned handle are insufficient. Do not infer whether
composition, visibility or a specific capture backend caused it without evidence.
Do not silently switch to desktop capture, record other apps, retarget windows,
insert synthetic game frames or rerun this failed recorder. Both exact owned
game/recorder paths/PIDs were checked and stopped; record capture_failure.json and
launcher exit/error qualification. No private application content was delivered.

All four recording routes are stopped. Keep the valid V13 functional/performance/
ordinary startup evidence and prepare its private review bundle independently;
report VIDEO as pending, not passed. A teammate's actual interactive validation
can follow the manual recording guide, but no message or recording by a teammate
has been sent/performed. Preserve every failed source/log/raw-media directory
under the private failure archive with selected hashes. No source/model/rig/grip/
weapon/Catalog/publication change or full course readiness follows.
