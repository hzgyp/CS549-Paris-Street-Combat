# MI015 — Synthetic Foley rejected; recorded observer snaps its heading

9 October 2026. Human review of draft02 accepts the gunshot only and rejects the
walking and reload mechanical audio. The opening actions also show an abrupt
about-face. Sound repair is authorized; turning is recorded for later correction.
New screen recording is held until explicit manual sound acceptance.

The generator uses decaying low-frequency sine/noise impacts for boots and repeated
790Hz impulses for reload. These have no recorded sole/ground or rifle-mechanism
origin. Actual output, nonzero samples and cue correlation were valid technical
checks; they did not establish realism. Repeating the synthesis with new frequencies
or claiming success from RMS would repeat this failure. Use licensed recorded Foley
and actual M1 mechanism samples, with original animation timing and human listening.

The opt-in finite observer's Move() immediately sets control rotation toward its
target; prone arrival resets control rotation to zero. This can produce a camera
snap that normal continuous mouse motion does not demonstrate. It is diagnostic
automation, not evidence of a mouse-control or turning-animation pass. Locate the
old footage and retain the code/log witness. Do not record a new demonstration or
silently change its director under the current sound-only correction.

Preserve approved fire.wav, valid dead-restore/resource/save/HUD behavior, every
model/finger pose and prior AVv3/parent identity. Archive copies of affected rejected
audio and generator/helper/observer sources, with references to raw MKV and draft02;
do not move or delete protected playable/history files. Follow the paired
[revision plan](../../Docs/Development/G1_AUDIO_REALISM_REVISION_20261009.md).

Old raw inspection now confirms a visible heading discontinuity between source
46.47s and46.53s, immediately after logged step_prone_move at46.459s. The forward
bridge view becomes the rear street view across approximately two30fps frames.
Code line70 in the preserved observer directly sets the target rotation; line205
calls it for the return-to-prone-site move. Line210's zero rotation at arrival is
an additional later snap risk. New private turn_sheet/turn.json and untouched raw
MKV hash retain this witness. No observer/camera/animation fix or new video ran.

Intake parserV1 also failed to find the public HQ media URL because it expected an
older preview filename convention. The primary CC0 pages were retained; corrected
parsing admits their explicitly published -hq.mp3 URLs. Original uncompressed WAV
downloads require login and were not fetched. These are genuine recording-derived
lossy references decoded to PCM, not claimed to be lossless master recordings.

The first diagnostic verifier wrongly associates worlds by UUID lexical order
and demands the restored world's entire final audio history stay empty. It fails:
the actual restored generation has0events/voices at first and at the three-second
terminal gate, then one accepted player shot at4.037s (saved shots9->10, loaded7->6).
Its native input origin is unclassified; it is not death replay or manual acoustic
approval. Preserve the failed verifier/run. Correct evidence association using
the logged generation and original gate: three-second silence/terminal corpses
and no restored death events. Do not rerun the game to manufacture empty history.

Native diagnostic WAV duration is shorter than the game's wall-clock sequence;
its exact waveform matches establish cue playback, not audiovisual cadence.
Constructed listening examples are labelled separately and must not be used as
a captured soundtrack. In-game manual listening remains the timing/realism gate.

First delivery fails its final92-file assumption: the archive already includes a
root launcher, so replacing it yields91files. The replacement was written through
a hard link, temporarily changing the old AVv3 Archive launcher and new Archive
launcher to the candidate UserDir. Game/native/source/save data never changed.
Freeze failed bytes/scripts first, then authenticate the561-byte original from
the retained HUD Archive (SHA147371d3…1d1db), restore the exact old launcher and
detach both candidate launchers as independent files. All47 parent Archive rows
must match the original frozen hashes afterward. Correct mutable launcher linking
and metadata count only; no repeat build/game/video needed. Private
delivery_launcher_failure/recovery.json records the actual transient drift and
recovery; do not claim protected files never changed during this failed transfer.
