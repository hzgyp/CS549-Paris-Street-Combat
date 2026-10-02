[CmdletBinding()]
param(
    [switch]$NoGui,

    [ValidateRange(1, 60)]
    [int]$IntervalSeconds = 2,

    [ValidateRange(1, 86400)]
    [int]$DurationSeconds = 30,

    [string]$SessionName = "CS549 development",

    [string]$InitialPhase = "Idle baseline",

    [ValidateSet("Auto", "Always", "Pause")]
    [string]$RecordingMode = "Auto",

    [ValidateRange(0, 120)]
    [int]$PreRollSeconds = 10,

    [ValidateRange(0, 600)]
    [int]$ActivityGraceSeconds = 30,

    [string]$ProjectRoot,

    [switch]$AutoStart,

    [string]$OutputDirectory,

    [string[]]$ProcessNames = @(
        "UnrealEditor",
        "UnrealEditor-Cmd",
        "ShaderCompileWorker",
        "UnrealBuildTool",
        "AutomationTool",
        "UnrealPak",
        "IoStore",
        "BuildPatchTool",
        "LiveCodingConsole",
        "CrashReportClientEditor",
        "Blender",
        "EpicGamesLauncher",
        "Code",
        "Rider64",
        "devenv"
    )
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$script:InvariantCulture = [System.Globalization.CultureInfo]::InvariantCulture
$script:NvidiaSmiPath = $null

function Resolve-NvidiaSmi {
    $command = Get-Command "nvidia-smi.exe" -ErrorAction SilentlyContinue
    if ($command -and $command.Source) {
        return $command.Source
    }

    $candidates = @(
        (Join-Path $env:SystemRoot "System32\nvidia-smi.exe"),
        (Join-Path $env:ProgramW6432 "NVIDIA Corporation\NVSMI\nvidia-smi.exe")
    )
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
    }
    return $null
}

function Convert-ToDoubleOrNull {
    param([AllowNull()][object]$Value)

    if ($null -eq $Value) {
        return $null
    }
    $number = 0.0
    $text = ([string]$Value).Trim()
    if ([double]::TryParse(
            $text,
            [System.Globalization.NumberStyles]::Float,
            $script:InvariantCulture,
            [ref]$number)) {
        return [double]$number
    }
    return $null
}

function Format-Number {
    param(
        [AllowNull()][object]$Value,
        [int]$Decimals = 2
    )

    if ($null -eq $Value) {
        return ""
    }
    return ([double]$Value).ToString("F$Decimals", $script:InvariantCulture)
}

function Convert-ToCsvField {
    param([AllowNull()][object]$Value)

    if ($null -eq $Value) {
        return '""'
    }
    $text = ([string]$Value).Replace('"', '""')
    return '"' + $text + '"'
}

function Get-SafeName {
    param([string]$Value)

    $safe = $Value -replace '[^A-Za-z0-9._-]+', '-'
    $safe = $safe.Trim('-','.')
    if ([string]::IsNullOrWhiteSpace($safe)) {
        return "session"
    }
    if ($safe.Length -gt 48) {
        return $safe.Substring(0, 48)
    }
    return $safe
}

function Get-CpuLoad {
    try {
        $rows = @(Get-CimInstance -ClassName Win32_PerfFormattedData_PerfOS_Processor -ErrorAction Stop)
        $totalRow = $rows | Where-Object { $_.Name -eq "_Total" } | Select-Object -First 1
        $coreRows = @($rows | Where-Object { $_.Name -ne "_Total" })
        $total = if ($totalRow) { [double]$totalRow.PercentProcessorTime } else { $null }
        $maxCore = $null
        if ($coreRows.Count -gt 0) {
            $maxCore = [double](($coreRows | Measure-Object -Property PercentProcessorTime -Maximum).Maximum)
        }
        return [pscustomobject]@{
            TotalPercent = $total
            MaxCorePercent = $maxCore
        }
    }
    catch {
        try {
            $processors = @(Get-CimInstance -ClassName Win32_Processor -ErrorAction Stop)
            $loads = @($processors | ForEach-Object { [double]$_.LoadPercentage })
            $average = if ($loads.Count -gt 0) {
                [double](($loads | Measure-Object -Average).Average)
            }
            else {
                $null
            }
            return [pscustomobject]@{
                TotalPercent = $average
                MaxCorePercent = $average
            }
        }
        catch {
            return [pscustomobject]@{
                TotalPercent = $null
                MaxCorePercent = $null
            }
        }
    }
}

function Get-MemoryLoad {
    try {
        $os = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop
        $totalGiB = ([double]$os.TotalVisibleMemorySize * 1KB) / 1GB
        $availableGiB = ([double]$os.FreePhysicalMemory * 1KB) / 1GB
        $usedGiB = $totalGiB - $availableGiB
        $usedPercent = if ($totalGiB -gt 0) { 100.0 * $usedGiB / $totalGiB } else { $null }
        return [pscustomobject]@{
            UsedPercent = $usedPercent
            UsedGiB = $usedGiB
            AvailableGiB = $availableGiB
            TotalGiB = $totalGiB
        }
    }
    catch {
        return [pscustomobject]@{
            UsedPercent = $null
            UsedGiB = $null
            AvailableGiB = $null
            TotalGiB = $null
        }
    }
}

function Get-NvidiaLoad {
    if (-not $script:NvidiaSmiPath) {
        return [pscustomobject]@{
            Available = $false
            Names = ""
            DeviceCount = 0
            UtilizationPercent = $null
            MemoryUsedMiB = $null
            MemoryTotalMiB = $null
            MemoryPercent = $null
            TemperatureC = $null
        }
    }

    try {
        $query = "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu"
        $format = "--format=csv,noheader,nounits"
        $lines = @(& $script:NvidiaSmiPath $query $format 2>$null)
        if ($LASTEXITCODE -ne 0 -or $lines.Count -eq 0) {
            throw "nvidia-smi returned no GPU rows."
        }

        $devices = @()
        foreach ($line in $lines) {
            $parts = @($line -split ',' | ForEach-Object { $_.Trim() })
            if ($parts.Count -lt 5) {
                continue
            }
            $devices += [pscustomobject]@{
                Name = $parts[0]
                UtilizationPercent = Convert-ToDoubleOrNull $parts[1]
                MemoryUsedMiB = Convert-ToDoubleOrNull $parts[2]
                MemoryTotalMiB = Convert-ToDoubleOrNull $parts[3]
                TemperatureC = Convert-ToDoubleOrNull $parts[4]
            }
        }
        if ($devices.Count -eq 0) {
            throw "nvidia-smi rows could not be parsed."
        }

        $validUtil = @($devices | Where-Object { $null -ne $_.UtilizationPercent } | ForEach-Object { $_.UtilizationPercent })
        $validUsed = @($devices | Where-Object { $null -ne $_.MemoryUsedMiB } | ForEach-Object { $_.MemoryUsedMiB })
        $validTotal = @($devices | Where-Object { $null -ne $_.MemoryTotalMiB } | ForEach-Object { $_.MemoryTotalMiB })
        $validTemp = @($devices | Where-Object { $null -ne $_.TemperatureC } | ForEach-Object { $_.TemperatureC })

        $gpuUtil = if ($validUtil.Count -gt 0) { [double](($validUtil | Measure-Object -Maximum).Maximum) } else { $null }
        $memoryUsed = if ($validUsed.Count -gt 0) { [double](($validUsed | Measure-Object -Sum).Sum) } else { $null }
        $memoryTotal = if ($validTotal.Count -gt 0) { [double](($validTotal | Measure-Object -Sum).Sum) } else { $null }
        $memoryPercent = if ($null -ne $memoryUsed -and $memoryTotal -gt 0) {
            100.0 * $memoryUsed / $memoryTotal
        }
        else {
            $null
        }
        $temperature = if ($validTemp.Count -gt 0) { [double](($validTemp | Measure-Object -Maximum).Maximum) } else { $null }

        return [pscustomobject]@{
            Available = $true
            Names = (($devices | ForEach-Object { $_.Name }) -join "; ")
            DeviceCount = $devices.Count
            UtilizationPercent = $gpuUtil
            MemoryUsedMiB = $memoryUsed
            MemoryTotalMiB = $memoryTotal
            MemoryPercent = $memoryPercent
            TemperatureC = $temperature
        }
    }
    catch {
        return [pscustomobject]@{
            Available = $false
            Names = ""
            DeviceCount = 0
            UtilizationPercent = $null
            MemoryUsedMiB = $null
            MemoryTotalMiB = $null
            MemoryPercent = $null
            TemperatureC = $null
        }
    }
}

function Get-ForegroundProcessId {
    try {
        if (-not ("CS549ForegroundWindow" -as [type])) {
            Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class CS549ForegroundWindow {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
'@
        }
        $window = [CS549ForegroundWindow]::GetForegroundWindow()
        if ($window -eq [IntPtr]::Zero) {
            return 0
        }
        [uint32]$processId = 0
        [void][CS549ForegroundWindow]::GetWindowThreadProcessId($window, [ref]$processId)
        return [int]$processId
    }
    catch {
        return 0
    }
}

function Get-ProjectBindingMap {
    param(
        [Parameter(Mandatory = $true)][object]$State,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Processes
    )

    $bindings = @{}
    if ($Processes.Count -eq 0) {
        return $bindings
    }

    try {
        $cimRows = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop)
    }
    catch {
        return $bindings
    }

    $allByPid = @{}
    foreach ($row in $cimRows) {
        $allByPid[[int]$row.ProcessId] = $row
    }

    $targetPids = @{}
    $titles = @{}
    foreach ($process in $Processes) {
        $targetPids[[int]$process.Id] = $true
        try { $titles[[int]$process.Id] = [string]$process.MainWindowTitle } catch { $titles[[int]$process.Id] = "" }
    }

    $rootToken = ([string]$State.ProjectRoot).Replace('/','\').ToLowerInvariant()
    foreach ($pidValue in $targetPids.Keys) {
        if (-not $allByPid.ContainsKey($pidValue)) {
            continue
        }
        $row = $allByPid[$pidValue]
        $commandLine = ([string]$row.CommandLine).Replace('/','\').ToLowerInvariant()
        $title = ([string]$titles[$pidValue]).ToLowerInvariant()

        if (($rootToken -and $commandLine.Contains($rootToken)) -or
            $commandLine.Contains('ww2franceliberation.uproject')) {
            $bindings[$pidValue] = "project path in process command line"
        }
        elseif ($title.Contains('ww2franceliberation') -or
                $title.Contains('paris street combat') -or
                $title.Contains('parisstreetcombat')) {
            $bindings[$pidValue] = "project identity in foreground-capable window"
        }
    }

    for ($pass = 0; $pass -lt 8; $pass++) {
        $changed = $false
        foreach ($pidValue in $targetPids.Keys) {
            if ($bindings.ContainsKey($pidValue) -or -not $allByPid.ContainsKey($pidValue)) {
                continue
            }
            $parentId = [int]$allByPid[$pidValue].ParentProcessId
            if ($bindings.ContainsKey($parentId)) {
                $bindings[$pidValue] = "child of project-bound process"
                $changed = $true
            }
        }
        if (-not $changed) {
            break
        }
    }
    return $bindings
}

function Get-TargetProcessLoad {
    param([Parameter(Mandatory = $true)][object]$State)

    $now = [DateTimeOffset]::Now
    $elapsed = ($now - $State.LastProcessSampleAt).TotalSeconds
    if ($elapsed -le 0) {
        $elapsed = [double]$State.IntervalSeconds
    }

    $wanted = @($State.TargetProcessNames | ForEach-Object { $_.ToLowerInvariant() })
    $currentCpu = @{}
    $rows = @()
    $processes = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $wanted -contains $_.ProcessName.ToLowerInvariant()
    })
    $projectBindings = Get-ProjectBindingMap -State $State -Processes $processes

    foreach ($process in $processes) {
        try {
            $cpuSeconds = if ($null -ne $process.CPU) { [double]$process.CPU } else { 0.0 }
            $key = [string]$process.Id
            $cpuPercent = 0.0
            if ($State.PreviousProcessCpu.ContainsKey($key)) {
                $delta = $cpuSeconds - [double]$State.PreviousProcessCpu[$key]
                if ($delta -ge 0) {
                    $cpuPercent = 100.0 * $delta / $elapsed / [double]$State.LogicalProcessorCount
                }
            }
            $currentCpu[$key] = $cpuSeconds
            $rows += [pscustomobject]@{
                ProcessName = $process.ProcessName
                Id = $process.Id
                CpuPercent = [math]::Max(0.0, $cpuPercent)
                WorkingSetGiB = [double]$process.WorkingSet64 / 1GB
                IsProjectBound = $projectBindings.ContainsKey([int]$process.Id)
                ProjectBindingReason = if ($projectBindings.ContainsKey([int]$process.Id)) { [string]$projectBindings[[int]$process.Id] } else { "" }
            }
        }
        catch {
            continue
        }
    }

    $State.PreviousProcessCpu = $currentCpu
    $State.LastProcessSampleAt = $now
    return @($rows | Sort-Object -Property CpuPercent -Descending)
}

function Get-ProjectActivitySignal {
    param(
        [Parameter(Mandatory = $true)][object]$State,
        [Parameter(Mandatory = $true)][object]$Sample
    )

    $projectRows = @($Sample.Processes | Where-Object { $_.IsProjectBound })
    $projectPids = @{}
    foreach ($row in $projectRows) { $projectPids[[string]$row.Id] = $true }
    $projectCpu = if ($projectRows.Count -gt 0) {
        [double](($projectRows | Measure-Object -Property CpuPercent -Sum).Sum)
    }
    else { 0.0 }

    $foregroundPid = Get-ForegroundProcessId
    $reasons = New-Object System.Collections.Generic.List[string]
    if ($foregroundPid -gt 0 -and $projectPids.ContainsKey([string]$foregroundPid)) {
        $reasons.Add("project window is foreground")
    }
    if ($projectCpu -ge 0.5) {
        $reasons.Add("project process CPU activity")
    }
    if ($projectRows.Count -gt 0 -and $null -ne $Sample.GpuUtilizationPercent -and $Sample.GpuUtilizationPercent -ge 5) {
        $reasons.Add("GPU activity while project process exists")
    }

    $newPids = @($projectPids.Keys | Where-Object { -not $State.PreviousProjectPids.ContainsKey($_) })
    if ($newPids.Count -gt 0) {
        $reasons.Add("project process started")
    }
    $State.PreviousProjectPids = $projectPids

    return [pscustomobject]@{
        IsActive = ($reasons.Count -gt 0)
        Reason = if ($reasons.Count -gt 0) { $reasons -join "; " } else { "no attributable CS549 workload" }
        ProjectProcessCount = $projectRows.Count
        ProjectCpuPercent = $projectCpu
    }
}

function New-MonitorSession {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][int]$SampleIntervalSeconds,
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][string[]]$Targets,
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [Parameter(Mandatory = $true)][string]$Mode,
        [Parameter(Mandatory = $true)][int]$PreRoll,
        [Parameter(Mandatory = $true)][int]$Grace
    )

    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $folderName = "$stamp-$(Get-SafeName $Name)"
    $sessionDirectory = Join-Path $Destination $folderName
    if (Test-Path -LiteralPath $sessionDirectory) {
        $sessionDirectory = "$sessionDirectory-$([guid]::NewGuid().ToString('N').Substring(0,6))"
    }
    New-Item -ItemType Directory -Path $sessionDirectory -Force | Out-Null

    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $metricsPath = Join-Path $sessionDirectory "metrics.csv"
    $processesPath = Join-Path $sessionDirectory "processes.csv"
    $metricsWriter = New-Object System.IO.StreamWriter($metricsPath, $false, $utf8)
    $processesWriter = New-Object System.IO.StreamWriter($processesPath, $false, $utf8)
    $metricsWriter.WriteLine("timestamp,elapsed_seconds,segment_id,recording_reason,activity_signal,activity_reason,phase,cpu_total_percent,cpu_busiest_core_percent,memory_used_percent,memory_used_gib,memory_available_gib,gpu_available,gpu_utilization_percent,vram_used_percent,vram_used_mib,vram_total_mib,gpu_temperature_c,target_cpu_percent,target_ram_gib,target_process_count,project_cpu_percent,project_process_count")
    $processesWriter.WriteLine("timestamp,elapsed_seconds,segment_id,phase,process_name,pid,cpu_percent,working_set_gib,is_project_bound,project_binding_reason")
    $metricsWriter.Flush()
    $processesWriter.Flush()

    $logicalProcessors = [Environment]::ProcessorCount
    try {
        $computerSystem = Get-CimInstance -ClassName Win32_ComputerSystem -ErrorAction Stop
        if ([int]$computerSystem.NumberOfLogicalProcessors -gt 0) {
            $logicalProcessors = [int]$computerSystem.NumberOfLogicalProcessors
        }
    }
    catch {
    }

    $processorName = "Unknown"
    try {
        $processorName = ((Get-CimInstance -ClassName Win32_Processor -ErrorAction Stop | Select-Object -First 1).Name).Trim()
    }
    catch {
    }

    $gpuProbe = Get-NvidiaLoad
    $metadata = [ordered]@{
        schema_version = 1
        session_name = $Name
        started_at = [DateTimeOffset]::Now.ToString("o")
        interval_seconds = $SampleIntervalSeconds
        recording_mode = $Mode
        project_root = $ProjectPath
        pre_roll_seconds = $PreRoll
        activity_grace_seconds = $Grace
        computer_name = $env:COMPUTERNAME
        operating_system = [Environment]::OSVersion.VersionString
        processor = $processorName
        logical_processors = $logicalProcessors
        gpu_sampler = if ($script:NvidiaSmiPath) { "nvidia-smi" } else { "unavailable" }
        gpu_names = $gpuProbe.Names
        monitored_process_names = $Targets
        interpretation = "Heuristic indicators only; confirm with repeated workloads and Unreal profiling."
    }
    $metadataPath = Join-Path $sessionDirectory "session.json"
    [System.IO.File]::WriteAllText(
        $metadataPath,
        ($metadata | ConvertTo-Json -Depth 4),
        $utf8)

    return [pscustomobject]@{
        Name = $Name
        Directory = $sessionDirectory
        IntervalSeconds = $SampleIntervalSeconds
        RecordingMode = $Mode
        ProjectRoot = $ProjectPath
        PreRollSeconds = $PreRoll
        ActivityGraceSeconds = $Grace
        TargetProcessNames = @($Targets)
        LogicalProcessorCount = $logicalProcessors
        StartedAt = [DateTimeOffset]::Now
        Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        LastProcessSampleAt = [DateTimeOffset]::Now
        PreviousProcessCpu = @{}
        PreviousProjectPids = @{}
        LastActivityAt = $null
        IsRecording = $false
        SegmentId = 0
        ObservedSampleCount = 0
        PendingSamples = New-Object System.Collections.Generic.List[object]
        MetricsWriter = $metricsWriter
        ProcessesWriter = $processesWriter
        Samples = New-Object System.Collections.Generic.List[object]
        ProcessSamples = New-Object System.Collections.Generic.List[object]
        Closed = $false
    }
}

function Write-RecordedSample {
    param(
        [Parameter(Mandatory = $true)][object]$State,
        [Parameter(Mandatory = $true)][object]$Sample,
        [Parameter(Mandatory = $true)][string]$RecordingReason
    )

    $Sample.WasRecorded = $true
    $Sample.SegmentId = $State.SegmentId
    $Sample.RecordingReason = $RecordingReason
    $State.Samples.Add($Sample)

    $metricValues = @(
        (Convert-ToCsvField $Sample.Timestamp.ToString("o"))
        (Convert-ToCsvField (Format-Number $Sample.ElapsedSeconds))
        (Convert-ToCsvField $Sample.SegmentId)
        (Convert-ToCsvField $RecordingReason)
        (Convert-ToCsvField $Sample.ActivitySignal)
        (Convert-ToCsvField $Sample.ActivityReason)
        (Convert-ToCsvField $Sample.Phase)
        (Convert-ToCsvField (Format-Number $Sample.CpuTotalPercent))
        (Convert-ToCsvField (Format-Number $Sample.CpuMaxCorePercent))
        (Convert-ToCsvField (Format-Number $Sample.MemoryUsedPercent))
        (Convert-ToCsvField (Format-Number $Sample.MemoryUsedGiB))
        (Convert-ToCsvField (Format-Number $Sample.MemoryAvailableGiB))
        (Convert-ToCsvField $Sample.GpuAvailable)
        (Convert-ToCsvField (Format-Number $Sample.GpuUtilizationPercent))
        (Convert-ToCsvField (Format-Number $Sample.VramUsedPercent))
        (Convert-ToCsvField (Format-Number $Sample.VramUsedMiB))
        (Convert-ToCsvField (Format-Number $Sample.VramTotalMiB))
        (Convert-ToCsvField (Format-Number $Sample.GpuTemperatureC))
        (Convert-ToCsvField (Format-Number $Sample.TargetCpuPercent))
        (Convert-ToCsvField (Format-Number $Sample.TargetRamGiB))
        (Convert-ToCsvField $Sample.Processes.Count)
        (Convert-ToCsvField (Format-Number $Sample.ProjectCpuPercent))
        (Convert-ToCsvField $Sample.ProjectProcessCount)
    )
    $State.MetricsWriter.WriteLine(($metricValues -join ','))

    foreach ($processRow in $Sample.Processes) {
        $State.ProcessSamples.Add([pscustomobject]@{
            Timestamp = $Sample.Timestamp
            ElapsedSeconds = $Sample.ElapsedSeconds
            SegmentId = $Sample.SegmentId
            Phase = $Sample.Phase
            ProcessName = $processRow.ProcessName
            Id = $processRow.Id
            CpuPercent = $processRow.CpuPercent
            WorkingSetGiB = $processRow.WorkingSetGiB
            IsProjectBound = $processRow.IsProjectBound
            ProjectBindingReason = $processRow.ProjectBindingReason
        })
        $processValues = @(
            (Convert-ToCsvField $Sample.Timestamp.ToString("o"))
            (Convert-ToCsvField (Format-Number $Sample.ElapsedSeconds))
            (Convert-ToCsvField $Sample.SegmentId)
            (Convert-ToCsvField $Sample.Phase)
            (Convert-ToCsvField $processRow.ProcessName)
            (Convert-ToCsvField $processRow.Id)
            (Convert-ToCsvField (Format-Number $processRow.CpuPercent))
            (Convert-ToCsvField (Format-Number $processRow.WorkingSetGiB))
            (Convert-ToCsvField $processRow.IsProjectBound)
            (Convert-ToCsvField $processRow.ProjectBindingReason)
        )
        $State.ProcessesWriter.WriteLine(($processValues -join ','))
    }
    $State.MetricsWriter.Flush()
    $State.ProcessesWriter.Flush()
}

function Submit-MonitorSample {
    param(
        [Parameter(Mandatory = $true)][object]$State,
        [Parameter(Mandatory = $true)][object]$Sample
    )

    $State.ObservedSampleCount++
    if ($Sample.ActivitySignal) {
        $State.LastActivityAt = $Sample.Timestamp
    }

    if ($State.RecordingMode -eq "Pause") {
        $State.IsRecording = $false
        $State.LastActivityAt = $null
        $State.PendingSamples.Clear()
        $Sample.RecordingStatus = "Paused - observing without recording"
        return
    }

    $withinGrace = $false
    if ($null -ne $State.LastActivityAt) {
        $withinGrace = (($Sample.Timestamp - $State.LastActivityAt).TotalSeconds -le $State.ActivityGraceSeconds)
    }
    $shouldRecord = ($State.RecordingMode -eq "Always") -or
                    ($State.RecordingMode -eq "Auto" -and ($Sample.ActivitySignal -or $withinGrace))

    if ($State.IsRecording) {
        if ($shouldRecord) {
            $reason = if ($State.RecordingMode -eq "Always") { "Always mode" }
                      elseif ($Sample.ActivitySignal) { "active project signal" }
                      else { "activity grace period" }
            Write-RecordedSample -State $State -Sample $Sample -RecordingReason $reason
            $Sample.RecordingStatus = "Recording segment $($State.SegmentId): $reason"
        }
        else {
            $State.IsRecording = $false
            $State.PendingSamples.Clear()
            $State.PendingSamples.Add($Sample)
            $Sample.RecordingStatus = "Observing - no attributable CS549 workload"
        }
        return
    }

    $State.PendingSamples.Add($Sample)
    $maxPending = [math]::Max(1, [math]::Ceiling($State.PreRollSeconds / [double]$State.IntervalSeconds) + 1)
    while ($State.PendingSamples.Count -gt $maxPending) {
        $State.PendingSamples.RemoveAt(0)
    }

    if (-not $shouldRecord) {
        $Sample.RecordingStatus = "Observing - no attributable CS549 workload"
        return
    }

    $State.IsRecording = $true
    $State.SegmentId++
    for ($pendingIndex = 0; $pendingIndex -lt $State.PendingSamples.Count; $pendingIndex++) {
        $pending = $State.PendingSamples[$pendingIndex]
        $reason = if ([object]::ReferenceEquals($pending, $Sample)) {
            if ($State.RecordingMode -eq "Always") { "Always mode" } else { "active project signal" }
        }
        else {
            "pre-roll"
        }
        Write-RecordedSample -State $State -Sample $pending -RecordingReason $reason
    }
    $State.PendingSamples.Clear()
    $Sample.RecordingStatus = "Recording segment $($State.SegmentId): activity detected"
}

function Add-MonitorSample {
    param(
        [Parameter(Mandatory = $true)][object]$State,
        [Parameter(Mandatory = $true)][string]$Phase
    )

    if ($State.Closed) {
        throw "The monitor session is already closed."
    }
    if ([string]::IsNullOrWhiteSpace($Phase)) {
        $Phase = "Unlabeled"
    }

    $timestamp = [DateTimeOffset]::Now
    $cpu = Get-CpuLoad
    $memory = Get-MemoryLoad
    $gpu = Get-NvidiaLoad
    $processRows = @(Get-TargetProcessLoad -State $State)
    $targetCpu = if ($processRows.Count -gt 0) { [double](($processRows | Measure-Object CpuPercent -Sum).Sum) } else { 0.0 }
    $targetRam = if ($processRows.Count -gt 0) { [double](($processRows | Measure-Object WorkingSetGiB -Sum).Sum) } else { 0.0 }

    $sample = [pscustomobject]@{
        Timestamp = $timestamp
        ElapsedSeconds = [double]$State.Stopwatch.Elapsed.TotalSeconds
        SegmentId = 0
        RecordingReason = ""
        RecordingStatus = "Observing"
        WasRecorded = $false
        ActivitySignal = $false
        ActivityReason = ""
        ProjectProcessCount = 0
        ProjectCpuPercent = 0.0
        Phase = $Phase
        CpuTotalPercent = $cpu.TotalPercent
        CpuMaxCorePercent = $cpu.MaxCorePercent
        MemoryUsedPercent = $memory.UsedPercent
        MemoryUsedGiB = $memory.UsedGiB
        MemoryAvailableGiB = $memory.AvailableGiB
        MemoryTotalGiB = $memory.TotalGiB
        GpuAvailable = [bool]$gpu.Available
        GpuNames = $gpu.Names
        GpuUtilizationPercent = $gpu.UtilizationPercent
        VramUsedPercent = $gpu.MemoryPercent
        VramUsedMiB = $gpu.MemoryUsedMiB
        VramTotalMiB = $gpu.MemoryTotalMiB
        GpuTemperatureC = $gpu.TemperatureC
        TargetCpuPercent = $targetCpu
        TargetRamGiB = $targetRam
        Processes = $processRows
    }
    $activity = Get-ProjectActivitySignal -State $State -Sample $sample
    $sample.ActivitySignal = $activity.IsActive
    $sample.ActivityReason = $activity.Reason
    $sample.ProjectProcessCount = $activity.ProjectProcessCount
    $sample.ProjectCpuPercent = $activity.ProjectCpuPercent
    Submit-MonitorSample -State $State -Sample $sample
    return $sample
}

function Get-Percentile {
    param(
        [object[]]$Values,
        [ValidateRange(0, 100)][double]$Percentile
    )

    $clean = @($Values | Where-Object { $null -ne $_ } | ForEach-Object { [double]$_ } | Sort-Object)
    if ($clean.Count -eq 0) {
        return $null
    }
    $index = [math]::Ceiling(($Percentile / 100.0) * $clean.Count) - 1
    $index = [math]::Max(0, [math]::Min($clean.Count - 1, $index))
    return [double]$clean[$index]
}

function Get-AverageOrNull {
    param([object[]]$Values)

    $clean = @($Values | Where-Object { $null -ne $_ } | ForEach-Object { [double]$_ })
    if ($clean.Count -eq 0) {
        return $null
    }
    return [double](($clean | Measure-Object -Average).Average)
}

function Get-MinimumOrNull {
    param([object[]]$Values)

    $clean = @($Values | Where-Object { $null -ne $_ } | ForEach-Object { [double]$_ })
    if ($clean.Count -eq 0) {
        return $null
    }
    return [double](($clean | Measure-Object -Minimum).Minimum)
}

function Get-MaximumOrNull {
    param([object[]]$Values)

    $clean = @($Values | Where-Object { $null -ne $_ } | ForEach-Object { [double]$_ })
    if ($clean.Count -eq 0) {
        return $null
    }
    return [double](($clean | Measure-Object -Maximum).Maximum)
}

function Get-PressureAssessment {
    param(
        [object[]]$Rows,
        [int]$LogicalProcessorCount = 1
    )

    if ($Rows.Count -lt 5) {
        return [pscustomobject]@{
            Label = "Insufficient samples"
            Signals = @()
            Advice = "Record at least five samples in this phase before drawing a conclusion."
        }
    }

    $cpuP95 = Get-Percentile @($Rows | ForEach-Object { $_.CpuTotalPercent }) 95
    $coreP95 = Get-Percentile @($Rows | ForEach-Object { $_.CpuMaxCorePercent }) 95
    $memoryP95 = Get-Percentile @($Rows | ForEach-Object { $_.MemoryUsedPercent }) 95
    $availableMin = Get-MinimumOrNull @($Rows | ForEach-Object { $_.MemoryAvailableGiB })
    $gpuP95 = Get-Percentile @($Rows | ForEach-Object { $_.GpuUtilizationPercent }) 95
    $vramP95 = Get-Percentile @($Rows | ForEach-Object { $_.VramUsedPercent }) 95
    $targetCpuP95 = Get-Percentile @($Rows | ForEach-Object { $_.ProjectCpuPercent }) 95
    $hotCoreSamples = @($Rows | Where-Object { $null -ne $_.CpuMaxCorePercent -and $_.CpuMaxCorePercent -ge 95 }).Count
    $hotCoreFraction = [double]$hotCoreSamples / [double]$Rows.Count
    $singleCoreTargetThreshold = 75.0 / [math]::Max(1, $LogicalProcessorCount)

    $signals = New-Object System.Collections.Generic.List[string]
    $advice = New-Object System.Collections.Generic.List[string]

    if (($null -ne $memoryP95 -and $memoryP95 -ge 85) -or ($null -ne $availableMin -and $availableMin -le 2)) {
        $signals.Add("Memory")
        $advice.Add("Repeat the workload with unnecessary applications closed. If pressure remains, additional system RAM is the most direct hardware change.")
    }
    if ($null -ne $vramP95 -and $vramP95 -ge 90) {
        $signals.Add("VRAM")
        $advice.Add("Inspect texture, Nanite and render-target memory. A GPU with more VRAM may help if project-side reductions are insufficient.")
    }
    if ($null -ne $gpuP95 -and $gpuP95 -ge 90) {
        $signals.Add("GPU")
        $advice.Add("Confirm with Unreal stat gpu and a fixed scene. Sustained GPU saturation can justify a faster GPU after scalability and content checks.")
    }
    if ($null -ne $cpuP95 -and $cpuP95 -ge 85) {
        $signals.Add("CPU-total")
        $advice.Add("High total CPU can limit shader compilation, cooking or packaging. Compare core count and sustained clocks before a platform upgrade.")
    }
    elseif ($null -ne $coreP95 -and $coreP95 -ge 95 -and
            $hotCoreFraction -ge 0.5 -and
            $null -ne $targetCpuP95 -and $targetCpuP95 -ge $singleCoreTargetThreshold) {
        $signals.Add("CPU-single-core")
        $advice.Add("A core stayed saturated while monitored project processes were active. This can indicate a game-thread or editor-thread limit; confirm attribution with Unreal Insights before upgrading.")
    }

    if ($signals.Count -eq 0) {
        return [pscustomobject]@{
            Label = "No sustained CPU/RAM/GPU saturation"
            Signals = @()
            Advice = "Check storage I/O, Unreal thread timing and project configuration; this monitor does not measure those causes."
        }
    }

    $label = if ($signals.Count -eq 1) {
        "$($signals[0]) pressure"
    }
    else {
        "Mixed pressure: $($signals -join ', ')"
    }
    return [pscustomobject]@{
        Label = $label
        Signals = @($signals)
        Advice = ($advice -join " ")
    }
}

function Write-SessionSummary {
    param([Parameter(Mandatory = $true)][object]$State)

    $summaryPath = Join-Path $State.Directory "summary.md"
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# CS549 Resource Monitor Summary")
    $lines.Add("")
    $lines.Add("- Session: $($State.Name)")
    $lines.Add("- Started: $($State.StartedAt.ToString('o'))")
    $lines.Add("- Observed duration: $([math]::Round($State.Stopwatch.Elapsed.TotalSeconds, 1)) seconds")
    $lines.Add("- Recording mode: $($State.RecordingMode)")
    $lines.Add("- Observed samples: $($State.ObservedSampleCount)")
    $lines.Add("- Recorded samples: $($State.Samples.Count)")
    $lines.Add("- Recorded segments: $($State.SegmentId)")
    $lines.Add("- Interval: $($State.IntervalSeconds) seconds")
    $lines.Add("- Method: Windows performance data plus nvidia-smi when available")
    $lines.Add("")
    $lines.Add("> These are investigation indicators, not proof of a hardware bottleneck. Repeat representative work and confirm gameplay with Unreal profiling tools before purchasing hardware.")
    $lines.Add("")
    $lines.Add("## Phase summary")
    $lines.Add("")
    $lines.Add("| Phase | Samples | CPU avg / p95 | Busiest core p95 | Project-process CPU p95 | RAM p95 | GPU p95 | VRAM p95 | Indicator |")
    $lines.Add("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |")

    $phaseGroups = @($State.Samples | Group-Object -Property Phase)
    $assessments = @()
    foreach ($group in $phaseGroups) {
        $rows = @($group.Group)
        $cpuAverage = Get-AverageOrNull @($rows | ForEach-Object { $_.CpuTotalPercent })
        $cpuP95 = Get-Percentile @($rows | ForEach-Object { $_.CpuTotalPercent }) 95
        $coreP95 = Get-Percentile @($rows | ForEach-Object { $_.CpuMaxCorePercent }) 95
        $memoryP95 = Get-Percentile @($rows | ForEach-Object { $_.MemoryUsedPercent }) 95
        $gpuP95 = Get-Percentile @($rows | ForEach-Object { $_.GpuUtilizationPercent }) 95
        $vramP95 = Get-Percentile @($rows | ForEach-Object { $_.VramUsedPercent }) 95
        $targetCpuP95 = Get-Percentile @($rows | ForEach-Object { $_.ProjectCpuPercent }) 95
        $assessment = Get-PressureAssessment -Rows $rows -LogicalProcessorCount $State.LogicalProcessorCount
        $assessments += [pscustomobject]@{
            Phase = $group.Name
            Assessment = $assessment
        }
        $safePhase = ([string]$group.Name).Replace('|','/')
        $lines.Add("| $safePhase | $($rows.Count) | $(Format-Number $cpuAverage 1)% / $(Format-Number $cpuP95 1)% | $(Format-Number $coreP95 1)% | $(Format-Number $targetCpuP95 1)% | $(Format-Number $memoryP95 1)% | $(Format-Number $gpuP95 1)% | $(Format-Number $vramP95 1)% | $($assessment.Label) |")
    }

    if ($phaseGroups.Count -eq 0) {
        $lines.Add("| No samples | 0 |  |  |  |  |  |  | No conclusion |")
    }

    $lines.Add("")
    $lines.Add("## Interpretation")
    $lines.Add("")
    foreach ($item in $assessments) {
        $lines.Add("### $($item.Phase)")
        $lines.Add("")
        $lines.Add("$($item.Assessment.Label). $($item.Assessment.Advice)")
        $lines.Add("")
    }

    $lines.Add("## Monitored process peaks")
    $lines.Add("")
    $lines.Add("| Process | Samples | Project-bound samples | Peak CPU | Peak working set |")
    $lines.Add("| --- | ---: | ---: | ---: | ---: |")
    $processGroups = @($State.ProcessSamples | Group-Object -Property ProcessName | Sort-Object -Property Name)
    foreach ($group in $processGroups) {
        $peakCpu = Get-MaximumOrNull @($group.Group | ForEach-Object { $_.CpuPercent })
        $peakRam = Get-MaximumOrNull @($group.Group | ForEach-Object { $_.WorkingSetGiB })
        $projectBoundCount = @($group.Group | Where-Object { $_.IsProjectBound }).Count
        $lines.Add("| $($group.Name) | $($group.Count) | $projectBoundCount | $(Format-Number $peakCpu 1)% | $(Format-Number $peakRam 2) GiB |")
    }
    if ($processGroups.Count -eq 0) {
        $lines.Add("| No monitored process observed | 0 | 0 |  |  |")
    }

    $lines.Add("")
    $lines.Add("## Recommended confirmation")
    $lines.Add("")
    $lines.Add("- Run an idle baseline, map load, shader compile, Play in Editor and package-build session separately.")
    $lines.Add("- Use Unreal Insights for game, render and worker thread timing.")
    $lines.Add("- Use stat unit and stat gpu in the same fixed gameplay route.")
    $lines.Add("- Compare repeated runs before and after closing background applications.")

    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($summaryPath, $lines, $utf8)
    return $summaryPath
}

function Complete-MonitorSession {
    param([Parameter(Mandatory = $true)][object]$State)

    if (-not $State.Closed) {
        $State.Stopwatch.Stop()
        $State.MetricsWriter.Flush()
        $State.ProcessesWriter.Flush()
        $State.MetricsWriter.Dispose()
        $State.ProcessesWriter.Dispose()
        $State.Closed = $true
    }
    return Write-SessionSummary -State $State
}

function Get-LiveSignal {
    param([Parameter(Mandatory = $true)][object]$Sample)

    $signals = @()
    if ($null -ne $Sample.MemoryUsedPercent -and $Sample.MemoryUsedPercent -ge 85) { $signals += "RAM" }
    if ($null -ne $Sample.VramUsedPercent -and $Sample.VramUsedPercent -ge 90) { $signals += "VRAM" }
    if ($null -ne $Sample.GpuUtilizationPercent -and $Sample.GpuUtilizationPercent -ge 90) { $signals += "GPU" }
    if ($null -ne $Sample.CpuTotalPercent -and $Sample.CpuTotalPercent -ge 85) { $signals += "CPU total" }
    elseif ($null -ne $Sample.CpuMaxCorePercent -and $Sample.CpuMaxCorePercent -ge 95 -and
            $Sample.ProjectCpuPercent -ge (75.0 / [math]::Max(1, [Environment]::ProcessorCount))) {
        $signals += "possible project CPU core"
    }

    if ($signals.Count -eq 0) {
        return "Current signal: no saturation threshold crossed"
    }
    return "Current signal: $($signals -join ', ') pressure"
}

function Limit-Percent {
    param([AllowNull()][object]$Value)
    if ($null -eq $Value) { return 0.0 }
    return [math]::Max(0.0, [math]::Min(100.0, [double]$Value))
}

function Start-HeadlessMonitor {
    $state = New-MonitorSession -Name $SessionName -SampleIntervalSeconds $IntervalSeconds -Destination $OutputDirectory -Targets $ProcessNames -ProjectPath $ProjectRoot -Mode $RecordingMode -PreRoll $PreRollSeconds -Grace $ActivityGraceSeconds
    Write-Host "Observing in $RecordingMode mode; output directory: $($state.Directory)"
    try {
        while ($state.Stopwatch.Elapsed.TotalSeconds -lt $DurationSeconds) {
            $sample = Add-MonitorSample -State $state -Phase $InitialPhase
            $gpuText = if ($sample.GpuAvailable) { "GPU $(Format-Number $sample.GpuUtilizationPercent 0)%" } else { "GPU unavailable" }
            Write-Host ("{0,6:N1}s  CPU {1,5}%  Core {2,5}%  RAM {3,5}%  {4}  VRAM {5,5}%  {6}" -f `
                $sample.ElapsedSeconds,
                (Format-Number $sample.CpuTotalPercent 0),
                (Format-Number $sample.CpuMaxCorePercent 0),
                (Format-Number $sample.MemoryUsedPercent 0),
                $gpuText,
                (Format-Number $sample.VramUsedPercent 0),
                $sample.RecordingStatus)
            if ($state.Stopwatch.Elapsed.TotalSeconds -lt $DurationSeconds) {
                Start-Sleep -Seconds $IntervalSeconds
            }
        }
    }
    finally {
        $summary = Complete-MonitorSession -State $state
        Write-Host "Summary: $summary"
    }
}

function Start-MonitorGui {
    Add-Type -AssemblyName PresentationFramework
    Add-Type -AssemblyName PresentationCore
    Add-Type -AssemblyName WindowsBase

    [xml]$xaml = @'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="CS549 Resource Monitor" Height="690" Width="920"
        MinHeight="620" MinWidth="820" WindowStartupLocation="CenterScreen"
        Background="#F3F5F7" FontFamily="Segoe UI">
  <Grid Margin="18">
    <Grid.RowDefinitions>
      <RowDefinition Height="Auto"/>
      <RowDefinition Height="Auto"/>
      <RowDefinition Height="Auto"/>
      <RowDefinition Height="*"/>
      <RowDefinition Height="120"/>
    </Grid.RowDefinitions>

    <TextBlock Grid.Row="0" Text="CS549 Development Resource Monitor" FontSize="25" FontWeight="SemiBold" Foreground="#172331" Margin="0,0,0,14"/>

    <Grid Grid.Row="1" Margin="0,0,0,14">
      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="65"/>
        <ColumnDefinition Width="170"/>
        <ColumnDefinition Width="58"/>
        <ColumnDefinition Width="65"/>
        <ColumnDefinition Width="45"/>
        <ColumnDefinition Width="95"/>
        <ColumnDefinition Width="52"/>
        <ColumnDefinition Width="*"/>
      </Grid.ColumnDefinitions>
      <TextBlock Grid.Column="0" Text="Session" VerticalAlignment="Center"/>
      <TextBox x:Name="SessionNameBox" Grid.Column="1" Height="28" VerticalContentAlignment="Center" Text="CS549 development" Margin="0,0,12,0"/>
      <TextBlock Grid.Column="2" Text="Interval" VerticalAlignment="Center"/>
      <ComboBox x:Name="IntervalBox" Grid.Column="3" Height="28" SelectedIndex="1" Margin="0,0,12,0">
        <ComboBoxItem Content="1"/>
        <ComboBoxItem Content="2"/>
        <ComboBoxItem Content="5"/>
      </ComboBox>
      <TextBlock Grid.Column="4" Text="Mode" VerticalAlignment="Center"/>
      <ComboBox x:Name="ModeBox" Grid.Column="5" Height="28" SelectedIndex="0" Margin="0,0,12,0">
        <ComboBoxItem Content="Auto"/>
        <ComboBoxItem Content="Always"/>
        <ComboBoxItem Content="Pause"/>
      </ComboBox>
      <TextBlock Grid.Column="6" Text="Phase" VerticalAlignment="Center"/>
      <ComboBox x:Name="PhaseBox" Grid.Column="7" Height="28" IsEditable="True" Text="Idle baseline">
        <ComboBoxItem Content="Idle baseline"/>
        <ComboBoxItem Content="Open project / map"/>
        <ComboBoxItem Content="Compile shaders"/>
        <ComboBoxItem Content="Play in Editor"/>
        <ComboBoxItem Content="Package build"/>
        <ComboBoxItem Content="Blender / asset work"/>
      </ComboBox>
    </Grid>

    <Border Grid.Row="2" Background="White" BorderBrush="#D7DDE4" BorderThickness="1" CornerRadius="6" Padding="14" Margin="0,0,0,14">
      <Grid>
        <Grid.ColumnDefinitions>
          <ColumnDefinition Width="150"/>
          <ColumnDefinition Width="*"/>
          <ColumnDefinition Width="190"/>
        </Grid.ColumnDefinitions>
        <Grid.RowDefinitions>
          <RowDefinition Height="34"/>
          <RowDefinition Height="34"/>
          <RowDefinition Height="34"/>
          <RowDefinition Height="34"/>
          <RowDefinition Height="34"/>
          <RowDefinition Height="42"/>
        </Grid.RowDefinitions>

        <TextBlock Grid.Row="0" Grid.Column="0" Text="CPU total" VerticalAlignment="Center"/>
        <ProgressBar x:Name="CpuBar" Grid.Row="0" Grid.Column="1" Height="17" Maximum="100" VerticalAlignment="Center" Foreground="#2E75B6"/>
        <TextBlock x:Name="CpuValue" Grid.Row="0" Grid.Column="2" Text="--" Margin="12,0,0,0" VerticalAlignment="Center"/>

        <TextBlock Grid.Row="1" Grid.Column="0" Text="Busiest CPU core" VerticalAlignment="Center"/>
        <ProgressBar x:Name="CoreBar" Grid.Row="1" Grid.Column="1" Height="17" Maximum="100" VerticalAlignment="Center" Foreground="#5B9BD5"/>
        <TextBlock x:Name="CoreValue" Grid.Row="1" Grid.Column="2" Text="--" Margin="12,0,0,0" VerticalAlignment="Center"/>

        <TextBlock Grid.Row="2" Grid.Column="0" Text="Physical memory" VerticalAlignment="Center"/>
        <ProgressBar x:Name="MemoryBar" Grid.Row="2" Grid.Column="1" Height="17" Maximum="100" VerticalAlignment="Center" Foreground="#70AD47"/>
        <TextBlock x:Name="MemoryValue" Grid.Row="2" Grid.Column="2" Text="--" Margin="12,0,0,0" VerticalAlignment="Center"/>

        <TextBlock Grid.Row="3" Grid.Column="0" Text="GPU utilization" VerticalAlignment="Center"/>
        <ProgressBar x:Name="GpuBar" Grid.Row="3" Grid.Column="1" Height="17" Maximum="100" VerticalAlignment="Center" Foreground="#ED7D31"/>
        <TextBlock x:Name="GpuValue" Grid.Row="3" Grid.Column="2" Text="--" Margin="12,0,0,0" VerticalAlignment="Center"/>

        <TextBlock Grid.Row="4" Grid.Column="0" Text="VRAM" VerticalAlignment="Center"/>
        <ProgressBar x:Name="VramBar" Grid.Row="4" Grid.Column="1" Height="17" Maximum="100" VerticalAlignment="Center" Foreground="#FFC000"/>
        <TextBlock x:Name="VramValue" Grid.Row="4" Grid.Column="2" Text="--" Margin="12,0,0,0" VerticalAlignment="Center"/>

        <TextBlock x:Name="SignalText" Grid.Row="5" Grid.ColumnSpan="3" Text="Ready" FontWeight="SemiBold" Foreground="#24384B" VerticalAlignment="Center"/>
      </Grid>
    </Border>

    <DataGrid x:Name="ProcessGrid" Grid.Row="3" AutoGenerateColumns="False" IsReadOnly="True" CanUserAddRows="False" HeadersVisibility="Column" GridLinesVisibility="Horizontal" Background="White" BorderBrush="#D7DDE4">
      <DataGrid.Columns>
        <DataGridTextColumn Header="Process" Binding="{Binding ProcessName}" Width="*"/>
        <DataGridTextColumn Header="PID" Binding="{Binding Id}" Width="90"/>
        <DataGridTextColumn Header="549" Binding="{Binding ProjectDisplay}" Width="65"/>
        <DataGridTextColumn Header="CPU %" Binding="{Binding CpuDisplay}" Width="110"/>
        <DataGridTextColumn Header="RAM GiB" Binding="{Binding RamDisplay}" Width="110"/>
      </DataGrid.Columns>
    </DataGrid>

    <Grid Grid.Row="4" Margin="0,12,0,0">
      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="Auto"/>
        <ColumnDefinition Width="Auto"/>
        <ColumnDefinition Width="Auto"/>
        <ColumnDefinition Width="*"/>
      </Grid.ColumnDefinitions>
      <Button x:Name="StartButton" Grid.Column="0" Content="Start monitoring" Width="135" Height="34" Margin="0,0,10,0" Background="#2E75B6" Foreground="White" FontWeight="SemiBold"/>
      <Button x:Name="StopButton" Grid.Column="1" Content="Stop and summarize" Width="145" Height="34" Margin="0,0,10,0" IsEnabled="False"/>
      <Button x:Name="OpenButton" Grid.Column="2" Content="Open output" Width="110" Height="34" Margin="0,0,12,0"/>
      <TextBox x:Name="LogBox" Grid.Column="3" IsReadOnly="True" TextWrapping="Wrap" VerticalScrollBarVisibility="Auto" Background="#172331" Foreground="#E8EEF4" Padding="8" FontFamily="Consolas" FontSize="12"/>
    </Grid>
  </Grid>
</Window>
'@

    $reader = New-Object System.Xml.XmlNodeReader $xaml
    $window = [Windows.Markup.XamlReader]::Load($reader)

    $sessionBox = $window.FindName("SessionNameBox")
    $intervalBox = $window.FindName("IntervalBox")
    $modeBox = $window.FindName("ModeBox")
    $phaseBox = $window.FindName("PhaseBox")
    $cpuBar = $window.FindName("CpuBar")
    $coreBar = $window.FindName("CoreBar")
    $memoryBar = $window.FindName("MemoryBar")
    $gpuBar = $window.FindName("GpuBar")
    $vramBar = $window.FindName("VramBar")
    $cpuValue = $window.FindName("CpuValue")
    $coreValue = $window.FindName("CoreValue")
    $memoryValue = $window.FindName("MemoryValue")
    $gpuValue = $window.FindName("GpuValue")
    $vramValue = $window.FindName("VramValue")
    $signalText = $window.FindName("SignalText")
    $processGrid = $window.FindName("ProcessGrid")
    $startButton = $window.FindName("StartButton")
    $stopButton = $window.FindName("StopButton")
    $openButton = $window.FindName("OpenButton")
    $logBox = $window.FindName("LogBox")

    $sessionBox.Text = $SessionName
    $phaseBox.Text = $InitialPhase
    $modeBox.SelectedIndex = switch ($RecordingMode) { "Always" { 1 } "Pause" { 2 } default { 0 } }
    $script:GuiMonitorState = $null
    $script:LastOutputDirectory = $OutputDirectory
    $script:LastRecordingStatus = ""
    $timer = New-Object Windows.Threading.DispatcherTimer

    $appendLog = {
        param([string]$Message)
        $logBox.AppendText("[$(Get-Date -Format 'HH:mm:ss')] $Message`r`n")
        $logBox.ScrollToEnd()
    }

    $updateUi = {
        param([object]$Sample)
        $cpuBar.Value = Limit-Percent $Sample.CpuTotalPercent
        $coreBar.Value = Limit-Percent $Sample.CpuMaxCorePercent
        $memoryBar.Value = Limit-Percent $Sample.MemoryUsedPercent
        $gpuBar.Value = Limit-Percent $Sample.GpuUtilizationPercent
        $vramBar.Value = Limit-Percent $Sample.VramUsedPercent

        $cpuValue.Text = "$(Format-Number $Sample.CpuTotalPercent 0)%"
        $coreValue.Text = "$(Format-Number $Sample.CpuMaxCorePercent 0)%"
        $memoryValue.Text = "$(Format-Number $Sample.MemoryUsedPercent 0)%  ($(Format-Number $Sample.MemoryAvailableGiB 1) GiB free)"
        if ($Sample.GpuAvailable) {
            $gpuValue.Text = "$(Format-Number $Sample.GpuUtilizationPercent 0)%  ($(Format-Number $Sample.GpuTemperatureC 0) C)"
            $vramValue.Text = "$(Format-Number $Sample.VramUsedPercent 0)%  ($(Format-Number ($Sample.VramUsedMiB / 1024.0) 1) / $(Format-Number ($Sample.VramTotalMiB / 1024.0) 1) GiB)"
        }
        else {
            $gpuValue.Text = "Unavailable"
            $vramValue.Text = "Unavailable"
        }
        $signalText.Text = "$($Sample.RecordingStatus) | $(Get-LiveSignal -Sample $Sample)"
        if ($Sample.RecordingStatus -ne $script:LastRecordingStatus) {
            & $appendLog $Sample.RecordingStatus
            $script:LastRecordingStatus = $Sample.RecordingStatus
        }

        $rows = @($Sample.Processes | ForEach-Object {
            [pscustomobject]@{
                ProcessName = $_.ProcessName
                Id = $_.Id
                ProjectDisplay = if ($_.IsProjectBound) { "Yes" } else { "" }
                CpuDisplay = Format-Number $_.CpuPercent 1
                RamDisplay = Format-Number $_.WorkingSetGiB 2
            }
        })
        $processGrid.ItemsSource = $null
        $processGrid.ItemsSource = $rows
    }

    $sampleNow = {
        if ($null -eq $script:GuiMonitorState) {
            return
        }
        try {
            $selectedMode = $modeBox.SelectedItem
            if ($selectedMode -and $selectedMode.Content) {
                $script:GuiMonitorState.RecordingMode = [string]$selectedMode.Content
            }
            $sample = Add-MonitorSample -State $script:GuiMonitorState -Phase ([string]$phaseBox.Text)
            & $updateUi $sample
        }
        catch {
            & $appendLog "Sample failed: $($_.Exception.Message)"
        }
    }

    $timer.Add_Tick($sampleNow)

    $startMonitoring = {
        try {
            $selected = $intervalBox.SelectedItem
            $selectedText = if ($selected -and $selected.Content) { [string]$selected.Content } else { "2" }
            $interval = [int]$selectedText
            $name = [string]$sessionBox.Text
            if ([string]::IsNullOrWhiteSpace($name)) { $name = "CS549 development" }
            $selectedMode = $modeBox.SelectedItem
            $mode = if ($selectedMode -and $selectedMode.Content) { [string]$selectedMode.Content } else { "Auto" }
            $script:GuiMonitorState = New-MonitorSession -Name $name -SampleIntervalSeconds $interval -Destination $OutputDirectory -Targets $ProcessNames -ProjectPath $ProjectRoot -Mode $mode -PreRoll $PreRollSeconds -Grace $ActivityGraceSeconds
            $script:LastOutputDirectory = $script:GuiMonitorState.Directory
            $script:LastRecordingStatus = ""
            $timer.Interval = [TimeSpan]::FromSeconds($interval)
            $timer.Start()
            $startButton.IsEnabled = $false
            $stopButton.IsEnabled = $true
            $sessionBox.IsEnabled = $false
            $intervalBox.IsEnabled = $false
            & $appendLog "Monitoring started in $mode mode: $($script:GuiMonitorState.Directory)"
            & $sampleNow
        }
        catch {
            & $appendLog "Start failed: $($_.Exception.Message)"
        }
    }
    $startButton.Add_Click($startMonitoring)

    $stopButton.Add_Click({
        if ($null -eq $script:GuiMonitorState) {
            return
        }
        try {
            $timer.Stop()
            $report = Complete-MonitorSession -State $script:GuiMonitorState
            & $appendLog "Stopped. Summary: $report"
            $signalText.Text = "Session complete. Review summary.md before making an upgrade decision."
        }
        catch {
            & $appendLog "Stop failed: $($_.Exception.Message)"
        }
        finally {
            $script:GuiMonitorState = $null
            $startButton.IsEnabled = $true
            $stopButton.IsEnabled = $false
            $sessionBox.IsEnabled = $true
            $intervalBox.IsEnabled = $true
        }
    })

    $openButton.Add_Click({
        try {
            if (-not (Test-Path -LiteralPath $script:LastOutputDirectory)) {
                New-Item -ItemType Directory -Path $script:LastOutputDirectory -Force | Out-Null
            }
            Start-Process explorer.exe -ArgumentList @($script:LastOutputDirectory)
        }
        catch {
            & $appendLog "Could not open output: $($_.Exception.Message)"
        }
    })

    $window.Add_Closing({
        if ($null -ne $script:GuiMonitorState) {
            try {
                $timer.Stop()
                Complete-MonitorSession -State $script:GuiMonitorState | Out-Null
            }
            catch {
            }
            $script:GuiMonitorState = $null
        }
    })

    & $appendLog "Ready. Change the phase label as your task changes."
    if (-not $script:NvidiaSmiPath) {
        & $appendLog "nvidia-smi was not found. CPU and memory monitoring remain available."
    }
    if ($AutoStart) {
        $window.Add_ContentRendered({
            if ($null -eq $script:GuiMonitorState) {
                & $startMonitoring
            }
        })
    }
    [void]$window.ShowDialog()
}

$script:NvidiaSmiPath = Resolve-NvidiaSmi

$workspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = $workspaceRoot
}
else {
    $ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
}

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $workspaceRoot "Saved\PerformanceMonitor"
}
else {
    $OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
}

if ($NoGui) {
    Start-HeadlessMonitor
}
else {
    Start-MonitorGui
}
