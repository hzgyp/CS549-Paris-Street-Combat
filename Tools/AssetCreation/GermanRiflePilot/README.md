# Isolated German rifle pilot

Implementation: `Docs/Development/GERMAN_RIFLE_PILOT_IMPLEMENTATION_V1.md` / `_ZH.md`. Read `reference_notes.md`, `work_state.json` and the result before any action. Binaries and sensitive API state stay in the ignored LocalWorking pilot directory; no formal UE or SFTP asset selection.

Final checkpoint: two adaptations stopped without production visual acceptance. Read `GERMAN_RIFLE_PILOT_RESULT_20261003.md` / `_ZH.md` in Docs/Development and GP001. Basic14-check pass/identical28,884-triangle GLB reproduction does not cure reduction color artifacts or jagged incomplete handle cuts. No automatic third repair or cloud task.

`aholo_rifle.py`: the isolated once-only gifted-credit task. **Do not call submit again.** Base task3919866 already used20 gift credits (260→240); existing state/reservation prevents duplicate submission. The code adapts the official [generation contract](https://github.com/manycore-research/Aholo-Lux3D/blob/master/plugins/codex/aholo-lux3d/skills/lux3d/core/contracts/lux3d-generation.v1.json) and [asset block-upload client](https://github.com/manycore-research/Aholo-Lux3D/blob/master/plugins/codex/aholo-lux3d/skills/lux3d/core/runtime/asset_uploader.py), using urllib instead of installing requests. Originals exceed one upload block: the first client guard stopped before upload POST; later block uploads finished via status-only queries. Tokens/URLs/request/account details are private state, never console output or Git. No character task code/state is executed or modified.

`inspect_rifle.py`: deterministic neutral/PBR multiview of imported geometry; normalizes an inspection copy to approximate1.105m extent, measures topology/components/UV/images and saves a packed inspection scene. It does not label an imported model accepted or semantic parts separated. Output directory must be new.

Example local inspection (PowerShell):

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --disable-autoexec --python Tools/AssetCreation/GermanRiflePilot/inspect_rifle.py -- --input 'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/incoming/kar98k-base-v1.glb' --output 'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/incoming_v1'
```

`verify_protected.py --output NEW_PATH.json`: read-only size/SHA checks of43 retained native files and7 action drafts. It writes only the specified verification evidence; does not restore or alter any native bytes.

`adapt_rifle.py`: raw-base-only deterministic bounded body/exterior-handle candidate; round2 explicitly validates13 duplicate body faces before save/export. Two rounds are already used. `validate_rifle.py`: basic export/import checks and exploded-handle diagnostic, not final mechanical acceptance. `diagnose_uv.py`: frozen unlit color comparison; no geometry change. `record_outputs.py`:77 private artifact/reference/evidence files and7 script hashes, no sensitive API state. Source/hash inventory is not a Catalog or automatic restore set.
