# MI014 — Saved death replay and absent gameplay/video audio

9 October 2026. User observes German death animation replay after F9 in draft01
and reports absent walking/running/fire/death audio; requests English-only text
after fixing the behavior. This does not reject the selected models/grip/HUD or
the valid resource/consent/save checks.

ApplySnapshot correctly restores dead/resources but calls ordinary PC_Die.
That endpoint applies lifecycle guards and plays Rifle_Death_3 from time0.
Dead=true and numeric restoration do not prove immediate terminal corpse pose.
Restore presentation separately: retain lifecycle protection, seek existing clip
to its end without animation notifies, stop and evaluate before revealing the
restored world. Normal combat death must retain its original transition.

Draft01 launcher used -NoSound and OBS had all audio off. Those were recording
choices, not a working audiovisual demo. User's previous normal game log shows
an initialized WASAPI playback device; microphone-input warnings do not diagnose
output silence. Source/authoring paths have no footsteps/fire/death sound wiring.
Confirm local audio inventory/actual packaged output before claiming sound fixed.
Counters alone, audio added in editing or an enabled device alone are insufficient.

Preserve original snapshot/trial/user saves/draft01/raw/provenance. New private
wrapper must use selected hud_v3 and real game-event audio, prime trackers after
restore, release voices on travel and demonstrate old-journal compatibility.
Do not replay stopped RHI/GDI recorders or change models/fingers/weapon rules.
Follow [the bounded repair/recording plan](../../Docs/Development/G1_DEATH_AUDIO_VIDEO_REVISION_20261009.md).

Additional retained negatives during this repair:

- HelperV1 compilation fails on two ToSharedRef calls applied to TSharedRef;
  freeze42 source files and compile log before the exact V2 argument correction.
- First V2 background checkpoint mix is all-zero even with positive cue counters.
  UE's default UnfocusedVolumeMultiplier=0 and blocked foreground explain why
  counters cannot admit audio. A focused V2 action end produces actual output.
- First V3 checkpoint is again numerically valid but audio-silent behind a new
  executable's Windows Firewall prompt. Keep both runs; never automate that
  security prompt or relabel the silent mix as a successful recording.
- Short sounds outside their attenuation range return null AudioComponents by
  design. The first death-cue range covers only23.4m and all3 ranged kills are
  culled. Use a separate documented61.2m death-impact range with attenuation,
  retain footsteps' range, and explicitly skip out-of-range playback.

V3 actual mixed-audio verification with an explicit recording-process background
volume override produces9 accepted-shot cues and3 genuine deaths (original clip
playing at its beginning), unclipped stereo48kHz PCM. Restored corpses stop at
3.933333s, and first/settled restored trackers have0 events/voices. Exact old
HUDv3 V5 journal load passes the same3-second terminal/lifecycle gates. Normal
playtest focus-loss muting stays at the engine default. This does not establish
OBS audiovisual alignment, stress/performance or course acceptance; new video
must pass its separate actual capture/media gates before delivery.

The finite OBS actions probe subsequently passes actual full audiovisual decode,
reviewed real frames and in-game fire correlation0.9843/delay0.1452s. Its first
full mission launch then exits3 before Ready, at frame2, with D3D12 device removed
and Aftermath MMU page fault. Actual GPU use4,871.56MB versus9,285MB budget does
not prove exhaustion; exact cause remains unresolved. Its case is preserved as
`tmp/g1-demo-draft02-20261009/checkpoint_gpu_fail_1` and raw19:56:44 MKV remains.
No failed startup imagery is admitted into draft02. One documented separate fresh
entry uses identical settings; a repeated fault stops that recovery route. This
is not a rerun of MI008-MI011's stopped capture implementations.

Final local repair and actual English/audio draft02 are delivered; see
[actual result](../../Docs/Development/G1_DEATH_AUDIO_VIDEO_RESULT_20261009.md).
The separate fresh mission exits0. Actual rapid-shot matching must distinguish
neighboring identical cues: broad matcher false0.43s result retained, corrected
initial-transient analysis passes unchanged gates. Overlapping death impact is
verified by original-template residual/tail analysis, never soundtrack editing.
First export's global1:30 timebase emits2,177 AAC backward-input warnings; the
whole export_v1 remains. Video-only option scope produces zero-warning full AV
decode output. These results do not erase any earlier negative or explain the
occasional startup GPU fault. New and original trial/video/source/evidence/user
files are protected; normal audio remains basic original synthesized SFX.
