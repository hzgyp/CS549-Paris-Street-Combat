param([ValidatePattern('^[a-z0-9_]+$')][string]$Identity='survey_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-team-completion-20261010'
$taskOut=Join-Path $taskBase ('checks/'+$Identity)
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Preserve active engine/build'}
if(Test-Path -LiteralPath $taskOut){throw 'Preserve occupied survey'}
New-Item -ItemType Directory -Path $taskOut | Out-Null
$taskRuntime=Get-Content -LiteralPath (Join-Path $taskBase 'RUNTIME.json') -Raw | ConvertFrom-Json
$taskExe=Join-Path $taskRuntime.path 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
if((Get-FileHash -LiteralPath $taskExe).Hash.ToLowerInvariant() -ne $taskRuntime.game_sha256){throw 'Runtime changed'}
$taskArgs=@('-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-DisablePython','-noraytracing','-UDPMESSAGING_TRANSPORT_ENABLE=false',('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),('-ParisSavePrefix=ParisCompletion_'+$Identity),('-ParisSpaceSurveyOut="'+$taskOut+'"'),'-ExecCmds="sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,r.VSync 0,t.MaxFPS 60"')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskReceipt=[ordered]@{status='running';identity=$Identity;pid=$taskProcess.Id;started=[DateTimeOffset]::Now.ToString('o');game_sha256=$taskRuntime.game_sha256;arguments=$taskArgs}
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
[ordered]@{pid=$taskProcess.Id;identity=$Identity}|ConvertTo-Json -Compress
$taskDeadline=[DateTime]::UtcNow.AddSeconds(215)
while(-not $taskProcess.WaitForExit(1000)){if([DateTime]::UtcNow -gt $taskDeadline){throw 'Preserve owned process for inspection; no force termination'}}
$taskReceipt.exit_code=$taskProcess.ExitCode;$taskReceipt.status='exited';$taskReceipt.finished=[DateTimeOffset]::Now.ToString('o')
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
if($taskProcess.ExitCode -ne 0){throw 'Preserve abnormal survey'}
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut 'result.json') -Raw | ConvertFrom-Json
[ordered]@{status=$taskResult.status;npc_cells=$taskResult.npc_cells.Count;prone_corridors=$taskResult.prone_corridors.Count;exit_code=$taskProcess.ExitCode}|ConvertTo-Json -Compress
if(-not $taskResult.status.StartsWith('pass_')){throw 'Finite survey failed'}
