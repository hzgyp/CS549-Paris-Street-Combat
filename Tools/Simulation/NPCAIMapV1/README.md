# Paris 2D interaction design board

Open `tmp/npc-ai-map-v1-20261017/run_v3/index.html` locally. No server, network or engine is required. Keep the adjacent `board.js`, `data.js` and `maps/` directory together. The generated page reuses the original eight separate candidate/status raster pairs and the ten canonical NPC AI V2 candidate traces. It projects those traces, without rerunning policy/pathfinding against the map. Layout mode edits desired placements, arrows and notes separately; generate JSON before closing if you want to retain a draft.

Reproduce in a NEW output identity, using the bundled Python with Pillow:

```powershell
& 'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' Tools/Simulation/NPCAIMapV1/build.py --out tmp/npc-ai-map-v1-20261017/<new-run>
& 'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' Tools/Simulation/NPCAIMapV1/inspect.cjs tmp/npc-ai-map-v1-20261017/<new-run> C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
```

The input receipt records exact byte/hash identities, candidate/status colour counts and the coordinate convention. Status classification uses embedded run-length codes reconstructed byte-exactly from the pinned status PNGs; this avoids `file://` canvas readback restrictions. Source maps remain full resolution and byte-identical. Screenshots are small JPEGs for conversation review, not measurement evidence.

This design board is suitable for specifying outcomes. A later measured-graph adapter needs height/support identities and actual directed edges; line of sight, cover and acoustics need their own data. The final UE gate still needs actual arrival, movement ownership, collision, resources/actions and each faction/two-Allied travel. Do not infer those from this overlay or restart the paused map survey.
