# MI018 — Native performance-stat placement is unsuitable for this HUD

10 October2026. Private probe actions_live_v1 used frozen V6 Gamea6015c94 with
stat fps/summary/unit. Ready reached; values really updated, but small text
overlaid the lower right part of the minimap. GO absent, OBS idle, no gameplay
recording admitted, owned PID41628 exits0. Launch/game logs are retained at
tmp/g1-demo-draft04-20261010/actions_live_v1.

Local UE5.8 DrawStatsHUD starts RHS at viewport20% height and width minus110;
this overlaps the selected minimap. A large memory-stat table or hiding part of
the minimap would not meet this recording requirement. Do not claim built-in
stat availability alone establishes a readable video.

The bounded replacement is an opt-in recording-only Canvas panel using the same
live timing/cycle/memory sources as stat unit. Frozen V6 input bytes are exact;
two added source files plus module wiring/RHI dependency produce exact46 source
Gameaa11d14d. Selected normal audioV2 source/Game/cooked closure are protected.
The new panel is drawn in UE before OBS capture beside the minimap; no historical
CSV values or postproduction numerical overlay. Frame/CPU/GPU/RHI times use
0.9/0.1 filtering and4Hz text refresh, process RAM and VRAM/OS budget are direct
native readings. Unavailable metrics are N/A; ms is not utilization percent.

Early actual actions_panel_v1 raw frames show changing values, intact minimap,
normal movement/shot/reload and recorded process sound. A checker initially
included startup readings and used an invalid fixed product tolerance on rounded
FPS/ms; the corrected read-only audit restricts to the capture time and accounts
for3-decimal serialization precision. This is an audit correction, not changed
performance values or a replayed game. No UI/game/input parameter sweep.

Read recording04 plan before reuse. Keep instrumentation/OBS/input-helper overhead
disclosed; counters establish this actual capture, not normal Game capacity or
course acceptance. Restore original V6 stable-runtime bytes when capture ends.

Final decode's initial exact frame-count assertion retained4747actual vs4746planned
frames, a one-frame CFR boundary difference. Read-only QA now permits at most one
frame and reports both durations/counts; original failed log/receipt retained in
DemoDraft04/QA. No counter/media/game changes. Final14-frame review passes with
post-load texture warning/timing spikes visible; human approval remains pending.
