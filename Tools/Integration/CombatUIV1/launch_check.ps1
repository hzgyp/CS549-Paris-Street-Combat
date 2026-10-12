param([string]$Revision='candidate_ui_v1',[ValidateSet('pages','pages_small','pause','confirm','equipment_pause')][string]$Mode='pause',[ValidatePattern('^[a-z0-9_]+$')][string]$Identity='ui_pause_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-tactical-equipment-20261010'
$taskOut=Join-Path $taskRoot ('tmp/g1-combat-ui-20261011/checks/'+$Identity)
if(Get-Process WW2FranceLiberation*,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Preserve active game/build'}
if(Test-Path -LiteralPath $taskOut){throw 'Preserve occupied diagnostic identity'}
$taskRuntime=Get-Content -LiteralPath (Join-Path $taskBase ($Revision+'/runtime.json')) -Raw | ConvertFrom-Json
$taskExe=Join-Path $taskRuntime.path 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
if((Get-FileHash -LiteralPath $taskExe).Hash.ToLowerInvariant() -ne $taskRuntime.game_sha256){throw 'Runtime changed'}
New-Item -ItemType Directory -Path $taskOut | Out-Null
$taskWidth=if($Mode -eq 'pages_small'){1280}else{1920}
$taskHeight=if($Mode -eq 'pages_small'){720}else{1080}
$taskCV='sg.ViewDistanceQuality=2,sg.AntiAliasingQuality=2,sg.ShadowQuality=2,sg.GlobalIlluminationQuality=2,sg.ReflectionQuality=2,sg.PostProcessQuality=2,sg.TextureQuality=2,sg.EffectsQuality=2,sg.FoliageQuality=2,sg.ShadingQuality=2,r.ScreenPercentage=100,r.Streaming.PoolSize=1536,r.VSync=0,t.MaxFPS=60'
$taskArgs=@('-windowed','-ForceRes',('-ResX='+$taskWidth),('-ResY='+$taskHeight),'-NoSplash','-DisablePython','-noraytracing','-UDPMESSAGING_TRANSPORT_ENABLE=false',('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),('-ParisSavePrefix=ParisUI_'+$Identity),('-DPCVars="'+$taskCV+'"'),('-ParisCombatUIProbe='+$Mode),('-ParisCombatUIOut="'+$taskOut+'"'))
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskReceipt=[ordered]@{status='running';pid=$taskProcess.Id;mode=$Mode;identity=$Identity;revision=$Revision;game_sha256=$taskRuntime.game_sha256;arguments=$taskArgs;started=[DateTimeOffset]::Now.ToString('o')}
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
@{pid=$taskProcess.Id;mode=$Mode}|ConvertTo-Json -Compress
$taskDeadline=[DateTime]::UtcNow.AddSeconds(160)
while(-not $taskProcess.WaitForExit(1000)){if([DateTime]::UtcNow -gt $taskDeadline){throw 'Deadline: preserve owned game for inspection'}}
$taskReceipt.exit_code=$taskProcess.ExitCode;$taskReceipt.status='exited';$taskReceipt.finished=[DateTimeOffset]::Now.ToString('o')
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
if($taskProcess.ExitCode -ne 0){throw 'Abnormal exit; preserve crash identity'}
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut 'RESULT.json') -Raw | ConvertFrom-Json
@{status=$taskResult.status;reason=$taskResult.reason;checks=$taskResult.checks.Count;exit_code=$taskProcess.ExitCode}|ConvertTo-Json -Compress
if($taskResult.status -notlike 'pass*'){throw 'Stop failed UI fixture'}
