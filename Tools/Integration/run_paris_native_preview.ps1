param([string]$EngineEditor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe',[switch]$CheckOnly)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Existing user-owned Unreal session: close it before another launch.'}
$taskCatalog=Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/Sync/CATALOG.json') -Raw | ConvertFrom-Json
$taskRelease=$taskCatalog.active_manifests|Where-Object {$_.asset_id -eq 'paris-gameplay-native-playtest'}
if(@($taskRelease).Count -ne 1){throw 'Missing selected playtest release; update Git and read TEAM_PLAYTEST.md'}
$taskManifestPath=Join-Path $taskRoot $taskRelease.path
if((Get-FileHash -LiteralPath $taskManifestPath -Algorithm SHA256).Hash.ToLower() -ne $taskRelease.sha256){throw 'Catalog/manifest mismatch'}
$taskManifest=Get-Content -LiteralPath $taskManifestPath -Raw|ConvertFrom-Json
foreach($taskFile in $taskManifest.files){
    $taskFilePath=Join-Path $taskRoot $taskFile.path
    if((Get-Item -LiteralPath $taskFilePath).Length -ne $taskFile.size_bytes -or (Get-FileHash -LiteralPath $taskFilePath -Algorithm SHA256).Hash.ToLower() -ne $taskFile.sha256){throw "Unsynchronized native file: $($taskFile.path)"}
}
$taskCityRelease=$taskCatalog.active_manifests|Where-Object {$_.asset_id -eq 'france-liberation-content'}
$taskCityPath=Join-Path $taskRoot $taskCityRelease.path
if((Get-FileHash -LiteralPath $taskCityPath -Algorithm SHA256).Hash.ToLower() -ne $taskCityRelease.sha256){throw 'City catalog/manifest mismatch'}
$taskCity=Get-Content -LiteralPath $taskCityPath -Raw|ConvertFrom-Json
# Full city SHA verification is done by restore_native_playtest.py verify.
# Check availability/size here rather than hash 26 GiB at every startup.
foreach($taskFile in $taskCity.files){
    if((Get-Item -LiteralPath (Join-Path $taskRoot $taskFile.path)).Length -ne $taskFile.size_bytes){throw "City dependency missing/different: $($taskFile.path)"}
}
if(-not(Test-Path -LiteralPath $EngineEditor)){throw 'UE editor not found; supply -EngineEditor with your UE5.8.2 installation'}
$taskVersionPath=Join-Path (Split-Path (Split-Path (Split-Path $EngineEditor))) 'Build/Build.version'
$taskVersion=Get-Content -LiteralPath $taskVersionPath -Raw|ConvertFrom-Json
if($taskVersion.MajorVersion -ne 5 -or $taskVersion.MinorVersion -ne 8 -or $taskVersion.PatchVersion -ne 2 -or $taskVersion.Changelist -ne 56702186){throw 'Team playtest requires UE5.8.2 CL56702186'}
if($CheckOnly){Write-Output 'Selected gameplay hashes, city sizes and UE5.8.2 checked; no game launched';return}
$taskLog=Join-Path $taskRoot ('tmp/continuous-arms-native/human-native-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.log')
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-game','-DisablePlugins=ParisEditorBridge,PythonScriptPlugin',
 '-NoP4','-NoSplash','-windowed','-ResX=1280','-ResY=720',('-abslog="'+$taskLog+'"'))
# Visible user review only when this launcher is requested; no auto quit/test/Python callback.
$taskProcess=Start-Process -FilePath $EngineEditor -ArgumentList $taskArgs -WindowStyle Normal -PassThru
@{pid=$taskProcess.Id;log=$taskLog;user_owned=$true;python_disabled=$true;game_mode=$true}|ConvertTo-Json
Write-Output 'WASD / mouse / left click / R. Alt+F4 closes this game window; no map save.'
