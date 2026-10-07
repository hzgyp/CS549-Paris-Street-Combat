param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
 [ValidateSet('author','visual')][string]$Mode='author')
$ErrorActionPreference='Stop'
throw 'AN003 stop-lock: binding/contact proof failed sleeve/view acceptance. Read failure/result and use a different authorized implementation; do not rerun this fixture.'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'No concurrent Unreal writer'}
$taskLog=Join-Path $taskRoot "tmp/reload-contact-binding-v3/$Identity.log"
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadContactBindingV3/$Identity"
if((Test-Path -LiteralPath $taskLog) -or (Test-Path -LiteralPath $taskOut)){throw 'Preserve occupied proof identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$env:CS549_APPROVED_IDENTITY=$Identity
$taskMap=if($Mode -eq 'author'){'/Engine/Maps/Entry'}else{'/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'}
$taskScript=Join-Path $PSScriptRoot "ue_reload_approved_v4_$Mode.py"
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),$taskMap,
 '-DisablePlugins=ParisEditorBridge','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',
 ('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "Bounded V4 $Mode PID $($taskProcess.Id), log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(6)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000) | Out-Null; $taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Task-owned proof timeout; evidence retained'}
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;mode=$Mode;identity=$Identity} | ConvertTo-Json | Set-Content -LiteralPath ($taskLog+'.exit.json')
Get-Content -LiteralPath ($taskLog+'.exit.json')
