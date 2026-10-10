# G1 HUD real-time video draft implementation

9 October 2026. The user requests an actual recording with explanatory text as a
reviewable first draft. No upload or submission is requested. This plan applies
to selected hud_v3, executable49722142…d1c42b, matching source79421db8…fa0119.

## Cases read and bounded difference

Read HANDOFF, current baseline JSON/MD and package-retirement plan, Assignment3
requirements, MI007 performance, MI008 sparse hidden backbuffer, MI009 blank
post-tick readback, MI010 startup device hang and MI011 GDI wallpaper capture.
Read the current HUD/save and V10 input results. Those four recorder routes remain
stopped. Existing licensed models, fingers, animations, combat/ammunition/save
logic, source/native assets and user saves are protected.

This attempt uses preinstalled OBS and its Windows graphics **specific-window**
capture, not GDI, direct RHI reads, screenshot-to-video synthesis or desktop
capture. Computer Use selects actual returned OBS/game windows. Capture is
restricted to the separately owned current executable; no other app/audio is
recorded. Use an isolated save prefix/UserDir and logs under a new private
G1DemoDraft20261009 identity. Reuse the existing finite native checkpoint input
observer only as explicitly labelled automated real gameplay when useful; it
uses genuine shots/navigation and cannot fabricate resources or deaths. No
Game/Editor build, recook, source/gameplay patch or abandoned-route replay.

OBS scene/profile changes must be bounded to a named project-only profile and
scene collection; record the original selection and restore it on completion.
Target1080p/30fps, hardware H264 when available, recorded MKV followed by MP4
remux/encoding. Recorded30fps is media cadence, not proof of60FPS game target.

## Early acceptance and stopping condition

Before launch verify source40/current executable/native703/source758 and actual
process inventory. Preserve any user-owned game/OBS recording; do not stop it.
Confirm actual ordinary Ready and readable HUD before the capture. Record one
10-15second probe with an intentional visible change, then inspect extracted
early/middle/late frames, duration/timestamps and encoder/render-drop counters.
Require the authentic Paris game/HUD, readable text, continuous useful motion and
no unrelated desktop content. A numeric nonblank check alone is insufficient.

Stop at the first startup GPU/strict error, blank/wrong-content/cadence failure,
unknown window ownership, failed save/resources or capture error. Stop only owned
processes normally, retain negative logs/media privately and record the observed
cause without speculative attribution. No fallback desktop recording or encoder/
capture-backend sweep. A different correction requires new measured evidence and
a separately documented bounded plan.

## Draft and verification

After probe admission, record2-3minutes of actual current gameplay. Aim to show
G1 scope/roster and HUD, animation/reload and obstruction, bridge/squad navigation,
three-guard capture, consent/save/load/restart. Place English explanatory captions
over observed events, with an editable transcript/SRT and Chinese review notes.
Real-time footage remains1x; any cuts and automated controls are disclosed.
Do not claim natural bilateral combat or a new benchmark from scripted footage.

A real stress-limit segment is included only if separately admitted actual
current-build workload/capture is available. Old V13 measurements are historical,
labelled with their build, never recast as current HUD FPS or current video proof.
If a required pillar/stress demonstration cannot be witnessed, mark that gap in
the draft/result instead of manufacturing it. Draft creation does not pass all
Assignment3 gates or authorize YouTube/Vimeo/SFTP publication.

Final check: actual duration/resolution/frame timing; representative playback
and captions on every segment; readable HUD; no unrelated content; current
source/model/game/asset identities and user saves retained. Keep raw recording,
OBS log/scene/profile provenance, launch/test receipts and hashes private. Only
team source/docs/字幕 text may enter Git later under a separate publication request.

Official OBS references: [window capture](https://obsproject.com/kb/window-capture-sources),
[recording settings](https://obsproject.com/kb/advanced-recording-settings-guide).

## Probe admission, 18:55 EDT

OBS32.2.2 launch was explicitly approved after the updater completed. The new
ParisG1Demo20261009 profile/scene uses explicit WGC/title-must-match/client-area,
cursor off; global desktop/microphone sources disabled. MKV/NVENC CQP23/p5,
1920x1080/30fps. The UI stop took longer than planned: actual35.866s, retained
unaltered. Early/middle/late and reload23-26s decoded originals show authentic
game/HUD, real animation and2/16->8/10. Reload24-26s has60 decoded frames and60
distinct hashes; no motion interpolation. OBS1077 output frames,1094 drawn;
no reported rendering/encoding lag or strict GPU/game errors. Background idle
is not a game FPS benchmark. Probe exits normally through owned Alt-F4.
Current703/758/40 and executable exact before launch; user save identity isolated.

Admit one finite checkpoint recording and one action recording if useful.
Record the new game from launch to avoid missing automated Ready input; exclude
only declared startup/pre-roll and post-exit black tails. Preserve all raw bytes.
Keep the actual game foreground during the finite sequence for useful cadence.
Do not count startup black pre-roll as gameplay or synthesize replacement frames.

## Bounded post-capture export correction

The first edit renders authentic footage but reports an x264 macroblock-rate
warning and a 1/1000000 video timebase after concat. Preserve that entire first
export privately. Re-export the same admitted source frame ranges once, explicitly
using a 1/30 encoder timebase and 30fps metadata. Each retained decoded frame gets
one consecutive 30Hz timestamp; no interpolation, duplicate insertion, frame
removal or speed-up. Expected frame count is3891, duration129.7seconds. Require a
clean full decode, exact frame count/timing and readable representative captions;
stop export if those checks fail, without launching or changing the game.

Also replace the unsupported opening wording "two allies accompany" with the
directly witnessed two-allied roster at the start. The recording does not measure
full squad following or establish natural bilateral AI combat. Caption editing
must retain that distinction. [FFmpeg's encoder timebase and passthrough options](https://ffmpeg.org/ffmpeg.html#Advanced-options)
describe the export settings; all admission evidence and original raw media remain.
FFmpeg7.1 rejects the initial combination of explicit -r30 and passthrough before
opening the output; its option error is retained. Use CFR mode with the already
consecutive 30Hz timestamps and require the same3891 decoded frames, so this
cannot conceal frame insertion/removal. No capture/game retry is involved.
