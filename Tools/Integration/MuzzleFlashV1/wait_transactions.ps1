param([Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
 [ValidateSet('Transient','SaveFresh','Fresh','Formal')][string]$Mode='Transient',
 [ValidatePattern('^[A-Za-z0-9_]+$')][string]$Previous)
$ErrorActionPreference='Stop'
$taskDeadline=(Get-Date).AddMinutes(8)
function Test-ForeignBusy {
 if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){return $true}
 return [bool](Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.Name -match '^(powershell|pwsh|python|pythonw)\.exe$' -and $_.CommandLine -match 'Tools[/\\]Integration[/\\](?!MuzzleFlashV1[/\\])[^\s"]+[/\\](?:run|launch)(?:_|\.)[^\s"]*' })
}
Write-Output 'Waiting at most8min for actual engine AND foreign launcher release; no process will be stopped'
while(Test-ForeignBusy){
 if((Get-Date) -ge $taskDeadline){throw 'Bounded wait ended; foreign owners preserved, no native entry'}
 Start-Sleep -Seconds 1
}
Write-Output 'Current slot free; native launcher will independently recheck before entry'
$taskArgs=@{Identity=$Identity;Mode=$Mode}
if($Previous){$taskArgs.Previous=$Previous}
& (Join-Path $PSScriptRoot 'run_transactions.ps1') @taskArgs
