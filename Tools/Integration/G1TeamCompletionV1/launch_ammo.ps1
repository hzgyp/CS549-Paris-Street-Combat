param([ValidatePattern('^[a-z0-9_]+$')][string]$Identity='ammo_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-team-completion-20261010'
$taskOut=Join-Path $taskBase ('checks/'+$Identity)
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Preserve active engine/build'}
if(Test-Path -LiteralPath $taskOut){throw 'Preserve occupied test identity'}
New-Item -ItemType Directory -Path $taskOut | Out-Null
$taskRuntime=Get-Content -LiteralPath (Join-Path $taskBase 'RUNTIME.json') -Raw | ConvertFrom-Json
$taskExe=Join-Path $taskRuntime.path 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
if((Get-FileHash -LiteralPath $taskExe).Hash.ToLowerInvariant() -ne $taskRuntime.game_sha256){throw 'Runtime changed'}
$taskArgs=@('-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-DisablePython','-noraytracing','-UDPMESSAGING_TRANSPORT_ENABLE=false',('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),('-ParisSavePrefix=ParisTeamP1_'+$Identity),('-ParisP1Out="'+$taskOut+'"'),('-ParisAVAuditOut="'+$taskOut+'/av"'),'-ExecCmds="sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,r.VSync 0,t.MaxFPS 60"')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskReceipt=[ordered]@{status='running';pid=$taskProcess.Id;identity=$Identity;started=[DateTimeOffset]::Now.ToString('o');game_sha256=$taskRuntime.game_sha256;arguments=$taskArgs}
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
[ordered]@{pid=$taskProcess.Id;identity=$Identity}|ConvertTo-Json -Compress
$taskDeadline=[DateTime]::UtcNow.AddSeconds(130)
while(-not $taskProcess.WaitForExit(1000)){if([DateTime]::UtcNow -gt $taskDeadline){throw 'Inspect owned game; no automatic termination'}}
$taskReceipt.exit_code=$taskProcess.ExitCode;$taskReceipt.status='exited'
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
if($taskProcess.ExitCode -ne 0){throw 'Preserve abnormal game'}
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut 'RESULT.json') -Raw | ConvertFrom-Json
[ordered]@{status=$taskResult.status;checks=$taskResult.checks.Count;exit_code=$taskProcess.ExitCode}|ConvertTo-Json -Compress
if(-not $taskResult.status.StartsWith('pass_')){throw 'Native ammo/layout check failed'}
