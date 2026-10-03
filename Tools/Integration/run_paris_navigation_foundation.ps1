param([Parameter(Mandatory=$true)][ValidateSet('Author','Resave','Fresh')][string]$Mode,
      [Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
      [switch]$NullRHI,
      [ValidateSet('CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json','CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json','CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json','CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json')]
      [string]$NativeCheckpoint='CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json')
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if (Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue) { throw 'Close competing engines first' }
$taskEvidence = Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/NavigationFoundation/$Identity"
$taskLogs = Join-Path $taskRoot 'tmp/paris-navigation-ai-20261002'
$taskLog = Join-Path $taskLogs "foundation_$Identity.log"
if ((Test-Path -LiteralPath $taskEvidence) -or (Test-Path -LiteralPath $taskLog)) { throw 'Preserve occupied run identity' }
New-Item -ItemType Directory -Path $taskLogs -Force | Out-Null
$env:CS549_NAV_FOUNDATION_IDENTITY = $Identity
$env:CS549_NAV_FOUNDATION_AUTHOR = if ($Mode -in @('Author','Resave')) { '1' } else { '0' }
$env:CS549_NAV_FOUNDATION_RESAVE = if ($Mode -eq 'Resave') { '1' } else { '0' }
$env:CS549_NAV_FOUNDATION_LOG = $taskLog
if ($Mode -ne 'Fresh' -and $NativeCheckpoint -ne 'CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json') { throw 'Later weapon checkpoints are fresh-test only' }
$env:CS549_NAV_NATIVE_CHECKPOINT = $NativeCheckpoint
$taskRender = if ($NullRHI) { '-NullRHI' } else { '-RenderOffscreen' }
$taskArgs = @(
    ('"' + (Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject') + '"'),
    '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1',$taskRender,'-unattended','-NoSplash','-NoSound','-NoP4',
    '-DisablePlugins=ParisEditorBridge',
    ('-ExecutePythonScript="' + (Join-Path $PSScriptRoot 'ue_paris_navigation_foundation.py') + '"'),
    ('-abslog="' + $taskLog + '"'))
$taskEngine = Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "Navigation $Mode PID $($taskEngine.Id); evidence $taskEvidence"
$taskDeadline = (Get-Date).AddMinutes(12)
while (-not $taskEngine.HasExited -and (Get-Date) -lt $taskDeadline) {
    $taskEngine.WaitForExit(1000) | Out-Null
    $taskEngine.Refresh()
}
if (-not $taskEngine.HasExited) {
    Stop-Process -Id $taskEngine.Id
    throw 'Navigation task-owned process timed out; preserve its partial evidence'
}
$taskResult = Get-Content -LiteralPath (Join-Path $taskEvidence 'result.json') -Raw | ConvertFrom-Json
$taskResult | Select-Object status,summary,errors,protected_bytes_unchanged | ConvertTo-Json -Depth 5
$taskEngineErrors = @(Select-String -LiteralPath $taskLog -Pattern 'Error:|Fatal:|Ensure condition failed|=== Handled ensure')
$taskRegistrationErrors = @(Select-String -LiteralPath $taskLog -Pattern 'RegistrationFailed_AgentNotValid|NavData.*will be removed')
if ($Mode -eq 'Fresh' -and $taskRegistrationErrors.Count) { throw 'Fresh-load nav-data registration/replacement warning: not a retained-data pass' }
if ($taskEngine.ExitCode -ne 0 -or $taskResult.status -eq 'failed' -or -not $taskResult.protected_bytes_unchanged -or $taskEngineErrors.Count) {
    throw "Navigation/report/log failure; inspect preserved report and $taskLog"
}
Write-Output 'Engine exit and bounded navigation report/log checks passed; not AI/mission acceptance.'
