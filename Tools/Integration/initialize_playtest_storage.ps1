param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Owner)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor*,blender -ErrorAction SilentlyContinue){throw 'Close editors before creating a Content mount'}
$taskLink=Join-Path $taskRoot 'Unreal/ParisStreetCombat/Content'
$taskTarget=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/$Owner/paris-gameplay-v1/Content"
if(Test-Path -LiteralPath $taskLink){
    $taskExisting=Get-Item -LiteralPath $taskLink -Force
    if($taskExisting.LinkType -ne 'Junction'){throw 'Existing physical Content: preserve it and coordinate migration; nothing moved or deleted'}
    $taskResolved=[IO.Path]::GetFullPath([string]$taskExisting.Target)
    if(-not $taskResolved.StartsWith(($taskRoot+[IO.Path]::DirectorySeparatorChar),[StringComparison]::OrdinalIgnoreCase)){throw 'Existing Content mount points outside this checkout'}
    Write-Output "Existing local Content junction retained: $taskResolved"
    return
}
# No existing directory is moved, merged or deleted by this initializer.
New-Item -ItemType Directory -Path $taskTarget -Force|Out-Null
New-Item -ItemType Junction -Path $taskLink -Target $taskTarget|Out-Null
Write-Output "Created one writable asset home and Content alias: $taskTarget"
