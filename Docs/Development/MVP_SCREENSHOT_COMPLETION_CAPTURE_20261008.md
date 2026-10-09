# Capture actual native SHOWUI screenshot completions

8 October 2026. [Chinese review](MVP_SCREENSHOT_COMPLETION_CAPTURE_20261008_ZH.md).
Cases read: MI003/MI005-MI009, Failure index, previous demo/readback plans.
V14 direct tick reads are stopped: null RHI texture/blank image and failed frame
admission. No direct-read retry, time/quality/window/tolerance sweep or false pass.

Different instrument_v15 uses FScreenshotRequest::RequestScreenshot(SHOWUI=true)
and UGameViewportClient::OnScreenshotCaptured, the installed engine's documented
actual successful screenshot-completion path already exercised by inspected
Ready/Won Shot SHOWUI images. Request in the observer tick; NEVER read pixels
there. Bind only for -ParisCapture, save actual callback bitmap1920x1080, wall
timestamp, original HUD, max8 asynchronous writes; remove owned callback on
shutdown. This is original screenshot API scheduling, not a game/pose driver.

Early acceptance: exact V13 mission/header/native/source epoch; actual full-size
NONBLANK frames, nominal10Hz scheduling,>=30frames in first12s after first image,
callback within2s of request outside actual world loading. First strict error,
missing callback/blank/write/size/cadence/hash/mission/deadline failure stops.
Retain original55cm/25s/180s/700s gates, source models/actions/guns and all input.
No recording FPS claims; separate V13 benchmark binary is named explicitly.

Finish three scripted recording rounds plus fresh native restores/restarts using
the same accepted mission source, then inspect >=900realframes over2-3minute wall
interval, actual loading gaps and readable timed annotations. Check ordinary V15
startup with observer/callback inactive. Deliver the independently tested V13
review package; V15 is a capture variant with exact native game implementation.
No canonical save/source/Catalog/Git/adoption or public distribution. Another
failure requires a different measured mechanism and plan; never fake a movie.
