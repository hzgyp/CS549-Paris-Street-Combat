# CS549 Development Resource Monitor - Implementation V1

## Purpose

Provide a small Windows utility that records CPU, memory and NVIDIA GPU load while the Paris Street Combat project is being developed. The output supports upgrade decisions; it does not replace Unreal Insights, `stat unit`, `stat gpu`, RenderDoc or an in-engine performance pass.

## Scope

- Live system CPU, busiest logical core, physical-memory, GPU and VRAM percentages.
- Per-process CPU and working-set memory for Unreal Editor, shader workers, Blender and common supporting tools.
- Editable activity phase labels such as map loading, shader compilation, Play in Editor, packaging and Blender work.
- Continuous observation with automatic recording gates. Idle observations stay in memory and are not written to the session CSV.
- Project binding uses the active workspace/uproject path, process ancestry and foreground-window evidence. A plain Epic Games Launcher process is not project activity.
- Ten seconds of pre-roll and a 30-second activity grace period capture workload startup and completion without logging hours of unrelated idle time.
- `Auto`, `Always` and `Pause` modes provide a visible manual override when automatic attribution cannot identify a project task.
- CSV logs plus a Markdown summary grouped by activity phase and active segment.
- Heuristic CPU, memory, GPU and VRAM pressure flags. The report labels them as indicators, not proven root causes.
- A WPF desktop interface and a headless mode for repeatable smoke tests.

Disk, network, frame-time attribution, Unreal thread timing and per-draw-call analysis are outside V1. NVIDIA system utilization comes from `nvidia-smi`; other GPU vendors are reported as unavailable rather than guessed.

## Prerequisites

- Windows PowerShell 5.1 for the WPF interface.
- NVIDIA driver tools on `PATH` for GPU/VRAM sampling. CPU and memory monitoring still work without them.
- No Python package, administrator access, Unreal plugin or external service.
- Runtime logs are written under ignored `Saved/PerformanceMonitor/`; no commercial asset bytes or credentials are read.

## Files and storage changes

- `Tools/PerformanceMonitor/CS549-ResourceMonitor.ps1`: monitor, logger and report generator.
- `Tools/PerformanceMonitor/Start-CS549-ResourceMonitor.vbs`: console-free double-click launcher.
- `Tools/PerformanceMonitor/Start-CS549-ResourceMonitor.cmd`: compatibility entry that immediately forwards to the silent launcher.
- `Tools/PerformanceMonitor/README.md`: operating and interpretation instructions.
- `Saved/PerformanceMonitor/<timestamp>-<session>/`: generated CSV, metadata and summary. This location is ignored by Git.

No Unreal package, model, texture, animation, audio, SFTP manifest or external asset is changed.

## Implementation order

1. Sample Windows CPU/core and physical-memory counters.
2. Sample NVIDIA GPU utilization and memory with `nvidia-smi` when available.
3. Track target-process CPU deltas and working sets.
4. Bind relevant processes to the CS549 workspace through command-line, window-title and parent-process evidence.
5. Keep a short in-memory rolling buffer, record only active/grace samples in Auto mode and mark active segments/reasons.
6. Write system and process CSV streams with phase and segment labels.
7. Add the WPF dashboard, automatic start, mode override and start/stop/open-output controls.
8. Generate per-phase p95/peak summaries and conservative bottleneck indicators.
9. Run Auto/Always headless smoke tests, inspect the CSV/report and launch the GUI.

## Acceptance evidence

- Headless run completes without administrator rights.
- `metrics.csv`, `processes.csv`, `session.json` and `summary.md` are created.
- CSV timestamps and numeric fields parse correctly.
- The summary reports sample count and metrics per phase.
- Auto mode writes no long idle tail when no project-bound process is active.
- A project-bound process activation flushes the pre-roll buffer, creates a numbered segment and records the reason.
- Always mode remains available for controlled tests or workloads that cannot expose a project path.
- The GUI opens, starts/stops sampling and shows live CPU, memory and GPU values.
- Missing `nvidia-smi` produces an explicit unavailable state while CPU/memory logging continues.

## Interpretation rules

- CPU indicator: p95 total CPU at least 85%, or a core at least 95% in at least half the phase while monitored project processes consume at least 75% of one logical core's system-wide capacity.
- Memory indicator: p95 physical-memory use at least 85%, or minimum available memory at most 2 GiB.
- GPU indicator: p95 GPU utilization at least 90%.
- VRAM indicator: p95 VRAM use at least 90%.
- More than one indicator produces a mixed-pressure result.
- Fewer than five samples in a phase are marked as insufficient for a reliable conclusion.

These thresholds guide investigation. Upgrade decisions should use several representative sessions and Unreal's internal frame/thread profilers before purchase.

## Failure and rollback

- If WPF cannot load, run the same script with `-NoGui` to preserve logging.
- If GPU sampling fails, retain CPU/memory/process monitoring and show the GPU limitation in the report.
- If a session stops unexpectedly, existing CSV rows remain readable; a later session writes to a new timestamped directory.
- Rollback consists of removing `Tools/PerformanceMonitor/` and this document. Generated files under `Saved/PerformanceMonitor/` are independent, ignored evidence and may be retained or deleted by the user.
