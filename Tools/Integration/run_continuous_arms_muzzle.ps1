param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close existing Unreal sessions first'}
$taskLog=Join-Path $taskRoot "tmp/continuous-arms-v3/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied identity'}
$env:CS549_COMBAT_PIE_IDENTITY=$Identity
$env:CS549_CITY_NATIVE_CHECKPOINT='CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json'
$env:CS549_CONTINUOUS_ARMS_MUZZLE_PREVIEW='1'
$env:CS549_PLAYER_AIM_PREVIEW='0';$env:CS549_FIRST_PERSON_VIEW_PREVIEW='0'
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-DisablePlugins=ParisEditorBridge','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',
 ('-ExecCmds="py '+((Join-Path $PSScriptRoot 'ue_paris_combat_pie.py') -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "Continuous arms muzzle regression PID $($taskProcess.Id)"
$taskDeadline=(Get-Date).AddMinutes(7)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Task-owned probe timeout'}
@{exit_code=$taskProcess.ExitCode;identity=$Identity;dispatch='console';log=$taskLog}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json')
Get-Content -LiteralPath ($taskLog+'.exit.json')
