param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
      [ValidateSet('Query','Traversal','Height')][string]$Stage='Query')
$ErrorActionPreference='Stop'
if ($Stage -eq 'Traversal') { throw 'ML001 stopped occupied-anchor fixture; do not rerun. Height has a separate bounded plan.' }
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if (Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue) { throw 'Competing engine: preserve its ownership; survey not started' }
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MissionConnectivityV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/mission-connectivity-v1/$Identity.log"
if ((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)) { throw 'Preserve existing run identity' }
New-Item -ItemType Directory -Path $taskOut | Out-Null
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$taskSource=if ($Stage -eq 'Height') {'ue_traverse_connectivity.py'} else {'ue_query_connectivity.py'}
$taskReport=if ($Stage -eq 'Height') {'traversal.json'} else {'query.json'}
$taskScript=Join-Path $taskOut $taskSource
Copy-Item -LiteralPath (Join-Path $PSScriptRoot $taskSource) -Destination $taskScript
$env:CS549_CONNECT_ROOT=$taskRoot
$env:CS549_CONNECT_OUT=$taskOut
$env:CS549_CONNECT_KIND=if ($Stage -eq 'Height') {'height_only'} else {'query'}
$taskArgs=@(
 ('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Engine/Maps/Entry','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',
 '-DisablePlugins=ParisEditorBridge',('-ExecCmds="py '+$taskScript.Replace('\','/')+'"'),
 ('-abslog="'+$taskLog+'"'))
$taskEngine=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "Read-only connectivity PID $($taskEngine.Id); $taskOut"
$taskDeadline=(Get-Date).AddMinutes($(if ($Stage -eq 'Height') {12} else {7}))
while (-not $taskEngine.HasExited -and (Get-Date) -lt $taskDeadline) {
 $taskEngine.WaitForExit(1000) | Out-Null
 $taskEngine.Refresh()
}
if (-not $taskEngine.HasExited) {
 Stop-Process -Id $taskEngine.Id
 throw 'Task-owned survey timed out; evidence retained'
}
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut $taskReport) -Raw | ConvertFrom-Json
$taskErrors=@(Select-String -LiteralPath $taskLog -Pattern 'Error:|Fatal:|Ensure condition failed|=== Handled ensure|RegistrationFailed_AgentNotValid|NavData.*will be removed')
$taskResult | Select-Object status,summary,errors,protected_bytes_unchanged | ConvertTo-Json -Depth 5
if ($taskEngine.ExitCode -ne 0 -or $taskResult.errors.Count -or -not $taskResult.protected_bytes_unchanged -or $taskErrors.Count) { throw 'Survey/API/log gate failed; preserve evidence' }
Write-Output 'Current navigation queries completed; physical movement and vertical topology remain unaccepted.'
