$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,blender* -ErrorAction SilentlyContinue){throw 'Preserve existing editor'}
$taskLog=Join-Path $taskRoot 'tmp/german-npc-formal-v14/ordinary_game_v2.log'
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied game entry'}
$taskProject=Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
$taskArgs='"'+$taskProject+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -game -unattended -DisablePlugins=ParisEditorBridge,PythonScriptPlugin -NoP4 -NoSplash -windowed -ResX=1280 -ResY=720 -seconds=35 -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;identity='ordinary_game_v2';python_disabled=$true;unattended=$true}|ConvertTo-Json
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;identity='ordinary_game_v2'}|ConvertTo-Json | Set-Content -LiteralPath "$taskLog.exit.json"
if($taskProcess.ExitCode -ne 0){throw 'Ordinary game failed'}
$taskText=Get-Content -LiteralPath $taskLog -Raw
if(([regex]::Matches($taskText,'PARIS_GERMAN_GRIP_READY')).Count -ne 3 -or ([regex]::Matches($taskText,'PARIS_ALLIED_GRIP_READY')).Count -ne 2 -or $taskText -match 'PARIS_(GERMAN|ALLIED)_GRIP_FAILURE'){throw 'Both saved faction policies must bind natively'}
Select-String -LiteralPath $taskLog -Pattern 'PARIS_GERMAN_GRIP_READY','PARIS_ALLIED_GRIP_READY'
