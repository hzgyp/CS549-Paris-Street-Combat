param([string]$EngineEditor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot 'tmp/team-sync-20261008-v1'
if(Get-Process UnrealEditor*,blender -ErrorAction SilentlyContinue){throw 'Preserve active native writer/session'}
if(Test-Path -LiteralPath (Join-Path $taskOut 'audit.log')){throw 'Preserve occupied read-only audit identity'}
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '-run=pythonscript',('-script="'+(Join-Path $PSScriptRoot 'ue_audit.py')+'"'),
 '-EnablePlugins=ParisBridgeMissionV1','-DisablePlugins=ParisEditorBridge',
 '-unattended','-NoP4','-NoSplash','-NullRHI',('-abslog="'+(Join-Path $taskOut 'audit.log')+'"'))
$taskProcess=Start-Process -FilePath $EngineEditor -ArgumentList $taskArgs -WindowStyle Hidden -PassThru -Wait
@{exit_code=$taskProcess.ExitCode;read_only=$true;pid=$taskProcess.Id}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'audit-exit.json')
if($taskProcess.ExitCode -ne 0){throw 'Read-only dependency audit failed; preserve log and receipt'}
