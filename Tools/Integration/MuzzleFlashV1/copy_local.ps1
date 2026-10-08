param([Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
function Assert-FreeNativeSlot {
 if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve occupied native slot'}
 if(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.Name -match '^(powershell|pwsh|python|pythonw)\.exe$' -and $_.CommandLine -match 'Tools[/\\]Integration[/\\](?!MuzzleFlashV1[/\\])[^\s"]+[/\\](?:run|launch)(?:_|\.)[^\s"]*' }){throw 'Preserve foreign launcher'}
}
Assert-FreeNativeSlot
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MuzzleFlashV1/$Identity"
$taskPlan=Get-Content -LiteralPath (Join-Path $taskOut 'install_plan.json') -Raw|ConvertFrom-Json
if(Test-Path -LiteralPath (Join-Path $taskOut 'descriptor.original')){throw 'Preserve occupied copy stage'}
& python -B -c "import sys;sys.path.insert(0,r'$PSScriptRoot');from common import guards,intake_rows;assert len(guards())==703 and len(intake_rows())==68"
if($LASTEXITCODE -ne 0){throw 'Protection gate failed'}
Copy-Item -LiteralPath (Join-Path $taskRoot $taskPlan.original_row.path) -Destination (Join-Path $taskOut 'descriptor.original')
if((Get-FileHash -LiteralPath (Join-Path $taskOut 'descriptor.original') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskPlan.original_row.sha256){throw 'Descriptor backup changed'}
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskOut 'copy_source.ps1')
foreach($taskFile in $taskPlan.files){
 Assert-FreeNativeSlot
 $taskSource=Join-Path $taskRoot $taskFile.source
 $taskDestination=Join-Path $taskRoot $taskFile.destination
 if(Test-Path -LiteralPath $taskDestination){throw 'Refuse occupied selected file'}
 if((Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskFile.sha256){throw 'Input changed'}
 New-Item -ItemType Directory -Path (Split-Path $taskDestination) -Force|Out-Null
 Copy-Item -LiteralPath $taskSource -Destination $taskDestination
 if((Get-Item -LiteralPath $taskDestination).Length -ne $taskFile.size_bytes -or (Get-FileHash -LiteralPath $taskDestination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskFile.sha256){throw 'Selected exact readback failed'}
}
foreach($taskAlias in $taskPlan.aliases){
 Assert-FreeNativeSlot
 $taskPath=Join-Path $taskRoot $taskAlias.path
 if(Test-Path -LiteralPath $taskPath){throw 'Preserve occupied selected alias'}
 New-Item -ItemType Directory -Path (Split-Path $taskPath) -Force|Out-Null
 New-Item -ItemType Junction -Path $taskPath -Target (Join-Path $taskRoot $taskAlias.target)|Out-Null
}
Write-Output 'Exact local copies and one-home bindings complete; descriptor remains disabled until explicit patch/proof/ledger'
