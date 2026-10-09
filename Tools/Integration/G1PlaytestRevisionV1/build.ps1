param([ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity='candidate_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active user/other engine processes'}
$taskOut=Join-Path $taskRoot ('tmp/g1-playtest-revision-20261008/'+$Identity)
$taskPrepared=Get-Content (Join-Path $taskOut 'prepare_revision.json') -Raw|ConvertFrom-Json
$taskProject=Join-Path $taskPrepared.project 'WW2FranceLiberation.uproject'
if($taskPrepared.descriptor_sha256 -and (Get-FileHash -LiteralPath $taskProject).Hash.ToLower() -ne $taskPrepared.descriptor_sha256){throw 'Private project descriptor changed'}
if($taskPrepared.status -ne 'prepared_runtime_unverified'){throw 'Exact preparation required'}
foreach($taskRow in $taskPrepared.private_source_files){
 if((Get-FileHash -LiteralPath (Join-Path $taskPrepared.project $taskRow.path)).Hash.ToLower() -ne $taskRow.sha256){throw 'Prepared source changed'}
}
if(Test-Path -LiteralPath (Join-Path $taskOut 'build_revision.json')){throw 'Preserve occupied build receipt'}
$taskReceipt=[ordered]@{identity=$Identity;started=(Get-Date).ToString('o');status='building_editor_and_private_game';scope='Private wrapper only; no source asset save or Catalog selection'}
$taskReceipt|ConvertTo-Json|Set-Content (Join-Path $taskOut 'build_revision.json') -Encoding UTF8
if($taskPrepared.observer_only_game_build -or $taskPrepared.private_method_only_game_build){
 $taskReceipt.editor_build='not_run_private_game_only_no_reflected_schema_change'
}else{
$taskEditorArgs=@('WW2FranceLiberationEditor','Win64','Development',('-Project='+$taskProject),'-WaitMutex','-NoHotReload')
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' @taskEditorArgs 2>&1|Tee-Object (Join-Path $taskOut 'editor_build.log')
$taskReceipt.editor_exit_code=$LASTEXITCODE
if($LASTEXITCODE -ne 0){$taskReceipt.status='editor_compile_failed';$taskReceipt|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'build_revision.json');throw 'Preserve failed editor compile identity'}
}
if($taskPrepared.reuse_v3_cook){
 foreach($taskRow in $taskPrepared.cooked_files){
  $taskFile=Join-Path $taskPrepared.project ('Saved/Cooked/Windows/'+$taskRow.path)
  if((Get-Item -LiteralPath $taskFile).Length -ne $taskRow.size_bytes -or (Get-FileHash -LiteralPath $taskFile).Hash.ToLower() -ne $taskRow.sha256){throw 'Frozen cooked content changed'}
 }
 $taskGameArgs=@('WW2FranceLiberation','Win64','Development',('-Project='+$taskProject),'-WaitMutex','-NoHotReload')
 & 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' @taskGameArgs 2>&1|Tee-Object (Join-Path $taskOut 'game_build.log')
 $taskReceipt.game_build_exit_code=$LASTEXITCODE
 if($LASTEXITCODE -ne 0){$taskReceipt.status='game_compile_failed';$taskReceipt|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'build_revision.json');throw 'Preserve failed game compile'}
 foreach($taskRow in $taskPrepared.archive_files){
  $taskFrom=Join-Path $taskPrepared.reuse_archive $taskRow.path
  if((Get-Item -LiteralPath $taskFrom).Length -ne $taskRow.size_bytes){throw 'Admitted archive size changed'}
  $taskTo=Join-Path $taskOut ('Archive/'+$taskRow.path)
  New-Item -ItemType Directory -Path (Split-Path $taskTo) -Force|Out-Null
  Copy-Item -LiteralPath $taskFrom -Destination $taskTo
 }
 $taskNewGame=Join-Path $taskPrepared.project 'Binaries/Win64/WW2FranceLiberation.exe'
 if((Get-FileHash -LiteralPath $taskNewGame).Hash.ToLower() -eq $taskPrepared.v3_game_sha256){throw 'Expected new method implementation binary'}
 Copy-Item -LiteralPath $taskNewGame -Destination (Join-Path $taskOut 'Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe') -Force
 foreach($taskRow in $taskPrepared.archive_files){
  if($taskRow.path.Replace([IO.Path]::DirectorySeparatorChar,[char]'/') -eq 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'){continue}
  $taskFile=Join-Path $taskOut ('Archive/'+$taskRow.path)
  if((Get-FileHash -LiteralPath $taskFile).Hash.ToLower() -ne $taskRow.sha256){throw 'Only monolithic game executable may change'}
 }
 $taskReceipt.method_only_binary_rebuild=$true
}else{
$taskArgs=@('BuildCookRun','-nop4',('-project='+$taskProject),'-installed','-platform=Win64','-clientconfig=Development',
 '-build','-cook','-stage','-pak','-iostore','-archive',('-archivedirectory='+$taskOut+'/Archive'),
 '-map=/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1','-unattended','-utf8output','-unrealexe=UnrealEditor-Cmd.exe',
 '-nocompileeditor','-skipbuildeditor','-nodebuginfo','-AdditionalCookerOptions=-CookProcessCount=1 -DisablePlugins=ParisEditorBridge -DisablePython')
$taskReceipt.arguments=$taskArgs
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' @taskArgs 2>&1|Tee-Object (Join-Path $taskOut 'uat.log')
$taskReceipt.uat_exit_code=$LASTEXITCODE
if($LASTEXITCODE -ne 0){$taskReceipt.status='cook_or_build_failed';$taskReceipt|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'build_revision.json');throw 'Preserve failed cook identity'}
}
if($taskPrepared.reuse_v3_cook){
 # The complete copied-file check above includes every ucas payload.
 $taskReceipt.reused_content_payloads_exact=$true
}
$taskUIDir=Join-Path $taskOut 'Archive/Windows/WW2FranceLiberation/UI'
New-Item -ItemType Directory -Path $taskUIDir -Force|Out-Null
Copy-Item (Join-Path $taskOut 'UI/*') $taskUIDir
$taskLauncher=@'
@echo off
cd /d "%~dp0"
"%~dp0Windows\WW2FranceLiberation\Binaries\Win64\WW2FranceLiberation.exe" -windowed -ResX=1920 -ResY=1080 -DisablePython -noraytracing -ParisSavePrefix=ParisG1PlaytestV5 -UserDir="%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestV5" -ExecCmds="sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0"
'@
$taskLauncher|Set-Content (Join-Path $taskOut 'Archive/PLAY_G1_REVISION.cmd') -Encoding ASCII
$taskReceipt.status='built_private_revision_runtime_unverified'
$taskReceipt.game_sha256=(Get-FileHash (Join-Path $taskOut 'Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')).Hash.ToLower()
$taskReceipt.finished=(Get-Date).ToString('o')
$taskReceipt|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'build_revision.json') -Encoding UTF8
