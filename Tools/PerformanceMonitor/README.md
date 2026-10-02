# CS549 Resource Monitor

This Windows utility records development-machine CPU, memory, NVIDIA GPU and VRAM use. It also tracks Unreal Editor, shader-worker, Blender and related process CPU/RAM use.

## Start the dashboard

For a console-free launch, double-click:

`Start-CS549-ResourceMonitor.vbs`

The `.cmd` file is retained only as a compatibility entry and forwards immediately to the silent launcher.

The launcher starts monitoring immediately. In the default **Auto** mode, the app keeps observing but writes CSV rows only when it can associate an active Unreal, shader, build, Blender or editor process with this CS549 workspace. Change the phase while the session is running when the activity changes. Click **Stop and summarize** before reviewing the report.

Recording modes:

- **Auto**: recommended. Record project activity, ten seconds of pre-roll and a 30-second completion grace period.
- **Always**: record every sample for a controlled benchmark or an activity the path detector cannot recognize.
- **Pause**: keep the dashboard visible without writing samples.

Recommended phases:

- Idle baseline
- Open project / map
- Compile shaders
- Play in Editor
- Package build
- Blender / asset work

## Headless run

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Tools\PerformanceMonitor\CS549-ResourceMonitor.ps1 `
  -NoGui -DurationSeconds 60 -IntervalSeconds 2 -RecordingMode Always `
  -SessionName "Map-load-test" -InitialPhase "Open project / map"
```

## Output

Each run creates a directory under `Saved/PerformanceMonitor/` containing:

- `metrics.csv`: recorded system CPU, busiest core, RAM, GPU and VRAM samples, including segment and activation reason.
- `processes.csv`: CPU and working-set RAM for monitored processes, including whether each process was bound to this project.
- `session.json`: machine, session and monitor configuration.
- `summary.md`: per-phase p95/peak values and upgrade-oriented indicators.

These outputs are ignored by Git. Share them only after checking that session and phase names contain no private information.

## Reading the result

- High total CPU usually points to parallel work such as shader compilation or packaging.
- A saturated busiest core with lower total CPU can indicate a single-thread limit.
- High physical-memory use or very low available memory suggests RAM pressure.
- High GPU utilization suggests graphics throughput pressure.
- High VRAM use suggests that a GPU with more memory may help.
- No flagged resource does not prove the machine is fast enough. Storage, engine thread synchronization and project configuration are not measured by this tool.
- If Auto mode misses a legitimate project task, switch to Always for that phase rather than weakening the path-based detector.

Run several representative sessions before buying hardware. Confirm gameplay conclusions with Unreal Insights and Unreal's `stat unit`, `stat gpu` and memory tools.
