# G1 AI narration voice auditions

9 October 2026. The user requests several voices to choose from and adds AI
narration alongside English captions. Voice selection is pending. This extends
the reviewed script03; it does not authorize recording or change gameplay.
[Chinese review](G1_DEMO_VOICE_AUDITION_20261009_ZH.md).

## Cases read, difference and early check

Read AGENTS/HANDOFF, current baseline/audio selectors, script03 and its English
SRT, Failures index and MI014/MI015/MI016. Previous actual-game audio requirements
remain: do not replace the game soundtrack with Foley or diagnostic mixer WAVs.
The new authorized layer is clearly identified offline AI narration, on its own
track. Narration never establishes a passed game/AI/performance gate.

Generate four samples from the same original English text, at the same nominal
speed with independent output loudness matching. Use local Kokoro1.0 ONNX CPU
inference, four stock voices, no voice cloning or paid/API account. Install only
in the task's private runtime under tmp; keep weights/audio outside Git. No game,
OBS, Unreal asset/source, user save, prior video or SFTP publication is touched.

Early check: model/voice names, source metadata and size/hash provenance; successful
local package import/model load; a first nonempty finite PCM waveform at24kHz.
Stop on download identity/size failure, import/inference failure, nonfinite/silent
output, clipping or failed encode/decode. Preserve failed receipts; do not silently
switch to a paid service or claim listening quality from waveform statistics.
Human listening selects the voice; technical output checks are not realism review.

## Candidates and common text

| ID | Kokoro stock voice | Catalogue identity |
|---|---|---|
| A | am_michael | American English, male |
| B | bm_george | British English, male |
| C | bf_emma | British English, female |
| D | af_heart | American English, female |

Common original text:

> Welcome to Paris Street Combat. Lead an Allied squad across the bridge and
> secure the German-held bridgehead. This demonstration shows movement,
> collision, navigation, and enemy behavior. Save after clearing the guards,
> or restart the mission if the player is killed.

These are voice auditions, not a captured soundtrack or the full final narration.
Use the same speed1.0 and loudness target; preserve the raw24kHz PCM before MP3
delivery. Duration may differ naturally between voices. No assertion that the
assistant listened to the clips is made.

Primary sources: [model/card and Apache2.0 weights](https://huggingface.co/hexgrad/Kokoro-82M),
[voice catalogue](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md),
[ONNX implementation/MIT licence](https://github.com/thewh1teagle/kokoro-onnx),
[maintainer model release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0).
Source references, installed versions/licences and complete input/output hashes
stay with the private audition receipt. Stock voice IDs are not claims of a
particular real person's identity or consent to cloning.

## Final narration rule

After selection, write short English narration against actual shot boundaries.
Do not mechanically read every SRT cue or talk continuously over the action demo.
Leave clear original-audio windows for walking/running/jump/landing, reload/fire
and death/restore checks. Mix narration on a separate stem, lowering gameplay
level only during speech when needed; never remove or replace recorded events.
Disclose AI narration. Subtitle explanations remain readable and agree with
observed behavior; current-build stress figures are still pending.

Local samples/receipts belong in
`Assets/LocalShared/Deliverables/Assignment3/VoiceAudition20261009`;
runtime/weights/logs in `tmp/g1-voice-audition-20261009`.
Generation/technical results will be recorded there after execution. No full
voiceover, screen recording or external upload is part of this audition task.

## Retained export-parser negative

First inference successfully creates Michael's raw PCM, but the loudness JSON
parser stops on FFmpeg's trailing progress summary (JSONDecodeError: Extra data).
No MP3 is admitted from that attempt. Retain the original source/run log under
tmp/g1-voice-audition-20261009/failed_v1 and first raw/log files in the delivery
root. The bounded correction reads only the complete JSON value, retaining the
following log text. Use a new selected_v2 output identity, reuse the exact first
Michael PCM and synthesize only the other three voices. Text, model, voices,
speed, loudness target and audio/encode gates are unchanged; no game/source edit.

Delivered-MP3 comparison finds Heart at−20.67LUFS, outside an additional0.6dB
comparison check. Retain selected_v2 and its loudness logs as the negative; no
clipping or synthesis failure occurred. Calibrate into new selected_v3: reuse
original float PCM and the same normalization, applying only measured attenuation
to a common−21LUFS target (no gain boost/re-synthesis or lossy-input transcoding).
Require final complete MP3 decode, no clipped true peak and within0.2dB of−21;
stop on failure. First Michael PCM sample arrays are exact; WAV container hashes
differ, so do not claim the rewritten container bytes match the first file.

## Actual delivery

Four final MP3 auditions are complete under
`Assets/LocalShared/Deliverables/Assignment3/VoiceAudition20261009/selected_v3`.
A Michael18.496s, B George17.578667s, C Emma15.061333s, D Heart16.704s; same text,
stock speed1.0 and measured final−20.99to−21.00LUFS. All full decodes exit0; true
peaks stay below0dB. AUDITION_RESULT.json identifies original PCM, gain, bytes
and final hashes. Model/runtime/source/export logs and prior negatives retained.
No listening/voice selection is claimed. Current Game53ab36d9…950aec remains
exact; no game/OBS/video entry or publication occurred. Script03 now allows
separate AI narration and its English opening caption discloses it. Final
spoken script/mix will follow user voice selection and actual footage.
