param([Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
 [ValidateSet('author','headings','bridgehook','staging','test','plain')][string]$Mode='test',
 [ValidateSet('ready','functional','load','travel','encounter','outcomes','view','spawnview','lifecycle')][string]$Stage='ready')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve occupied native slot'}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/G1MissionV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/g1-mission-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve previous entry'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$env:CS549_G1_OUT=$taskOut;$env:CS549_G1_STAGE=$Stage;$env:CS549_G1_ROOT=$taskRoot
New-Item -ItemType Directory -Path $taskOut | Out-Null
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskOut 'launcher_source.ps1')
$taskPlugin=Join-Path $taskRoot 'Unreal/ParisStreetCombat/Plugins/ParisBridgeMissionV1'
$taskRuntimeFiles=@(Get-Item -LiteralPath (Join-Path $taskPlugin 'ParisBridgeMissionV1.uplugin'))+@(Get-ChildItem -LiteralPath (Join-Path $taskPlugin 'Source') -File -Recurse)+@(Get-ChildItem -LiteralPath (Join-Path $taskPlugin 'Binaries/Win64') -Filter *.dll -File)
@{files=@($taskRuntimeFiles | ForEach-Object {@{path=[IO.Path]::GetRelativePath($taskRoot,$_.FullName).Replace('\','/');size_bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'runtime_manifest.json')
$taskProject=Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
$taskArgs=@(('"'+$taskProject+'"'),'/Engine/Maps/Entry','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound','-EnablePlugins=ParisBridgeMissionV1,ParisMapSurveyV1,ParisFormalSurveyV1',('-abslog="'+$taskLog+'"'))
$taskStaging=Test-Path -LiteralPath (Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/G1MissionV1/staging_author_v2_20261008/result.json')
if($Stage -in @('functional','load')){$taskArgs+=$(if($taskStaging){'-ParisSavePrefix=G1Functional4_20261008'}else{'-ParisSavePrefix=G1Functional2_20261008'})}
if($Stage -eq 'outcomes'){$taskArgs+=$(if($taskStaging){'-ParisSavePrefix=G1Outcomes2_20261008'}else{'-ParisSavePrefix=G1Outcomes_20261008'})}
if($Stage -eq 'lifecycle'){$taskArgs+='-ParisSavePrefix=G1Lifecycle_20261008'}
if($Mode -eq 'plain'){
 $taskArgs=@(('"'+$taskProject+'"'),'/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1','-game','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound','-EnablePlugins=ParisBridgeMissionV1','-DisablePlugins=ParisEditorBridge','-DisablePython','-seconds=30',('-abslog="'+$taskLog+'"'))
}else{
 $taskScript=Join-Path $PSScriptRoot $(if($Mode -eq 'author'){'ue_author.py'}elseif($Mode -eq 'headings'){'ue_headings.py'}elseif($Mode -eq 'bridgehook'){'ue_bridge_hook.py'}elseif($Mode -eq 'staging'){'ue_staging_author.py'}else{'ue_test.py'})
 $taskSnapshot=Join-Path $taskOut 'native_source.py'
 Copy-Item -LiteralPath $taskScript -Destination $taskSnapshot
 $taskArgs+=('-ExecCmds="py '+($taskSnapshot -replace '\\','/')+'"')
 if($Mode -in @('author','headings','bridgehook','staging')){$taskArgs+='-NullRHI'}else{$taskArgs+='-DisablePlugins=ParisEditorBridge'}
}
$taskProcess=Start-Process 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
"Owned G1 $Mode PID $($taskProcess.Id), evidence $taskOut"
$taskProcess.WaitForExit()
@{identity=$Identity;pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;mode=$Mode;stage=$Stage}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json')
if($taskProcess.ExitCode -ne 0){throw 'Owned G1 process failed; preserve logs'}
if($Mode -ne 'plain'){Get-Content -LiteralPath (Join-Path $taskOut 'result.json') -Raw}
& 'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 (Join-Path $PSScriptRoot 'audit.py') --identity $Identity --mode $(if($Mode -in @('headings','bridgehook','staging')){'author'}else{$Mode})
if($LASTEXITCODE -ne 0){throw 'Independent native G1 entry audit failed; retain raw evidence'}
