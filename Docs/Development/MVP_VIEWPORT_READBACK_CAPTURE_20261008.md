# Capture-only native viewport readback

8 October 2026. [Chinese review](MVP_VIEWPORT_READBACK_CAPTURE_20261008_ZH.md).
Cases read: Failures/README, MI003/MI005/MI006/MI007/MI008 and finite demo plan.
V13 three-round functional/old-config rejection, ordinary startup and independent
CSV results stand. MI008's sparse hidden callback is stopped, not a usable video.

New instrument_v14 changes ONLY the opt-in capture branch: read actual viewport
pixels through GetViewportScreenShot at nominal10Hz after native preparation,
save original1920x1080PNG asynchronously (max8writes), record actual readback wall
times, no simulation-time or pose/health/ammo/brain writes. No Slate backbuffer
callback dependency. UE UnrealClient.cpp:2407 delegates to Viewport::ReadPixels;
the actual previously inspected Shot images establish this viewport can be read.
Do not claim the new repeated recorder has passed before a fresh entry.

Require exact V13 native mission/header hashes, all canonical758/359/703, same
route/input/55cm/25s/180s/700s gates. Capture is a separate run, never a benchmark.
Early admission: actual1920x1080 readback and >=30captures in first12s after first
captured frame, exact recorded dimensions/files; stop on first readback/admission/
write/mission/hash/error/deadline failure. No hidden window/input/camera/quality/
time/gate sweep. A different later failure requires its own analysis/plan.

Native rendering has one-frame latency; record readback completion wall time.
Real loading gaps remain explicit and annotated, with last actual frame held only
for that measured gap. Final2-3minute video must contain >=900realframes, preserve
wall intervals, actual loading, original HUD, scripted-input and recording-overhead
disclosure. Inspect originals plus early/middle/end encoded frames and duration.
Ordinary observer-disabled V14 startup is rechecked. Delivery identifies separate
V13 performance/functional binary and V14 capture-only binary, exact native source
parity; no false single-binary benchmark claim. Private review only, no canonical
source/Catalog/adoption/Git/publication change.
