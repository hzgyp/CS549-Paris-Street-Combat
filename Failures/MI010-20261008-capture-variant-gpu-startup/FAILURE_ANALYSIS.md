# MI010 - Capture variant GPU startup fails before any recorded frame

8 October 2026. [Chinese review](FAILURE_ANALYSIS_ZH.md).
demo_capture_v3/instrument_v15 exits nonzero with DXGI_ERROR_DEVICE_HUNG / GPU
PageFault at frame1-2, zero captured frames, no native Ready observation. Log reports
local4861.93MB versus9285MB budget; it does not establish VRAM exhaustion. Neither
a screenshot-completion callback nor a full mission is known to have run. Do not
assert that the capture API, approved models, driver or earlier null-read attempt
caused this crash without evidence. Whole V15 entry failed; no demo or FPS pass.

Stop V15 capture route. Preserve source, strict log, launch and crash data privately;
never expose the full crash XML containing machine/account identifiers. The already
completed V13 functional/performance/plain evidence remains historical valid proof,
not proof that the current graphics state is healthy. A separate READ-ONLY original
V13 ordinary-startup readiness probe may now observe native Ready, actual1080p,
strict log and normal exit. No capture flag/driver/device/system changes, no mission
input/save, no V15 retry or rendering-profile sweep. First error/time bound stops.

If that original probe fails too, stop all graphics work pending diagnosis/external
state change and finish independent source/report review only. If it passes, it
still does not explain this isolated GPU crash or authorize rerunning stopped
recorders; any different external recorder needs its own bounded plan. Retain
candidate source and original asset/weapon/grip protections. Public access, human,
second-machine,60FPS and valid demo remain open. MANIFEST records the closed failed
entry/build archive and selected hashes.
