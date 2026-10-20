param([int]$Port = 0, [ValidateSet('127.0.0.1','0.0.0.0')][string]$BindAddress = '', [switch]$NoBrowser, [switch]$KeepAccessLink)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskPython = Join-Path $taskRoot 'Assets/LocalWorking/AssetWorkbench/runtime/venv/Scripts/python.exe'
$localConfig = Join-Path $taskRoot 'Assets/LocalWorking/AssetWorkbench/config.local.json'
$taskConfig = if (Test-Path -LiteralPath $localConfig) { Get-Content -LiteralPath $localConfig -Raw | ConvertFrom-Json } else { $null }
if ($Port -eq 0) { $Port = if ($taskConfig.port) { $taskConfig.port } else { 8765 } }
if (-not $BindAddress) { $BindAddress = if ($taskConfig.host) { $taskConfig.host } else { '127.0.0.1' } }
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Run setup.ps1 first.' }
$taskSession = Join-Path $taskRoot 'Assets/LocalWorking/AssetWorkbench/runtime/session.json'
function Test-WorkbenchProcess($Process, $Session) {
    return $Process -and $Session.port -eq $Port -and $Process.CommandLine.Contains($taskPython) -and $Process.CommandLine.Contains("-m app.cli serve --port $Port")
}
if (Test-Path -LiteralPath $taskSession) {
    $existing = Get-Content -LiteralPath $taskSession -Raw | ConvertFrom-Json
    $running = Get-CimInstance Win32_Process -Filter "ProcessId=$($existing.pid)" -ErrorAction SilentlyContinue
    if (Test-WorkbenchProcess $running $existing) {
        $existingBind = if ($existing.host) { $existing.host } else { '127.0.0.1' }
        if ($existingBind -ne $BindAddress) { throw "Existing Asset Workbench listens on $existingBind. Restart its service to apply $BindAddress." }
        $expectedExternal = if ($BindAddress -eq '0.0.0.0') { [string]$taskConfig.external_url } else { '' }
        if ([string]$existing.external_url -ne $expectedExternal) { throw 'External sharing address changed. Restart the Asset Workbench service to apply it.' }
        if (-not $NoBrowser) { Start-Process "http://127.0.0.1:$Port/#token=$($existing.token)" }
        Write-Output "Existing Asset Workbench: http://127.0.0.1:$Port"
        exit 0
    }
}
$runArgs = @('-m','app.cli','serve','--port',"$Port",'--host',$BindAddress)
if ($KeepAccessLink) { $runArgs += '--reuse-access-link' }
if (-not $NoBrowser) { $runArgs += '--open-browser' }
$logRoot = Join-Path $taskRoot 'Assets/LocalWorking/AssetWorkbench/runs'
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$owned = Start-Process -FilePath $taskPython -ArgumentList $runArgs -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logRoot "$stamp-service.out.log") -RedirectStandardError (Join-Path $logRoot "$stamp-service.err.log") -PassThru
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    if ($owned.HasExited) { throw "Asset Workbench exited. See $logRoot/$stamp-service.err.log" }
    try {
        $ready = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/" -UseBasicParsing -TimeoutSec 1
        if ($ready.StatusCode -eq 200 -and (Test-Path -LiteralPath $taskSession)) {
            $currentSession = Get-Content -LiteralPath $taskSession -Raw | ConvertFrom-Json
            $currentProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$($currentSession.pid)" -ErrorAction SilentlyContinue
            if ((Test-WorkbenchProcess $currentProcess $currentSession) -and ($currentProcess.ParentProcessId -eq $owned.Id -or $currentProcess.ProcessId -eq $owned.Id)) { Write-Output "Asset Workbench ready: http://127.0.0.1:$Port"; exit 0 }
        }
    } catch { }
    Start-Sleep -Milliseconds 250
}
throw "Asset Workbench did not become ready. See $logRoot/$stamp-service.err.log"
