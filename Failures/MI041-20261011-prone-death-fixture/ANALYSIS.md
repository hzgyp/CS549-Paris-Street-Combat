# MI041: original spawn does not admit the prone fixture

11 October2026. candidate_death_v3 passes mine/frag/standing/crouched death diagnostics, but prone_v3 exits0 with failed_player_death_prone / actual_prone_before_death. Actual01_before remains STANDING on the original rubble-edge spawn; no prone death was triggered. Do not call this a player death-camera failure or relax prone admission.

Preserve source/build/probe result/log/raw frame. The next bounded probe uses the earlier physically reached prone site (1762.5,-20662.5,114.402 feet cm, referenced by ParisCompletionProbe), waits for real Z input and requires actual DesiredPosture2 before damage. Relocation is a declared diagnostic fixture, not a new spawn or map edit. Original posture/collision/navigation/gun/save rules stay exact. If that original gate still rejects, stop and diagnose the actual support/action state; do not force the posture field.
