# Larger behavior-tree workspace

17 October 2026. The installed local NPC page replaces the fixed 480px graph/inspector limit with a viewport-relative workspace. Fullscreen uses the available browser viewport, with Fit to window, zoom buttons, 100% reset, Ctrl/Command-scroll zoom and background drag. The inspector can be hidden to give the graph its full width. Existing node inspection, actual execution status, actor selection, trace timestamps and full-tree expansion remain available.

Fullscreen is a separate portal with the underlying page inert and body scrolling suspended. Escape or Exit fullscreen closes it, restores body access and focuses the entry button. Zoom preserves the viewed centre; focus-executed-node centres within the graph without scrolling the surrounding page. Diagram scaling is via an SVG viewBox; the complete diagram can be fitted rather than clipped by the original fixed-size panel. Fit gives an overview; zoom provides readable detail.

Source changes are bounded to NpcBehaviorTree.tsx, npc-behavior-tree.css and the new useTreeWindow.ts. No simulation/backend/world rules, metadata registration, current selector, Game/native/save bytes or authentication were changed by this presentation package. The original behavior-tree work and its pending acceptance remain separate. No service replacement or index refresh was needed.

## Verification

Evidence: `Assets/LocalWorking/AssetWorkbench/runs/tree-window-20261017`.

- `BUILD.txt`: TypeScript and production frontend build pass; existing ModelViewer chunk-size warning retained.
- `BROWSER_TESTS.txt`: three installed-browser scenarios pass. They check an inline area taller than 480px, near-viewport fullscreen size, full expanded-diagram fit, inspector width recovery, node inspection, stable actor/decision identity, zoom, background drag without selecting a different node, Ctrl-scroll, active-node focus, Escape/focus/body restoration, English and a 390x844 fullscreen layout.
- Small JPEG contact evidence (`PAGE_QA_FIRST.jpg`) was visually inspected for entire-tree overview, zoomed node with inspector and English narrow fullscreen. Actual selected screenshots remain under `screenshots/`; no source imagery was overwritten.
- `SOURCE_HANDOFF.json` pins changed presentation files and the two exact original presentation preimages in `recovery/`. `GIT_BEFORE.txt` preserves the pre-existing dirty workspace state.

The initial browser run found that opener focus was captured after the fullscreen portal replaced the entry DOM. Capture now occurs before expansion; both Escape and the exit button restore the entry control. `BROWSER_FIRST_ATTEMPT.txt` and its QA contact remain retained. Existing map/AI/continuous-motion acceptance is not expanded by these UI checks.

Review entry: `http://127.0.0.1:8766/npc-simulation`. Use Fullscreen, then Fit to window; drag background or zoom for details. Rollback is limited to these presentation additions against exact preimages, with any later concurrent work preserved. No publication, asset cleanup or coursework delivery occurred.
