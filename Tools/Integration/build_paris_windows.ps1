param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Identity,
      [ValidateSet('CITY_PACKAGE_DRAFT_INVENTORY_20261002.json','CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json','CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json','CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json','CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json')]
      [string]$NativeInventory = 'CITY_PACKAGE_DRAFT_INVENTORY_20261002.json')
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskBuildDir = Join-Path $taskRoot "tmp/paris-city-package-20261002/$Identity"
if (Test-Path -LiteralPath $taskBuildDir) { throw 'Preserve occupied build identity' }
if (Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue) { throw 'Close affected engine writers first' }
$taskProject = Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
$taskUAT = 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat'
$taskGuardFiles = @{}
foreach ($taskInventoryName in @('RELOAD_DRAFT_SNAPSHOT_20261002.json',$NativeInventory)) {
    $taskInventory = Get-Content -LiteralPath (Join-Path $taskRoot "Assets/Integration/$taskInventoryName") -Raw | ConvertFrom-Json
    foreach ($taskItem in $taskInventory.files) {
        $taskPath = Join-Path $taskRoot $taskItem.path
        if ((Get-Item -LiteralPath $taskPath).Length -ne $taskItem.size_bytes -or (Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskItem.sha256) { throw "Native hash/size conflict: $taskPath" }
        $taskGuardFiles[$taskPath] = $taskItem.sha256
    }
}
Get-ChildItem -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/Content/WW2City/Maps') -Filter '*.umap' -Recurse | ForEach-Object {
    $taskGuardFiles[$_.FullName] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
}
New-Item -ItemType Directory -Path $taskBuildDir | Out-Null
$taskRecord = [ordered]@{
    identity=$Identity; started_at=(Get-Date).ToString('o'); scope='Private early actual-city Windows Development build; no full mission/FPS/public distribution pass'
    git_revision=(& git -C $taskRoot rev-parse HEAD); dirty_source=$true; engine='UE 5.8.2'
    entry='/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'; configs=@{}; guarded_files=$taskGuardFiles.Count
    native_inventory=$NativeInventory
}
foreach ($taskConfig in @('DefaultEngine.ini','DefaultGame.ini','DefaultInput.ini')) {
    $taskRecord.configs[$taskConfig] = (Get-FileHash -LiteralPath (Join-Path $taskRoot "Unreal/ParisStreetCombat/Config/$taskConfig") -Algorithm SHA256).Hash.ToLowerInvariant()
}
$taskArgs = @('BuildCookRun','-nop4',"-project=$taskProject",'-installed','-platform=Win64','-clientconfig=Development',
    '-build','-cook','-stage','-pak','-iostore','-archive',"-archivedirectory=$taskBuildDir/Archive",'-map=/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1',
    '-unattended','-utf8output','-unrealexe=UnrealEditor-Cmd.exe','-nocompileeditor','-skipbuildeditor','-nodebuginfo',
    '-AdditionalCookerOptions=-CookProcessCount=1 -DisablePlugins=ParisEditorBridge')
$taskRecord.arguments = $taskArgs
$taskRecord | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskBuildDir 'build_record.json') -Encoding utf8
try {
    & $taskUAT @taskArgs 2>&1 | Tee-Object -FilePath (Join-Path $taskBuildDir 'uat.log')
    $taskRecord.exit_code = $LASTEXITCODE
    $taskRecord.status = if ($LASTEXITCODE -eq 0) { 'buildcookrun_success_runtime_not_tested' } else { 'buildcookrun_failed' }
} catch {
    $taskRecord.exit_code = 1
    $taskRecord.status = 'launcher_or_build_failed'
    $taskRecord.error = $_.Exception.ToString()
} finally {
    $taskRecord.finished_at = (Get-Date).ToString('o')
    $taskChanged = @($taskGuardFiles.Keys | Where-Object { (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskGuardFiles[$_] })
    $taskRecord.guarded_bytes_unchanged = ($taskChanged.Count -eq 0)
    $taskRecord.unexpected_changes = $taskChanged
    $taskRecord | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskBuildDir 'build_record.json') -Encoding utf8
}
if (-not $taskRecord.guarded_bytes_unchanged) { throw 'Unexpected native change; inspect recorded paths before further work' }
exit $taskRecord.exit_code
