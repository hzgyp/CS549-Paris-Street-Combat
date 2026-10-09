param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Existing engine/build process; preserve it'}
$taskPython='C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython (Join-Path $PSScriptRoot 'prepare_build.py') $Identity
if($LASTEXITCODE -ne 0){throw 'Build preparation failed'}
$taskOut=Join-Path $taskRoot ('tmp/mvp-closeout-20261008/'+$Identity)
$taskProject=Join-Path $taskOut 'Project/WW2FranceLiberation.uproject'
$taskArgs=@('BuildCookRun','-nop4',('-project='+$taskProject),'-installed','-platform=Win64','-clientconfig=Development',
 '-build','-cook','-stage','-pak','-iostore','-archive',('-archivedirectory='+$taskOut+'/Archive'),
 '-map=/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1','-unattended','-utf8output','-unrealexe=UnrealEditor-Cmd.exe',
 '-nocompileeditor','-skipbuildeditor','-nodebuginfo','-AdditionalCookerOptions=-CookProcessCount=1 -DisablePlugins=ParisEditorBridge -DisablePython')
$taskReceipt=[ordered]@{identity=$Identity;started=(Get-Date).ToString('o');arguments=$taskArgs;status='running'}
$taskReceipt|ConvertTo-Json -Depth 6|Set-Content (Join-Path $taskOut 'build.json') -Encoding utf8
try{
 & 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' @taskArgs 2>&1|Tee-Object -FilePath (Join-Path $taskOut 'uat.log')
 $taskReceipt.exit_code=$LASTEXITCODE
 $taskReceipt.status=if($LASTEXITCODE -eq 0){'built_runtime_unverified'}else{'build_failed'}
}catch{$taskReceipt.exit_code=1;$taskReceipt.status='launcher_failed';$taskReceipt.error=$_.Exception.ToString()}
$taskReceipt.finished=(Get-Date).ToString('o')
$taskReceipt|ConvertTo-Json -Depth 6|Set-Content (Join-Path $taskOut 'build.json') -Encoding utf8
exit $taskReceipt.exit_code
