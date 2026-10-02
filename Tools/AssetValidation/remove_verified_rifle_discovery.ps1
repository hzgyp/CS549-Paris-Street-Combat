$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$proofPath=Join-Path $projectRoot 'tmp/rifle-motion-20261002-v1/cleanup-eligibility.json'
$proof=[IO.File]::ReadAllText($proofPath) | ConvertFrom-Json -Depth 10
if($proof.status -ne 'verified_redundant_discovery_only' -or $proof.file_count -ne 753){throw 'Missing exact cleanup proof'}
if(Get-Process UnrealEditor,UnrealEditor-Cmd,blender -ErrorAction SilentlyContinue){throw 'Close affected editors first'}
$expectedTarget=Join-Path $projectRoot 'Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1/Content/Rifle_01'
$target=[IO.Path]::GetFullPath((Join-Path $projectRoot $proof.target))
if($target -ne [IO.Path]::GetFullPath($expectedTarget)){throw 'Unexpected recursive removal target'}
$lab=Join-Path $projectRoot 'Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1'
$all=@(Get-Item -LiteralPath $target)+@(Get-ChildItem -LiteralPath $target -Recurse -Force)
if(@($all | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Refuse alias removal'}
if(@($all | Where-Object {-not $_.PSIsContainer}).Count -ne 753){throw 'File set changed after proof'}
foreach($entry in $proof.files){
    $p=[IO.Path]::GetFullPath((Join-Path $lab $entry.path))
    $retained=Join-Path (Join-Path $projectRoot $proof.retained_original) $entry.path
    if(-not $p.StartsWith($target+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe proven file'}
    if((Get-Item -LiteralPath $p).Length -ne $entry.size_bytes -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256){throw 'Discovery changed after proof'}
    if((Get-Item -LiteralPath $retained).Length -ne $entry.size_bytes -or (Get-FileHash -LiteralPath $retained -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256){throw 'Retained original changed'}
}
# Every file is proven identical to a retained original. Evidence is outside
# this exact Content subtree. Native PowerShell is used end-to-end.
Remove-Item -LiteralPath $target -Recurse -Force
$selectedContent=Join-Path (Join-Path $projectRoot $proof.retained_selected) 'Content/Rifle_01'
New-Item -ItemType Junction -Path $target -Target $selectedContent | Out-Null
$alias=Get-Item -LiteralPath $target
if($alias.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath($alias.Target) -ne [IO.Path]::GetFullPath($selectedContent)){throw 'Alias verification failed'}
@{status='complete'; removed_redundant_files=753; recovered_from=$proof.retained_original; freed_bytes=$proof.size_bytes; retained_alias=$proof.target; alias_target=$proof.retained_selected+'/Content/Rifle_01'; reason='Existing candidate-probe scripts use the original lab mount; alias points only to the one writable selected workspace'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $projectRoot 'tmp/rifle-motion-20261002-v1/cleanup.json') -Encoding utf8
Write-Output 'Removed 753 verified redundant discovery files; originals/evidence/releases retained; selected writable lab junction verified.'
