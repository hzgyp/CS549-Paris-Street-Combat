param(
 [Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
 [ValidateSet('saved','actions')][string]$Scope='saved'
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'User/editor session still open; no concurrent process'}
$taskLog=Join-Path $taskRoot "tmp/reload-contact-binding-v3/$Identity.log"
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadContactBindingV3/$Identity"
if((Test-Path -LiteralPath $taskLog) -or (Test-Path -LiteralPath $taskOut)){throw 'Preserve occupied identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$env:CS549_BINDING_IDENTITY=$Identity
$env:CS549_BINDING_SCOPE=$Scope
$taskScript=Join-Path $PSScriptRoot 'ue_reload_game_binding_v3.py'
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-DisablePlugins=ParisEditorBridge',
 '-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',
 ('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "Disposable binding probe $Scope PID $($taskProcess.Id), log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(5)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000) | Out-Null; $taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Task-owned probe timed out; evidence retained'}
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;scope=$Scope;identity=$Identity} | ConvertTo-Json | Set-Content -LiteralPath ($taskLog+'.exit.json')
Get-Content -LiteralPath ($taskLog+'.exit.json')
