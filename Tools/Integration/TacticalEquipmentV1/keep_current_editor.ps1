param([Parameter(Mandatory=$true)][string]$Revision)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-tactical-equipment-20261010'
$taskRegistryPath=Join-Path $taskBase 'editor-sessions.json'
$taskSessions=@()
if(Test-Path -LiteralPath $taskRegistryPath){$taskSessions=@(Get-Content -LiteralPath $taskRegistryPath -Raw | ConvertFrom-Json)}
elseif(Test-Path -LiteralPath (Join-Path $taskBase 'editor-session.json')){$taskSessions=@(Get-Content -LiteralPath (Join-Path $taskBase 'editor-session.json') -Raw | ConvertFrom-Json)}
$taskEditors=@(Get-Process UnrealEditor -ErrorAction SilentlyContinue)
foreach($taskEditor in $taskEditors){if($taskEditor.Id -notin @($taskSessions.pid)){throw 'Preserve unrelated Editor; no automatic close'}}
foreach($taskSession in $taskSessions){if($taskSession.revision -eq $Revision -and $taskSession.pid -in @($taskEditors.Id)){$taskSession | ConvertTo-Json;exit}}
$taskBuild=Get-Content -LiteralPath (Join-Path $taskBase ($Revision+'/build-editor.json')) -Raw | ConvertFrom-Json
if($taskBuild.exit_code -ne 0 -or $taskBuild.status -eq 'building'){throw 'Matching successful Editor build required'}
$taskProject=Join-Path $taskBase ($Revision+'/Project/WW2FranceLiberation.uproject')
$taskLog=Join-Path $taskBase ('editor-'+$Revision+'-fallback.log')
# Official installed-engine local DDC graph bypasses the stalled Zen startup.
# Existing sessions remain open. Neither session writes shared Content during these checks.
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList @(('"'+$taskProject+'"'),'/Engine/Maps/Entry','-DDC=InstalledNoZenLocalFallback','-NoSplash','-NoLoadStartupPackages','-DisablePython','-noraytracing','-UDPMESSAGING_TRANSPORT_ENABLE=false',('-abslog="'+$taskLog+'"'),'-ExecCmds="t.MaxFPS 15"') -WindowStyle Hidden -PassThru
$taskNew=[ordered]@{pid=$taskProcess.Id;revision=$Revision;project=$taskProject;log=$taskLog;policy='keep open; no automatic termination; no PIE/Content writes during immutable Game checks';started=[DateTimeOffset]::Now.ToString('o')}
$taskSessions+=@($taskNew)
ConvertTo-Json -InputObject $taskSessions -Depth 5 | Set-Content -LiteralPath $taskRegistryPath
$taskNew | ConvertTo-Json
