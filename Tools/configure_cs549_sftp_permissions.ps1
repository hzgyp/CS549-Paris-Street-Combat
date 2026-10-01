[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$SftpRoot = 'D:\0.Rutgers\CS549\Project-New\Assets\LocalShared\SFTP'
$SftpUser = "$env:COMPUTERNAME\cs549sftp"
$ReportPath = 'C:\ProgramData\ssh\cs549-sftp-permissions.txt'

if (-not (Test-Path -LiteralPath $SftpRoot -PathType Container)) {
    throw "SFTP root does not exist: $SftpRoot"
}

$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [System.Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run this script from an elevated PowerShell session.'
}

# Keep the chroot root itself non-writable. Grant Modify only to established
# shared release/transfer areas, not private intake awaiting rights clearance.
# Modify includes read, create, overwrite, rename and delete, not ACL changes.
$rootAclBefore = (Get-Acl -LiteralPath $SftpRoot).Sddl
$children = @('baselines', 'incoming', 'objects', 'releases' | ForEach-Object {
    Get-Item -LiteralPath (Join-Path $SftpRoot $_) -Force
})
foreach ($child in $children) {
    if (-not $child.PSIsContainer -or
        ($child.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Expected an ordinary shared directory: $($child.FullName)"
    }
    foreach ($entry in Get-ChildItem -LiteralPath $child.FullName -Recurse -Force) {
        if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Refusing recursive ACL changes through a reparse point: $($entry.FullName)"
        }
    }
}
foreach ($child in $children) {
    if ($child.PSIsContainer) {
        & icacls.exe $child.FullName /grant "${SftpUser}:(OI)(CI)M" /T /C | Out-Null
    }
    else {
        & icacls.exe $child.FullName /grant "${SftpUser}:M" /C | Out-Null
    }
    if ($LASTEXITCODE -ne 0) {
        throw "icacls failed for $($child.FullName) with exit code $LASTEXITCODE"
    }
}
if ((Get-Acl -LiteralPath $SftpRoot).Sddl -ne $rootAclBefore) {
    throw 'The SFTP root ACL changed unexpectedly.'
}

$report = [System.Collections.Generic.List[string]]::new()
$report.Add("Generated: $(Get-Date -Format o)")
$report.Add("SFTP root: $SftpRoot")
$report.Add("Account: $SftpUser")
$report.Add('Root ACL unchanged; baselines/incoming/objects/releases grant Modify recursively.')
$report.Add('Private workspaces and unknown root children are not changed by this tool.')
$report.Add('')
$report.Add('ROOT ACL:')
$report.AddRange([string[]](& icacls.exe $SftpRoot 2>&1))
foreach ($child in $children) {
    $report.Add('')
    $report.Add("CHILD ACL: $($child.FullName)")
    $report.AddRange([string[]](& icacls.exe $child.FullName 2>&1))
}

$report | Set-Content -LiteralPath $ReportPath -Encoding utf8
Write-Host "SFTP collaboration permissions applied. Report: $ReportPath"
