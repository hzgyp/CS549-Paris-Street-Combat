param([string]$EngineEditor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe',
 [ValidateSet('G1','Formal')][string]$Entry='G1',[switch]$LoadSave,[switch]$CheckOnly)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Existing user-owned Unreal session: close it before another launch.'}
$taskCatalog=Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/Sync/CATALOG.json') -Raw | ConvertFrom-Json
$taskRelease=$taskCatalog.active_manifests|Where-Object {$_.asset_id -eq 'paris-gameplay-native-playtest'}
if(@($taskRelease).Count -ne 1){throw 'Missing selected playtest release; update Git and read TEAM_PLAYTEST.md'}
$taskManifestPath=Join-Path $taskRoot $taskRelease.path
if((Get-FileHash -LiteralPath $taskManifestPath -Algorithm SHA256).Hash.ToLower() -ne $taskRelease.sha256){throw 'Catalog/manifest mismatch'}
$taskManifest=Get-Content -LiteralPath $taskManifestPath -Raw|ConvertFrom-Json
if($taskManifest.source_contract){
    $taskContractPath=Join-Path $taskRoot $taskManifest.source_contract.path
    if((Get-FileHash -LiteralPath $taskContractPath -Algorithm SHA256).Hash.ToLower() -ne $taskManifest.source_contract.sha256){throw 'Update Git: source contract differs'}
    $taskContract=Get-Content -LiteralPath $taskContractPath -Raw|ConvertFrom-Json
    if($taskContract.asset_version -ne $taskManifest.asset_version){throw 'Source/asset versions differ'}
    foreach($taskSource in $taskContract.files){
        $taskSourceText=[IO.File]::ReadAllBytes((Join-Path $taskRoot $taskSource.path))
        $taskCanonical=[Text.Encoding]::UTF8.GetBytes([Text.Encoding]::UTF8.GetString($taskSourceText).Replace("`r`n","`n"))
        $taskHasher=[Security.Cryptography.SHA256]::Create()
        try{$taskDigest=[BitConverter]::ToString($taskHasher.ComputeHash($taskCanonical)).Replace('-','').ToLower()}finally{$taskHasher.Dispose()}
        if($taskDigest -ne $taskSource.sha256_lf){throw "Source differs from team release: $($taskSource.path)"}
    }
}
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
if($taskManifest.first_person_selection){
    $taskProjectConfig=Get-Content -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject') -Raw|ConvertFrom-Json
    if(-not ($taskProjectConfig.Plugins|Where-Object {$_.Name -eq 'ParisGripBindingV18' -and $_.Enabled})){throw 'Update Git: approved first-person runtime plugin is not enabled'}
    $taskModule=Get-Content -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18/Binaries/Win64/UnrealEditor.modules') -Raw|ConvertFrom-Json
    $taskEngineModule=Get-Content -LiteralPath (Join-Path (Split-Path $EngineEditor) 'UnrealEditor.modules') -Raw|ConvertFrom-Json
    if($taskModule.BuildId -ne $taskEngineModule.BuildId){throw 'Private native module does not match installed editor build'}
}
if($taskManifest.allied_npc_selection -or $taskManifest.german_npc_selection){
    $taskProjectConfig=Get-Content -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject') -Raw|ConvertFrom-Json
    if(-not ($taskProjectConfig.Plugins|Where-Object {$_.Name -eq 'ParisNPCGripV15' -and $_.Enabled})){throw 'Update Git: approved NPC runtime plugin is not enabled'}
    $taskModule=Get-Content -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/Plugins/ParisNPCGripV15/Binaries/Win64/UnrealEditor.modules') -Raw|ConvertFrom-Json
    $taskEngineModule=Get-Content -LiteralPath (Join-Path (Split-Path $EngineEditor) 'UnrealEditor.modules') -Raw|ConvertFrom-Json
    if($taskModule.BuildId -ne $taskEngineModule.BuildId){throw 'NPC native module does not match installed editor build'}
}
foreach($taskPluginName in @('ParisGripBindingV18','ParisNPCGripV15','ParisBridgeMissionV1','ParisMuzzleFlashV1')){
    $taskModulesPath=Join-Path $taskRoot ('Unreal/ParisStreetCombat/Plugins/'+$taskPluginName+'/Binaries/Win64/UnrealEditor.modules')
    $taskModules=Get-Content -LiteralPath $taskModulesPath -Raw|ConvertFrom-Json
    $taskEngineModules=Get-Content -LiteralPath (Join-Path (Split-Path $EngineEditor) 'UnrealEditor.modules') -Raw|ConvertFrom-Json
    if($taskModules.BuildId -ne $taskEngineModules.BuildId){throw "Module/editor build mismatch: $taskPluginName"}
}
$taskMap=if($Entry -eq 'G1'){$taskManifest.entries.g1}else{$taskManifest.entries.formal}
if(-not $taskMap){throw 'Update Git/assets: selected map entry unavailable'}
if($LoadSave){
    if($Entry -ne 'G1'){throw 'LoadSave is only supported for G1'}
    $taskMap+='?ParisLoad'
}
if($CheckOnly){Write-Output "Selected source/native hashes, city sizes and UE5.8.2 checked: $Entry; no game launched";return}
$taskLog=Join-Path $taskRoot ('tmp/continuous-arms-native/human-native-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.log')
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 $taskMap,'-game','-DisablePlugins=ParisEditorBridge','-DisablePython',
 '-NoP4','-NoSplash','-windowed','-ResX=1280','-ResY=720',('-abslog="'+$taskLog+'"'))
if($Entry -eq 'G1'){$taskArgs+='-EnablePlugins=ParisBridgeMissionV1'}
# Visible user review only when this launcher is requested; no auto quit/test/Python callback.
$taskProcess=Start-Process -FilePath $EngineEditor -ArgumentList $taskArgs -WindowStyle Normal -PassThru
@{pid=$taskProcess.Id;log=$taskLog;user_owned=$true;python_disabled=$true;game_mode=$true}|ConvertTo-Json
Write-Output 'WASD / mouse / left click / R. G1: Enter start, F5 save, F9 load, Ctrl+R restart. Alt+F4 closes.'
