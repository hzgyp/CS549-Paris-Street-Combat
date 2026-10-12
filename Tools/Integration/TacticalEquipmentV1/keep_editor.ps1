param([string]$Revision='candidate_full_v7')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-tactical-equipment-20261010'
$taskExisting=@(Get-Process UnrealEditor -ErrorAction SilentlyContinue)
if($taskExisting.Count){Get-Content -LiteralPath (Join-Path $taskBase 'editor-session.json');exit}
$taskBuild=Get-Content -LiteralPath (Join-Path $taskBase ($Revision+'/build-editor.json')) -Raw | ConvertFrom-Json
if($taskBuild.exit_code -ne 0 -or $taskBuild.status -eq 'building'){throw 'Matching Editor build required'}
$taskProject=Join-Path $taskBase ($Revision+'/Project/WW2FranceLiberation.uproject')
$taskLog=Join-Path $taskBase ('editor-'+$Revision+'.log')
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList @(('"'+$taskProject+'"'),'/Engine/Maps/Entry','-NoSplash','-NoLoadStartupPackages','-DisablePython','-noraytracing','-UDPMESSAGING_TRANSPORT_ENABLE=false',('-abslog="'+$taskLog+'"'),'-ExecCmds="t.MaxFPS 15"') -WindowStyle Hidden -PassThru
[ordered]@{pid=$taskProcess.Id;revision=$Revision;project=$taskProject;log=$taskLog;policy='keep open; no automatic close; no PIE or Content writes during immutable Game checks';started=[DateTimeOffset]::Now.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskBase 'editor-session.json')
Get-Content -LiteralPath (Join-Path $taskBase 'editor-session.json')
