# MI009 - Post-actor-tick viewport has no valid RHI read texture

8 October 2026. [Chinese review](FAILURE_ANALYSIS_ZH.md).
demo_capture_v2/instrument_v14 stops at its first12s capture admission:
16frames,20.807s total,normalexit0 but strict ensure InRHITexture in
D3D12RenderTarget.cpp:599. The first1920x1080PNG has ALL RGBA extrema(0,0).
Dimensions and ReadPixels' nonempty buffer did not prove usable visual content.
No mission movement started, no movie/performance/whole-loop pass.

The failed call is made during OnWorldPostActorTick. It differs from the working
Shot SHOWUI flow. Installed GameViewportClient.cpp:2369-2580 shows that native
ProcessScreenShots handles SHOWUI through Slate::TakeScreenshot, then broadcasts
OnScreenshotCaptured after a successful image, sets alpha255 and resets the
request. The task's prior inspected1920x1080Shot SHOWUI images are actual positive
evidence for this different request/completion mechanism, not direct tick reads.

Preserve/stop the direct-read method; never repeatedly retry null textures, weaken
frame admission or crop out errors. A new capture-only completion plan is required.
Original V13 native source/function/performance remains unchanged and valid in its
bounded scope. Canonical assets/source/Catalog untouched. MI009 MANIFEST records
the closed failed entry/build's private archive and selected hashes.
