param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$BuildIdentity,
      [Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Identity,
      [ValidateSet('CITY_PACKAGE_DRAFT_INVENTORY_20261002.json','CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json','CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json','CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json','CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json')]
      [string]$NativeInventory = 'CITY_PACKAGE_DRAFT_INVENTORY_20261002.json')
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskBuildDir = Join-Path $taskRoot "tmp/paris-city-package-20261002/$BuildIdentity"
$taskBuild = Get-Content -LiteralPath (Join-Path $taskBuildDir 'build_record.json') -Raw | ConvertFrom-Json
if ($taskBuild.exit_code -ne 0 -or -not $taskBuild.guarded_bytes_unchanged) { throw 'Require an actually successful guarded build' }
if ($taskBuild.native_inventory -and $taskBuild.native_inventory -ne $NativeInventory) { throw 'Build/current native inventory mismatch' }
if (-not $taskBuild.native_inventory -and $NativeInventory -ne 'CITY_PACKAGE_DRAFT_INVENTORY_20261002.json') { throw 'Old build is not the selected native-increment package' }
if (Get-Process UnrealEditor,UnrealEditor-Cmd,WW2FranceLiberation -ErrorAction SilentlyContinue) { throw 'Close affected processes first' }
$taskExe = @(Get-ChildItem -LiteralPath (Join-Path $taskBuildDir 'Archive') -Filter 'WW2FranceLiberation.exe' -Recurse | Where-Object FullName -Match '[\\/]Binaries[\\/]Win64[\\/]')
if ($taskExe.Count -ne 1) { throw 'Expected one archived game binary, not a bootstrap parent' }
$taskOut = Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/Packaging/$Identity"
if (Test-Path -LiteralPath $taskOut) { throw 'Preserve occupied startup evidence' }
New-Item -ItemType Directory -Path $taskOut | Out-Null
$taskNativeHashes = @{}
foreach ($taskName in @('RELOAD_DRAFT_SNAPSHOT_20261002.json',$NativeInventory)) {
    $taskInventory = Get-Content -LiteralPath (Join-Path $taskRoot "Assets/Integration/$taskName") -Raw | ConvertFrom-Json
    foreach ($taskItem in $taskInventory.files) {
        $taskPath = Join-Path $taskRoot $taskItem.path
        $taskHash = (Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($taskHash -ne $taskItem.sha256) { throw "Native checkpoint conflict: $taskPath" }
        $taskNativeHashes[$taskPath] = $taskHash
    }
}
$taskUserDir = (Join-Path $taskOut 'User').Replace('\','/')
$taskCsv = (Join-Path $taskUserDir 'Saved/Profiling/CSV/initial_frames.csv').Replace('\','/')
New-Item -ItemType Directory -Path (Split-Path -Parent $taskCsv) -Force | Out-Null
$taskPng = (Join-Path $taskOut 'packaged_view.png').Replace('\','/')
$taskLog = Join-Path $taskOut 'game.log'
$taskExec = 'r.SetRes 1920x1080w,sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.VSync 0,t.MaxFPS 0,csvprofile STARTFILE=initial_frames,csvprofile FRAMES=600'
$taskArgs = @('-RenderOffscreen','-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-NoSound','-unattended',
    '-ExitAfterCsvProfiling','-csvCompression=0','-csvGpuStats',('-UserDir="' + $taskUserDir + '"'),('-abslog="' + $taskLog + '"'),
    ('-ExecCmds="' + $taskExec + '"'),('-csvExecCmds="500:Shot SHOWUI -nosuffix filename=' + $taskPng + '"'))
$taskRecord = [ordered]@{ identity=$Identity; build_identity=$BuildIdentity; started_at=(Get-Date).ToString('o')
    native_inventory=$NativeInventory
    scope='Packaged stationary offscreen startup only; not physical input, warmed route, AI/mission or target-FPS acceptance'
    executable=$taskExe[0].FullName; executable_sha256=(Get-FileHash -LiteralPath $taskExe[0].FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    resolution='1920x1080'; scalability='High, ten sg.*Quality=2'; screen_percentage=100; arguments=$taskArgs }
$taskProcess = Start-Process -FilePath $taskExe[0].FullName -WorkingDirectory $taskExe[0].DirectoryName -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskRecord.pid = $taskProcess.Id
$taskRecord | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'result.json') -Encoding utf8
Write-Output "Packaged startup PID $($taskProcess.Id); evidence $taskOut"
try {
    $taskDeadline = (Get-Date).AddMinutes(5)
    while (-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline) { $taskProcess.WaitForExit(1000) | Out-Null; $taskProcess.Refresh() }
    if (-not $taskProcess.HasExited) {
        $taskRecord.status = 'failed_timeout_owned_process_terminated'
        Stop-Process -Id $taskProcess.Id
    } else {
        $taskRecord.exit_code = $taskProcess.ExitCode
        $taskRecord.status = if ($taskProcess.ExitCode -eq 0) { 'completed_inspect_log_and_view_before_pass' } else { 'failed_game_exit' }
    }
} finally {
    $taskRecord.finished_at = (Get-Date).ToString('o')
    $taskRecord.capture_exists = Test-Path -LiteralPath $taskCsv
    $taskRecord.screenshot_exists = Test-Path -LiteralPath $taskPng
    if ($taskRecord.screenshot_exists) {
        $taskPngHeader = [IO.File]::ReadAllBytes($taskPng)
        $taskW = $taskPngHeader[16..19]; $taskH = $taskPngHeader[20..23]
        [array]::Reverse($taskW); [array]::Reverse($taskH)
        $taskRecord.observed_screenshot_resolution = ([BitConverter]::ToInt32($taskW,0).ToString() + 'x' + [BitConverter]::ToInt32($taskH,0).ToString())
        $taskRecord.requested_resolution_matched = $taskRecord.observed_screenshot_resolution -eq '1920x1080'
    }
    $taskRecord.guarded_bytes_unchanged = @($taskNativeHashes.Keys | Where-Object { (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskNativeHashes[$_] }).Count -eq 0
    $taskRecord | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'result.json') -Encoding utf8
}
if ($taskRecord.status -like 'failed*' -or -not $taskRecord.guarded_bytes_unchanged) { exit 1 }
exit 0
