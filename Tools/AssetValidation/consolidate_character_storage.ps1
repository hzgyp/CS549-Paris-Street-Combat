[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\0.Rutgers\CS549\Project-New'
$taskStore = Join-Path $taskRoot 'Assets\LocalShared\SFTP'
$taskPrivate = Join-Path $taskStore 'workspaces'
$taskResult = Join-Path $taskRoot 'tmp\character-storage-consolidation.json'
$taskOwner = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$taskTransfers = @(
    @{Source=(Join-Path $taskRoot 'Assets\LocalWorking\Intake\2026-09-30'); Target=(Join-Path $taskPrivate 'yg745\character-intake-20260930')},
    @{Source=(Join-Path $taskRoot 'Assets\LocalWorking\Validation\UE582\2026-09-30-v1'); Target=(Join-Path $taskPrivate 'yg745\character-ue582-v1')}
)
$taskReport = [ordered]@{status='running';started_at=(Get-Date -Format o);moved=@();shared_with_sftp_account=$false;root_acl_changed=$false}
function Save-Report { $taskReport | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $taskResult -Encoding utf8 }
function Validate-Child($Base,$Path) {
    $taskPrefix=[IO.Path]::GetFullPath($Base).TrimEnd('\')+'\'
    $taskAbsolute=[IO.Path]::GetFullPath($Path)
    if(-not $taskAbsolute.StartsWith($taskPrefix,[StringComparison]::OrdinalIgnoreCase)){throw "Unsafe target: $Path"}
    return $taskAbsolute
}
function Inventory($Folder) {
    $taskInventory=@{}
    foreach($taskFile in Get-ChildItem -LiteralPath $Folder -Recurse -File -Force){
        $taskRelative=$taskFile.FullName.Substring($Folder.TrimEnd('\').Length+1)
        $taskInventory[$taskRelative]=@{sha256=(Get-FileHash -LiteralPath $taskFile.FullName -Algorithm SHA256).Hash;bytes=$taskFile.Length}
    }
    return $taskInventory
}
try {
    if(-not ([Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Requires local administrator for protected SFTP child creation.'}
    if(Get-Process UnrealEditor*,blender -ErrorAction SilentlyContinue){throw 'Close affected UE/Blender processes before relocation.'}
    foreach($taskTransfer in $taskTransfers){
        [void](Validate-Child $taskRoot $taskTransfer.Source)
        [void](Validate-Child $taskPrivate $taskTransfer.Target)
        if((Get-Item -LiteralPath $taskTransfer.Source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Source is already a mapping; inspect existing migration first.'}
        if(Test-Path -LiteralPath $taskTransfer.Target){throw 'Target exists; never merge or overwrite.'}
    }
    if(-not(Test-Path -LiteralPath $taskPrivate)){
        New-Item -ItemType Directory -Path $taskPrivate | Out-Null
        $taskAcl=[Security.AccessControl.DirectorySecurity]::new()
        $taskAcl.SetAccessRuleProtection($true,$false)
        foreach($taskIdentity in @('BUILTIN\Administrators','NT AUTHORITY\SYSTEM')){
            $taskAcl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($taskIdentity,'FullControl','ContainerInherit,ObjectInherit','None','Allow'))
        }
        $taskAcl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($taskOwner,'Modify','ContainerInherit,ObjectInherit','None','Allow'))
        Set-Acl -LiteralPath $taskPrivate -AclObject $taskAcl
    } else { throw 'Private workspace root already exists; inspect ACLs before reuse.' }
    Save-Report
    foreach($taskTransfer in $taskTransfers){
        $taskBefore=Inventory $taskTransfer.Source
        New-Item -ItemType Directory -Path (Split-Path $taskTransfer.Target -Parent) -Force | Out-Null
        Move-Item -LiteralPath $taskTransfer.Source -Destination $taskTransfer.Target
        # Moving on NTFS retains old ACLs. Explicitly inherit the private parent's policy.
        & icacls.exe $taskTransfer.Target /reset /T /C | Out-Null
        if($LASTEXITCODE -ne 0){throw 'Could not apply private workspace ACL inheritance.'}
        $taskAfter=Inventory $taskTransfer.Target
        if($taskBefore.Count -ne $taskAfter.Count){throw 'File count changed after relocation.'}
        foreach($taskName in $taskBefore.Keys){
            if(-not $taskAfter.ContainsKey($taskName) -or $taskBefore[$taskName].sha256 -ne $taskAfter[$taskName].sha256 -or $taskBefore[$taskName].bytes -ne $taskAfter[$taskName].bytes){throw "Relocation integrity failure: $taskName"}
        }
        New-Item -ItemType Junction -Path $taskTransfer.Source -Target $taskTransfer.Target | Out-Null
        $taskReport.moved+=@{source_mapping=$taskTransfer.Source;physical_target=$taskTransfer.Target;file_count=$taskAfter.Count;verified_bytes=[long](($taskAfter.Values|ForEach-Object{$_.bytes}|Measure-Object -Sum).Sum)}
        Save-Report
    }
    $taskReport.status='complete'
    $taskReport.completed_at=Get-Date -Format o
    $taskReport.note='One physical location; old paths are junction aliases, not copies. Workspaces are private until rights and regression gates permit immutable publication.'
} catch {
    $taskReport.status='failed'
    $taskReport.error=$_.Exception.Message
} finally { Save-Report }
