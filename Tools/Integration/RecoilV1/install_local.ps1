param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$BuildIdentity,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$AuditIdentity,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Native slot occupied; no shared write'}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/RecoilV1/$Identity"
if(Test-Path -LiteralPath $taskOut){throw 'Preserve occupied installation evidence'}
$taskAuditPath=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/RecoilV1/$AuditIdentity/result.json"
$taskAudit=Get-Content -LiteralPath $taskAuditPath -Raw|ConvertFrom-Json
if($taskAudit.status -ne 'pass_finite_candidate_receipts_visual_review_separate'){throw 'Candidate audit absent'}
$taskFiles=@(
    @('ParisGripBindingV18','UnrealEditor-ParisGripBindingV18.dll'),
    @('ParisNPCGripV15','UnrealEditor-ParisNPCGripV15.dll'),
    @('ParisNPCGripV15','UnrealEditor-ParisNPCGripV15Editor.dll')
)
# Generating evidence is separate from changing the repository authorization
# ledger; the latter is authored explicitly after this exact receipt is read.
& python (Join-Path $PSScriptRoot 'common.py') --identity $Identity
if($LASTEXITCODE -ne 0){throw 'Selected703 preflight failed'}
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskOut 'installer_source.ps1')
$taskRows=@()
foreach($taskPair in $taskFiles){
    $taskRelative="Unreal/ParisStreetCombat/Plugins/$($taskPair[0])/Binaries/Win64/$($taskPair[1])"
    $taskSelected=[IO.Path]::GetFullPath((Join-Path $taskRoot $taskRelative))
    $taskAllowedPrefix=Join-Path $taskRoot "Unreal/ParisStreetCombat/Plugins/$($taskPair[0])/Binaries/Win64/"
    if(-not $taskSelected.StartsWith($taskAllowedPrefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected selected target'}
    $taskCandidate=Join-Path $taskRoot "tmp/recoil-v1/Build_$BuildIdentity/$($taskPair[0])/Binaries/Win64/$($taskPair[1])"
    $taskBackup=Join-Path $taskOut "$($taskPair[0])_$($taskPair[1]).original"
    $taskOldFile=Get-Item -LiteralPath $taskSelected
    $taskOld=@{path=$taskRelative;size_bytes=$taskOldFile.Length;sha256=(Get-FileHash -LiteralPath $taskSelected -Algorithm SHA256).Hash.ToLowerInvariant()}
    $taskNewFile=Get-Item -LiteralPath $taskCandidate
    $taskNew=@{path=$taskRelative;size_bytes=$taskNewFile.Length;sha256=(Get-FileHash -LiteralPath $taskCandidate -Algorithm SHA256).Hash.ToLowerInvariant()}
    Copy-Item -LiteralPath $taskSelected -Destination $taskBackup
    if((Get-FileHash -LiteralPath $taskBackup -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskOld.sha256){throw 'Backup authentication failed'}
    $taskRows+=@{old=$taskOld;new=$taskNew;backup=$taskBackup;candidate=$taskCandidate;selected=$taskSelected}
}
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Native slot changed; backups retained, no replacement'}
foreach($taskRow in $taskRows){
    if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'New native owner appeared; do not continue shared replacement'}
    if((Get-FileHash -LiteralPath $taskRow.selected -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskRow.old.sha256){throw 'Selected binary changed since backup'}
    Copy-Item -LiteralPath $taskRow.candidate -Destination $taskRow.selected -Force
    if((Get-FileHash -LiteralPath $taskRow.selected -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskRow.new.sha256){throw 'Selected readback failed; backup retained'}
}
$taskPreflight=Get-Content -LiteralPath (Join-Path $taskOut 'preflight.json') -Raw|ConvertFrom-Json
$taskChanged=@($taskRows|ForEach-Object{$_.new.path})
foreach($taskGuard in $taskPreflight.guards){
    if($taskGuard.path -notin $taskChanged){
        $taskPath=Join-Path $taskRoot $taskGuard.path
        if((Get-Item -LiteralPath $taskPath).Length -ne $taskGuard.size_bytes -or (Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskGuard.sha256){throw 'Non-display guard changed; retain backups'}
    }
}
@{
    status='pass_local_recoil_display_binaries_installed_runtime_unpassed'
    authorization='2026-10-07 user requests visible firing recoil repair for character presentation'
    candidate_audit=$taskAuditPath.Replace('\','/').Substring($taskRoot.Length+1)
    candidate_audit_sha256=(Get-FileHash -LiteralPath $taskAuditPath -Algorithm SHA256).Hash.ToLowerInvariant()
    original_guard_count=703
    unchanged_other_guard_count=700
    unchanged_other_guards=$true
    original_rows=@($taskRows|ForEach-Object{$_.old})
    new_rows=@($taskRows|ForEach-Object{$_.new})
    backups=@($taskRows|ForEach-Object{$_.backup.Replace('\','/').Substring($taskRoot.Length+1)})
    local_only=$true
    fresh_original_project_runtime_passed=$false
}|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $taskOut 'result.json') -Encoding utf8
Write-Output 'Three display DLLs installed with exact backups/700 other guards preserved; explicit ledger and fresh regression pending'
