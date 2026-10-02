# Exact, dated permission repair. No root ACL or owner changes.
$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$shareRoot=Join-Path $projectRoot 'Assets/LocalShared/SFTP'
$outFile=Join-Path $projectRoot 'tmp/rifle-motion-20261002-v1/acl-repair.json'
$result=@{status='started'; root_acl_unchanged=$false; targets=@(); errors=@()}
try {
    $principal=New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if(-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Requires Windows administrator confirmation'}
    $rootBefore=(Get-Acl -LiteralPath $shareRoot).Sddl
    $targets=@('baselines/rifle-pro-mocap-original/rifle-motion-20261002-v1','workspaces/yg745/rifle-motion-ue582-v1')
    foreach($relative in $targets){
        $target=[IO.Path]::GetFullPath((Join-Path $shareRoot $relative))
        if(-not $target.StartsWith($shareRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe ACL target'}
        $items=@(Get-Item -LiteralPath $target)+@(Get-ChildItem -LiteralPath $target -Recurse -Force)
        if(@($items | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Refuse alias in ACL tree'}
        $account="$env:COMPUTERNAME\cs549sftp"
        $log=& icacls $target /grant "${account}:(OI)(CI)M" /T /C 2>&1
        if($LASTEXITCODE -ne 0){throw 'Recursive shared Modify grant failed'}
        foreach($item in $items){
            $rules=(Get-Acl -LiteralPath $item.FullName).Access
            $allowed=@($rules | Where-Object {$_.IdentityReference.Value -eq $account -and $_.AccessControlType -eq 'Allow' -and ($_.FileSystemRights -band [Security.AccessControl.FileSystemRights]::Modify) -eq [Security.AccessControl.FileSystemRights]::Modify})
            if(-not $allowed.Count){throw 'Missing Modify rule after grant'}
        }
        $result.targets+=@{path=$relative; entries_verified=$items.Count; permissions='shared-account Modify; no owner/ACL administration'}
    }
    $result.root_acl_unchanged=((Get-Acl -LiteralPath $shareRoot).Sddl -eq $rootBefore)
    if(-not $result.root_acl_unchanged){throw 'Protected root ACL changed'}
    $result.status='complete'
} catch {$result.status='failed';$result.errors+=@($_.Exception.Message)}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outFile -Encoding utf8
if($result.status -ne 'complete'){exit 1}
