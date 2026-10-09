# MI008 - Hidden backbuffer callback is too sparse for a real-time demo

8 October 2026. [Chinese review](FAILURE_ANALYSIS_ZH.md).
demo_capture_v1/instrument_v13 uses FFrameGrabber with a hidden RenderOffscreen
window. At19:57:03EDT only50PNG files had been saved since19:55:18, in intermittent
bursts. This fails the continuous nominal10Hz observation contract. It is not a
valid demo and supplies no performance or full-loop acceptance. Exact owned
PID14800/executable was checked against launch.json, then stopped; launcher
exit-1/raw source/log/frames retained. No user engine was terminated.

The installed implementation obtains frames from Slate's backbuffer-present
callback. Sparse hidden-window delivery is the observed limitation; do not
invent a universal cause or turn these50stills into a successful real-time demo.
The separate V13 functional/performance/plain startup receipts remain valid.

Different capture-only plan uses the actual FViewport readback API behind UE's
GetViewportScreenShot, already exercised by this task's native screenshots.
See MVP_VIEWPORT_READBACK_CAPTURE_20261008 EN/ZH before implementation. Preserve
the exact V13 mission/header, original input, assets/AI/weapon and test gates.
No recording frames are a benchmark. Further failure stops rather than silently
lowering the capture admission. Archive this run and its capture-only source
snapshot; the shared V13 build remains a valid functional candidate.
