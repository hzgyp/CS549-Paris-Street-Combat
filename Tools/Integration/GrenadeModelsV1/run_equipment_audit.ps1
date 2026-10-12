$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot 'tmp/g1-grenade-models-20261011/asset_lookup'
New-Item -ItemType Directory -Path $taskOut -Force | Out-Null
$taskProject=Join-Path $taskRoot 'tmp/g1-tactical-equipment-20261010/candidate_full_v16/Project/WW2FranceLiberation.uproject'
$taskScript=Join-Path $PSScriptRoot 'ue_inspect_equipment.py'
$taskLog=Join-Path $taskOut 'equipment-v1-engine.log'
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied audit'}
$taskArgs=@(('"'+$taskProject+'"'),'-run=pythonscript',('-script="'+$taskScript+'"'),'-EnablePlugins=PythonScriptPlugin,GLTFExporter','-NullRHI','-unattended','-NoP4','-NoSplash','-nosound','-DDC=InstalledNoZenLocalFallback','-UDPMESSAGING_TRANSPORT_ENABLE=false',('-abslog="'+$taskLog+'"'))
$taskProc=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
[ordered]@{pid=$taskProc.Id;project=$taskProject;script=$taskScript;native_save=$false} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'equipment-v1-launch.json')
$taskProc.WaitForExit()
[ordered]@{pid=$taskProc.Id;exit_code=$taskProc.ExitCode;finished=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'equipment-v1-exit.json')
Get-Content -LiteralPath $taskLog -Tail 7
if($taskProc.ExitCode -ne 0){throw 'Preserve failed audit'}
